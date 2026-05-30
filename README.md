# Atlas: Hybrid RAG with Specialized MCP Tools

A lightweight RAG system that indexes documents and exposes specialized search tools. Choose between MCP integration for Claude or Greppy CLI for standalone semantic code search.

## What It Does

- Hybrid retrieval combining BM25 keyword matching and semantic vector search
- **Two ways to search:**
  - MCP tools for Claude Code integration (three specialized tools: search_keyword, search_semantic, search_hybrid)
  - Greppy CLI for standalone code search (semantic search, exact matching, file reading, auto-indexing)
- Local execution with zero network calls
- Automatic tool discovery in Claude Code
- File watching for incremental indexing
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

### Option 1: Greppy CLI (Standalone)

```bash
# Install
pip install -r requirements.txt && pip install -e .

# Index your codebase
atlas greppy index .

# Search!
atlas greppy search "authentication logic"
atlas greppy exact "def process_payment"
atlas greppy read src/auth.py:45
```

### Option 2: MCP Tools for Claude Code

```bash
# Install
pip install -r requirements.txt && pip install -e .

# Index documents
atlas index

# Start HTTP server (required)
python http_server.py

# Start MCP server (in another terminal)
python -m atlas.mcp_server

# Claude will auto-discover the three tools
```

See [GREPPY_GUIDE.md](GREPPY_GUIDE.md) for Greppy documentation or continue below for MCP setup.

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
├── mcp_server.py       Three MCP tools (search_keyword, search_semantic, search_hybrid)
├── greppy.py           Greppy CLI interface (search, exact, read, watch, index, status, clear)
├── bm25store.py        BM25 keyword search
├── vectorstore.py      Vector embeddings
├── embeddings.py       Embedding model loader
├── chunker.py          Document chunking
└── cli.py              Typer app with both MCP and Greppy commands

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

- [GREPPY_GUIDE.md](GREPPY_GUIDE.md) - Complete Greppy CLI documentation and setup
- BENCHMARK_RESULTS.md - Performance analysis with 5 test queries
- QUICK_START.md - Step-by-step setup guide
- LOCAL_MCP_SETUP.md - Detailed configuration
- PERFORMANCE_GUIDE.md - Testing and optimization

## References

- FastMCP: https://github.com/anthropics/mcp-sdk-python
- BM25: Okapi probabilistic retrieval model
- Sentence-Transformers: https://huggingface.co/sentence-transformers

