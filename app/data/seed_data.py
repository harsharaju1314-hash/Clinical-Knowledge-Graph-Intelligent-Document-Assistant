"""
Synthetic Clinical Dataset Definitions and Seeder.
Contains fictitious clinical study reports, drug profiles, safety monographs,
and baseline knowledge graph entities.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.schemas import DocumentCreate, EntityCreate, RelationshipCreate
from app.core.ontology import EntityType, RelationType
from app.ingestion.document_service import document_service
from app.graph.knowledge_graph import kg_engine

SYNTHETIC_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "title": "CARDIO-701 Phase 3 Clinical Study Summary: Cardiovax in Resistant Hypertension",
        "doc_type": "study_summary",
        "metadata": {
            "trial_id": "CARDIO-701",
            "phase": "Phase 3",
            "sponsor": "NovaBio Pharmaceuticals",
            "condition": "Resistant Hypertension",
            "investigational_drug": "Cardiovax",
        },
        "content": """# CARDIO-701 Phase 3 Clinical Study Summary

## Executive Summary
This document summarizes the findings from the CARDIO-701 Phase 3 randomized, double-blind, placebo-controlled trial evaluating Cardiovax in adult patients diagnosed with Resistant Hypertension. The study was conducted by NovaBio Pharmaceuticals in collaboration with the Apex Clinical Research Institute.

## Study Objectives and Patient Population
The trial enrolled 640 adult participants aged 18 to 75 with confirmed Resistant Hypertension who demonstrated inadequate blood pressure control on triple antihypertensive therapy. The primary objective was to assess systolic blood pressure (SBP) reduction at Week 12.

## Efficacy and Reported Outcomes
Cardiovax administered at 50 mg orally once daily demonstrated a statistically significant mean reduction in seated systolic blood pressure of 18.5 mmHg compared to 3.2 mmHg in the placebo arm (p < 0.001). Additionally, diastolic blood pressure decreased by an average of 9.8 mmHg.

## Safety Profile and Adverse Events
The safety profile indicated that Cardiovax was generally well-tolerated. The most common treatment-emergent adverse event was Orthostatic Hypotension reported in 6.4% of active group subjects versus 1.2% in placebo. No cases of acute renal failure or fatal cardiotoxicity were observed during the 24-week follow-up period.
""",
    },
    {
        "title": "NEURO-302 Phase 2b Protocol: Neurocalm-XR in Generalized Anxiety Disorder",
        "doc_type": "protocol_summary",
        "metadata": {
            "trial_id": "NEURO-302",
            "phase": "Phase 2b",
            "sponsor": "Apex Clinical Research Institute",
            "condition": "Generalized Anxiety Disorder",
            "investigational_drug": "Neurocalm-XR",
        },
        "content": """# NEURO-302 Phase 2b Protocol Summary

## Background and Rationale
Generalized Anxiety Disorder (GAD) represents a chronic neuropsychiatric condition requiring sustained therapeutic management. NEURO-302 evaluates the novel allosteric neuromodulator Neurocalm-XR developed by Apex Clinical Research Institute.

## Study Design and Enrollment Criteria
A total of 320 outpatient participants meeting DSM criteria for moderate-to-severe Generalized Anxiety Disorder were randomized 1:1 to receive either Neurocalm-XR 20 mg extended release daily or active comparator.

## Primary Outcome Measures
The primary endpoint was change from baseline in the Hamilton Anxiety Rating Scale (HAM-A) score at Week 8. Neurocalm-XR demonstrated a mean reduction of 12.4 points in HAM-A scores compared to 5.8 points in the placebo cohort (p = 0.002).

## Documented Adverse Events
Documented adverse events included Transient Somnolence in 8.1% of patients during the first 2 weeks of titration, which resolved spontaneously without treatment discontinuation.
""",
    },
    {
        "title": "ONCO-505 Oncology Safety and Efficacy Dossier: Oncotarget-B in HER2+ Breast Cancer",
        "doc_type": "safety_report",
        "metadata": {
            "trial_id": "ONCO-505",
            "phase": "Phase 3",
            "sponsor": "OncoLab Therapeutics",
            "condition": "HER2+ Metastatic Breast Cancer",
            "investigational_drug": "Oncotarget-B",
        },
        "content": """# ONCO-505 Safety and Efficacy Dossier

