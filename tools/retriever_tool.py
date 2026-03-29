from langchain_core.tools import tool
from rag.retriever import retrieve_relevant_info

@tool
def query_knowledge_base(query: str) -> str:
    """
    Query the agricultural knowledge base to retrieve information about:
    - Indian government schemes and subsidies (PM-KISAN, PMFBY, etc.)
    - Crop-specific advice and best practices
    - Pest and disease management
    - Water sustainability and irrigation techniques
    
    Use this tool when you need specific facts, guidelines, or details from official documents.
    """
    return retrieve_relevant_info(query)
