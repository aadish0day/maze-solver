"""Maze Solver - AI course project.

Interactive maze generator + solver that visualises Breadth-First Search (BFS),
Depth-First Search (DFS) and A* Search, either individually or side-by-side.

Controls
--------
R           : generate a new maze
Enter/Space : solve with the selected algorithm (or all three in compare mode)
Esc / C     : stop / clear the current search
1, 2, 3     : pick BFS, DFS or A* (single mode)
Click       : edit the maze with the selected tool (Wall / Start / Goal)
"""

import sys

import pygame

from maze import Maze, generate_maze_animated
from solver import ALGORITHMS
from ui import Button, CheckBox, RadioGroup, Slider
from visualizer import (
    COL_ACCENT, COL_BORDER, COL_MUTED, COL_PANEL, COL_TEXT, WHITE,
    cell_at, draw_legend, draw_maze,
)

WINDOW_W, WINDOW_H = 1280, 800
SIDEBAR_X, SIDEBAR_W = 1000, 280
MAZE_AREA_W = WINDOW_W - SIDEBAR_W

ROWS, COLS = 21, 29
FPS = 60
SIDEBAR = (SIDEBAR_X, SIDEBAR_X + SIDEBAR_W)

ALGO_NAMES = ("BFS", "DFS", "A*")
TOOLS = ("Wall", "Start", "Goal")


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Maze Solver  |  BFS · DFS · A*  |  AI Course Project")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

        self.frozen = False
        self.message = ""
        self.msg_until = 0
        self.mouse_down = False
        self.last_paint = None

        # Game-world state
        self.maze = Maze(ROWS, COLS)
        self.start = (0, 0)
        self.end = (ROWS - 1 if (ROWS - 1) % 2 == 0 else ROWS - 2,
                    COLS - 1 if (COLS - 1) % 2 == 0 else COLS - 2)
        self.state = "generating"
        self.compare = False
        self.solvers = {}      #  name -> generator
        self.live = {}         #  name -> (visited, frontier, path)
        self.results = {}      #  name -> {"nodes","path","found","exhausted"}

        self._build_ui()
        self.new_maze()

    # ------------------------------------------------------------- UI setup
    def _build_ui(self):
        x, w = SIDEBAR_X + 14, SIDEBAR_W - 28

        self.btn_new = Button((x, 104, w, 34), "New Maze   (R)", self.new_maze)
        self.btn_solve = Button((x, 144, w, 34), "Solve   (Enter)", self.solve)
        self.btn_stop = Button((x, 184, w, 34), "Stop / Clear   (Esc)", self.stop)

        self.tool_group = RadioGroup(TOOLS, (x, 248, w, 22))
        self.mode_group = RadioGroup(("Single solver", "Compare all 3"),
                                     (x, 342, w, 22), on_change=self._mode_changed)
        self.algo_group = RadioGroup(ALGO_NAMES, (x, 414, w, 22))

        self.speed = Slider((x, 508, w, 24), 1, 8, 5,
                            fmt=lambda v: f"2^{v - 1}")
        self.cb_frontier = CheckBox((x, 536, w, 16), "Show frontier", True)
        self.cb_visited = CheckBox((x, 560, w, 16), "Show visited cells", True)

    # --------------------------------------------------------- UI callbacks
    def _mode_changed(self, index):
        self.compare = (index == 1)

    @property
    def algo_name(self):
        return ALGO_NAMES[self.algo_group.index]

    @property
    def steps_per_frame(self):
        return 2 ** (self.speed.value - 1)

    # ------------------------------------------------------------- actions
    def new_maze(self):
        self.maze = Maze(ROWS, COLS)
        self._gen = generate_maze_animated(ROWS, COLS, maze=self.maze)
        self.state = "generating"
        self.current_cell = None
        self.solvers.clear()
        self.live.clear()
        self.results.clear()
        self.stop_overlay()

    def stop_overlay(self):
        self.solvers.clear()
        self.live.clear()
        self.results.clear()

    def solve(self):
        if self.state not in ("interactive", "solved"):
            return
        if self.start == self.end:
            self.set_message("Move Start/Goal apart first.")
            return
        names = ALGO_NAMES if self.compare else (self.algo_name,)
        self.solvers = {n: ALGORITHMS[n](self.maze, self.start, self.end) for n in names}
        self.live = {}
        self.results = {n: {"nodes": 0, "path": 0, "found": False, "exhausted": False}
                        for n in names}
        self.state = "solving"

    def stop(self):
        if self.state in ("solving", "solved"):
            self.stop_overlay()
            self.state = "interactive"

    def set_message(self, text, ms=2200):
        self.message = text
        self.msg_until = pygame.time.get_ticks() + ms

    # --------------------------------------------------------- state machine
    def _advance_generation(self, steps):
        for _ in range(steps):
            try:
                self.current_cell = next(self._gen)
            except StopIteration:
                self.state = "interactive"
                self.current_cell = None
                return

    def _step_solvers(self, steps):
        for name in list(self.solvers):
            gen = self.solvers[name]
            done = False
            for _ in range(steps):
                try:
                    visited, frontier, path = next(gen)
                except StopIteration:
                    done = True
                    break
                self.live[name] = (visited, frontier, path)
                res = self.results[name]
                if len(visited) > res["nodes"]:
                    res["nodes"] = len(visited)
                if path is not None:
                    res["found"] = True
                    res["path"] = len(path) - 1
            if done:
                res = self.results[name]
                if res["found"] and res["path"] == 0:
                    res["path"] = 0
                del self.solvers[name]
        if not self.solvers:
            self.state = "solved"

    # ------------------------------------------------------------ rendering
    def _pane_rects(self):
        if not self.compare:
            return [pygame.Rect(6, 6, MAZE_AREA_W - 12, WINDOW_H - 12)]
        gap, margin = 6, 6
        w = (MAZE_AREA_W - 2 * margin - 2 * gap) // 3
        return [pygame.Rect(margin + i * (w + gap), 6, w, WINDOW_H - 12)
                for i in range(3)]

    def _overlay(self, name):
        if self.state in ("solving", "solved") and name in self.live:
            v, f, p = self.live[name]
            return (v if self.cb_visited.checked else None,
                    f if self.cb_frontier.checked else None, p)
        return None, None, None

    def _draw_panels(self):
        panes = self._pane_rects()
        if self.compare:
            titles = ALGO_NAMES
        else:
            titles = (self.algo_name,)

        gen_overlay = self.state == "generating"
        for rect, title in zip(panes, titles):
            visited, frontier, path = self._overlay(title)
            current = self.current_cell if gen_overlay else None
            draw_maze(self.screen, self.font, title, self.maze, rect,
                      start=self.start, end=self.end,
                      visited=visited, frontier=frontier, path=path,
                      current=current)

    def _draw_sidebar(self):
        x, w = SIDEBAR_X, SIDEBAR_W
        pygame.draw.rect(self.screen, (30, 33, 42), (x, 0, w, WINDOW_H))
        pygame.draw.line(self.screen, COL_BORDER, (x, 0), (x, WINDOW_H), 2)

        title = self.font_title.render("MAZE SOLVER", True, COL_TEXT)
        self.screen.blit(title, (x + 14, 14))
        sub = self.font_small.render("BFS  ·  DFS  ·  A*   |   AI Project", True, COL_MUTED)
        self.screen.blit(sub, (x + 14, 46))

        self._draw_status(x + 14, 76)
        pygame.draw.rect(self.screen, COL_BORDER, (x + 10, 98, w - 20, 2))

        for btn in (self.btn_new, self.btn_solve, self.btn_stop):
            btn.enabled = True
            if btn is self.btn_solve and self.state not in ("interactive", "solved"):
                btn.enabled = False
            if btn is self.btn_stop and self.state not in ("solving", "solved"):
                btn.enabled = False
            btn.draw(self.screen, self.font)

        self._label(x + 14, 226, "EDIT TOOL")
        self.tool_group.draw(self.screen, self.font)
        self._label(x + 14, 318, "SOLVER MODE")
        self.mode_group.draw(self.screen, self.font)

        self._label(x + 14, 390, "ALGORITHM")
        self.algo_group.enabled = not self.compare
        self.algo_group.draw(self.screen, self.font)

        self._label(x + 14, 484, "SPEED")
        self.speed.draw(self.screen, self.font)
        speed_text = self.font_small.render(f"{2 ** (self.speed.value - 1)} steps/frame",
                                            True, COL_MUTED)
        self.screen.blit(speed_text, (x + 118, 482))

        self.cb_frontier.enabled = self.state in ("solving", "solved")
        self.cb_visited.enabled = self.state in ("solving", "solved")
        self.cb_frontier.draw(self.screen, self.font)
        self.cb_visited.draw(self.screen, self.font)

        self._draw_stats(pygame.Rect(x + 14, 594, SIDEBAR_W - 28, 140))
        draw_legend(self.screen, self.font_small, pygame.Rect(x + 14, 760, SIDEBAR_W - 28, 40))

    def _label(self, x, y, text):
        img = self.font_small.render(text, True, COL_MUTED)
        self.screen.blit(img, (x, y))

    def _draw_status(self, x, y):
        if self.state == "generating":
            text, color = "Generating maze...", COL_ACCENT
        elif self.state == "interactive":
            text, color = "Ready. Edit & press Enter to solve.", COL_TEXT
        elif self.state == "solving":
            text, color = "Solving... (Esc to stop)", COL_ACCENT
        else:
            text, color = "Solved!", (150, 255, 160)
        img = self.font.render(text, True, color)
        self.screen.blit(img, (x, y))

        if self.message and pygame.time.get_ticks() < self.msg_until:
            warn = self.font_small.render(self.message, True, (255, 200, 90))
            self.screen.blit(warn, (x, y + 24))

    def _draw_stats(self, rect):
        pygame.draw.rect(self.screen, COL_PANEL, rect, border_radius=10)
        pygame.draw.rect(self.screen, COL_BORDER, rect, 1, border_radius=10)
        title = self.font_small.render("STATS", True, COL_MUTED)
        self.screen.blit(title, (rect.x + 8, rect.y + 6))

        names = ALGO_NAMES if self.compare else (self.algo_name,)
        y = rect.y + 28
        for name in names:
            res = self.results.get(name)
            if res is None:
                line = f"{name:>3}   -"
                status = ""
            else:
                line = f"{name:>3}   nodes {res['nodes']:>4}   path {res['path']}"
                if res["found"]:
                    status = "found"
                elif res["exhausted"]:
                    status = "no path"
                else:
                    status = "searching..."
            img = self.font.render(line, True, COL_TEXT)
            self.screen.blit(img, (rect.x + 8, y))
            if status:
                st = self.font_small.render(status, True, COL_MUTED)
                self.screen.blit(st, (rect.x + 8, y + 18))
            y += 44

        hint = self.font_small.render("A* explores the fewest cells.", True, COL_MUTED)
        self.screen.blit(hint, (rect.x + 8, rect.y + rect.height - 20))

    # ------------------------------------------------------- event handling
    def _handle_keydown(self, key):
        if key == pygame.K_r:
            self.new_maze()
        elif key in (pygame.K_KP_ENTER, pygame.K_RETURN, pygame.K_SPACE):
            self.solve()
        elif key in (pygame.K_ESCAPE, pygame.K_c):
            self.stop()
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3):
            if not self.compare:
                self.algo_group.index = {pygame.K_1: 0, pygame.K_2: 1,
                                         pygame.K_3: 2}[key]

    def _edit_cell(self, pos):
        if self.state != "interactive":
            return
        for pane in self._pane_rects():
            if not pane.collidepoint(pos):
                continue
            cell = cell_at(pos, pane, self.maze)
            if cell is None:
                return
            r, c = cell
            tool = self.tool_group.index
            if tool == 0:  # Wall
                if cell in (self.start, self.end):
                    self.set_message("Can't wall up Start/Goal.")
                    return
                self.maze.toggle(r, c)
                self.last_paint = cell
            elif tool == 1:  # Start
                if self.maze.walls[r][c]:
                    self.set_message("Start must be on an open cell.")
                    return
                self.start = cell
                self.last_paint = None
            else:  # Goal
                if self.maze.walls[r][c]:
                    self.set_message("Goal must be on an open cell.")
                    return
                self.end = cell
                self.last_paint = None
            self.stop_overlay()
            return

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self._handle_keydown(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down = True
                    handled = (self.btn_new.handle_event(event)
                               or self.btn_solve.handle_event(event)
                               or self.btn_stop.handle_event(event)
                               or self.tool_group.handle_event(event)
                               or self.mode_group.handle_event(event)
                               or self.algo_group.handle_event(event)
                               or self.speed.handle_event(event)
                               or self.cb_frontier.handle_event(event)
                               or self.cb_visited.handle_event(event))
                    if not handled:
                        self._edit_cell(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.btn_new.handle_event(event)
                    self.btn_stop.handle_event(event)
                    self.speed.handle_event(event)
                    if (self.mouse_down and self.state == "interactive"
                            and self.tool_group.index == 0):
                        self._edit_cell(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False
                    self.speed.handle_event(event)

            if self.state == "generating":
                self._advance_generation(self.steps_per_frame)
                if self.state == "interactive":
                    self.stop_overlay()
            elif self.state == "solving":
                self._step_solvers(self.steps_per_frame)

            self.screen.fill(WHITE)
            self._draw_panels()
            self._draw_sidebar()
            pygame.display.flip()


def main():
    Game().run()


if __name__ == "__main__":
    main()