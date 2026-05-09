import re
import os
from functools import lru_cache
from typing import Any, Dict, List

from langchain_openai import OpenAIEmbeddings

if os.environ.get("MILVUS_MODE", "lite").lower() == "lite":
    # pymilvus treats MILVUS_URI as a remote endpoint at import time.
    # For Milvus Lite we use a local file path, so keep that setting under
    # an app-specific name and remove the conflicting env var before import.
    os.environ.pop("MILVUS_URI", None)

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from app.core.config import Settings, get_settings
from app.models.rag import RagRetrievalItem, RagRetrievalRequest, RagRetrievalResponse, RagStoreRequest, RagStoreResponse


class RagService:
    # This service owns vector persistence. Business services should never store or
    # query embeddings directly; they call RAG Service to preserve data autonomy.
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._connect()
        self._embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.embedding_model,
        )

    async def store(self, request: RagStoreRequest) -> RagStoreResponse:
        collection_name = self._collection_name(request.knowledge_base)
        collection = self._ensure_collection(collection_name)
        self._delete_existing_document(collection, request.document_id)

        texts = [chunk.text for chunk in request.chunks]
        vectors = self._embeddings.embed_documents(texts)

        payload = [
            [chunk.chunk_id for chunk in request.chunks],
            [request.document_id for _ in request.chunks],
            texts,
            [chunk.sequence for chunk in request.chunks],
            [request.metadata for _ in request.chunks],
            vectors,
        ]
        collection.insert(payload)
        collection.flush()

        return RagStoreResponse(
            documentId=request.document_id,
            storedChunkCount=len(request.chunks),
            status="completed",
            collectionName=collection_name,
        )

    async def retrieval(self, request: RagRetrievalRequest) -> RagRetrievalResponse:
        collection_name = self._collection_name(request.knowledge_base)
        collection = self._ensure_collection(collection_name)
        collection.load()

        query_vector = self._embeddings.embed_query(request.query)
        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            limit=request.top_k,
            param={
                "metric_type": self.settings.milvus_metric_type,
                "params": {"nprobe": 10},
            },
            output_fields=["chunk_id", "document_id", "text", "metadata"],
        )

        retrieval_items: List[RagRetrievalItem] = []
        raw_hits = results[0] if results else []
        for hit in raw_hits:
            entity = hit.entity
            if not self._matches_filters(entity.get("metadata"), request.filters):
                continue
            retrieval_items.append(
                RagRetrievalItem(
                    chunkId=entity.get("chunk_id"),
                    documentId=entity.get("document_id"),
                    score=float(hit.distance),
                    text=entity.get("text"),
                )
            )

        return RagRetrievalResponse(
            query=request.query,
            results=retrieval_items,
            collectionName=collection_name,
        )

    def _connect(self) -> None:
        connections.connect(
            alias="default",
            uri=self.settings.rag_milvus_uri,
            token=self.settings.milvus_token,
        )

    def _collection_name(self, knowledge_base: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9_]", "_", knowledge_base).lower()
        return f"{self.settings.milvus_collection_prefix}{normalized}"

    def _ensure_collection(self, collection_name: str) -> Collection:
        if utility.has_collection(collection_name):
            collection = Collection(collection_name)
            collection.load()
            return collection

        schema = CollectionSchema(
            fields=[
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=128),
                FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=128),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=8192),
                FieldSchema(name="sequence", dtype=DataType.INT64),
                FieldSchema(name="metadata", dtype=DataType.JSON),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.settings.milvus_vector_dim),
            ],
            description="Canvas RAG chunks",
        )
        collection = Collection(name=collection_name, schema=schema)
        collection.create_index(
            field_name="embedding",
            index_params={
                "index_type": "AUTOINDEX",
                "metric_type": self.settings.milvus_metric_type,
                "params": {},
            },
        )
        collection.load()
        return collection

    def _delete_existing_document(self, collection: Collection, document_id: str) -> None:
        escaped_document_id = document_id.replace('"', '\\"')
        collection.delete(expr=f'document_id == "{escaped_document_id}"')

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, str]) -> bool:
        if not filters:
            return True
        if metadata is None:
            return False
        for key, expected in filters.items():
            actual = metadata.get(key)
            if actual != expected:
                return False
        return True


@lru_cache(maxsize=1)
def get_rag_service() -> RagService:
    return RagService(get_settings())
