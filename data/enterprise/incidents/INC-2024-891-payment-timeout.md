# Incident Postmortem: INC-2024-891 (payment-service Outage)

## 1. Incident Metadata
- **Incident ID:** `INC-2024-891`
- **Title:** HTTP 504 Gateway Timeouts on Payment Checkout API
- **Severity:** Sev-1 (Critical Revenue Impact)
- **Status:** Resolved
- **Impacted Service:** `payment-service`
- **Incident Start Time:** 2024-10-10T14:15:00Z
- **Incident Resolved Time:** 2024-10-10T15:02:00Z
- **Duration:** 47 minutes
- **Impacted Customers:** Approximately 3,420 checkout attempts failed with HTTP 504.

## 2. Team Ownership & Responders
- **Resolving Team:** Payments Platform (`team-payments`)
- **Incident Commander:** Marcus Vance (Senior SRE)
- **Lead Responding Engineer:** Elena Rostova (Payments Platform Lead)
- **Communications Lead:** David Kim (Platform Engineer)

## 3. Root Cause Analysis
During high traffic following a promotional push, external payment gateway latency climbed from 180ms to 4,200ms. The `payment-service` client-side retry policy lacked exponential backoff with jitter, triggering a retry storm. All 80 connections in the database connection pool were tied up waiting for synchronous locking transactions, causing connection pool starvation. Incoming checkout requests queued indefinitely until timing out with HTTP 504.

## 4. Resolution & Mitigation
1. The Payments Platform team declared a Sev-1 incident at 14:22Z.
2. The team executed the recovery steps documented in runbook `RB-PAY-04` (Payment Gateway Recovery & Pool Reset).
3. Temporary connection pool limits were increased to 150 connections.
4. Downstream request queues were drained, and retry backoff limits were patched.
5. Service traffic returned to normal at 15:02Z with p99 latency stabilizing below 120ms.

## 5. Associated Runbooks & Documentation
- **Runbook Used for Fix:** `RB-PAY-04` (`RB-PAY-04-payment-recovery.md`)
- **Service Architecture:** `payment-service-spec.md`
- **Follow-up Jira Ticket:** `PAY-4891` (Implement circuit breaker in payments adapter)
