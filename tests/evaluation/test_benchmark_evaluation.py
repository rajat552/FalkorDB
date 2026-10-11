from __future__ import annotations
import pytest
from app.engine.pipeline import query_company_brain


BENCHMARK_SCENARIOS = [
    {
        "id": "EVAL-01",
        "name": "Canonical Multi-Hop Incident Inquiry",
        "query": "Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?",
        "expected_facts": ["Payments Platform", "INC-2024-891", "RB-PAY-04"],
        "expect_abstain": False,
        "min_citations": 2,
    },
    {
        "id": "EVAL-02",
        "name": "Service Ownership & Lead Inquiry",
        "query": "Who owns the auth-service and who is the team lead?",
        "expected_facts": ["Security Core", "Sarah Chen"],
        "expect_abstain": False,
        "min_citations": 1,
    },
    {
        "id": "EVAL-03",
        "name": "Runbook Procedure Lookup",
        "query": "What steps are required to recover the payment-service connection pool?",
        "expected_facts": ["RB-PAY-04", "DB_POOL_MAX_SIZE=150", "restart"],
        "expect_abstain": False,
        "min_citations": 1,
    },
    {
        "id": "EVAL-04",
        "name": "Incident Escalation SLA Inquiry",
        "query": "What is the SLA and escalation policy for Sev-1 payment incidents?",
        "expected_facts": ["15 minutes", "1-hour", "Sev-1"],
        "expect_abstain": False,
        "min_citations": 1,
    },
    {
        "id": "EVAL-05",
        "name": "Team Roster & Service Matrix",
        "query": "Who owns payment-service and what slack channel do they use?",
        "expected_facts": ["Payments Platform", "Elena Rostova"],
        "expect_abstain": False,
        "min_citations": 1,
    },
    {
        "id": "EVAL-06",
        "name": "Out-of-Scope Cookie Recipe (Honest Abstention)",
        "query": "What is the secret recipe for chocolate cookies?",
        "expected_facts": ["sufficient information"],
        "expect_abstain": True,
        "min_citations": 0,
    },
    {
        "id": "EVAL-07",
        "name": "Fictional Service Query (Honest Abstention)",
        "query": "Who is the primary maintainer of quantum-teleportation-service?",
        "expected_facts": ["sufficient information"],
        "expect_abstain": True,
        "min_citations": 0,
    },
    {
        "id": "EVAL-08",
        "name": "Incident Commander Identification",
        "query": "Who was the incident commander for INC-2024-891?",
        "expected_facts": ["Marcus Vance"],
        "expect_abstain": False,
        "min_citations": 1,
    },
]


@pytest.mark.parametrize("scenario", BENCHMARK_SCENARIOS, ids=[s["id"] for s in BENCHMARK_SCENARIOS])
def test_evaluation_benchmark_scenario(scenario):
    query = scenario["query"]
    result = query_company_brain(query)

    # 1. Assert abstention decision matches expectation
    assert result["insufficient_evidence"] == scenario["expect_abstain"], (
        f"Failed abstention check for {scenario['id']}: expected {scenario['expect_abstain']}, got {result['insufficient_evidence']}"
    )

    # 2. Check citation count
    assert len(result["citations"]) >= scenario["min_citations"], (
        f"Citation count {len(result['citations'])} < min required {scenario['min_citations']}"
    )

    # 3. Assert expected facts appear in answer
    answer = result["answer"]
    for fact in scenario["expected_facts"]:
        assert fact.lower() in answer.lower(), (
            f"Fact '{fact}' missing from answer for {scenario['id']}: {answer}"
        )
