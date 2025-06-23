from random import randint
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.spinner import Spinner

console = Console()

# Dice faces with colored dots
dices: dict[int, list[str]] = {
    1: ['┌─────────┐',
        '│         │',
        '│    [red]●[/red]    │',
        '│         │',
        '└─────────┘'],

    2: ['┌─────────┐',
        '│ [red]●[/red]       │',
        '│         │',
        '│       [red]●[/red] │',
        '└─────────┘'],

    3: ['┌─────────┐',
        '│ [red]●[/red]       │',
        '│    [red]●[/red]    │',
        '│       [red]●[/red] │',
        '└─────────┘'],

    4: ['┌─────────┐',
        '│ [red]●[/red]     [red]●[/red] │',
        '│         │',
        '│ [red]●[/red]     [red]●[/red] │',
        '└─────────┘'],

    5: ['┌─────────┐',
        '│ [red]●[/red]     [red]●[/red] │',
        '│     [red]●[/red]   │',
        '│ [red]●[/red]     [red]●[/red] │',
        '└─────────┘'],

    6: ['┌─────────┐',
        '│ [red]●[/red]     [red]●[/red] │',
        '│ [red]●[/red]     [red]●[/red] │',
        '│ [red]●[/red]     [red]●[/red] │',
        '└─────────┘']
}


def dice_shuffling(dice_list: list[int]) -> None:
    console.print("\n[bold yellow]Rolling the dice...[/bold yellow]")
    
    with console.status("[bold green]Shuffling dice...[/bold green]", spinner="dots"):
        sleep(2)

    dice_art_lines = [""] * 5
    for line in range(5):
        for dice in dice_list:
            dice_art_lines[line] += dices[dice][line] + "  "

    art = "\n".join(dice_art_lines)
    panel = Panel(Align.center(art), title="🎲 Your Dice 🎲", border_style="bright_blue")
    console.print(panel)


def running() -> None:
    while True:
        try:
            guest: int = int(console.input("[bold cyan]How many dice? [/bold cyan]"))
            if guest < 1:
                console.print("[red]You must roll at least one die![/red]")
                continue

            dice_num: list[int] = [randint(1, 6) for _ in range(guest)]
            total = sum(dice_num)

            dice_shuffling(dice_num)

            result_text = Text(f"\n🎲 Total: {total}\n", style="bold green on black", justify="center")
            console.print(result_text)
            break

        except ValueError:
            console.print("[bold red]Invalid input! Please enter a number.[/bold red]")


def main() -> None:
    console.rule("[bold blue]🎲 Dice Roller 🎲")
    running()
    console.rule("[green]Thanks for playing![/green]")


if __name__ == '__main__':
    main()