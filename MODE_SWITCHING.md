# Mode Switching Guide

Quickly switch between MCP and Greppy modes for different workflows.

## Quick Commands

```bash
# Check current mode
atlas mode status

# Switch to MCP mode (three tools + native search tools)
atlas mode mcp

# Switch to Greppy mode (CLI-only with blocked native tools)
atlas mode greppy
```

## What Gets Switched

### MCP Mode

**settings.json:**
```json
{
  "mcpServers": {
    "rag-agent": {
      "command": "python",
      "args": ["-m", "atlas.mcp_server"],
      "cwd": "..."
    }
  }
}
```

**Effect:**
- Enables MCP server integration
- Allows Glob, Grep, Read tools
- Claude can use mixed search strategies

**Requirements:**
- `python http_server.py` (running)
- `python -m atlas.mcp_server` (running in another terminal)

### Greppy Mode

**settings.json:**
```json
{
  "permissions": {
    "allow": [
      "Bash(atlas:*)",
      "Bash(greppy:*)"
    ],
    "deny": [
      "Glob",
      "Grep",
      "Read"
    ]
  }
}
```

**Effect:**
- Blocks Glob, Grep, Read tools
- Forces Claude to use `atlas greppy` commands
- Retrieval-first design prevents exploration loops

**Requirements:**
- None! Everything runs locally in-process

## Step-by-Step Workflow

### To Use MCP

1. ```bash
   atlas mode mcp
   ```

2. Start the servers (in separate terminals):
   ```bash
   # Terminal 1
   python http_server.py
   
   # Terminal 2
   python -m atlas.mcp_server
   ```

3. Restart Claude Code

4. Use any search approach:
   - Native: `ls`, `grep`, `cat`
   - MCP tools: "Find authentication logic"
   - Mixed strategies

### To Use Greppy

1. ```bash
   atlas mode greppy
   ```

2. Restart Claude Code

3. Use Greppy commands:
   ```bash
   atlas greppy search "query"
   atlas greppy exact "pattern"
   atlas greppy read file.py:45
   ```

## File Structure

```
.claude/
├── settings.json         <- Currently active (auto-managed)
├── settings.mcp.json     <- MCP configuration
└── settings.greppy.json  <- Greppy configuration
```

The mode manager automatically copies the appropriate settings to `settings.json` when you switch modes.

## Troubleshooting

### Mode switch doesn't take effect

**Problem:** Changed mode but Claude still sees old tools

**Solution:**
1. Run `atlas mode status` to confirm the switch worked
2. Restart Claude Code completely (close and reopen)
3. Check `.claude/settings.json` to verify the configuration

### Can't find mode command

**Problem:** `atlas mode` command not recognized

**Solution:**
```bash
# Reinstall the CLI
pip install -e .

# Then try
atlas mode status
```

### MCP mode but servers not found

**Problem:** "MCP server tools not found" in Claude

**Solution:**
1. Verify servers are running:
   ```bash
   curl http://127.0.0.1:8000/health   # Should return ok
   ```

2. Check the MCP server is actually running in another terminal

3. Restart Claude Code to refresh the tool discovery

### Greppy mode but native tools still work

**Problem:** Can still use Glob/Grep/Read despite blocking

**Solution:**
1. Run `atlas mode status` - confirm you're in Greppy mode
2. Verify `.claude/settings.json` has the `deny` section with Glob, Grep, Read
3. Restart Claude Code completely

## Advanced: Custom Modes

To create a custom mode that mixes MCP and permission restrictions:

```python
from src.atlas.mode_manager import ModeManager

mm = ModeManager()

# Start with Greppy but add an extra MCP server
custom_settings = mm.merge_settings("greppy", {
    "mcpServers": {
        "my-custom-tool": {
            "command": "python",
            "args": ["-m", "my_tool"],
        }
    }
})

# Save it
mm._save_settings(custom_settings, mm.settings_file)
```

## See Also

- [CLAUDE.md](CLAUDE.md) - Complete mode documentation
- [GREPPY_GUIDE.md](GREPPY_GUIDE.md) - Greppy CLI reference
- [README.md](README.md) - Project overview
