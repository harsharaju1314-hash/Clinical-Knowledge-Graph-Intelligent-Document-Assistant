"""
Clinical Entity and Relation Extraction.
Extracts ontology-compliant entities and relations from document text and metadata.
"""

import re
from typing import List, Dict, Any, Tuple
from app.core.ontology import EntityType, RelationType, ClinicalOntology
from app.core.schemas import EntityCreate, RelationshipCreate


class ClinicalExtractor:
    # Known clinical lexicon mapping for synthetic data extraction
    KNOWN_DRUGS = {
        "cardiovax": ("DRUG-CARDIOVAX", "Cardiovax"),
        "neurocalm": ("DRUG-NEUROCALM", "Neurocalm-XR"),
        "oncotarget": ("DRUG-ONCOTARGET-B", "Oncotarget-B"),
        "arthritin": ("DRUG-ARTHRITIN", "Arthritin-Bio"),
        "glycostat": ("DRUG-GLYCOSTAT", "Glycostat"),
    }

    KNOWN_CONDITIONS = {
        "hypertension": ("COND-HYPERTENSION", "Resistant Hypertension"),
        "generalized anxiety": ("COND-GAD", "Generalized Anxiety Disorder"),
        "breast cancer": ("COND-BREAST-CANCER", "HER2+ Metastatic Breast Cancer"),
        "rheumatoid arthritis": ("COND-RA", "Refractory Rheumatoid Arthritis"),
        "type 2 diabetes": ("COND-T2D", "Type 2 Diabetes Mellitus"),
    }

    KNOWN_STUDIES = {
        "cardio-701": ("STUDY-CARDIO-701", "CARDIO-701 Phase 3 Trial"),
        "neuro-302": ("STUDY-NEURO-302", "NEURO-302 Phase 2b Protocol"),
        "onco-505": ("STUDY-ONCO-505", "ONCO-505 Safety and Efficacy Dossier"),
        "immuno-109": ("STUDY-IMMUNO-109", "IMMUNO-109 Clinical Trial Report"),
        "metabo-204": ("STUDY-METABO-204", "METABO-204 Monograph and Trial"),
    }

    KNOWN_ADVERSE_EVENTS = {
        "hypotension": ("AE-HYPOTENSION", "Orthostatic Hypotension"),
        "somnolence": ("AE-SOMNOLENCE", "Transient Somnolence"),
        "neutropenia": ("AE-NEUTROPENIA", "Grade 2 Neutropenia"),
        "elevated alt": ("AE-ELEVATED-ALT", "Mildly Elevated ALT/AST"),
        "gastrointestinal distress": ("AE-GI-DISTRESS", "Gastrointestinal Distress"),
    }

    KNOWN_ORGANIZATIONS = {
        "novabio": ("ORG-NOVABIO", "NovaBio Pharmaceuticals"),
        "apex clinical": ("ORG-APEX", "Apex Clinical Research Institute"),
        "oncolab": ("ORG-ONCOLAB", "OncoLab Therapeutics"),
        "immunocare": ("ORG-IMMUNOCARE", "ImmunoCare International"),
        "endogen": ("ORG-ENDOGEN", "EndoGen Therapeutics"),
    }

    def extract_entities_from_text(self, text: str) -> List[EntityCreate]:
        """Extract ontology-compliant entities found in text."""
        entities: List[EntityCreate] = []
        text_lower = text.lower()
        extracted_ids = set()

        # Check Drugs
        for key, (ent_id, name) in self.KNOWN_DRUGS.items():
            if key in text_lower and ent_id not in extracted_ids:
                extracted_ids.add(ent_id)
                entities.append(
                    EntityCreate(
                        id=ent_id,
                        name=name,
                        entity_type=EntityType.DRUG,
                        description=f"Synthetic therapeutic drug candidate: {name}",
                        properties={"status": "Investigational / Synthetic"},
                    )
                )

        # Check Conditions
        for key, (ent_id, name) in self.KNOWN_CONDITIONS.items():
            if key in text_lower and ent_id not in extracted_ids:
                extracted_ids.add(ent_id)
                entities.append(
                    EntityCreate(
                        id=ent_id,
                        name=name,
                        entity_type=EntityType.CONDITION,
                        description=f"Synthetic clinical condition: {name}",
                        properties={"category": "Clinical Condition"},
                    )
                )

        # Check Studies
        for key, (ent_id, name) in self.KNOWN_STUDIES.items():
            if key in text_lower and ent_id not in extracted_ids:
                extracted_ids.add(ent_id)
                entities.append(
                    EntityCreate(
                        id=ent_id,
                        name=name,
                        entity_type=EntityType.CLINICAL_STUDY,
                        description=f"Synthetic clinical evaluation study: {name}",
                        properties={"phase": "Phase 2/3"},
                    )
                )

        # Check Adverse Events
        for key, (ent_id, name) in self.KNOWN_ADVERSE_EVENTS.items():
            if key in text_lower and ent_id not in extracted_ids:
                extracted_ids.add(ent_id)
                entities.append(
                    EntityCreate(
                        id=ent_id,
                        name=name,
                        entity_type=EntityType.ADVERSE_EVENT,
                        description=f"Documented synthetic adverse event: {name}",
                        properties={"severity": "Documented"},
                    )
                )

        # Check Organizations
        for key, (ent_id, name) in self.KNOWN_ORGANIZATIONS.items():
            if key in text_lower and ent_id not in extracted_ids:
                extracted_ids.add(ent_id)
                entities.append(
                    EntityCreate(
                        id=ent_id,
                        name=name,
                        entity_type=EntityType.ORGANIZATION,
                        description=f"Synthetic organization sponsor: {name}",
                        properties={"type": "Biotech/Sponsor"},
                    )
                )

        return entities

    def extract_relations_from_document(
        self, text: str, entities: List[EntityCreate]
    ) -> List[RelationshipCreate]:
        """Derive validated ontology relations among extracted entities."""
        relations: List[RelationshipCreate] = []
        ent_by_type: Dict[str, List[EntityCreate]] = {}
        for ent in entities:
            ent_by_type.setdefault(ent.entity_type, []).append(ent)

        drugs = ent_by_type.get(EntityType.DRUG, [])
        conditions = ent_by_type.get(EntityType.CONDITION, [])
        studies = ent_by_type.get(EntityType.CLINICAL_STUDY, [])
        adverse_events = ent_by_type.get(EntityType.ADVERSE_EVENT, [])
        orgs = ent_by_type.get(EntityType.ORGANIZATION, [])

        # Drug -> treats -> Condition
        for d in drugs:
            for c in conditions:
                relations.append(
                    RelationshipCreate(
                        source_id=d.id,
                        relation_type=RelationType.TREATS,
                        target_id=c.id,
                        properties={"source": "Document Extraction"},
                    )
                )

        # Drug -> associated_with -> Adverse Event
        for d in drugs:
            for ae in adverse_events:
                relations.append(
                    RelationshipCreate(
                        source_id=d.id,
                        relation_type=RelationType.ASSOCIATED_WITH,
                        target_id=ae.id,
                        properties={"source": "Document Extraction"},
                    )
                )

        # Clinical Study -> evaluates -> Drug
        for s in studies:
            for d in drugs:
                relations.append(
                    RelationshipCreate(
                        source_id=s.id,
                        relation_type=RelationType.EVALUATES,
                        target_id=d.id,
                        properties={"source": "Document Extraction"},
                    )
                )

        # Clinical Study -> studies -> Condition
        for s in studies:
            for c in conditions:
                relations.append(
                    RelationshipCreate(
                        source_id=s.id,
                        relation_type=RelationType.STUDIES,
                        target_id=c.id,
                        properties={"source": "Document Extraction"},
                    )
                )

        # Organization -> sponsors -> Clinical Study
        for o in orgs:
            for s in studies:
                relations.append(
                    RelationshipCreate(
                        source_id=o.id,
                        relation_type=RelationType.SPONSORS,
                        target_id=s.id,
                        properties={"source": "Document Extraction"},
                    )
                )

        return relations


clinical_extractor = ClinicalExtractor()
