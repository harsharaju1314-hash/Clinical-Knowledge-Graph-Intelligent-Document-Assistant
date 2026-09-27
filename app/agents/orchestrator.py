"""
Multi-Agent Orchestrator.
Coordinates the Retrieval Agent, Knowledge Graph Agent, and Response Agent
to generate strictly grounded clinical answers with full traceability.
"""

import time
from typing import List
from sqlalchemy.orm import Session
from app.core.models import QueryHistoryModel
from app.core.schemas import AskRequest, AskResponse, AgentTraceStep
from app.agents.retrieval_agent import retrieval_agent
from app.agents.kg_agent import kg_agent
from app.agents.response_agent import response_agent


class MultiAgentOrchestrator:
    """Coordinates the 3-agent clinical intelligence pipeline."""

    @staticmethod
    def answer_question(db: Session, request: AskRequest) -> AskResponse:
        start_time = time.time()
        traces: List[AgentTraceStep] = []

        # Step 1: Execute Knowledge Graph Agent
        graph_triples = []
        graph_text = ""
        if request.include_graph:
            try:
                triples, g_text, kg_summary = kg_agent.run(
                    db=db,
                    question=request.question,
                    max_hops=2,
                )
                graph_triples = triples
                graph_text = g_text
                traces.append(
                    AgentTraceStep(
                        agent_name="Knowledge Graph Agent",
                        status="SUCCESS",
                        summary=kg_summary,
                    )
                )
            except Exception as e:
                traces.append(
                    AgentTraceStep(
                        agent_name="Knowledge Graph Agent",
                        status="ERROR",
                        summary=f"Graph retrieval failed: {str(e)}",
                    )
                )

        # Step 2: Execute Retrieval Agent (Semantic Vector Search)
        vector_results = []
        citations = []
        if request.include_vector:
            try:
                results, cits, ret_summary = retrieval_agent.run(
                    db=db,
                    question=request.question,
                    top_k=request.top_k,
                )
                vector_results = results
                citations = cits
                traces.append(
                    AgentTraceStep(
                        agent_name="Retrieval Agent",
                        status="SUCCESS",
                        summary=ret_summary,
                    )
                )
            except Exception as e:
                traces.append(
                    AgentTraceStep(
                        agent_name="Retrieval Agent",
                        status="ERROR",
                        summary=f"Vector retrieval failed: {str(e)}",
                    )
                )

        # Step 3: Execute Response Agent (Synthesis & Grounding)
        try:
            answer_text, is_grounded, resp_summary = response_agent.run(
                question=request.question,
                vector_results=vector_results,
                graph_triples=graph_triples,
                graph_text=graph_text,
            )
            traces.append(
                AgentTraceStep(
                    agent_name="Response Agent",
                    status="SUCCESS",
                    summary=resp_summary,
                )
            )
        except Exception as e:
            answer_text = f"An error occurred while synthesizing response: {str(e)}"
            is_grounded = False
            traces.append(
                AgentTraceStep(
                    agent_name="Response Agent",
                    status="ERROR",
                    summary=f"Synthesis failed: {str(e)}",
                )
            )

        latency = round((time.time() - start_time) * 1000, 2)

        # Record query history in database
        try:
            history_record = QueryHistoryModel(
                question=request.question,
                answer=answer_text,
                rag_sources_json=[c.dict() for c in citations],
                graph_triples_json=[t.dict() for t in graph_triples],
                latency_ms=latency,
            )
            db.add(history_record)
            db.commit()
        except Exception:
            pass

        return AskResponse(
            question=request.question,
            answer=answer_text,
            grounded=is_grounded,
            citations=citations,
            graph_context=graph_triples,
            agent_traces=traces,
        )


agent_orchestrator = MultiAgentOrchestrator()
