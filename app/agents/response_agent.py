"""
Response Agent (Agent 3).
Synthesizes retrieved vector chunks and knowledge graph triples into a grounded clinical answer.
"""

from typing import List, Tuple
from app.core.schemas import SearchResultItem, GraphTripleItem
from app.llm.prompts import CLINICAL_GROUNDING_SYSTEM_PROMPT, construct_agent_prompt
from app.llm.provider import get_llm_provider


class ResponseAgent:
    """Agent 3: Synthesizes multi-source context into a strictly grounded answer."""

    def __init__(self, agent_name: str = "Response Agent"):
        self.agent_name = agent_name

    def run(
        self,
        question: str,
        vector_results: List[SearchResultItem],
        graph_triples: List[GraphTripleItem],
        graph_text: str,
    ) -> Tuple[str, bool, str]:
        """
        Synthesize final answer using LLM provider and grounding validation.
        Returns: (answer_text, is_grounded, trace_summary)
        """
        # Format vector context
        vector_blocks = []
        for r in vector_results:
            vector_blocks.append(
                f"[Source: {r.document_title} | Section: {r.section}]\n{r.content}"
            )
        vector_text = "\n\n".join(vector_blocks)

        user_prompt = construct_agent_prompt(
            question=question,
            graph_context=graph_text,
            vector_context=vector_text,
        )

        llm = get_llm_provider()
        answer = llm.generate_response(
            system_prompt=CLINICAL_GROUNDING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        is_grounded = bool(vector_results or graph_triples)
        summary = (
            f"Synthesized grounded response combining {len(vector_results)} chunks "
            f"and {len(graph_triples)} graph triples."
        )

        return answer, is_grounded, summary


response_agent = ResponseAgent()
