"""
Unit tests for document chunking, embedding generation, and vector retrieval.
"""

from app.ingestion.chunker import document_chunker
from app.vector.embeddings import embedding_service
from app.vector.vector_store import vector_store


def test_chunker_with_sections():
    sample_text = """# Study Title
This is the introduction.

## Clinical Endpoints
The endpoint was primary blood pressure reduction.

## Safety Observations
Adverse events were minimal.
"""
    chunks = document_chunker.chunk_document(sample_text)
    assert len(chunks) >= 3
    sections = [c["section"] for c in chunks]
    assert any("Clinical Endpoints" in s for s in sections)
    assert any("Safety Observations" in s for s in sections)


def test_embedding_generation():
    text = "Cardiovax treats resistant hypertension in clinical trials"
    emb = embedding_service.get_embedding(text)
    assert isinstance(emb, list)
    assert len(emb) == embedding_service.vector_dim


def test_cosine_similarity():
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [1.0, 0.0, 0.0]
    vec_c = [0.0, 1.0, 0.0]

    assert embedding_service.cosine_similarity(vec_a, vec_b) == 1.0
    assert embedding_service.cosine_similarity(vec_a, vec_c) == 0.0


def test_vector_store_search(db_session):
    results = vector_store.search(
        db=db_session,
        query="Cardiovax blood pressure reduction",
        top_k=2,
    )
    assert len(results) > 0
    assert "CARDIO-701" in results[0].document_title or "Cardiovax" in results[0].content
