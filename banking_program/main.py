from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, FloatPrompt
from rich import print

console = Console()

# Option 1: Show balance
def show_balance(balance: float) -> None:
    panel = Panel(f"[bold green]${balance:.2f}[/bold green]", title="[bold blue]Your Balance[/bold blue]", expand=False)
    console.print(panel)

# Option 2: Deposit money
def deposit() -> float:
    try:
        guest_money = FloatPrompt.ask("[bold yellow]Enter the amount you want to deposit[/bold yellow]", default=0.0)
        if guest_money < 0:
            console.print("[bold red]❌ INVALID MONEY[/bold red]")
            return 0.0
        return guest_money
    except ValueError:
        console.print("[bold red]❌ Please enter a valid number[/bold red]")
        return 0.0

# Option 3: Withdraw money
def withdraw(balance: float) -> float:
    try:
        guest_money = FloatPrompt.ask("[bold yellow]Enter the amount you want to withdraw[/bold yellow]", default=0.0)
        if guest_money < 0:
            console.print("[bold red]❌ INVALID MONEY[/bold red]")
            return 0.0
        elif balance >= guest_money:
            return -guest_money
        else:
            console.print("[bold red]💸 Not enough funds. Please deposit first.[/bold red]")
            return 0.0
    except ValueError:
        console.print("[bold red]❌ Please enter a valid number[/bold red]")
        return 0.0

# Option 4: Exit program
def exit_program() -> bool:
    console.print("[bold cyan]👋 Exiting the program. Have a nice day![/bold cyan]")
    return False

# Menu layout
def print_layout() -> None:
    console.print(Panel.fit("""
[bold cyan]ATM MENU[/bold cyan]
[green]1.[/green] Show Balance
[green]2.[/green] Deposit
[green]3.[/green] Withdraw
[green]4.[/green] Exit
""", title="💰 [bold magenta]Welcome to Dangle Bank[/bold magenta]", border_style="bright_blue"))

# Main loop
def running() -> None:
    is_running = True
    user_wallet: float = 0.0

    while is_running:
        sleep(1)
        print_layout()
        try:
            guest = IntPrompt.ask("[bold white]Enter your choice (1-4)[/bold white]", choices=["1", "2", "3", "4"])
            match guest:
                case 1:
                    show_balance(user_wallet)
                case 2:
                    user_wallet += deposit()
                case 3:
                    user_wallet += withdraw(user_wallet)
                case 4:
                    is_running = exit_program()
        except Exception as e:
            console.print(f"[bold red]❌ ERROR:[/bold red] {e}")
            is_running = False

# Entry point
def main() -> None:
    running()

if __name__ == '__main__':
    main()
