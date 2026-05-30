"""Mode manager: Switch between MCP and Greppy configurations.

This utility switches between different Claude Code settings configurations
depending on which feature you want to use.

Modes:
  - mcp: Use the MCP server with three specialized tools (search_keyword, search_semantic, search_hybrid)
  - greppy: Use the Greppy CLI with native tools restricted
"""

import json
import shutil
from pathlib import Path
from typing import Literal

from rich.console import Console

console = Console()


class ModeManager:
    """Manage Claude Code settings for different modes."""

    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.claude_dir = self.project_root / ".claude"
        self.settings_file = self.claude_dir / "settings.json"
        self.mcp_settings = self.claude_dir / "settings.mcp.json"
        self.greppy_settings = self.claude_dir / "settings.greppy.json"

    def _load_settings(self, path: Path) -> dict:
        """Load settings from a file."""
        if not path.exists():
            raise FileNotFoundError(f"Settings file not found: {path}")
        with open(path, "r") as f:
            return json.load(f)

    def _save_settings(self, settings: dict, path: Path):
        """Save settings to a file."""
        with open(path, "w") as f:
            json.dump(settings, f, indent=2)

    def switch_to_mcp(self) -> bool:
        """Switch to MCP mode.

        Requires:
        - HTTP server running: python http_server.py
        - MCP server: python -m atlas.mcp_server (in another terminal)
        """
        console.print("[cyan]Switching to MCP mode...[/cyan]")

        if not self.mcp_settings.exists():
            console.print(f"[red]Error: {self.mcp_settings} not found[/red]")
            return False

        try:
            settings = self._load_settings(self.mcp_settings)
            self._save_settings(settings, self.settings_file)
            console.print("[green]Switched to MCP mode[/green]")
            console.print("[dim]Remember to start the servers:[/dim]")
            console.print("[dim]  python http_server.py[/dim]")
            console.print("[dim]  python -m atlas.mcp_server[/dim]")
            return True
        except Exception as e:
            console.print(f"[red]Error switching to MCP mode: {e}[/red]")
            return False

    def switch_to_greppy(self) -> bool:
        """Switch to Greppy mode.

        Restricts native search tools (Glob, Grep, Read) and
        forces Claude to use 'atlas greppy' commands instead.
        """
        console.print("[cyan]Switching to Greppy mode...[/cyan]")

        if not self.greppy_settings.exists():
            console.print(f"[red]Error: {self.greppy_settings} not found[/red]")
            return False

        try:
            settings = self._load_settings(self.greppy_settings)
            self._save_settings(settings, self.settings_file)
            console.print("[green]Switched to Greppy mode[/green]")
            console.print("[dim]Restart Claude Code to apply changes[/dim]")
            console.print("[dim]Native tools (Glob, Grep, Read) are now blocked[/dim]")
            return True
        except Exception as e:
            console.print(f"[red]Error switching to Greppy mode: {e}[/red]")
            return False

    def get_current_mode(self) -> str:
        """Determine which mode is currently active."""
        if not self.settings_file.exists():
            return "unknown"

        try:
            settings = self._load_settings(self.settings_file)

            if "mcpServers" in settings and settings["mcpServers"]:
                return "mcp"
            elif "permissions" in settings and "deny" in settings["permissions"]:
                return "greppy"
            else:
                return "custom"
        except Exception:
            return "unknown"

    def status(self):
        """Show current mode and configuration."""
        mode = self.get_current_mode()
        console.print(f"\n[bold cyan]Current Mode: {mode.upper()}[/bold cyan]\n")

        if mode == "mcp":
            console.print("[green]MCP Mode[/green]")
            console.print("[dim]Uses three specialized MCP tools:[/dim]")
            console.print("  - search_keyword - Fast keyword search (BM25)")
            console.print("  - search_semantic - Semantic search (embeddings)")
            console.print("  - search_hybrid - Balanced hybrid search")
            console.print()
            console.print("[yellow]Requirements:[/yellow]")
            console.print("  - HTTP server: python http_server.py")
            console.print("  - MCP server: python -m atlas.mcp_server")
        elif mode == "greppy":
            console.print("[green]Greppy Mode[/green]")
            console.print("[dim]Uses Greppy CLI with restricted native tools:[/dim]")
            console.print("  - atlas greppy search - Semantic/keyword search")
            console.print("  - atlas greppy exact - Pattern matching")
            console.print("  - atlas greppy read - File reading")
            console.print("  - atlas greppy index - Indexing")
            console.print()
            console.print("[yellow]Blocked tools:[/yellow]")
            console.print("  - Glob (directory listing)")
            console.print("  - Grep (file searching)")
            console.print("  - Read (file reading)")
            console.print()
            console.print("[dim]Use 'atlas greppy' commands for all code operations[/dim]")
        else:
            console.print(f"[yellow]Unknown mode: {mode}[/yellow]")
            console.print("[dim]Current settings.json:[/dim]")
            if self.settings_file.exists():
                with open(self.settings_file) as f:
                    console.print(f.read())

        console.print()

    def merge_settings(self, base_mode: Literal["mcp", "greppy"], extra: dict) -> dict:
        """Merge extra settings into a base mode.

        Useful for customizing a mode without replacing it entirely.
        """
        if base_mode == "mcp":
            settings = self._load_settings(self.mcp_settings)
        elif base_mode == "greppy":
            settings = self._load_settings(self.greppy_settings)
        else:
            raise ValueError(f"Unknown mode: {base_mode}")

        # Deep merge
        self._deep_merge(settings, extra)
        return settings

    @staticmethod
    def _deep_merge(target: dict, source: dict):
        """Deep merge source into target."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                ModeManager._deep_merge(target[key], value)
            else:
                target[key] = value
