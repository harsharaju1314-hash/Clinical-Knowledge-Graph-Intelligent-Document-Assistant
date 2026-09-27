"""
Unit tests for the 3-Agent clinical intelligence architecture.
"""

from app.agents.retrieval_agent import retrieval_agent
from app.agents.kg_agent import kg_agent
from app.agents.response_agent import response_agent
from app.agents.orchestrator import agent_orchestrator
from app.core.schemas import AskRequest


def test_retrieval_agent(db_session):
    results, citations, summary = retrieval_agent.run(
        db=db_session,
        question="What were the outcomes of the Cardiovax trial?",
        top_k=2,
    )
    assert len(results) > 0
    assert len(citations) == len(results)
    assert "Retrieved" in summary


def test_kg_agent(db_session):
    triples, formatted_text, summary = kg_agent.run(
        db=db_session,
        question="Which condition is treated by Cardiovax?",
        max_hops=1,
    )
    assert len(triples) > 0
    assert "Cardiovax" in formatted_text
    assert "treats" in formatted_text
    assert "Identified" in summary


def test_response_agent_grounded():
    from app.core.schemas import SearchResultItem, GraphTripleItem
    mock_vector = [
        SearchResultItem(
            chunk_id="chk-1",
            document_id="doc-1",
            document_title="CARDIO-701 Summary",
            section="Efficacy",
            content="Cardiovax showed 18.5 mmHg SBP reduction.",
            similarity_score=0.92,
        )
    ]
    mock_kg = [
        GraphTripleItem(
            source_id="DRUG-CARDIOVAX",
            source_name="Cardiovax",
            source_type="Drug",
            relation="treats",
            target_id="COND-HYPERTENSION",
            target_name="Resistant Hypertension",
            target_type="Condition",
        )
    ]

    answer, grounded, summary = response_agent.run(
        question="What is Cardiovax indicated for?",
        vector_results=mock_vector,
        graph_triples=mock_kg,
        graph_text="(Cardiovax [Drug]) -> [treats] -> (Resistant Hypertension [Condition])",
    )
    assert grounded is True
    assert "Cardiovax" in answer
    assert "Synthesized" in summary


def test_orchestrator_pipeline(db_session):
    request = AskRequest(
        question="What studies evaluate Cardiovax for Resistant Hypertension?",
        include_graph=True,
        include_vector=True,
        top_k=3,
    )
    resp = agent_orchestrator.answer_question(db=db_session, request=request)
    assert resp.grounded is True
    assert len(resp.citations) > 0
    assert len(resp.graph_context) > 0
    assert len(resp.agent_traces) == 3
    assert resp.agent_traces[0].agent_name == "Knowledge Graph Agent"
    assert resp.agent_traces[1].agent_name == "Retrieval Agent"
    assert resp.agent_traces[2].agent_name == "Response Agent"
    assert "SYNTHETIC DATA NOTICE" in resp.disclaimer
