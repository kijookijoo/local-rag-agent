"""CLI entry point: python -m atlas <command>
Commands: index, chat, dev
To run MCP server: python -m atlas.mcp_server
"""
from .cli import app

if __name__ == "__main__":
    app()
