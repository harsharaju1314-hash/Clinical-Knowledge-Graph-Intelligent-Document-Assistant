"""
Semantic Search API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.schemas import SearchRequest, SearchResponse
from app.vector.vector_store import vector_store

router = APIRouter(prefix="/search", tags=["Semantic Search"])


@router.post("", response_model=SearchResponse)
def semantic_search(search_in: SearchRequest, db: Session = Depends(get_db)):
    """
    Perform semantic vector similarity search over document chunks.
    Computes cosine similarity between query embeddings and chunk embeddings.
    """
    if not search_in.query or not search_in.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty."
        )

    results = vector_store.search(
        db=db,
        query=search_in.query,
        top_k=search_in.top_k,
        min_score=search_in.min_score,
    )

    return SearchResponse(
        query=search_in.query,
        total_results=len(results),
        results=results,
    )
