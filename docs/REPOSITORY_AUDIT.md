# Repository Audit Report: Company Brain (Track 03 — Enterprise RAG)

**Date:** 2026-10-15  
**Target Solution:** Company Brain — Enterprise Knowledge Intelligence Assistant for IT Helpdesk & SRE  
**Auditor:** Senior Software Architect & DevOps Lead  

---

## 1. Executive Summary

This repository hosts **Company Brain**, a production-grade enterprise GraphRAG intelligence platform built on **FalkorDB** for IT helpdesk, DevOps, and Site Reliability Engineering (SRE) teams. 

Originally cloned from the base FalkorDB GraphRAG SDK (`graphrag_sdk` v0.1.2-beta), the repository has evolved into a complete, full-stack enterprise knowledge intelligence system comprising:
1. **A FalkorDB Graph Core** implementing a domain-specific IT ontology (`Service`, `Team`, `Incident`, `Employee`, `Document`, `EvidenceChunk`).
2. **An Ingestion Pipeline** providing MIME validation, SHA-256 fingerprinting for deduplication, deterministic sliding-window chunking, and relationship extraction.
3. **A Dual-Mode GraphRAG Retrieval & Generation Engine** executing multi-hop Cypher traversals, verifiable textual citation extraction with character offsets, and honest abstention when evidence is insufficient.
4. **A FastAPI REST API** with OpenAPI documentation, health monitoring, cascading document lifecycle management, and graph explorer query endpoints.
5. **A Responsive Web Dashboard** built with Vanilla CSS design tokens (WCAG AA compliant), HiDPI HTML5 Canvas graph visualizer, and verifiable citation drawer.
6. **An Automated Test & Benchmark Suite** verifying 100% test pass rate across 42 automated unit, integration, and quantitative evaluation benchmark tests (`EVAL-01` through `EVAL-08`).

---

## 2. Architecture & Technology Stack

| Component | Technology | Version / Specification | Role in Application |
| :--- | :--- | :--- | :--- |
| **Primary Database** | FalkorDB | `v1.7+` (Docker container on port `6379`) | Graph database storing nodes, relations, and text chunks |
| **Backend Framework** | FastAPI | `0.115.0+` | REST API routes, lifespan startup, CORS, static file serving |
| **ASGI Web Server** | Uvicorn | `0.30.0+` | High-performance asynchronous HTTP server |
| **Data Validation** | Pydantic v2 | `2.8.0+` | Request/response DTO schemas and configuration models |
| **Graph Query Language** | OpenCypher | Native FalkorDB | Graph pattern matching, path traversal, multi-hop joins |
| **Graph SDK** | `graphrag_sdk` | `0.1.2-beta` (local module) | Low-level FalkorDB ontology, entity, and relation abstractions |
| **Document Parsers** | PyPDF, BeautifulSoup4 | `pypdf>=5.0.0`, `beautifulsoup4>=4.12.0` | PDF and HTML document parsing and text extraction |
| **JSON Repair** | fix-busted-json | `0.0.19+` | Resilience against malformed JSON strings from LLMs |
| **Resilience & Retries** | Backoff | `2.2.1+` | Exponential backoff for database connection retries |
| **Generative LLM (Cloud)** | OpenAI / Google Gemini | `openai>=1.35.0`, `google-generativeai>=0.8.0` | Optional generative synthesis (GPT-4o, Gemini 1.5 Flash) |
| **Deterministic Generator** | Local Rule Engine | Native Python (`app/engine/generator.py`) | Zero-cost, zero-latency, 100% grounded fallback generator |
| **Frontend UI** | HTML5 / CSS3 / ES6 | Native Vanilla Web Stack (No Webpack/Vite) | Responsive workspace, Evidence Drawer, HTML5 canvas graph |
| **Testing Framework** | Pytest | `pytest>=8.2.0`, `anyio>=4.13.0` | Automated test suite (42 unit, integration, and benchmark tests) |
| **HTTP Client (Testing)** | HTTPX | `0.27.0+` | Backend integration test client (`TestClient`) |

---

## 3. Directory Structure & Source File Mapping

