# Clinical Knowledge Graph & Intelligent Document Assistant

A domain-specific clinical intelligence backend that ingests synthetic medical and research documents, extracts clinical entities into an ontology-constrained Knowledge Graph, and performs multi-agent hybrid retrieval (Vector Search + Knowledge Graph traversal) to generate grounded clinical answers.

> **SYNTHETIC DATA DISCLAIMER**: This application uses strictly synthetic, fictitious clinical trial summaries and medical records. It is designed for software engineering and clinical information retrieval demonstration only. It does not provide medical advice, diagnosis, or clinical decision support, and is not certified for clinical production environments.

---

## Overview

Clinical trial documents, safety dossiers, and study protocols contain rich unstructured narrative text as well as strict relational facts (e.g., drug indications, trial sponsors, reported outcomes, and adverse reactions). Relying exclusively on standard vector-based RAG often leads to disconnected factual associations or hallucinations across related studies.

This project implements a hybrid approach:
1. **Unstructured Narrative Search**: Chunking and dense vector semantic retrieval over synthetic clinical documents.
2. **Structured Factual Traversal**: A lightweight Knowledge Graph enforcing an explicit clinical domain ontology.
3. **Multi-Agent Orchestration**: A 3-agent pipeline (Retrieval Agent, Knowledge Graph Agent, and Response Agent) that synthesizes both modalities into a verified, cited answer.

---

## Problem Statement

Standard Retrieval-Augmented Generation (RAG) systems retrieve top-k textual chunks based on vector distance alone. In clinical research domains, this architecture exhibits key limitations:
- **Relational Ambiguity**: A vector search query for *"Adverse events of Drug A in Trial B"* may retrieve chunks discussing Trial C or Drug B if semantic phrasing is similar.
- **Entity Disconnect**: Unstructured embeddings do not inherently enforce explicit domain relations (e.g., verifying whether an adverse event is linked to a specific drug or comparator).
- **Hallucination Risk**: LLMs attempting to reason across disconnected text chunks may synthesize unsupported clinical claims.

**Solution**: By coupling relational Knowledge Graph traversal with semantic vector search, the system grounds LLM generation in explicit ontology-validated triples while maintaining access to detailed document text.

---

## Key Features

- **Clinical Domain Ontology**: Validates 7 core entity types (`Drug`, `Condition`, `Clinical Study`, `Outcome`, `Adverse Event`, `Patient Group`, `Organization`) and 8 strict relational rules.
- **Relational Knowledge Graph**: Stores entities and directed relationships in PostgreSQL with an in-memory NetworkX engine for sub-graph traversal up to N hops.
- **Document Chunking & Vector Search**: Automatic header-aware chunking with dense vector embeddings and cosine similarity retrieval.
- **3-Agent Multi-Agent Workflow**:
  - **Retrieval Agent**: Identifies and ranks relevant document chunks with similarity scoring.
  - **Knowledge Graph Agent**: Resolves entity mentions and traverses multi-hop factual triples.
  - **Response Agent**: Combines modalities, enforces anti-hallucination constraints, and outputs citations.
- **FastAPI REST API**: Fully typed Pydantic v2 endpoints for ingestion, search, graph queries, entity exploration, and Q&A.
- **Production Containerization**: Multi-container setup with Docker Compose and PostgreSQL 16.
- **Cloud-Ready AWS Deployment**: Verified deployment configurations for AWS App Runner and AWS ECS Fargate with RDS.
- **Automated CI/CD**: GitHub Actions workflow covering linting, pytest test suite execution, and Docker build validation.

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Language** | Python 3.12+ |
| **Web Framework** | FastAPI, Uvicorn, Pydantic v2 |
| **Database & ORM** | PostgreSQL, SQLite (testing/local fallback), SQLAlchemy 2.0 |
| **Graph Processing** | NetworkX, Relational Graph Schema |
| **NLP & Vectors** | Scikit-Learn (TF-IDF Dense Embeddings), NumPy |
| **LLM & Agents** | Modular LLM Provider (OpenAI GPT-4o-mini, Google Gemini, Deterministic Synthesizer) |
| **Testing** | Pytest, Pytest-Asyncio, Pytest-Cov, HTTPX, Postman |
| **Container & Cloud** | Docker, Docker Compose, AWS App Runner, AWS ECS Fargate, AWS RDS |
| **CI/CD & VCS** | Git, GitHub Actions |

