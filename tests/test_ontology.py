"""
Unit tests for the clinical domain ontology.
"""

from app.core.ontology import ClinicalOntology, EntityType, RelationType


def test_valid_entity_types():
    assert ClinicalOntology.is_valid_entity_type(EntityType.DRUG) is True
    assert ClinicalOntology.is_valid_entity_type(EntityType.CONDITION) is True
    assert ClinicalOntology.is_valid_entity_type(EntityType.CLINICAL_STUDY) is True
    assert ClinicalOntology.is_valid_entity_type("InvalidType") is False


def test_valid_relation_types():
    assert ClinicalOntology.is_valid_relation_type(RelationType.TREATS) is True
    assert ClinicalOntology.is_valid_relation_type(RelationType.EVALUATES) is True
    assert ClinicalOntology.is_valid_relation_type("invalid_rel") is False


def test_valid_ontology_triplets():
    # Drug -> treats -> Condition
    is_valid, msg = ClinicalOntology.validate_relationship(
        EntityType.DRUG, RelationType.TREATS, EntityType.CONDITION
    )
    assert is_valid is True

    # Clinical Study -> evaluates -> Drug
    is_valid, msg = ClinicalOntology.validate_relationship(
        EntityType.CLINICAL_STUDY, RelationType.EVALUATES, EntityType.DRUG
    )
    assert is_valid is True


def test_invalid_ontology_triplets():
    # Invalid: Drug -> evaluates -> Condition (Study evaluates Drug)
    is_valid, msg = ClinicalOntology.validate_relationship(
        EntityType.DRUG, RelationType.EVALUATES, EntityType.CONDITION
    )
    assert is_valid is False
    assert "violates ontology constraints" in msg

    # Invalid: Unknown entity type
    is_valid, msg = ClinicalOntology.validate_relationship(
        "AlienEntity", RelationType.TREATS, EntityType.CONDITION
    )
    assert is_valid is False
    assert "Invalid source entity type" in msg


def test_ontology_schema_export():
    schema = ClinicalOntology.get_ontology_schema()
    assert "entity_types" in schema
    assert "relation_types" in schema
    assert "allowed_triplets" in schema
    assert len(schema["entity_types"]) == 7
    assert len(schema["allowed_triplets"]) >= 8
