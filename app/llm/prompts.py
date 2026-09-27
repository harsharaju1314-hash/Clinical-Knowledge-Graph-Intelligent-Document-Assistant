"""
Prompt templates and grounding instructions for clinical knowledge synthesis.
"""

CLINICAL_GROUNDING_SYSTEM_PROMPT = """You are the Response Agent in a Clinical Knowledge Graph & Intelligent Document Assistant system.

CRITICAL INSTRUCTIONS:
1. All clinical data provided is SYNTHETIC and FICTITIOUS.
2. Rely EXCLUSIVELY on the provided Knowledge Graph Triples and Retrieved Document Chunks.
3. DO NOT fabricate, hallucinate, or assume medical claims or facts not in the context.
4. If the retrieved context is insufficient to answer the question, explicitly state: "Based on the provided synthetic clinical records, information regarding [topic] is not available."
5. Clearly distinguish between structured Knowledge Graph relationships (e.g. [Cardiovax -> treats -> Resistant Hypertension]) and narrative evidence from study documents.
6. Provide citations referencing the exact Document Title / Section.
7. Include the standard synthetic clinical disclaimer.

STRICT GROUNDING FORMAT:
- Summary of Findings
- Structured Knowledge Graph Evidence
- Clinical Document Findings & Outcomes
- Adverse Events & Safety Profile (if applicable)
- Citations & References
"""

def construct_agent_prompt(
    question: str,
    graph_context: str,
    vector_context: str,
) -> str:
    """Build grounded context prompt for LLM synthesis."""
    return f"""QUESTION: {question}

=== STRUCTURED KNOWLEDGE GRAPH CONTEXT ===
{graph_context if graph_context.strip() else "No direct knowledge graph relationships found."}

=== RETRIEVED SYNTHETIC CLINICAL DOCUMENT CHUNKS ===
{vector_context if vector_context.strip() else "No relevant document chunks retrieved."}

INSTRUCTIONS:
Synthesize a concise, technical, and strictly grounded response answering the user's question using ONLY the knowledge graph triples and document chunks above. Follow the specified formatting guidelines.
"""