---

## System Architecture & Workflow

```
User Query
    │
    ▼
FastAPI Router (POST /ask)
    │
    ▼
Multi-Agent Orchestrator
    ├──► [Agent 1: KG Agent] ──────► Graph Traversal ──► Structured Triples
    ├──► [Agent 2: Retrieval Agent] ─► Vector Search ────► Text Chunks & Scores
    │
    ▼
[Agent 3: Response Agent] (Synthesizes Triples + Chunks + Grounding Rules)
    │
    ▼
LLM / Synthesis Engine
    │
    ▼
Formatted Grounded Response (Answer + Citations + Triples + Traceability Log)
```

### End-to-End Information Flow
1. **User → API**: User submits a natural language question to `POST /ask`.
2. **Knowledge Graph Agent**: Parses entity mentions and traverses 1-hop and 2-hop edges from the Knowledge Graph.
3. **Retrieval Agent**: Generates query embeddings and computes cosine similarity across indexed chunks.
4. **Response Agent**: Formulates a grounding prompt containing structured triples and text chunks, instructing the model to cite exact sources and refuse unsupported claims.
5. **Database Logging**: Execution traces, citations, and latency metrics are persisted to the `query_history` table in PostgreSQL.

---

## Clinical Domain Ontology

The system enforces a lightweight clinical ontology to prevent invalid relationship creation:

```
[Organization] ───(sponsors)───────► [Clinical Study]
[Patient Group] ──(participates_in)─► [Clinical Study]
[Clinical Study] ──(evaluates)──────► [Drug]
[Clinical Study] ──(studies)────────► [Condition]
[Clinical Study] ──(reports)────────► [Outcome]
[Drug] ───────────(treats)─────────► [Condition]
[Drug] ───────────(associated_with)─► [Adverse Event]
```

### Entity Types
- `Drug`: Investigational or therapeutic molecules (e.g., *Cardiovax*, *Neurocalm-XR*, *Oncotarget-B*).
- `Condition`: Target diseases or disorders (e.g., *Resistant Hypertension*, *Generalized Anxiety Disorder*).
- `Clinical Study`: Formal research protocols and trials (e.g., *CARDIO-701*, *NEURO-302*).
- `Outcome`: Measured endpoints (e.g., *18.5 mmHg SBP reduction*, *14.2 months median PFS*).
- `Adverse Event`: Documented side effects (e.g., *Orthostatic Hypotension*, *Grade 2 Neutropenia*).
- `Patient Group`: Target participant cohorts (e.g., *Adults with Stage II Resistant Hypertension*).
- `Organization`: Research institutes and pharmaceutical sponsors (e.g., *NovaBio Pharmaceuticals*).

---

## Project Structure

