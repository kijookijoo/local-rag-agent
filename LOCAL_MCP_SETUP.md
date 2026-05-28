# Local MCP Server Setup (Single-User, Local Hosting)

Since you're the only user, hosting the MCP server **locally** is perfect. The server runs as a subprocess when Claude Code starts — no cloud deployment needed.

## 🏗️ Architecture

```
Your Machine
├─ Claude Code IDE
│  └─ Starts stdio MCP server (subprocess)
│     ├─ Loads .claude/settings.json
│     └─ Runs: python -m atlas
│        └─ Connects to: RAG Pipeline
│           ├─ Vector Index (./chroma_db)
│           ├─ BM25 Index (./bm25_db)
│           └─ OpenAI API
```

## ✅ Prerequisites

Before starting, verify you have:

1. **Indexed Documents**
   ```bash
   python -m atlas.cli index /path/to/your/documents
   ```
   This creates:
   - `./bm25_db/` (keyword index)
   - `./chroma_db/` (vector embeddings)

2. **Environment Variables** (in `.env`)
   ```
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL_NAME=gpt-4o-mini
   ```

3. **Dependencies Installed**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Setup Steps

### Step 1: Install MCP SDK

The MCP SDK is now in requirements.txt. Install it:

```bash
pip install -r requirements.txt
```

If you get SSL certificate errors:

**Option A: Upgrade certificates (recommended)**
```bash
pip install --upgrade certifi
```

**Option B: Bypass SSL (not recommended, security risk)**
```bash
pip install --no-cert-verify mcp
```

**Option C: Use corporate proxy** (if behind firewall)
```bash
pip install -r requirements.txt --proxy [user:passwd@]proxy.server:port
```

### Step 2: Verify Installation

```bash
python -c "from mcp.server.fastmcp import FastMCP; print('MCP SDK installed!')"
```

### Step 3: Test the MCP Server Locally

```bash
python -m atlas
```

You should see:
```
INFO:src.atlas.mcp_server:Starting RAG MCP server...
INFO:src.atlas.mcp_server:Initializing RAG service...
INFO:src.atlas.mcp_server:RAG service initialized successfully
```

The server is now running and waiting for connections. Keep this running.

### Step 4: Start Claude Code

In another terminal, start Claude Code in this directory:

```bash
claude-code
```

Or use the Claude Code desktop/web app and open this folder.

### Step 5: Ask Claude About Your Documents

In Claude Code, ask:

```
What are the main topics in our documentation?
```

Claude will:
1. See the `search_rag` tool is available
2. Call it to search your documents
3. Return relevant results
4. Answer your question based on the context

## 📝 How It Works (Behind the Scenes)

1. **You start Claude Code** → loads `.claude/settings.json`
2. **Claude sees MCP server config** → starts subprocess: `python -m atlas`
3. **MCP server initializes** → loads RAG pipeline (1-3 seconds)
4. **Server publishes tools** → Claude can now call `search_rag`
5. **You ask a question** → Claude calls `search_rag` tool
6. **Results injected** → Claude gets relevant context
7. **Response generated** → Claude answers efficiently

## 🔍 Monitoring the Server

The MCP server logs to `src.atlas.mcp_server` logger. To see more detail:

```python
# In mcp_server.py, change logging level
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

Or run with:
```bash
python -m atlas 2>&1 | grep -E "DEBUG|INFO|ERROR"
```

## 🛑 Stopping the Server

The server runs as a subprocess of Claude Code:
- **Stop Claude Code** → Server automatically stops
- **Or press Ctrl+C** in the terminal where you ran `python -m atlas`

## ⚠️ Troubleshooting

### "MCP server connection failed"
- Ensure `python -m atlas` is running
- Check `.claude/settings.json` is correct
- Try restarting Claude Code

### "No documents found"
- Run: `python -m atlas.cli index /path/to/docs`
- Verify `./chroma_db/` and `./bm25_db/` exist
- Try a more specific query

### "OPENAI_API_KEY not found"
- Create `.env` file with your key
- Or: `export OPENAI_API_KEY=sk-...`
- Restart server

### Server starts but slow first call (5-10 seconds)
- **Normal!** First call loads embedding models into memory
- Subsequent calls are fast (1-2 seconds)
- This is expected behavior

### SSL certificate errors
- Run: `pip install --upgrade certifi`
- Or use corporate proxy if behind firewall
- See "Install MCP SDK" section above

## 📊 Performance Expectations

| Metric | Value |
|--------|-------|
| First server startup | 1-3 seconds |
| First RAG search | 5-10 seconds (models load) |
| Subsequent searches | 1-2 seconds |
| Tokens saved (vs full doc injection) | 80-90% reduction |

## 🔐 Security Notes

**Local hosting is secure because:**
- ✓ Server runs only on your machine
- ✓ No network exposure
- ✓ No data leaves your computer (except to OpenAI API)
- ✓ Direct stdio connection between Claude Code and server
- ✓ No authentication overhead

## 🎯 Next Steps

1. Install MCP SDK: `pip install -r requirements.txt`
2. Test server: `python -m atlas`
3. Start Claude Code
4. Ask about your documents

## 💡 Tips

- **Keep the server running** while you use Claude Code
- **First query is slower** (models load) — subsequent are fast
- **Different queries** may hit cache if similar
- **Restart server** if it seems stuck: Ctrl+C and `python -m atlas`

## 📈 Upgrading Later (Optional)

If you want to share with teammates later, you can:
1. Deploy to cloud (Heroku, AWS, etc.)
2. Change to HTTP/SSE transport
3. Share the server URL in `.claude/settings.json`

But for now, **local is perfect** for your use case.

---

**Status**: ✅ Ready for local deployment!

Next: `pip install -r requirements.txt` → `python -m atlas` → Start Claude Code

