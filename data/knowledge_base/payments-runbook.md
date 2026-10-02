# Payments API Latency Runbook

## Symptoms
Increased p95 latency, elevated timeout rates, and downstream queue growth.

## Investigation
1. Check the active incident.
2. Inspect recent deployment history.
3. Check dependency health.
4. Compare latency across regions.
5. Review database connection saturation.

## Remediation
If the current deployment is strongly correlated with the incident, rollback may be considered. A service restart may be appropriate when the service is unhealthy and the restart is explicitly approved.

## Safety
Do not restart or rollback production services automatically without human approval.
