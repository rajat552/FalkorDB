# Project Overview & Repository Audit: Company Brain

**Project Name:** Company Brain — Enterprise Knowledge Intelligence  
**Hackathon Track:** Track 03 (Company Brain)  
**Target Environment:** Python 3.11–3.13, FalkorDB, FastAPI, Vanilla Web Dashboard  

---

## 1. Project Overview (In Plain English)

### What is Company Brain?
Imagine joining a company as an IT helpdesk engineer or Site Reliability Engineer (SRE). When a major service like the Payment Gateway goes down at 2:00 AM, the answers you need are scattered across five different places:
- Architecture specs in Notion or Google Docs
- Incident postmortems in Jira or Markdown
- Remediation procedures in emergency runbooks
- Team rosters and Slack channels in an internal wiki

If you ask a normal AI bot (like a standard ChatGPT vector search wrapper), it will find random text paragraphs based on similar keywords. But it **cannot connect the dots**: it doesn't know that **Team A** owns **Service B**, which suffered **Incident C**, which must be resolved using **Runbook D**. Worst of all, traditional bots often make up convincing lies (hallucinations) when they don't know the answer.

**Company Brain solves this.** It takes company documents, parses their operational entities into **FalkorDB** as a knowledge graph, and answers complex cross-document IT inquiries with **100% verified citations, authentic text passages, and zero hallucinations**.

---

## 2. Who is Supposed to Use It?

1. **IT Helpdesk & Operations Engineers:** Looking up incident escalation rules, on-call leads, and SLA policies.
2. **Site Reliability Engineers (SREs):** Finding root causes of past outages and step-by-step recovery commands from verified runbooks.
3. **Engineering Leads & Product Managers:** Understanding service dependencies, ownership matrices, and cross-team blast radiuses.

---

## 3. Technology Stack Breakdown

| Technology | Where It Is Used | Why It Is Needed | Role in the System |
| :--- | :--- | :--- | :--- |
| **FalkorDB (v1.7+)** | Graph Database engine (Port `6379`) | **Mandatory by hackathon.** Provides blazing-fast Cypher graph queries and relationship modeling. | Stores `Service`, `Team`, `Incident`, `Document`, and `EvidenceChunk` nodes and their interconnected edges. |
| **Python 3.11–3.13** | Core backend language | High performance, rich ecosystem for data parsing and graph query construction. | Executes ingestion, chunking, retrieval logic, and API endpoints. |
| **FastAPI (v0.115+)** | REST API Backend (`app/main.py`) | Lightweight, high-throughput asynchronous web framework with automatic OpenAPI documentation. | Serves `/api/chat`, `/api/documents`, `/api/graph/overview`, `/health`, and static frontend files. |
| **Uvicorn (v0.30+)** | ASGI Web Server (`run.py`) | Production-ready HTTP server for FastAPI applications. | Runs the local backend on port `8000`. |
| **Vanilla HTML5 / CSS3 / ES6** | Web Dashboard (`frontend/`) | Zero-dependency, instantaneous rendering without complex npm build pipelines or bundle bloat. | Delivers a warm, responsive dark/light dashboard with Chat, Document Management, and Graph Explorer. |
| **GraphRAG SDK** | Internal SDK module (`graphrag_sdk/`) | Structured graph modeling framework for FalkorDB. | Defines entities, attributes, relations, and Cypher query helpers. |
| **PyPDF & BeautifulSoup4** | Document Parsing (`app/ingestion/`) | Document extraction libraries. | Converts raw PDF, text, and Markdown files into plain text streams. |
| **Dual-Mode LLM Generator** | Generation Engine (`app/engine/generator.py`) | Generates natural language answers. Connects to OpenAI (`gpt-4o`) or Gemini (`gemini-1.5-flash`) when keys exist. | Includes a deterministic rule-grounded generator for zero-cost, offline, reproducible testing. |
| **Pytest (v8.2+)** | Automated Test Suite (`tests/`) | Testing framework for unit, integration, and quantitative benchmarks. | Runs 39 automated tests verifying 100% correctness across the pipeline. |
| **Docker** | Containerization | Runs FalkorDB and FalkorDB Studio. | Exposes database port `6379` and visual graph studio port `3000`. |

