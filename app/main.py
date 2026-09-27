"""
Main FastAPI Application Entrypoint.
Clinical Knowledge Graph & Intelligent Document Assistant.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import init_db, get_db, SessionLocal
from app.core.models import DocumentModel, EntityModel, RelationshipModel, DocumentChunkModel
from app.core.schemas import HealthResponse, SeedResponse
from app.data.seed_data import seed_synthetic_database
from app.graph.knowledge_graph import kg_engine

from app.api.routes_documents import router as documents_router
from app.api.routes_search import router as search_router
from app.api.routes_graph import router as graph_router
from app.api.routes_entities import router as entities_router
from app.api.routes_ask import router as ask_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clinical_kg_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle handler."""
    logger.info("Initializing database schema...")
    init_db()

    # Automatically seed synthetic records if database is fresh
    db = SessionLocal()
    try:
        doc_count = db.query(DocumentModel).count()
        if doc_count == 0:
            logger.info("Empty database detected. Seeding synthetic clinical knowledge base...")
            seed_synthetic_database(db)
            logger.info("Synthetic database seeding completed.")
        else:
            kg_engine.sync_from_database(db)
    except Exception as e:
        logger.error(f"Error during startup seeding: {e}")
    finally:
        db.close()

    yield
    logger.info("Application shutting down...")


app = FastAPI(
    title=settings.app_name,
    description=(
        "A realistic clinical intelligence backend utilizing synthetic medical documents, "
        "a lightweight clinical ontology, a relational Knowledge Graph, and a 3-agent RAG workflow."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(graph_router)
app.include_router(entities_router)
app.include_router(ask_router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """System health check and entity counts."""
    doc_count = db.query(DocumentModel).count()
    chunk_count = db.query(DocumentChunkModel).count()
    entity_count = db.query(EntityModel).count()
    rel_count = db.query(RelationshipModel).count()

    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version="1.0.0",
        database_status="connected",
        total_documents=doc_count,
        total_chunks=chunk_count,
        total_entities=entity_count,
        total_relationships=rel_count,
    )


@app.post("/seed", response_model=SeedResponse, tags=["System"])
def seed_data(db: Session = Depends(get_db)):
    """Seed or re-seed synthetic clinical documents, ontology entities, and relationships."""
    stats = seed_synthetic_database(db)
    return SeedResponse(
        status="success",
        message="Synthetic clinical dataset seeded successfully.",
        **stats,
    )
