# File Inventory & Classification Matrix: Company Brain

**Date:** 2026-10-15  
**Auditor:** Senior Software Architect & Code Quality Auditor  

This document tracks the classification, operational purpose, dependency relationships, and cleanup recommendations for all files and directories in the repository.

---

## 1. Classification Definitions

| Classification | Meaning |
| :--- | :--- |
| **KEEP AND TRACK** | Essential source code, configuration, assets, or tests required for reproducible development, CI/CD, and production runtime. |
| **ADD TO GITIGNORE** | Machine-specific, local-only, cache, or sensitive files that must not be committed to Git. |
| **REGENERATE WHEN NEEDED** | Build outputs, logs, or local database snapshots that can be recreated reliably from source code or seed scripts. |
| **REMOVE** | Verified obsolete, unused, or dead files with no active references in code, tests, or deployment. |
| **REFACTOR** | Essential files that require updates to dependencies, formatting, or missing configurations. |
| **INVESTIGATE** | Items requiring verification before final action. |

---

## 2. File & Directory Inventory

### 2.1 Project Root Files & Configuration

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `README.md` | **KEEP AND TRACK** | Root documentation and GitHub repository showcase | GitHub UI, user onboarding | Kept; fully up to date with real screenshots and architecture. |
| `IMPLEMENTATION_PLAN.md` | **KEEP AND TRACK** | Master engineering delivery checklist | Documentation index | Kept; tracks 10 milestone deliveries. |
| `run.py` | **KEEP AND TRACK** | Production/development server startup entrypoint | Manual execution (`python run.py`) | Kept; launches Uvicorn server with configured host/port. |
| `ingest.py` | **KEEP AND TRACK** | CLI dataset ingestion runner | Manual execution (`python ingest.py`) | Kept; supports `--force` reindexing flag. |
| `requirements.txt` | **KEEP AND TRACK** | Pip dependencies manifest | `pip install -r requirements.txt` | Kept; contains all 13 verified runtime dependencies. |
| `pyproject.toml` | **REFACTOR** | Poetry package manifest and pytest configuration | CI workflow (`test.yml`), `pytest` | Refactor: add `fastapi`, `uvicorn`, `pydantic`, `httpx`; remove unused `python-abc`, `vertexai`. |
| `.env.example` | **KEEP AND TRACK** | Safe environment variable template | Setup instructions, developers | Kept; non-secret template for local `.env`. |
| `.env` | **ADD TO GITIGNORE** | Active local environment variables | `app/config.py` | Kept local; strictly ignored by Git. |
| `.gitignore` | **REFACTOR** | Git exclusion rules | Git VCS | Refactor: expand with standard Python, OS, IDE, and test artifacts. |
| `.spellcheck.yml` | **KEEP AND TRACK** *(New)* | Spellchecking configuration for GitHub Actions | `.github/workflows/spellcheck.yml` | Add: config required by existing CI spellcheck workflow. |

---

### 2.2 CI/CD Workflows (`.github/workflows/`)

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `.github/workflows/test.yml` | **KEEP AND TRACK** | CI pipeline for FalkorDB integration & pytest suite | GitHub Actions on PR | Kept; requires `pyproject.toml` dependency synchronization. |
| `.github/workflows/spellcheck.yml`| **KEEP AND TRACK** | Markdown spellcheck workflow | GitHub Actions on PR & push | Kept; paired with `.spellcheck.yml`. |

---

