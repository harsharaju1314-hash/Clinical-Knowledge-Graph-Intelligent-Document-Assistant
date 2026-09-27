"""
Document management API routes.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.schemas import DocumentCreate, DocumentResponse
from app.ingestion.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def ingest_document(doc_in: DocumentCreate, db: Session = Depends(get_db)):
    """Ingest a new synthetic clinical document, chunk it, and index it into the Knowledge Graph and vector index."""
    if not doc_in.content or not doc_in.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content cannot be empty."
        )
    return document_service.ingest_document(db, doc_in)


@router.get("", response_model=List[DocumentResponse])
def list_documents(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """List all ingested documents with metadata."""
    return document_service.list_documents(db, limit=limit, offset=offset)


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Retrieve document metadata and all generated chunks by ID."""
    doc = document_service.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{doc_id}' was not found."
        )
    return doc
