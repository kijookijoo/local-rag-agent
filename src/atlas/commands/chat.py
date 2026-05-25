import getpass
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from ..atlas_banner import print_atlas_banner
from ..bm25store import BM25Store
from ..rag import RAGAgent
from ..strategies.rag_fusion import RAGFusionStrategy
from ..vectorstore import VectorStore

load_dotenv()


def chat_run(show_banner: bool = True):
    console = Console()
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

    if show_banner:
        print_atlas_banner(console)
    console.print(
        Text("Type your question. Use ", style="dim")
        + Text("exit", style="bold")
        + Text(" or ", style="dim")
        + Text("quit", style="bold")
        + Text(" to leave.\n", style="dim")
    )

    llm = ChatOpenAI(
        model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
        temperature=0,
    )

    vectorstore = VectorStore()
    dense_retriever = vectorstore.as_retriever(k=20)
    bm25_retriever = BM25Store().as_retriever(k=20)
    strategy = RAGFusionStrategy(llm, dense_retriever, bm25_retriever)

    agent = RAGAgent(strategy, llm)
    chat_history = []

    while True:
        query = Prompt.ask("[bold cyan]You[/bold cyan]")
        if query.lower() in {"exit", "quit"}:
            break

        with console.status("[bold cyan]Searching context[/bold cyan]", spinner="dots"):
            retrievals = strategy.retrieve(query)
            response = agent.ask(query, chat_history=chat_history)

        console.print(
            Panel(
                Text(query, style="bold"),
                title="[bold cyan]You[/bold cyan]",
                border_style="cyan",
                padding=(0, 1),
            )
        )

        if retrievals:
            source_table = Table.grid(expand=True)
            source_table.add_column(ratio=1)
            source_table.add_row(Text("Retrieved context", style="bold magenta"))
            console.print(source_table)

            for idx, doc in enumerate(retrievals, start=1):
                excerpt = doc.page_content.strip()
                if len(excerpt) > 500:
                    excerpt = excerpt[:497].rstrip() + "..."
                console.print(
                    Panel(
                        excerpt,
                        title=f"[bold magenta]Source {idx}[/bold magenta]",
                        border_style="magenta",
                        padding=(0, 1),
                    )
                )

        console.print(
            Panel(
                response.strip(),
                title="[bold green]Assistant[/bold green]",
                border_style="green",
                padding=(0, 1),
            )
        )
        console.print(Rule(style="dim"))

        chat_history.append({"user": query, "assistant": response.strip()})
