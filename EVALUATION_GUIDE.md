# Greppy Evaluation Guide

Comprehensive guide to measuring Greppy's performance and effectiveness.

## Quick Start

### 1. Build the Index

```bash
atlas greppy index .
```

### 2. Run Retrieval Evaluation (No API Key Required)

```bash
python scripts/evaluate_retrieval.py
```

This measures:
- **Latency** - How fast searches return results
- **Relevance** - How well results match the query
- **Token Overhead** - How many tokens are in results

### 3. Run Claude API Evaluation (Requires Anthropic API Key)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/evaluate_greppy.py
```

This measures:
- **Token Usage** - Greppy vs native tools
- **Cost** - USD cost comparison
- **Latency** - Time to complete task

## Evaluation Scripts

### Script 1: Retrieval Performance (`evaluate_retrieval.py`)

**Purpose:** Measure raw search performance

**What it does:**
- Runs 5 test queries
- Evaluates BM25 (keyword), Semantic, and Hybrid searches
- Measures latency, relevance, and token overhead
- Generates comparison tables

**Requirements:**
- Greppy index built: `atlas greppy index .`
- No API keys needed

**Usage:**

```bash
# Full evaluation (all search methods)
python scripts/evaluate_retrieval.py

# Specific search method
python scripts/evaluate_retrieval.py --mode keyword
python scripts/evaluate_retrieval.py --mode semantic
python scripts/evaluate_retrieval.py --mode hybrid

# Customize number of queries and results
python scripts/evaluate_retrieval.py --queries 3 --limit 20
```

**Output:**
- Console tables with metrics
- `retrieval_results.json` with detailed results

**Expected Results:**

| Metric | BM25 | Semantic | Hybrid |
|--------|------|----------|--------|
| Latency | ~10ms | ~1-2s | ~20ms |
| Relevance | 75% | 90% | 85% |
| Tokens | 1200 | 1500 | 1300 |

### Script 2: Claude API Evaluation (`evaluate_greppy.py`)

**Purpose:** Measure Claude's efficiency with Greppy vs native tools

**What it does:**
- Asks Claude 5 code understanding questions
- Measures tokens and latency WITH Greppy
- Measures tokens and latency WITHOUT Greppy (native tools only)
- Calculates cost savings

**Requirements:**
- Greppy index built: `atlas greppy index .`
- Anthropic API key: `export ANTHROPIC_API_KEY=sk-ant-...`
- ~$0.10-0.50 API cost per run

**Usage:**

```bash
# Set API key (do once per session)
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Run evaluation
python scripts/evaluate_greppy.py
```

**Output:**
- Console report with comparison
- `evaluation_results.json` with detailed results per task

**Expected Results:**

```
Greppy is 60% cheaper and 40% faster
```

Example detailed comparison:

| Metric | Greppy | Native | Improvement |
|--------|--------|--------|-------------|
| Total Tokens | 18,432 | 52,156 | -65% |
| Latency | 12.45s | 28.73s | -57% |
| Cost | $0.42 | $1.18 | -64% |

## Understanding Results

### Retrieval Evaluation Results

**Low Latency is Good**
- BM25: ~10-50ms (fastest, but lower relevance)
- Hybrid: ~20-100ms (balanced)
- Semantic: ~1-2s (slowest, but highest relevance)

**High Relevance is Good**
- BM25: 70-80% (matches keywords well)
- Semantic: 85-95% (understands intent well)
- Hybrid: 80-90% (best of both)

**Token Overhead**
- Measures context size of results
- Lower = cheaper to process
- BM25 typically smallest (most concise results)

### Claude API Evaluation Results

**Token Savings with Greppy**
- Greppy helps Claude avoid reading entire files
- Instead of 10+ file reads, Claude gets search results
- Typical savings: 50-70% fewer tokens

**Latency Improvements**
- Fewer exploration loops = faster response
- No HTTP overhead (local execution)
- Typical improvement: 40-60% faster

**Cost Savings**
- Direct correlation with token savings
- $0.01-0.50 saved per complex query
- Scales with task complexity

## Troubleshooting

### "Index is empty"

```bash
# Build the index
atlas greppy index .

