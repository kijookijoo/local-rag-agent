# Atlas: Hybrid RAG for Code Understanding

This project has **two modes** for code search. Choose one based on your workflow.

## Quick Mode Switch

```bash
# Switch to MCP mode (three specialized tools)
atlas mode mcp

# Switch to Greppy mode (CLI tool with restricted native tools)
atlas mode greppy

# Check current mode
atlas mode status
```

---

## Mode 1: MCP (Multi-Tool Integration)

**Best for:** Deep exploration with Claude's native tools + RAG tools

### How It Works

Claude can use three specialized MCP tools alongside native Glob/Grep/Read:

  - **search_keyword** - Fast BM25 keyword search (~300ms)
  - **search_semantic** - Semantic vector search (~1500ms)
  - **search_hybrid** - Balanced hybrid approach (~1000ms)

Claude intelligently chooses which tool to use based on the question.

### Setup

1. Switch to MCP mode:
   ```bash
   atlas mode mcp
   ```

2. Start the servers (in separate terminals):
   ```bash
   python http_server.py          # Terminal 1: HTTP backend
   python -m atlas.mcp_server     # Terminal 2: MCP server
   ```

3. Restart Claude Code - it will auto-discover the three tools

### When to Use MCP

- You want flexibility to use native search tools + RAG tools
- You're comfortable with Claude making mixed search strategies
- You want to leverage both semantic + keyword approaches
- Performance isn't the primary constraint

### Token Overhead

- ~320-477 tokens per query (for tool formatting + context)
- ~250-300ms per query (HTTP round-trip)
- 70-90% token savings vs full code context

---

## Mode 2: Greppy (Retrieval-First)

**Best for:** Fast, focused code search with minimal agent loops

### How It Works

Claude can ONLY use Greppy commands, forcing efficient retrieval-first interactions:

- **search** - Semantic/keyword search
- **exact** - Fast pattern matching
- **read** - File reading with context
- **index** - Manual indexing
- **watch** - Auto-index on file changes

Native tools (Glob, Grep, Read) are **blocked** to prevent exploration loops.

### Setup

1. Switch to Greppy mode:
   ```bash
   atlas mode greppy
   ```

2. Restart Claude Code

3. Use Greppy commands for code operations:
   ```bash
   atlas greppy search "authentication logic"
   atlas greppy exact "def process_payment"
   atlas greppy read src/auth.py:45
   ```

### When to Use Greppy

- You want minimal token usage and fast responses
- You're building a focused task (not deep exploration)
- You want to prevent repeated file exploration
- You prefer a structured retrieval workflow
- You want the latency benefits of local-only execution

### Token/Performance Benefits

- **22x cheaper** - Minimal context from search results
- **2x faster** - No HTTP overhead, local execution
- **Fewer loops** - Retrieval-first design prevents repeated searching

---

## Comparison

| Aspect | MCP | Greppy |
|--------|-----|--------|
| **Tools Available** | 3 MCP + Glob + Grep + Read | Only atlas greppy |
| **Flexibility** | High (mixed strategies) | Medium (retrieval-first) |
| **Token Cost** | ~320-477/query | ~100-200/query |
| **Latency** | ~250-300ms (HTTP) | ~50-200ms (local) |
| **Server Required** | Yes (HTTP + MCP) | No |
| **Best For** | Deep exploration | Fast, focused work |
| **Agent Loops** | Medium (can explore) | Low (forced retrieval) |

---

## For This Session

### In MCP Mode

Use any combination of these approaches:

```bash
# Option 1: Use native tools
ls -la src/
grep -r "authentication" src/

# Option 2: Use MCP tools (Claude will auto-suggest)
# "Find where authentication is handled" → Claude uses search_semantic

# Option 3: Mix both
# Claude reads files with native Read, then uses search_hybrid for context
```

### In Greppy Mode

Always use Greppy CLI:

```bash
# Don't: ls, grep, cat (blocked)
# Do: atlas greppy commands

atlas greppy search "authentication logic"
atlas greppy exact "def process_payment"
atlas greppy read src/auth.py:45
atlas greppy index .
atlas greppy watch
```

---

## File Structure

```
.claude/
├── settings.json          # Current active settings (auto-managed)
├── settings.mcp.json      # MCP mode configuration
├── settings.greppy.json   # Greppy mode configuration
└── CLAUDE.md              # This file

src/atlas/
├── cli.py                 # Mode management + all commands
├── mcp_server.py          # MCP tool implementation
├── greppy.py              # Greppy CLI implementation
├── mode_manager.py        # Mode switching utility
└── ...other modules
```

---

## Troubleshooting

### Mode switch not taking effect
- Run `atlas mode status` to see current mode
- Restart Claude Code after switching

### MCP mode - "Tools not found"
- Verify servers are running: `python http_server.py` & `python -m atlas.mcp_server`
- Check `.claude/settings.json` has `mcpServers` configured

### Greppy mode - "Command not allowed"
- Verify native tools are blocked: `atlas mode status`
- Try: `atlas greppy search "query"` instead of grep

### Embedding model download slow
- First run downloads ~90MB embedding model
- Subsequent runs are instant
- Greppy works with or without embeddings (falls back to BM25)

---

## Advanced: Custom Mode

To create a custom mode, merge settings:

```python
from src.atlas.mode_manager import ModeManager

mm = ModeManager()
custom_settings = mm.merge_settings("greppy", {
    "mcpServers": {"my-server": {...}},
})
```

---

## See Also

- [GREPPY_GUIDE.md](GREPPY_GUIDE.md) - Complete Greppy documentation
- [README.md](README.md) - Project overview
- [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) - Performance metrics
