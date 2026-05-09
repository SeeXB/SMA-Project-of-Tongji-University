from __future__ import annotations

from functools import lru_cache
from typing import List

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer


class EmbeddingModel:
    """Local sentence embedding model based on all-MiniLM-L6-v2."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._tokenizer, self._model = self._load_model(model_name)

    def embed_text(self, text: str) -> List[float]:
        encoded_input = self._tokenizer((text or ""), padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            model_output = self._model(**encoded_input)

        token_embeddings = model_output[0]
        attention_mask = encoded_input["attention_mask"]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sentence_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings[0].tolist()

    @staticmethod
    @lru_cache(maxsize=2)
    def _load_model(model_name: str):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        model.eval()
        return tokenizer, model
