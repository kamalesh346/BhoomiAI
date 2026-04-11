"""
BhoomiAI Agent Graph Configuration
----------------------------------
Defines the stateful workflow for the agricultural advisor using LangGraph.
Manages transitions between entry, recommendation, decision, reasoning, and memory nodes.
"""

from langgraph.graph import StateGraph, END
from api.agents.state import AgentState
from api.agents.nodes import entry_node, recommendation_node, decision_node, reasoning_node, memory_node

def route_from_entry(state: AgentState) -> str:
    """
    Dynamic router for the entry node.
    Determines the next step based on user input, selected options, or constraint changes.
    """
    if state.get("rerun_required"):
        # Triggered when physical constraints (e.g., budget, water) change significantly
        return "recommendation_node"
    
    if state.get("selected_option"):
        # User has picked a crop option (A, B, or C)
        return "decision_node"
    
    elif state.get("user_input"):
        # Ongoing consultation or general inquiry
        return "reasoning_node"
    
    else:
        # Default fallback to initial recommendations
        return "recommendation_node"

def build_graph():
    """
    Assembles the LangGraph workflow.
    Configures nodes, entry points, and conditional/fixed edges.
    """
    workflow = StateGraph(AgentState)
    
    # 1. Register Nodes
    workflow.add_node("entry_node", entry_node)                # Data fetching & state initialization
    workflow.add_node("recommendation_node", recommendation_node) # Generates top 3 crop options
    workflow.add_node("decision_node", decision_node)          # Persists user choice and generates metrics
    workflow.add_node("reasoning_node", reasoning_node)        # Main LLM logic for consultation/plans
    workflow.add_node("memory_node", memory_node)              # Handles state summarization & cleanup
    
    # 2. Define Control Flow
    workflow.set_entry_point("entry_node")
    
    workflow.add_conditional_edges(
        "entry_node",
        route_from_entry,
        {
            "recommendation_node": "recommendation_node",
            "decision_node": "decision_node",
            "reasoning_node": "reasoning_node"
        }
    )
    
    # Define terminal paths and transitions
    workflow.add_edge("recommendation_node", END)
    workflow.add_edge("decision_node", "reasoning_node")
    workflow.add_edge("reasoning_node", "memory_node")
    workflow.add_edge("memory_node", END)
    
    return workflow.compile()
    
# Exported graph instance for use in services
agent_graph = build_graph()
