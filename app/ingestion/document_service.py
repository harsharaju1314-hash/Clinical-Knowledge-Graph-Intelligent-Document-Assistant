"""
Document Ingestion Service.
Coordinates document parsing, chunking, embedding generation,
entity extraction, and knowledge graph linkage.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.models import DocumentModel, DocumentChunkModel
from app.core.schemas import DocumentCreate, DocumentResponse
from app.ingestion.chunker import document_chunker
from app.ingestion.extractor import clinical_extractor
from app.vector.embeddings import embedding_service
from app.graph.knowledge_graph import kg_engine


class DocumentService:
    @staticmethod
    def ingest_document(db: Session, doc_in: DocumentCreate) -> DocumentResponse:
        """
        Ingest a clinical document:
        1. Save document record
        2. Chunk document text
        3. Compute and store chunk embeddings
        4. Extract entities & relationships and sync to Knowledge Graph
        """
        doc_obj = DocumentModel(
            title=doc_in.title,
            doc_type=doc_in.doc_type,
            content=doc_in.content,
            metadata_json=doc_in.metadata or {},
        )
        db.add(doc_obj)
        db.commit()
        db.refresh(doc_obj)

        # Chunk document
        chunks_data = document_chunker.chunk_document(doc_in.content)
        chunk_texts = [c["content"] for c in chunks_data]
        embedding_service.update_vocabulary(chunk_texts)

        for c_data in chunks_data:
            embedding = embedding_service.get_embedding(c_data["content"])
            chunk_obj = DocumentChunkModel(
                document_id=doc_obj.id,
                chunk_index=c_data["chunk_index"],
                content=c_data["content"],
                section=c_data["section"],
                embedding_json=embedding,
            )
            db.add(chunk_obj)

        # Extract entities and relationships
        entities = clinical_extractor.extract_entities_from_text(doc_in.content)
        for ent in entities:
            try:
                kg_engine.add_entity(db, ent)
            except Exception:
                pass

        relations = clinical_extractor.extract_relations_from_document(doc_in.content, entities)
        for rel in relations:
            try:
                kg_engine.add_relationship(db, rel)
            except Exception:
                pass

        db.commit()
        db.refresh(doc_obj)

        return DocumentResponse.from_orm(doc_obj)

    @staticmethod
    def list_documents(db: Session, limit: int = 50, offset: int = 0) -> List[DocumentResponse]:
        """List documents with pagination."""
        docs = db.query(DocumentModel).offset(offset).limit(limit).all()
        return [DocumentResponse.from_orm(d) for d in docs]

    @staticmethod
    def get_document_by_id(db: Session, doc_id: str) -> Optional[DocumentResponse]:
        """Retrieve a specific document with its chunks."""
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        if not doc:
            return None
        return DocumentResponse.from_orm(doc)


document_service = DocumentService()