## Overview
Oncotarget-B is a targeted synthetic antibody-drug conjugate under clinical evaluation for advanced HER2+ Metastatic Breast Cancer. The ONCO-505 multinational trial was sponsored by OncoLab Therapeutics.

## Clinical Efficacy Outcomes
In the intent-to-treat population of 480 pretreated patients with HER2+ Metastatic Breast Cancer, Oncotarget-B achieved a median Progression-Free Survival (PFS) of 14.2 months compared to 8.1 months for standard-of-care chemotherapy regimens (Hazard Ratio = 0.62).

## Safety and Toxicities
The predominant hematologic adverse event was Grade 2 Neutropenia occurring in 14.5% of subjects, managed with temporary dose holds. No left ventricular ejection fraction declines below 50% were reported.
""",
    },
    {
        "title": "IMMUNO-109 Clinical Trial Report: Arthritin-Bio in Refractory Rheumatoid Arthritis",
        "doc_type": "study_summary",
        "metadata": {
            "trial_id": "IMMUNO-109",
            "phase": "Phase 3",
            "sponsor": "ImmunoCare International",
            "condition": "Refractory Rheumatoid Arthritis",
            "investigational_drug": "Arthritin-Bio",
        },
        "content": """# IMMUNO-109 Clinical Trial Report

## Introduction
The IMMUNO-109 global clinical study evaluated the biologic agent Arthritin-Bio in patients with Refractory Rheumatoid Arthritis exhibiting inadequate response to anti-TNF therapies.

## Clinical Endpoints and Outcomes
At Week 24, 45% of patients in the Arthritin-Bio cohort achieved an ACR50 clinical response compared to 18% in the placebo group (p < 0.001). Quality of life scores (HAQ-DI) improved significantly.

## Safety Observations
Laboratory monitoring identified Mildly Elevated ALT/AST transaminases in 5.3% of participants, which normalized following dose reduction. Serious opportunistic infections were not reported.
""",
    },
    {
        "title": "METABO-204 Drug Monograph: Glycostat in Type 2 Diabetes Mellitus",
        "doc_type": "monograph",
        "metadata": {
            "trial_id": "METABO-204",
            "phase": "Phase 3",
            "sponsor": "EndoGen Therapeutics",
            "condition": "Type 2 Diabetes Mellitus",
            "investigational_drug": "Glycostat",
        },
        "content": """# METABO-204 Monograph & Trial Summary

## Therapeutic Class and Mechanism
Glycostat is a synthetic dual metabolic receptor agonist developed by EndoGen Therapeutics for glycemic control in Type 2 Diabetes Mellitus.

## Key Outcomes
In the METABO-204 pivotal study involving 510 patients with uncontrolled Type 2 Diabetes Mellitus, Glycostat achieved a 1.4% reduction in HbA1c at 26 weeks alongside a mean weight reduction of 3.8 kg.

