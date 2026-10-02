import json
from langgraph.graph import END, StateGraph
from app.agents.state import AgentState
from app.core.config import settings
from app.rag.retriever import retriever
from app.tools.operations import execute_sensitive_action, lookup_incident
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

def _llm():
    if settings.mock_mode or not settings.openai_api_key or ChatOpenAI is None: return None
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0)

def planner(state):
    llm = _llm()
    if llm:
        prompt = f"You are an enterprise operations planning agent. Break this request into 3-5 concise steps. Return JSON array only. Request: {state['user_request']}"
        try: plan = json.loads(llm.invoke(prompt).content)
        except Exception: plan = ["Identify service", "Retrieve runbook", "Inspect incident", "Review evidence", "Recommend next steps"]
    else: plan = ["Identify the affected service and incident context", "Retrieve the relevant operational runbook", "Inspect the current incident status", "Review evidence and determine safe next steps"]
    return {"plan": plan, "events": ["Planner created an execution plan."]}

def researcher(state):
    docs = retriever.search(state["user_request"])
    return {"research": docs, "events": [f"RAG retrieved {len(docs)} knowledge-base chunk(s) using vector retrieval." if any(d.get("retrieval") == "pgvector-cosine" for d in docs) else f"RAG retrieved {len(docs)} knowledge-base document(s) using fallback retrieval."]}

def tool_executor(state):
    request = state["user_request"].lower()
    if "payment" in request:
        service = "payments"
    elif "auth" in request or "login" in request or "token" in request:
        service = "authentication"
    else:
        return {
            "tool_results": [{"tool": "lookup_incident", "result": {
                "found": False,
                "message": "Unsupported or unidentified service. Supported demo services: payments, authentication."
            }}],
            "events": ["Tool executor could not safely identify a supported service; no default incident was selected."]
        }
    incident = lookup_incident(service)
    results = [{"tool":"lookup_incident","result":incident}]
    sensitive = None
    if any(word in request for word in ["restart", "rollback", "execute", "change production"]):
        sensitive = {"action": "restart_service" if "restart" in request else "production_change", "target": incident["service"]}
    if sensitive and not state.get("approved", False):
        return {"tool_results": results, "pending_action": sensitive, "events": ["Tool execution paused because human approval is required."]}
    if sensitive:
        results.append({"tool": sensitive["action"], "result": execute_sensitive_action(sensitive["action"], sensitive["target"], True)})
    return {"tool_results": results, "events": ["Tool executor completed approved operations."]}

def review(state):
    issues=[]
    if not state.get("research"): issues.append("No runbook evidence was retrieved.")
    if not state.get("tool_results"): issues.append("No operational tool result was available.")
    return {"review":{"approved_for_response":not issues,"issues":issues,"evidence_count":len(state.get("research",[]))+len(state.get("tool_results",[]))},"events":["Reviewer checked evidence and execution state."]}

def finalizer(state):
    incident = next((x["result"] for x in state.get("tool_results",[]) if x["tool"]=="lookup_incident"), None)
    if state.get("rejection_reason"):
        response={"title":"Action rejected","summary":"The requested consequential action was rejected. No sensitive operation was executed.","incident":incident,"recommendation":"Continue investigation or submit a new request if a different action is intended.","approval_required":False}
    elif state.get("pending_action") and not state.get("approved"):
        response={"title":"Approval required","summary":"The workflow found a potentially consequential action and paused before execution.","incident":incident,"recommendation":f"Approve '{state['pending_action']['action']}' for {state['pending_action']['target']} only if you intend to execute the demo operation.","approval_required":True}
    else:
        if incident and incident.get("found") is False:
            response={"title":"Service not identified","summary":incident["message"],"incident":None,"recommendation":"Specify a supported service such as payments or authentication so the agent can retrieve the correct incident and runbook.","approval_required":False}
        else:
            response={"title":"Investigation complete","summary":f"Current incident: {incident['incident_id']} — {incident['summary']}" if incident else "The investigation completed.","incident":incident,"recommendation":"Use the runbook guidance and validate deployment/dependency signals before remediation. Keep consequential production actions behind explicit approval.","approval_required":False}
    return {"final_response":response,"events":["Finalizer produced the structured response."]}

def route_after_tools(state): return "finalizer" if state.get("pending_action") and not state.get("approved") else "review"
def build_graph():
    g=StateGraph(AgentState)
    for name, fn in [("planner",planner),("researcher",researcher),("tool_executor",tool_executor),("review",review),("finalizer",finalizer)]: g.add_node(name,fn)
    g.set_entry_point("planner"); g.add_edge("planner","researcher"); g.add_edge("researcher","tool_executor")
    g.add_conditional_edges("tool_executor",route_after_tools,{"review":"review","finalizer":"finalizer"})
    g.add_edge("review","finalizer"); g.add_edge("finalizer",END)
    return g.compile()
agent_graph=build_graph()
