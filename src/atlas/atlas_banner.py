from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def print_atlas_banner(console: Console):
    dock = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣤⣄⠀⠀⠀⠀⠀⠀⠐⠛⠛⠂⠀⠀⠀⠀⠀⠀⣠⣤⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠙⢿⣷⡶⠀⣀⣴⣶⣾⣟⣻⣷⣶⣦⣀⠀⢶⣾⡿⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠘⠋⣠⢞⣿⠿⠛⠉⣉⣉⠉⛛⠿⣿⡳⣄⠙⠃⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣼⣿⡟⠁⣤⡀⠀⢹⡏⠀⢀⣤⠈⢻⣿⣧⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⠀⣸⣿⡟⠀⠀⠈⠻⠂⢈⡁⠐⠟⠁⠀⠀⢻⣿⣇⠀⡀⠀⠀⠀⠀
⠀⢾⣿⣿⣿⠀⣿⣹⡇⢸⡷⠶⠆⠰⣿⣿⠆⠰⠶⢾⡇⢸⣏⣿⠀⣿⣿⣿⡷⠀
⠀⠀⠀⠀⠈⠀⢹⣿⣧⠀⠀⢀⣴⠄⢈⡁⠠⣦⡀⠀⠀⣼⣿⡏⠀⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⢻⣿⣧⡀⠛⠁⠀⣸⣇⠀⠈⠛⢀⣼⣿⡟⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⣄⠙⢮⣿⣶⣤⣀⣉⣉⣀⣤⣶⣿⡵⠋⣠⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⣾⡿⠷⠀⠉⠻⠿⢿⣯⣽⡿⠿⠟⠉⠀⠾⢿⣷⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠛⠋⠀⠀⠀⠀⠀⠀⠠⣤⣤⠄⠀⠀⠀⠀⠀⠀⠙⠛⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

    atlas = r"""
                      ,----,   ,--,
                    ,/   .`|,---.'|
   ,---,          ,`   .'  :|   | :      ,---,       .--.--.
  '  .' \       ;    ;     /:   : |     '  .' \     /  /    '.
 /  ;    '.   .'___,/    ,' |   ' :    /  ;    '.  |  :  /`. /
:  :       \  |    :     |  ;   ; '   :  :       \ ;  |  |--`
:  |   /\   \ ;    |.';  ;  '   | |__ :  |   /\   \|  :  ;_
|  :  ' ;.   :`----'  |  |  |   | :.'||  :  ' ;.   :\  \    `.
|  |  ;/  \   \   '   :  ;  '   :    ;|  |  ;/  \   \`----.   \
'  :  | \  \ ,'   |   |  '  |   |  ./ '  :  | \  \ ,'__ \  \  |
|  |  '  '--'     '   :  |  ;   : ;   |  |  '  '--' /  /`--'  /
|  :  :           ;   |.'   |   ,/    |  :  :      '--'.     /
|  | ,'           '---'     '---'     |  | ,'        `--'---'
`--''                                 `--''
"""

    body = Table.grid(padding=(0, 2))
    body.add_column(justify="left", no_wrap=True)
    body.add_column(justify="left")
    body.add_row(
        Text.from_markup(f"[bold cyan]{dock}[/bold cyan]"),
        Text.from_markup(f"[bold blue]{atlas}[/bold blue]"),
    )

    console.print(
        Panel(
            Align.center(body),
            title="[bold cyan]ATLAS[/bold cyan]",
            subtitle="[dim]Fast local retrieval for code and knowledge.[/dim]",
            subtitle_align="center",
            border_style="cyan",
            box=box.SQUARE,
        )
    )
