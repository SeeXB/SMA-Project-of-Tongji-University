from pydantic import BaseModel, Field


class RagChunk(BaseModel):
    chunk_id: str = Field(..., alias="chunkId")
    text: str
    sequence: int


class RagStoreRequest(BaseModel):
    knowledge_base: str = Field(..., alias="knowledgeBase")
    document_id: str = Field(..., alias="documentId")
    metadata: dict[str, str] = Field(default_factory=dict)
    chunks: list[RagChunk]


class RagStoreResponse(BaseModel):
    document_id: str = Field(..., alias="documentId")
    stored_chunk_count: int = Field(..., alias="storedChunkCount")
    status: str
    collection_name: str = Field(..., alias="collectionName")


class RagRetrievalRequest(BaseModel):
    knowledge_base: str = Field(..., alias="knowledgeBase")
    query: str
    top_k: int = Field(5, alias="topK")
    filters: dict[str, str] = Field(default_factory=dict)


class RagRetrievalItem(BaseModel):
    chunk_id: str = Field(..., alias="chunkId")
    document_id: str = Field(..., alias="documentId")
    score: float
    text: str


class RagRetrievalResponse(BaseModel):
    query: str
    results: list[RagRetrievalItem]
    collection_name: str = Field(..., alias="collectionName")
