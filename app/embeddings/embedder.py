from __future__ import annotations

from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer


class BGEEmbedder:
    """
    Uses sentence-transformers BGE when available.
    Falls back to TF-IDF vectors when sentence-transformers is not installed.
    """

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._st_model = None
        self._vectorizer: Optional[TfidfVectorizer] = None

        try:
            from sentence_transformers import SentenceTransformer

            self._st_model = SentenceTransformer(model_name)
        except Exception:
            self._st_model = None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self._st_model is not None:
            vectors = self._st_model.encode(texts, normalize_embeddings=True)
            return [vec.tolist() for vec in vectors]

        self._vectorizer = TfidfVectorizer(max_features=1024)
        matrix = self._vectorizer.fit_transform(texts)
        return matrix.toarray().tolist()

    def embed_query(self, query: str) -> list[float]:
        if self._st_model is not None:
            vector = self._st_model.encode([query], normalize_embeddings=True)[0]
            return vector.tolist()

        if self._vectorizer is None:
            raise RuntimeError("Vectorizer not fit. Call embed_texts before embed_query.")

        return self._vectorizer.transform([query]).toarray()[0].tolist()
