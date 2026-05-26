"""Simple HTTP server for RAG - BM25 only

Run:
    python http_server.py

Server will start on http://localhost:8000
"""

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.atlas.bm25store import BM25Store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Server", description="Simple RAG HTTP server")
bm25_store = None


@app.on_event("startup")
async def startup():
    global bm25_store
    logger.info("Initializing BM25 search...")
    bm25_store = BM25Store()
    logger.info("BM25 ready")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "rag-server"}


@app.post("/search")
async def search(query: str, top_k: int = 5):
    """Search documents using BM25"""
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
            "count": len(formatted),
            "results": formatted,
        }
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting HTTP server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
