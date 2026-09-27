"""
Vector store implementation for semantic search over indexed document chunks.
Uses cosine similarity over stored chunk embeddings with database metadata enrichment.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.models import DocumentChunkModel, DocumentModel
from app.core.schemas import SearchResultItem
from app.vector.embeddings import embedding_service


class VectorStoreService:
    @staticmethod
    def search(
        db: Session,
        query: str,
        top_k: int = 4,
        min_score: float = 0.0,
        doc_type_filter: Optional[str] = None,
    ) -> List[SearchResultItem]:
        """
        Perform semantic similarity search over all document chunks.
        Computes cosine similarity between query embedding and chunk embeddings.
        """
        query_embedding = embedding_service.get_embedding(query)

        # Query all chunks with their associated document metadata
        query_obj = db.query(DocumentChunkModel).join(DocumentModel)
        if doc_type_filter:
            query_obj = query_obj.filter(DocumentModel.doc_type == doc_type_filter)

        chunks = query_obj.all()
        if not chunks:
            return []

        scored_results = []
        for chunk in chunks:
            chunk_embedding = chunk.embedding_json
            if not chunk_embedding:
                # Generate on-the-fly if missing
                chunk_embedding = embedding_service.get_embedding(chunk.content)
                chunk.embedding_json = chunk_embedding

            score = embedding_service.cosine_similarity(query_embedding, chunk_embedding)

            # Boost score slightly if exact keywords match
            query_tokens = set(query.lower().split())
            content_lower = chunk.content.lower()
            keyword_matches = sum(1 for token in query_tokens if len(token) > 3 and token in content_lower)
            adjusted_score = min(1.0, score + (0.05 * keyword_matches))

            if adjusted_score >= min_score:
                scored_results.append((adjusted_score, chunk))

        # Sort by similarity score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        top_results = scored_results[:top_k]

        results: List[SearchResultItem] = []
        for score, chunk in top_results:
            results.append(
                SearchResultItem(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    document_title=chunk.document.title if chunk.document else "Unknown",
                    section=chunk.section or "General",
                    content=chunk.content,
                    similarity_score=round(float(score), 4),
                )
            )

        return results


vector_store = VectorStoreService()
