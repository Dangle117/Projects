# 🧠 Mastermind Game (Terminal Edition)

A simple terminal-based number guessing game built with Python.  
The goal? Uncover a **4-digit secret number** one digit at a time — just like in the classic *Mastermind* game!

---

## 🎮 How to Play

- The computer generates a **random 4-digit number** between 1000 and 9999.
- Your job is to **guess the number**.
- After each guess:
  - Correct digits in the correct positions are **revealed**.
  - All other digits remain hidden as `"X"`.
- You’ll keep guessing until you reveal all four digits.

---

## 🧠 Example Gameplay

``` bash
XXXX

guess the number today: 1234
X2XX

guess the 4 digit number: 7234
72XX

guess the 4 digit number: 7239
723X

guess the 4 digit number: 7231
7231
You've become a Mastermind.
It took you only 4 tries.
```

---

## 💡 Features

- 🎲 Random number generation (1000–9999)
- 📏 Input validation (number-only, 4 digits)
- 🎨 Styled terminal output using the [`rich`](https://pypi.org/project/rich/) library
- 🎯 Victory message with try count

---

## 📦 Requirements

- Python 3.7+
- `rich` library for terminal styling

### Install `rich`:

```bash
pip install rich
```

# ▶️ Run the Game

In your terminal:

``` bash
python main.py
```

## 📌 Notes

- If you guess the number in 1 try, you'll unlock a special message 🎉

- Great project for practicing:

 - Input validation

 - Loops and conditions

 - Working with strings and lists

 - Terminal output formatting

