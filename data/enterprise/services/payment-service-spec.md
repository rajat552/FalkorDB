# Service Specification: Payment Gateway Service (payment-service)

## 1. Overview
The `payment-service` is a Tier-1 critical microservice responsible for processing credit card charges, refunds, merchant settlements, and webhook callbacks.

- **Service ID:** `srv-payment-01`
- **Service Name:** `payment-service`
- **Tier:** Tier-1 (Mission Critical)
- **Repository:** `github.com/company/payment-service`
- **Primary Runtime:** Python 3.12 / FastAPI / AsyncIO
- **Database:** PostgreSQL (Transactions), FalkorDB (Fraud graph & relationship indexing)
- **Message Broker:** Kafka topic `payments.events.v1`

## 2. Ownership & Team Contacts
- **Owning Team:** Payments Platform (`team-payments`)
- **Team Lead:** Elena Rostova (`elena.rostova@company.com`)
- **Primary On-Call:** Marcus Vance (`marcus.vance@company.com`)
- **Slack Channel:** `#payments-platform`
- **PagerDuty Escalation Policy:** `PD-PAYMENTS-TIER1`

## 3. Upstream & Downstream Dependencies
- **Upstream Callers:** Web Checkout Frontend, Mobile API Gateway, Subscription Worker.
- **Downstream Internal Services:**
  - `auth-service`: Validates user authentication tokens and merchant API keys.
  - `notification-hub`: Dispatches asynchronous payment confirmation emails and SMS.
- **Downstream External Providers:** Stripe Core API, Adyen Gateway.

## 4. Operational Runbooks
- **Outage Recovery & Pool Reset:** `RB-PAY-04` (Payment Gateway Recovery & Pool Reset)
- **Provider Failover (Stripe to Adyen):** `RB-PAY-02`
- **Database Failover Procedure:** `RB-DB-09`
