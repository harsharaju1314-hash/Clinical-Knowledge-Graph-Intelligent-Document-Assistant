"""
Knowledge Graph Agent (Agent 2).
Responsible for identifying entity mentions, traversing the knowledge graph,
and returning structured factual triples.
"""

from typing import List, Tuple
from sqlalchemy.orm import Session
from app.core.schemas import GraphTripleItem
from app.graph.knowledge_graph import kg_engine


class KnowledgeGraphAgent:
    """Agent 2: Identifies entities and queries graph relationships."""

    def __init__(self, agent_name: str = "Knowledge Graph Agent"):
        self.agent_name = agent_name

    def run(
        self, db: Session, question: str, max_hops: int = 2
    ) -> Tuple[List[GraphTripleItem], str, str]:
        """
        Extract subgraph relevant to the question.
        Returns: (triples, formatted_graph_text, trace_summary)
        """
        triples = kg_engine.extract_subgraph_for_query_text(
            db=db,
            query_text=question,
            max_hops=max_hops,
        )

        formatted_lines = []
        for t in triples:
            formatted_lines.append(
                f"({t.source_name} [{t.source_type}]) -> [{t.relation}] -> ({t.target_name} [{t.target_type}])"
            )

        formatted_text = "\n".join(formatted_lines)
        summary = f"Identified and traversed {len(triples)} ontology relationships from the clinical knowledge graph."
        return triples, formatted_text, summary


kg_agent = KnowledgeGraphAgent()