```text
Company Brain/
├── .env.example                          # Safe environment configuration template
├── .gitignore                            # Git exclusion rules
├── .github/
│   └── workflows/
│       ├── test.yml                      # CI test pipeline (Poetry + Pytest)
│       └── spellcheck.yml                # CI markdown spellcheck workflow
├── app/                                  # Core Application Package
│   ├── __init__.py                       # Package initializer
│   ├── config.py                         # Environment variable loader and settings
│   ├── db.py                             # FalkorDB client, schema indexer, retry connection
│   ├── main.py                           # FastAPI endpoints, CORS, static mounts, lifespan
│   ├── ontology.py                       # Enterprise IT domain ontology definition
│   ├── engine/                           # GraphRAG Query & Citation Engine
│   │   ├── citations.py                  # Citation extraction, offset validation, formatting
│   │   ├── generator.py                  # Dual-mode synthesis (Deterministic / OpenAI / Gemini)
│   │   ├── pipeline.py                   # High-level query coordinator (query_company_brain)
│   │   └── retriever.py                  # Multi-hop Cypher queries and evidence collector
│   └── ingestion/                        # Document Processing Pipeline
│       ├── chunker.py                    # Sliding window chunker (start/end char tracking)
│       ├── entity_extractor.py           # Regex & AST extraction for services, teams, incidents
│       ├── pipeline.py                   # Atomic graph ingestion, deduplication, cascade deletion
│       └── validator.py                  # MIME format validation and SHA-256 fingerprinting
├── data/
│   ├── enterprise/                       # Enterprise Synthetic Evaluation Dataset
│   │   ├── incidents/                    # Production incident reports (INC-2024-891)
│   │   ├── policies/                     # IT escalation matrix and SLAs
│   │   ├── runbooks/                     # Recovery runbooks (RB-PAY-04)
│   │   ├── services/                     # Service architecture specs (payment, auth)
│   │   └── teams/                        # Engineering on-call rosters and team directories
│   └── falkordb/                         # Local FalkorDB persistent volume (dump.rdb)
├── docs/                                 # Project Documentation & Architecture
│   ├── API_SPECIFICATION.md              # REST API endpoint reference
│   ├── ARCHITECTURE.md                   # System architecture and Cypher data models
│   ├── DATABASE_OPERATIONS.md            # FalkorDB operations and schema maintenance
│   ├── END_TO_END_WORKFLOW.md            # Ingestion and querying lifecycle walk-throughs
│   ├── EVALUATION_REPORT.md              # 8-scenario benchmark quantitative metrics
│   ├── FEATURE_STATUS.md                 # Implementation status matrix
│   ├── FRONTEND_UI_AUDIT.md              # Design tokens, WCAG AA compliance, layout fixes
│   ├── HACKATHON_ACTION_PLAN.md          # Hackathon milestone delivery plan
│   ├── HACKATHON_ALIGNMENT_REPORT.md     # Hackathon track alignment and judging criteria audit
│   ├── HACKATHON_REQUIREMENTS.md         # Track 03 requirements breakdown
│   ├── JUDGE_PERSPECTIVE_REVIEW.md       # Review and pitch walkthrough from judges' POV
│   ├── PROJECT_EXPLAINED.md              # Plain-English technical explanation
│   ├── PROJECT_OVERVIEW.md               # High-level product summary
│   ├── REPOSITORY_AUDIT.md               # Complete repository audit and health assessment
│   ├── TECHNICAL_ARCHITECTURE.md         # Component deep-dive with Mermaid diagrams
│   ├── TECHNICAL_RISKS.md                # Risk register and mitigation strategies
│   ├── TEST_PLAN.md                      # Test strategy and scenario definitions
│   └── assets/screenshots/               # Real UI showcase screenshots
│       ├── chat-evidence-panel.png       # Verifiable citation drawer screenshot
│       ├── documents-manager.png         # Document dropzone and management screenshot
│       ├── graph-explorer.png            # Interactive FalkorDB canvas screenshot
│       └── workspace-chat.png            # Main chat workspace interface screenshot
├── frontend/                             # Single Page Web Dashboard
│   ├── app.js                            # UI controller, HiDPI canvas renderer, toasts
│   ├── index.html                        # Semantic HTML5 layout with ARIA accessibility
│   └── style.css                         # CSS design system, responsive flexbox layout
├── graphrag_sdk/                         # Bundled FalkorDB GraphRAG SDK
│   ├── attribute.py, entity.py, ...      # Core SDK classes
│   ├── kg.py, ontology.py, relation.py   # SDK KnowledgeGraph & Schema management
│   ├── helpers.py                        # Cypher validation, JSON extraction
│   ├── agents/, models/, steps/          # Agent and model abstractions
│   └── orchestrator/                     # Multi-step plan orchestrator
├── tests/                                # Automated Test Suite (42 Tests)
│   ├── evaluation/
│   │   └── test_benchmark_evaluation.py  # 8 Quantitative benchmark scenarios
│   ├── integration/
│   │   └── test_pipeline_and_api.py      # 10 API & database lifecycle tests
│   ├── unit/
│   │   └── test_validation_and_chunking.py# 8 Ingestion and verification unit tests
│   ├── test_helper_validate_cypher.py    # 12 SDK Cypher validation tests
│   └── test_kg.py                        # 4 SDK KnowledgeGraph tests
├── IMPLEMENTATION_PLAN.md                # Master milestone delivery checklist
├── README.md                             # Production-grade GitHub repository documentation
├── ingest.py                             # CLI document ingestion runner (--force flag support)
├── pyproject.toml                        # Poetry project specification & test options
├── requirements.txt                      # Pip requirements lockfile
└── run.py                                # Server entrypoint runner (Uvicorn launcher)
```

