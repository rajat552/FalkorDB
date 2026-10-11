from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.db import check_health, get_graph, init_schema
from app.ingestion.pipeline import (
    ingest_file,
    list_documents,
    get_document_details,
    delete_document,
    ingest_enterprise_dataset,
    DuplicateDocumentError,
    DocumentValidationError,
)
from app.engine.pipeline import query_company_brain

# Setup application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("company_brain")

app = FastAPI(
    title="Company Brain API",
    description="Enterprise Knowledge Intelligence Assistant with GraphRAG and Verifiable Citations",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup hook
@app.on_event("startup")
def on_startup():
    try:
        init_schema()
        logger.info("FalkorDB graph schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not initialize schema on startup: {e}")


# --- Models ---
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language IT helpdesk query")
    top_k: Optional[int] = Field(5, ge=1, le=20)


class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict[str, Any]]
    graph_context: Dict[str, Any]
    insufficient_evidence: bool


# --- Endpoints ---

@app.get("/health", summary="Health check and FalkorDB diagnostics")
def health_endpoint():
    db_health = check_health()
    return {
        "status": "healthy" if db_health["connected"] else "degraded",
        "database": db_health,
        "model": {
            "openai_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "gemini_configured": bool(os.environ.get("GOOGLE_API_KEY")),
            "active_mode": "live" if (os.environ.get("OPENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY")) else "deterministic_local",
        },
        "version": "1.0.0",
    }


@app.post("/api/documents/upload", status_code=status.HTTP_201_CREATED, summary="Upload and ingest a document")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        res = ingest_file(filename=file.filename or "unknown.txt", content=content)
        return res
    except DuplicateDocumentError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_DOCUMENT",
                "message": str(e),
                "existing_document_id": e.existing_document_id,
            },
        )
    except DocumentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "VALIDATION_FAILED", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INGESTION_ERROR", "message": str(e)},
        )


@app.get("/api/documents", summary="List all ingested documents")
def get_documents():
    docs = list_documents()
    return {"documents": docs, "total": len(docs)}


@app.get("/api/documents/{document_id}", summary="Get document details and evidence chunks")
def get_document(document_id: str):
    doc = get_document_details(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return doc


@app.delete("/api/documents/{document_id}", summary="Delete document and associated chunks")
def remove_document(document_id: str):
    res = delete_document(document_id)
    if res.get("status") == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return res


@app.post("/api/documents/reindex", summary="Re-index synthetic enterprise dataset")
def reindex_dataset():
    try:
        results = ingest_enterprise_dataset()
        return {"status": "reindexed", "ingested_count": len(results), "documents": results}
    except Exception as e:
        logger.error(f"Reindexing error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@app.post("/api/chat", response_model=ChatResponse, summary="Query the knowledge graph with verifiable citations")
def chat_endpoint(request: ChatRequest):
    try:
        res = query_company_brain(request.query)
        return res
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "QUERY_ERROR", "message": str(e)},
        )


@app.get("/api/sources/{source_id}", summary="Get source evidence chunk by ID")
def get_source(source_id: str):
    graph = get_graph()
    safe_id = source_id.replace("'", "\\'")
    res = graph.query(
        f"MATCH (c:EvidenceChunk {{id: '{safe_id}'}}) "
        f"OPTIONAL MATCH (d:Document {{id: c.document_id}}) "
        f"RETURN c.id, c.document_id, d.filename, d.title, c.text, c.start_char, c.end_char"
    ).result_set

    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source chunk not found.")

    r = res[0]
    return {
        "chunk_id": r[0],
        "document_id": r[1],
        "filename": r[2],
        "document_title": r[3],
        "text": r[4],
        "start_char": r[5],
        "end_char": r[6],
    }


@app.get("/api/graph/overview", summary="Knowledge graph summary metrics")
def get_graph_overview():
    graph = get_graph()
    try:
        nodes_res = graph.query("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC").result_set
        node_counts = {r[0]: r[1] for r in nodes_res if r[0]}

        edges_res = graph.query("MATCH ()-[r]->() RETURN type(r) AS rel, count(r) AS count ORDER BY count DESC").result_set
        edge_counts = {r[0]: r[1] for r in edges_res if r[0]}

        return {
            "node_counts": node_counts,
            "edge_counts": edge_counts,
            "total_nodes": sum(node_counts.values()),
            "total_edges": sum(edge_counts.values()),
        }
    except Exception as e:
        logger.error(f"Graph overview error: {e}")
        return {"node_counts": {}, "edge_counts": {}, "total_nodes": 0, "total_edges": 0, "error": str(e)}


@app.get("/api/graph/related", summary="Get entity neighborhood")
def get_related(
    entity_name: str = Query(..., description="Name or ID of entity to explore"),
    entity_label: Optional[str] = Query(None, description="Optional label filter"),
):
    graph = get_graph()
    safe_name = entity_name.replace("'", "\\'")
    
    label_clause = f":{entity_label}" if entity_label else ""
    q = f"""
    MATCH (n{label_clause}) WHERE n.name = '{safe_name}' OR n.id = '{safe_name}' OR n.title = '{safe_name}'
    OPTIONAL MATCH (n)-[r]->(target)
    OPTIONAL MATCH (source)-[r_in]->(n)
    RETURN labels(n)[0] AS center_label,
           coalesce(n.name, n.id, n.title) AS center_name,
           type(r) AS outgoing_rel,
           labels(target)[0] AS target_label,
           coalesce(target.name, target.id, target.title) AS target_name,
           type(r_in) AS incoming_rel,
           labels(source)[0] AS source_label,
           coalesce(source.name, source.id, source.title) AS source_name
    LIMIT 25
    """
    try:
        res = graph.query(q).result_set
        if not res:
            return {"center": {"name": entity_name}, "connections": []}

        connections = []
        center_label = res[0][0]
        center_name = res[0][1]

        for r in res:
            _, _, out_rel, tgt_lbl, tgt_name, in_rel, src_lbl, src_name = r
            if out_rel and tgt_name:
                connections.append({
                    "direction": "outgoing",
                    "relationship": out_rel,
                    "target_label": tgt_lbl,
                    "target_name": tgt_name,
                })
            if in_rel and src_name:
                connections.append({
                    "direction": "incoming",
                    "relationship": in_rel,
                    "source_label": src_lbl,
                    "source_name": src_name,
                })

        return {
            "center": {"label": center_label, "name": center_name},
            "connections": connections,
        }
    except Exception as e:
        logger.error(f"Related graph query failed: {e}")
        return {"center": {"name": entity_name}, "connections": [], "error": str(e)}


# Mount static frontend directory if present
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
