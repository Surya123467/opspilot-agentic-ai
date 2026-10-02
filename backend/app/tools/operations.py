from pydantic import BaseModel
class Incident(BaseModel):
    incident_id: str; service: str; severity: str; status: str; summary: str
INCIDENTS = {
    "payments": Incident(incident_id="INC-1042", service="payments-api", severity="SEV-2", status="Investigating", summary="Elevated p95 latency and intermittent timeouts."),
    "authentication": Incident(incident_id="INC-1048", service="authentication", severity="SEV-2", status="Monitoring", summary="Elevated token-service errors after configuration change."),
}
def lookup_incident(service):
    service = service.lower()
    for key, incident in INCIDENTS.items():
        if key in service or service in key: return incident.model_dump()
    return {"incident_id":"UNKNOWN","service":service,"severity":"UNKNOWN","status":"No active incident found","summary":"No matching incident was found in the demo incident system."}
def execute_sensitive_action(action, target, approved=False):
    if not approved: return {"status":"approval_required","action":action,"target":target,"message":"This operation requires explicit human approval."}
    return {"status":"executed","action":action,"target":target,"message":"Demo action executed. No real production system was changed."}
