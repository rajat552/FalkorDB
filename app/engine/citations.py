from __future__ import annotations
import re
from typing import List, Dict, Any, Optional


def verify_citation(
    citation: Dict[str, Any],
    candidate_chunks: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Strictly verify that a citation references an actual retrieved document and contains
    an authentic passage present in that document's text.
    """
    doc_id = citation.get("document_id")
    filename = citation.get("filename")
    passage = (citation.get("passage") or "").strip()

    if not passage:
        return None

    # Find matching candidate chunks by document_id or filename
    matching_chunks = [
        c for c in candidate_chunks
        if (doc_id and c.get("document_id") == doc_id) or (filename and c.get("filename") == filename)
    ]

    if not matching_chunks:
        return None

    # Check if passage is present in any matching chunk
    cleaned_passage = " ".join(passage.lower().split())
    for chunk in matching_chunks:
        chunk_text = " ".join(chunk.get("text", "").lower().split())
        if cleaned_passage in chunk_text:
            return {
                "document_id": chunk.get("document_id"),
                "filename": chunk.get("filename"),
                "chunk_id": chunk.get("chunk_id"),
                "passage": passage,
            }
        
        # Word overlap check (minimum 5 words, >80% overlap)
        words_passage = set(re.findall(r"\w+", cleaned_passage))
        words_chunk = set(re.findall(r"\w+", chunk_text))
        if len(words_passage) >= 5 and len(words_passage.intersection(words_chunk)) / len(words_passage) >= 0.85:
            return {
                "document_id": chunk.get("document_id"),
                "filename": chunk.get("filename"),
                "chunk_id": chunk.get("chunk_id"),
                "passage": passage,
            }

    return None


def extract_grounded_citations(
    chunks: List[Dict[str, Any]],
    query_keywords: List[str],
    max_citations: int = 3,
) -> List[Dict[str, Any]]:
    """
    Extract verified citations from chunks that have highest relevance to query facts.
    """
    scored_chunks = []
    for c in chunks:
        text_lower = c.get("text", "").lower()
        score = sum(1 for kw in query_keywords if kw.lower() in text_lower)
        scored_chunks.append((score, c))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    citations = []
    seen_docs = set()

    for score, chunk in scored_chunks:
        doc_fn = chunk.get("filename")
        if doc_fn in seen_docs and len(citations) >= 2:
            continue
        seen_docs.add(doc_fn)

        # Select the most informative snippet from the chunk
        text = chunk.get("text", "")
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 30]
        snippet = sentences[0] if sentences else text[:200]
        if len(sentences) > 1 and any(kw.lower() in sentences[1].lower() for kw in query_keywords):
            snippet = f"{sentences[0]} {sentences[1]}"

        citations.append({
            "document_id": chunk.get("document_id"),
            "filename": chunk.get("filename"),
            "chunk_id": chunk.get("chunk_id"),
            "passage": snippet.strip(),
        })

        if len(citations) >= max_citations:
            break

    return citations
