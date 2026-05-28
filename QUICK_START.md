# Quick Start: RAG MCP Server

Get your RAG server running in 5 minutes.

## Prerequisites

- Documents indexed: `python -m atlas.cli index /path/to/docs`
- `.env` file with `OPENAI_API_KEY=sk-...`

## Setup (5 minutes)

### 1. Install
```bash
pip install -r requirements.txt
```

If SSL errors, run: `pip install --upgrade certifi`

### 2. Test
```bash
python test_mcp_server.py
```

### 3. Run Server
```bash
python -m atlas
```

Keep this running. You should see:
```
INFO:src.atlas.mcp_server:Starting RAG MCP server...
INFO:src.atlas.mcp_server:RAG service initialized successfully
```

### 4. Start Claude Code
In another terminal:
```bash
claude-code
```

Or open this folder in VS Code Claude Code extension.

### 5. Done!
Ask Claude about your documents:
```
"What are the main topics?"
"How do I authenticate?"
```

Claude calls your RAG server, injects context, answers efficiently.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: mcp` | `pip install mcp` |
| `OPENAI_API_KEY not set` | Create `.env` with your key |
| `No documents found` | Run `python -m atlas.cli index /path` |
| Server won't start | Check OpenAI key, verify docs indexed |
| Claude can't find tool | Restart Claude Code after starting server |

## Next

- **Detailed setup**: See `LOCAL_MCP_SETUP.md`
- **How it works**: See `IMPLEMENTATION_SUMMARY.md`
- **Alternatives**: See `INTEGRATION_GUIDE.md`

---

That's it! Server is local, secure, and efficient. 🚀
