from rich import print
import random

def mastermind_game() -> None:
    
    num: str = str(random.randint(1000,9999))
    hide_digit: str = "X" * 4
    
    list_hd: list[str] = list(hide_digit)
    print(f"[bold yellow]{hide_digit} [/bold yellow]", end="\n\n")
    
    guess = input("guess the number today: ")
    guess_count: int = 0
    
    while not guess.isnumeric():
        print("[bold red]This is not a number! [/bold red]")
        guess = input("guess the number today: ")
        
    while len(guess) != 4:
        print("Enter [bold green]the number[/bold green] from 1000 to 9999!")
        guess = input("guess the number today: ")
        
        
    while guess != num:
        for i, n in enumerate(guess):
            if n == num[i]:
                list_hd[i] = n 
                
        hide_digit = ''.join(list_hd)        
        guess_count += 1
        
        print(f"[bold yellow]{hide_digit} [/bold yellow]", end="\n\n")
        guess = input("guess the 4 digit number: ")
        
        while not guess.isnumeric():
            print("[bold red]This is not a number! [/bold red]")
            guess = input("guess the number today: ")
        
        while len(guess) != 4:
            print("Enter [bold green]the number[/bold green] from 1000 to 9999!")
            guess = input("guess the number today: ")
        
        hide_digit: str = "X" * 4
        list_hd = list(hide_digit)
    
    print(f"[green]{num}[/green]")
    print("[bold green]You've become a Mastermind.[/bold green]")
    print(f"It took you only {guess_count} tries.")
    
    
    if guess_count == 1:
        print("Great! You guessed the number in just 1 try! You're a Mastermind!")

def main():
    mastermind_game()


if __name__ == "__main__":
    main()

