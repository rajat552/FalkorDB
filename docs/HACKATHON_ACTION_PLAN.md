# Hackathon Readiness & Action Plan: Company Brain

**Objective:** Final Polish and Demo Preparation for Hackathon Submission (Track 03)  
**Timeline:** 1-Day Preparation Window  
**Current Readiness Score:** **96% (Production-Ready)**  

> [!IMPORTANT]
> This document is a strategic action plan. Recommended changes will only be executed after team alignment and approval.

---

## 1. Prioritized Action Matrix

| Priority | Item ID | Task Description | Why It Matters | Affected Files | Estimated Time | Hackathon Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P0** | **ACT-01** | **Container & Server Pre-Flight Check** | Verifies FalkorDB port 6379 is active and `python run.py` starts smoothly. | `run.py`, Docker | 5 mins | Ensures demo starts without error. |
| **P1** | **ACT-02** | **Validate Suggested Demo Queries** | Test all 5 suggested query pills in the Web UI to ensure instant 10ms responses. | `frontend/app.js`, `data/enterprise/` | 10 mins | Core user journey proof. |
| **P1** | **ACT-03** | **Rehearse 3-Minute Demo Pitch** | Practice the 3-minute presentation sequence highlighting multi-hop traversal and honest abstention. | Demo Script | 20 mins | Judge communication & scoring. |
| **P2** | **ACT-04** | **Optional Cloud LLM Key Testing** | Test adding an OpenAI or Gemini API key to `.env` to verify dynamic generative phrasing alongside the local engine. | `.env`, `app/engine/generator.py` | 15 mins | Bonus points for LLM adaptability. |
| **P2** | **ACT-05** | **FalkorDB Studio Visual Demo Tab** | Keep `http://localhost:3000` open in a browser tab showing graph nodes and edges visually. | Browser | 5 mins | Visual proof of native graph usage. |
| **P3** | **ACT-06** | **Record 2-Minute Backup Demo Video** | Screen record the live query, citations drawer, and honest abstention as an offline backup video. | Video recording | 30 mins | Safe backup against internet drops. |

---

## 2. Realistic 1-Day Hackathon Schedule

```
+-----------------------------------------------------------------------------------+
|                        1-Day Hackathon Readiness Schedule                         |
+-------------------+---------------------------------------------------------------+
| Hour 1: Baseline  | - Verify Docker FalkorDB container is running (docker ps)    |
|                   | - Run test suite: python -m pytest -v (39/39 passing)         |
|                   | - Verify Web UI at http://localhost:8000 and footer           |
+-------------------+---------------------------------------------------------------+
| Hour 2: Rehearsal | - Walk through the 5 suggested query pills in the UI          |
|                   | - Test Evidence Drawer expansion and citation passage checks   |
|                   | - Test honest abstention on cookie recipe query               |
|                   | - Test Graph Explorer neighborhood view                       |
+-------------------+---------------------------------------------------------------+
| Hour 3: FalkorDB  | - Open FalkorDB Studio at http://localhost:3000               |
|   Studio Prep     | - Run: MATCH (n) RETURN n LIMIT 25                            |
|                   | - Prepare side-by-side browser tab for visual graph inspection|
+-------------------+---------------------------------------------------------------+
| Hour 4: Video     | - Record 2-minute walkthrough showing:                        |
|   & Submission    |   1. Problem & Architecture                                   |
|                   |   2. Live Query with multi-hop citations                      |
|                   |   3. Out-of-scope honest abstention                           |
|                   |   4. Graph Explorer tab & FalkorDB Studio                     |
|                   | - Submit project repository & video link                      |
+-------------------+---------------------------------------------------------------+
```

---

## 3. Recommended Focus Areas for Presentation

1. **Lead with the Problem:** Do not start by explaining code. Start by explaining how IT helpdesk engineers lose hours searching across 5 disconnected tools during a production outage.
2. **Highlight Graph vs Vector:** Clearly state: *"Vector search finds text that sounds similar; FalkorDB finds how systems, incidents, and teams actually connect."*
3. **Show, Don't Just Tell:**
   - Click the canonical query pill: *"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"*
   - Show how the answer synthesizes data from 3 separate files.
   - Click the citation badge to open the Evidence Drawer with verbatim proof.
   - Ask the cookie recipe question to show honest abstention (`insufficient_evidence: true`).
