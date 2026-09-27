"""
Multi-Agent RAG Q&A API route.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.schemas import AskRequest, AskResponse
from app.agents.orchestrator import agent_orchestrator

router = APIRouter(tags=["Multi-Agent Assistant"])


@router.post("/ask", response_model=AskResponse)
def ask_clinical_assistant(request: AskRequest, db: Session = Depends(get_db)):
    """
    Execute 3-Agent Grounded Q&A Workflow:
    1. Knowledge Graph Agent: Extracts entities and retrieves relevant graph triples.
    2. Retrieval Agent: Performs semantic vector retrieval across document chunks.
    3. Response Agent: Synthesizes graph + vector context into a strictly grounded answer with citations.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    return agent_orchestrator.answer_question(db=db, request=request)