```
Clinical-Knowledge-Graph-Intelligent-Document-Assistant/
├── .github/
│   └── workflows/
│       └── ci.yml                     # GitHub Actions CI pipeline
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI entrypoint & lifespan events
│   ├── config.py                      # App configuration & environment settings
│   ├── api/                           # REST API endpoint routers
│   │   ├── routes_documents.py        # /documents (ingest, list, get)
│   │   ├── routes_search.py           # /search (vector similarity search)
│   │   ├── routes_graph.py            # /graph/query & /graph/ontology
│   │   ├── routes_entities.py         # /entities & /relationships
│   │   └── routes_ask.py              # /ask (3-agent Q&A pipeline)
│   ├── core/                          # Core schemas, database, and ontology
│   │   ├── database.py                # Database connection & session factory
│   │   ├── models.py                  # SQLAlchemy ORM models
│   │   ├── schemas.py                 # Pydantic v2 validation models
│   │   └── ontology.py                # Domain ontology & triplet validator
│   ├── graph/                         # Knowledge Graph engine
│   │   └── knowledge_graph.py         # Graph traversal, entity matching & NetworkX
│   ├── ingestion/                     # Ingestion pipeline
│   │   ├── chunker.py                 # Header-aware document chunker
│   │   ├── extractor.py               # Clinical entity & relation extraction
│   │   └── document_service.py        # Ingestion orchestration
│   ├── vector/                        # Vector embeddings & similarity store
│   │   ├── embeddings.py              # Embedding generation & cosine distance
│   │   └── vector_store.py            # Chunk ranking & search service
│   ├── agents/                        # Multi-Agent implementation
│   │   ├── retrieval_agent.py         # Agent 1: Semantic Document Retrieval
│   │   ├── kg_agent.py                # Agent 2: Knowledge Graph Traversal
│   │   ├── response_agent.py          # Agent 3: Grounded Context Synthesis
│   │   └── orchestrator.py            # Multi-Agent coordinator & trace logger
│   ├── llm/                           # LLM interface & prompt templates
│   │   ├── provider.py                # Pluggable LLM provider factory
│   │   └── prompts.py                 # Anti-hallucination grounding prompts
│   └── data/                          # Synthetic dataset & database seeder
│       └── seed_data.py               # 5 clinical trial dossiers & seed triples
├── tests/                             # Pytest automated test suite (39 tests)
│   ├── conftest.py                    # Test client & in-memory DB fixture
│   ├── test_ontology.py               # Ontology rules & constraint checks
│   ├── test_knowledge_graph.py        # Entity, relation, and graph traversal tests
│   ├── test_chunking_embeddings.py    # Chunking & vector similarity tests
│   ├── test_agents.py                 # Individual agent & pipeline tests
│   ├── test_api_documents.py          # Document REST endpoints
│   ├── test_api_graph.py              # Graph & ontology REST endpoints
│   ├── test_api_search.py             # Semantic search REST endpoints
│   └── test_api_ask.py                # Multi-Agent Q&A & health endpoints
├── postman/
│   └── Clinical_Knowledge_Graph_Assistant.postman_collection.json
├── deployment/
│   ├── aws-app-runner.json            # AWS App Runner deployment template
│   └── task-definition.json           # AWS ECS Fargate task definition
├── Dockerfile                         # Production container definition
├── docker-compose.yml                 # Local multi-container development environment
├── pytest.ini                         # Pytest configuration
├── requirements.txt                   # Production Python dependencies
├── requirements-dev.txt               # Testing and development dependencies
├── .env.example                       # Example environment configuration
└── README.md                          # Project documentation
```

---

## Installation & Local Setup

### Prerequisites
- Python 3.12+ (or Python 3.11+)
- Git
- Docker and Docker Compose (optional for containerized run)

### 1. Clone the Repository
```bash
git clone https://github.com/harsharaju1314-hash/Clinical-Knowledge-Graph-Intelligent-Document-Assistant.git
cd Clinical-Knowledge-Graph-Intelligent-Document-Assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Default settings will automatically run in local mode with SQLite and deterministic offline LLM synthesis — no paid API keys required).*

---

## Running the Application

### Option A: Local Development (FastAPI)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
On startup, the application automatically initializes the database tables and seeds the synthetic clinical knowledge base.

- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc UI: `http://localhost:8000/redoc`

### Option B: Docker Compose (FastAPI + PostgreSQL)
```bash
docker-compose up --build
```
This starts:
- PostgreSQL 16 on port `5432`
- FastAPI Application on port `8000`

---

## REST API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service health status, database connection, and entity count statistics |
| `POST` | `/seed` | Re-seed the baseline synthetic documents, entities, and graph relationships |
| `POST` | `/documents` | Ingest a synthetic clinical document, generate chunk embeddings, and link entities |
| `GET` | `/documents` | List all ingested clinical documents with metadata |
| `GET` | `/documents/{doc_id}` | Retrieve specific document content and its parsed chunk segments |
| `POST` | `/search` | Semantic vector search across document chunks with similarity scoring |
| `GET` | `/graph/ontology` | Return the clinical domain ontology schema and allowed relation triplets |
| `POST` | `/graph/query` | Query knowledge graph triples with multi-hop neighbor expansion |
| `GET` | `/entities` | List registered entities with optional type filter (`?entity_type=Drug`) |
| `GET` | `/entities/{entity_id}` | Get entity profile with incoming and outgoing graph relationships |
| `POST` | `/entities` | Register a new entity conforming to ontology constraints |
| `POST` | `/relationships` | Register a directed relationship after validating domain ontology rules |
| `POST` | `/ask` | Execute the 3-Agent grounded Q&A workflow (Vector + Graph + LLM) |

