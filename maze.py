"""Maze data structure and maze generation via recursive backtracking.

A maze is a grid (rows x cols) where each cell is either a wall (True) or an
open passage (False). The generator carves passages by "stepping by 2", which
produces perfect mazes with 1-cell thick walls.
"""

import random

# (dr, dc) for the four cardinal directions
DIRS = [(0, -1), (-1, 0), (0, 1), (1, 0)]


class Maze:
    """Rectangular grid of wall / open cells."""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.walls = [[True] * cols for _ in range(rows)]

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_open(self, r, c):
        return self.in_bounds(r, c) and not self.walls[r][c]

    def carve(self, r, c):
        self.walls[r][c] = False

    def toggle(self, r, c):
        self.walls[r][c] = not self.walls[r][c]

    def get_open_neighbors(self, r, c, order=None):
        """Return the list of open neighbours of (r, c)."""
        dirs = order if order is not None else DIRS
        result = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if self.is_open(nr, nc):
                result.append((nr, nc))
        return result


def generate_maze_animated(rows, cols, maze=None, rng=None):
    """Carve a perfect maze into `maze` one step at a time.

    Uses the iterative version of recursive backtracking (explicit stack) so it
    never hits Python's recursion limit, and it is written as a generator so the
    caller can animate the carving process.

    Yields the (row, col) of the cell currently being carved.
    """
    rng = rng or random
    if maze is None:
        maze = Maze(rows, cols)

    # The step-by-2 carving means the maze "nodes" live on even-even cells.
    even_rows = [r for r in range(rows) if r % 2 == 0]
    even_cols = [c for c in range(cols) if c % 2 == 0]

    visited = [[False] * cols for _ in range(rows)]
    start = (0, 0)  # anchored so the start cell is always an open node
    stack = [start]
    visited[start[0]][start[1]] = True
    maze.carve(*start)
    yield start

    while stack:
        r, c = stack[-1]
        candidates = []
        for dr, dc in ((0, 2), (2, 0), (0, -2), (-2, 0)):
            nr, nc = r + dr, c + dc
            if (
                nr % 2 == 0 and nc % 2 == 0
                and maze.in_bounds(nr, nc)
                and not visited[nr][nc]
            ):
                candidates.append((nr, nc, dr // 2, dc // 2))

        if candidates:
            nr, nc, wr, wc = rng.choice(candidates)
            maze.carve(r + wr, c + wc)  # pass through the wall
            maze.carve(nr, nc)          # carve the node
            visited[nr][nc] = True
            stack.append((nr, nc))
            yield (nr, nc)
        else:
            stack.pop()  # backtrack


def generate_maze(rows, cols):
    """Carve a perfect maze and return the finished Maze object."""
    maze = Maze(rows, cols)
    for _ in generate_maze_animated(rows, cols, maze=maze):
        pass
    return maze