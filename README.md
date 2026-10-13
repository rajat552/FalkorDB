# Company Brain — Enterprise Knowledge Intelligence (Track 03)

[![FalkorDB](https://img.shields.io/badge/Graph_Database-FalkorDB-FF8101?style=for-the-badge&logo=redis)](https://falkordb.com/)
[![Track](https://img.shields.io/badge/Hackathon_Track-03_Enterprise_RAG-6366F1?style=for-the-badge)](https://falkordb.com)
[![Tests](https://img.shields.io/badge/Tests-39_Passed_100%25-10B981?style=for-the-badge)](https://github.com/rajat552/FalkorDB)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11_|_3.12_|_3.13-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

**Company Brain** is an enterprise knowledge intelligence assistant engineered for internal IT helpdesks, site reliability engineers (SREs), and platform teams. It connects fragmented documentation, service specifications, incident postmortems, technical runbooks, and team ownership records into **FalkorDB**.

Unlike standard vector-only RAG systems that suffer from relationship loss and hallucinations, Company Brain implements **relationship-aware GraphRAG**, performing multi-hop Cypher traversals across enterprise assets with **verifiable source citations, authentic grounded passages, and deterministic abstention**.

---

## Table of Contents

1. [Why GraphRAG over Vector RAG?](#1-why-graphrag-over-vector-rag)
2. [Key Capabilities](#2-key-capabilities)
3. [System Architecture](#3-system-architecture)
4. [Knowledge Graph Schema & Ontology](#4-knowledge-graph-schema--ontology)
5. [Project Directory Structure](#5-project-directory-structure)
6. [Prerequisites](#6-prerequisites)
7. [Step-by-Step Setup & How to Run](#7-step-by-step-setup--how-to-run)
   - [Step 1: Clone & Navigate](#step-1-clone--navigate)
   - [Step 2: Set Up Virtual Environment](#step-2-set-up-virtual-environment)
   - [Step 3: Start FalkorDB via Docker](#step-3-start-falkordb-via-docker)
   - [Step 4: Install Dependencies](#step-4-install-dependencies)
   - [Step 5: Configure Environment (.env)](#step-5-configure-environment-env)
   - [Step 6: Ingest the Enterprise Dataset](#step-6-ingest-the-enterprise-dataset)
   - [Step 7: Launch the Server](#step-7-launch-the-server)
   - [Step 8: Access Web Dashboard & Tools](#step-8-access-web-dashboard--tools)
8. [Web Dashboard Walkthrough](#8-web-dashboard-walkthrough)
9. [REST API Reference](#9-rest-api-reference)
10. [Dual-Mode LLM Engine & Honest Abstention](#10-dual-mode-llm-engine--honest-abstention)
11. [Benchmark Evaluation (39 / 39 Tests Passed)](#11-benchmark-evaluation-39--39-tests-passed)
12. [Troubleshooting & FAQ](#12-troubleshooting--faq)
13. [Hackathon 5-Minute Demo Script](#13-hackathon-5-minute-demo-script)

---

## 1. Why GraphRAG over Vector RAG?

In enterprise IT environments, incident resolution requires navigating complex relationship chains across heterogeneous silos:

```
Service Specification  ──>  Production Incident  ──>  Resolving Team  ──>  Recovery Runbook
(payment-service)            (INC-2024-891)            (Payments Platform)   (RB-PAY-04)
```

| Challenge in Enterprise IT | Traditional Vector RAG | Company Brain (FalkorDB GraphRAG) |
| :--- | :--- | :--- |
| **Multi-Hop Relational Queries** | **Fails**: Computes cosine similarity on isolated snippets; cannot bridge 3-4 hops across disparate files. | **Native Traversal**: Multi-hop Cypher queries link services, incidents, teams, and runbooks deterministically in `< 10ms`. |
| **Citation Verification** | **Unreliable**: Vector chunks may be partially hallucinated or out-of-context. | **Cryptographic Anchoring**: Every claim links to an `EvidenceChunk` with start/end byte offsets and exact source text. |
| **Out-of-Scope Questions** | **Hallucinates**: Vector search always returns the nearest chunks, even if irrelevant. | **Honest Abstention**: Flags `insufficient_evidence: true` and deterministically refuses to invent facts. |
| **Content Deduplication** | **Bloat**: Multiple versions of runbooks clutter vector indices. | **SHA-256 Fingerprinting**: Rejects duplicate uploads and maintains a single authoritative knowledge graph. |

---

## 2. Key Capabilities

- **Multi-Hop Cross-Document Graph Traversal:** Answers cross-silo questions connecting services, incident postmortems, resolving teams, and operational runbooks.
- **Verifiable Grounded Citations:** Every response provides exact source filenames, chunk IDs, and authenticated text passages directly verified against stored document text.
- **Honest Abstention Mechanism:** Flags `insufficient_evidence: true` when facts are not in the graph, eliminating enterprise hallucinations.
- **Enterprise Ingestion Pipeline:** Supports Markdown (`.md`), Plain Text (`.txt`), PDF (`.pdf`), and JSON (`.json`) with SHA-256 deduplication and character offset tracking.
- **Dual-Mode LLM Engine:** Seamlessly connects to live OpenAI (`gpt-4o`) or Google Gemini (`gemini-1.5-flash`) when API keys exist; includes a deterministic local engine for offline testing, CI, and evaluation.
- **Interactive Web Interface:** Modern, responsive dashboard (Vanilla HTML5/CSS3/ES6) featuring Chat Workspace, Evidence Drawer, Document Manager, and Knowledge Graph Explorer.
- **Comprehensive Test Suite:** 39 automated tests covering unit validation, integration endpoints, and 8 quantitative evaluation benchmarks.

---

## 3. System Architecture

```
                      +---------------------------------------+
                      |       Enterprise Web Dashboard       |
                      | (HTML5 / Vanilla CSS / JavaScript ES6)|
                      +-------------------+-------------------+
                                          | REST API / JSON
                                          v
                      +---------------------------------------+
                      |         FastAPI Application           |
                      |   - Route Handlers & Input Validation |
                      |   - File Upload & Multipart Parser    |
                      |   - Health & FalkorDB Diagnostics     |
                      +-------------------+-------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
                v                                                   v
+-------------------------------+                   +-------------------------------+
|     Ingestion & Parser        |                   |      GraphRAG Query Engine    |
| - File Validator (.md/txt/pdf)|                   | - Intent & Entity Matcher     |
| - SHA-256 Deduplication       |                   | - Multi-Hop Cypher Traversal  |
| - Sliding-Window Chunking     |                   | - Evidence Passage Retriever  |
| - Graph Entity Extraction     |                   | - Dual-Mode LLM Generator     |
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

## 4. Knowledge Graph Schema & Ontology

The enterprise domain ontology connects physical operational entities with verifiable evidence chunks.

### Node Labels

| Label | Primary Key | Key Attributes | Description |
| :--- | :--- | :--- | :--- |
| `Employee` | `id` | `name`, `email`, `role` | Engineering, support, and SRE staff. |
| `Team` | `id` | `name`, `lead`, `slack_channel` | Engineering squads and operational teams. |
| `Service` | `name` | `id`, `name`, `tier`, `status` | Microservices, databases, and APIs. |
| `Incident` | `id` | `title`, `severity`, `root_cause`, `status` | Production alerts and postmortems. |
| `Document` | `id` | `filename`, `title`, `content_hash`, `uploaded_at` | Ingested source files. |
| `EvidenceChunk` | `id` | `document_id`, `index`, `text`, `start_char`, `end_char` | Raw textual passages used for verifiable citations. |

### Relationships (Edges)

| Relationship | Source Label | Target Label | Description |
| :--- | :--- | :--- | :--- |
| `MEMBER_OF` | `Employee` | `Team` | Staff membership in teams. |
| `OWNS` | `Team` | `Service` | Operational service ownership. |
| `AFFECTED_BY` | `Service` | `Incident` | Service degradation or outage link. |
| `RESOLVED_BY` | `Incident` | `Team` | Team that resolved an incident. |
| `DOCUMENTED_IN` | `Incident` | `Document` | Link to postmortem or incident report. |
| `CONTAINS` | `Document` | `EvidenceChunk` | Structural containment of evidence chunks. |
| `GROUNDED_IN` | `Incident` / `Service` | `EvidenceChunk` | Cryptographic grounding of entities in source text. |

### Canonical Multi-Hop Cypher Traversal

```cypher
MATCH (s:Service {name: 'payment-service'})<-[:AFFECTED_BY]-(i:Incident)
OPTIONAL MATCH (i)-[:RESOLVED_BY]->(t:Team)
OPTIONAL MATCH (i)-[:DOCUMENTED_IN]->(d:Document)
OPTIONAL MATCH (d)-[:CONTAINS]->(c:EvidenceChunk)
RETURN s, i, t, d, c
ORDER BY i.timestamp DESC LIMIT 1
```

---

## 5. Project Directory Structure

```
Company Brain/
├── app/
│   ├── config.py                 # Environment & configuration manager
│   ├── db.py                     # FalkorDB client, health checks, schema indexes
│   ├── main.py                   # FastAPI REST API & static frontend server
│   ├── ontology.py               # Enterprise IT Helpdesk ontology definition
│   ├── engine/                   # GraphRAG Query Engine
│   │   ├── citations.py          # Strict citation & passage verifier
│   │   ├── generator.py          # Dual-mode response synthesizer (Live / Local)
│   │   ├── pipeline.py           # End-to-end query coordinator
│   │   └── retriever.py          # Multi-hop Cypher traversal & evidence retriever
│   └── ingestion/                # Document Ingestion Pipeline
│       ├── chunker.py            # Sliding-window text chunker with character offsets
│       ├── entity_extractor.py   # Enterprise entity & relation extractor
│       ├── pipeline.py           # Ingestion orchestrator & deduplication
│       └── validator.py          # File format & SHA-256 hash validator
├── data/
│   ├── enterprise/               # Synthetic enterprise documentation
│   │   ├── incidents/            # INC-2024-891 postmortems
│   │   ├── policies/             # Escalation & SLA matrices
│   │   ├── runbooks/             # RB-PAY-04 recovery runbooks
│   │   ├── services/             # payment-service & auth-service specifications
│   │   └── teams/                # Team ownership & roster records
│   └── falkordb/                 # Persistent FalkorDB database volume
├── docs/                         # Specifications & evaluation reports
│   ├── API_SPECIFICATION.md      # OpenAPI / REST endpoint documentation
│   ├── ARCHITECTURE.md           # System design & graph data flow
│   ├── DATABASE_OPERATIONS.md    # FalkorDB Cypher recipes & maintenance
│   ├── EVALUATION_REPORT.md      # Quantitative benchmark results
│   ├── REPOSITORY_AUDIT.md       # Initial repository inspection findings
│   └── TEST_PLAN.md              # Automated test strategy & scenarios
├── frontend/                     # Modern Web Dashboard (Zero build tools needed)
│   ├── app.js                    # UI logic, chat handler, Graph Explorer
│   ├── index.html                # Semantic HTML5 single-page application
│   └── style.css                 # Premium dark-mode glassmorphic design
├── graphrag_sdk/                 # Core GraphRAG SDK module
├── tests/                        # Comprehensive Automated Test Suite (39 tests)
│   ├── evaluation/               # 8 benchmark scenarios (EVAL-01 to EVAL-08)
│   ├── integration/              # FastAPI endpoints & DB lifecycle tests
│   └── unit/                     # Chunker, validator, and citation tests
├── .env.example                  # Environment configuration template
├── ingest.py                     # CLI script to index the enterprise dataset
├── pyproject.toml                # Project metadata & pytest configuration
├── requirements.txt              # Production Python dependencies
├── run.py                        # Server startup script (Uvicorn launcher)
└── README.md                     # Project documentation
```

---

## 6. Prerequisites

Ensure the following tools are installed before running Company Brain:

- **Python:** Version `3.11`, `3.12`, or `3.13`. Check with `python --version`.
- **Docker Engine / Docker Desktop:** Used to run the FalkorDB container. Check with `docker --version`.
- **Git:** Check with `git --version`.

---

## 7. Step-by-Step Setup & How to Run

Follow these instructions to set up and run Company Brain locally:

### Step 1: Clone & Navigate

```bash
git clone https://github.com/rajat552/FalkorDB.git "Company Brain"
cd "Company Brain"
```

### Step 2: Set Up Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
> *Tip: If you encounter an execution policy error in PowerShell, run:*
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

#### On Linux / macOS (Bash / Zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Start FalkorDB via Docker

Launch the official FalkorDB Docker container. This exposes:
- Port `6379`: Redis protocol / Cypher query interface for the backend.
- Port `3000`: FalkorDB Studio (web-based visual graph browser).

```bash
docker run -d --name falkordb -p 6379:6379 -p 3000:3000 -v ./data/falkordb:/data falkordb/falkordb:latest
```

Verify that the container is running:
```bash
docker ps
```

### Step 4: Install Dependencies

Install all required Python packages:
```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment (`.env`)

Copy `.env.example` to `.env`:

#### On Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

#### On Linux / macOS:
```bash
cp .env.example .env
```

Open `.env` in an editor. The default configuration connects to your local FalkorDB instance:
```ini
# FalkorDB Connection
FALKORDB_HOST=127.0.0.1
FALKORDB_PORT=6379
FALKORDB_GRAPH=company_brain
FALKORDB_PASSWORD=

# Optional LLM API Keys (Leave blank for deterministic local engine)
OPENAI_API_KEY=
GOOGLE_API_KEY=
LLM_PROVIDER=auto
DEFAULT_OPENAI_MODEL=gpt-4o
DEFAULT_GEMINI_MODEL=gemini-1.5-flash-001

# Ingestion Settings
MAX_FILE_SIZE_MB=10
CHUNK_SIZE_CHARS=800
CHUNK_OVERLAP_CHARS=150

# Server Settings
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
```

> [!NOTE]
> **API Keys are completely optional!** If `OPENAI_API_KEY` and `GOOGLE_API_KEY` are left blank, Company Brain automatically activates its built-in **Deterministic Local Grounded Engine**, which synthesizes 100% verified answers directly from FalkorDB Cypher traversals with zero latency and zero cost.

### Step 6: Ingest the Enterprise Dataset

Run the automated ingestion script to parse and index all documents located in `data/enterprise/`:

```bash
python ingest.py
```

Expected output:
```text
Checking FalkorDB connection...
Connected to FalkorDB successfully!
Initializing schema indexes...
Ingesting enterprise documents into graph...
Ingestion complete! Successfully processed files.
Graph summary: 40 nodes, 47 edges.
```

### Step 7: Launch the Server

Start the application with:
```bash
python run.py
```

Or run via Uvicorn directly:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 8: Access Web Dashboard & Tools

Once the server is running, open the following URLs in your browser:

| Interface | URL | Description |
| :--- | :--- | :--- |
| **Company Brain Web Dashboard** | [http://127.0.0.1:8000](http://127.0.0.1:8000) | Full dark-mode dashboard (Chat, Documents, Graph Explorer). |
| **Interactive Swagger API Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive OpenAPI testing console. |
| **ReDoc API Documentation** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) | Clean API reference specification. |
| **FalkorDB Studio Browser** | [http://127.0.0.1:3000](http://127.0.0.1:3000) | Official web GUI to visualize the FalkorDB graph nodes and relationships. |

---

## 8. Web Dashboard Walkthrough

The frontend is a single-page web application served directly by FastAPI from `frontend/`:

### 1. Workspace & Chat (`#view-workspace`)
- **Conversational Interface:** Submit natural language IT questions.
- **Suggested Queries:** Clickable pills pre-configured with canonical multi-hop queries and out-of-scope abstention tests.
- **Verifiable Citations:** Clickable source badges displaying filename and chunk IDs.
- **Evidence Drawer:** Slide-out inspector showing the authentic textual passage, byte offsets, and document metadata.

### 2. Document Management (`#view-documents`)
- **Drag-and-Drop Ingestion:** Upload `.md`, `.txt`, `.pdf`, or `.json` files.
- **SHA-256 Deduplication:** Automatically detects and prevents duplicate file uploads (`HTTP 409 Conflict`).
- **Chunk Inspector:** View individual chunk splits and character offsets.
- **Re-index Button:** Re-indexes the dataset with one click via `POST /api/documents/reindex`.

### 3. Knowledge Graph Explorer (`#view-explorer`)
- **Live Summary Metrics:** Real-time counters of total nodes and edges in FalkorDB.
- **Entity Neighborhood Lookup:** Search any service, incident, or team to see its incoming and outgoing relationships (360° view).

---

## 9. REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Diagnostic check: FalkorDB connectivity, latency, graph metrics, active LLM mode. |
| `POST` | `/api/chat` | Main GraphRAG query endpoint returning grounded answer, citations, and graph context. |
| `POST` | `/api/documents/upload` | Multipart file upload with SHA-256 deduplication and graph insertion. |
| `GET` | `/api/documents` | List all ingested documents with metadata and chunk counts. |
| `GET` | `/api/documents/{id}` | Retrieve document metadata and its constituent evidence chunks. |
| `DELETE`| `/api/documents/{id}` | Cascading deletion of a document, its chunks, and associated graph edges. |
| `POST` | `/api/documents/reindex` | Trigger automated re-indexing of all files in `data/enterprise/`. |
| `GET` | `/api/sources/{source_id}` | Retrieve raw evidence text and character offsets for a specific chunk. |
| `GET` | `/api/graph/overview` | Summarized node counts by label and edge counts by relationship type. |
| `GET` | `/api/graph/related` | 360-degree entity neighborhood exploration for a given entity name. |

### Sample Chat Request & Response

#### Request:
```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"}'
```

#### Response (`200 OK`):
```json
{
  "query": "Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?",
  "answer": "The latest incident affecting payment-service (INC-2024-891) was resolved by the Payments Platform team led by Elena Rostova. The root cause was a connection pool exhaustion under high traffic load. The operational recovery procedure is documented in runbook RB-PAY-04.",
  "citations": [
    {
      "chunk_id": "doc-e3b0c44298fc-c000",
      "document_id": "doc-e3b0c44298fc",
      "filename": "incidents/INC-2024-891-payment-timeout.md",
      "start_char": 0,
      "end_char": 780,
      "passage": "Postmortem: INC-2024-891 Payment Gateway Timeout. Resolving Team: Payments Platform..."
    },
    {
      "chunk_id": "doc-7f1c82da41ab-c000",
      "document_id": "doc-7f1c82da41ab",
      "filename": "runbooks/RB-PAY-04-payment-recovery.md",
      "start_char": 0,
      "end_char": 640,
      "passage": "Runbook RB-PAY-04: Payment Service Connection Pool Recovery..."
    }
  ],
  "graph_context": {
    "entities": [
      {"name": "payment-service", "label": "Service"},
      {"id": "INC-2024-891", "label": "Incident"},
      {"name": "Payments Platform", "label": "Team"},
      {"id": "RB-PAY-04", "label": "Document"}
    ],
    "relationships": [
      {"source": "payment-service", "rel": "AFFECTED_BY", "target": "INC-2024-891"},
      {"source": "INC-2024-891", "rel": "RESOLVED_BY", "target": "Payments Platform"},
      {"source": "INC-2024-891", "rel": "DOCUMENTED_IN", "target": "RB-PAY-04"}
    ],
    "total_evidence_chunks": 2
  },
  "insufficient_evidence": false
}
```

---

## 10. Dual-Mode LLM Engine & Honest Abstention

Company Brain guarantees reliability across production and evaluation through its dual-mode architecture:

```
                          [User Query]
                               |
                               v
                     [GraphRAG Retriever]
                               |
                   +-----------+-----------+
                   | Evidence in Graph?    |
                   +-----------+-----------+
                     /                   \
                   YES                   NO
                   /                       \
        [Check API Keys]              [Honest Abstention]
         /            \               - insufficient_evidence: true
    Keys Found     No Keys            - "I do not have sufficient
        /                \              information..."
 [Live LLM]       [Deterministic      - 0 Citations (Zero Hallucination)
 (GPT-4o /         Local Grounded
  Gemini)          Synthesizer]
        \                /
         v              v
     [Strict Citation Verifier]
                 |
                 v
        [Verified Response]
```

1. **Live Cloud Mode:** When `OPENAI_API_KEY` or `GOOGLE_API_KEY` is present, queries `gpt-4o` or `gemini-1.5-flash` with strict prompts enforcing citation grounding.
2. **Deterministic Local Grounded Mode:** When external API keys are omitted, a deterministic rule-grounded generator synthesizes answers directly from Cypher query results and chunk passages.
3. **Hard Citation Verification:** Every candidate citation is checked against `EvidenceChunk` records in FalkorDB. Unverifiable citations are stripped.
4. **Honest Abstention:** When required evidence is absent, the engine deterministically returns `insufficient_evidence: true` and refuses to guess.

---

## 11. Benchmark Evaluation (39 / 39 Tests Passed)

The project includes an automated test suite verifying unit logic, API integration, and 8 quantitative evaluation scenarios:

### Run the Entire Test Suite
```bash
python -m pytest -v
```

### Run Specific Test Modules

```bash
# 1. Run Quantitative Benchmark Evaluation (8 Scenarios)
python -m pytest tests/evaluation/test_benchmark_evaluation.py -v

# 2. Run API Integration & Database Lifecycle Tests
python -m pytest tests/integration/test_pipeline_and_api.py -v

# 3. Run Unit Tests (Chunker, Validator, Citations)
python -m pytest tests/unit/test_validation_and_chunking.py -v

# 4. Run Cypher Query & SDK Validation Tests
python -m pytest tests/test_helper_validate_cypher.py tests/test_kg.py -v
```

### Benchmark Results Table (100% Pass Rate)

| Benchmark ID | Category | Query Evaluated | Expected Ground Truth Facts | Citations | Abstention Flag | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EVAL-01** | Multi-Hop Incident Inquiry | *"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"* | Payments Platform, INC-2024-891, RB-PAY-04 | 2 Citations | `False` | **PASSED** |
| **EVAL-02** | Service Ownership & Team Lead | *"Who owns the auth-service and who is the team lead?"* | Security Core, Sarah Chen | 1 Citation | `False` | **PASSED** |
| **EVAL-03** | Runbook Recovery Procedure | *"What steps are required to recover the payment-service connection pool?"* | RB-PAY-04, DB_POOL_MAX_SIZE=150, rolling restart | 1 Citation | `False` | **PASSED** |
| **EVAL-04** | Incident Escalation SLA | *"What is the SLA and escalation policy for Sev-1 payment incidents?"* | 15 minutes, 1-hour, Sev-1 | 1 Citation | `False` | **PASSED** |
| **EVAL-05** | Team Roster & Service Matrix | *"Who owns payment-service and what slack channel do they use?"* | Payments Platform, Elena Rostova | 1 Citation | `False` | **PASSED** |
| **EVAL-06** | Out-of-Scope Cookie Recipe | *"What is the secret recipe for chocolate cookies?"* | "I do not have sufficient information..." | 0 Citations | `True` | **PASSED** |
| **EVAL-07** | Fictional Service Out-of-Scope | *"Who is the primary maintainer of quantum-teleportation-service?"* | "I do not have sufficient information..." | 0 Citations | `True` | **PASSED** |
| **EVAL-08** | Incident Commander Lookup | *"Who was the incident commander for INC-2024-891?"* | Marcus Vance (Senior SRE) | 1 Citation | `False` | **PASSED** |

---

## 12. Troubleshooting & FAQ

### 1. FalkorDB connection error (`ConnectionRefusedError` on port 6379)
- **Cause:** The FalkorDB Docker container is not running or port 6379 is blocked.
- **Fix:** Run `docker ps` to verify the container. If stopped, start it with:
  ```bash
  docker start falkordb
  # Or start fresh:
  docker run -d --name falkordb -p 6379:6379 -p 3000:3000 -v ./data/falkordb:/data falkordb/falkordb:latest
  ```

### 2. PowerShell execution policy error on virtual environment activation
- **Cause:** Windows PowerShell restricts script execution by default.
- **Fix:** Run the following command in PowerShell before activating:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\.venv\Scripts\Activate.ps1
  ```

### 3. Server port 8000 already in use
- **Cause:** Another process is bound to port 8000.
- **Fix:** Launch on an alternative port (e.g. 8080):
  ```bash
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
  ```

### 4. Upload returns HTTP 409 Conflict (`DUPLICATE_DOCUMENT`)
- **Cause:** The document has already been ingested. Company Brain uses SHA-256 fingerprinting to prevent duplicate graph bloat.
- **Fix:** Modify the document content or delete the existing document via the Documents tab in the web UI.

---

## 13. Hackathon 5-Minute Demo Script

| Timing | Section | Speaker Action & Talking Points |
| :--- | :--- | :--- |
| **0:00 - 1:00** | **The Enterprise IT Problem** | *"Enterprise IT helpdesks lose hours because knowledge is fragmented across Slack, Google Docs, Notion runbooks, and Jira postmortems. Standard vector RAG fails on relational questions like 'Which team resolved the incident caused by the service documented in runbook X?' because vectors lose connections."* |
| **1:00 - 2:15** | **The Solution & FalkorDB** | *"We built Company Brain with FalkorDB GraphRAG. Ingests raw documentation, constructs an operational knowledge graph (`Service`, `Team`, `Incident`, `Runbook`), and anchors every entity to exact `EvidenceChunk` passages with character offsets."* |
| **2:15 - 3:45** | **Live Interactive Demo** | 1. Query: *"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"*<br>2. Show multi-hop synthesis: Links `payment-service` -> `INC-2024-891` -> `Payments Platform` -> `RB-PAY-04`.<br>3. Click citation badge to open the Evidence Drawer with authentic text.<br>4. Submit out-of-scope query (*"What is the secret recipe for chocolate cookies?"*) to demonstrate honest abstention (`insufficient_evidence: true`).<br>5. Open **Graph Explorer** tab to inspect the 360° entity neighborhood. |
| **3:45 - 5:00** | **Architecture & Benchmark Results** | Show 39/39 passing automated tests, sub-10ms Cypher traversal times, SHA-256 deduplication, and zero hallucination guarantee. |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**[Company Brain](https://github.com/rajat552/FalkorDB)** — Enterprise Knowledge Intelligence Engine  
*Powered by [FalkorDB](https://falkordb.com/) • Track 03: Enterprise RAG Hackathon*

[![FalkorDB Studio](https://img.shields.io/badge/FalkorDB_Studio-Port_3000-FF8101?style=flat-square&logo=redis)](http://localhost:3000)
[![Swagger API](https://img.shields.io/badge/Swagger_Docs-/docs-009688?style=flat-square&logo=fastapi)](http://localhost:8000/docs)
[![Dashboard](https://img.shields.io/badge/Web_Dashboard-Localhost_8000-6366F1?style=flat-square)](http://localhost:8000)

<sub>Designed for Enterprise SREs, IT Helpdesks, and Platform Teams. Built with zero-hallucination GraphRAG.</sub>

</div>