### 2.3 Core Application (`app/`)

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `app/__init__.py` | **KEEP AND TRACK** | Application package marker | Python module resolver | Kept. |
| `app/config.py` | **KEEP AND TRACK** | Environment settings and defaults | `app/db.py`, `app/main.py`, `run.py` | Kept. |
| `app/db.py` | **KEEP AND TRACK** | FalkorDB client, schema indexes, connection retries | `app/main.py`, `ingest.py`, `tests/` | Kept. |
| `app/ontology.py` | **KEEP AND TRACK** | Enterprise domain graph ontology | `app/db.py`, `app/ingestion/` | Kept; models `Service`, `Team`, `Incident`, `Employee`, `Document`, `EvidenceChunk`. |
| `app/main.py` | **KEEP AND TRACK** | FastAPI routes, CORS, lifespan startup, static mounts | `run.py`, HTTP clients, `tests/` | Kept. |
| `app/engine/citations.py` | **KEEP AND TRACK** | Citation extraction and character offset validation | `app/engine/generator.py`, `tests/` | Kept. |
| `app/engine/generator.py` | **KEEP AND TRACK** | Deterministic & LLM grounded answer synthesis | `app/engine/pipeline.py` | Kept; supports local rule engine, OpenAI, and Gemini. |
| `app/engine/pipeline.py` | **KEEP AND TRACK** | High-level query coordinator (`query_company_brain`) | `app/main.py` | Kept. |
| `app/engine/retriever.py` | **KEEP AND TRACK** | Multi-hop Cypher queries and evidence retrieval | `app/engine/pipeline.py` | Kept; service dependency and catalog graph traversal. |
| `app/ingestion/chunker.py` | **KEEP AND TRACK** | Sliding window chunker with offset boundaries | `app/ingestion/pipeline.py`, `tests/` | Kept. |
| `app/ingestion/entity_extractor.py`| **KEEP AND TRACK** | Entity and relationship extractor from text | `app/ingestion/pipeline.py` | Kept; extracts service dependencies, owners, team members. |
| `app/ingestion/pipeline.py`| **KEEP AND TRACK** | Document ingestion, deduplication, cascade deletion | `app/main.py`, `ingest.py`, `tests/` | Kept; supports force reindexing. |
| `app/ingestion/validator.py` | **KEEP AND TRACK** | Format validation and SHA-256 digest hashing | `app/ingestion/pipeline.py`, `tests/` | Kept. |

---

### 2.4 Frontend Dashboard (`frontend/`)

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `frontend/index.html` | **KEEP AND TRACK** | Semantic SPA markup with ARIA accessibility | `app/main.py` (served at `/`) | Kept; clean semantic structure. |
| `frontend/style.css` | **KEEP AND TRACK** | Unified design tokens, flex layouts, luxury footer | `frontend/index.html` | Kept; WCAG AA compliant. |
| `frontend/app.js` | **KEEP AND TRACK** | SPA controller, HiDPI canvas visualizer, toasts | `frontend/index.html` | Kept; handles chat, dropzone, and graph exploration. |

---

### 2.5 Documentation & Assets (`docs/`)

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `docs/API_SPECIFICATION.md` | **KEEP AND TRACK** | Complete OpenAPI / REST API specification | Developers, README links | Kept. |
| `docs/ARCHITECTURE.md` | **KEEP AND TRACK** | High-level architecture and schema documentation | Developers, README links | Kept. |
| `docs/TECHNICAL_ARCHITECTURE.md`| **KEEP AND TRACK**| Detailed component deep-dive with Mermaid diagrams | Architecture review | Kept. |
| `docs/DATABASE_OPERATIONS.md` | **KEEP AND TRACK** | FalkorDB operational guide | DevOps, SRE | Kept. |
| `docs/END_TO_END_WORKFLOW.md` | **KEEP AND TRACK** | Ingestion & query lifecycle workflows | Reviewers, Hackathon judges | Kept. |
| `docs/EVALUATION_REPORT.md` | **KEEP AND TRACK** | Quantitative benchmark evaluation metrics | Hackathon judges | Kept. |
| `docs/FEATURE_STATUS.md` | **KEEP AND TRACK** | Feature completeness matrix | Project management | Kept. |
| `docs/FRONTEND_UI_AUDIT.md` | **KEEP AND TRACK** | Design tokens and accessibility checklist | Frontend developers | Kept. |
| `docs/HACKATHON_*.md` (4 files)| **KEEP AND TRACK**| Track alignment, requirements, action plan | Hackathon submission | Kept. |
| `docs/JUDGE_PERSPECTIVE_REVIEW.md`| **KEEP AND TRACK**| Hackathon scoring and judging alignment | Pitch preparation | Kept. |
| `docs/PROJECT_*.md` (2 files) | **KEEP AND TRACK** | Overview and plain-English explanations | Onboarding, presentations | Kept. |
| `docs/REPOSITORY_AUDIT.md` | **KEEP AND TRACK** | Full codebase audit and dependency analysis | DevOps, Maintainers | Kept; newly updated. |
| `docs/FILE_INVENTORY.md` | **KEEP AND TRACK** | File classification and decision register | Maintenance, Audits | Newly created. |
| `docs/TECHNICAL_RISKS.md` | **KEEP AND TRACK** | Risk register and mitigations | Architecture review | Kept. |
| `docs/TEST_PLAN.md` | **KEEP AND TRACK** | Test specifications and test strategy | QA, Developers | Kept. |
| `docs/assets/screenshots/*` (4 pngs)| **KEEP AND TRACK**| Genuine running application UI screenshots | `README.md` | Kept; embedded in GitHub README. |

