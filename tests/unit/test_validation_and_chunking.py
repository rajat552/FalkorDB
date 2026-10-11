from __future__ import annotations
import pytest
from app.ingestion.validator import validate_file, compute_content_hash, DocumentValidationError
from app.ingestion.chunker import chunk_document
from app.engine.citations import verify_citation, extract_grounded_citations
from app.engine.generator import generate_grounded_response
from app.engine.retriever import RetrievedEvidence


def test_validator_allowed_formats():
    filename, text = validate_file("test.md", b"# Service Title\nService documentation.")
    assert filename == "test.md"
    assert "Service Title" in text


def test_validator_rejected_format():
    with pytest.raises(DocumentValidationError):
        validate_file("malicious.exe", b"\x4d\x5a\x90\x00")


def test_validator_empty_file():
    with pytest.raises(DocumentValidationError):
        validate_file("empty.txt", b"   \n\t  ")


def test_content_hash_deterministic():
    content = b"Deterministic payload for content hashing."
    h1 = compute_content_hash(content)
    h2 = compute_content_hash(content)
    assert h1 == h2
    assert len(h1) == 64


def test_chunking_boundaries_and_offsets():
    text = (
        "Paragraph 1 contains important payment service details and SLAs.\n\n"
        "Paragraph 2 discusses database connection pool timeouts and HikariCP settings.\n\n"
        "Paragraph 3 covers the runbook RB-PAY-04 for failover procedures."
    )
    chunks = chunk_document(document_id="doc-test-1", text=text, chunk_size=100, overlap=20)
    assert len(chunks) >= 2
    for c in chunks:
        assert c.chunk_id.startswith("chunk-doc-test-1-")
        assert c.char_count == len(c.text)
        assert text[c.start_char:c.end_char].strip() == c.text


def test_citation_verification_valid():
    candidate_chunks = [
        {
            "chunk_id": "chunk-101",
            "document_id": "doc-891",
            "filename": "payment-incident.md",
            "text": "Incident INC-2024-891 was resolved by the Payments Platform team after resetting pool quotas.",
        }
    ]
    citation = {
        "document_id": "doc-891",
        "filename": "payment-incident.md",
        "passage": "Incident INC-2024-891 was resolved by the Payments Platform team",
    }
    verified = verify_citation(citation, candidate_chunks)
    assert verified is not None
    assert verified["chunk_id"] == "chunk-101"


def test_citation_verification_hallucination_rejected():
    candidate_chunks = [
        {
            "chunk_id": "chunk-101",
            "document_id": "doc-891",
            "filename": "payment-incident.md",
            "text": "Incident INC-2024-891 was resolved by the Payments Platform team.",
        }
    ]
    fake_citation = {
        "document_id": "doc-891",
        "filename": "payment-incident.md",
        "passage": "A completely fabricated passage about alien invasions that does not exist.",
    }
    verified = verify_citation(fake_citation, candidate_chunks)
    assert verified is None


def test_abstention_on_empty_evidence():
    evidence = RetrievedEvidence()
    res = generate_grounded_response("Any query", evidence)
    assert res["insufficient_evidence"] is True
    assert len(res["citations"]) == 0
    assert "sufficient information" in res["answer"].lower()
