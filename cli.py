import typer
from commands.index import index_run
from commands.chat import chat_run
from atlas_banner import print_atlas_banner
from rich.console import Console


app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        print_atlas_banner(console)
        console.print("[dim]Use [bold]atlas chat[/bold] or [bold]atlas index[/bold].[/dim]")

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

if __name__ == "__main__":
    app()
