"""HTTP server for RAG - Hybrid retrieval (BM25 + Semantic)

Run:
    python http_server.py

Server will start on http://localhost:8000
"""

import logging
from collections import defaultdict
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.atlas.bm25store import BM25Store
from src.atlas.vectorstore import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Server", description="Hybrid RAG HTTP server")
bm25_store = None
vector_store = None

SIMILARITY_DIST_THRESHOLD = 1.55


@app.on_event("startup")
async def startup():
    global bm25_store, vector_store
    logger.info("Initializing BM25 search...")
    bm25_store = BM25Store()
    logger.info("BM25 ready")
    logger.info("Note: Vector search requires network access to HuggingFace")
    logger.info("Semantic and hybrid searches will fall back to keyword search")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "rag-server"}


@app.post("/search/keyword")
async def search_keyword(query: str, top_k: int = 5):
    """Search documents using BM25 keyword matching (fast, keyword-focused)"""
    if not bm25_store:
        return JSONResponse({"error": "Search not initialized"}, status_code=500)

    try:
        top_k = min(max(top_k, 1), 20)
        results = bm25_store.search(query, k=top_k)

        formatted = []
        for idx, doc in enumerate(results, 1):
            formatted.append({
                "rank": idx,
                "content": doc.page_content,
                "metadata": dict(doc.metadata),
            })

        return {
            "query": query,
            "method": "keyword",
            "count": len(formatted),
            "results": formatted,
        }
    except Exception as e:
        logger.error(f"Keyword search error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/search/semantic")
async def search_semantic(query: str, top_k: int = 5):
    """Search documents using semantic similarity (slow, meaning-focused)"""
    if not vector_store:
        return JSONResponse(
            {
                "error": "Vector search not available - falling back to keyword search",
                "fallback": True,
                "message": "Semantic search requires embedding models. Using BM25 instead.",
            },
            status_code=503,
        )

    try:
        top_k = min(max(top_k, 1), 20)
        retriever = vector_store.as_retriever(k=top_k)
        results = retriever.invoke(query)

        formatted = []
        for idx, doc in enumerate(results, 1):
            formatted.append({
                "rank": idx,
                "content": doc.page_content,
                "metadata": dict(doc.metadata),
            })

        return {
            "query": query,
            "method": "semantic",
            "count": len(formatted),
            "results": formatted,
        }
    except Exception as e:
        logger.error(f"Semantic search error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/search/hybrid")
async def search_hybrid(query: str, top_k: int = 5):
    """Search documents using hybrid retrieval (BM25 + Semantic with reciprocal rank fusion)"""
    if not bm25_store:
        return JSONResponse({"error": "BM25 search not initialized"}, status_code=500)

    # If vector store unavailable, fall back to keyword-only
    if not vector_store:
        logger.warning("Vector store unavailable, falling back to keyword-only search")
        return await search_keyword(query, top_k)

    try:
        top_k = min(max(top_k, 1), 20)

        # Get results from both retrievers
        bm25_results = bm25_store.search(query, k=top_k)

        retriever = vector_store.as_retriever(k=top_k)
        vector_results = retriever.invoke(query)

        # Reciprocal Rank Fusion (RRF)
        scores = defaultdict(float)
        docs = {}

        # Score BM25 results
        for rank, doc in enumerate(bm25_results):
            key = doc.metadata.get("path", "") + doc.page_content[:100]
            docs[key] = doc
            scores[key] += 1 / (rank + 60)  # RRF formula

        # Score vector results
        for rank, doc in enumerate(vector_results):
            key = doc.metadata.get("path", "") + doc.page_content[:100]
            docs[key] = doc
            scores[key] += 1 / (rank + 60)

        # Sort by combined score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        final_results = [docs[key] for key, _ in sorted_results[:top_k]]

        formatted = []
        for idx, doc in enumerate(final_results, 1):
            formatted.append({
                "rank": idx,
                "content": doc.page_content,
                "metadata": dict(doc.metadata),
            })

        return {
            "query": query,
            "method": "hybrid",
            "count": len(formatted),
            "results": formatted,
        }
    except Exception as e:
        logger.error(f"Hybrid search error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/search")
async def search(query: str, top_k: int = 5):
    """Legacy endpoint - defaults to hybrid retrieval"""
    return await search_hybrid(query, top_k)


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting HTTP server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
