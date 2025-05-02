# 🐍 Automatic Snake Game with A* Pathfinding (Pygame)

This is an automatic Snake game implemented in **Python** using **Pygame** and powered by the **A\*** (A-star) pathfinding algorithm. The snake intelligently finds and follows the shortest path to the food using real-time A* path planning.

## 🎮 Features

- Fully automatic Snake controlled by A* pathfinding.
- Smooth grid-based animation with growing snake.
- Real-time food generation.
- Wall and self-collision detection.
- Optional path visualization (can be enabled in the code).
- Clean and readable Pygame structure.

## 🧠 How It Works

- The snake's head is treated as the A* start node.
- Food acts as the goal node.
- The snake's body (except head and tail) is considered as obstacles.
- A* finds the shortest path while avoiding collisions.
- The snake then follows this path step-by-step.

## 🖥️ Requirements

- Python 3.x
- Pygame

## 🔧 Installation

1. **Clone this repository or copy the script.**

2. **Install dependencies:**

```bash
pip install pygame
```
