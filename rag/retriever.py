import os
import pickle
import logging
import warnings
from pathlib import Path
from typing import List, Tuple

# Suppress logs during embedding initialization
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import DATA_DIR, FAISS_INDEX_PATH, EMBEDDING_MODEL


_vectorstore = None


def _get_doc_files() -> List[Path]:
    return list(DATA_DIR.glob("doc_*.txt"))


def build_vectorstore() -> FAISS:
    """Build FAISS vectorstore from document files."""
    doc_files = _get_doc_files()
    if not doc_files:
        raise FileNotFoundError("No doc_*.txt files found in data directory.")

    all_docs = []
    for filepath in doc_files:
        text = filepath.read_text(encoding="utf-8")
        all_docs.append(Document(
            page_content=text,
            metadata={"source": filepath.name}
        ))

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(all_docs)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    return vectorstore


def load_vectorstore() -> FAISS:
    """Load existing FAISS index or build a new one."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    index_path = Path(FAISS_INDEX_PATH)
    if index_path.exists():
        try:
            _vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings,
                allow_dangerous_deserialization=True
            )
            return _vectorstore
        except Exception:
            pass

    # Build fresh
    _vectorstore = build_vectorstore()
    return _vectorstore


def retrieve_relevant_info(query: str, k: int = 3) -> str:
    """
    Retrieve relevant chunks from FAISS for a given query.
    Returns concatenated text of top-k chunks.
    """
    try:
        vs = load_vectorstore()
        docs = vs.similarity_search(query, k=k)
        if not docs:
            return ""
        return "\n\n---\n\n".join([d.page_content for d in docs])
    except Exception as e:
        print(f"[RAG error] {e}")
        return ""


def get_subsidy_info(crops: List[str], farmer_location: str = "") -> str:
    """Get subsidy information relevant to given crops."""
    query = f"government subsidies schemes support for {', '.join(crops[:3])} farmers"
    if farmer_location:
        query += f" in {farmer_location}"
    return retrieve_relevant_info(query, k=2)


def get_pest_warnings(crops: List[str], season: str = "") -> str:
    """Get pest and disease warnings for crops."""
    query = f"pest disease warning management for {', '.join(crops[:3])}"
    if season:
        query += f" during {season}"
    return retrieve_relevant_info(query, k=2)


def get_water_conservation_tips(water_source: str = "", crops: List[str] = None) -> str:
    """Get water management tips."""
    query = "water conservation irrigation techniques for Indian farmers"
    if crops:
        query += f" growing {', '.join(crops[:2])}"
    return retrieve_relevant_info(query, k=2)
