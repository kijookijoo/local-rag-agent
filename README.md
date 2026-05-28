# Atlas: Hybrid RAG with Specialized MCP Tools

A lightweight RAG system that indexes documents and exposes three specialized search tools via MCP for Claude. Reduces token overhead while improving retrieval accuracy through intelligent tool selection.

## What It Does

- Hybrid retrieval combining BM25 keyword matching and semantic vector search
- Three specialized MCP tools: search_keyword (fast), search_semantic (accurate), search_hybrid (balanced)
- Local execution with zero network calls
- Automatic tool discovery in Claude Code
- Benchmark-tested performance metrics

## Architecture

```
Documents (yours)
    |
    +-- Chunked & Indexed
        |
        +-- BM25 Store (keyword index)
        +-- Vector Store (embeddings via all-MiniLM-L6-v2)
    |
    +-- HTTP Server (http://127.0.0.1:8000)
        |
        +-- /search/keyword (fast, exact match)
        +-- /search/semantic (slow, meaning-based)
        +-- /search/hybrid (balanced, RRF fusion)
    |
    +-- MCP Server (fastmcp)
        |
        +-- search_keyword() tool
        +-- search_semantic() tool
        +-- search_hybrid() tool
    |
    +-- Claude (auto-discovers tools)
```

## Quick Start

```bash
# Install
pip install -r requirements.txt && pip install -e .

# Index documents
python -m atlas.cli index /path/to/documents

# Start HTTP server (required)
python http_server.py

# Start MCP server (in another terminal)
python -m atlas.mcp_server

# Claude will auto-discover the three tools
```

## Tools

| Tool | Speed | Best For | Tokens |
|------|-------|----------|--------|
| search_keyword | ~300ms | Code lookups, specific terms | ~345/query |
| search_semantic | ~1500ms | Conceptual, meaning-based | ~423/query |
| search_hybrid | ~1000ms | General questions | ~477/query |

Claude automatically selects the right tool based on your question.

## Performance

| Metric | Value |
|--------|-------|
| Token overhead per query | ~320 tokens (for context + tools) |
| Time overhead | ~250-300ms (HTTP call) |
| Token savings vs full context | 70-90% |
| Cost impact | < $0.00001 per query |

See BENCHMARK_RESULTS.md for detailed measurements.

## Dependencies

Core:
- Python 3.9+
- langchain (embeddings, document processing)
- sentence-transformers (all-MiniLM-L6-v2 model)
- bm25s (keyword search)
- chromadb (vector store)

MCP:
- anthropic/mcp (FastMCP server)
- httpx (HTTP client)

Server:
- fastapi + uvicorn (HTTP backend)

## File Structure

```
src/atlas/
├── mcp_server.py       Three MCP tools
├── bm25store.py        BM25 keyword search
├── vectorstore.py      Vector embeddings
├── embeddings.py       Embedding model loader
├── chunker.py          Document chunking
└── cli.py              Index command

http_server.py          HTTP server with 3 endpoints
.claude/
└── settings.json       MCP server config
```

## When to Use MCP Tools

Use search_keyword for:
- Looking up specific code, function names, identifiers
- Fast retrieval when you know exact terms

Use search_semantic for:
- Understanding concepts and relationships
- Paraphrased or natural language questions

Use search_hybrid for:
- General questions about your documents
- When you're unsure which method fits
- Maximum accuracy desired

## Limitations

- Requires vector store initialization (downloads embedding model on first run)
- Offline operation possible with keyword search only
- Single-user local execution (HTTP server not meant for scale)
- Context size limited by LLM window (30K tokens for Opus)

## Resources

- BENCHMARK_RESULTS.md - Performance analysis with 5 test queries
- QUICK_START.md - Step-by-step setup guide
- LOCAL_MCP_SETUP.md - Detailed configuration
- PERFORMANCE_GUIDE.md - Testing and optimization

## References

- FastMCP: https://github.com/anthropics/mcp-sdk-python
- BM25: Okapi probabilistic retrieval model
- Sentence-Transformers: https://huggingface.co/sentence-transformers

