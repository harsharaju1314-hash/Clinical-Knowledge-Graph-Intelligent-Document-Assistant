"""
Database models for documents, chunks, knowledge graph entities,
relationships, and query history using SQLAlchemy.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    doc_type = Column(String(64), nullable=False)  # study_summary, protocol, monograph, safety_report
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    section = Column(String(128), default="General")
    embedding_json = Column(JSON, default=list)  # Stored embedding vector
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("DocumentModel", back_populates="chunks")


class EntityModel(Base):
    __tablename__ = "entities"

    id = Column(String(128), primary_key=True)  # Human-readable identifier e.g. DRUG-CARDIOVAX
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    description = Column(Text, default="")
    properties_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    outgoing_relations = relationship(
        "RelationshipModel",
        foreign_keys="RelationshipModel.source_id",
        back_populates="source_entity",
        cascade="all, delete-orphan",
    )
    incoming_relations = relationship(
        "RelationshipModel",
        foreign_keys="RelationshipModel.target_id",
        back_populates="target_entity",
        cascade="all, delete-orphan",
    )


class RelationshipModel(Base):
    __tablename__ = "relationships"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(128), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(64), nullable=False, index=True)
    target_id = Column(String(128), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    properties_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    source_entity = relationship("EntityModel", foreign_keys=[source_id], back_populates="outgoing_relations")
    target_entity = relationship("EntityModel", foreign_keys=[target_id], back_populates="incoming_relations")


class QueryHistoryModel(Base):
    __tablename__ = "query_history"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    rag_sources_json = Column(JSON, default=list)
    graph_triples_json = Column(JSON, default=list)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
