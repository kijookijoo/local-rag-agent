from rich.panel import Panel
from rich.padding import Padding
from rich.text import Text

def print_atlas_banner(console) -> None:
    art = Text.from_markup(
                    r"""
            [bold cyan]                      ,----,   ,--,                             [/bold cyan]
            [bold blue]                    ,/   .`|,---.'|                             [/bold blue]
            [bold bright_cyan]   ,---,          ,`   .'  :|   | :      ,---,       .--.--.    [/bold bright_cyan]
            [bold magenta]  '  .' \       ;    ;     /:   : |     '  .' \     /  /    '.  [/bold magenta]
            [bold purple] /  ;    '.   .'___,/    ,' |   ' :    /  ;    '.  |  :  /`. /  [/bold purple]
            [bold cyan]:  :       \  |    :     |  ;   ; '   :  :       \ ;  |  |--`   [/bold cyan]
            [bold blue]:  |   /\   \ ;    |.';  ;  '   | |__ :  |   /\   \|  :  ;_     [/bold blue]
            [bold bright_cyan]|  :  ' ;.   :`----'  |  |  |   | :.'||  :  ' ;.   :\  \    `.  [/bold bright_cyan]
            [bold magenta]|  |  ;/  \   \   '   :  ;  '   :    ;|  |  ;/  \   \`----.   \ [/bold magenta]
            [bold purple]'  :  | \  \ ,'   |   |  '  |   |  ./ '  :  | \  \ ,'__ \  \  | [/bold purple]
            [bold cyan]|  |  '  '--'     '   :  |  ;   : ;   |  |  '  '--' /  /`--'  / [/bold cyan]
            [bold blue]|  :  :           ;   |.'   |   ,/    |  :  :      '--'.     /  [/bold blue]
            [bold bright_cyan]|  | ,'           '---'     '---'     |  | ,'        `--'---'   [/bold bright_cyan]
            [bold magenta]`--''                                 `--''                     [/bold magenta]

            [bold cyan]                         Semantic Code Navigation[/bold cyan]
            """
    )

    console.print(
        Panel(
            Padding(art, (0, 2)),
            border_style="cyan",
            padding=(0, 1),
            title="[bold cyan]ATLAS[/bold cyan]",
            subtitle="[dim]Semantic Code Navigation[/dim]",
        )
    )
    
    console.print(
        Text("Aesthetic retrieval CLI for fast local exploration", style="dim")
    )
