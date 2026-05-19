import typer
from commands.index import index_run
from commands.chat import chat_run
from atlas_banner import print_atlas_banner
from rich.console import Console


app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    print_atlas_banner(console)
    if ctx.invoked_subcommand is None:
        console.print("[dim]Use [bold]rag chat[/bold] or [bold]rag index[/bold].[/dim]")

@app.command()
def index():
    index_run()

@app.command()
def chat():
    chat_run()

if __name__ == "__main__":
    app()
