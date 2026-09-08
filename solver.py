"""The three search algorithm solvers: BFS, DFS and A*.

Every solver is implemented as a *generator* so the visualizer can step the
search forward one cell at a time. Each ``yield`` exposes the current state:

    (visited_set, frontier_set, path_list)

``path_list`` is ``None`` until the goal is reached.
"""

import heapq
import itertools
from collections import deque

from maze import DIRS


def manhattan(a, b):
    """Admissible heuristic for 4-directional movement on a grid."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct(came_from, start, end):
    """Walk back through the came_from links to rebuild the solution path."""
    if end not in came_from:
        return []
    path = []
    cur = end
    while cur != start:
        path.append(cur)
        cur = came_from[cur]
    path.append(start)
    path.reverse()
    return path


def bfs_solve(maze, start, end):
    """Breadth-First Search -- queue (FIFO). Guarantees the shortest path."""
    visited = {start}
    came_from = {start: None}
    queue = deque([start])
    frontier = {start}
    while queue:
        cur = queue.popleft()
        frontier.discard(cur)
        if cur == end:
            yield visited, frontier, reconstruct(came_from, start, end)
            return
        for nb in maze.get_open_neighbors(*cur, order=DIRS):
            if nb not in visited:
                visited.add(nb)
                came_from[nb] = cur
                queue.append(nb)
                frontier.add(nb)
        yield visited, frontier, None
    yield visited, frontier, None  # no path found


def dfs_solve(maze, start, end):
    """Depth-First Search -- stack (LIFO). Explores one branch deep first."""
    order = DIRS[::-1]  # bias exploration in the opposite direction to BFS
    visited = {start}
    came_from = {start: None}
    stack = [start]
    frontier = {start}
    while stack:
        cur = stack.pop()
        frontier.discard(cur)
        if cur == end:
            yield visited, frontier, reconstruct(came_from, start, end)
            return
        for nb in maze.get_open_neighbors(*cur, order=order):
            if nb not in visited:
                visited.add(nb)
                came_from[nb] = cur
                stack.append(nb)
                frontier.add(nb)
        yield visited, frontier, None
    yield visited, frontier, None  # no path found


def astar_solve(maze, start, end):
    """A* Search -- priority queue (min-heap) with the Manhattan heuristic.

    Priority = g (cost from start) + h (manhattan distance to goal).
    """
    visited = set()
    came_from = {start: None}
    g_score = {start: 0}
    counter = itertools.count()  # tie-breaker so the heap never compares cells
    heap = [(manhattan(start, end), 0, next(counter), start)]
    frontier = {start}
    while heap:
        _, g, _, cur = heapq.heappop(heap)
        if cur in visited:
            frontier.discard(cur)
            yield visited, frontier, None
            continue
        visited.add(cur)
        frontier.discard(cur)
        if cur == end:
            yield visited, frontier, reconstruct(came_from, start, end)
            return
        for nb in maze.get_open_neighbors(*cur, order=DIRS):
            ng = g + 1
            if ng < g_score.get(nb, float("inf")):
                came_from[nb] = cur
                g_score[nb] = ng
                heapq.heappush(heap, (ng + manhattan(nb, end), ng, next(counter), nb))
                frontier.add(nb)
        yield visited, frontier, None
    yield visited, frontier, None  # no path found


ALGORITHMS = {
    "BFS": bfs_solve,
    "DFS": dfs_solve,
    "A*": astar_solve,
}