---

## Sample Usage & Example Responses

### 1. Multi-Agent Grounded Inquiry (`POST /ask`)

**Request Payload**:
```json
{
  "question": "What clinical studies evaluate Cardiovax for Resistant Hypertension and what adverse events occurred?",
  "include_graph": true,
  "include_vector": true,
  "top_k": 3
}
```

**Response**:
```json
{
  "question": "What clinical studies evaluate Cardiovax for Resistant Hypertension and what adverse events occurred?",
  "answer": "### Clinical Synthesis for: What clinical studies evaluate Cardiovax for Resistant Hypertension and what adverse events occurred?\n\n#### 1. Structured Knowledge Graph Relationships\nThe following factual relationships were retrieved from the domain ontology knowledge graph:\n- (Cardiovax [Drug]) -> [treats] -> (Resistant Hypertension [Condition])\n- (Cardiovax [Drug]) -> [associated_with] -> (Orthostatic Hypotension [Adverse Event])\n- (CARDIO-701 Phase 3 Trial [Clinical Study]) -> [evaluates] -> (Cardiovax [Drug])\n- (CARDIO-701 Phase 3 Trial [Clinical Study]) -> [studies] -> (Resistant Hypertension [Condition])\n- (CARDIO-701 Phase 3 Trial [Clinical Study]) -> [reports] -> (18.5 mmHg Systolic Blood Pressure Reduction [Outcome])\n\n#### 2. Clinical Document Evidence & Outcomes\nThe following findings were extracted from the synthetic clinical trial dossiers:\n- [Source: CARDIO-701 Phase 3 Clinical Study Summary: Cardiovax in Resistant Hypertension | Section: Efficacy and Reported Outcomes]\nCardiovax demonstrated a statistically significant mean reduction in seated systolic blood pressure of 18.5 mmHg compared to 3.2 mmHg in placebo (p < 0.001)...\n- [Source: CARDIO-701 Phase 3 Clinical Study Summary: Cardiovax in Resistant Hypertension | Section: Safety Profile and Adverse Events]\nThe most common treatment-emergent adverse event was Orthostatic Hypotension reported in 6.4% of active group subjects versus 1.2% in placebo...\n\n#### 3. Grounded Conclusion\nSynthesizing the structured graph triples with the trial document evidence confirms the documented clinical evaluations, therapeutic targets, and safety profile without unsupported external claims.",
  "grounded": true,
  "citations": [
    {
      "document_id": "58c95840-b33f-406f-8650-d4d32bc08b18",
      "document_title": "CARDIO-701 Phase 3 Clinical Study Summary: Cardiovax in Resistant Hypertension",
      "section": "Efficacy and Reported Outcomes",
      "chunk_index": 0,
      "similarity_score": 0.8842
    }
  ],
  "graph_context": [
    {
      "source_id": "DRUG-CARDIOVAX",
      "source_name": "Cardiovax",
      "source_type": "Drug",
      "relation": "treats",
      "target_id": "COND-HYPERTENSION",
      "target_name": "Resistant Hypertension",
      "target_type": "Condition"
    }
  ],
  "agent_traces": [
    {
      "agent_name": "Knowledge Graph Agent",
      "status": "SUCCESS",
      "summary": "Identified and traversed 5 ontology relationships from the clinical knowledge graph."
    },
    {
      "agent_name": "Retrieval Agent",
      "status": "SUCCESS",
      "summary": "Retrieved 3 relevant synthetic document chunks (top similarity score: 0.8842)."
    },
    {
      "agent_name": "Response Agent",
      "status": "SUCCESS",
      "summary": "Synthesized grounded response combining 3 chunks and 5 graph triples."
    }
  ],
  "disclaimer": "SYNTHETIC DATA NOTICE: All medical and clinical information in this response is synthetic/fictitious. This system does not provide medical diagnoses, treatment advice, or clinical decisions."
}
```

---

## Database Schema

The database uses 5 relational tables designed in PostgreSQL / SQLite:

1. **`documents`**:
   - `id` (VARCHAR(64), Primary Key)
   - `title` (VARCHAR(255), Not Null)
   - `doc_type` (VARCHAR(64), Not Null)
   - `content` (TEXT, Not Null)
   - `metadata_json` (JSON)
   - `created_at` (TIMESTAMP)

