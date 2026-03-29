import os
from typing import Dict, List, Any, TypedDict, Annotated, Sequence
import operator

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig

from config import GROQ_API_KEY, GROQ_MIXTRAL
from tools.retriever_tool import query_knowledge_base

# Define the state for our agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    farmer_profile: Dict[str, Any]

def get_agent_executor():
    """
    Creates and returns the LangGraph agent executor.
    """
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MIXTRAL,
        temperature=0.7,
        max_tokens=1024,
    )

    tools = [query_knowledge_base]

    system_message = """You are Digital Sarathi, an expert Indian agricultural consultant.
    Your goal is to provide practical, personalized, and empathetic advice to farmers.
    
    You have access to:
    1. A knowledge base (via query_knowledge_base tool) for facts about government schemes, subsidies, pest management, and best practices.
    2. The farmer's profile (provided in context).
    
    Rules:
    - Always personalize your advice based on the farmer's land size, location, water source, and budget.
    - Ask ONE focused follow-up question at a time to keep the conversation manageable.
    - Use a friendly, professional, and supportive tone.
    - If you use information from the knowledge base, explain how it specifically applies to the farmer's situation.
    - If the farmer asks about something not in your tools or profile, use your general expertise but remain grounded in the Indian context.
    
    Current Farmer Profile:
    {farmer_context}
    """

    def _build_farmer_context(profile: Dict) -> str:
        return (
            f"- Name: {profile.get('name', 'Farmer')}\n"
            f"- Location: {profile.get('location', 'Unknown')}\n"
            f"- Land Size: {profile.get('land_size', 1)} ha\n"
            f"- Water Source: {profile.get('water_source', 'Unknown')}\n"
            f"- Budget: ₹{profile.get('budget', 50000)}\n"
            f"- Risk Level: {profile.get('risk_level', 'medium')}\n"
            f"- Soil Type: {profile.get('soil_type', 'Unknown')}\n"
            f"- Current Seasons: {', '.join(profile.get('current_seasons', ['Kharif']))}"
        )

    # Note: create_react_agent in latest langgraph expects a list of messages or a string for state_modifier
    # We will use a function to dynamically inject the farmer context into the system message.
    
    def state_modifier(state: AgentState) -> List[BaseMessage]:
        farmer_ctx = _build_farmer_context(state.get("farmer_profile", {}))
        return [SystemMessage(content=system_message.format(farmer_context=farmer_ctx))] + state["messages"]

    agent_executor = create_react_agent(llm, tools, state_modifier=state_modifier)
    return agent_executor

def run_agent_interaction(
    user_input: str, 
    chat_history: List[BaseMessage], 
    farmer_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Runs a single interaction with the agent.
    """
    executor = get_agent_executor()
    
    inputs = {
        "messages": chat_history + [HumanMessage(content=user_input)],
        "farmer_profile": farmer_profile
    }
    
    # We use stream or invoke. For a simple response, invoke is fine.
    response = executor.invoke(inputs)
    
    # The last message in the response is the agent's final answer
    final_message = response["messages"][-1]
    
    # Determine if RAG was used by checking if any tool calls were made in the trace
    # (Simplified check: look for any ToolMessage in the result)
    from langchain_core.messages import ToolMessage
    rag_used = any(isinstance(m, ToolMessage) for m in response["messages"])
    
    return {
        "message": final_message.content,
        "messages": response["messages"], # Return the full history including tool calls
        "rag_used": rag_used
    }
