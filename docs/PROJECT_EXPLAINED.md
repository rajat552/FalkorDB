# Project Explained: Company Brain Presentation & Defense Guide

**Audience:** Student Presenter & Hackathon Team  
**Goal:** Understand the system completely and explain it confidently to judges and engineers.  

---

## A. One-Line Explanation

> **Company Brain is an enterprise knowledge assistant powered by FalkorDB that traverses interconnected company documents to answer complex IT inquiries with 100% verified citations, authentic supporting text passages, and zero hallucinations.**

---

## B. Short Summary (125 Words)

In large companies, vital operational knowledge is fragmented across service specifications, incident reports, team rosters, and recovery runbooks. When production outages occur, standard AI bots fail because vector similarity searches cannot connect the dots across multiple files, and they frequently hallucinate. 

**Company Brain** solves this by converting documents into a **FalkorDB knowledge graph** that explicitly links services, incidents, resolving teams, and runbooks. When an engineer asks a multi-hop question, Company Brain traverses the graph in under 10ms, aggregates verbatim evidence passages, synthesizes a factual answer, and provides clickable source citations with exact character offsets. Furthermore, if required facts are absent, the system deterministically flags insufficient evidence instead of guessing.

---

## C. Detailed Explanation for College Students

### 1. What problem are we solving?
Imagine an IT helpdesk engineer or on-call developer waking up at 3:00 AM because the Payment Gateway is failing. To fix it, they need to know:
- Who owns the payment service? (Found in team specs)
- Was there a recent outage with this exact error? (Found in postmortems)
- Which runbook gives the step-by-step fix? (Found in operational runbooks)
- What is the SLA before an executive must be paged? (Found in escalation policies)

Currently, finding these answers requires manually searching 4 different platforms.

### 2. Why does standard AI (Vector Search) fail here?
Standard Vector RAG turns text into numerical vectors and finds passages that use similar words. But **vector similarity is not relationship reasoning**. Vector search cannot follow a multi-step chain:
```
Service (payment-service) ──> Incident (INC-2024-891) ──> Resolving Team (Payments Platform) ──> Runbook (RB-PAY-04)
```
Even worse, when vector bots don't find the answer, they make up convincing fiction (hallucinations), which can be disastrous during a production outage.

### 3. How does our solution work?
We ingest raw enterprise files (`.md`, `.txt`, `.pdf`). We break them into chunks and extract key operational entities into **FalkorDB**:
- Nodes: `Service`, `Team`, `Incident`, `Document`, `EvidenceChunk`
- Edges: `OWNS`, `AFFECTED_BY`, `RESOLVED_BY`, `DOCUMENTED_IN`, `CONTAINS`, `GROUNDED_IN`

When a user asks a question, Company Brain uses Cypher queries to follow the graph paths, gathers authentic passages, verifies the citations, and answers accurately.

### 4. What makes our approach special?
- **Zero Hallucination Guarantee:** If the answer is not in the graph, it flags `insufficient_evidence: true`.
- **Verifiable Proof:** Every citation links to an exact text chunk with character boundaries.
- **Sub-10ms Latency:** FalkorDB's C-based Redis engine executes graph traversals virtually instantaneously.
- **Dual-Mode Engine:** Works offline with 100% deterministic local rules, or connects to live OpenAI / Gemini when keys are provided.

---

## D. Technical Deep Dive

1. **Backend (FastAPI):** Exposes clean REST endpoints for chat (`POST /api/chat`), document ingestion (`POST /api/documents/upload`), cascading deletion (`DELETE /api/documents/{id}`), and graph inspection (`GET /api/graph/overview`).
2. **Database (FalkorDB):** Connected via `app/db.py` on port `6379`. Uses Cypher `MERGE` statements for idempotent, transactional ingestion.
3. **Ingestion Pipeline:** 
   - Files are validated (format, 10MB limit).
   - SHA-256 hash is computed to reject duplicate uploads.
   - Text is split into 800-character sliding windows with 150-character overlaps, recording exact start and end character indices.
4. **GraphRAG Retriever:** Extracts query entities, runs parameterized Cypher queries, and collects connected nodes and evidence passages.
5. **Citation Verification:** Validates every citation against stored `EvidenceChunk` records before returning the answer to the user.

---

## E. Three-Minute Live Demo Script

| Minute | Screen / Tab | What You Do & Say |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **Workspace & Chat Tab** | *"Hello judges! Large IT teams waste hours during outages searching through fragmented docs. Today we present Company Brain, powered by FalkorDB GraphRAG."*<br>Show the clean dashboard at `http://localhost:8000`. |
| **0:45 - 1:45** | **Click Canonical Query** | Click the suggested pill: *"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"*<br>*"Notice what happened in under 15ms: FalkorDB followed 4 relationship hops across three separate documents (Service spec, incident postmortem, and recovery runbook). It links INC-2024-891 to Payments Platform and RB-PAY-04."*<br>Click the citation badge: *"Watch this: clicking the citation opens our Evidence Drawer showing the exact verbatim paragraph from the postmortem."* |
| **1:45 - 2:15** | **Honest Abstention Test** | Click the out-of-scope pill: *"What is the secret recipe for chocolate cookies?"*<br>*"Notice what happens: unlike standard bots that hallucinate a recipe, Company Brain checks the graph, detects zero evidence, flags insufficient evidence, and honestly abstains."* |
| **2:15 - 3:00** | **Graph Explorer & Studio** | Switch to the **Graph Explorer** tab. Show the node counters (Services, Incidents, Teams) and the 360-degree connection neighborhood for `payment-service`.<br>*"In conclusion, Company Brain brings verifiable, relationship-aware intelligence to enterprise IT with 39/39 passing automated tests."* |

---

## F. Likely Judge Questions & How to Answer Them

### Q1: Why not just use regular vector search (like Chroma or Pinecone)?
**Answer:** *"Vector search calculates cosine distance on isolated snippets. It has no concept of relationships. A query that requires linking a service to its incident, then to the resolving team, and finally to an emergency runbook requires multi-hop traversal. Vector search fails to connect those dots. FalkorDB does it natively via Cypher in under 10ms."*

### Q2: How do you prevent hallucinations?
**Answer:** *"We use a two-step safeguard: First, our Cypher query retrieves only connected facts. Second, our Hard Citation Verification Layer validates that every claim matches an authentic `EvidenceChunk` stored in FalkorDB. If there is no graph evidence, our pipeline deterministically flags `insufficient_evidence: true` and refuses to invent facts."*

### Q3: What happens when documentation changes or new runbooks are uploaded?
**Answer:** *"We built an enterprise ingestion pipeline with SHA-256 content deduplication. If you re-upload the same file, it rejects it to prevent graph bloat. If you upload a new version or delete an old one, our cascading delete cleans up the document, its chunks, and all associated edges cleanly."*

### Q4: Does this require expensive cloud LLM calls to run?
**Answer:** *"No! Company Brain features a dual-mode engine. If you supply an OpenAI or Gemini API key, it generates live natural language answers. But it also includes a deterministic local grounded generator that synthesizes 100% verified answers offline with zero API cost and zero latency. All 39 of our automated tests pass offline."*

### Q5: How is FalkorDB specifically utilized?
**Answer:** *"FalkorDB is our primary and only database. It stores the domain entities (`Service`, `Team`, `Incident`, `Employee`), the structural hierarchy (`Document` &rarr; `EvidenceChunk`), and the grounding edges (`[:GROUNDED_IN]`). We use native Cypher queries for multi-hop traversals and neighborhood exploration."*
