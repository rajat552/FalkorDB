from __future__ import annotations
import datetime
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.db import get_graph
from app.config import ENTERPRISE_DATA_DIR
from app.ingestion.validator import validate_file, compute_content_hash, DocumentValidationError
from app.ingestion.chunker import chunk_document, EvidenceChunkData
from app.ingestion.entity_extractor import extract_entities_from_text, ExtractedEntities

logger = logging.getLogger(__name__)


class DuplicateDocumentError(Exception):
    def __init__(self, message: str, existing_document_id: str):
        super().__init__(message)
        self.existing_document_id = existing_document_id


def ingest_file(
    filename: str,
    content: bytes,
    graph_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validate, chunk, extract knowledge, and transactionally store an enterprise document.
    """
    cleaned_filename, text = validate_file(filename, content)
    content_hash = compute_content_hash(content)
    graph = get_graph(graph_name)

    # 1. Check for duplicate upload via content hash
    check_q = f"MATCH (d:Document {{content_hash: '{content_hash}'}}) RETURN d.id AS id, d.filename AS filename LIMIT 1"
    existing = graph.query(check_q).result_set
    if existing:
        existing_id = existing[0][0]
        raise DuplicateDocumentError(
            f"A document with identical content has already been ingested ({existing[0][1]}).",
            existing_document_id=existing_id,
        )

    # 2. Derive document metadata
    doc_id = f"doc-{content_hash[:12]}"
    
    # Extract title from first markdown header or filename
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else cleaned_filename
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 3. Create document chunks
    chunks = chunk_document(document_id=doc_id, text=text)

    # 4. Extract entities and relationships
    extracted = extract_entities_from_text(text=text, filename=cleaned_filename, document_id=doc_id)

    # 5. Insert Document node
    safe_title = title.replace("'", "\\'")
    safe_filename = cleaned_filename.replace("'", "\\'")
    graph.query(
        f"MERGE (d:Document {{id: '{doc_id}'}}) "
        f"SET d.filename = '{safe_filename}', d.title = '{safe_title}', "
        f"d.content_hash = '{content_hash}', d.uploaded_at = '{now_iso}', "
        f"d.chunk_count = {len(chunks)}"
    )

    # 6. Insert EvidenceChunk nodes and link to Document
    for c in chunks:
        # Escape single quotes and backslashes for Cypher
        safe_chunk_text = c.text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        graph.query(
            f"MERGE (c:EvidenceChunk {{id: '{c.chunk_id}'}}) "
            f"SET c.document_id = '{doc_id}', c.index = {c.index}, "
            f"c.text = '{safe_chunk_text}', c.start_char = {c.start_char}, "
            f"c.end_char = {c.end_char}, c.char_count = {c.char_count}"
        )
        graph.query(
            f"MATCH (d:Document {{id: '{doc_id}'}}), (c:EvidenceChunk {{id: '{c.chunk_id}'}}) "
            f"MERGE (d)-[:CONTAINS {{order: {c.index}}}]->(c)"
        )

    first_chunk_id = chunks[0].chunk_id if chunks else None

    # 7. Insert extracted Services
    for srv in extracted.services:
        s_name = srv["name"].replace("'", "\\'")
        graph.query(
            f"MERGE (s:Service {{name: '{s_name}'}}) "
            f"SET s.id = '{srv['id']}', s.tier = '{srv['tier']}', s.status = '{srv['status']}'"
        )
        if first_chunk_id:
            graph.query(
                f"MATCH (s:Service {{name: '{s_name}'}}), (c:EvidenceChunk {{id: '{first_chunk_id}'}}) "
                f"MERGE (s)-[:GROUNDED_IN]->(c)"
            )

    # 8. Insert extracted Teams
    for t in extracted.teams:
        t_name = t["name"].replace("'", "\\'")
        t_lead = t["lead"].replace("'", "\\'")
        graph.query(
            f"MERGE (team:Team {{name: '{t_name}'}}) "
            f"SET team.id = '{t['id']}', team.lead = '{t_lead}'"
        )

    # 9. Insert extracted Incidents
    for inc in extracted.incidents:
        inc_id = inc["id"]
        safe_inc_title = inc["title"].replace("'", "\\'")
        safe_cause = inc["root_cause"].replace("'", "\\'")
        safe_commander = inc.get("commander", "").replace("'", "\\'")
        graph.query(
            f"MERGE (i:Incident {{id: '{inc_id}'}}) "
            f"SET i.title = '{safe_inc_title}', i.severity = '{inc['severity']}', "
            f"i.root_cause = '{safe_cause}', i.status = '{inc['status']}', "
            f"i.commander = '{safe_commander}', i.document_id = '{doc_id}'"
        )
        # Link incident to document
        graph.query(
            f"MATCH (i:Incident {{id: '{inc_id}'}}), (d:Document {{id: '{doc_id}'}}) "
            f"MERGE (i)-[:DOCUMENTED_IN]->(d)"
        )
        if first_chunk_id:
            graph.query(
                f"MATCH (i:Incident {{id: '{inc_id}'}}), (c:EvidenceChunk {{id: '{first_chunk_id}'}}) "
                f"MERGE (i)-[:GROUNDED_IN]->(c)"
            )

    # 10. Insert extracted Employees
    for emp in extracted.employees:
        emp_name = emp["name"].replace("'", "\\'")
        emp_email = emp["email"].replace("'", "\\'")
        graph.query(
            f"MERGE (e:Employee {{name: '{emp_name}'}}) "
            f"SET e.id = '{emp['id']}', e.email = '{emp_email}', e.role = '{emp['role']}'"
        )

    # 11. Insert extracted explicit Relationships
    for rel in extracted.relationships:
        f_lbl = rel["from_label"]
        f_key = rel["from_key"]
        f_val = str(rel["from_id"]).replace("'", "\\'")
        t_lbl = rel["to_label"]
        t_key = rel["to_key"]
        t_val = str(rel["to_id"]).replace("'", "\\'")
        r_type = rel["rel_type"]

        q = (
            f"MATCH (a:{f_lbl} {{{f_key}: '{f_val}'}}), (b:{t_lbl} {{{t_key}: '{t_val}'}}) "
            f"MERGE (a)-[:{r_type}]->(b)"
        )
        try:
            graph.query(q)
        except Exception as e:
            logger.debug(f"Failed to create relationship: {e}")

    # 12. Cross-link Incidents to referenced Runbook Documents
    for inc in extracted.incidents:
        inc_id = inc["id"]
        rb_matches = re.findall(r"\b(RB-[A-Z]+-\d{2,3})\b", text)
        for rb_code in rb_matches:
            link_q = (
                f"MATCH (i:Incident {{id: '{inc_id}'}}), (rb:Document) "
                f"WHERE rb.filename CONTAINS '{rb_code}' OR rb.title CONTAINS '{rb_code}' "
                f"MERGE (i)-[:DOCUMENTED_IN]->(rb)"
            )
            try:
                graph.query(link_q)
            except Exception as e:
                logger.debug(f"Failed to link incident to runbook: {e}")

    # If this document is itself a runbook, link to any incidents referencing it
    rb_self = re.search(r"\b(RB-[A-Z]+-\d{2,3})\b", cleaned_filename + " " + title)
    if rb_self:
        rb_code = rb_self.group(1)
        link_back = (
            f"MATCH (i:Incident), (c:EvidenceChunk), (rb:Document {{id: '{doc_id}'}}) "
            f"WHERE c.document_id = i.document_id AND c.text CONTAINS '{rb_code}' "
            f"MERGE (i)-[:DOCUMENTED_IN]->(rb)"
        )
        try:
            graph.query(link_back)
        except Exception as e:
            pass

    return {
        "document_id": doc_id,
        "filename": cleaned_filename,
        "title": title,
        "content_hash": content_hash,
        "total_chunks": len(chunks),
        "entities_extracted": len(extracted.services) + len(extracted.teams) + len(extracted.incidents),
        "relationships_extracted": len(extracted.relationships),
        "status": "ingested",
    }


def list_documents(graph_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve list of all ingested documents in FalkorDB."""
    graph = get_graph(graph_name)
    query = (
        "MATCH (d:Document) "
        "OPTIONAL MATCH (d)-[:CONTAINS]->(c:EvidenceChunk) "
        "RETURN d.id, d.filename, d.title, d.uploaded_at, d.content_hash, count(c) AS chunk_count "
        "ORDER BY d.uploaded_at DESC"
    )
    result = graph.query(query).result_set
    docs = []
    for r in result:
        docs.append({
            "id": r[0],
            "filename": r[1],
            "title": r[2],
            "uploaded_at": r[3],
            "content_hash": r[4],
            "chunk_count": r[5],
        })
    return docs


def get_document_details(document_id: str, graph_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get detailed document record and ordered chunks."""
    graph = get_graph(graph_name)
    doc_res = graph.query(f"MATCH (d:Document {{id: '{document_id}'}}) RETURN d.id, d.filename, d.title, d.uploaded_at, d.content_hash").result_set
    if not doc_res:
        return None
    
    r = doc_res[0]
    doc = {
        "id": r[0],
        "filename": r[1],
        "title": r[2],
        "uploaded_at": r[3],
        "content_hash": r[4],
        "chunks": [],
    }

    chunks_res = graph.query(
        f"MATCH (d:Document {{id: '{document_id}'}})-[:CONTAINS]->(c:EvidenceChunk) "
        f"RETURN c.id, c.index, c.text, c.start_char, c.end_char, c.char_count "
        f"ORDER BY c.index ASC"
    ).result_set

    for cr in chunks_res:
        doc["chunks"].append({
            "chunk_id": cr[0],
            "index": cr[1],
            "text": cr[2],
            "start_char": cr[3],
            "end_char": cr[4],
            "char_count": cr[5],
        })
    return doc


def delete_document(document_id: str, graph_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely delete a document, its chunks, and associated edges from FalkorDB.
    """
    graph = get_graph(graph_name)
    # Check if document exists
    check = graph.query(f"MATCH (d:Document {{id: '{document_id}'}}) RETURN count(d)").result_set
    if not check or check[0][0] == 0:
        return {"status": "not_found", "document_id": document_id, "deleted_chunks": 0}

    # Count and delete chunks
    del_chunks = graph.query(
        f"MATCH (d:Document {{id: '{document_id}'}})-[:CONTAINS]->(c:EvidenceChunk) "
        f"DETACH DELETE c"
    )

    # Detach delete document node
    graph.query(f"MATCH (d:Document {{id: '{document_id}'}}) DETACH DELETE d")

    return {
        "status": "deleted",
        "document_id": document_id,
    }


def ingest_enterprise_dataset(graph_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Ingest all synthetic enterprise documents from data/enterprise/ directory."""
    results = []
    if not ENTERPRISE_DATA_DIR.exists():
        logger.warning(f"Enterprise data directory {ENTERPRISE_DATA_DIR} does not exist.")
        return results

    for root, _, files in os.walk(ENTERPRISE_DATA_DIR):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in [".md", ".txt"]:
                with open(file_path, "rb") as f:
                    content = f.read()
                try:
                    rel_name = file_path.relative_to(ENTERPRISE_DATA_DIR).as_posix()
                    res = ingest_file(filename=rel_name, content=content, graph_name=graph_name)
                    results.append(res)
                except DuplicateDocumentError:
                    logger.info(f"Skipping already ingested document: {file}")
                except Exception as e:
                    logger.error(f"Error ingesting {file}: {e}")
                    raise e
    return results
