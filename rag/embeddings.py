# -*- coding: utf-8 -*-
"""嵌入模型封装：延迟加载 sentence-transformers。"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddings:
    """提供与检索模块兼容的 embed_query / embed_documents 接口。"""

    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list[float]:
        return list(self._model.encode(text, normalize_embeddings=True))

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [list(vec) for vec in vectors]


@lru_cache(maxsize=2)
def get_embedding_model(model_name: str) -> SentenceTransformerEmbeddings:
    """缓存嵌入模型，避免重复加载。"""
    return SentenceTransformerEmbeddings(model_name)
