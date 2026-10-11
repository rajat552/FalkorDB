# Company Brain Architecture: Enterprise GraphRAG Intelligence

**Track 03:** Company Brain / Enterprise RAG  
**System:** FalkorDB GraphRAG-SDK Enterprise Assistant  

---

## 1. High-Level System Architecture

Company Brain combines a graph database engine (**FalkorDB**) with an evidence-grounded retrieval pipeline to answer IT helpdesk questions with verifiable cross-document citations.

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

## 2. Knowledge Graph Schema & Domain Ontology

To support multi-document reasoning for internal IT inquiries, the schema represents physical operational entities alongside source documents and verifiable passages.

### 2.1 Entity Types (`Labels`)

| Label | Key Properties | Description |
| :--- | :--- | :--- |
| `Employee` | `id`, `name`, `email`, `role` | Engineering and operations staff |
| `Team` | `id`, `name`, `lead`, `slack_channel` | Engineering or support squads |
| `Service` | `id`, `name`, `tier`, `repository`, `status` | Software services, APIs, databases |
| `Incident` | `id`, `title`, `severity`, `root_cause`, `status`, `timestamp` | Production alerts and postmortems |
| `Document` | `id`, `filename`, `file_type`, `content_hash`, `title`, `uploaded_at` | Ingested source files |
| `EvidenceChunk` | `id`, `document_id`, `chunk_index`, `text`, `start_char`, `end_char` | Exact textual passages for citations |

### 2.2 Relationship Types (`Edges`)

| Relationship | Source Label | Target Label | Properties | Description |
| :--- | :--- | :--- | :--- | :--- |
| `MEMBER_OF` | `Employee` | `Team` | `role` | Staff membership in teams |
| `OWNS` | `Team` | `Service` | `ownership_type` | Team responsible for a service |
| `AFFECTED_BY` | `Service` | `Incident` | `impact_level` | Service outage or degradation |
| `RESOLVED_BY` | `Incident` | `Team` | `resolved_at` | Team that mitigated the incident |
| `DOCUMENTED_IN` | `Incident` | `Document` | `section` | Incident postmortem or runbook link |
| `COVERS` | `Document` | `Service` | `doc_type` | Service specification or architecture |
| `CONTAINS` | `Document` | `EvidenceChunk` | `order` | Structural link to source passage |
| `GROUNDED_IN` | `Incident` / `Service` | `EvidenceChunk` | `confidence` | Direct traceability from entity to passage |

---

## 3. Data Flow Pipelines

### 3.1 Document Ingestion Flow
1. **Upload:** User submits file (PDF, Markdown, TXT) via `/api/documents/upload`.
2. **Validation:** Checks MIME type, size limit (10MB), and computes SHA-256 content hash.
3. **Deduplication:** Rejects or skips duplicate uploads based on content hash.
4. **Chunking:** Parses content into overlapping chunks (typically 500-1000 characters) preserving character offsets.
5. **Entity & Relation Extraction:** Extracts structured enterprise entities and cross-references.
6. **Atomic Graph Insertion:** Uses Cypher `MERGE` transactions in FalkorDB to create:
   - `Document` node.
   - `EvidenceChunk` nodes connected via `[:CONTAINS]`.
   - Domain nodes (`Service`, `Team`, `Incident`) connected to `EvidenceChunk` via `[:GROUNDED_IN]`.

### 3.2 Query & Grounded Retrieval Flow
1. **Query Input:** User asks: *"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"*
2. **Entity & Intent Recognition:** Matches query targets (`Payment Service`, `Incident`, `Team`, `Runbook`).
3. **Graph Traversal (FalkorDB Cypher):**
   ```cypher
   MATCH (s:Service {name: 'payment-service'})<-[:AFFECTED_BY]-(i:Incident)
   OPTIONAL MATCH (i)-[:RESOLVED_BY]->(t:Team)
   OPTIONAL MATCH (i)-[:DOCUMENTED_IN]->(d:Document)
   OPTIONAL MATCH (d)-[:CONTAINS]->(c:EvidenceChunk)
   RETURN s, i, t, d, c
   ORDER BY i.timestamp DESC LIMIT 1
   ```
4. **Evidence Aggregation:** Collects candidate nodes and exact `EvidenceChunk` passages.
5. **Grounded Synthesis:** The generation engine synthesizes a concise, factual answer referencing only verified facts.
6. **Hard Citation Validation:** Validates that every citation in the response matches an actual chunk in FalkorDB.
7. **Abstention Decision:** If no matching nodes or evidence chunks exist, returns `insufficient_evidence: true` with a clear explanation instead of hallucinating.

---

## 4. Dual-Mode LLM Generation Architecture

To ensure demo reliability regardless of external cloud API availability:
1. **Live Cloud Mode:** When `OPENAI_API_KEY` or `GOOGLE_API_KEY` is present, queries `gpt-4o` or `gemini-1.5-flash` using strict system instructions requiring citations.
2. **Deterministic Local Mode:** When external API keys are not supplied, a rule-grounded generator extracts facts directly from retrieved Cypher records and chunks, producing 100% verified answers and citations with zero network dependencies.

---

## 5. Security & Isolation Controls

- **API Secrets Protection:** Secrets loaded via `.env`; never logged, staged, or sent to frontend.
- **Input Sanitization:** Cypher parameterization prevents Cypher injection.
- **Upload Restrictions:** Restricts uploaded files to `.md`, `.txt`, `.pdf`, `.json` with strict size limits.
- **Public API Isolation:** No unrestricted database administration commands exposed over REST.
