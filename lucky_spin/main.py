import random
import os
import time
from rich import print

def systems() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def spinning_game() -> None:
    print("----------------------------")
    print("[bold blue]WELCOME TO THE SPINNING GAME")
    print("----------------------------")

    symbols: list[str] = ['🍒', '🍋', '🍊', '🍉', '🍇', '🍓', '💎', '🔔']

    while True:
        player = input("Press Enter to spin (q to quit) > ")
        if player.lower() == 'q':
            print("[bold blue]Thanks for playing!")
            break

        for _ in range(10):
            a, b, c = random.choices(symbols, k=3)
            systems()
            print("     +--------+")
            print(f"     |{a}|{b}|{c}|")
            print("     +--------+")
            time.sleep(0.001)

        if a == b == c:
            print("-------------------------")
            print("[bold green]CONGRATULATIONS, YOU WON!")
            print("-------------------------")
        else:
            print("[bold yellow]Better luck next time!")

def main() -> None:
    spinning_game()

if __name__ == '__main__':
    main()
