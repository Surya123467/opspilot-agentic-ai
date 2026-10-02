from typing import Any, TypedDict

class AgentState(TypedDict, total=False):
    thread_id: str
    user_request: str
    plan: list[str]
    research: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    review: dict[str, Any]
    final_response: dict[str, Any]
    pending_action: dict[str, Any] | None
    approved: bool
    events: list[str]
    rejection_reason: str
