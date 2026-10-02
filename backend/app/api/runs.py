from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.graph import agent_graph
from app.agents.state import AgentState
from app.db.repository import add_event, create_run, get_events, update_run

router = APIRouter(prefix="/api/runs", tags=["agent-runs"])
RUN_STATES: dict[str, AgentState] = {}

class RunRequest(BaseModel):
    message: str
    thread_id: str | None = None

def _payload(tid, status, result):
    return {"thread_id": tid, "status": status, "response": result.get("final_response"),
            "pending_action": result.get("pending_action"), "plan": result.get("plan", []),
            "research": result.get("research", []), "tool_results": result.get("tool_results", [])}

@router.post("")
def create_agent_run(payload: RunRequest):
    # Every new user prompt is a NEW run. thread_id is reserved for resume/approval flows.
    tid = str(uuid4())
    state: AgentState = {"thread_id": tid, "user_request": payload.message.strip(), "approved": False, "events": []}
    if not state["user_request"]:
        raise HTTPException(400, "Message cannot be empty")
    create_run(tid, state["user_request"]); add_event(tid, "run_started", state["user_request"])
    result = agent_graph.invoke(state); RUN_STATES[tid] = result
    for e in result.get("events", []): add_event(tid, "agent", e)
    status = "approval_required" if result.get("pending_action") and not result.get("approved") else "completed"
    update_run(tid, status, result.get("final_response"))
    return _payload(tid, status, result)

def _resume(tid: str, approved: bool):
    state = RUN_STATES.get(tid)
    if not state: raise HTTPException(404, "Run not found or server state expired")
    if not state.get("pending_action"):
        raise HTTPException(409, "This run has no pending approval")
    if not approved:
        state = {**state, "approved": False, "pending_action": None}
        result = agent_graph.invoke({**state, "rejection_reason": "Human operator rejected the requested action."})
        result["pending_action"] = None
        result["final_response"] = {
            "title": "Action rejected",
            "summary": "The requested consequential action was rejected. No sensitive operation was executed.",
            "incident": next((x["result"] for x in result.get("tool_results", []) if x.get("tool") == "lookup_incident"), None),
            "recommendation": "Continue investigation or submit a new request if a different action is intended.",
            "approval_required": False,
        }
    else:
        state = {**state, "approved": True, "pending_action": None}
        result = agent_graph.invoke(state)
    RUN_STATES[tid] = result
    for e in result.get("events", []): add_event(tid, "agent", e)
    update_run(tid, "completed", result.get("final_response"))
    return _payload(tid, "completed", result)

@router.post("/{thread_id}/approve")
def approve(thread_id: str): return _resume(thread_id, True)

@router.post("/{thread_id}/reject")
def reject(thread_id: str): return _resume(thread_id, False)

@router.get("/{thread_id}/events")
def events(thread_id: str): return {"thread_id": thread_id, "events": get_events(thread_id)}
