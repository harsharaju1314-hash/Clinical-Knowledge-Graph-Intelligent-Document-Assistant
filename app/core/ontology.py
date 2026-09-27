"""
Clinical Ontology Definition Module.

Defines a lightweight, explainable domain ontology for synthetic clinical
and research documents, including allowed entity types, relationship types,
and semantic validation rules.
"""

from typing import Dict, List, Set, Tuple


class EntityType:
    DRUG = "Drug"
    CONDITION = "Condition"
    CLINICAL_STUDY = "Clinical Study"
    OUTCOME = "Outcome"
    ADVERSE_EVENT = "Adverse Event"
    PATIENT_GROUP = "Patient Group"
    ORGANIZATION = "Organization"

    @classmethod
    def all_types(cls) -> Set[str]:
        return {
            cls.DRUG,
            cls.CONDITION,
            cls.CLINICAL_STUDY,
            cls.OUTCOME,
            cls.ADVERSE_EVENT,
            cls.PATIENT_GROUP,
            cls.ORGANIZATION,
        }


class RelationType:
    TREATS = "treats"
    ASSOCIATED_WITH = "associated_with"
    EVALUATES = "evaluates"
    STUDIES = "studies"
    REPORTS = "reports"
    PARTICIPATES_IN = "participates_in"
    SPONSORS = "sponsors"
    MANUFACTURES = "manufactures"

    @classmethod
    def all_relations(cls) -> Set[str]:
        return {
            cls.TREATS,
            cls.ASSOCIATED_WITH,
            cls.EVALUATES,
            cls.STUDIES,
            cls.REPORTS,
            cls.PARTICIPATES_IN,
            cls.SPONSORS,
            cls.MANUFACTURES,
        }


# Canonical Triplet Schema: (Source Type, Relation Type, Target Type)
VALID_ONTOLOGY_RELATIONS: Set[Tuple[str, str, str]] = {
    (EntityType.DRUG, RelationType.TREATS, EntityType.CONDITION),
    (EntityType.DRUG, RelationType.ASSOCIATED_WITH, EntityType.ADVERSE_EVENT),
    (EntityType.CLINICAL_STUDY, RelationType.EVALUATES, EntityType.DRUG),
    (EntityType.CLINICAL_STUDY, RelationType.STUDIES, EntityType.CONDITION),
    (EntityType.CLINICAL_STUDY, RelationType.REPORTS, EntityType.OUTCOME),
    (EntityType.PATIENT_GROUP, RelationType.PARTICIPATES_IN, EntityType.CLINICAL_STUDY),
    (EntityType.ORGANIZATION, RelationType.SPONSORS, EntityType.CLINICAL_STUDY),
    (EntityType.ORGANIZATION, RelationType.MANUFACTURES, EntityType.DRUG),
}


class ClinicalOntology:
    """Validator and query helper for the clinical ontology."""

    @staticmethod
    def is_valid_entity_type(entity_type: str) -> bool:
        """Check if an entity type is recognized by the ontology."""
        return entity_type in EntityType.all_types()

    @staticmethod
    def is_valid_relation_type(relation_type: str) -> bool:
        """Check if a relation type is recognized."""
        return relation_type in RelationType.all_relations()

    @staticmethod
    def validate_relationship(
        source_type: str, relation_type: str, target_type: str
    ) -> Tuple[bool, str]:
        """
        Validate whether a triple conforming to (source_type, relation, target_type)
        is allowed by the domain ontology.
        """
        if not ClinicalOntology.is_valid_entity_type(source_type):
            return False, f"Invalid source entity type: '{source_type}'"

        if not ClinicalOntology.is_valid_entity_type(target_type):
            return False, f"Invalid target entity type: '{target_type}'"

        if not ClinicalOntology.is_valid_relation_type(relation_type):
            return False, f"Invalid relation type: '{relation_type}'"

        triple = (source_type, relation_type, target_type)
        if triple not in VALID_ONTOLOGY_RELATIONS:
            return (
                False,
                f"Relationship '{source_type} -> {relation_type} -> {target_type}' "
                f"violates ontology constraints.",
            )

        return True, "Valid"

    @staticmethod
    def get_ontology_schema() -> Dict[str, List]:
        """Return the complete ontology definition structure."""
        return {
            "entity_types": sorted(list(EntityType.all_types())),
            "relation_types": sorted(list(RelationType.all_relations())),
            "allowed_triplets": [
                {"source": s, "relation": r, "target": t}
                for s, r, t in sorted(list(VALID_ONTOLOGY_RELATIONS))
            ],
        }