---

## 4. Dependency Analysis & Discrepancies

### 4.1 `requirements.txt` vs `pyproject.toml`
The application runs reliably using `pip install -r requirements.txt`. All 13 dependencies in `requirements.txt` are directly imported:
- `falkordb>=1.7.1`
- `fastapi>=0.115.0`
- `uvicorn>=0.30.0`
- `pydantic>=2.8.0`
- `python-dotenv>=1.0.1`
- `pypdf>=5.0.0`
- `beautifulsoup4>=4.12.0`
- `openai>=1.35.0`
- `google-generativeai>=0.8.0`
- `backoff>=2.2.1`
- `fix-busted-json>=0.0.19`
- `pytest>=8.2.0`
- `httpx>=0.27.0`

### 4.2 Discrepancies in `pyproject.toml`
In `pyproject.toml`, which is used by `.github/workflows/test.yml` during `poetry install`:
1. **Missing Critical Runtime Packages:** `fastapi`, `uvicorn`, `pydantic`, and `httpx` were not listed under `[tool.poetry.dependencies]`. In an automated CI environment running `poetry install`, importing `fastapi` would fail.
2. **Unused Packages:**
   - `python-abc = "^0.2.0"`: An obsolete empty package from 2018 with zero code references.
   - `vertexai = "^1.49.0"`: A heavy Google Cloud SDK (>100MB) that is not imported or used anywhere in the codebase (Google Gemini is integrated via `google-generativeai`).
   - `ipykernel = "^6.29.5"`: Jupyter kernel package placed in main dependencies rather than `dev`.
3. **Recommendation:** Synchronize `pyproject.toml` with `requirements.txt` by adding `fastapi`, `uvicorn`, `pydantic`, `httpx`, and removing `python-abc` and `vertexai`.

---

## 5. Configuration & Environment Security

1. **`.env` vs `.env.example`:**
   - `.env` contains local configuration and is properly ignored by Git.
   - `.env.example` contains safe, clean placeholders with no real credentials.
   - When API keys (`OPENAI_API_KEY`, `GOOGLE_API_KEY`) are absent, Company Brain automatically activates its built-in Deterministic Local Grounded Engine, ensuring zero-cost, zero-risk operation.
2. **Secret Leak Scan:**
   - Automated regex scanning confirmed zero exposed API keys (`sk-...`, `AIza...`) or private keys across all tracked files.
3. **Persistent Data Isolation:**
   - The FalkorDB data volume `data/falkordb/dump.rdb` is stored locally and excluded from Git tracking via `.gitignore`.

---

## 6. CI/CD Workflow Audit

1. **`.github/workflows/test.yml`:**
   - Provisions FalkorDB and Ollama services via Docker containers.
   - Executes `poetry install` and `poetry run pytest`.
   - Requires `fastapi`, `uvicorn`, `pydantic`, and `httpx` in `pyproject.toml` to pass successfully.
2. **`.github/workflows/spellcheck.yml`:**
   - Uses `rojopolis/spellcheck-github-actions@0.33.1` with `config_path: .spellcheck.yml`.
   - **Identified Defect:** `.spellcheck.yml` was missing from the repository root. This causes the spellcheck GitHub Action to fail when triggered on PR or push.
   - **Resolution:** Supply a clean `.spellcheck.yml` configuration configured to check documentation with appropriate technical dictionaries.

---

## 7. Recommended Cleanup & Optimization Actions

1. **Refine `.gitignore`:** Expand with standard Python, OS, IDE, and test artifacts (`*.py[cod]`, `.coverage`, `dist/`, `.vscode/`, `.idea/`, `Thumbs.db`, `.DS_Store`). Explicitly whitelist `!.env.example`.
2. **Update `pyproject.toml`:** Add `fastapi`, `uvicorn`, `pydantic`, `httpx`; remove unused `python-abc` and `vertexai`.
3. **Add `.spellcheck.yml`:** Add the missing configuration file so the existing GitHub Action workflow executes cleanly.
4. **Preserve All Core Source Files:** All files in `app/`, `frontend/`, `data/enterprise/`, `tests/`, and `graphrag_sdk/` are verified active and essential.
