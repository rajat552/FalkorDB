from __future__ import annotations
import re
from typing import List, Dict, Any, Optional


class ExtractedEntities:
    def __init__(self):
        self.services: List[Dict[str, Any]] = []
        self.teams: List[Dict[str, Any]] = []
        self.incidents: List[Dict[str, Any]] = []
        self.employees: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []


def extract_entities_from_text(
    text: str, filename: str, document_id: str
) -> ExtractedEntities:
    """
    Extract enterprise IT domain entities and relationships from document text.
    Handles service specs, incident postmortems, runbooks, and team directories.
    """
    data = ExtractedEntities()

    # 1. Detect Incident (e.g., INC-2024-891)
    inc_match = re.search(r"\b(INC-\d{4}-\d+)\b", text, re.IGNORECASE)
    if inc_match:
        inc_id = inc_match.group(1).upper()
        
        # Extract title
        title_match = re.search(r"Title[:\s]+([^\n]+)", text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else f"Incident {inc_id}"
        
        # Extract severity
        sev_match = re.search(r"Severity[:\s]+(Sev-[1-4])", text, re.IGNORECASE)
        severity = sev_match.group(1) if sev_match else "Sev-1"
        
        # Extract root cause
        root_match = re.search(r"Root Cause[^:\n]*[:\n]+([^\n\.]+\.)", text, re.IGNORECASE)
        root_cause = root_match.group(1).strip() if root_match else "Under investigation"

        cmd_match = re.search(r"Incident Commander[:\s*]+([A-Z][a-z]+ [A-Z][a-z]+)", text, re.IGNORECASE)
        commander = cmd_match.group(1).strip() if cmd_match else ""

        data.incidents.append({
            "id": inc_id,
            "title": title,
            "severity": severity,
            "root_cause": root_cause,
            "status": "Resolved",
            "commander": commander,
            "document_id": document_id,
        })

    # 2. Detect Services (e.g., payment-service, auth-service, order-processing-service)
    service_names = set(re.findall(r"\b([a-z]+-[a-z]+(?:-[a-z]+)?-service|[a-z]+-service|[a-z]+-hub)\b", text, re.IGNORECASE))
    for s_name in service_names:
        s_lower = s_name.lower()
        tier = "Tier-1" if any(k in s_lower for k in ["payment", "auth", "order"]) else "Tier-2"
        data.services.append({
            "id": f"srv-{s_lower}",
            "name": s_lower,
            "tier": tier,
            "status": "Active",
        })

    # 3. Detect Teams (e.g., Payments Platform, Security Core, Orders Squad, Platform Ops)
    team_patterns = [
        r"(Payments Platform(?: Team)?)",
        r"(Security Core(?: Team)?)",
        r"(Orders (?:& Logistics )?Squad(?: Team)?)",
        r"(Platform (?:Ops|Engineering)(?: Team)?)",
    ]
    for pattern in team_patterns:
        t_match = re.search(pattern, text, re.IGNORECASE)
        if t_match:
            t_raw = t_match.group(1).strip()
            # Normalize team name
            t_name = "Payments Platform" if "payment" in t_raw.lower() else (
                "Security Core" if "security" in t_raw.lower() else (
                    "Orders Squad" if "order" in t_raw.lower() else "Platform Ops"
                )
            )
            # Find team lead scoped to this team section
            team_section_match = re.search(rf"{re.escape(t_raw)}[\s\S]{{1,400}}?(?=###|\Z)", text, re.IGNORECASE)
            team_block = team_section_match.group(0) if team_section_match else text
            lead_match = re.search(r"Team Lead[:\s*]+([A-Z][a-z]+ [A-Z][a-z]+)", team_block, re.IGNORECASE)
            lead = lead_match.group(1) if lead_match else ""
            data.teams.append({
                "id": f"team-{t_name.lower().replace(' ', '-')}",
                "name": t_name,
                "lead": lead,
            })

    # 4. Detect Runbooks (e.g., RB-PAY-04, RB-AUTH-02)
    rb_matches = set(re.findall(r"\b(RB-[A-Z]+-\d{2,3})\b", text))
    for rb_id in rb_matches:
        # Link incident to runbook document if incident present
        for inc in data.incidents:
            data.relationships.append({
                "from_label": "Incident",
                "from_id": inc["id"],
                "from_key": "id",
                "rel_type": "DOCUMENTED_IN",
                "to_label": "Document",
                "to_id": rb_id,
                "to_key": "title",
            })

    # 5. Extract Team Responders and Incident Resolution Links
    if data.incidents and data.teams:
        for inc in data.incidents:
            for team in data.teams:
                if "resolved by" in text.lower() or "owning team" in text.lower() or "resolving team" in text.lower():
                    data.relationships.append({
                        "from_label": "Incident",
                        "from_id": inc["id"],
                        "from_key": "id",
                        "rel_type": "RESOLVED_BY",
                        "to_label": "Team",
                        "to_id": team["name"],
                        "to_key": "name",
                    })

    # 6. Extract Service Outage Links
    if data.services and data.incidents:
        for inc in data.incidents:
            for srv in data.services:
                if srv["name"] in text.lower():
                    data.relationships.append({
                        "from_label": "Service",
                        "from_id": srv["name"],
                        "from_key": "name",
                        "rel_type": "AFFECTED_BY",
                        "to_label": "Incident",
                        "to_id": inc["id"],
                        "to_key": "id",
                    })

    # 7. Extract Service Ownership Links
    if data.services and data.teams:
        for srv in data.services:
            for team in data.teams:
                # Match payments -> payment-service, security -> auth-service, orders -> order-service
                if ("payment" in srv["name"] and "Payments" in team["name"]) or \
                   ("auth" in srv["name"] and "Security" in team["name"]) or \
                   ("order" in srv["name"] and "Orders" in team["name"]):
                    data.relationships.append({
                        "from_label": "Team",
                        "from_id": team["name"],
                        "from_key": "name",
                        "rel_type": "OWNS",
                        "to_label": "Service",
                        "to_id": srv["name"],
                        "to_key": "name",
                    })

    # 8. Detect Employees (e.g., Elena Rostova, Marcus Vance, Sarah Chen)
    emp_matches = re.findall(r"([A-Z][a-z]+ [A-Z][a-z]+)\s*\(([^@\)]+@[^\)]+)\)", text)
    for name, email in emp_matches:
        data.employees.append({
            "id": f"emp-{name.lower().replace(' ', '-')}",
            "name": name,
            "email": email,
            "role": "Engineer",
        })
        # If a team is present, associate employee with team
        if data.teams:
            data.relationships.append({
                "from_label": "Employee",
                "from_id": name,
                "from_key": "name",
                "rel_type": "MEMBER_OF",
                "to_label": "Team",
                "to_id": data.teams[0]["name"],
                "to_key": "name",
            })

    return data
