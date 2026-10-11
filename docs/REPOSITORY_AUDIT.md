# Repository Audit Report: FalkorDB GraphRAG-SDK (Track 03 — Enterprise RAG)

**Date:** 2026-10-12  
**Target Solution:** Company Brain — Enterprise Knowledge Intelligence Assistant  
**Auditor:** Senior Software Architect & GraphRAG Technical Lead  

---

## 1. Executive Summary

This repository is a clone of the **FalkorDB GraphRAG-SDK-v2** (`graphrag_sdk` version `0.1.2-beta`), designed as an SDK for constructing and querying Knowledge Graphs using FalkorDB as the graph storage engine and OpenAI / Google Gemini as generative models.

The current codebase is in an early beta state with critical import-order bugs, missing dependency installations, and incomplete public API exports that prevent original tests from running out of the box. Furthermore, while the SDK provides rudimentary graph extraction and Cypher query generation, it lacks enterprise document chunking, source passage traceability, citation generation, abstention logic, backend APIs, and user interfaces required for **Track 03: Company Brain (Enterprise RAG)**.

---

## 2. Repository & Environment Status

| Dimension | Current State | Notes |
| :--- | :--- | :--- |
| **Project Root** | `c:\Users\LENOVO\Downloads\GraphRAG-SDK-v2-master` | Confirmed local project workspace |
| **Git Branch** | `main` | Clean working tree |
| **Latest Commit** | `e93ae49 Initial commit` | Fresh commit containing all project files; previous remote history reset |
| **Remote Repository** | `https://github.com/rajat552/FalkorDB.git` | Synced with GitHub `origin/main` |
| **Python Version** | `Python 3.13.1` (Windows 64-bit) | Modern Python runtime |
| **Package Manager** | `pip 26.2.1` | Upgraded from 26.1.2; Poetry is not installed on system PATH |
| **Docker Status** | Operational | Docker daemon running |
| **FalkorDB Container** | `falkordb/falkordb:latest` (ID `8178bd676684`, name `beautiful_shamir`) | Active on `0.0.0.0:6379` (Redis protocol) & `0.0.0.0:3000` (FalkorDB Studio UI) |
| **Database Connectivity** | Verified (`RETURN 1 AS test` passed) | Direct TCP connection on `127.0.0.1:6379` via `falkordb` Python client |
| **Environment Variables** | Blank template in `.env.example` | `OPENAI_API_KEY` and `GOOGLE_API_KEY` currently unpopulated |

---

## 3. Architecture & Dependency Manifest Inspection

### 3.1 Dependency Manifest (`pyproject.toml`)
The repository specifies:
- `python = "^3.11.4"`
- `falkordb = "^1.0.4"`
- `typing-extensions = "^4.12.1"`
- `bs4 = "^0.0.2"`
- `pypdf = "^4.2.0"`
- `vertexai = "^1.49.0"`
- `backoff = "^2.2.1"`
- `ratelimit = "^2.2.1"`
- `python-dotenv = "^1.0.1"`
- `openai = "^1.35.9"`
- `fix-busted-json = "^0.0.18"`
- `ollama = "^0.2.1"`
- `google-generativeai = "^0.8.1"`
- `pytest = "^8.2.1"`

### 3.2 Installation Challenges & Resolution in Python 3.13
- **Dependency Installation:** The workspace initially lacked installed dependencies in the global Python environment.
- **`ratelimit` Wheel Issue:** `ratelimit 2.2.1` distributes only source tarballs (`.tar.gz`). On Python 3.13 under Windows, standard `pip` triggers a regression in `tarfile.py` (`AttributeError: module 'ntpath' has no attribute 'ALLOW_MISSING'`). 
- **Resolution:** `ratelimit` was extracted and built into a wheel using a custom extraction filter, enabling full installation alongside `falkordb 1.7.1`, `openai 3.29.0`, `google-generativeai 0.8.6`, `pypdf 6.20.0`, `beautifulsoup4 4.15.0`, `fix-busted-json 0.0.19`, and `backoff 2.2.1`.

---

## 4. Codebase Analysis: SDK Structure & Public APIs

