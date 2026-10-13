from __future__ import annotations
import logging
import re
from typing import Dict, Any, List, Optional, Set, Tuple

from app.db import get_graph

logger = logging.getLogger(__name__)


class RetrievedEvidence:
    def __init__(self):
        self.entities: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
        self.raw_facts: List[str] = []

    def is_empty(self) -> bool:
        return len(self.entities) == 0 and len(self.chunks) == 0


def retrieve_graph_evidence(query: str, graph_name: Optional[str] = None) -> RetrievedEvidence:
    """
    Perform relationship-aware graph traversal and evidence chunk retrieval for a user question.
    """
    graph = get_graph(graph_name)
    evidence = RetrievedEvidence()
    q_lower = query.lower()

    # Typo tolerance & keyword normalization
    q_normalized = q_lower
    typo_map = {
        "paymrnt": "payment",
        "paymnt": "payment",
        "paymnet": "payment",
        "pament": "payment",
        "aut": "auth",
        "authen": "auth",
        "secuirty": "security",
        "ordr": "order",
        "notif": "notification",
        "membr": "member",
        "membrs": "members",
    }
    for typo, correction in typo_map.items():
        q_normalized = re.sub(rf"\b{typo}\b", correction, q_normalized)

    # 1. Identify query entity keywords
    known_services = ["payment-service", "auth-service", "order-processing-service", "notification-hub"]
    matched_services = [s for s in known_services if s in q_normalized or s.split("-")[0] in q_normalized]

    matched_incidents = re.findall(r"\b(INC-\d{4}-\d+)\b", query, re.IGNORECASE)
    matched_runbooks = re.findall(r"\b(RB-[A-Z]+-\d{2,3})\b", query, re.IGNORECASE)

    # 2. Multi-hop Service Outage & Incident Traversal
    for srv in matched_services:
        cypher = f"""
        MATCH (s:Service {{name: '{srv}'}})
        OPTIONAL MATCH (team:Team)-[:OWNS]->(s)
        OPTIONAL MATCH (s)-[:AFFECTED_BY]->(i:Incident)
        OPTIONAL MATCH (i)-[:RESOLVED_BY]->(res_team:Team)
        OPTIONAL MATCH (i)-[:DOCUMENTED_IN]->(d:Document)
        OPTIONAL MATCH (d)-[:CONTAINS]->(c:EvidenceChunk)
        RETURN s.name, team.name, team.lead, i.id, i.title, i.root_cause, res_team.name, d.id, d.filename, d.title, c.id, c.text
        LIMIT 10
        """
        try:
            res = graph.query(cypher).result_set
            for row in res:
                s_name, t_name, t_lead, inc_id, inc_title, inc_cause, r_team, doc_id, doc_fn, doc_t, c_id, c_text = row
                
                if s_name:
                    evidence.entities.append({"label": "Service", "name": s_name})
                if t_name:
                    evidence.entities.append({"label": "Team", "name": t_name, "lead": t_lead})
                    evidence.relationships.append({"from": t_name, "type": "OWNS", "to": s_name})
                    evidence.raw_facts.append(f"Service '{s_name}' is owned by team '{t_name}' (Lead: {t_lead}).")
                if inc_id:
                    evidence.entities.append({"label": "Incident", "id": inc_id, "title": inc_title, "root_cause": inc_cause})
                    evidence.relationships.append({"from": s_name, "type": "AFFECTED_BY", "to": inc_id})
                    evidence.raw_facts.append(f"Incident '{inc_id}' affected '{s_name}': cause was '{inc_cause}'.")
                if r_team and inc_id:
                    evidence.entities.append({"label": "Team", "name": r_team})
                    evidence.relationships.append({"from": inc_id, "type": "RESOLVED_BY", "to": r_team})
                    evidence.raw_facts.append(f"Incident '{inc_id}' was resolved by team '{r_team}'.")
                if doc_id and doc_fn:
                    evidence.entities.append({"label": "Document", "id": doc_id, "filename": doc_fn, "title": doc_t})
                    if inc_id:
                        evidence.relationships.append({"from": inc_id, "type": "DOCUMENTED_IN", "to": doc_fn})
                if c_id and c_text:
                    evidence.chunks.append({
                        "chunk_id": c_id,
                        "document_id": doc_id,
                        "filename": doc_fn,
                        "text": c_text,
                    })
        except Exception as e:
            logger.debug(f"Service graph traversal failed: {e}")

    # 3. Direct Incident Traversal
    for inc_id in matched_incidents:
        cypher = f"""
        MATCH (i:Incident {{id: '{inc_id.upper()}'}})
        OPTIONAL MATCH (s:Service)-[:AFFECTED_BY]->(i)
        OPTIONAL MATCH (i)-[:RESOLVED_BY]->(t:Team)
        OPTIONAL MATCH (i)-[:DOCUMENTED_IN]->(d:Document)
        OPTIONAL MATCH (d)-[:CONTAINS]->(c:EvidenceChunk)
        RETURN i.id, i.title, i.root_cause, s.name, t.name, d.id, d.filename, c.id, c.text
        LIMIT 10
        """
        try:
            res = graph.query(cypher).result_set
            for row in res:
                i_id, i_title, i_cause, s_name, t_name, d_id, d_fn, c_id, c_text = row
                evidence.entities.append({"label": "Incident", "id": i_id, "title": i_title, "root_cause": i_cause})
                if s_name:
                    evidence.entities.append({"label": "Service", "name": s_name})
                    evidence.relationships.append({"from": s_name, "type": "AFFECTED_BY", "to": i_id})
                if t_name:
                    evidence.entities.append({"label": "Team", "name": t_name})
                    evidence.relationships.append({"from": i_id, "type": "RESOLVED_BY", "to": t_name})
                    evidence.raw_facts.append(f"Incident '{i_id}' was resolved by '{t_name}'.")
                if d_fn:
                    evidence.relationships.append({"from": i_id, "type": "DOCUMENTED_IN", "to": d_fn})
                if c_id and c_text:
                    evidence.chunks.append({
                        "chunk_id": c_id,
                        "document_id": d_id,
                        "filename": d_fn,
                        "text": c_text,
                    })
        except Exception as e:
            logger.debug(f"Incident graph traversal failed: {e}")

    # 4. Direct Runbook Traversal
    for rb_code in matched_runbooks:
        cypher = f"""
        MATCH (d:Document) WHERE d.filename CONTAINS '{rb_code.upper()}' OR d.title CONTAINS '{rb_code.upper()}'
        MATCH (d)-[:CONTAINS]->(c:EvidenceChunk)
        OPTIONAL MATCH (i:Incident)-[:DOCUMENTED_IN]->(d)
        RETURN d.id, d.filename, d.title, c.id, c.text, i.id
        LIMIT 5
        """
        try:
            res = graph.query(cypher).result_set
            for row in res:
                d_id, d_fn, d_t, c_id, c_text, i_id = row
                evidence.entities.append({"label": "Document", "id": d_id, "filename": d_fn, "title": d_t})
                if i_id:
                    evidence.relationships.append({"from": i_id, "type": "DOCUMENTED_IN", "to": d_fn})
                if c_id and c_text:
                    evidence.chunks.append({
                        "chunk_id": c_id,
                        "document_id": d_id,
                        "filename": d_fn,
                        "text": c_text,
                    })
        except Exception as e:
            logger.debug(f"Runbook traversal failed: {e}")

    # 5. Team Ownership / Lead / On-call Traversal
    if any(k in q_normalized for k in ["team", "lead", "owns", "ownership", "roster", "who owns", "member", "members", "staff"]):
        cypher = """
        MATCH (t:Team)-[:OWNS]->(s:Service)
        RETURN t.name, t.lead, s.name
        """
        try:
            for row in graph.query(cypher).result_set:
                t_name, t_lead, s_name = row
                if s_name in q_normalized or not matched_services:
                    evidence.entities.append({"label": "Team", "name": t_name, "lead": t_lead})
                    evidence.entities.append({"label": "Service", "name": s_name})
                    evidence.relationships.append({"from": t_name, "type": "OWNS", "to": s_name})
                    evidence.raw_facts.append(f"Team '{t_name}' (Lead: {t_lead}) owns '{s_name}'.")
        except Exception as e:
            logger.debug(f"Team ownership query failed: {e}")

    # 5b. Team Members & Employee Directory Traversal
    if any(k in q_normalized for k in ["member", "members", "staff", "who works", "who is on", "people", "engineer", "directory"]):
        target_team_filter = ""
        if "payment" in q_normalized:
            target_team_filter = "WHERE t.name CONTAINS 'Payment'"
        elif "security" in q_normalized or "auth" in q_normalized:
            target_team_filter = "WHERE t.name CONTAINS 'Security'"
        elif "order" in q_normalized:
            target_team_filter = "WHERE t.name CONTAINS 'Order'"

        cypher_emp = f"""
        MATCH (e:Employee)-[:MEMBER_OF]->(t:Team)
        {target_team_filter}
        RETURN e.name, e.email, e.role, t.name
        """
        try:
            for row in graph.query(cypher_emp).result_set:
                e_name, e_email, e_role, t_name = row
                clean_email = e_email.strip("`")
                evidence.entities.append({"label": "Employee", "name": e_name, "email": clean_email, "role": e_role})
                evidence.entities.append({"label": "Team", "name": t_name})
                evidence.relationships.append({"from": e_name, "type": "MEMBER_OF", "to": t_name})
                evidence.raw_facts.append(f"{e_name} ({clean_email}) is a member of '{t_name}'.")
        except Exception as e:
            logger.debug(f"Employee membership query failed: {e}")

        # Also link evidence chunk from team-ownership-roster.md
        roster_q = """
        MATCH (d:Document) WHERE d.filename CONTAINS 'roster' OR d.filename CONTAINS 'team'
        MATCH (d)-[:CONTAINS]->(c:EvidenceChunk)
        RETURN d.id, d.filename, d.title, c.id, c.text
        LIMIT 3
        """
        try:
            for row in graph.query(roster_q).result_set:
                d_id, d_fn, d_t, c_id, c_text = row
                evidence.entities.append({"label": "Document", "id": d_id, "filename": d_fn, "title": d_t})
                evidence.chunks.append({
                    "chunk_id": c_id,
                    "document_id": d_id,
                    "filename": d_fn,
                    "text": c_text,
                })
        except Exception as e:
            pass

    # 6. Policy & SLA Traversal
    if any(k in q_lower for k in ["sla", "policy", "escalat", "response target", "severity"]):
        cypher = """
        MATCH (d:Document) WHERE d.filename CONTAINS 'policy' OR d.filename CONTAINS 'escalation'
        MATCH (d)-[:CONTAINS]->(c:EvidenceChunk)
        RETURN d.id, d.filename, d.title, c.id, c.text
        LIMIT 3
        """
        try:
            for row in graph.query(cypher).result_set:
                d_id, d_fn, d_t, c_id, c_text = row
                evidence.entities.append({"label": "Document", "id": d_id, "filename": d_fn, "title": d_t})
                evidence.chunks.append({
                    "chunk_id": c_id,
                    "document_id": d_id,
                    "filename": d_fn,
                    "text": c_text,
                })
        except Exception as e:
            logger.debug(f"Policy query failed: {e}")

    # 7. Fallback Keyword Match on EvidenceChunks if chunks set is empty
    if len(evidence.chunks) == 0:
        tokens = [w for w in re.findall(r"[a-zA-Z0-9_-]{3,}", query) if w.lower() not in {"what", "which", "where", "when", "does", "the", "and", "for", "with"}]
        for token in tokens[:4]:
            q_token = token.replace("'", "\\'")
            cypher = f"""
            MATCH (d:Document)-[:CONTAINS]->(c:EvidenceChunk)
            WHERE c.text CONTAINS '{q_token}'
            RETURN d.id, d.filename, d.title, c.id, c.text
            LIMIT 3
            """
            try:
                for row in graph.query(cypher).result_set:
                    d_id, d_fn, d_t, c_id, c_text = row
                    evidence.chunks.append({
                        "chunk_id": c_id,
                        "document_id": d_id,
                        "filename": d_fn,
                        "text": c_text,
                    })
                    evidence.entities.append({"label": "Document", "id": d_id, "filename": d_fn})
            except Exception as e:
                pass

    # Deduplicate entities & chunks
    unique_entities = []
    seen_e = set()
    for e in evidence.entities:
        key = (e.get("label"), e.get("name") or e.get("id") or e.get("filename"))
        if key not in seen_e:
            seen_e.add(key)
            unique_entities.append(e)
    evidence.entities = unique_entities

    unique_chunks = []
    seen_c = set()
    for c in evidence.chunks:
        if c["chunk_id"] not in seen_c:
            seen_c.add(c["chunk_id"])
            unique_chunks.append(c)
    evidence.chunks = unique_chunks

    return evidence
