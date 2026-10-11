# Service Specification: Authentication & Identity Service (auth-service)

## 1. Overview
The `auth-service` manages employee and customer identity, OAuth2 / OIDC token issuance, API key validation, and role-based access control (RBAC).

- **Service ID:** `srv-auth-02`
- **Service Name:** `auth-service`
- **Tier:** Tier-1 (Security Critical)
- **Repository:** `github.com/company/auth-service`
- **Primary Runtime:** Go 1.22 / Gin / gRPC
- **Database:** PostgreSQL (User records), Redis Cluster (Session cache)

## 2. Ownership & Team Contacts
- **Owning Team:** Security Core (`team-security`)
- **Team Lead:** Sarah Chen (`sarah.chen@company.com`)
- **Senior Security Engineer:** Alex Rivera (`alex.rivera@company.com`)
- **Slack Channel:** `#security-core`
- **On-Call Contact:** `sec-oncall@company.com`

## 3. Dependent Services
All internal microservices depend on `auth-service` for token validation:
- `payment-service`: Validates merchant API tokens.
- `order-processing-service`: Validates customer checkout JWT bearer tokens.
- `notification-hub`: Verifies internal dispatch credentials.

## 4. Runbooks & Procedures
- **Token Invalidation Runbook:** `RB-AUTH-02` (Emergency Session Revocation and Token Flush)
- **Key Rotation Procedure:** `RB-SEC-08`
