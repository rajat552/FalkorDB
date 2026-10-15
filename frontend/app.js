/**
 * Company Brain — Client Application Logic (Vanilla JS ES6)
 * Handles Chat, Evidence Display, Document Management, and Graph Explorer
 * High-DPI Canvas • Responsive • Accessible • Toast Notifications
 */

const API_BASE = ""; // Relative path when served via FastAPI mount

// State
let activeTab = "workspace";
let isQuerying = false;
let renderedGraphNodes = [];
let hoveredNode = null;
let currentCenterData = null;
let currentConnections = [];
let allDocumentsCache = [];

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  fetchHealth();
  loadDocumentsList();
  loadGraphOverview();
  loadGraphEntities();
  exploreSelectedEntity();

  const canvas = document.getElementById("graph-canvas");
  if (canvas) {
    canvas.addEventListener("click", handleCanvasClick);
    canvas.addEventListener("mousemove", handleCanvasMouseMove);
    canvas.addEventListener("mouseleave", handleCanvasMouseLeave);
  }

  window.addEventListener("resize", debounce(() => {
    if (activeTab === "explorer" && currentCenterData) {
      renderTopologyCanvas(currentCenterData, currentConnections);
    }
  }, 150));

  // Poll health and metrics every 15 seconds
  setInterval(fetchHealth, 15000);
});

// --- Tab Switching ---
function switchTab(tabId) {
  activeTab = tabId;
  window.scrollTo({ top: 0, behavior: "instant" });

  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.classList.remove("active");
    tab.setAttribute("aria-selected", "false");
  });
  document.querySelectorAll(".view-panel").forEach(panel => panel.classList.remove("active"));

  const targetTabBtn = document.getElementById(`tab-${tabId}`);
  const targetView = document.getElementById(`view-${tabId}`);

  if (targetTabBtn) {
    targetTabBtn.classList.add("active");
    targetTabBtn.setAttribute("aria-selected", "true");
  }
  if (targetView) targetView.classList.add("active");

  if (tabId === "documents") {
    loadDocumentsList();
  } else if (tabId === "explorer") {
    loadGraphOverview();
    loadGraphEntities();
    exploreSelectedEntity();
  }
}

// --- Health & Status Diagnostics ---
async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("Health check endpoint returned non-200");
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
    const indicator = document.getElementById("db-indicator");
    const statusText = document.getElementById("db-status-text");
    if (indicator) indicator.className = "status-indicator offline";
    if (statusText) statusText.textContent = "API: Disconnected";
  }
}

// --- Toast Notification System ---
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: "✓",
    error: "✕",
    info: "ℹ",
  };

  toast.innerHTML = `
    <span class="toast-icon">${iconMap[type] || "ℹ"}</span>
    <span class="toast-text">${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

// --- Chat & Workspace Logic ---
function scrollChatToBottom() {
  const container = document.getElementById("chat-messages");
  if (!container) return;
  requestAnimationFrame(() => {
    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth"
    });
  });
}

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
  showToast("Chat history cleared.", "info");
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
    showToast(`Query failed: ${err.message}`, "error");
  } finally {
    isQuerying = false;
    sendBtn.disabled = false;
    input.focus();
    scrollChatToBottom();
  }
}

function appendUserMessage(text) {
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.className = "message message-user";
  msgEl.innerHTML = `
    <div class="message-avatar" aria-hidden="true">YOU</div>
    <div class="message-content">
      <div class="message-text">${escapeHtml(text)}</div>
    </div>
  `;
  container.appendChild(msgEl);
  scrollChatToBottom();
}

function appendLoadingMessage() {
  const id = `loading-${Date.now()}`;
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.id = id;
  msgEl.className = "message message-bot";
  msgEl.innerHTML = `
    <div class="message-avatar" aria-hidden="true">CB</div>
    <div class="message-content">
      <div class="message-text" style="color: var(--text-dim); font-style: italic;">
        Traversing knowledge graph and validating evidence passages...
      </div>
    </div>
  `;
  container.appendChild(msgEl);
  scrollChatToBottom();
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
    : `<span class="badge-grounded">✓ Grounded in ${data.citations ? data.citations.length : 0} Verified Sources</span>`;

  msgEl.innerHTML = `
    <div class="message-avatar" aria-hidden="true">CB</div>
    <div class="message-content">
      <div class="message-text">${formatResponseText(data.answer)}</div>
      <div class="message-meta">${badgeHtml}</div>
    </div>
  `;
  container.appendChild(msgEl);
  scrollChatToBottom();
}

function appendErrorMessage(errorText) {
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.className = "message message-bot";
  msgEl.innerHTML = `
    <div class="message-avatar" style="background: var(--accent-rose);" aria-hidden="true">!</div>
    <div class="message-content">
      <div class="message-text" style="border-color: rgba(225, 29, 72, 0.4); background: #FFF5F7;">${escapeHtml(errorText)}</div>
    </div>
  `;
  container.appendChild(msgEl);
  scrollChatToBottom();
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
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `View citation from ${c.filename}`);
    card.onclick = () => openChunkModal(c.chunk_id, c.filename, c.passage);
    card.onkeydown = (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openChunkModal(c.chunk_id, c.filename, c.passage);
      }
    };

    card.innerHTML = `
      <div class="citation-meta">
        <span class="citation-filename">${escapeHtml(c.filename)}</span>
        <span class="citation-chunk-id">${escapeHtml(c.chunk_id || "Chunk #" + (idx + 1))}</span>
      </div>
      <div class="citation-passage">"${escapeHtml(c.passage)}"</div>
      <div class="citation-footer-hint">View full source passage ›</div>
    `;
    citationsList.appendChild(card);
  });

  // Render relationships traversed
  const rels = (data.graph_context && data.graph_context.relationships) || [];
  if (rels.length > 0) {
    graphContext.style.display = "flex";
    relPillsContainer.innerHTML = "";
    rels.slice(0, 8).forEach(r => {
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
    allDocumentsCache = docs;
    badge.textContent = docs.length;

    renderDocumentsTable(docs);
  } catch (err) {
    console.error("Load docs error:", err);
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error loading documents: ${err.message}</td></tr>`;
  }
}

