# Technical Runbook: RB-PAY-04 (Payment Gateway Recovery & Pool Reset)

## 1. Runbook Summary
- **Runbook ID:** `RB-PAY-04`
- **Title:** Payment Gateway Recovery and Connection Pool Reset
- **Target Service:** `payment-service`
- **Owning Team:** Payments Platform (`team-payments`)
- **Author:** Marcus Vance (`marcus.vance@company.com`)
- **Last Verified:** October 2024

## 2. Trigger Conditions
Use this runbook when:
- `payment-service` reports p99 latency > 2,000ms across 3 consecutive evaluation windows.
- Influx of HTTP 504 errors on endpoint `/api/v2/charge`.
- Prometheus alert `PaymentDBPoolExhaustion` fires.

## 3. Step-by-Step Recovery Procedure

### Step 1: Drain In-Flight Stalled Requests
Issue a graceful queue drain to release locked database transactions:
```bash
kubectl exec -it deployment/payment-service-api -n prod -- python -m scripts.drain_queue --force
```

### Step 2: Reset Database Connection Pool Quotas
Increase connection pool capacity and reset stuck idle connections:
```bash
kubectl set env deployment/payment-service-api -n prod DB_POOL_MAX_SIZE=150 DB_POOL_TIMEOUT=5
```

### Step 3: Trigger Rolling Restart of Worker Pods
Restart application pods to apply new pool allocations without downtime:
```bash
kubectl rollout restart deployment/payment-service-api -n prod
kubectl rollout status deployment/payment-service-api -n prod --timeout=180s
```

### Step 4: Verification & Smoke Test
Run automated health check probe:
```bash
curl -X GET https://payment-service.internal/health/live
```
Confirm `database_pool_active` drops below 40% and transaction error rate drops to 0.00%.
