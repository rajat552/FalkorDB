# IT Helpdesk & Incident Escalation Policy

## 1. Severity Levels & SLA Response Targets

| Severity | Definition | Target First Response | Target Mitigation SLA | Communication Cadence |
| :--- | :--- | :--- | :--- | :--- |
| **Sev-1** | Critical outage affecting core customer revenue or authentication. | **15 minutes** | **1 hour** | Every 15 minutes |
| **Sev-2** | Degraded functionality or non-critical service disruption. | **30 minutes** | **4 hours** | Hourly |
| **Sev-3** | Internal tooling or minor cosmetic glitch with workaround. | **4 hours** | **24 hours** | Daily update |

## 2. Escalation Workflow
1. **Declaration:** Helpdesk or automated alerting detects failure.
2. **On-Call Paging:** PagerDuty immediately pages primary on-call engineer for the owning team.
3. **Escalation Trigger:** If unacknowledged within 15 minutes for Sev-1, incident automatically escalates to Team Lead.
4. **War Room:** Incident Commander opens dedicated Slack channel `#incident-<id>` and Google Meet war room.
5. **Postmortem Requirement:** Any Sev-1 or Sev-2 incident requires a published postmortem and associated runbook updates within 48 hours of resolution.
