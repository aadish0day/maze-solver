# Maze Solver

Interactive maze generator and pathfinding visualizer built with Python and Pygame. Watch BFS, DFS, and A* algorithms solve mazes in real time — either one at a time or all three side by side.

## Features

- **Animated maze generation** using recursive backtracking
- **Three pathfinding algorithms**: BFS, DFS, and A*
- **Side-by-side comparison** of all three algorithms at once
- **Interactive editing** — click to add/remove walls, move start/goal
- **Adjustable speed** — control how fast the search progresses
- **Live stats** — see visited cells and path length per algorithm

## Controls

| Key / Action       | Description                              |
| ------------------ | ---------------------------------------- |
| `R`                | Generate a new maze                      |
| `Enter` / `Space`  | Solve with selected algorithm            |
| `Esc` / `C`        | Stop / clear current search              |
| `1`, `2`, `3`      | Select BFS, DFS, or A* (single mode)     |
| Left click / drag  | Edit maze (wall, start, goal)            |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame-ce
python main.py
```

## Project Structure

| File           | Description                                         |
| -------------- | --------------------------------------------------- |
| `main.py`      | Game loop, UI layout, event handling                |
| `maze.py`      | Maze data structure and recursive backtracking generator |
| `solver.py`    | BFS, DFS, and A* solver implementations (generators) |
| `ui.py`        | Reusable Pygame widgets (buttons, sliders, radio groups) |
| `visualizer.py`| Drawing routines for the maze grid and sidebar      |
