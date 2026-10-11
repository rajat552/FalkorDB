/**
 * Company Brain — Client Application Logic (Vanilla JS ES6)
 * Handles Chat, Evidence Display, Document Management, and Graph Explorer
 */

const API_BASE = ""; // Relative path when served via FastAPI mount

// State
let activeTab = "workspace";
let isQuerying = false;

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  fetchHealth();
  loadDocumentsList();
  loadGraphOverview();
  exploreSelectedEntity();

  // Poll health and metrics every 15 seconds
  setInterval(fetchHealth, 15000);
});

// --- Tab Switching ---
function switchTab(tabId) {
  activeTab = tabId;
  document.querySelectorAll(".nav-tab").forEach(tab => tab.classList.remove("active"));
  document.querySelectorAll(".view-panel").forEach(panel => panel.classList.remove("active"));

  const targetTabBtn = document.getElementById(`tab-${tabId}`);
  const targetView = document.getElementById(`view-${tabId}`);

  if (targetTabBtn) targetTabBtn.classList.add("active");
  if (targetView) targetView.classList.add("active");

  if (tabId === "documents") {
    loadDocumentsList();
  } else if (tabId === "explorer") {
    loadGraphOverview();
    exploreSelectedEntity();
  }
}

// --- Health & Status ---
async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("Health check failed");
    const data = await res.json();

    const indicator = document.getElementById("db-indicator");
    const statusText = document.getElementById("db-status-text");
    const nodesSpan = document.getElementById("metric-nodes");
    const edgesSpan = document.getElementById("metric-edges");

    if (data.database && data.database.connected) {
      indicator.className = "status-indicator live";
      statusText.textContent = `FalkorDB: Connected (${data.database.latency_ms}ms)`;
      nodesSpan.textContent = data.database.total_nodes;
      edgesSpan.textContent = data.database.total_edges;
    } else {
      indicator.className = "status-indicator offline";
      statusText.textContent = "FalkorDB: Offline";
    }
  } catch (err) {
    console.error("Health check error:", err);
    const indicator = document.getElementById("db-indicator");
    const statusText = document.getElementById("db-status-text");
    if (indicator) indicator.className = "status-indicator offline";
    if (statusText) statusText.textContent = "API: Disconnected";
  }
}

// --- Chat & Workspace Logic ---
function runSuggestedQuery(btn) {
  const query = btn.textContent.trim();
  const input = document.getElementById("chat-input");
  input.value = query;
  handleChatSubmit(new Event("submit"));
}

function clearChat() {
  const container = document.getElementById("chat-messages");
  container.innerHTML = `
    <div class="message message-bot">
      <div class="message-avatar">CB</div>
      <div class="message-content">
        <div class="message-text">
          History cleared. Ask any question to retrieve grounded facts with verified source citations.
        </div>
      </div>
    </div>
  `;
  document.getElementById("active-citations-list").innerHTML = "";
  document.getElementById("active-graph-context").style.display = "none";
  document.getElementById("empty-evidence-state").style.display = "flex";
  document.getElementById("evidence-counter").textContent = "0 citations";
}

