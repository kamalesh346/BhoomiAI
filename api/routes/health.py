from fastapi import APIRouter
from db.database import _conn
import os

router = APIRouter()

@router.get("/")
def health_check():
    health_status = {
        "status": "healthy",
        "components": {
            "api": "ok",
            "database": "unknown",
            "rag": "unknown",
            "llm": "unknown"
        }
    }

    # Check Database
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        health_status["components"]["database"] = "connected"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check RAG
    try:
        from rag.retriever import load_vectorstore

        vs = load_vectorstore()
        if vs:
            health_status["components"]["rag"] = "loaded"
        else:
            health_status["components"]["rag"] = "failed to load"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["rag"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check LLM Configuration (Groq)
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if groq_api_key:
        health_status["components"]["llm"] = "configured (Groq)"
    else:
        health_status["components"]["llm"] = "mock mode (no API key)"

    return health_status
