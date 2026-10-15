from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import check_health, get_graph, init_schema
from app.ingestion.pipeline import (
    ingest_file,
    list_documents,
    get_document_details,
    delete_document,
    DuplicateDocumentError,
)
from app.engine.pipeline import query_company_brain


@pytest.fixture(scope="module")
def client():
    init_schema()
    return TestClient(app)


def test_db_health():
    health = check_health()
    assert health["connected"] is True
    assert health["error"] is None
    assert health["latency_ms"] >= 0


def test_api_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"]["connected"] is True


def test_api_documents_list(client):
    res = client.get("/api/documents")
    assert res.status_code == 200
    data = res.json()
    assert "documents" in data
    assert isinstance(data["documents"], list)


def test_upload_and_delete_lifecycle(client):
    content = b"# Temporary Test Service Spec\n\n- Service: temp-test-service\n- Owner: Platform Ops\n"
    res = client.post(
        "/api/documents/upload",
        files={"file": ("temp-service.md", content, "text/markdown")},
    )
    assert res.status_code in (201, 409)
    if res.status_code == 201:
        doc_id = res.json()["document_id"]
        # Verify details
        detail_res = client.get(f"/api/documents/{doc_id}")
        assert detail_res.status_code == 200
        assert len(detail_res.json()["chunks"]) >= 1

        # Delete document
        del_res = client.delete(f"/api/documents/{doc_id}")
        assert del_res.status_code == 200

        # Verify not found after deletion
        get_deleted = client.get(f"/api/documents/{doc_id}")
        assert get_deleted.status_code == 404


def test_chat_canonical_query(client):
    payload = {
        "query": "Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["insufficient_evidence"] is False
    assert len(data["citations"]) >= 1
    assert "Payments Platform" in data["answer"]
    assert "INC-2024-891" in data["answer"]
    assert "RB-PAY-04" in data["answer"]


def test_chat_unsupported_query(client):
    payload = {"query": "What is the secret recipe for chocolate cookies?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["insufficient_evidence"] is True
    assert len(data["citations"]) == 0
    assert "sufficient information" in data["answer"].lower()


def test_graph_overview_endpoint(client):
    res = client.get("/api/graph/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_nodes"] > 0
    assert data["total_edges"] > 0
    assert "Service" in data["node_counts"]
    assert "Incident" in data["node_counts"]


def test_graph_entities_endpoint(client):
    res = client.get("/api/graph/entities")
    assert res.status_code == 200
    data = res.json()
    assert "services" in data
    assert "teams" in data
    assert "incidents" in data
    assert "employees" in data
    assert "documents" in data
    assert len(data["services"]) >= 1
    assert any(s["name"] == "payment-service" for s in data["services"])
    assert any(t["name"] == "Payments Platform" for t in data["teams"])


def test_chat_dependencies_query(client):
    payload = {"query": "What internal services depend on auth-service?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["insufficient_evidence"] is False
    assert len(data["citations"]) >= 1
    assert "auth-service" in data["answer"].lower()


def test_chat_team_members_query(client):
    payload = {"query": "Who are the members of the Payments Platform team?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["insufficient_evidence"] is False
    assert "Elena Rostova" in data["answer"]
    assert "Marcus Vance" in data["answer"]