async function handleChatSubmit(event) {
  if (event) event.preventDefault();
  const input = document.getElementById("chat-input");
  const query = (input.value || "").trim();
  if (!query || isQuerying) return;

  isQuerying = true;
  const sendBtn = document.getElementById("btn-send");
  sendBtn.disabled = true;

  // Append user message
  appendUserMessage(query);
  input.value = "";

  // Append temporary loading message
  const loadingMsgId = appendLoadingMessage();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const data = await res.json();
    removeLoadingMessage(loadingMsgId);
    appendBotResponse(data);
    renderEvidence(data);
  } catch (err) {
    removeLoadingMessage(loadingMsgId);
    appendErrorMessage(`Error executing query: ${err.message}. Please verify FalkorDB connection.`);
  } finally {
    isQuerying = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

function appendUserMessage(text) {
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.className = "message message-user";
  msgEl.innerHTML = `
    <div class="message-avatar">YOU</div>
    <div class="message-content">
      <div class="message-text">${escapeHtml(text)}</div>
    </div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

function appendLoadingMessage() {
  const id = `loading-${Date.now()}`;
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.id = id;
  msgEl.className = "message message-bot";
  msgEl.innerHTML = `
    <div class="message-avatar">CB</div>
    <div class="message-content">
      <div class="message-text" style="color: var(--text-muted); font-style: italic;">
        Traversing knowledge graph and validating evidence passages...
      </div>
    </div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeLoadingMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendBotResponse(data) {
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.className = "message message-bot";

  const isAbstain = data.insufficient_evidence;
  const badgeHtml = isAbstain
    ? `<span class="badge-abstain">Honest Abstention (Insufficient Evidence)</span>`
    : `<span class="badge-grounded">Grounded in ${data.citations.length} Verified Sources</span>`;

  msgEl.innerHTML = `
    <div class="message-avatar">CB</div>
    <div class="message-content">
      <div class="message-text">${formatResponseText(data.answer)}</div>
      <div class="message-meta">${badgeHtml}</div>
    </div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

function appendErrorMessage(errorText) {
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.className = "message message-bot";
  msgEl.innerHTML = `
    <div class="message-avatar" style="background: var(--accent-rose);">!</div>
    <div class="message-content">
      <div class="message-text" style="border-color: rgba(244, 63, 94, 0.4);">${escapeHtml(errorText)}</div>
    </div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

// --- Evidence & Citations Panel Rendering ---
function renderEvidence(data) {
  const citations = data.citations || [];
  const emptyState = document.getElementById("empty-evidence-state");
  const citationsList = document.getElementById("active-citations-list");
  const counter = document.getElementById("evidence-counter");
  const graphContext = document.getElementById("active-graph-context");
  const relPillsContainer = document.getElementById("relationship-pills");

  counter.textContent = `${citations.length} citation${citations.length === 1 ? "" : "s"}`;

  if (citations.length === 0) {
    emptyState.style.display = "flex";
    emptyState.querySelector("p").textContent = data.insufficient_evidence
      ? "No supporting documents or relationships matched this inquiry. The engine abstained to prevent hallucination."
      : "No direct citations found for this answer.";
    citationsList.innerHTML = "";
    graphContext.style.display = "none";
    return;
  }

  emptyState.style.display = "none";
  citationsList.innerHTML = "";

  citations.forEach((c, idx) => {
    const card = document.createElement("div");
    card.className = "citation-card";
    card.onclick = () => openChunkModal(c.chunk_id, c.filename, c.passage);
    card.innerHTML = `
      <div class="citation-meta">
        <span class="citation-filename">${escapeHtml(c.filename)}</span>
        <span class="citation-chunk-id">${escapeHtml(c.chunk_id || "Chunk #" + (idx + 1))}</span>
      </div>
      <div class="citation-passage">"${escapeHtml(c.passage)}"</div>
    `;
    citationsList.appendChild(card);
  });

  // Render relationships traversed
  const rels = (data.graph_context && data.graph_context.relationships) || [];
  if (rels.length > 0) {
    graphContext.style.display = "flex";
    relPillsContainer.innerHTML = "";
    rels.slice(0, 6).forEach(r => {
      const pill = document.createElement("div");
      pill.className = "rel-pill";
      pill.innerHTML = `(${escapeHtml(r.from)}) <span class="rel-type">-[${escapeHtml(r.type)}]-></span> (${escapeHtml(r.to)})`;
      relPillsContainer.appendChild(pill);
    });
  } else {
    graphContext.style.display = "none";
  }
}

// --- Document Management Logic ---
async function loadDocumentsList() {
  const tbody = document.getElementById("docs-tbody");
  const badge = document.getElementById("docs-count-badge");
  try {
    const res = await fetch(`${API_BASE}/api/documents`);
    if (!res.ok) throw new Error("Failed to load documents");
    const data = await res.json();
    const docs = data.documents || [];
    badge.textContent = docs.length;

    if (docs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No documents ingested yet. Upload files or click 'Re-index Synthetic Dataset'.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    docs.forEach(d => {
      const tr = document.createElement("tr");
      const dateStr = d.uploaded_at ? new Date(d.uploaded_at).toLocaleString() : "-";
      tr.innerHTML = `
        <td>
          <div style="font-weight: 600; color: #fff;">${escapeHtml(d.filename)}</div>
          <div style="font-size: 0.75rem; color: var(--text-dim);">${escapeHtml(d.title || "")}</div>
        </td>
        <td class="text-mono">${escapeHtml(d.id)}</td>
        <td><span class="badge">${d.chunk_count} chunks</span></td>
        <td class="text-mono" title="${escapeHtml(d.content_hash)}">${escapeHtml(d.content_hash.substring(0, 10))}...</td>
        <td style="font-size: 0.78rem;">${escapeHtml(dateStr)}</td>
        <td class="text-right">
          <button class="btn btn-sm btn-secondary" onclick="deleteDoc('${d.id}')">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Load docs error:", err);
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error loading documents: ${err.message}</td></tr>`;
  }
}

async function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) uploadFile(file);
}

function handleDragOver(e) {
  e.preventDefault();
  document.getElementById("upload-dropzone").classList.add("dragover");
}

function handleDragLeave(e) {
  e.preventDefault();
  document.getElementById("upload-dropzone").classList.remove("dragover");
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById("upload-dropzone").classList.remove("dragover");
  if (e.dataTransfer.files.length > 0) {
    uploadFile(e.dataTransfer.files[0]);
  }
}

async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/api/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (res.status === 409) {
      const err = await res.json();
      alert(`Duplicate Document: ${err.detail.message}`);
      return;
    }
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail ? err.detail.message : `HTTP ${res.status}`);
    }

    const data = await res.json();
    alert(`Document '${data.filename}' ingested successfully (${data.total_chunks} chunks).`);
    loadDocumentsList();
    fetchHealth();
  } catch (err) {
    alert(`Upload failed: ${err.message}`);
  }
}

