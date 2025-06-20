import requests
from rich import print
from rich.panel import Panel
from rich.table import Table

path = "https://db.ygoprodeck.com/api/v7/cardinfo.php?name="

def get_card_data(name):
    url = f"{path}{name}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"[bold red]❌ ERROR {response.status_code}[/bold red]: Unable to fetch data.")
        return None


def clean_data(data):
    expected = ["id", "name", "type", "atk", "def", "level", "card_prices"]
    
    try:
        card = data["data"][0]
        print(Panel(f"[bold cyan]{card['name']}[/bold cyan]", title="🃏 Card Name", style="bold green"))

        for key in expected:
            if key in card:
                value = card[key]

                if key == "card_prices":
                    print("\n[bold underline green]💰 Card Prices:[/bold underline green]")
                    table = Table(title="Market Prices", show_header=True, header_style="bold magenta")
                    table.add_column("Market")
                    table.add_column("Price (USD)", justify="right")

                    for market, cost in value[0].items():
                        table.add_row(market, f"${cost}")
                    print(table)

                elif type(value) is int:
                    print(f"[bold yellow]{key.capitalize()}[/bold yellow]: [cyan]{value}[/cyan]")

                else:
                    print(f"[bold yellow]{key.capitalize()}[/bold yellow]: [bold white]{value}[/bold white]")
                    
    except (TypeError, KeyError):
        print("[bold red]⚠️ Error: Invalid data format[/bold red]")


def main():
    print(Panel("[bold blue]Welcome to Yu-Gi-Oh! Card Info Lookup[/bold blue]", subtitle="Powered by YGOPRODeck API", style="bold purple"))
    
    name_card = input("🔍 Enter your card name: ").capitalize()
    card_data = get_card_data(name=name_card)

    if card_data:
        clean_data(data=card_data)
    else:
        print("[bold red]Card not found or API error.[/bold red]")


if __name__ == "__main__":
    main()
