"""
Retrieval Agent (Agent 1).
Responsible for semantic vector search, chunk filtering, and citation preparation.
"""

from typing import List, Tuple
from sqlalchemy.orm import Session
from app.core.schemas import SearchResultItem, Citation
from app.vector.vector_store import vector_store


class RetrievalAgent:
    """Agent 1: Searches and ranks relevant clinical document chunks."""

    def __init__(self, agent_name: str = "Retrieval Agent"):
        self.agent_name = agent_name

    def run(
        self, db: Session, question: str, top_k: int = 4, min_score: float = 0.15
    ) -> Tuple[List[SearchResultItem], List[Citation], str]:
        """
        Execute semantic retrieval over document chunks.
        Returns: (results, citations, trace_summary)
        """
        results = vector_store.search(
            db=db,
            query=question,
            top_k=top_k,
            min_score=min_score,
        )

        citations: List[Citation] = []
        for r in results:
            citations.append(
                Citation(
                    document_id=r.document_id,
                    document_title=r.document_title,
                    section=r.section,
                    chunk_index=0,
                    similarity_score=r.similarity_score,
                )
            )

        summary = f"Retrieved {len(results)} relevant synthetic document chunks (top similarity score: {results[0].similarity_score if results else 0.0})."
        return results, citations, summary


retrieval_agent = RetrievalAgent()