---

### 2.6 Synthetic Enterprise Dataset (`data/enterprise/`)

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `data/enterprise/incidents/INC-2024-891-payment-timeout.md` | **KEEP AND TRACK** | Real-world incident postmortem fixture | `ingest.py`, EVAL-01, EVAL-08 | Kept. |
| `data/enterprise/policies/it-incident-escalation-policy.md` | **KEEP AND TRACK** | IT escalation matrix fixture | `ingest.py`, EVAL-03 | Kept. |
| `data/enterprise/runbooks/RB-PAY-04-payment-recovery.md` | **KEEP AND TRACK** | Disaster recovery runbook fixture | `ingest.py`, EVAL-01, EVAL-04 | Kept. |
| `data/enterprise/services/auth-service-spec.md` | **KEEP AND TRACK** | Authentication service architecture fixture | `ingest.py`, dependency tests | Kept. |
| `data/enterprise/services/payment-service-spec.md` | **KEEP AND TRACK** | Payment service architecture fixture | `ingest.py`, EVAL-01 | Kept. |
| `data/enterprise/teams/team-ownership-roster.md` | **KEEP AND TRACK** | Team directory & on-call roster fixture | `ingest.py`, EVAL-02, EVAL-05 | Kept. |

---

### 2.7 Bundled GraphRAG SDK (`graphrag_sdk/`)

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `graphrag_sdk/__init__.py` | **KEEP AND TRACK** | Public exports for Ontology, Entity, Relation | `app/ontology.py`, `tests/` | Kept; verified clean imports. |
| `graphrag_sdk/*.py` (10 files) | **KEEP AND TRACK** | Core classes (Attribute, Entity, Relation, KG, Helpers)| `app/ontology.py`, `tests/` | Kept. |
| `graphrag_sdk/agents/` | **KEEP AND TRACK** | Agent abstractions (`kg_agent.py`) | SDK tests | Kept. |
| `graphrag_sdk/document_loaders/`| **KEEP AND TRACK**| Loaders for PDF, HTML, text, CSV, JSONL | SDK loaders | Kept. |
| `graphrag_sdk/models/` | **KEEP AND TRACK** | LLM model wrappers (OpenAI, Gemini, Ollama) | `app/engine/generator.py` | Kept. |
| `graphrag_sdk/orchestrator/` | **KEEP AND TRACK** | Multi-agent execution planner and steps | SDK orchestration | Kept. |
| `graphrag_sdk/steps/` | **KEEP AND TRACK** | Extraction, QA, and Cypher generation steps | SDK query steps | Kept. |

---

### 2.8 Automated Tests (`tests/`)

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `tests/evaluation/test_benchmark_evaluation.py` | **KEEP AND TRACK** | 8 Quantitative benchmark scenarios (`EVAL-01`..`08`)| `pytest` | Kept; 100% passing. |
| `tests/integration/test_pipeline_and_api.py` | **KEEP AND TRACK** | API endpoints, upload, delete, chat tests | `pytest` | Kept; 100% passing. |
| `tests/unit/test_validation_and_chunking.py` | **KEEP AND TRACK** | Format validation, hash, chunk boundary tests | `pytest` | Kept; 100% passing. |
| `tests/test_helper_validate_cypher.py` | **KEEP AND TRACK** | 12 SDK Cypher query validation tests | `pytest` | Kept; 100% passing. |
| `tests/test_kg.py` | **KEEP AND TRACK** | 4 SDK KnowledgeGraph node/edge tests | `pytest` | Kept; 100% passing. |

---

### 2.9 Local Runtime, Cache & Ignored Data

| File / Path | Classification | Purpose | Direct References / Callers | Status & Action |
| :--- | :--- | :--- | :--- | :--- |
| `data/falkordb/dump.rdb` | **ADD TO GITIGNORE** | Persistent local Redis/FalkorDB database snapshot | Docker container volume | Local-only; ignored by Git. |
| `__pycache__/` (all directories)| **ADD TO GITIGNORE** | Compiled Python bytecode (`.pyc`) | Python runtime | Machine-specific; ignored by Git. |
| `.pytest_cache/` | **ADD TO GITIGNORE** | Pytest test execution cache | Pytest runtime | Machine-specific; ignored by Git. |
| `.venv/` | **ADD TO GITIGNORE** | Python virtual environment | Local shell | Machine-specific; ignored by Git. |
