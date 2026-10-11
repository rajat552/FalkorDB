from __future__ import annotations
from graphrag_sdk.ontology import Ontology
from graphrag_sdk.entity import Entity
from graphrag_sdk.relation import Relation
from graphrag_sdk.attribute import Attribute, AttributeType


def get_enterprise_ontology() -> Ontology:
    """
    Build the canonical Enterprise IT Helpdesk ontology for Track 03: Company Brain.
    Entities: Employee, Team, Service, Incident, Document, EvidenceChunk.
    Relationships: MEMBER_OF, OWNS, AFFECTED_BY, RESOLVED_BY, DOCUMENTED_IN, CONTAINS, GROUNDED_IN.
    """
    ont = Ontology()

    # 1. Employee
    employee = Entity(
        label="Employee",
        attributes=[
            Attribute("id", AttributeType.STRING, unique=True, required=True),
            Attribute("name", AttributeType.STRING, unique=True, required=True),
            Attribute("email", AttributeType.STRING, unique=False, required=False),
            Attribute("role", AttributeType.STRING, unique=False, required=False),
        ],
    )
    ont.add_entity(employee)

    # 2. Team
    team = Entity(
        label="Team",
        attributes=[
            Attribute("id", AttributeType.STRING, unique=True, required=False),
            Attribute("name", AttributeType.STRING, unique=True, required=True),
            Attribute("lead", AttributeType.STRING, unique=False, required=False),
        ],
    )
    ont.add_entity(team)

    # 3. Service
    service = Entity(
        label="Service",
        attributes=[
            Attribute("id", AttributeType.STRING, unique=True, required=False),
            Attribute("name", AttributeType.STRING, unique=True, required=True),
            Attribute("tier", AttributeType.STRING, unique=False, required=False),
            Attribute("status", AttributeType.STRING, unique=False, required=False),
        ],
    )
    ont.add_entity(service)

    # 4. Incident
    incident = Entity(
        label="Incident",
        attributes=[
            Attribute("id", AttributeType.STRING, unique=True, required=True),
            Attribute("title", AttributeType.STRING, unique=False, required=False),
            Attribute("severity", AttributeType.STRING, unique=False, required=False),
            Attribute("root_cause", AttributeType.STRING, unique=False, required=False),
            Attribute("status", AttributeType.STRING, unique=False, required=False),
            Attribute("document_id", AttributeType.STRING, unique=False, required=False),
        ],
    )
    ont.add_entity(incident)

    # 5. Document
    document = Entity(
        label="Document",
        attributes=[
            Attribute("id", AttributeType.STRING, unique=True, required=True),
            Attribute("filename", AttributeType.STRING, unique=False, required=True),
            Attribute("title", AttributeType.STRING, unique=False, required=False),
            Attribute("content_hash", AttributeType.STRING, unique=False, required=False),
            Attribute("uploaded_at", AttributeType.STRING, unique=False, required=False),
            Attribute("chunk_count", AttributeType.NUMBER, unique=False, required=False),
        ],
    )
    ont.add_entity(document)

    # 6. EvidenceChunk
    evidence_chunk = Entity(
        label="EvidenceChunk",
        attributes=[
            Attribute("id", AttributeType.STRING, unique=True, required=True),
            Attribute("document_id", AttributeType.STRING, unique=False, required=True),
            Attribute("index", AttributeType.NUMBER, unique=False, required=False),
            Attribute("text", AttributeType.STRING, unique=False, required=True),
            Attribute("start_char", AttributeType.NUMBER, unique=False, required=False),
            Attribute("end_char", AttributeType.NUMBER, unique=False, required=False),
            Attribute("char_count", AttributeType.NUMBER, unique=False, required=False),
        ],
    )
    ont.add_entity(evidence_chunk)

    # --- Relationships ---
    # (Employee)-[:MEMBER_OF]->(Team)
    ont.add_relation(
        Relation(label="MEMBER_OF", source="Employee", target="Team", attributes=[])
    )

    # (Team)-[:OWNS]->(Service)
    ont.add_relation(
        Relation(label="OWNS", source="Team", target="Service", attributes=[])
    )

    # (Service)-[:AFFECTED_BY]->(Incident)
    ont.add_relation(
        Relation(label="AFFECTED_BY", source="Service", target="Incident", attributes=[])
    )

    # (Incident)-[:RESOLVED_BY]->(Team)
    ont.add_relation(
        Relation(label="RESOLVED_BY", source="Incident", target="Team", attributes=[])
    )

    # (Incident)-[:DOCUMENTED_IN]->(Document)
    ont.add_relation(
        Relation(label="DOCUMENTED_IN", source="Incident", target="Document", attributes=[])
    )

    # (Document)-[:CONTAINS]->(EvidenceChunk)
    ont.add_relation(
        Relation(label="CONTAINS", source="Document", target="EvidenceChunk", attributes=[])
    )

    # (Service)-[:GROUNDED_IN]->(EvidenceChunk)
    ont.add_relation(
        Relation(label="GROUNDED_IN", source="Service", target="EvidenceChunk", attributes=[])
    )

    # (Incident)-[:GROUNDED_IN]->(EvidenceChunk)
    ont.add_relation(
        Relation(label="GROUNDED_IN", source="Incident", target="EvidenceChunk", attributes=[])
    )

    return ont
