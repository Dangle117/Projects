# Bouncing Balls Simulation (Pygame + NumPy)

This project is a physics-based bouncing ball simulation built with **Pygame** and **NumPy**.  
Balls move inside a rotating circular boundary, collide with the walls, and may escape through a spinning arc opening.

---

## ✨ Features

- 🟠 **Circular arena** with customizable radius  
- 🌀 **Rotating arc opening** where balls can escape  
- 🟡 **Multiple balls**, each with random colors and velocities  
- 🧮 **Physics simulation**:
  - Gravity  
  - Collision detection  
  - Tangential velocity and normal reflection  
- 🔄 **Automatic ball respawn** when a ball exits the screen

---

## 🧠 How It Works

### 1. **Balls Class**
Each ball stores:
- Position (`pos`)
- Velocity (`vel`)
- Random color
- A flag indicating if it's still inside the circle (`is_in`)

### 2. **Circular Arena**
- Centered on the screen  
- Fixed radius  
- Rendered as an outline using `pygame.draw.circle`

### 3. **Rotating Arc Opening**
- Defined by `start_angle` and `end_angle`
- Continuously rotates (`SPINNING_SPEED`)
- Drawn with a filled polygon

### 4. **Collision Physics**
When a ball hits the circle wall:
- It is projected back inside  
- A reflection vector is computed  
- Tangential velocity is applied to simulate rotation

### 5. **Ball Escape Logic**
If the angle of the ball relative to the center lies between the arc angle range, the ball is allowed to leave the circle.

---

## ▶️ How to Run

### **1. Install dependencies**
Make sure Python is installed, then run:

```bash
pip install pygame numpy
```

### 2. Run the program
```bash
python main.python
```

## 📸 Output
![output](example/Bouncing_Balls.gif)