function renderDocumentsTable(docs) {
  const tbody = document.getElementById("docs-tbody");
  if (!tbody) return;

  if (docs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding: 32px 20px;">No documents found. Upload files above or click 'Re-index Synthetic Dataset'.</td></tr>`;
    return;
  }

  tbody.innerHTML = "";
  docs.forEach(d => {
    const tr = document.createElement("tr");
    const dateStr = d.uploaded_at ? new Date(d.uploaded_at).toLocaleString() : "-";
    tr.innerHTML = `
      <td>
        <div style="font-weight: 700; color: var(--text-main);">${escapeHtml(d.filename)}</div>
        <div style="font-size: 0.76rem; color: var(--text-dim); margin-top: 1px;">${escapeHtml(d.title || "")}</div>
      </td>
      <td class="text-mono">${escapeHtml(d.id)}</td>
      <td><span class="badge" style="cursor: pointer;" title="Inspect chunks" onclick="openDocChunks('${d.id}', '${escapeHtml(d.filename)}')">${d.chunk_count} chunks</span></td>
      <td class="text-mono" title="${escapeHtml(d.content_hash)}">${escapeHtml((d.content_hash || "").substring(0, 10))}…</td>
      <td style="font-size: 0.78rem; white-space: nowrap;">${escapeHtml(dateStr)}</td>
      <td class="text-right">
        <button class="btn btn-sm btn-danger" onclick="deleteDoc('${d.id}')" title="Delete document">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function filterDocumentsTable() {
  const searchInput = document.getElementById("docs-search");
  if (!searchInput) return;
  const term = searchInput.value.toLowerCase().trim();

  if (!term) {
    renderDocumentsTable(allDocumentsCache);
    return;
  }

  const filtered = allDocumentsCache.filter(d =>
    (d.filename && d.filename.toLowerCase().includes(term)) ||
    (d.title && d.title.toLowerCase().includes(term)) ||
    (d.id && d.id.toLowerCase().includes(term))
  );

  renderDocumentsTable(filtered);
}

async function openDocChunks(docId, filename) {
  try {
    const res = await fetch(`${API_BASE}/api/documents/${docId}`);
    if (res.ok) {
      const data = await res.json();
      const chunks = data.chunks || [];
      const combined = chunks.map(c => `[Chunk #${c.index} | offset ${c.start_char}-${c.end_char}]\n${c.text}`).join("\n\n---\n\n");
      openChunkModal(docId, `${filename} (${chunks.length} chunks)`, combined);
    }
  } catch (e) {
    showToast(`Could not load chunks: ${e.message}`, "error");
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

  showToast(`Uploading and indexing '${file.name}' into FalkorDB...`, "info");

  try {
    const res = await fetch(`${API_BASE}/api/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (res.status === 409) {
      const err = await res.json();
      showToast(`Duplicate: ${err.detail ? err.detail.message : "File already exists."}`, "error");
      return;
    }
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail ? (err.detail.message || JSON.stringify(err.detail)) : `HTTP ${res.status}`);
    }

    const data = await res.json();
    showToast(`Document '${data.filename}' ingested (${data.total_chunks} chunks).`, "success");
    loadDocumentsList();
    loadGraphEntities();
    loadGraphOverview();
    fetchHealth();
  } catch (err) {
    showToast(`Upload failed: ${err.message}`, "error");
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
    showToast(`Document '${docId}' removed from graph.`, "success");
    loadDocumentsList();
    loadGraphEntities();
    loadGraphOverview();
    fetchHealth();
  } catch (err) {
    showToast(`Failed to delete document: ${err.message}`, "error");
  }
}

async function reindexSampleDataset() {
  if (!confirm("Re-index all synthetic enterprise documents into FalkorDB?")) return;
  showToast("Re-indexing enterprise dataset...", "info");
  try {
    const res = await fetch(`${API_BASE}/api/documents/reindex?force=true`, { method: "POST" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    showToast(`Dataset synchronized: ${data.ingested_count} indexed, ${data.total_documents} active.`, "success");
    loadDocumentsList();
    loadGraphEntities();
    loadGraphOverview();
    fetchHealth();
    exploreSelectedEntity();
  } catch (err) {
    showToast(`Re-index failed: ${err.message}`, "error");
  }
}

// --- Knowledge Graph Explorer Logic ---
async function loadGraphEntities(userTriggered = false) {
  const select = document.getElementById("entity-select");
  if (!select) return;

  try {
    const res = await fetch(`${API_BASE}/api/graph/entities`);
    if (!res.ok) throw new Error("Entities fetch failed");
    const data = await res.json();

    const currentVal = select.value;
    select.innerHTML = "";

    const addGroup = (label, items, getNameFn) => {
      if (items && items.length > 0) {
        const group = document.createElement("optgroup");
        group.label = label;
        items.forEach(item => {
          const name = getNameFn(item);
          const opt = document.createElement("option");
          opt.value = name;
          opt.textContent = name;
          group.appendChild(opt);
        });
        select.appendChild(group);
      }
    };

    addGroup("Services", data.services, s => s.name);
    addGroup("Teams", data.teams, t => t.name);
    addGroup("Incidents", data.incidents, i => i.id);
    addGroup("Employees", data.employees, e => e.name);
    addGroup("Documents", data.documents, d => d.filename);

    if (currentVal && Array.from(select.options).some(o => o.value === currentVal)) {
      select.value = currentVal;
    } else if (select.options.length > 0) {
      select.selectedIndex = 0;
    }

    if (userTriggered) {
      showToast("Graph entities refreshed from FalkorDB.", "success");
      exploreSelectedEntity();
    }
  } catch (err) {
    console.warn("Could not load dynamic entity list:", err);
  }
}

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
  const entityName = select ? select.value : "payment-service";
  if (!entityName) return;

  const centerLabel = document.getElementById("exp-center-label");
  const centerName = document.getElementById("exp-center-name");
  const connCount = document.getElementById("exp-connections-count");
  const connList = document.getElementById("exp-connections-list");

  try {
    const res = await fetch(`${API_BASE}/api/graph/related?entity_name=${encodeURIComponent(entityName)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const centerInfo = data.center || { name: entityName, label: "Entity" };
    centerLabel.textContent = centerInfo.label || "Entity";
    centerName.textContent = centerInfo.name || entityName;

    const connections = data.connections || [];
    connCount.textContent = `${connections.length} connected edges`;

    currentCenterData = centerInfo;
    currentConnections = connections;

    // Render interactive canvas with HiDPI support
    renderTopologyCanvas(centerInfo, connections);

    if (connections.length === 0) {
      connList.innerHTML = `<p class="text-muted" style="grid-column: 1/-1; padding: 12px 0;">No connected relationships found in graph.</p>`;
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

      card.tabIndex = 0;
      card.setAttribute("role", "button");
      card.setAttribute("aria-label", `Inspect related node ${otherName}`);
      card.onclick = () => selectAndExploreNode(otherName);
      card.onkeydown = (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectAndExploreNode(otherName);
        }
      };
      card.title = `Click to inspect ${otherName}`;

      card.innerHTML = `
        <div>
          <span class="badge" style="font-size: 0.68rem;">${escapeHtml(otherLabel || "Node")}</span>
          <div style="font-weight: 700; font-size: 0.88rem; margin-top: 4px; color: var(--text-main);">${escapeHtml(otherName || "")}</div>
        </div>
        <span class="conn-rel">${arrow} ${escapeHtml(c.relationship)}</span>
      `;
      connList.appendChild(card);
    });
  } catch (err) {
    connList.innerHTML = `<p class="text-danger" style="grid-column: 1/-1;">Error: ${err.message}</p>`;
  }
}

function selectAndExploreNode(nodeName) {
  if (!nodeName) return;
  const select = document.getElementById("entity-select");
  if (!select) return;

  let exists = false;
  for (let opt of select.options) {
    if (opt.value === nodeName) {
      select.value = nodeName;
      exists = true;
      break;
    }
  }

  if (!exists) {
    const opt = document.createElement("option");
    opt.value = nodeName;
    opt.textContent = nodeName;
    select.appendChild(opt);
    select.value = nodeName;
  }

  exploreSelectedEntity();
}

// --- Interactive Canvas Visualization (HiDPI Retina Ready) ---
function renderTopologyCanvas(centerData, connections) {
  const canvas = document.getElementById("graph-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // HiDPI Scaling
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const displayWidth = rect.width || canvas.parentElement.clientWidth || 960;
  const displayHeight = 420;

  canvas.width = displayWidth * dpr;
  canvas.height = displayHeight * dpr;
  canvas.style.width = displayWidth + "px";
  canvas.style.height = displayHeight + "px";

  ctx.resetTransform ? ctx.resetTransform() : ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, displayWidth, displayHeight);
  renderedGraphNodes = [];

  const centerX = displayWidth / 2;
  const centerY = displayHeight / 2;

  const colorMap = {
    Service: { fill: "#FFF0E6", stroke: "#FA7B38", text: "#C2410C" },
    Team: { fill: "#E6F8F0", stroke: "#059669", text: "#047857" },
    Incident: { fill: "#FFF0F4", stroke: "#E11D48", text: "#BE123C" },
    Employee: { fill: "#F3E8FF", stroke: "#7C3AED", text: "#6D28D9" },
    Document: { fill: "#E0F2FE", stroke: "#0284C7", text: "#0369A1" },
    Default: { fill: "#F3F4F6", stroke: "#6B7280", text: "#374151" },
  };

  const centerLabel = (centerData && centerData.label) || "Service";
  const centerName = (centerData && centerData.name) || "Center Node";
  const centerColors = colorMap[centerLabel] || colorMap.Default;

  const validConns = [];
  const seenNeighbors = new Set();
  (connections || []).forEach(c => {
    const isOut = c.direction === "outgoing";
    const nName = isOut ? c.target_name : c.source_name;
    const nLabel = isOut ? c.target_label : c.source_label;
    if (nName && !seenNeighbors.has(nName)) {
      seenNeighbors.add(nName);
      validConns.push({
        name: nName,
        label: nLabel || "Entity",
        rel: c.relationship || "RELATED_TO",
        direction: c.direction,
      });
    }
  });

  const totalNeighbors = validConns.length;
  const radiusX = Math.min(displayWidth * 0.38, 360);
  const radiusY = Math.min(displayHeight * 0.36, 140);

  const neighborPositions = validConns.map((conn, idx) => {
    const angle = (idx / Math.max(totalNeighbors, 1)) * 2 * Math.PI - Math.PI / 2;
    const x = centerX + radiusX * Math.cos(angle);
    const y = centerY + radiusY * Math.sin(angle);
    return { ...conn, x, y };
  });

  // 1. Draw Connection Lines
  neighborPositions.forEach(node => {
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(node.x, node.y);
    ctx.strokeStyle = "#FFD0B5";
    ctx.lineWidth = 2.2;
    ctx.stroke();

    const midX = (centerX + node.x) / 2;
    const midY = (centerY + node.y) / 2;
    const relText = `:${node.rel}`;
    ctx.font = "600 10.5px 'JetBrains Mono', monospace";
    const textWidth = ctx.measureText(relText).width;

    ctx.fillStyle = "#FFFFFF";
    ctx.strokeStyle = "#FFEADB";
    ctx.lineWidth = 1;
    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(midX - textWidth / 2 - 7, midY - 10, textWidth + 14, 20, 6);
    } else {
      ctx.rect(midX - textWidth / 2 - 7, midY - 10, textWidth + 14, 20);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#374151";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(relText, midX, midY);
    ctx.restore();
  });

  // 2. Draw Outer Nodes
  neighborPositions.forEach((node, idx) => {
    const nColors = colorMap[node.label] || colorMap.Default;
    const nodeRadius = 28;
    const isHovered = hoveredNode && hoveredNode.name === node.name;

    ctx.save();
    if (isHovered) {
      ctx.shadowColor = nColors.stroke;
      ctx.shadowBlur = 18;
    } else {
      ctx.shadowColor = nColors.stroke + "33";
      ctx.shadowBlur = 10;
    }

    ctx.beginPath();
    ctx.arc(node.x, node.y, isHovered ? nodeRadius + 3 : nodeRadius, 0, 2 * Math.PI);
    ctx.fillStyle = nColors.fill;
    ctx.fill();
    ctx.lineWidth = isHovered ? 3.2 : 2.2;
    ctx.strokeStyle = nColors.stroke;
    ctx.stroke();
    ctx.restore();

    ctx.save();
    ctx.font = "bold 9.5px 'Plus Jakarta Sans', sans-serif";
    ctx.fillStyle = nColors.text;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const shortLabel = (node.label || "").substring(0, 4).toUpperCase();
    ctx.fillText(shortLabel, node.x, node.y);

    ctx.font = "700 11.5px 'Plus Jakarta Sans', sans-serif";
    ctx.fillStyle = "#111827";
    const displayName = node.name.length > 20 ? node.name.substring(0, 18) + "…" : node.name;
    ctx.fillText(displayName, node.x, node.y + nodeRadius + 14);
    ctx.restore();

    renderedGraphNodes.push({
      x: node.x,
      y: node.y,
      radius: nodeRadius + 6,
      name: node.name,
      label: node.label,
    });
  });

  // 3. Draw Center Node
  const centerRadius = 38;
  ctx.save();
  ctx.shadowColor = "rgba(250, 123, 56, 0.4)";
  ctx.shadowBlur = 18;

  ctx.beginPath();
  ctx.arc(centerX, centerY, centerRadius, 0, 2 * Math.PI);
  ctx.fillStyle = centerColors.fill;
  ctx.fill();
  ctx.lineWidth = 3.2;
  ctx.strokeStyle = centerColors.stroke;
  ctx.stroke();
  ctx.restore();

  ctx.save();
  ctx.font = "bold 10px 'Plus Jakarta Sans', sans-serif";
  ctx.fillStyle = centerColors.text;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(centerLabel.toUpperCase(), centerX, centerY - 8);

  ctx.font = "800 12px 'Plus Jakarta Sans', sans-serif";
  ctx.fillStyle = "#111827";
  const displayCenter = centerName.length > 16 ? centerName.substring(0, 14) + "…" : centerName;
  ctx.fillText(displayCenter, centerX, centerY + 10);
  ctx.restore();

  renderedGraphNodes.push({
    x: centerX,
    y: centerY,
    radius: centerRadius,
    name: centerName,
    label: centerLabel,
    isCenter: true,
  });
}

function handleCanvasMouseMove(event) {
  const canvas = document.getElementById("graph-canvas");
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  let foundNode = null;
  for (const node of renderedGraphNodes) {
    if (!node.isCenter) {
      const dx = mouseX - node.x;
      const dy = mouseY - node.y;
      if (Math.sqrt(dx * dx + dy * dy) <= node.radius) {
        foundNode = node;
        break;
      }
    }
  }

  if (foundNode !== hoveredNode) {
    hoveredNode = foundNode;
    canvas.style.cursor = foundNode ? "pointer" : "default";
    if (currentCenterData) {
      renderTopologyCanvas(currentCenterData, currentConnections);
    }
  }
}

function handleCanvasMouseLeave() {
  if (hoveredNode) {
    hoveredNode = null;
    const canvas = document.getElementById("graph-canvas");
    if (canvas) canvas.style.cursor = "default";
    if (currentCenterData) {
      renderTopologyCanvas(currentCenterData, currentConnections);
    }
  }
}

function handleCanvasClick(event) {
  const canvas = document.getElementById("graph-canvas");
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const clickY = event.clientY - rect.top;

  for (const node of renderedGraphNodes) {
    if (!node.isCenter) {
      const dx = clickX - node.x;
      const dy = clickY - node.y;
      if (Math.sqrt(dx * dx + dy * dy) <= node.radius) {
        selectAndExploreNode(node.name);
        break;
      }
    }
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

function closeChunkModal(event) {
  if (event && event.target !== event.currentTarget) return;
  document.getElementById("chunk-modal").style.display = "none";
}

// --- Utility Helpers ---
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
  // Highlight backticked code
  formatted = formatted.replace(/`([^`]+)`/g, "<code style='background: #FFF0E6; color: #C2410C; padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.85em;'>$1</code>");
  // Convert newlines to paragraphs/breaks
  formatted = formatted.replace(/\n\n/g, "<br><br>").replace(/\n/g, "<br>");
  return formatted;
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
