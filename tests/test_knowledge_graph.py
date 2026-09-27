"""
Unit tests for Knowledge Graph engine and relational storage.
"""

import pytest
from app.core.schemas import EntityCreate, RelationshipCreate
from app.core.ontology import EntityType, RelationType
from app.graph.knowledge_graph import kg_engine


def test_add_entity_valid(db_session):
    ent = EntityCreate(
        id="DRUG-TEST-101",
        name="TestVax",
        entity_type=EntityType.DRUG,
        description="A test pharmaceutical entity",
    )
    obj = kg_engine.add_entity(db_session, ent)
    assert obj.id == "DRUG-TEST-101"
    assert obj.name == "TestVax"


def test_add_entity_invalid_type(db_session):
    ent = EntityCreate(
        id="INVALID-01",
        name="BadEntity",
        entity_type="UnknownType",
    )
    with pytest.raises(ValueError, match="Invalid entity type"):
        kg_engine.add_entity(db_session, ent)


def test_add_relationship_valid(db_session):
    # Create test entities
    e1 = EntityCreate(id="DRUG-ALPHA", name="AlphaDrug", entity_type=EntityType.DRUG)
    e2 = EntityCreate(id="COND-BETA", name="BetaDisorder", entity_type=EntityType.CONDITION)
    kg_engine.add_entity(db_session, e1)
    kg_engine.add_entity(db_session, e2)

    rel = RelationshipCreate(
        source_id="DRUG-ALPHA",
        relation_type=RelationType.TREATS,
        target_id="COND-BETA",
    )
    rel_obj = kg_engine.add_relationship(db_session, rel)
    assert rel_obj.source_id == "DRUG-ALPHA"
    assert rel_obj.relation_type == RelationType.TREATS
    assert rel_obj.target_id == "COND-BETA"


def test_add_relationship_ontology_violation(db_session):
    # Invalid: Condition -> treats -> Drug
    e1 = EntityCreate(id="DRUG-X", name="DrugX", entity_type=EntityType.DRUG)
    e2 = EntityCreate(id="COND-Y", name="CondY", entity_type=EntityType.CONDITION)
    kg_engine.add_entity(db_session, e1)
    kg_engine.add_entity(db_session, e2)

    rel = RelationshipCreate(
        source_id="COND-Y",
        relation_type=RelationType.TREATS,
        target_id="DRUG-X",
    )
    with pytest.raises(ValueError, match="Ontology Constraint Violation"):
        kg_engine.add_relationship(db_session, rel)


def test_query_subgraph_by_entity(db_session):
    triples = kg_engine.query_subgraph(
        db_session,
        entity_id="DRUG-CARDIOVAX",
        max_hops=1,
    )
    assert len(triples) >= 1
    relations = [t.relation for t in triples]
    assert "treats" in relations or "associated_with" in relations


def test_extract_subgraph_for_query_text(db_session):
    triples = kg_engine.extract_subgraph_for_query_text(
        db_session,
        query_text="What adverse events are associated with Cardiovax?",
        max_hops=1,
    )
    assert len(triples) > 0
    source_names = [t.source_name for t in triples]
    assert "Cardiovax" in source_names