2. **`document_chunks`**:
   - `id` (VARCHAR(64), Primary Key)
   - `document_id` (VARCHAR(64), Foreign Key → `documents.id` ON DELETE CASCADE)
   - `chunk_index` (INTEGER)
   - `content` (TEXT)
   - `section` (VARCHAR(128))
   - `embedding_json` (JSON, dense vector representation)
   - `created_at` (TIMESTAMP)

3. **`entities`**:
   - `id` (VARCHAR(128), Primary Key, e.g. `DRUG-CARDIOVAX`)
   - `name` (VARCHAR(255), Indexed)
   - `entity_type` (VARCHAR(64), Indexed)
   - `description` (TEXT)
   - `properties_json` (JSON)
   - `created_at` (TIMESTAMP)

4. **`relationships`**:
   - `id` (VARCHAR(64), Primary Key)
   - `source_id` (VARCHAR(128), Foreign Key → `entities.id` ON DELETE CASCADE)
   - `relation_type` (VARCHAR(64), Indexed)
   - `target_id` (VARCHAR(128), Foreign Key → `entities.id` ON DELETE CASCADE)
   - `properties_json` (JSON)
   - `created_at` (TIMESTAMP)

5. **`query_history`**:
   - `id` (VARCHAR(64), Primary Key)
   - `question` (TEXT)
   - `answer` (TEXT)
   - `rag_sources_json` (JSON)
   - `graph_triples_json` (JSON)
   - `latency_ms` (FLOAT)
   - `created_at` (TIMESTAMP)

---

## Automated Testing Strategy

The test suite contains **39 automated tests** with 100% pass rate:
- **Ontology Tests (`test_ontology.py`)**: Tests entity types, valid relation constraints, and invalid triple rejections.
- **Knowledge Graph Tests (`test_knowledge_graph.py`)**: Tests node insertion, relational edge validation, multi-hop sub-graph traversal, and entity neighbor queries.
- **Chunking & Vector Tests (`test_chunking_embeddings.py`)**: Tests markdown section splitting, embedding normalization, cosine similarity math, and chunk ranking.
- **Agent Tests (`test_agents.py`)**: Tests Retrieval Agent, Knowledge Graph Agent, Response Agent, and Orchestrator execution traces.
- **API Tests (`test_api_*.py`)**: Tests all FastAPI endpoints, 404/400 validation handlers, and seed mechanisms using in-memory database sessions.

### Running Tests Locally
```bash
pytest -v
```

### Running Tests with Coverage
```bash
pytest --cov=app --cov-report=term-missing
```

---

## AWS Deployment Architecture

```
Internet
   │
   ▼
[AWS Route 53 / Custom Domain]
   │
   ▼
[AWS App Runner Service / ECS Fargate]
   ├── Container Port: 8000
   ├── Environment Variables (App Config)
   └── Auto-Scaling: 1 - 5 instances
   │
   ▼
[Amazon RDS PostgreSQL 16 (Multi-AZ)]
   ├── Database: clinical_kg_db
   └── Encrypted Storage (AWS KMS)
```

### Deployment Options

#### 1. AWS App Runner (Recommended for Simplicity)
AWS App Runner offers direct container deployment with managed load balancing, SSL, and health check monitoring.
1. Build and push image to Amazon ECR:
   ```bash
   aws ecr create-repository --repository-name clinical-kg-assistant
   docker tag clinical-kg-assistant:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/clinical-kg-assistant:latest
   docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/clinical-kg-assistant:latest
   ```
2. Deploy service using `deployment/aws-app-runner.json`:
   ```bash
   aws apprunner create-service --cli-input-json file://deployment/aws-app-runner.json
   ```

#### 2. AWS ECS Fargate + RDS PostgreSQL
For teams requiring custom VPC networking and private subnets:
1. Create an AWS RDS PostgreSQL instance in private subnets.
2. Register the task definition via `aws ecs register-task-definition --cli-input-json file://deployment/task-definition.json`.
3. Create an ECS Fargate Service attached to an Application Load Balancer (ALB).

---

## CI/CD Pipeline (GitHub Actions)

