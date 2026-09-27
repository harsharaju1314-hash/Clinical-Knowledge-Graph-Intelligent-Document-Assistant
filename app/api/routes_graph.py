"""
Knowledge Graph query and ontology routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.ontology import ClinicalOntology
from app.core.schemas import GraphQueryRequest, GraphQueryResponse
from app.graph.knowledge_graph import kg_engine

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.post("/query", response_model=GraphQueryResponse)
def query_graph(query_in: GraphQueryRequest, db: Session = Depends(get_db)):
    """
    Query knowledge graph triples by entity ID, entity type, or relation type,
    with multi-hop neighbor expansion.
    """
    triples = kg_engine.query_subgraph(
        db=db,
        entity_id=query_in.entity_id,
        entity_type=query_in.entity_type,
        relation_type=query_in.relation_type,
        max_hops=query_in.max_hops,
    )
    return GraphQueryResponse(
        triples=triples,
        total_triples=len(triples),
    )


@router.get("/ontology")
def get_ontology_schema():
    """Retrieve the clinical domain ontology schema, allowed entity types, and valid relation triplets."""
    return ClinicalOntology.get_ontology_schema()
