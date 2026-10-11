# Company Brain Test & Quality Assurance Plan

**Track 03:** Enterprise RAG  
**System:** FalkorDB GraphRAG-SDK Application  

---

## 1. Test Strategy & Scope

The testing plan guarantees that every layer of the Company Brain architecture—from ingestion and graph modeling to query traversal, citation validation, and honest abstention—operates with deterministic precision.

```
+--------------------------------------------------------+
|   End-to-End Evaluation Suite (8 Benchmark Queries)     |
+---------------------------+----------------------------+
                            |
+---------------------------v----------------------------+
|         Integration Tests (FalkorDB + FastAPI)         |
+---------------------------+----------------------------+
                            |
+---------------------------v----------------------------+
|        Unit Tests (Chunker, Citations, Ontology)       |
+--------------------------------------------------------+
```

---

## 2. Unit Testing Suite (`tests/unit/`)

### 2.1 File & Ingestion Validation
- `test_document_validator_allowed_formats`: Verifies `.md`, `.txt`, `.pdf` are accepted.
- `test_document_validator_disallowed_formats`: Verifies `.exe`, `.bin` are rejected with `400 Bad Request`.
- `test_document_validator_size_limits`: Verifies files exceeding 10MB are rejected.
- `test_content_hash_deduplication`: Verifies identical content yields identical SHA-256 and duplicate detection triggers.

### 2.2 Document Chunking & Offsets
- `test_chunk_text_boundaries`: Verifies chunks maintain paragraph or sentence integrity.
- `test_chunk_id_determinism`: Verifies chunk IDs are strictly unique and deterministic (`chunk-{doc_id}-{index}`).
- `test_chunk_char_offsets`: Verifies `start_char` and `end_char` correspond to actual substring indices.

### 2.3 Citation & Groundedness Verifier
- `test_citation_valid_match`: Confirms citations referencing existing chunk IDs and exact passage substrings are accepted.
- `test_citation_hallucination_rejection`: Confirms fabricated passages not present in retrieved chunks are filtered out.
- `test_abstention_trigger`: Verifies that queries with no matching graph entities or chunks return `insufficient_evidence: true`.

---

## 3. Integration Testing Suite (`tests/integration/`)

### 3.1 FalkorDB Graph Connectivity & Schema
- `test_falkordb_connection`: Connects to `127.0.0.1:6379`, creates a temporary graph, and verifies `RETURN 1 AS ping`.
- `test_ontology_constraints`: Asserts unique constraints on `Service(name)`, `Team(name)`, `Incident(id)`, `Document(id)`.
- `test_multi_hop_cypher_traversal`: Traverses `(Service)<-[:AFFECTED_BY]-(Incident)-[:RESOLVED_BY]->(Team)`.

### 3.2 Ingestion to Graph Persistence
- `test_ingest_sample_incident`: Ingests `INC-2024-891-payment-timeout.md`, asserts `Document`, `Incident`, and `EvidenceChunk` nodes exist in FalkorDB.
- `test_cascade_document_deletion`: Deletes a document and confirms its `EvidenceChunk` nodes and `[:CONTAINS]` edges are removed without orphan leaks.

### 3.3 REST API Endpoints
- `test_api_health`: `GET /health` returns status `200` with database metrics.
- `test_api_upload_and_list`: Uploads file via `POST /api/documents/upload` and retrieves via `GET /api/documents`.
- `test_api_chat_known_query`: `POST /api/chat` returns grounded answer with non-empty citations.
- `test_api_chat_unsupported_query`: `POST /api/chat` returns `insufficient_evidence: true`.

---

## 4. End-to-End Evaluation Scenarios (8 Benchmark Queries)

| # | Evaluation Scenario | Question | Expected Grounded Facts | Expected Behavior |
| :- | :--- | :--- | :--- | :--- |
| **Q1** | **Multi-hop incident inquiry** | *"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"* | Team: Payments Platform<br>Cause: Connection pool starvation<br>Runbook: RB-PAY-04 | 2 citations returned; valid answer |
| **Q2** | **Service ownership inquiry** | *"Who owns the auth-service and who is the team lead?"* | Team: Security Core<br>Lead: Sarah Chen | Grounded answer with team roster citation |
| **Q3** | **Active incident check** | *"What active incidents are currently impacting the order-processing service?"* | Incident: INC-2024-915 (Kafka lag)<br>Severity: Sev-2 | Incident report citation returned |
| **Q4** | **Runbook lookup** | *"What steps should be taken if the payment-service throws HTTP 504 timeouts?"* | Procedure: Reset connection pool quotas & drain queue (RB-PAY-04) | Runbook citation returned |
| **Q5** | **Escalation policy inquiry** | *"What is the SLA and escalation path for Sev-1 payment incidents?"* | SLA: 15-minute response, page Payments On-Call | IT Policy document citation |
| **Q6** | **Out-of-scope inquiry** | *"What is the recipe for chocolate chip cookies?"* | None | `insufficient_evidence: true`, 0 citations |
| **Q7** | **Conflicting/outdated doc check** | *"What is the legacy database for payment-service before migration?"* | Legacy: MySQL 5.7 (Archived Doc) | Notes migration to FalkorDB/Postgres |
| **Q8** | **Cross-team dependency** | *"Which services depend on auth-service and who maintains them?"* | Payment Service (Payments Platform) & Order Engine (Orders Squad) | Multi-entity graph context returned |

---

## 5. Security & Verification Checks

- No hardcoded secrets in source files or git history.
- Rate limiting on API upload and query endpoints.
- Path traversal protection on document retrieval (`os.path.basename` sanitization).
- Cypher parameterized queries to prevent graph injection.
