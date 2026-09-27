"""
Entity and Relationship management API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.models import EntityModel
from app.core.schemas import (
    EntityCreate,
    EntityResponse,
    EntityWithNeighborsResponse,
    RelationshipCreate,
    RelationshipResponse,
)
from app.graph.knowledge_graph import kg_engine

router = APIRouter(tags=["Entities & Relationships"])


@router.get("/entities", response_model=List[EntityResponse])
def list_entities(
    entity_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List clinical entities with optional entity type filter."""
    query = db.query(EntityModel)
    if entity_type:
        query = query.filter(EntityModel.entity_type == entity_type)
    entities = query.offset(offset).limit(limit).all()
    return [EntityResponse.from_orm(e) for e in entities]


@router.get("/entities/{entity_id}", response_model=EntityWithNeighborsResponse)
def get_entity_details(entity_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed entity profile with connected outgoing and incoming relations."""
    entity_data = kg_engine.get_entity_with_connections(db, entity_id)
    if not entity_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID '{entity_id}' not found in knowledge graph.",
        )
    return entity_data


@router.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(entity_in: EntityCreate, db: Session = Depends(get_db)):
    """Create or update a clinical entity conforming to the ontology."""
    try:
        entity_obj = kg_engine.add_entity(db, entity_in)
        return EntityResponse.from_orm(entity_obj)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )


@router.post("/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship(rel_in: RelationshipCreate, db: Session = Depends(get_db)):
    """Create a validated directed relationship between two entities."""
    try:
        rel_obj = kg_engine.add_relationship(db, rel_in)
        return RelationshipResponse.from_orm(rel_obj)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
