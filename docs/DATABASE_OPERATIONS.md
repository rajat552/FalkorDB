# FalkorDB Database Operations & Troubleshooting Guide

**Service:** FalkorDB Graph Database  
**Default Port:** 6379 (Redis / Cypher protocol), 3000 (FalkorDB Studio Browser)  

---

## 1. Quick Startup & Configuration

### Option A: Direct Docker Run (Current Active Mode)
FalkorDB is run with port mappings:
```powershell
docker run -p 6379:6379 -p 3000:3000 -it --rm -v ${PWD}/data/falkordb:/data falkordb/falkordb:latest
```

### Option B: Background Daemon (Production / Long Running)
```powershell
docker run -d --name company_brain_falkordb -p 6379:6379 -p 3000:3000 --restart unless-stopped -v ${PWD}/data/falkordb:/data falkordb/falkordb:latest
```

---

## 2. Environment Variables

Store these in `.env`:

```env
FALKORDB_HOST=127.0.0.1
FALKORDB_PORT=6379
FALKORDB_GRAPH=company_brain
FALKORDB_PASSWORD=
```

---

## 3. Operational Diagnostics & Commands

### Checking Container Status
```powershell
docker ps --filter "ancestor=falkordb/falkordb:latest"
```

### Inspecting Database Logs
```powershell
docker logs beautiful_shamir --tail 50
```

### Testing Connection via Application
```powershell
python -c "from app.db import check_health; print(check_health())"
```

Expected healthy output:
```json
{"connected": true, "host": "127.0.0.1", "port": 6379, "graph_name": "company_brain", "latency_ms": 5.25, "total_nodes": 0, "total_edges": 0, "error": null}
```

---

## 4. Troubleshooting

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **`ConnectionRefusedError: [WinError 10061]`** | FalkorDB container is stopped or port 6379 blocked | Run `docker ps` to verify container is running; start container with `docker run -p 6379:6379 ...`. |
| **`Index already exists`** | Cypher schema index was already created | Normal behavior; `app.db.init_schema()` suppresses and logs as debug. |
| **Web UI inaccessible at `localhost:3000`** | Port 3000 not forwarded in Docker | Ensure `-p 3000:3000` is included in the `docker run` command. |
| **Container restarts or data missing** | Container restarted without volume | Mount persistent volume `-v ${PWD}/data/falkordb:/data` in `docker run`. |
