from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    farmer_id: int
    session_id: int
    farmer_profile: Dict[str, Any]
    past_summary: str
    past_choices: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]
    user_input: Optional[str]
    selected_option: Optional[str]
    message_id: Optional[str]
    ai_response: Optional[Dict[str, Any]]
    metrics: Optional[List[Dict[str, Any]]]
