"""
Embedding generation and similarity utilities.
Provides deterministic dense vector embeddings via TF-IDF / Subword n-grams
and optional external LLM/Embedding API providers.
"""

import math
import re
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from app.config import settings


class EmbeddingService:
    def __init__(self, vector_dim: int = 128):
        self.vector_dim = vector_dim
        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=vector_dim,
            stop_words="english",
        )
        self._is_fitted = False
        self._corpus: List[str] = [
            "Cardiovax treats resistant hypertension in adult patients",
            "Neurocalm-XR evaluates generalized anxiety disorder safety",
            "Oncotarget-B HER2+ metastatic breast cancer oncology outcome",
            "Arthritin-Bio refractory rheumatoid arthritis ACR50 response",
            "Glycostat type 2 diabetes mellitus HbA1c reduction",
            "Adverse event hypotension headache nausea elevation",
            "Clinical study randomized double-blind placebo-controlled trial",
            "Organization pharmaceutical bio research institute university",
            "Patient group adult subjects aged 18 to 75 years",
        ]
        self._fit_initial_corpus()

    def _fit_initial_corpus(self) -> None:
        """Fit the vectorizer with foundational vocabulary."""
        try:
            self._vectorizer.fit(self._corpus)
            self._is_fitted = True
        except Exception:
            self._is_fitted = False

    def update_vocabulary(self, texts: List[str]) -> None:
        """Dynamically expand vocabulary with newly ingested texts."""
        if not texts:
            return
        combined = list(set(self._corpus + texts))
        self._corpus = combined
        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=self.vector_dim,
            stop_words="english",
        )
        self._vectorizer.fit(self._corpus)
        self._is_fitted = True

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate a normalized dense embedding vector for a given text string.
        Uses TF-IDF feature projection with fallback to deterministic character hashing.
        """
        if not text or not text.strip():
            return [0.0] * self.vector_dim

        # Check if OpenAI embeddings are enabled and key is present
        if settings.embedding_provider == "openai" and settings.openai_api_key:
            try:
                import requests
                headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
                payload = {"input": text, "model": "text-embedding-3-small"}
                resp = requests.post("https://api.openai.com/v1/embeddings", json=payload, headers=headers, timeout=10)
                if resp.status_code == 200:
                    return resp.json()["data"][0]["embedding"]
            except Exception:
                pass  # Fall back to deterministic local embedding

        # Deterministic local TF-IDF embedding
        cleaned_text = re.sub(r"[^\w\s-]", " ", text.lower())
        if self._is_fitted:
            try:
                vec = self._vectorizer.transform([cleaned_text]).toarray()[0]
                # If vector is all zeros (out-of-vocabulary), generate dense pseudo-semantic hash
                if np.linalg.norm(vec) > 0:
                    norm_vec = vec / np.linalg.norm(vec)
                    return norm_vec.tolist()
            except Exception:
                pass

        # Dense character/token hash fallback
        return self._compute_token_hash_vector(cleaned_text)

    def _compute_token_hash_vector(self, text: str) -> List[float]:
        """Compute a deterministic, dense normalized pseudo-embedding."""
        vec = np.zeros(self.vector_dim, dtype=float)
        tokens = text.split()
        if not tokens:
            return vec.tolist()

        for idx, token in enumerate(tokens):
            h = hash(token) % self.vector_dim
            weight = 1.0 / math.sqrt(idx + 1)
            vec[h] += weight

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        a = np.array(vec_a, dtype=float)
        b = np.array(vec_b, dtype=float)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))


# Singleton instance
embedding_service = EmbeddingService()