---

## 4. Annotated File and Directory Structure

```
Company Brain/
├── app/                                 # Main Backend Application Package
│   ├── config.py                        # Centralized environment variable loader (.env)
│   ├── db.py                            # FalkorDB client, health diagnostics, index initialization
│   ├── main.py                          # FastAPI server, route controllers, static UI mount
│   ├── ontology.py                      # Enterprise IT ontology (Employee, Team, Service, Incident)
│   ├── engine/                          # GraphRAG Retrieval and Generation Engine
│   │   ├── citations.py                 # Verifies citations against raw FalkorDB chunk text
│   │   ├── generator.py                 # Synthesizes answers (Live cloud LLM or local deterministic)
│   │   ├── pipeline.py                  # End-to-end question answering pipeline coordinator
│   │   └── retriever.py                 # Cypher multi-hop graph traversal and passage collector
│   └── ingestion/                       # Multi-Document Ingestion Pipeline
│       ├── chunker.py                   # Sliding-window character chunker with offset preservation
│       ├── entity_extractor.py          # Extracts enterprise entities (Services, Incidents, Teams)
│       ├── pipeline.py                  # Ingestion orchestrator with SHA-256 deduplication
│       └── validator.py                 # Validates file format, MIME type, and size limits
│
├── data/                                # Data Storage & Datasets
│   ├── enterprise/                      # Realistic synthetic enterprise IT documentation
│   │   ├── incidents/                   # INC-2024-891 postmortems (Payment Gateway timeout)
│   │   ├── policies/                    # IT incident escalation matrix and SLAs
│   │   ├── runbooks/                    # RB-PAY-04 payment connection pool recovery runbook
│   │   ├── services/                    # Service architecture specs (payment-service, auth-service)
│   │   └── teams/                       # Team rosters (Payments Platform, Security Core)
│   └── falkordb/                        # Mounted volume for persistent FalkorDB database storage
│
├── docs/                                # Project Specifications & Audit Reports
│   ├── API_SPECIFICATION.md             # REST API endpoint schemas and examples
│   ├── ARCHITECTURE.md                  # System architecture, schemas, and Cypher flows
│   ├── DATABASE_OPERATIONS.md           # FalkorDB maintenance recipes
│   ├── EVALUATION_REPORT.md             # 8-scenario quantitative benchmark report
│   ├── HACKATHON_REQUIREMENTS.md        # Official challenge rules and track analysis
│   ├── PROJECT_OVERVIEW.md              # This document: Plain English overview & tech stack
│   ├── REPOSITORY_AUDIT.md              # Initial code audit findings
│   └── TEST_PLAN.md                     # Test strategy, coverage, and scenarios
│
├── frontend/                            # Single-Page Web Dashboard (Zero build tools needed)
│   ├── app.js                           # UI logic, chat handler, tab switching, Graph Explorer
│   ├── index.html                       # Semantic HTML5 dashboard with luxury brand footer
│   └── style.css                        # PawSpa warm luxury color palette and responsive layout
│
├── graphrag_sdk/                        # Core GraphRAG SDK module
│   ├── ontology.py                      # Schema ontology builder
│   ├── entity.py                        # Graph entity class
│   ├── relation.py                      # Graph relation class
│   ├── attribute.py                     # Attribute definitions and types
│   └── helpers.py                       # Cypher query validation utilities
│
├── tests/                               # Comprehensive Automated Test Suite (39 Tests)
│   ├── evaluation/                      # 8 benchmark scenarios (EVAL-01 to EVAL-08)
│   ├── integration/                     # FastAPI endpoint lifecycle and database tests
│   ├── unit/                            # Chunker, validator, and citation unit tests
│   ├── test_helper_validate_cypher.py   # Cypher syntax and direction tests
│   └── test_kg.py                       # Knowledge graph node/edge creation tests
│
├── .env.example                         # Template for environment configuration
├── ingest.py                            # Standalone script to index enterprise dataset
├── pyproject.toml                       # Project metadata and pytest configuration
├── requirements.txt                     # Production Python dependencies
├── run.py                               # Server launcher (runs app.main:app on port 8000)
└── README.md                            # Comprehensive user and judge guide
```
