# Evaluation Scripts

Scripts for measuring Greppy effectiveness and performance.

## 1. Retrieval Performance Evaluation

**File:** `evaluate_retrieval.py`

Measures the raw retrieval performance: latency, token usage, and result quality without needing Claude API calls.

### What It Measures

- **Latency** - How fast each search method returns results (ms)
- **Token Overhead** - Estimated tokens in results (chars ÷ 4)
- **Relevance** - How well results match expected keywords (0-1)
- **Comparison** - BM25 vs Semantic vs Hybrid search methods

### Usage

```bash
# Evaluate all search methods (default)
python scripts/evaluate_retrieval.py

# Evaluate only BM25 keyword search
python scripts/evaluate_retrieval.py --mode keyword

# Evaluate only semantic search
python scripts/evaluate_retrieval.py --mode semantic

# Evaluate only Greppy hybrid search
python scripts/evaluate_retrieval.py --mode hybrid

# Use only 3 queries instead of 5
python scripts/evaluate_retrieval.py --queries 3

# Get 20 results per query instead of 10
python scripts/evaluate_retrieval.py --limit 20
```

### Requirements

- Greppy index must be built: `atlas greppy index .`
- No API keys needed

### Output

Generates:
- **Console tables** with search latency, token counts, relevance scores
- **JSON file** `retrieval_results.json` with detailed results

### Example Results

```
Results by Query

BM25 Search Performance
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Query      ┃ Latency  ┃ Res ┃ Avg Siz ┃ Tokens ┃ Relevan┃
┣━━━━━━━━━━━━╋━━━━━━━━━━╋━━━━━╋━━━━━━━━━╋━━━━━━━━╋━━━━━━━━┫
┃ authenticat┃   12.34 ┃  10 ┃   1250  ┃   312  ┃   100% ┃
...
```

### Performance Expectations

Based on benchmark data:

| Metric | BM25 | Semantic | Greppy |
|--------|------|----------|--------|
| **Latency** | ~10-50ms | ~1-2s | ~20-100ms |
| **Relevance** | 70-80% | 85-95% | 80-90% |
| **Token Overhead** | Low | Medium | Low-Medium |

## 2. Claude API Evaluation

**File:** `evaluate_greppy.py`

Measures token usage and latency when Claude uses Greppy vs native tools for code understanding tasks.

### What It Measures

- **Token Usage** - Total input + output tokens (Greppy vs native)
- **Latency** - Time to complete task (Greppy vs native)
- **Cost** - Estimated USD cost per query
- **Improvement** - Percentage savings with Greppy

### Prerequisites

1. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

2. Build the Greppy index:
   ```bash
   atlas greppy index .
   ```

### Usage

```bash
# Run full evaluation (5 tasks, both modes)
python scripts/evaluate_greppy.py

# Runs each of these tasks twice:
# 1. WITH Greppy: using atlas greppy commands
# 2. WITHOUT Greppy: using native tools (ls, grep, cat)
```

### Cost

- Uses Claude Opus 4.7 ($15 per 1M input tokens, $45 per 1M output tokens)
- Expected cost: ~$0.10-0.50 per run (5 tasks × 2 modes)

### Output

Generates:
- **Console report** with token usage and cost comparison
- **JSON file** `evaluation_results.json` with detailed results per task

### Example Results

```
GREPPY EVALUATION RESULTS
════════════════════════════════════════════════════════════════════

Task: Authentication flow tracing
────────────────────────────────────────────────────────────────────
Metric                     Greppy               Native               Improvement
────────────────────────────────────────────────────────────────────
Total Tokens               3,245                8,932                -63.7%
Latency (seconds)          2.34                 4.12                 -43.2%
Cost (USD)                 $0.074               $0.218               -66.1%

SUMMARY (All Tasks)
════════════════════════════════════════════════════════════════════
Total Tokens               18,432               52,156               -64.7%
Total Latency (seconds)    12.45                28.73                -56.7%
Total Cost (USD)           $0.42                $1.18                -64.4%

Greppy is 65% cheaper and 57% faster
════════════════════════════════════════════════════════════════════
```

## Test Queries

Both scripts use realistic code understanding tasks:

1. **auth_flow** - Trace authentication flow across files
2. **search_impl** - Find all search implementations
3. **error_handling** - Investigate error handling patterns
4. **data_flow** - Explain data transformation pipeline
5. **indexing** - Understand indexing system

These tasks typically require multiple file reads and cross-file understanding, making them ideal for measuring RAG effectiveness.

## Interpreting Results

### Retrieval Evaluation

- **Lower latency is better** - Faster response time
- **Higher relevance is better** - More useful results
- **Lower token overhead is better** - Cheaper to process results

**Key insight:** If BM25 has low latency but low relevance, semantic search might be worth the latency tradeoff.

### Claude API Evaluation

- **Lower token usage is better** - Cheaper, faster
- **Lower latency is better** - Faster task completion
- **Higher improvement % is better** - Bigger savings with Greppy

**Key insight:** Greppy usually saves tokens because Claude doesn't need to read entire files to explore the codebase.

## Troubleshooting

### "Index is empty"

```bash
# Build the index first
atlas greppy index .
```

### "Semantic search unavailable"

This is normal if embeddings can't download (SSL issues, offline, etc.). The scripts fall back to BM25.

### "API key not set"

```bash
# For Claude API evaluation
export ANTHROPIC_API_KEY=sk-ant-...

# For OpenAI API (if using OpenAI instead)
export OPENAI_API_KEY=sk-...
```

### Results seem inconsistent

Claude's responses vary due to:
- Model temperature (set to 0 for consistency)
- Different reasoning paths
- Caching effects

Run multiple times and average results for stable benchmarks.

## Logging Results

After running an experiment, automatically log results to `BENCHMARK_RESULTS.md`:

```bash
# After running retrieval evaluation
python scripts/log_experiment.py --experiment retrieval \
    --results retrieval_results.json \
    --summary "Greppy is 2.24ms latency, 75% relevant"

# After running Claude API evaluation
python scripts/log_experiment.py --experiment claude-api \
    --results evaluation_results.json \
    --summary "Greppy is 65% cheaper and 57% faster"
```

This automatically:
- Updates BENCHMARK_RESULTS.md with new results
- Parses JSON results into formatted tables
- Adds date and status
- Maintains experiment history

See [BENCHMARK_RESULTS.md](../BENCHMARK_RESULTS.md) for complete experiment history.

## Extending the Scripts

### Add Custom Queries

Edit the `TEST_QUERIES` list in either script:

```python
TEST_QUERIES = [
    {
        "id": "my_task",
        "query": "Find all database operations",
        "semantic_query": "database access patterns",
        "expected_keywords": ["db", "query", "select", "insert"],
    },
    ...
]
```

### Custom Search Methods

In `evaluate_retrieval.py`, add a new evaluation function:

```python
def evaluate_custom(queries: List[dict]) -> List[RetrievalResult]:
    """Your custom search implementation."""
    results = []
    for query in queries:
        # Implement your search logic
        pass
    return results
```

Then add it to the mode selection:

```python
if args.mode in ["custom", "all"]:
    all_results.extend(evaluate_custom(queries))
```

## See Also

- [GREPPY_GUIDE.md](../GREPPY_GUIDE.md) - Greppy CLI reference
- [MODE_SWITCHING.md](../MODE_SWITCHING.md) - Mode switching guide
- [CLAUDE.md](../CLAUDE.md) - Complete mode documentation