## Tolerability and Adverse Events
The primary reported adverse event was mild-to-moderate Gastrointestinal Distress (nausea and bloating) occurring in 11.2% of subjects, typically subsiding after 3 weeks of continuous administration.
""",
    },
]

SEED_ENTITIES: List[EntityCreate] = [
    # Drugs
    EntityCreate(id="DRUG-CARDIOVAX", name="Cardiovax", entity_type=EntityType.DRUG, description="Synthetic dual calcium-channel and renin inhibitor candidate", properties={"route": "Oral", "daily_dose": "50mg"}),
    EntityCreate(id="DRUG-NEUROCALM", name="Neurocalm-XR", entity_type=EntityType.DRUG, description="Synthetic extended-release allosteric neuromodulator", properties={"route": "Oral", "daily_dose": "20mg"}),
    EntityCreate(id="DRUG-ONCOTARGET-B", name="Oncotarget-B", entity_type=EntityType.DRUG, description="Synthetic HER2-directed antibody conjugate", properties={"route": "IV Infusion"}),
    EntityCreate(id="DRUG-ARTHRITIN", name="Arthritin-Bio", entity_type=EntityType.DRUG, description="Synthetic targeted biologic interleukin inhibitor", properties={"route": "Subcutaneous"}),
    EntityCreate(id="DRUG-GLYCOSTAT", name="Glycostat", entity_type=EntityType.DRUG, description="Synthetic dual metabolic insulin-sensitizing agonist", properties={"route": "Oral"}),

    # Conditions
    EntityCreate(id="COND-HYPERTENSION", name="Resistant Hypertension", entity_type=EntityType.CONDITION, description="Uncontrolled blood pressure despite concurrent three-agent regimen"),
    EntityCreate(id="COND-GAD", name="Generalized Anxiety Disorder", entity_type=EntityType.CONDITION, description="Chronic neuropsychiatric disorder characterized by persistent worry"),
    EntityCreate(id="COND-BREAST-CANCER", name="HER2+ Metastatic Breast Cancer", entity_type=EntityType.CONDITION, description="Advanced malignant neoplasm overexpressing HER2 receptor"),
    EntityCreate(id="COND-RA", name="Refractory Rheumatoid Arthritis", entity_type=EntityType.CONDITION, description="Severe inflammatory arthritis refractory to standard DMARDs"),
    EntityCreate(id="COND-T2D", name="Type 2 Diabetes Mellitus", entity_type=EntityType.CONDITION, description="Chronic metabolic disorder with insulin resistance and hyperglycemia"),

    # Studies
    EntityCreate(id="STUDY-CARDIO-701", name="CARDIO-701 Phase 3 Trial", entity_type=EntityType.CLINICAL_STUDY, description="Phase 3 trial evaluating Cardiovax in Resistant Hypertension"),
    EntityCreate(id="STUDY-NEURO-302", name="NEURO-302 Phase 2b Protocol", entity_type=EntityType.CLINICAL_STUDY, description="Phase 2b protocol investigating Neurocalm-XR in GAD"),
    EntityCreate(id="STUDY-ONCO-505", name="ONCO-505 Safety and Efficacy Dossier", entity_type=EntityType.CLINICAL_STUDY, description="Safety and survival dossier for Oncotarget-B in breast cancer"),
    EntityCreate(id="STUDY-IMMUNO-109", name="IMMUNO-109 Clinical Trial Report", entity_type=EntityType.CLINICAL_STUDY, description="Biologic evaluation trial of Arthritin-Bio in arthritis"),
    EntityCreate(id="STUDY-METABO-204", name="METABO-204 Monograph and Trial", entity_type=EntityType.CLINICAL_STUDY, description="Glycemic trial for Glycostat in Type 2 Diabetes"),

    # Adverse Events
    EntityCreate(id="AE-HYPOTENSION", name="Orthostatic Hypotension", entity_type=EntityType.ADVERSE_EVENT, description="Postural drop in blood pressure with dizziness"),
    EntityCreate(id="AE-SOMNOLENCE", name="Transient Somnolence", entity_type=EntityType.ADVERSE_EVENT, description="Mild daytime sleepiness during initial dose titration"),
    EntityCreate(id="AE-NEUTROPENIA", name="Grade 2 Neutropenia", entity_type=EntityType.ADVERSE_EVENT, description="Reversible decrease in absolute neutrophil count"),
    EntityCreate(id="AE-ELEVATED-ALT", name="Mildly Elevated ALT/AST", entity_type=EntityType.ADVERSE_EVENT, description="Transient elevation of hepatic transaminases"),
    EntityCreate(id="AE-GI-DISTRESS", name="Gastrointestinal Distress", entity_type=EntityType.ADVERSE_EVENT, description="Mild nausea and abdominal bloating"),

    # Organizations
    EntityCreate(id="ORG-NOVABIO", name="NovaBio Pharmaceuticals", entity_type=EntityType.ORGANIZATION, description="Biotechnology sponsor focused on cardiovascular therapeutics"),
    EntityCreate(id="ORG-APEX", name="Apex Clinical Research Institute", entity_type=EntityType.ORGANIZATION, description="Academic and clinical research institute for neuroscience"),
    EntityCreate(id="ORG-ONCOLAB", name="OncoLab Therapeutics", entity_type=EntityType.ORGANIZATION, description="Specialized oncology biopharmaceutical company"),
    EntityCreate(id="ORG-IMMUNOCARE", name="ImmunoCare International", entity_type=EntityType.ORGANIZATION, description="Immunology and biologic therapeutic consortium"),
    EntityCreate(id="ORG-ENDOGEN", name="EndoGen Therapeutics", entity_type=EntityType.ORGANIZATION, description="Metabolic disease discovery organization"),

    # Patient Groups
    EntityCreate(id="PG-ADULT-HYPERTENSION", name="Adults with Stage II Resistant Hypertension", entity_type=EntityType.PATIENT_GROUP, description="Adult subjects 18-75 on triple antihypertensive therapy"),
    EntityCreate(id="PG-GAD-OUTPATIENTS", name="Moderate-to-Severe GAD Outpatients", entity_type=EntityType.PATIENT_GROUP, description="Outpatient adult cohort with baseline HAM-A >= 20"),
    EntityCreate(id="PG-HER2-ADVANCED", name="Pretreated HER2+ Advanced Cancer Patients", entity_type=EntityType.PATIENT_GROUP, description="Adult female cohort with progressive metastatic disease"),

    # Outcomes
    EntityCreate(id="OUTCOME-SBP-18", name="18.5 mmHg Systolic Blood Pressure Reduction", entity_type=EntityType.OUTCOME, description="Primary efficacy endpoint at Week 12"),
    EntityCreate(id="OUTCOME-HAMA-12", name="12.4 Point HAM-A Score Improvement", entity_type=EntityType.OUTCOME, description="Statistically significant anxiety reduction at Week 8"),
    EntityCreate(id="OUTCOME-PFS-14", name="14.2 Months Median Progression-Free Survival", entity_type=EntityType.OUTCOME, description="PFS prolongation in intent-to-treat population"),
    EntityCreate(id="OUTCOME-ACR50-45", name="45% ACR50 Clinical Response Rate", entity_type=EntityType.OUTCOME, description="ACR50 achievement at Week 24"),
    EntityCreate(id="OUTCOME-HBA1C-14", name="1.4% HbA1c Glycemic Reduction", entity_type=EntityType.OUTCOME, description="Primary metabolic endpoint at Week 26"),
]

SEED_RELATIONSHIPS: List[RelationshipCreate] = [
    # Drug -> treats -> Condition
    RelationshipCreate(source_id="DRUG-CARDIOVAX", relation_type=RelationType.TREATS, target_id="COND-HYPERTENSION"),
    RelationshipCreate(source_id="DRUG-NEUROCALM", relation_type=RelationType.TREATS, target_id="COND-GAD"),
    RelationshipCreate(source_id="DRUG-ONCOTARGET-B", relation_type=RelationType.TREATS, target_id="COND-BREAST-CANCER"),
    RelationshipCreate(source_id="DRUG-ARTHRITIN", relation_type=RelationType.TREATS, target_id="COND-RA"),
    RelationshipCreate(source_id="DRUG-GLYCOSTAT", relation_type=RelationType.TREATS, target_id="COND-T2D"),

    # Drug -> associated_with -> Adverse Event
    RelationshipCreate(source_id="DRUG-CARDIOVAX", relation_type=RelationType.ASSOCIATED_WITH, target_id="AE-HYPOTENSION"),
    RelationshipCreate(source_id="DRUG-NEUROCALM", relation_type=RelationType.ASSOCIATED_WITH, target_id="AE-SOMNOLENCE"),
    RelationshipCreate(source_id="DRUG-ONCOTARGET-B", relation_type=RelationType.ASSOCIATED_WITH, target_id="AE-NEUTROPENIA"),
    RelationshipCreate(source_id="DRUG-ARTHRITIN", relation_type=RelationType.ASSOCIATED_WITH, target_id="AE-ELEVATED-ALT"),
    RelationshipCreate(source_id="DRUG-GLYCOSTAT", relation_type=RelationType.ASSOCIATED_WITH, target_id="AE-GI-DISTRESS"),

    # Clinical Study -> evaluates -> Drug
    RelationshipCreate(source_id="STUDY-CARDIO-701", relation_type=RelationType.EVALUATES, target_id="DRUG-CARDIOVAX"),
    RelationshipCreate(source_id="STUDY-NEURO-302", relation_type=RelationType.EVALUATES, target_id="DRUG-NEUROCALM"),
    RelationshipCreate(source_id="STUDY-ONCO-505", relation_type=RelationType.EVALUATES, target_id="DRUG-ONCOTARGET-B"),
    RelationshipCreate(source_id="STUDY-IMMUNO-109", relation_type=RelationType.EVALUATES, target_id="DRUG-ARTHRITIN"),
    RelationshipCreate(source_id="STUDY-METABO-204", relation_type=RelationType.EVALUATES, target_id="DRUG-GLYCOSTAT"),

    # Clinical Study -> studies -> Condition
    RelationshipCreate(source_id="STUDY-CARDIO-701", relation_type=RelationType.STUDIES, target_id="COND-HYPERTENSION"),
    RelationshipCreate(source_id="STUDY-NEURO-302", relation_type=RelationType.STUDIES, target_id="COND-GAD"),
    RelationshipCreate(source_id="STUDY-ONCO-505", relation_type=RelationType.STUDIES, target_id="COND-BREAST-CANCER"),
    RelationshipCreate(source_id="STUDY-IMMUNO-109", relation_type=RelationType.STUDIES, target_id="COND-RA"),
    RelationshipCreate(source_id="STUDY-METABO-204", relation_type=RelationType.STUDIES, target_id="COND-T2D"),

    # Clinical Study -> reports -> Outcome
    RelationshipCreate(source_id="STUDY-CARDIO-701", relation_type=RelationType.REPORTS, target_id="OUTCOME-SBP-18"),
    RelationshipCreate(source_id="STUDY-NEURO-302", relation_type=RelationType.REPORTS, target_id="OUTCOME-HAMA-12"),
    RelationshipCreate(source_id="STUDY-ONCO-505", relation_type=RelationType.REPORTS, target_id="OUTCOME-PFS-14"),
    RelationshipCreate(source_id="STUDY-IMMUNO-109", relation_type=RelationType.REPORTS, target_id="OUTCOME-ACR50-45"),
    RelationshipCreate(source_id="STUDY-METABO-204", relation_type=RelationType.REPORTS, target_id="OUTCOME-HBA1C-14"),

    # Organization -> sponsors -> Clinical Study
    RelationshipCreate(source_id="ORG-NOVABIO", relation_type=RelationType.SPONSORS, target_id="STUDY-CARDIO-701"),
    RelationshipCreate(source_id="ORG-APEX", relation_type=RelationType.SPONSORS, target_id="STUDY-NEURO-302"),
    RelationshipCreate(source_id="ORG-ONCOLAB", relation_type=RelationType.SPONSORS, target_id="STUDY-ONCO-505"),
    RelationshipCreate(source_id="ORG-IMMUNOCARE", relation_type=RelationType.SPONSORS, target_id="STUDY-IMMUNO-109"),
    RelationshipCreate(source_id="ORG-ENDOGEN", relation_type=RelationType.SPONSORS, target_id="STUDY-METABO-204"),

    # Patient Group -> participates_in -> Clinical Study
    RelationshipCreate(source_id="PG-ADULT-HYPERTENSION", relation_type=RelationType.PARTICIPATES_IN, target_id="STUDY-CARDIO-701"),
    RelationshipCreate(source_id="PG-GAD-OUTPATIENTS", relation_type=RelationType.PARTICIPATES_IN, target_id="STUDY-NEURO-302"),
    RelationshipCreate(source_id="PG-HER2-ADVANCED", relation_type=RelationType.PARTICIPATES_IN, target_id="STUDY-ONCO-505"),
]


def seed_synthetic_database(db: Session) -> Dict[str, int]:
    """Populate database with synthetic entities, relationships, and documents."""
    # 1. Seed baseline entities
    entities_count = 0
    for ent in SEED_ENTITIES:
        try:
            kg_engine.add_entity(db, ent)
            entities_count += 1
        except Exception:
            pass

    # 2. Seed baseline relationships
    rel_count = 0
    for rel in SEED_RELATIONSHIPS:
        try:
            kg_engine.add_relationship(db, rel)
            rel_count += 1
        except Exception:
            pass

    # 3. Seed synthetic documents & chunks
    docs_count = 0
    chunks_count = 0
    for doc_dict in SYNTHETIC_DOCUMENTS:
        doc_in = DocumentCreate(
            title=doc_dict["title"],
            doc_type=doc_dict["doc_type"],
            content=doc_dict["content"],
            metadata=doc_dict["metadata"],
        )
        doc_resp = document_service.ingest_document(db, doc_in)
        docs_count += 1
        if doc_resp.chunks:
            chunks_count += len(doc_resp.chunks)

    kg_engine.sync_from_database(db)

    return {
        "documents_seeded": docs_count,
        "chunks_created": chunks_count,
        "entities_seeded": entities_count,
        "relationships_seeded": rel_count,
    }
