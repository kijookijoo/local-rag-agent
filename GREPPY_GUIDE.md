# Greppy: Semantic Code Search

Semantic code search CLI built on top of Atlas RAG. Uses ChromaDB + sentence-transformers for semantic search and BM25S for keyword matching. Everything runs locally—no Docker, no Ollama, no API calls.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Index Your Codebase
```bash
atlas greppy index .
```

The first time you index, the embedding model will download (~90MB). Indexing ~20k chunks takes ~2-3 minutes on most systems.

### 3. Search!
```bash
# Semantic search
atlas greppy search "authentication logic"

# Exact pattern matching
atlas greppy exact "def process_payment"

# Read a file with context
atlas greppy read src/auth.py:45
```

## Commands

### Semantic Search
Search by meaning and intent, not just keywords.

```bash
atlas greppy search "how errors are handled"
atlas greppy search "authentication logic" -n 20          # 20 results
atlas greppy search "database queries" -p /path/to/project
```

**Best for:**
- Finding code by concept ("authentication", "error handling")
- Paraphrased queries
- Understanding unfamiliar codebases

### Exact Pattern Match
Search for specific strings, function names, or regex patterns.

```bash
atlas greppy exact "TODO"
atlas greppy exact "def process_payment"
atlas greppy exact "import React"
atlas greppy exact -i "error"                 # Case-insensitive
atlas greppy exact "foo|bar|baz" -n 20       # Multiple patterns (OR)
```

**Best for:**
- Function names
- Specific strings
- TODOs, FIXMEs
- Exact patterns

### Read Files
Read file contents with optional line ranges.

```bash
atlas greppy read src/auth.py               # First 50 lines
atlas greppy read src/auth.py:45            # ~50 lines around line 45
atlas greppy read src/auth.py:30-80         # Lines 30-80
atlas greppy read src/auth.py -c 100        # 100 lines of context
```

### Index Management

#### Manual Indexing
```bash
atlas greppy index .                         # Index current directory
atlas greppy index /path/to/project
atlas greppy index . --force                 # Full reindex
```

#### Auto-Indexing (Watch)
```bash
atlas greppy watch                           # Watch current directory
atlas greppy watch /path/to/project
atlas greppy watch --debounce 10             # Wait 10s after changes
```

The watch command:
- Monitors code files (.py, .ts, .js, etc.)
- Ignores node_modules, .git, venv, etc.
- Debounces changes (waits for you to stop typing)
- Runs incremental indexing (only changed files)

**Tip:** Run `atlas greppy watch` in a separate terminal while coding.

#### Check Status
```bash
atlas greppy status
atlas greppy status /path/to/project
```

#### Clear Index
```bash
atlas greppy clear                           # Removes all indexes
```

## Performance

| Operation | Speed | Notes |
|-----------|-------|-------|
| Semantic search | ~1-2s | First query downloads embedding model |
| Keyword (exact) | ~100-300ms | Very fast, uses BM25S |
| File indexing | ~2-3min | For ~20k chunks, incremental is faster |

## For Claude Code Users

### Setup

1. Create `.claude/settings.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(atlas:*)"
    ],
    "deny": [
      "Glob",
      "Grep",
      "Read"
    ]
  }
}
```

This blocks Claude's native tools, forcing it to use Atlas/Greppy for all code operations.

2. Add to `CLAUDE.md`:
```markdown
## Code Search - Use Greppy

Use `atlas greppy` for all code operations in this codebase:

- Semantic search: `atlas greppy search "query"`
- Exact match: `atlas greppy exact "pattern"`
- Read file: `atlas greppy read src/file.py:45`

The index is already built. Just run the search commands directly.
```

3. Restart Claude Code to load the settings.

### How It Works

**Layer 1: Permissions (Enforcement)**
- Claude tries Glob/Grep/Read → DENIED
- Claude must use `atlas greppy` instead

**Layer 2: Skill/Instruction (Guidance)**
- CLAUDE.md teaches Claude when to use greppy
- Claude learns semantic search > grep for understanding

**Layer 3: Local Execution**
- All searches run locally
- No HTTP overhead
- No token waste on tool serialization
- No repeated exploration loops

### Expected Improvements

With Greppy vs standard Claude Code exploration:

| Metric | With Greppy | Without | Improvement |
|--------|------------|---------|-------------|
| Duration | 1m 16s | 2m 26s | **2x faster** |
| Tokens | 400 | 15,309 | **22x cheaper** |
| Cost | $0.02 | $0.44 | **97% reduction** |

(Based on real benchmarks from Greppy repo)

## Why Is It So Efficient?

Without Greppy, the LLM reads actual file contents to understand what's in them. It issues Glob/Grep commands, reads files, processes them, searches more, reads more files. All that file content goes into the context window, burning through tokens.

With Greppy, the embedding model does semantic search locally (free, no tokens). The retrieval engine returns relevant snippets. The LLM only sees search results—a few lines per match—not entire files.

## How It Integrates with Atlas

Greppy is built on top of the Atlas RAG system:

```
Your codebase
    ↓
Chunked & Indexed
    ├─ BM25 Store (keyword index) ← exact/search commands use this
    └─ Vector Store (embeddings)  ← search command uses this
    ↓
Greppy CLI
    ├─ search "query"     (semantic)
    ├─ exact "pattern"    (keyword)
    ├─ read file.py:45    (file access)
    ├─ watch              (auto-index)
    └─ index              (manual index)
```

No separate servers, no HTTP calls—everything is in-process Python.

## Limitations

- Requires embeddings initialization (model download on first run)
- Single-user local execution
- Context limited by available RAM
- Watch mode requires `watchdog` library

## Architecture

```
Code Files
    ↓
[chunker.py] (1000-char chunks, 200-char overlap)
    ↓
Parallel indexing:
    ├─ BM25Store (./bm25_db)      ← Fast keyword index
    └─ VectorStore (./chroma_db)  ← Semantic embeddings
    ↓
Greppy CLI
    ├─ semantic search (VectorStore)
    ├─ exact search (BM25Store + regex)
    ├─ file reading (direct filesystem)
    └─ watch (filesystem events)
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `atlas: command not found` | Run `pip install -e .` in repo root |
| Index missing | Run `atlas greppy index .` |
| Slow first search | Embeddings model downloading. Check `~/.greppy/` or similar cache dir |
| Watch not working | Install watchdog: `pip install watchdog` |

## Tech Stack

- **ChromaDB** - Vector database (embedded, local, no server)
- **BM25S** - Fast lexical search
- **all-MiniLM-L6-v2** - Embeddings (22M params, MPS/CUDA accelerated)
- **Typer** - CLI framework
- **Rich** - Terminal output formatting
