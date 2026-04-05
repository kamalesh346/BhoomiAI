from langgraph.graph import StateGraph, END
from api.agents.state import AgentState
from api.agents.nodes import entry_node, recommendation_node, decision_node, reasoning_node, memory_node

def route_from_entry(state: AgentState) -> str:
    if state.get("selected_option"):
        return "decision_node"
    elif state.get("user_input"):
        return "reasoning_node"
    else:
        return "recommendation_node"

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("entry_node", entry_node)
    workflow.add_node("recommendation_node", recommendation_node)
    workflow.add_node("decision_node", decision_node)
    workflow.add_node("reasoning_node", reasoning_node)
    workflow.add_node("memory_node", memory_node)
    
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
    
    workflow.add_edge("recommendation_node", END)
    workflow.add_edge("decision_node", "reasoning_node")
    workflow.add_edge("reasoning_node", "memory_node")
    workflow.add_edge("memory_node", END)
    
    return workflow.compile()
    
agent_graph = build_graph()
