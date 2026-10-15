from __future__ import annotations
import time
import logging
from typing import Any, Dict, List, Optional
import falkordb
from app.config import (
    FALKORDB_HOST,
    FALKORDB_PORT,
    FALKORDB_USERNAME,
    FALKORDB_PASSWORD,
    FALKORDB_GRAPH,
)

logger = logging.getLogger(__name__)


def get_db_client() -> falkordb.FalkorDB:
    """Connect to FalkorDB instance using configured credentials."""
    kwargs: Dict[str, Any] = {
        "host": FALKORDB_HOST,
        "port": FALKORDB_PORT,
    }
    if FALKORDB_USERNAME:
        kwargs["username"] = FALKORDB_USERNAME
    if FALKORDB_PASSWORD:
        kwargs["password"] = FALKORDB_PASSWORD
    return falkordb.FalkorDB(**kwargs)


def get_graph(graph_name: Optional[str] = None) -> falkordb.Graph:
    """Select the active FalkorDB graph."""
    db = get_db_client()
    return db.select_graph(graph_name or FALKORDB_GRAPH)


def check_health() -> Dict[str, Any]:
    """Execute diagnostics and return database connection metrics."""
    start_time = time.time()
    try:
        db = get_db_client()
        graph = db.select_graph(FALKORDB_GRAPH)
        
        # Test basic cypher execution
        result = graph.query("RETURN 1 AS ping")
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        # Collect node and edge metrics
        node_res = graph.query("MATCH (n) RETURN count(n) AS node_count")
        node_count = node_res.result_set[0][0] if node_res.result_set else 0

        edge_res = graph.query("MATCH ()-[r]->() RETURN count(r) AS edge_count")
        edge_count = edge_res.result_set[0][0] if edge_res.result_set else 0

        return {
            "connected": True,
            "host": FALKORDB_HOST,
            "port": FALKORDB_PORT,
            "graph_name": FALKORDB_GRAPH,
            "latency_ms": latency_ms,
            "total_nodes": node_count,
            "total_edges": edge_count,
            "error": None,
        }
    except Exception as exc:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"FalkorDB health check failed: {exc}")
        return {
            "connected": False,
            "host": FALKORDB_HOST,
            "port": FALKORDB_PORT,
            "graph_name": FALKORDB_GRAPH,
            "latency_ms": latency_ms,
            "total_nodes": 0,
            "total_edges": 0,
            "error": str(exc),
        }


def init_schema(graph_name: Optional[str] = None) -> Dict[str, Any]:
    """Create indices for fast entity and evidence retrieval."""
    graph = get_graph(graph_name)
    indices = [
        "CREATE INDEX FOR (s:Service) ON (s.name)",
        "CREATE INDEX FOR (i:Incident) ON (i.id)",
        "CREATE INDEX FOR (t:Team) ON (t.name)",
        "CREATE INDEX FOR (d:Document) ON (d.id)",
        "CREATE INDEX FOR (c:EvidenceChunk) ON (c.id)",
        "CREATE INDEX FOR (e:Employee) ON (e.id)",
    ]
    created = []
    for q in indices:
        try:
            graph.query(q)
            created.append(q)
        except Exception as e:
            # Index might already exist, which is safe to ignore
            logger.debug(f"Index creation note for '{q}': {e}")
    return {"status": "initialized", "indices": created}
