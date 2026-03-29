from langchain_core.tools import tool
from rag.retriever import retrieve_relevant_info

@tool
def query_rag(query: str) -> str:
    """
    Search the agricultural knowledge base for facts about:
    - Indian government schemes (PM-KISAN, PMFBY, etc.)
    - Subsidies and subsidies eligibility
    - Specific crop advice and best practices
    - Pest and disease management
    - Water sustainability
    """
    return retrieve_relevant_info(query)