async function deleteDoc(docId) {
  if (!confirm(`Are you sure you want to delete document '${docId}' and its associated chunks from FalkorDB?`)) {
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/api/documents/${docId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    loadDocumentsList();
    fetchHealth();
  } catch (err) {
    alert(`Failed to delete document: ${err.message}`);
  }
}

async function reindexSampleDataset() {
  if (!confirm("Re-index all 6 synthetic enterprise documents into FalkorDB?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/documents/reindex`, { method: "POST" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    alert(`Synthetic dataset indexed successfully (${data.ingested_count} documents).`);
    loadDocumentsList();
    fetchHealth();
  } catch (err) {
    alert(`Re-index failed: ${err.message}`);
  }
}

// --- Knowledge Graph Explorer Logic ---
async function loadGraphOverview() {
  try {
    const res = await fetch(`${API_BASE}/api/graph/overview`);
    if (!res.ok) throw new Error("Overview query failed");
    const data = await res.json();
    const nc = data.node_counts || {};

    document.getElementById("m-services").textContent = nc["Service"] || 0;
    document.getElementById("m-teams").textContent = nc["Team"] || 0;
    document.getElementById("m-incidents").textContent = nc["Incident"] || 0;
    document.getElementById("m-employees").textContent = nc["Employee"] || 0;
    document.getElementById("m-documents").textContent = nc["Document"] || 0;
    document.getElementById("m-chunks").textContent = nc["EvidenceChunk"] || 0;
  } catch (err) {
    console.error("Overview error:", err);
  }
}

async function exploreSelectedEntity() {
  const select = document.getElementById("entity-select");
  const entityName = select.value;

  const centerLabel = document.getElementById("exp-center-label");
  const centerName = document.getElementById("exp-center-name");
  const connCount = document.getElementById("exp-connections-count");
  const connList = document.getElementById("exp-connections-list");

  try {
    const res = await fetch(`${API_BASE}/api/graph/related?entity_name=${encodeURIComponent(entityName)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    centerLabel.textContent = (data.center && data.center.label) || "Entity";
    centerName.textContent = (data.center && data.center.name) || entityName;

    const connections = data.connections || [];
    connCount.textContent = `${connections.length} connected edges`;

    if (connections.length === 0) {
      connList.innerHTML = `<p class="text-muted" style="grid-column: 1/-1;">No connected relationships found in graph.</p>`;
      return;
    }

    connList.innerHTML = "";
    connections.forEach(c => {
      const card = document.createElement("div");
      card.className = "conn-card";
      const isOut = c.direction === "outgoing";
      const otherLabel = isOut ? c.target_label : c.source_label;
      const otherName = isOut ? c.target_name : c.source_name;
      const arrow = isOut ? "→" : "←";

      card.innerHTML = `
        <div>
          <span class="badge" style="font-size: 0.68rem;">${escapeHtml(otherLabel || "Node")}</span>
          <div style="font-weight: 600; font-size: 0.88rem; margin-top: 4px;">${escapeHtml(otherName || "")}</div>
        </div>
        <span class="conn-rel">${arrow} ${escapeHtml(c.relationship)}</span>
      `;
      connList.appendChild(card);
    });
  } catch (err) {
    connList.innerHTML = `<p class="text-danger" style="grid-column: 1/-1;">Error: ${err.message}</p>`;
  }
}

// --- Chunk Viewer Modal ---
async function openChunkModal(chunkId, filename, snippet) {
  const modal = document.getElementById("chunk-modal");
  const idEl = document.getElementById("modal-chunk-id");
  const docEl = document.getElementById("modal-chunk-doc");
  const textEl = document.getElementById("modal-chunk-text");

  idEl.textContent = chunkId || "Evidence Chunk";
  docEl.textContent = filename || "Source Document";
  textEl.textContent = "Loading full chunk passage...";
  modal.style.display = "flex";

  if (chunkId) {
    try {
      const res = await fetch(`${API_BASE}/api/sources/${encodeURIComponent(chunkId)}`);
      if (res.ok) {
        const data = await res.json();
        textEl.textContent = data.text;
        return;
      }
    } catch (e) {
      console.warn("Could not fetch full chunk:", e);
    }
  }

  textEl.textContent = snippet || "Passage content unavailable.";
}

function closeChunkModal() {
  document.getElementById("chunk-modal").style.display = "none";
}

// --- Helpers ---
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatResponseText(text) {
  if (!text) return "";
  let formatted = escapeHtml(text);
  // Highlight bold text
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  // Convert newlines to paragraphs/breaks
  formatted = formatted.replace(/\n\n/g, "<br><br>").replace(/\n/g, "<br>");
  return formatted;
}
