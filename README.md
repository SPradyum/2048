# 🧩 Enhanced 2048 Game (Python + Tkinter)

A fully upgraded and feature-rich version of the classic **2048 puzzle game**, built using Python and Tkinter.  
Designed with clean architecture, modern UI layout, and several extra functionalities that improve gameplay and usability.

---

## 🚀 Features

### 🎮 Gameplay Enhancements
- Smooth and responsive movement
- Undo last move (1-step undo)
- Move counter
- Dynamic score tracking
- Persistent **Best Score** saved locally
- Configurable **Target Tile** (2048 / 4096 / 8192)

### 🖥️ GUI Improvements
- Full Tkinter-based graphical interface  
- Neatly structured layout (board → controls → keypad → status)
- Centered board with well-spaced tiles  
- On-screen arrow controls in addition to keyboard input  
- Tile animations (simple flash feedback on merges)

### ⚙️ Technical Highlights
- Clean OOP structure (Board + Game + App classes)
- Grid logic (merge, compress, transpose, reverse)
- Automatic game-over and victory detection
- Local storage of best score using JSON
- Fully self-contained Python file (no external dependencies)

---

## ▶️ How to Run

### Requirements
- Python **3.8+**
- No external libraries needed (Tkinter is built-in)

### Run the game:
```bash
python main.py
```

---

## 🎮 Controls

### Keyboard:
| Key | Action |
|-----|--------|
| ← | Move Left |
| → | Move Right |
| ↑ | Move Up |
| ↓ | Move Down |

### On-screen buttons (mouse):
- Arrow keypad under the grid  
- New Game / Undo / Reset Best / Set Target

---

## 🏆 Game Rules

- Combine tiles with matching numbers to create larger tiles.
- Your objective is to reach the **target tile** (default: 2048).
- If no moves remain, the game ends.
- Try to beat your **Best Score**!

---


## 📚 Learning Benefits

This project is excellent for practicing:
- Tkinter GUI development  
- Object-Oriented Programming (OOP)  
- Event handling & keyboard bindings  
- Game development logic  
- Data storage using JSON  
- UI layout management in Python  

---

## 🤝 Contributing

Pull requests and constructive feedback are always welcome.

---

## ⭐ Support  
If you enjoyed this project, please give the repo a **⭐ star** on GitHub!

