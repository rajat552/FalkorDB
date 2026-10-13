# Company Brain — Implementation Plan (Track 03: Enterprise RAG)

## 1. Project Overview & Target Objective

Build **"Company Brain"**, an enterprise knowledge intelligence assistant for an internal IT helpdesk. Company Brain ingests company documents, technical runbooks, incident reports, service architecture documentation, and team ownership records into FalkorDB. It answers cross-document IT queries with verified citations, supporting passages, and knowledge graph relationship traversals, while honestly abstaining when evidence is insufficient.

---

## 2. Milestone Progress Checklist

- [x] **Milestone 1 — Repository Audit & Environment Baseline (Phase 1)**
  - Audited repository files, Python 3.13 dependencies, FalkorDB Docker container, and test state.
  - Resolved Python 3.13 pip installation hurdles for `ratelimit`, `falkordb`, `openai`, `pypdf`, `beautifulsoup4`.
  - Identified circular import bug in `graphrag_sdk/helpers.py` and missing exports in `graphrag_sdk/__init__.py`.
  - Created [`docs/REPOSITORY_AUDIT.md`](docs/REPOSITORY_AUDIT.md).

- [x] **Milestone 2 — Product Specification & Architecture (Phase 2)**
  - Created [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).
  - Created [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
  - Created [`docs/API_SPECIFICATION.md`](docs/API_SPECIFICATION.md).
  - Created [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md).

- [x] **Milestone 3 — Environment, Core SDK Fix & Database Diagnostics (Phase 3)**
  - Resolved circular import in `graphrag_sdk/__init__.py` and `graphrag_sdk/helpers.py`.
  - Verified existing SDK unit tests run cleanly.
  - Implemented FalkorDB health check, connection diagnostics, and retry utilities.
  - Created `.env` configuration loader with fallback diagnostic reporting.

- [x] **Milestone 4 — Synthetic Enterprise Dataset & Document Ingestion Engine (Phase 4)**
  - Generated realistic enterprise dataset in `data/enterprise/`:
    - Service Docs: Payment Gateway, Auth Service, Order Engine, Notification Hub.
    - Incident Reports: INC-2024-891 (payment timeout), INC-2024-912 (auth memory leak).
    - Runbooks: RB-PAY-04 (payment circuit breaker reset), RB-AUTH-02 (token flush).
    - Team & Ownership: Platform engineering, Payments, Security, SRE rosters.
    - IT Policies: Escalation matrix, SLA definitions, incident triage policy.
  - Built ingestion pipeline (`app/ingestion/`):
    - File validation (type, size, encoding).
    - Chunking with chunk ID, byte offsets, and document hashing (SHA-256) for deduplication.
    - Transactional graph ingestion and cascade deletion of documents and chunks.

- [x] **Milestone 5 — Domain Ontology & Graph Model (Phase 5)**
  - Defined Enterprise IT Ontology in FalkorDB:
    - Entities: `Employee`, `Team`, `Service`, `Incident`, `Document`, `EvidenceChunk`.
    - Relationships: `MEMBER_OF`, `OWNS`, `AFFECTED_BY`, `RESOLVED_BY`, `DOCUMENTED_IN`, `CONTAINS`.
  - Built entity normalization and edge validator.
  - Verified bidirectional traceability from graph entities to source `Document` and `EvidenceChunk` nodes.

- [x] **Milestone 6 — GraphRAG Query Engine with Verifiable Citations (Phase 6)**
  - Built GraphRAG Query Engine (`app/engine/`):
    - Multi-hop Cypher traversal for cross-document questions.
    - Evidence extraction & passage grounding.
    - Strict citation verification (matching document IDs, filenames, and text passages).
    - Deterministic abstention logic (`insufficient_evidence: true`) when evidence is missing.
    - Dual-mode LLM engine: Live OpenAI / Gemini when keys are present, and deterministic rule-grounded generator for testing.

- [x] **Milestone 7 — Backend REST API (Phase 7)**
  - Implemented FastAPI backend (`app/main.py`):
    - `GET /health` — Database status, graph metrics, model status.
    - `POST /api/documents/upload` — Multipart file upload with hash deduplication.
    - `GET /api/documents` — List all ingested documents and metadata.
    - `GET /api/documents/{document_id}` — Document details and chunks.
    - `DELETE /api/documents/{document_id}` — Cascading removal of document & graph references.
    - `POST /api/chat` — Relationship-aware querying with structured citations and graph context.
    - `GET /api/sources/{source_id}` — Supporting passage inspection.
    - `GET /api/graph/overview` — Graph node/edge summary and entity listing.
    - `GET /api/graph/related` — Entity neighborhood inspection.
  - Implemented CORS, logging, validation schemas, and automated endpoint tests.

- [x] **Milestone 8 — Professional Frontend Interface (Phase 8)**
  - Built modern, responsive UI (`frontend/`):
    - Knowledge Workspace: Conversational interface with suggested enterprise questions.
    - Document Management: Drag-and-drop file upload, file status, delete actions.
    - Answer Evidence Panel: Real-time citations, verifiable passages, document metadata.
    - Knowledge Graph Explorer: Entity cards, relationship lists, visual connection viewer.
    - Operational States: Loading, error notifications, offline/insufficient-evidence badges.
  - Served frontend directly from FastAPI static mount.

- [x] **Milestone 9 — Automated Testing, Security & Evaluation (Phase 9)**
  - Unit tests: validation, chunking, citation matching, abstention logic.
  - Integration tests: FalkorDB queries, document ingestion, entity creation.
  - End-to-end evaluation suite: 8 benchmark scenarios measuring correctness, groundedness, and abstention honesty (39/39 tests passed).

- [x] **Milestone 10 — Documentation & Hackathon Finalization (Phase 10)**
  - Completed `README.md` with architecture diagrams, quickstart, and demo walkthrough.
  - Documented evaluation benchmark results in `docs/EVALUATION_REPORT.md`.
  - Created `run.py` and `ingest.py` production scripts.

---

## 3. Risk Management & Fallback Strategies

| Identified Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **No API Keys in Environment** | High | Implemented dual-mode engine: connects to live OpenAI / Gemini when configured, but includes a deterministic, verified local engine for offline testing and evaluation without crashes. |
| **SDK Circular Import Bug** | High | Resolved import order in `graphrag_sdk/__init__.py` and typed `helpers.py` safely using string annotations. |
| **Python 3.13 Windows Pip Sdist Bug** | Medium | Built wheels for sdist-only packages (`ratelimit`) avoiding `tarfile.py` regression. |
| **FalkorDB Container Disruption** | Medium | Application includes connection health check and auto-reconnect logic on port 6379. |
| **Hallucinated Citations** | High | Hard citation verification layer validates passages against actual chunk text before attaching to output. |
