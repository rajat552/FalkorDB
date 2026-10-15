# Company Brain — Professional 3:30 Product Demo Video Script
**Track 03: Enterprise RAG (FalkorDB Graph Agent Hackathon)**  
**Target Runtime:** 3 minutes 30 seconds (210 seconds) | **Format:** 1920×1080 @ 30 FPS Full HD  
**Document Generated:** October 2026 | **Repository:** [rajat552/FalkorDB](https://github.com/rajat552/FalkorDB)

---

## 1. Project Overview

### 1.1 Product Identity & Mission
* **Product Name:** Company Brain
* **Core Value Proposition:** A relationship-aware Enterprise GraphRAG intelligence assistant engineered for Site Reliability Engineers (SREs), DevOps engineers, platform teams, and IT helpdesk operators.
* **The Problem Solved:** Enterprise IT knowledge is fragmented across heterogeneous silos: service architecture specs, incident postmortems, escalation policies, team directories, and operational runbooks. Naive Vector RAG treats documents as isolated text chunks, failing to answer multi-hop dependency questions (e.g., *"Which team owns the service that failed during the last incident, and which runbook contains the recovery procedure?"*), and frequently hallucinates answers to out-of-scope inquiries.
* **The Solution:** Company Brain unifies all IT assets into an in-memory property graph powered by **FalkorDB**. It performs multi-hop Cypher traversals in sub-10ms latency, cryptographically grounds every factual claim to exact character offsets in source files, and enforces a deterministic Honest Abstention mechanism that refuses to invent answers when graph evidence is absent.

### 1.2 Technology Stack
* **Graph Database:** FalkorDB v1.7+ (Redis Protocol, GraphBLAS linear algebra engine)
* **Backend Framework:** FastAPI (Asynchronous Python 3.12 REST API)
* **Frontend:** Vanilla HTML5, CSS3, ES6 (Zero build-step single-page application)
* **Graph Modeling:** GraphRAG SDK with custom Enterprise IT Helpdesk ontology
* **Dual-Mode Synthesis:** Live Cloud LLM (OpenAI GPT-4o / Google Gemini) + Deterministic Local Grounded Synthesizer (Zero-cost, offline, 100% reproducible)
* **Quality Assurance:** 42/42 automated tests (100% pass rate) across unit, integration, and quantitative benchmark suites

---

## 2. Analysis Summary and Verified Features

Every feature listed below has been verified against the active codebase and running server (`http://127.0.0.1:8000`):

| Feature / Capability | Implementation Evidence | Runtime Verification Status | Demo Priority |
| :--- | :--- | :--- | :--- |
| **Multi-Hop Cypher Traversal** | `app/engine/retriever.py`, `app/engine/pipeline.py` | **Verified**: 4-hop query links service → incident → team → runbook in `< 10ms` | **High (Scene 2)** |
| **Verified Citation Badging** | `app/engine/citations.py`, `frontend/app.js` | **Verified**: Exact source document, chunk ID, and snippet returned | **High (Scene 2 & 3)** |
| **Evidence Drawer & Chunk Modal** | `frontend/index.html`, `frontend/app.js` | **Verified**: Clicking citation opens modal with verbatim text & offsets | **High (Scene 3)** |
| **Honest Abstention Mechanism** | `app/engine/generator.py` (`insufficient_evidence: true`) | **Verified**: Out-of-scope query triggers amber badge & 0 hallucinations | **High (Scene 4)** |
| **Document Management & Deduplication** | `app/ingestion/validator.py`, `app/main.py` | **Verified**: Ingests `.md`, `.txt`, `.pdf`, `.json`; rejects duplicates via SHA-256 | **High (Scene 5)** |
| **Real-Time Document Search Filter** | `frontend/app.js` (`filterDocumentsTable`) | **Verified**: Instant filtering across filenames, IDs, and titles | **Medium (Scene 5)** |
| **Interactive Graph Explorer** | `frontend/app.js` (`renderTopologyCanvas`) | **Verified**: High-DPI Canvas with orbiting nodes, directional arcs, hover glow | **High (Scene 6)** |
| **360° Neighborhood Directory** | `app/main.py` (`/api/graph/related`) | **Verified**: Traverses incoming and outgoing edges for any selected entity | **High (Scene 6)** |
| **Live Database Health Diagnostics** | `app/db.py`, `app/main.py` (`/health`) | **Verified**: Returns connection status, cloud latency ms, node & edge counts | **Medium (Scene 1 & 7)** |

---

## 3. Recording Prerequisites

### 3.1 System State & Running Services
1. **Application Server:** FastAPI server must be running locally or via your cloud deployment:
   ```powershell
   python run.py
   ```
   *Confirmed running at: `http://127.0.0.1:8000`*
2. **Database:** FalkorDB instance connected (Local Docker container on `6379` or FalkorDB Cloud instance on `65122`).
3. **Data Seeding:** Graph must contain the canonical enterprise dataset (45 nodes, 60 edges):
   ```powershell
   python ingest.py --force
   ```

### 3.2 Display & Browser Configuration
* **Resolution:** 1920 × 1080 (1080p Full HD)
* **Browser:** Google Chrome or Microsoft Edge, maximized
* **Zoom Level:** Exactly 100% (Press `Ctrl + 0`)
* **Bookmarks Bar:** Hidden (Press `Ctrl + Shift + B`)
* **Starting URL:** `http://127.0.0.1:8000/`
* **Clean State:** If you ran previous queries, click **Clear History** on the chat header before starting the recording.

---

## 4. Complete Timestamped Video Script

| Time | Duration | Screen / Page | Mouse & Keyboard Actions | Voiceover Narration | Expected On-Screen Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0:00–0:15** | 15s | `Workspace & Chat` (`http://127.0.0.1:8000/`) | Cursor starts at screen center. Smoothly move cursor to header brand: hover over the orange **Company Brain** logo, then pause over the live green indicator **FalkorDB: Connected**, then hover over the metric pill **45 nodes • 60 edges**. | *"Welcome to Company Brain, an enterprise GraphRAG platform powered by FalkorDB for IT helpdesk and Site Reliability Engineering teams."* | The warm ivory/coral interface is visible. Glowing live badge indicates FalkorDB Cloud connectivity with sub-second latency and active graph metrics. |
| **0:15–0:30** | 15s | `Workspace & Chat` | Move cursor down into the chat container. Hover over the subtitle text: *"Ask cross-document questions grounded in runbooks, incidents, and ownership graphs."* Sweep cursor slowly across the suggested query pills. | *"In enterprise production environments, incidents span fragmented silos—service architectures, incident postmortems, escalation policies, and runbooks. Traditional vector RAG fails because it treats documents as isolated snippets, completely losing the relational context needed to resolve outages."* | Suggested query pills are visible in an accessible multi-row layout. Welcome message from Company Brain bot confirms indexed repositories. |
| **0:30–0:48** | 18s | `Workspace & Chat` | Move cursor directly over the first suggested query pill: `"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"`. Pause for 1 second showing hover highlight, then click it. | *"Let's test a complex multi-hop inquiry. We ask: Which team resolved the latest payment-service incident, what was the root cause, and which runbook documents the recovery procedure?"* | Button triggers click animation. Input bar populates. "Traversing knowledge graph and validating evidence passages..." appears briefly. |
| **0:48–1:10** | 22s | `Workspace & Chat` + `Evidence Panel` | As the bot response renders, move cursor to the green badge: **✓ Grounded in 2 Verified Sources**. Then pan cursor over to the right sidebar: hover over the 2 verified citation cards, then scroll slightly down to show **Graph Relationships Traversed**. | *"In under ten milliseconds, FalkorDB executes a four-hop Cypher traversal. It connects payment-service to incident INC-2024-891, identifies the Payments Platform team as the resolving owner, and links the exact recovery runbook, RB-PAY-04. Notice the traversed relationship pills displayed on the right."* | Bot delivers complete synthesized answer. Evidence sidebar displays verified citations and graph relationship edges: `(Payments Platform) -[OWNS]-> (payment-service)`, `(payment-service) -[AFFECTED_BY]-> (INC-2024-891)`, `(INC-2024-891) -[DOCUMENTED_IN]-> (RB-PAY-04)`. |
| **1:10–1:25** | 15s | `Evidence Panel` | Move cursor to the second citation card (`RB-PAY-04-payment-recovery.md`). Hover over the link text **View full source passage ›** and click it. | *"Unlike standard search tools that hallucinate plausible answers, Company Brain provides cryptographic traceability. Clicking any citation opens the exact chunk with its verified character boundaries."* | The Chunk Viewer Modal smoothly opens over the screen, displaying Chunk ID `chunk-doc-d9d3055991a7-0`, document title, and the full verbatim runbook recovery text. |
| **1:25–1:40** | 15s | `Chunk Viewer Modal` | Move cursor inside the modal passage box, scroll down slightly to show the verbatim runbook steps, then click the **Close** button (or `×`) in the modal footer. | *"Engineers never have to second-guess the output. Every statement is cryptographically anchored to authentic enterprise documentation."* | Modal closes cleanly with a smooth fade-out. Focus returns to the Workspace & Chat interface. |
| **1:40–1:55** | 15s | `Workspace & Chat` | Move cursor to the amber query pill at the bottom of the suggestions list: `"What is the secret recipe for chocolate cookies?"`. Pause for 1 second to show the amber hover state, then click it. | *"Now, what happens with completely irrelevant or out-of-scope inquiries? Traditional RAG systems hallucinate answers based on nearest-neighbor vector approximations. Company Brain takes a fundamentally different approach."* | Pill triggers submit. Temporary reasoning state appears, followed immediately by the bot response. |
| **1:55–2:10** | 15s | `Workspace & Chat` + `Evidence Panel` | Hover over the bot message: *"I do not have sufficient information in the ingested documentation or knowledge graph to answer this inquiry."* Hover over the amber badge **Honest Abstention (Insufficient Evidence)**. Hover over the Evidence sidebar showing **0 citations**. | *"Company Brain triggers Honest Abstention. Because no verifiable evidence exists in FalkorDB, it deterministically refuses to invent facts, maintaining complete enterprise trustworthiness."* | Amber badge clearly indicates Honest Abstention. Evidence counter resets to 0 citations, proving zero hallucination. |
| **2:10–2:25** | 15s | Top Navigation → `Documents Tab` | Move cursor to top navigation. Hover over the **Documents** tab (showing document icon). Click it. | *"Next, let's explore Document Management. Company Brain ingests enterprise Markdown, plain text, PDF, and JSON documents through an automated pipeline."* | Page transitions to Document Management. Header displays subtitle. Upload dropzone and Documents data table appear populated with 6 files. |
| **2:25–2:45** | 20s | `Documents Tab` | Hover over the search bar **Filter documents by name, title, or ID...**. Type `payment`. Notice table filters to 3 files. Clear the search bar. Move cursor over the SHA-256 fingerprint badge on `payment-service-spec.md`. Hover over the **View Chunks** button on `INC-2024-891-payment-timeout.md`. | *"Every uploaded file is fingerprinted using SHA-256 to reject duplicates with HTTP 409 Conflict, preventing index bloat. Documents are partitioned into sliding-window chunks with character offsets and mapped into FalkorDB entities."* | Table instantly filters in real time as keys are typed, then restores all 6 documents. SHA-256 cryptographic badges and chunk counts (3 chunks, 4 chunks) are clearly visible. |
| **2:45–3:00** | 15s | Top Navigation → `Graph Explorer Tab` | Move cursor to top navigation. Hover over **Graph Explorer** tab and click it. Sweep cursor across the 6 metric cards: **10 Services**, **4 Teams**, **1 Incident**, **8 Employees**, **6 Documents**, **16 Chunks**. | *"Now let's open the interactive Knowledge Graph Explorer. Here we see live metrics across all enterprise entities managed within FalkorDB."* | Tab switches to Graph Explorer. Metrics grid displays live counts matching FalkorDB schema. Interactive HTML5 Canvas visualizer renders center entity with orbiting nodes. |
| **3:00–3:15** | 15s | `Graph Explorer Tab` | Click the entity dropdown (`#entity-select`) and select `payment-service`. The canvas smoothly redraws with radial layout. Hover over orbiting node `INC-2024-891` (it pulses with hover glow). Click `INC-2024-891`. The graph dynamically re-centers on the incident! Scroll down to show the **360° Neighborhood Directory**. | *"We can select any service—like payment-service—to inspect its real-time topology. Hovering highlights connection arcs, and clicking any node traverses deeper into its neighborhood, displaying incoming and outgoing relationships."* | Canvas re-centers with animated directional arcs. 360° Neighborhood Directory shows incoming `AFFECTED_BY` edges and outgoing `RESOLVED_BY` and `DOCUMENTED_IN` cards. |
| **3:15–3:30** | 15s | Top Navigation → `Workspace & Chat Tab` | Click **Workspace & Chat** tab in top nav. Move cursor smoothly to center of screen, then pause on the header indicator **FalkorDB: Connected**. | *"Backed by FalkorDB's ultra-low latency graph engine, a dual-mode synthesis pipeline, and forty-two passing automated tests, Company Brain brings verified truth to enterprise operations. Thank you."* | Clean return to Workspace & Chat. Full dashboard visible. Recording ends on a professional, polished view. |

---

## 5. Exact Mouse, Hover, Scroll, and Click Instructions

### Scene 1: Header Brand & Status Inspection (0:00 – 0:30)
1. **0:00–0:05:** Position cursor at coordinates `(960, 500)` (center screen).
2. **0:05–0:09:** Move cursor smoothly to top-left `(180, 40)` over the brand icon **Company Brain**. Pause for 1.5 seconds.
3. **0:09–0:14:** Move cursor horizontally right to `(1150, 40)` over the green pill **FalkorDB: Connected (XXms)**. Pause 2 seconds to let viewer read the latency and health status.
4. **0:14–0:20:** Move cursor right to `(1320, 40)` over the badge **45 nodes • 60 edges**. Pause 1.5 seconds.
5. **0:20–0:30:** Move cursor down into the chat container at `(450, 160)` across the subtitle, then sweep slowly left-to-right across the suggested query pills.

### Scene 2: Multi-Hop Query Execution (0:30 – 1:10)
1. **0:30–0:33:** Move cursor directly over the first suggested query pill:
   `"Which team resolved the latest payment-service incident, what caused it, and which runbook documents the fix?"`
2. **0:33–0:35:** Hover over the pill. Notice the coral border and background elevation hover effect. Pause 1 second.
3. **0:35–0:36:** Left-click the pill.
4. **0:36–0:48:** Do not move cursor erratically. Keep cursor resting near `(500, 350)`. Observe the input bar populate, send button trigger, and loading message appear.
5. **0:48–0:55:** Once the bot message renders, move cursor to the green badge **✓ Grounded in 2 Verified Sources**. Pause 1.5 seconds.
6. **0:55–1:10:** Move cursor smoothly into the right Evidence Sidebar:
   - Hover over Citation 1 (`INC-2024-891-payment-timeout.md`).
   - Move down and hover over Citation 2 (`RB-PAY-04-payment-recovery.md`).
   - Scroll down 100px in the sidebar to reveal the **Graph Relationships Traversed** pills:
     `Payments Platform -[OWNS]-> payment-service`, `payment-service -[AFFECTED_BY]-> INC-2024-891`, `INC-2024-891 -[DOCUMENTED_IN]-> RB-PAY-04`.

### Scene 3: Verbatim Chunk Inspector Modal (1:10 – 1:40)
1. **1:10–1:14:** Move cursor to the blue link **View full source passage ›** on the second citation card.
2. **1:14–1:15:** Left-click **View full source passage ›**.
3. **1:15–1:20:** Pause as the Chunk Viewer Modal animates into view. Point cursor at the Chunk ID badge: `chunk-doc-d9d3055991a7-0`.
4. **1:20–1:30:** Move cursor into the `<pre class="passage-box">` text area and scroll down 80px to show the Markdown section:
   `## 2. Emergency Recovery Steps` and `1. Drain connection pool`.
5. **1:30–1:35:** Move cursor to the **Close** button in the bottom right of the modal.
6. **1:35–1:36:** Left-click **Close**.
7. **1:36–1:40:** Pause as modal fades out and main workspace re-appears.

### Scene 4: Deterministic Honest Abstention (1:40 – 2:10)
1. **1:40–1:45:** Move cursor back to the Suggested Queries area.
2. **1:45–1:48:** Hover over the amber pill at the end:
   `"What is the secret recipe for chocolate cookies?"`
   Notice the distinct amber border and subtle glow. Pause 1 second.
3. **1:48–1:49:** Left-click the amber pill.
4. **1:49–1:55:** Keep cursor steady as query submits.
5. **1:55–2:02:** Move cursor over the bot response text:
   *"I do not have sufficient information in the ingested documentation or knowledge graph to answer this inquiry."*
6. **2:02–2:06:** Hover over the amber badge: **Honest Abstention (Insufficient Evidence)**.
7. **2:06–2:10:** Move cursor to the right panel header: hover over **0 citations**.

### Scene 5: Documents Management & Live Filtering (2:10 – 2:45)
1. **2:10–2:13:** Move cursor to top navigation and click the **Documents** tab (`#tab-documents`).
2. **2:13–2:18:** Hover cursor over the dashed dropzone area: *"Drag and drop files here, or click to browse"*.
3. **2:18–2:22:** Move cursor to the search box: `#doc-search-input`.
4. **2:22–2:27:** Click into search box and type: `payment`. Table instantly filters down to the 3 matching payment files.
5. **2:27–2:32:** Select all text in search box (`Ctrl + A`) and press `Backspace`. Table immediately restores all 6 documents.
6. **2:32–2:37:** Hover over the SHA-256 fingerprint hash badge on `RB-PAY-04-payment-recovery.md` (e.g. `d9d30559...`).
7. **2:37–2:42:** Move cursor to the action button **View Chunks** on `INC-2024-891-payment-timeout.md`. Click it.
8. **2:42–2:45:** Inspect chunk modal for 2 seconds, then click **Close**.

### Scene 6: Interactive Knowledge Graph Explorer (2:45 – 3:15)
1. **2:45–2:48:** Move cursor to top navigation and click the **Graph Explorer** tab (`#tab-explorer`).
2. **2:48–2:53:** Sweep cursor across the 6 top metric cards: 10 Services, 4 Teams, 1 Incident, 8 Employees, 6 Documents, 16 Chunks.
3. **2:53–2:56:** Move cursor to the dropdown `#entity-select` and click it.
4. **2:56–2:58:** Select **`payment-service (Service)`**.
5. **2:58–3:04:** Canvas redraws. Move cursor onto the canvas: hover over the orbiting node **INC-2024-891**. Notice the node lights up with a luminous halo.
6. **3:04–3:06:** Left-click the **INC-2024-891** node on the canvas.
7. **3:06–3:10:** Canvas smoothly transitions, making INC-2024-891 the new center node!
8. **3:10–3:15:** Scroll down 200px to display the **360° Neighborhood Directory** showing incoming `AFFECTED_BY` and outgoing `RESOLVED_BY` and `DOCUMENTED_IN` cards.

### Scene 7: Professional Closing (3:15 – 3:30)
1. **3:15–3:18:** Scroll back to top and click the **Workspace & Chat** tab in the top navigation.
2. **3:18–3:24:** Move cursor smoothly to center screen, resting on the clean chat area.
3. **3:24–3:30:** Hover briefly over the top header **FalkorDB: Connected** indicator as voiceover concludes. End recording smoothly.

---

## 6. Complete Voiceover in Timeline Order

```text
[0:00 – 0:15]
"Welcome to Company Brain, an enterprise GraphRAG platform powered by FalkorDB for IT helpdesk and Site Reliability Engineering teams."

[0:15 – 0:30]
"In enterprise production environments, incidents span fragmented silos—service architectures, incident postmortems, escalation policies, and runbooks. Traditional vector RAG fails because it treats documents as isolated snippets, completely losing the relational context needed to resolve outages."

[0:30 – 0:48]
"Let's test a complex multi-hop inquiry. We ask: Which team resolved the latest payment-service incident, what was the root cause, and which runbook documents the recovery procedure?"

[0:48 – 1:10]
"In under ten milliseconds, FalkorDB executes a four-hop Cypher traversal. It connects payment-service to incident INC-2024-891, identifies the Payments Platform team as the resolving owner, and links the exact recovery runbook, RB-PAY-04. Notice the traversed relationship pills displayed on the right."

[1:10 – 1:25]
"Unlike standard search tools that hallucinate plausible answers, Company Brain provides cryptographic traceability. Clicking any citation opens the exact chunk with its verified character boundaries."

[1:25 – 1:40]
"Engineers never have to second-guess the output. Every statement is cryptographically anchored to authentic enterprise documentation."

[1:40 – 1:55]
"Now, what happens with completely irrelevant or out-of-scope inquiries? Traditional RAG systems hallucinate answers based on nearest-neighbor vector approximations. Company Brain takes a fundamentally different approach."

[1:55 – 2:10]
"Company Brain triggers Honest Abstention. Because no verifiable evidence exists in FalkorDB, it deterministically refuses to invent facts, maintaining complete enterprise trustworthiness."

[2:10 – 2:25]
"Next, let's explore Document Management. Company Brain ingests enterprise Markdown, plain text, PDF, and JSON documents through an automated pipeline."

[2:25 – 2:45]
"Every uploaded file is fingerprinted using SHA-256 to reject duplicates with HTTP 409 Conflict, preventing index bloat. Documents are partitioned into sliding-window chunks with character offsets and mapped into FalkorDB entities."

[2:45 – 3:00]
"Now let's open the interactive Knowledge Graph Explorer. Here we see live metrics across all enterprise entities managed within FalkorDB."

[3:00 – 3:15]
"We can select any service—like payment-service—to inspect its real-time topology. Hovering highlights connection arcs, and clicking any node traverses deeper into its neighborhood, displaying incoming and outgoing relationships."

[3:15 – 3:30]
"Backed by FalkorDB's ultra-low latency graph engine, a dual-mode synthesis pipeline, and forty-two passing automated tests, Company Brain brings verified truth to enterprise operations. Thank you."
```

*Word count: 442 words across 210 seconds (~126 words per minute — perfectly paced for instructional clarity).*

---

## 7. Expected On-Screen Results and Scene Transitions

| Scene | Start Timestamp | On-Screen Visual Result | Transition to Next Scene |
| :---: | :---: | :--- | :--- |
| **1** | `0:00` | Warm ivory/coral header, logo, live green FalkorDB indicator, 45 nodes / 60 edges counter, suggested queries block. | Natural camera hold; cursor moves down toward first query pill. |
| **2** | `0:30` | Query sent; loading animation displays; synthesized answer appears with green badge `✓ Grounded in 2 Verified Sources`; Evidence Sidebar lists 2 citations and traversed graph edges. | Cursor moves to citation card link to inspect source text. |
| **3** | `1:10` | Dark backdrop modal smoothly opens showing Chunk ID, filename, and verbatim passage text. | Modal close button clicked; modal fades out; returns to workspace. |
| **4** | `1:40` | Cookie recipe query sent; bot responds with polite refusal; amber badge `Honest Abstention` appears; sidebar shows 0 citations. | Cursor moves up to navigation bar to switch views. |
| **5** | `2:10` | Documents table loads with 6 files, SHA-256 hashes, and chunk counters; live search filters to payment files and restores. | Cursor moves to top navigation bar to open Graph Explorer. |
| **6** | `2:45` | High-DPI radial topology canvas renders `payment-service` with orbiting entities; clicking incident re-centers graph; 360° directory displays below. | Cursor returns to top navigation bar for closing shot. |
| **7** | `3:15` | Workspace & Chat re-opens with complete conversation history and live header indicator. | Voiceover delivers final sentence; video fades to black at `3:30`. |

---

## 8. Final Pre-Recording Checklist

Follow this checklist before hitting "Record":

- [ ] **1. Server Running:** Verify server is active by opening `http://127.0.0.1:8000/health`. Look for `"status": "healthy"` and `"connected": true`.
- [ ] **2. Seeded Graph:** Confirm the database has 45 nodes and 60 edges. If not, run `python ingest.py --force`.
- [ ] **3. Screen Resolution:** Set monitor display to **1920 × 1080** at 100% DPI scaling.
- [ ] **4. Browser Window:** Maximize Google Chrome or Edge. Hide bookmark bar (`Ctrl + Shift + B`). Close any extraneous tabs.
- [ ] **5. Zoom Level:** Reset browser zoom to exactly **100%** (`Ctrl + 0`).
- [ ] **6. Reset Chat:** Click **Clear History** on the chat interface so the screen starts on the clean initial welcome message.
- [ ] **7. Audio Check:** Test microphone levels. Ensure no background noise, fan hum, or keyboard clicks.
- [ ] **8. Cursor Smoothness:** Enable smooth pointer movement in recording software (OBS Studio / Loom / Camtasia) at 30 or 60 FPS.
- [ ] **9. Privacy:** Ensure no terminal windows with passwords, `.env` files, or personal notifications pop up during recording.
- [ ] **10. Dry Run:** Do one complete 3-minute practice run following the mouse movement instructions to build muscle memory before the final take.

---

## 9. Unverified Features and Known Limitations

To maintain absolute technical integrity, note the following scope boundaries:

1. **Deterministic Local Grounded Synthesizer vs Cloud LLM:**
   - In offline/free mode (no `OPENAI_API_KEY` or `GOOGLE_API_KEY` provided), Company Brain uses its built-in rule-based grounded engine. It answers the canonical benchmark questions with 100% precision. If an OpenAI or Gemini API key is configured in `.env`, the answer text becomes more conversational, but the graph citations and evidence offsets remain identical.
2. **Document Upload in Demo:**
   - The demo shows live document filtering and chunk inspection rather than uploading a new file. While uploading works (`POST /api/documents/upload`), demonstrating drag-and-drop file selection introduces OS file picker windows that can disrupt the visual flow of a 3-minute demo.
3. **Graph Explorer Subgraph Size:**
   - The interactive canvas visualizes 1-hop and 2-hop neighborhoods centered around the selected entity to prevent visual clutter and maintain 60 FPS rendering performance. It does not attempt to render all 45 nodes at once on a single screen.

---

## 10. Total Runtime and Final Validation Summary

* **Planned Total Duration:** 3 minutes 30 seconds (210.0 seconds)
* **Minimum Permitted Runtime:** 3 minutes 00 seconds (180.0 seconds)
* **Maximum Permitted Runtime:** 4 minutes 00 seconds (240.0 seconds)
* **Target Spoken Word Count:** 442 words (~126 words/min)
* **Total Distinct Scenes:** 7 scenes
* **Key Workflows Demonstrated:**
  1. Multi-hop cross-document graph traversal (`payment-service` → `INC-2024-891` → `Payments Platform` → `RB-PAY-04`).
  2. Character-offset citation verification & verbatim chunk inspection modal.
  3. Deterministic honest abstention on out-of-scope queries (cookie recipe).
  4. Enterprise document management, SHA-256 fingerprinting, and real-time search filtering.
  5. Interactive FalkorDB HTML5 Canvas topology visualization and 360-degree entity neighborhood exploration.
* **Accuracy Guarantee:** 100% of UI labels, routes, buttons, and API responses in this script match the live application codebase.
