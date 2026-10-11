# Team Ownership & Staff Directory

## 1. Engineering Teams Overview

### Payments Platform Team (`team-payments`)
- **Mission:** High-reliability payment processing, transaction settlements, checkout flow.
- **Team Lead:** Elena Rostova (`elena.rostova@company.com`)
- **Senior SRE:** Marcus Vance (`marcus.vance@company.com`)
- **Backend Engineer:** David Kim (`david.kim@company.com`)
- **Slack:** `#payments-platform`
- **Owned Services:** `payment-service`, `refund-worker`, `settlement-ledger`

### Security Core Team (`team-security`)
- **Mission:** Authentication, authorization, secrets management, encryption.
- **Team Lead:** Sarah Chen (`sarah.chen@company.com`)
- **Security Engineer:** Alex Rivera (`alex.rivera@company.com`)
- **Identity Architect:** Maya Lin (`maya.lin@company.com`)
- **Slack:** `#security-core`
- **Owned Services:** `auth-service`, `kms-proxy`, `vault-agent`

### Orders & Logistics Squad (`team-orders`)
- **Mission:** Order lifecycle, inventory management, fulfillment dispatch.
- **Team Lead:** Priya Patel (`priya.patel@company.com`)
- **Fullstack Engineer:** Carlos Mendez (`carlos.mendez@company.com`)
- **Slack:** `#orders-engineering`
- **Owned Services:** `order-processing-service`, `inventory-sync`

## 2. Service-to-Team Ownership Matrix

| Service Name | Tier | Primary Owning Team | Lead Contact | Escalation Policy |
| :--- | :--- | :--- | :--- | :--- |
| `payment-service` | Tier-1 | Payments Platform | Elena Rostova | `PD-PAYMENTS-TIER1` |
| `auth-service` | Tier-1 | Security Core | Sarah Chen | `PD-SECURITY-TIER1` |
| `order-processing-service` | Tier-1 | Orders Squad | Priya Patel | `PD-ORDERS-TIER1` |
| `notification-hub` | Tier-2 | Platform Ops | Marcus Vance | `PD-PLATFORM-TIER2` |
