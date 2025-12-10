# 🎮 2048 Terminal Game with Python

This is a fully-featured **2048 clone in the terminal**, built with:

- 🐍 **Python** for core game logic
- 🎨 **Rich** for beautiful, colorful terminal output
- 🤖 A simple heuristic **AI autoplay mode**

---

## 🚀 Features

✅ Classic 4x4 2048 gameplay  
✅ Pretty colors and board rendering in terminal  
✅ Random 2/4 spawning with realistic 10% chance for 4  
✅ Merge and slide logic just like original  
✅ Smart auto-play bot with simple heuristic (maximize empty cells + top-left priority)

---

## 🧠 AI Strategy
The built-in AI:
- Tries all four moves each turn
- Scores them by:
    - Number of empty cells
    - Bonus for large tiles in the top-left
- Picks the move with the highest score
- Ends when it wins or has no more moves.

---


## 🖥️ How to run

Install dependencies:

```bash
pip install rich
```

Run the game:

``` bash
python main.py
```