### 4.1 Structure
```
graphrag_sdk/
├── __init__.py                # Incomplete exports & broken import order
├── kg.py                      # KnowledgeGraph class (connects to FalkorDB)
├── ontology.py                # Ontology schema definition
├── entity.py                  # Entity schema definition
├── relation.py                # Relation schema definition
├── attribute.py               # Attribute & AttributeType definitions
├── source.py                  # AbstractSource, Source factory (PDF, HTML, TEXT, URL, CSV, JSONL)
├── document.py                # Document container
├── model_config.py            # KnowledgeGraphModelConfig
├── helpers.py                 # Cypher validation, json repair, string formatters
├── agents/
│   └── kg_agent.py            # KGAgent definition
├── orchestrator/
│   ├── orchestrator.py        # Multi-agent orchestrator
│   ├── orchestrator_runner.py # Execution loop
│   ├── execution_plan.py      # Plan generator
│   └── step.py                # Plan steps
├── document_loaders/          # Loaders for CSV, HTML, JSONL, PDF, Text, URL
├── fixtures/                  # Prompts (GRAPH_QA, CYPHER_GEN, EXTRACT_DATA)
├── models/                    # GenerativeModel abstractions: OpenAI, Gemini, Ollama
└── steps/
    ├── extract_data_step.py   # Extract entities & relations via LLM
    ├── graph_query_step.py    # LLM Cypher generation & query execution
    └── qa_step.py             # QA synthesis using graph context
```

### 4.2 Critical Bug Identified: Circular Import & Broken `__init__.py`
When running `pytest` or importing `graphrag_sdk`:
```text
File "graphrag_sdk\helpers.py", line 81, in <module>
    cypher: str, ontology: graphrag_sdk.Ontology
AttributeError: module 'graphrag_sdk' has no attribute 'Ontology'
```
**Root Cause:**
1. `graphrag_sdk/__init__.py` imports `from .orchestrator import Orchestrator`, which imports `orchestrator_runner.py`, which imports `from graphrag_sdk.helpers import extract_json`.
2. `helpers.py` at line 81 defines `validate_cypher(cypher: str, ontology: graphrag_sdk.Ontology)` where type annotation is evaluated immediately during module loading.
3. At that moment, `graphrag_sdk` has not yet finished loading and does not export `Ontology`.
4. Furthermore, `graphrag_sdk/__init__.py` completely omitted `KnowledgeGraph`, `Ontology`, `Entity`, `Relation`, `Source`, and `KnowledgeGraphModelConfig` from its exports, even though all tests and documentation rely on them.

---

## 5. Functional Assessment against Track 03 (Company Brain)

| Feature Required by Track 03 | Native SDK Support | Gap Analysis |
| :--- | :--- | :--- |
| **Enterprise Document Ingestion** | Basic single-file loaders (PDF, TXT, HTML, CSV) | No chunk ID generation, no content hash deduplication, no file validation, no metadata indexing. |
| **Evidence & Chunk Storage** | None | Entities are extracted directly to graph nodes; no `Document` or `EvidenceChunk` nodes or relationships (`CONTAINS`, `DOCUMENTED_IN`) are stored. |
| **Domain Ontology** | Generic entity/relation schemas | Needs enterprise IT helpdesk ontology: `Employee`, `Team`, `Service`, `Incident`, `Document`, `EvidenceChunk` linked via `MEMBER_OF`, `OWNS`, `AFFECTED_BY`, `RESOLVED_BY`, `DOCUMENTED_IN`, `CONTAINS`. |
| **Multi-Hop Cypher Generation** | Basic single-prompt Cypher generation | Prone to syntax hallucinations on complex multi-hop joins; lacks enterprise question templates. |
| **Citations & Passage Grounding** | None | Original `kg.ask()` returns only `(answer_text, chat_session)`. No source filenames, chunk IDs, or verified passages returned. |
| **Abstention & Insufficient Evidence** | Weak string fallback | Needs deterministic evidence threshold checks and structured JSON responses (`insufficient_evidence: true`). |
| **Backend API** | None | No REST API endpoints exist. |
| **Frontend UI** | None | No UI exists (only Jupyter notebook demos). |

---

## 6. Known Limitations & Blockers

1. **Missing External API Keys:** Neither `OPENAI_API_KEY` nor `GOOGLE_API_KEY` is currently set in the environment. A dual-mode model architecture is needed: live LLM when keys are present, and a deterministic local mock engine for testing and automated evaluation.
2. **Import Bug:** `graphrag_sdk/__init__.py` and `helpers.py` must be normalized to enable clean imports across tests and application modules.
3. **No Incremental / Cascade Deletion:** In the original SDK, deleting sources does not remove orphaned entities or edges from the graph.

---

## 7. Next Steps: Phase 2 Action Plan

1. Create `IMPLEMENTATION_PLAN.md` with phased milestones and acceptance criteria.
2. Create `docs/ARCHITECTURE.md` detailing the dual-layer GraphRAG engine (FalkorDB + Evidence Store).
3. Create `docs/API_SPECIFICATION.md` defining REST endpoints for documents, chat, sources, and graph exploration.
4. Create `docs/TEST_PLAN.md` defining unit, integration, and end-to-end evaluation suites.
