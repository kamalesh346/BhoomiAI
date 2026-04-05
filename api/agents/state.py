from typing import TypedDict, List, Dict, Any, Optional

class ScoredCrop(TypedDict):
    name: str
    base_score: float
    final_score: float
    suitability_details: Dict[str, Any]
    required_setup: Optional[str]
    setup_impact: float # Potential score increase if setup is done
    subsidies: List[str]
    warnings: List[str]

class AgentState(TypedDict):
    farmer_id: int
    session_id: int
    farmer_profile: Dict[str, Any]
    pest_history: List[Dict[str, Any]]
    past_summary: str
    past_choices: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]
    
    # New state fields for 8-agent system
    candidate_crops: List[ScoredCrop]
    viable_candidates: List[ScoredCrop] # Pre-computed cache (Top 15-20)
    
    user_input: Optional[str]
    selected_option: Optional[str]
    message_id: Optional[str]
    ai_response: Optional[Dict[str, Any]]
    metrics: Optional[List[Dict[str, Any]]]
    rerun_required: Optional[bool]
