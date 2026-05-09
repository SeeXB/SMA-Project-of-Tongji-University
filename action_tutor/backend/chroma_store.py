from __future__ import annotations

import os
from typing import Any, Dict, List


class ChromaStore:
	def __init__(self, persist_dir: str, collection_name: str = "learning_traces") -> None:
		self.persist_dir = persist_dir
		self.collection_name = collection_name
		self._memory: List[Dict[str, Any]] = []
		self._collection = None

		os.makedirs(self.persist_dir, exist_ok=True)
		try:
			import chromadb

			client = chromadb.PersistentClient(path=self.persist_dir)
			self._collection = client.get_or_create_collection(name=self.collection_name)
		except Exception:
			# If Chroma is unavailable at runtime, keep a local in-memory store.
			self._collection = None

	def add_concept(self, concept: str, embedding: List[float], metadata: Dict[str, Any], document: str) -> None:
		record_id = f"{concept}:{metadata.get('last_seen', 'na')}:{len(self._memory)}"
		self._memory.append(
			{
				"id": record_id,
				"concept": concept,
				"embedding": embedding,
				"metadata": metadata,
				"document": document,
			}
		)

		if self._collection is not None:
			self._collection.add(
				ids=[record_id],
				documents=[document],
				embeddings=[embedding],
				metadatas=[metadata],
			)

	def query(self, embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
		if self._collection is not None:
			return self._collection.query(query_embeddings=[embedding], n_results=n_results)

		# Lightweight cosine-like retrieval from fallback memory.
		def dot(a: List[float], b: List[float]) -> float:
			return sum(x * y for x, y in zip(a, b))

		ranked = sorted(self._memory, key=lambda row: dot(row["embedding"], embedding), reverse=True)
		top = ranked[:n_results]
		return {
			"ids": [[row["id"] for row in top]],
			"documents": [[row["document"] for row in top]],
			"metadatas": [[row["metadata"] for row in top]],
		}

