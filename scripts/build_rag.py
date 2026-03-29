#!/usr/bin/env python3
"""
Build the FAISS vector index from policy documents.
Run once before starting the app (or it auto-builds on first use).
Usage: python scripts/build_rag.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.retriever import build_vectorstore

if __name__ == "__main__":
    print("Building RAG vector index from documents...")
    print("  (This downloads 'all-MiniLM-L6-v2' on first run — ~90MB)")
    try:
        vs = build_vectorstore()
        print(f"✅ FAISS index built with {vs.index.ntotal} vectors.")
        print(f"   Saved to: rag/faiss_index/")
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

    print("\n🔍 Testing retrieval...")
    from rag.retriever import retrieve_relevant_info
    result = retrieve_relevant_info("crop insurance subsidy for farmers")
    print(f"✅ Retrieval test OK ({len(result)} chars returned)")