The workflow defined in `.github/workflows/ci.yml` runs on every pull request and push to `main`:
1. **Environment Setup**: Provisions Ubuntu runner with Python 3.12.
2. **Dependency Installation**: Caches and installs production & development packages.
3. **Linting**: Runs Flake8 for syntax verification and complexity boundaries.
4. **Automated Testing**: Executes full Pytest test suite with code coverage export.
5. **Container Validation**: Runs `docker build` to verify production image integrity.

---

## Technical Interview & Conceptual Breakdown

Here is a summary of the technical principles implemented in this project:

### 1. What is an ontology?
An ontology is a formal specification of concepts, entity types, and permissible relationships within a specific domain. In this project, the ontology strictly allows triples like `(Drug, treats, Condition)` and prevents invalid triples like `(Condition, treats, Drug)`.

### 2. How is a Knowledge Graph different from an ontology?
The ontology is the *schema/rules* (e.g., *Drugs treat Conditions*), whereas the Knowledge Graph is the *instance data* populated according to that schema (e.g., *Cardiovax treats Resistant Hypertension*).

### 3. Why use a Knowledge Graph?
Knowledge Graphs provide structured, verifiable facts with deterministic relationships. Unlike purely probabilistic language models, a knowledge graph enables multi-hop relational queries (e.g. finding which clinical study evaluated a drug and what sponsor funded it) without ambiguity.

### 4. Why use RAG (Retrieval-Augmented Generation)?
RAG dynamically fetches relevant context from an external repository at query time, feeding factual passages directly into the LLM's prompt window rather than relying on the LLM's frozen internal parameters.

### 5. Why use semantic search?
Keyword search fails when users search with synonyms or descriptive phrases (e.g., *"blood pressure medication"* vs *"antihypertensive agent"*). Semantic vector search computes cosine distance in dense embedding space, retrieving conceptually relevant passages regardless of exact wording.

### 6. Why combine Knowledge Graph retrieval with Vector retrieval (Hybrid RAG)?
Vector search is ideal for narrative context and descriptive text, while Knowledge Graphs are ideal for precise relational connectivity. Combining both ensures the LLM receives verified factual links (triples) along with descriptive narrative context (chunks).

### 7. What does each agent do?
- **Agent 1 (Retrieval Agent)**: Performs semantic search over chunked clinical dossiers and computes similarity scores.
- **Agent 2 (Knowledge Graph Agent)**: Identifies entities and extracts 1-hop and 2-hop connected sub-graphs.
- **Agent 3 (Response Agent)**: Blends structured triples and narrative chunks, validates context constraints, and invokes the LLM.

### 8. Why use FastAPI?
FastAPI offers asynchronous execution, native Pydantic v2 data validation, high throughput, and automated OpenAPI documentation.

### 9. Why PostgreSQL?
PostgreSQL provides robust ACID compliance, relational integrity with foreign keys, JSONB support for flexible metadata, and native extension pathways (e.g., `pgvector`).

### 10. How are hallucinations controlled?
1. The LLM prompt explicitly restricts answers to the provided context.
2. The model is mandated to output citations and explicitly declare when information is missing.
3. Structured triples provide hard constraints that counter probabilistic drift.

---

## Future Improvements

- Add native `pgvector` extension integration for vector search in PostgreSQL.
- Add support for HL7 / FHIR clinical data format ingestion.
- Implement streaming tokens (Server-Sent Events) for the `/ask` endpoint.
- Expand ontology schema with bio-molecular targets and contraindications.

---

## What I Learned

- Designing and enforcing domain ontologies to constrain relational graph databases.
- Implementing multi-agent architectures where specialized agents handle separate retrieval responsibilities.
- Structuring hybrid RAG pipelines that synthesize both structured graph triples and unstructured vector chunks.
- Writing comprehensive Pytest suites with in-memory database fixtures and test client mocking.
- Creating containerized microservices ready for AWS deployment with automated CI/CD validation.

---

## Author

**Harsha Raju**  
- GitHub: [@harsharaju1314-hash](https://github.com/harsharaju1314-hash)  
- Repository: [Clinical-Knowledge-Graph-Intelligent-Document-Assistant](https://github.com/harsharaju1314-hash/Clinical-Knowledge-Graph-Intelligent-Document-Assistant)
