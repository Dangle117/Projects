import random
from rich import print

def topic_game() -> tuple[str, list[str]]:
    # Topic game
    topics: dict[str, list[str]] = {
        # "Topic game": [words]
        "car_brand": [
            "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes", "Volkswagen",
            "Hyundai", "Kia", "Subaru", "Mazda", "Audi", "Lexus", "Porsche", "Jaguar"
        ],
        "fruits": [
            "Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape", "Honeydew",
            "Kiwi", "Lemon", "Mango", "Nectarine", "Orange", "Papaya", "Quince", "Raspberry"
        ],
        "drink_brands": [
            "Coca-Cola", "Pepsi", "Sprite", "Fanta", "Dr Pepper", "Mountain Dew", "Rockstar",
            "Red Bull", "Monster", "Starbucks", "Nescafe"
        ],
        "animals": [
            "Lion", "Tiger", "Elephant", "Giraffe", "Zebra", "Kangaroo", "Panda", "Koala",
            "Dolphin", "Whale", "Shark", "Penguin", "Eagle", "Falcon", "Owl", "Parrot"
        ],
        "fashion_brands": [
            "Nike", "Adidas", "Puma", "Reebok", "Under Armour", "New Balance", "Asics", "Vans",
            "Converse", "Zara", "Gucci", "Prada", "Chanel", "Louis Vuitton"
        ],
        "countries": [
            "United States", "Canada", "Mexico", "Brazil", "Argentina", "Chile", "Colombia", "Peru",
            "Venezuela", "Ecuador", "Bolivia", "Vietnam", "Uruguay", "China", "Russia", "France"
        ],
        "professions": [
            "Doctor", "Engineer", "Teacher", "Nurse", "Scientist", "Artist", "Musician", "Chef",
            "Writer", "Actor", "Lawyer", "Architect", "Journalist", "Photographer", "Programmer",
            "Designer"
        ],
        "sports": [
            "Soccer", "Basketball", "Tennis", "Baseball", "Cricket", "Rugby", "Hockey", "Golf",
            "Swimming", "Athletics", "Boxing", "Volleyball", "Badminton", "Cycling",
            "Wrestling"
        ]
    }

    topic = random.choice(list(topics.keys()))
    
    return topic , topics[topic] # (topic game, words)
 

def hangman_game() -> None:

    while True:        
        # Choose the topic
        topic, words = topic_game()
        
        # Choose randomly 1 word to guess
        word: str = random.choice(words).lower()
        hide_word: str = '_' * len(word) # Hiding the word
        
        # Design the header 
        print("-------------------------------------")
        print("WELCOME TO HANGMAN GAME (PYTHON CODE)")
        print(f"THE TOPIC TODAY IS: [bold purple]{topic.upper()}[/bold purple].")
        print(f"AND THE WORD TODAY HAS {len(word)} CHARACTERS!")
        print("-------------------------------------")
        
        print(f"word: [bold yellow]{hide_word}[/bold yellow]")

        # Create the way player fail to guess
        wrong_guesses: int = 0
        max_wrong: int = 5
        guessed_letter: set[str] = set()
        
        # Run hangman game
        while hide_word != word and wrong_guesses < max_wrong:
            print(f"you have {max_wrong - wrong_guesses} incorrect guesses left. ")
            
            guess: str = input("Enter a letter: ").lower()
            
            # Check if player type more than 1 or contain special words
            if len(guess) != 1 or not guess.isalpha():
                print("-------------------------------------------")
                print("Please enter a single alphabetic character.")
                continue
            
            # Check if player already typed that letter
            if guess in guessed_letter:
                print("--------------------------------")
                print("You already guessed that letter!")
                continue
            
            guessed_letter.add(guess)
            
            if guess in word:
                hide_word_list = list(hide_word)
                for i, c in enumerate(word):
                    if c == guess:
                        # Show the correct letter that player guess
                        hide_word_list[i] = guess
                
                hide_word = ''.join(hide_word_list)
            
            else:
                # increase by 1 if player guess wrong 
                wrong_guesses += 1
            
            # Design the terminal
            if wrong_guesses < max_wrong:
                print(f"\nword: [bold yellow]{hide_word}[/bold yellow]", end= '\n\n')
        
        # Show the word when you won or lose the game
        if hide_word ==  word:            
            print()
            print("----------------------------------")
            print("[bold green]          CONGRATULATION!         ")
            print("[bold green]         YOU WON THE GAME.        ")
            print("----------------------------------")
        else:
            print()
            print("-------------")
            print("[bold red]YOU FAILED :(")
            print(f"result: [bold yellow] {word}")
            print("-------------")

        # Ask player if they want to play again
        play_again: str = input("Do you want to play again: ")
        if play_again.lower() != 'y' and play_again.lower() != 'yes':
            print("[bold blue]SEE YOU LATER[/bold blue] 🖐️!")
            break

def main() -> None:
    hangman_game()
    
if __name__ == '__main__':
    main()