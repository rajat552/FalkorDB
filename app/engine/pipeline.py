from __future__ import annotations
import logging
from typing import Dict, Any, Optional

from app.engine.retriever import retrieve_graph_evidence
from app.engine.generator import generate_grounded_response

logger = logging.getLogger(__name__)


def query_company_brain(
    query: str,
    graph_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main entry point for GraphRAG query execution.
    1. Validates input query.
    2. Retrieves relationship-aware evidence and chunks.
    3. Synthesizes a factual, grounded answer with verifiable citations.
    4. Expresses honest abstention when evidence is insufficient.
    """
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        return {
            "query": query,
            "answer": "Please provide a valid question to search the company knowledge graph.",
            "citations": [],
            "graph_context": {"entities": [], "relationships": []},
            "insufficient_evidence": True,
        }

    # 1. Evidence Retrieval
    evidence = retrieve_graph_evidence(query=cleaned_query, graph_name=graph_name)

    # 2. Grounded Generation & Citation Verification
    response_data = generate_grounded_response(query=cleaned_query, evidence=evidence)

    # 3. Assemble Structured Graph Context
    graph_context = {
        "entities": evidence.entities,
        "relationships": evidence.relationships,
        "total_evidence_chunks": len(evidence.chunks),
    }

    return {
        "query": cleaned_query,
        "answer": response_data["answer"],
        "citations": response_data["citations"],
        "graph_context": graph_context,
        "insufficient_evidence": response_data["insufficient_evidence"],
    }
