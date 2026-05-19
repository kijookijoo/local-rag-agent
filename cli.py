import typer
from commands.index import index_run
from commands.chat import chat_run


app = typer.Typer()

@app.command()
def index():
    index_run()

@app.command()
def chat():
    chat_run()

if __name__ == "__main__":
    app()