# Verify it was created
ls -lh bm25_db/
```

### "Semantic search unavailable"

This is normal if the environment has SSL certificate issues. The system falls back to BM25 automatically.

To test semantic search:
```bash
# Try downloading the model manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### "API key not found"

```bash
# Check if API key is set
echo $ANTHROPIC_API_KEY

# Set it if not
export ANTHROPIC_API_KEY=sk-ant-your-key
```

### Results show as "N/A" or strange values

This can happen if:
- Index hasn't been built recently
- Only a few files in the codebase
- Network issues during retrieval

Try:
```bash
# Rebuild index with verbose output
atlas greppy index . --force

# Re-run evaluation
python scripts/evaluate_retrieval.py
```

## Comparison with Previous Results

If you have previous benchmark results, you can compare:

```python
import json

# Load old results
with open("old_evaluation_results.json") as f:
    old = json.load(f)

# Load new results
with open("evaluation_results.json") as f:
    new = json.load(f)

# Compare metrics
print(f"Token improvement: {(1 - sum(r['total_tokens'] for r in new) / sum(r['total_tokens'] for r in old)) * 100:.0f}%")
```

## Advanced: Custom Evaluation

### Add Custom Queries

Edit `TEST_QUERIES` in the script:

```python
TEST_QUERIES = [
    {
        "id": "custom_task",
        "query": "Find all database queries",
        "description": "Database operation investigation"
    },
    ...
]
```

### Measure Specific Methods

Modify the script to only run certain search methods:

```bash
# Only test BM25
python scripts/evaluate_retrieval.py --mode keyword

# Only test semantic (shows impact of embeddings)
python scripts/evaluate_retrieval.py --mode semantic
```

### Profile Search Performance

For more detailed timing information:

```python
import time
from src.atlas.greppy import Greppy

g = Greppy()

# Measure individual searches
start = time.perf_counter()
results = g.search("your query")
print(f"Search took {(time.perf_counter() - start)*1000:.2f}ms")
```

## Key Metrics Explained

### Input Tokens
Tokens sent to Claude for processing (question + context)

**Why it matters:** Directly affects cost ($15 per 1M on Opus input)

### Output Tokens
Tokens generated by Claude in response

**Why it matters:** Directly affects cost ($45 per 1M on Opus output)

### Latency (Seconds)
Wall-clock time from question to answer

**Why it matters:** User experience and API billing minutes

### Cost (USD)
Estimated cost using current Claude pricing

**Why it matters:** Budget tracking and ROI calculation

### Relevance Score (0-1)
How well results contain relevant keywords (0% = none, 100% = all)

**Why it matters:** Quality of search results and Claude's ability to answer

## When to Re-Evaluate

Re-run evaluations when:

1. **After code changes** - Did refactoring improve search?
2. **After reindexing** - Did adding more files improve results?
3. **When comparing tools** - BM25 vs Semantic vs new search method
4. **For regression testing** - Did a change break anything?
5. **Before optimization** - Establish baseline before tuning

## Sharing Results

Example: Include in project documentation

```markdown
## Performance

Last evaluated: 2024-05-31

### Retrieval Performance
- Greppy hybrid search: 2.24ms latency, 75% relevance
- Token overhead per search: ~1600 tokens

### Claude Integration
- With Greppy: 18,432 tokens per 5 tasks
- Without Greppy: 52,156 tokens per 5 tasks
- **Improvement: 65% cheaper, 57% faster**

See [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md) for details.
```

## See Also

- [scripts/README.md](scripts/README.md) - Script documentation
- [GREPPY_GUIDE.md](GREPPY_GUIDE.md) - Greppy CLI reference
- [MODE_SWITCHING.md](MODE_SWITCHING.md) - Mode switching guide
