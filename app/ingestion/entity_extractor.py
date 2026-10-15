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
    text_lower = text.lower()

    # 1. Detect Incident (e.g., INC-2024-891)
    inc_match = re.search(r"\b(INC-\d{4}-\d+)\b", text, re.IGNORECASE)
    if inc_match:
        inc_id = inc_match.group(1).upper()

        title_match = re.search(r"Title[:\s]+([^\n]+)", text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else f"Incident {inc_id}"

        sev_match = re.search(r"Severity[:\s]+(Sev-[1-4])", text, re.IGNORECASE)
        severity = sev_match.group(1) if sev_match else "Sev-1"

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

    # 2. Detect Services (e.g., payment-service, auth-service, order-processing-service, notification-hub)
    service_names = set(re.findall(r"\b([a-z]+-[a-z]+(?:-[a-z]+)?-service|[a-z]+-service|[a-z]+-hub)\b", text, re.IGNORECASE))
    
    # Also find explicit backticked service names in tables or text
    table_service_names = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", text))
    for s_raw in table_service_names:
        if any(token in s_raw for token in ["service", "hub", "worker", "ledger", "proxy", "agent", "sync"]):
            service_names.add(s_raw)

    for s_name in service_names:
        s_lower = s_name.lower()
        tier = "Tier-1" if any(k in s_lower for k in ["payment", "auth", "order"]) else "Tier-2"
        data.services.append({
            "id": f"srv-{s_lower}",
            "name": s_lower,
            "tier": tier,
            "status": "Active",
        })

    # Helper: team normalizer
    def normalize_team(raw_name: str) -> str:
        r = raw_name.lower()
        if "payment" in r:
            return "Payments Platform"
        if "security" in r:
            return "Security Core"
        if "order" in r:
            return "Orders Squad"
        if "platform" in r or "ops" in r:
            return "Platform Ops"
        return raw_name.strip()

    # 3. Detect Team Sections & Members in Rosters (e.g., team-ownership-roster.md)
    team_sections = re.findall(r"###\s+([^\n]+)\n([\s\S]*?)(?=\n###|\n##|\Z)", text)
    found_teams: Dict[str, Dict[str, Any]] = {}

    for sec_header, sec_body in team_sections:
        if any(kw in sec_header.lower() for kw in ["team", "squad", "ops"]):
            t_name = normalize_team(sec_header)
            
            # Find lead
            lead_match = re.search(r"Team Lead[:\s*]+([A-Z][a-z]+ [A-Z][a-z]+)", sec_body, re.IGNORECASE)
            lead = lead_match.group(1).strip() if lead_match else ""

            if t_name not in found_teams or (lead and not found_teams[t_name].get("lead")):
                found_teams[t_name] = {
                    "id": f"team-{t_name.lower().replace(' ', '-')}",
                    "name": t_name,
                    "lead": lead,
                }

            # Find all employees in this section with roles
            emp_lines = re.findall(r"-\s+\*\*([^*:]+):?\*\*\s+([A-Za-z\s]+?)\s*\(`?([^`\)]+@[^`\)]+)`?\)", sec_body)
            for role_raw, emp_name, emp_email in emp_lines:
                clean_name = emp_name.strip()
                clean_role = role_raw.strip().replace(":", "")
                clean_email = emp_email.strip("` ")
                data.employees.append({
                    "id": f"emp-{clean_name.lower().replace(' ', '-')}",
                    "name": clean_name,
                    "email": clean_email,
                    "role": clean_role,
                })
                # Link employee specifically to this team
                data.relationships.append({
                    "from_label": "Employee",
                    "from_id": clean_name,
                    "from_key": "name",
                    "rel_type": "MEMBER_OF",
                    "to_label": "Team",
                    "to_id": t_name,
                    "to_key": "name",
                })


            # Check owned services in this section
            owned_match = re.search(r"Owned Services[:\s*]+([^\n]+)", sec_body, re.IGNORECASE)
            if owned_match:
                srv_in_sec = re.findall(r"`([a-z0-9-]+)`", owned_match.group(1))
                for s_owned in srv_in_sec:
                    data.relationships.append({
                        "from_label": "Team",
                        "from_id": t_name,
                        "from_key": "name",
                        "rel_type": "OWNS",
                        "to_label": "Service",
                        "to_id": s_owned,
                        "to_key": "name",
                    })

    # 4. Service-to-Team Ownership Matrix Table (in team-ownership-roster.md)
    matrix_rows = re.findall(r"\|\s*`([a-z0-9-]+)`\s*\|\s*([A-Za-z0-9-]+)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|", text)
    for s_name, tier, raw_team, raw_lead in matrix_rows:
        t_name = normalize_team(raw_team)
        lead = raw_lead.strip()
        if t_name not in found_teams:
            found_teams[t_name] = {
                "id": f"team-{t_name.lower().replace(' ', '-')}",
                "name": t_name,
                "lead": lead,
            }
        elif lead and not found_teams[t_name].get("lead"):
            found_teams[t_name]["lead"] = lead

        # Create OWNS relationship
        data.relationships.append({
            "from_label": "Team",
            "from_id": t_name,
            "from_key": "name",
            "rel_type": "OWNS",
            "to_label": "Service",
            "to_id": s_name,
            "to_key": "name",
        })

    # Add all unique detected teams
    for t_info in found_teams.values():
        data.teams.append(t_info)

    # 5. Service Specifications (e.g. auth-service-spec.md, payment-service-spec.md)
    if not found_teams:
        # Detect teams referenced in spec docs
        owning_team_match = re.search(r"Owning Team[:\s*]+([A-Za-z\s]+?)(?:\s*\(|\n)", text, re.IGNORECASE)
        if owning_team_match:
            t_name = normalize_team(owning_team_match.group(1))
            lead_match = re.search(r"Team Lead[:\s*]+([A-Z][a-z]+ [A-Z][a-z]+)", text, re.IGNORECASE)
            lead = lead_match.group(1).strip() if lead_match else ""
            data.teams.append({
                "id": f"team-{t_name.lower().replace(' ', '-')}",
                "name": t_name,
                "lead": lead,
            })
            # Link to the PRIMARY service specified in this doc
            spec_srv_match = re.search(r"Service Name[:\s*]+`?([a-z0-9-]+)`?", text, re.IGNORECASE)
            primary_srv = spec_srv_match.group(1).lower() if spec_srv_match else None
            if primary_srv:
                data.relationships.append({
                    "from_label": "Team",
                    "from_id": t_name,
                    "from_key": "name",
                    "rel_type": "OWNS",
                    "to_label": "Service",
                    "to_id": primary_srv,
                    "to_key": "name",
                })
            elif data.services:
                data.relationships.append({
                    "from_label": "Team",
                    "from_id": t_name,
                    "from_key": "name",
                    "rel_type": "OWNS",
                    "to_label": "Service",
                    "to_id": data.services[0]["name"],
                    "to_key": "name",
                })


    # 6. Service Dependencies (Downstream/Dependent Services)
    if "dependent services" in text_lower or "downstream" in text_lower:
        # Determine primary service of this spec
        spec_srv_match = re.search(r"Service Name[:\s*]+`?([a-z0-9-]+)`?", text, re.IGNORECASE)
        primary_srv = spec_srv_match.group(1).lower() if spec_srv_match else None
        
        if primary_srv:
            # If doc lists dependent services (e.g., auth-service where other services depend on it)
            if "depend on `auth-service`" in text_lower or "depend on auth-service" in text_lower:
                caller_matches = re.findall(r"- `([a-z0-9-]+)`:", text)
                for caller in caller_matches:
                    data.relationships.append({
                        "from_label": "Service",
                        "from_id": caller,
                        "from_key": "name",
                        "rel_type": "DEPENDS_ON",
                        "to_label": "Service",
                        "to_id": primary_srv,
                        "to_key": "name",
                    })
            # If doc lists downstream services (e.g., payment-service calls auth-service, notification-hub)
            downstream_matches = re.findall(r"- `([a-z0-9-]+)`:", text)
            if "downstream internal services" in text_lower:
                for target in downstream_matches:
                    data.relationships.append({
                        "from_label": "Service",
                        "from_id": primary_srv,
                        "from_key": "name",
                        "rel_type": "DEPENDS_ON",
                        "to_label": "Service",
                        "to_id": target,
                        "to_key": "name",
                    })

    # 7. Incident Resolution & Outage Links
    if data.incidents:
        for inc in data.incidents:
            # Resolving Team
            res_team_match = re.search(r"Resolving Team[:\s*]+([A-Za-z\s]+?)(?:\s*\(|\n)", text, re.IGNORECASE)
            if res_team_match:
                res_team = normalize_team(res_team_match.group(1))
                data.teams.append({
                    "id": f"team-{res_team.lower().replace(' ', '-')}",
                    "name": res_team,
                    "lead": "",
                })
                data.relationships.append({
                    "from_label": "Incident",
                    "from_id": inc["id"],
                    "from_key": "id",
                    "rel_type": "RESOLVED_BY",
                    "to_label": "Team",
                    "to_id": res_team,
                    "to_key": "name",
                })


            # Impacted Service
            for srv in data.services:
                if srv["name"] in text_lower:
                    data.relationships.append({
                        "from_label": "Service",
                        "from_id": srv["name"],
                        "from_key": "name",
                        "rel_type": "AFFECTED_BY",
                        "to_label": "Incident",
                        "to_id": inc["id"],
                        "to_key": "id",
                    })

    # 8. Runbook Links (e.g. RB-PAY-04)
    rb_matches = set(re.findall(r"\b(RB-[A-Z]+-\d{2,3})\b", text))
    for rb_id in rb_matches:
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

    # Deduplicate employees and relationships
    seen_emp = set()
    deduped_emp = []
    for emp in data.employees:
        if emp["name"] not in seen_emp:
            seen_emp.add(emp["name"])
            deduped_emp.append(emp)
    data.employees = deduped_emp

    seen_rel = set()
    deduped_rel = []
    for r in data.relationships:
        key = (r["from_label"], str(r["from_id"]), r["rel_type"], r["to_label"], str(r["to_id"]))
        if key not in seen_rel:
            seen_rel.add(key)
            deduped_rel.append(r)
    data.relationships = deduped_rel

    return data
