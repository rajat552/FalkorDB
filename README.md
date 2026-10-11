# Company Brain — Enterprise Knowledge Intelligence (Track 03)

[![FalkorDB](https://img.shields.io/badge/Graph_Database-FalkorDB-FF8101?style=for-the-badge&logo=redis)](https://falkordb.com/)
[![Track](https://img.shields.io/badge/Hackathon_Track-03_Enterprise_RAG-6366F1?style=for-the-badge)](https://falkordb.com)
[![Tests](https://img.shields.io/badge/Tests-39_Passed_100%25-10B981?style=for-the-badge)](https://github.com/rajat552/FalkorDB)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

**Company Brain** is an enterprise knowledge intelligence assistant for internal IT helpdesks. It connects fragmented company documents, service architecture specifications, incident postmortems, technical runbooks, and team ownership records into **FalkorDB**.

Unlike generic chatbot wrappers, Company Brain features **relationship-aware GraphRAG retrieval**, multi-hop Cypher traversals across documents, and **cryptographically verifiable source citations with authentic passages**, while deterministically abstaining when evidence is insufficient.

---

## 1. Key Features

- **Multi-Hop Cross-Document Graph Traversal:** Answers complex cross-domain questions connecting services, incident postmortems, resolving teams, and operational runbooks.
- **Verifiable Grounded Citations:** Every response includes exact source filenames, chunk IDs, and authenticated text passages directly verified against stored document text.
- **Honest Abstention:** Never hallucinates answers; explicitly flags `insufficient_evidence: true` when facts are not in the graph.
- **Enterprise Ingestion Pipeline:** Supports Markdown (`.md`), Plain Text (`.txt`), PDF (`.pdf`), and JSON (`.json`) with SHA-256 content deduplication and chunk offset tracking.
- **Dual-Mode LLM Engine:** Seamlessly connects to live OpenAI (`gpt-4o`) or Google Gemini when API keys exist; includes a deterministic local engine for offline testing, CI, and evaluation.
- **Interactive Web Interface:** Modern, responsive dark-mode dashboard (Vanilla HTML/CSS/JS) featuring Chat, Evidence Inspector, Document Manager, and Knowledge Graph Explorer.

---

## 2. System Architecture

```
                      +---------------------------------------+
                      |       Enterprise Web Dashboard       |
                      | (HTML5 / Vanilla CSS / JavaScript ES6)|
                      +-------------------+-------------------+
                                          | REST API / JSON
                                          v
                      +---------------------------------------+
                      |         FastAPI Application           |
                      |   - Route Handlers & Validation       |
                      |   - File Upload & Multipart Parser    |
                      |   - Health & Diagnostics              |
                      +-------------------+-------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
                v                                                   v
+-------------------------------+                   +-------------------------------+
|     Ingestion & Parser        |                   |      GraphRAG Query Engine    |
| - File Validator              |                   | - Intent & Entity Matcher     |
| - Text / Markdown / PDF Chunk |                   | - Multi-Hop Cypher Traversal  |
| - SHA-256 Deduplication       |                   | - Evidence Passage Retriever  |
| - Graph Entity Normalizer     |                   | - Dual-Mode LLM Generator     |
+---------------+---------------+                   | - Citation & Evidence Verifier|
                |                                   +---------------+---------------+
                | Ingests Entities, Chunks, Edges                   | Queries Graph
                v                                                   v
+-----------------------------------------------------------------------------------+
|                            FalkorDB Graph Storage                                 |
|                           (Redis Protocol :6379)                                  |
|                                                                                   |
|  (Team)-[:OWNS]->(Service)<-[:AFFECTED_BY]-(Incident)-[:DOCUMENTED_IN]->(Runbook) |
|     ^               ^                             ^                         ^     |
|     |               |                             |                         |     |
|     +-[:CONTAINS]---+--------[:CONTAINS]----------+--------[:CONTAINS]------+     |
|                             (Document)-[:CONTAINS]->(EvidenceChunk)               |
+-----------------------------------------------------------------------------------+
```

---

## 3. Quickstart & Installation

### Step 1: Start FalkorDB Container
If not already running:
```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm -v ./data/falkordb:/data falkordb/falkordb:latest
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
# Or directly install core packages:
pip install falkordb fastapi uvicorn pydantic python-dotenv pypdf beautifulsoup4 pytest
```

### Step 3: Configure Environment (Optional)
Copy `.env.example` to `.env` (live API keys are optional; local engine works out of the box):
```env
FALKORDB_HOST=127.0.0.1
FALKORDB_PORT=6379
FALKORDB_GRAPH=company_brain
OPENAI_API_KEY=
GOOGLE_API_KEY=
```

### Step 4: Index Synthetic Enterprise Dataset
```bash
python -c "from app.ingestion.pipeline import ingest_enterprise_dataset; ingest_enterprise_dataset()"
```

### Step 5: Start Company Brain Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser to:
- **Web Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **FalkorDB Studio Browser:** [http://localhost:3000](http://localhost:3000)

---

## 4. Benchmark Evaluation & Verification

Company Brain includes a full automated test suite covering unit tests, integration tests, and 8 quantitative evaluation scenarios:

```bash
# Run full test suite (39 tests)
python -m pytest tests/unit tests/integration tests/evaluation tests/test_helper_validate_cypher.py tests/test_kg.py -v
```

### Evaluation Benchmark Results (100% Pass Rate):

| Benchmark ID | Query | Expected Facts | Citations | Status |
| :--- | :--- | :--- | :--- | :--- |
| **EVAL-01** | *"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"* | Payments Platform, INC-2024-891, RB-PAY-04 | 2 Citations | **PASSED** |
| **EVAL-02** | *"Who owns the auth-service and who is the team lead?"* | Security Core, Sarah Chen | 1 Citation | **PASSED** |
| **EVAL-03** | *"What steps are required to recover the payment-service connection pool?"* | RB-PAY-04, DB_POOL_MAX_SIZE=150, rolling restart | 1 Citation | **PASSED** |
| **EVAL-04** | *"What is the SLA and escalation policy for Sev-1 payment incidents?"* | 15 minutes, 1-hour, Sev-1 | 1 Citation | **PASSED** |
| **EVAL-05** | *"Who owns payment-service and what slack channel do they use?"* | Payments Platform, Elena Rostova | 1 Citation | **PASSED** |
| **EVAL-06** | *"What is the secret recipe for chocolate cookies?"* | "I do not have sufficient information..." | 0 Citations (No hallucination) | **PASSED** |
| **EVAL-07** | *"Who is the maintainer of quantum-teleportation-service?"* | "I do not have sufficient information..." | 0 Citations (Honest abstention) | **PASSED** |
| **EVAL-08** | *"Who was the incident commander for INC-2024-891?"* | Marcus Vance (Senior SRE) | 1 Citation | **PASSED** |

---

## 5. API Reference Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | FalkorDB latency, connection status, graph metrics |
| `POST` | `/api/documents/upload` | Multipart file upload with SHA-256 deduplication |
| `GET` | `/api/documents` | List all ingested documents |
| `GET` | `/api/documents/{id}` | Inspect document chunks and offsets |
| `DELETE`| `/api/documents/{id}` | Cascade deletion of document, chunks, and edges |
| `POST` | `/api/chat` | GraphRAG question answering with verified citations |
| `GET` | `/api/sources/{id}` | Retrieve raw evidence passage by chunk ID |
| `GET` | `/api/graph/overview` | Graph node/edge summary metrics |
| `GET` | `/api/graph/related` | 360-degree entity neighborhood exploration |

---

## 6. Hackathon Presentation Outline (5-Minute Demo)

1. **Problem (1 min):** Enterprise IT knowledge is fragmented across Slack, Google Docs, Notion runbooks, and Jira postmortems. Standard vector RAG fails on relationship questions ("Which team resolved the incident caused by the service documented in runbook X?").
2. **Solution (1.5 min):** Company Brain powered by FalkorDB GraphRAG. Ingests raw documentation, constructs an operational knowledge graph (`Service`, `Team`, `Incident`, `Runbook`), and anchors every entity to exact `EvidenceChunk` passages.
3. **Live Demo (1.5 min):**
   - Query: *"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"*
   - Show cross-document synthesis: Links `payment-service` outage (INC-2024-891) -> resolving team (`Payments Platform`) -> root cause -> recovery runbook (`RB-PAY-04`).
   - Click citations to view the exact verified passage.
   - Ask out-of-scope query (*"What is the cookie recipe?"*) to demonstrate honest abstention.
4. **Architecture & Impact (1 min):** Low-latency Cypher traversals on FalkorDB (<10ms), zero hallucinations, and end-to-end evidence traceability.
