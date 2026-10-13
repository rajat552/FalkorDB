# Hackathon Requirements & Guidelines Audit

**Challenge Name:** FalkorDB Graph Agent Hackathon  
**Target Track:** Track 03 — Company Brain  
**Source:** Hackathon platform guidelines, FAQ sections, and challenge overview screenshots (Images 1–4)

---

## 1. Executive Summary of the Hackathon

The hackathon challenges developers to move away from traditional AI agents that "see pieces, not the whole picture." Standard agents lose track of earlier sessions, miss relationships between people and systems, and hallucinate because they work from guesswork rather than explicit connections.

The core challenge brief is:
> **"Put the agent's context in a graph. Data, memory, and company knowledge become nodes and edges the agent can follow, so it works from real relationships instead of guessing."**  
> *"Build an agent that acts on connected data, remembers what it learns, and can show how it got to each answer."*

---

## 2. Mandatory Rules & Platform Constraints

From the official FAQ and overview materials (Images 1–3):

1. **FalkorDB is Mandatory (Strict Condition):**
   - *"Is FalkorDB mandatory? Yes. FalkorDB must be the primary graph database, and it must support a central part of the product."* (Image 2)
2. **Team Size:**
   - Solo or up to a team of 4 members. Free to enter worldwide.
3. **Language & Tools:**
   - Any programming language is permitted (Python, TypeScript, Go, etc.).
   - Coding assistants are allowed.
4. **Tracks & Multi-Entry:**
   - Participants can submit to one, two, or all three tracks; each track carries its own prize.
5. **The Graph's Fundamental Role:**
   - Follow connections across data.
   - Connect people, projects, systems, and decisions.
   - Show the path/evidence behind an answer (explainable results).

---

## 3. Detailed Track Breakdown

The challenge features three specialized tracks (Image 4):

```
+-----------------------------------------------------------------------------------+
|                            FalkorDB Hackathon Tracks                              |
+-------------------------+-------------------------+-------------------------------+
|        Track 01         |        Track 02         |           Track 03            |
|  Agents That Act on     |  Agent Memory and       |        Company Brain          |
|     Connected Data      |      Coordination       |   (OUR SELECTED TRACK)        |
+-------------------------+-------------------------+-------------------------------+
| - Uses graph to decide  | - Remembers across      | - Understands how a company   |
|   and execute actions   |   sessions & agents     |   works (people, docs, teams) |
| - Fraud, security, code | - Episodic, semantic,   | - Cross-silo GraphRAG         |
|   triage                |   procedural memory     | - "Who owns what & who knows" |
| - MCP tool selection    | - Multi-agent handoffs  | - Decision tracing & sources  |
+-------------------------+-------------------------+-------------------------------+
```

### Detailed Requirements for Track 03: Company Brain (Our Track)

According to Image 4, Track 03 has five explicit key focus areas:

| Hackathon Requirement | Meaning in Simple English | What Judges Will Look For |
| :--- | :--- | :--- |
| **1. Knowledge from docs, tickets, and chats in one graph** | Ingest messy, separate company files (Markdown, PDFs, text, runbooks) into a single unified FalkorDB knowledge graph. | Can the system parse multiple documents and link their contents together? |
| **2. Who owns what, and who knows what** | Model real operational relationships (which team leads which service, which engineer resolved which outage). | Does the graph have `Team`, `Employee`, and `Service` nodes connected by `OWNS` or `MEMBER_OF` edges? |
| **3. Tracing decisions back to their source** | Never give an answer without proving where the information came from. | Are answers linked directly to original file chunks and exact text passages? |
| **4. Keeping knowledge current as things change** | Deduplicate content, support updates/reindexing, and allow adding or deleting documents without breaking the graph. | Is there file hashing (SHA-256) and clean cascading deletion/reindexing? |
| **5. Answers with clear sources** | Zero hallucinations; clear, verifiable citations displayed to the user with exact filenames and chunk passages. | Can the user click a citation badge and read the authentic excerpt? |

---

## 4. Hackathon Requirements Checklist

This checklist tracks every rule and expectation extracted from the challenge materials:

- [x] **FalkorDB as Primary Database:** FalkorDB runs as the central graph engine over Redis protocol (`:6379`).
- [x] **Track 03 Alignment:** System acts as an enterprise knowledge assistant connecting services, teams, incidents, and runbooks.
- [x] **Multi-Hop Graph Traversals:** Connects distinct entities across multiple documents via Cypher queries.
- [x] **Clear, Grounded Sources:** Cryptographically verifiable citations with exact start/end character offsets.
- [x] **Zero Guessing / Honest Abstention:** Explicitly returns `insufficient_evidence: true` when information is not in the graph.
- [x] **Multi-Document Ingestion:** Supports `.md`, `.txt`, `.pdf`, `.json` with SHA-256 deduplication.
- [x] **Working Prototype & Dashboard:** Accessible local/hosted web UI with live chat, evidence drawer, and graph explorer.
- [x] **Automated Tests & Evidence:** Test suite verifying queries, citations, and abstention behavior.
