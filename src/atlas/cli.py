import typer
from rich.console import Console

from .atlas_banner import print_atlas_banner
from .commands.chat import chat_run
from .commands.index import index_run
from .greppy import Greppy

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


if __name__ == "__main__":
    app()
