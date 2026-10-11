# Company Brain REST API Specification

**Base URL:** `http://localhost:8000`  
**Protocol:** HTTP/1.1  
**Format:** JSON (`application/json`) / Multipart Form (`multipart/form-data`)  

---

## 1. System & Health

### `GET /health`
Returns health status of the API, FalkorDB connection, graph metrics, and model configuration.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "host": "127.0.0.1",
    "port": 6379,
    "graph_name": "company_brain",
    "total_nodes": 42,
    "total_edges": 68
  },
  "model": {
    "provider": "openai",
    "model_name": "gpt-4o",
    "mode": "live"
  },
  "version": "1.0.0"
}
```

---

## 2. Document Management

### `POST /api/documents/upload`
Uploads and ingests a single enterprise document (Markdown, Text, or PDF).

#### Request
- **Content-Type:** `multipart/form-data`
- **Body:** `file` (binary)

#### Response `201 Created`
```json
{
  "document_id": "doc-8f3a921",
  "filename": "incidents/INC-2024-891-payment-timeout.md",
  "file_type": "text/markdown",
  "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "total_chunks": 3,
  "entities_extracted": 6,
  "relationships_extracted": 8,
  "status": "ingested",
  "message": "Document processed and graph constructed successfully."
}
```

#### Response `409 Conflict` (Duplicate Upload)
```json
{
  "error": "DUPLICATE_DOCUMENT",
  "message": "A document with identical content has already been ingested.",
  "existing_document_id": "doc-8f3a921"
}
```

---

### `GET /api/documents`
Lists all ingested documents with metadata and ingestion timestamp.

#### Response `200 OK`
```json
{
  "documents": [
    {
      "id": "doc-8f3a921",
      "filename": "incidents/INC-2024-891-payment-timeout.md",
      "file_type": "text/markdown",
      "title": "Postmortem: INC-2024-891 Payment Gateway Timeout",
      "chunk_count": 3,
      "uploaded_at": "2026-10-12T01:30:00Z"
    }
  ],
  "total": 1
}
```

---

### `GET /api/documents/{document_id}`
Returns details and chunks of a specific document.

#### Response `200 OK`
```json
{
  "id": "doc-8f3a921",
  "filename": "incidents/INC-2024-891-payment-timeout.md",
  "title": "Postmortem: INC-2024-891 Payment Gateway Timeout",
  "content_hash": "e3b0c442...",
  "uploaded_at": "2026-10-12T01:30:00Z",
  "chunks": [
    {
      "chunk_id": "chunk-doc-8f3a921-0",
      "index": 0,
      "text": "Incident INC-2024-891 occurred on October 10...",
      "char_count": 480
    }
  ]
}
```

---

### `DELETE /api/documents/{document_id}`
Safely removes a document, its associated chunks, and isolates orphaned references.

#### Response `200 OK`
```json
{
  "status": "deleted",
  "document_id": "doc-8f3a921",
  "removed_chunks": 3
}
```

---

## 3. Query & Enterprise RAG

### `POST /api/chat`
Answers an enterprise IT helpdesk query with verified citations and graph traversals.

#### Request Body
```json
{
  "query": "Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?",
  "top_k": 5
}
```

#### Response `200 OK` (Evidence Found)
```json
{
  "query": "Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?",
  "answer": "The latest incident on payment-service (INC-2024-891) was resolved by the Payments Platform team. The root cause was a connection pool starvation in the database adapter under high retry volume. The mitigation is documented in runbook RB-PAY-04 (Payment Gateway Recovery & Pool Reset).",
  "citations": [
    {
      "document_id": "doc-inc-891",
      "filename": "INC-2024-891-payment-timeout.md",
      "chunk_id": "chunk-inc-891-1",
      "passage": "Incident INC-2024-891 was resolved by the Payments Platform team. Root cause was identified as connection pool exhaustion under sudden traffic spikes."
    },
    {
      "document_id": "doc-rb-pay-04",
      "filename": "RB-PAY-04-payment-recovery.md",
      "chunk_id": "chunk-rb-pay-04-0",
      "passage": "Runbook RB-PAY-04 documents the procedure to reset connection pool quotas and drain uncommitted transactions during gateway degradation."
    }
  ],
  "graph_context": {
    "entities": [
      {"id": "service-payment", "label": "Service", "name": "payment-service"},
      {"id": "inc-891", "label": "Incident", "title": "INC-2024-891"},
      {"id": "team-payments", "label": "Team", "name": "Payments Platform"},
      {"id": "rb-pay-04", "label": "Document", "title": "RB-PAY-04"}
    ],
    "relationships": [
      {"from": "payment-service", "type": "AFFECTED_BY", "to": "INC-2024-891"},
      {"from": "INC-2024-891", "type": "RESOLVED_BY", "to": "Payments Platform"},
      {"from": "INC-2024-891", "type": "DOCUMENTED_IN", "to": "RB-PAY-04"}
    ]
  },
  "insufficient_evidence": false
}
```

#### Response `200 OK` (Insufficient Evidence / Honest Abstention)
```json
{
  "query": "What is the secret Wi-Fi password for the Tokyo branch office?",
  "answer": "I do not have sufficient information in the ingested documentation or knowledge graph to answer this inquiry.",
  "citations": [],
  "graph_context": {
    "entities": [],
    "relationships": []
  },
  "insufficient_evidence": true
}
```

---

## 4. Knowledge Graph Exploration

### `GET /api/graph/overview`
Returns summary metrics and top entities in the knowledge graph.

#### Response `200 OK`
```json
{
  "node_counts": {
    "Service": 4,
    "Team": 3,
    "Incident": 3,
    "Employee": 8,
    "Document": 6,
    "EvidenceChunk": 18
  },
  "edge_counts": {
    "OWNS": 4,
    "MEMBER_OF": 8,
    "AFFECTED_BY": 3,
    "RESOLVED_BY": 3,
    "DOCUMENTED_IN": 3,
    "CONTAINS": 18
  }
}
```

---

### `GET /api/graph/related`
Returns nodes and edges directly connected to an entity.

#### Query Parameters
- `entity_label`: e.g. `Service`
- `entity_name`: e.g. `payment-service`

#### Response `200 OK`
```json
{
  "center": {"label": "Service", "name": "payment-service"},
  "connected_nodes": [
    {"label": "Team", "name": "Payments Platform", "relationship": "OWNED_BY"},
    {"label": "Incident", "name": "INC-2024-891", "relationship": "AFFECTED_BY"}
  ]
}
```
