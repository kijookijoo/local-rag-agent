import typer
from rich.console import Console

from .atlas_banner import print_atlas_banner
from .commands.chat import chat_run
from .commands.index import index_run
from .greppy import Greppy
from .mode_manager import ModeManager

app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        print_atlas_banner(console)
        console.print("[dim]Use [bold]atlas chat[/bold], [bold]atlas index[/bold], or [bold]atlas greppy[/bold].[/dim]")


@app.command()
def index():
    index_run(show_banner=True)


@app.command()
def chat():
    chat_run(show_banner=True)


@app.command()
def dev():
    print_atlas_banner(console)
    index_run(show_banner=False)
    chat_run(show_banner=False)


# Mode management commands
mode_app = typer.Typer()
mm = ModeManager()


@mode_app.command()
def status():
    """Show current mode and configuration."""
    mm.status()


@mode_app.command()
def mcp():
    """Switch to MCP mode (three specialized tools for Claude)."""
    if mm.switch_to_mcp():
        console.print()
        console.print("[bold cyan]MCP Mode Setup:[/bold cyan]")
        console.print("1. Start the HTTP server: [bold]python http_server.py[/bold]")
        console.print("2. In another terminal, start MCP: [bold]python -m atlas.mcp_server[/bold]")
        console.print("3. Restart Claude Code")
        console.print("4. Claude will auto-discover the three tools")


@mode_app.command()
def greppy():
    """Switch to Greppy mode (CLI tool with restricted native tools)."""
    if mm.switch_to_greppy():
        console.print()
        console.print("[bold cyan]Greppy Mode Setup:[/bold cyan]")
        console.print("1. Restart Claude Code")
        console.print("2. Use 'atlas greppy' for all code operations:")
        console.print("   - atlas greppy search 'query'")
        console.print("   - atlas greppy exact 'pattern'")
        console.print("   - atlas greppy read file.py:45")
        console.print("3. Native tools (Glob, Grep, Read) are blocked")


# Greppy commands
greppy_app = typer.Typer()


@greppy_app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    n: int = typer.Option(10, "--limit", "-n", help="Max results (1-20)"),
    p: str = typer.Option(None, "--path", "-p", help="Project path"),
):
    """Semantic search using vector embeddings."""
    g = Greppy(p)
    results = g.search(query, limit=n, path=p)
    console.print(g.format_results(results, "semantic search"))


@greppy_app.command()
def exact(
    pattern: str = typer.Argument(..., help="Pattern to search (regex or string)"),
    i: bool = typer.Option(False, "--ignore-case", "-i", help="Case-insensitive"),
    n: int = typer.Option(20, "--limit", "-n", help="Max results"),
    p: str = typer.Option(None, "--path", "-p", help="Project path"),
):
    """Exact pattern matching using regex/keyword."""
    g = Greppy(p)
    results = g.exact(pattern, limit=n, path=p, ignore_case=i)
    console.print(g.format_results(results, "exact pattern match"))


@greppy_app.command()
def read(
    location: str = typer.Argument(..., help="File path or file.py:45 or file.py:30-80"),
    c: int = typer.Option(50, "--context", "-c", help="Lines of context"),
):
    """Read file contents with optional line range."""
    g = Greppy()
    try:
        content = g.read(location, context=c)
        console.print(content)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")


@greppy_app.command()
def index(
    path: str = typer.Argument(None, help="Directory to index"),
    force: bool = typer.Option(False, "--force", help="Force full reindex"),
):
    """Index a directory."""
    g = Greppy(path)
    g.index(path, force=force)


@greppy_app.command()
def watch(
    path: str = typer.Argument(None, help="Directory to watch"),
    debounce: int = typer.Option(5, "--debounce", "-d", help="Debounce seconds"),
):
    """Watch for file changes and auto-index."""
    g = Greppy(path)
    g.watch(path, debounce=debounce)


@greppy_app.command()
def status(
    path: str = typer.Argument(None, help="Project path"),
):
    """Show index status."""
    g = Greppy(path)
    g.status(path)


@greppy_app.command()
def clear():
    """Clear all indexes."""
    g = Greppy()
    if console.confirm("[red]Clear all indexes? This cannot be undone.[/red]"):
        g.clear()


app.add_typer(greppy_app, name="greppy", help="Greppy: Semantic code search CLI")
app.add_typer(mode_app, name="mode", help="Switch between MCP and Greppy modes")


if __name__ == "__main__":
    app()
