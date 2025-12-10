from string import ascii_lowercase, ascii_uppercase, digits
from rich import print

lowercase = str(ascii_lowercase)
uppercase = str(ascii_uppercase)
digits = str(digits)
special_characters = "!@#$%^&*()-_=+[]{}|;:',.<>?/~`"   



def strong_password() -> None:
    while True:
        # Get user input for password
        password: str = input("Enter a password: ")
        
        # Checking the quality of the password
        if len(password) < 8: 
            print("Password must be at least 8 characters Long.")
            print("--------------------------------------------")
        
        elif not any(char in lowercase for char in password):
            print("Password must contain at least one lowercase letter.")
            print("-----------------------------------------------------")
        
        elif not any(char in uppercase for char in password):
            print("Password must contain at least one uppercase letter.")
            print("----------------------------------------------------")
            
        elif not any(char in digits for char in password):
            print("Password must contain at least one digit.")
            print("-----------------------------------------")
            
        elif not any(char in special_characters for char in password):
            print("Password must contain at least one special character.")
            print("-----------------------------------------------------")
            
        else:
            print("Password is valid.")
            break


def main() -> None:
    strong_password()    

if __name__ == '__main__':
    main()