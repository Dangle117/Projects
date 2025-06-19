# 🔐 Strong Password Validator

A simple Python command-line program that checks whether a user-entered password meets common strength requirements. It ensures the password contains a mix of letters, numbers, and special characters for better security.

---

## 🚀 Features

- Checks for:
  - Minimum length of 8 characters
  - At least one lowercase letter
  - At least one uppercase letter
  - At least one digit
  - At least one special character (e.g. `!@#$%^&*()`)
- Gives clear feedback for missing requirements
- Uses the `rich` library for styled terminal output

---

## 🧠 How It Works

1. Prompts the user to enter a password.
2. Validates the input against a set of strength criteria.
3. Displays a message for each rule the password does not meet.
4. Confirms when a strong password is entered.

---

## 📦 Requirements

- Python 3.7+
- [`rich`](https://pypi.org/project/rich/) library for styled terminal output

### Install rich (if not installed):

```bash
pip install rich
```

## ▶️ Usage

Run the script from your terminal:

``` bash
python main.py
```

Example interaction:

``` bash
Enter a password: 12345
Password must be at least 8 characters Long.
--------------------------------------------

Enter a password: strongPASS
Password must contain at least one digit.
-----------------------------------------

Enter a password: StrongPass1!
Password is valid.

```

---

## 📌 Notes
- This is a basic validator, great for beginner-level Python practice.

- For real-world applications, use built-in libraries like `getpass` to hide user input, or integrate it into web forms with hashed storage.

---

## 📝 License

- This project is open source and available under the MIT License.