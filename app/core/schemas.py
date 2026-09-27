"""
Pydantic schemas for request validation and response serialization.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# -------------------------------------------------------------------------
# Document Schemas
# -------------------------------------------------------------------------
class DocumentCreate(BaseModel):
    title: str = Field(..., description="Document title", example="CARDIO-701 Phase 3 Clinical Study Summary")
    doc_type: str = Field(..., description="Document type", example="study_summary")
    content: str = Field(..., description="Full text content of the clinical document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata key-value pairs")


class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    section: str

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    title: str
    doc_type: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_json")
    created_at: datetime
    chunks: Optional[List[DocumentChunkResponse]] = None

    class Config:
        from_attributes = True
        populate_by_name = True


# -------------------------------------------------------------------------
# Entity & Relationship Schemas
# -------------------------------------------------------------------------
class EntityCreate(BaseModel):
    id: str = Field(..., description="Unique entity identifier", example="DRUG-CARDIOVAX")
    name: str = Field(..., description="Human-readable entity name", example="Cardiovax")
    entity_type: str = Field(..., description="Type conforming to ontology", example="Drug")
    description: str = Field("", description="Optional entity description")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Entity attributes")


class EntityResponse(BaseModel):
    id: str
    name: str
    entity_type: str
    description: str
    properties: Dict[str, Any] = Field(default_factory=dict, alias="properties_json")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class RelationshipCreate(BaseModel):
    source_id: str = Field(..., description="Source entity ID", example="DRUG-CARDIOVAX")
    relation_type: str = Field(..., description="Relationship type", example="treats")
    target_id: str = Field(..., description="Target entity ID", example="COND-HYPERTENSION")
    properties: Dict[str, Any] = Field(default_factory=dict)


class RelationshipResponse(BaseModel):
    id: str
    source_id: str
    relation_type: str
    target_id: str
    properties: Dict[str, Any] = Field(default_factory=dict, alias="properties_json")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class GraphQueryRequest(BaseModel):
    entity_id: Optional[str] = Field(None, description="Optional entity ID to center the query on")
    entity_type: Optional[str] = Field(None, description="Filter by source or target entity type")
    relation_type: Optional[str] = Field(None, description="Filter by relationship type")
    max_hops: int = Field(1, ge=1, le=3, description="Maximum traversal depth (1-3 hops)")


class GraphTripleItem(BaseModel):
    source_id: str
    source_name: str
    source_type: str
    relation: str
    target_id: str
    target_name: str
    target_type: str


class GraphQueryResponse(BaseModel):
    triples: List[GraphTripleItem]
    total_triples: int


class EntityWithNeighborsResponse(BaseModel):
    entity: EntityResponse
    outgoing: List[Dict[str, Any]]
    incoming: List[Dict[str, Any]]


# -------------------------------------------------------------------------
# Semantic Search Schemas
# -------------------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query", example="What drugs are used for hypertension?")
    top_k: int = Field(4, ge=1, le=20, description="Number of chunks to retrieve")
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity score threshold")


class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    section: str
    content: str
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]


# -------------------------------------------------------------------------
# Multi-Agent RAG Schemas
# -------------------------------------------------------------------------
class AskRequest(BaseModel):
    question: str = Field(..., description="Clinical inquiry or research question", example="What studies evaluate Cardiovax for Resistant Hypertension?")
    include_graph: bool = Field(True, description="Whether to include knowledge graph traversal")
    include_vector: bool = Field(True, description="Whether to include semantic vector retrieval")
    top_k: int = Field(3, ge=1, le=10)


class Citation(BaseModel):
    document_id: str
    document_title: str
    section: str
    chunk_index: int
    similarity_score: float


class AgentTraceStep(BaseModel):
    agent_name: str
    status: str
    summary: str


class AskResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    citations: List[Citation]
    graph_context: List[GraphTripleItem]
    agent_traces: List[AgentTraceStep]
    disclaimer: str = (
        "SYNTHETIC DATA NOTICE: All medical and clinical information in this response is synthetic/fictitious. "
        "This system does not provide medical diagnoses, treatment advice, or clinical decisions."
    )


# -------------------------------------------------------------------------
# Health and Seed Schemas
# -------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    database_status: str
    total_documents: int
    total_chunks: int
    total_entities: int
    total_relationships: int


class SeedResponse(BaseModel):
    status: str
    message: str
    documents_seeded: int
    chunks_created: int
    entities_seeded: int
    relationships_seeded: int
