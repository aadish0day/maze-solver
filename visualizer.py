"""Everything related to drawing the maze and the game panels."""

import pygame

WHITE = (26, 28, 36)          # window background
COL_WALL = (58, 63, 78)       # wall cells
COL_OPEN = (216, 218, 226)    # open passage
COL_VISITED = (92, 150, 255)  # visited / explored cells
COL_FRONTIER = (70, 215, 240) # frontier (currently in the queue / stack / heap)
COL_PATH = (255, 208, 74)     # final solution path
COL_START = (88, 214, 122)    # start cell
COL_END = (245, 96, 96)       # end cell
COL_CURRENT = (255, 130, 110) # carving cursor during generation
COL_TEXT = (232, 232, 240)
COL_MUTED = (150, 155, 165)
COL_ACCENT = (120, 170, 255)
COL_PANEL = (35, 38, 48)
COL_BORDER = (72, 77, 92)

HEADER = 30  # vertical space reserved for a panel title


def grid_layout(grid_rect, maze):
    """Work out where the grid is drawn inside a panel rect.

    Returns (origin_x, origin_y, cell_size) so drawing and mouse hit-testing
    share exactly the same math.
    """
    inner = grid_rect.inflate(-16, -16)
    cell = max(1, min(inner.width // maze.cols, inner.height // maze.rows))
    gw, gh = cell * maze.cols, cell * maze.rows
    ox = inner.x + (inner.width - gw) // 2
    oy = inner.y + (inner.height - gh) // 2
    return ox, oy, cell


def cell_at(pos, panel_rect, maze):
    """Map a mouse position to a maze cell inside a panel, or None."""
    grid_rect = pygame.Rect(panel_rect.x, panel_rect.y + HEADER,
                            panel_rect.width, panel_rect.height - HEADER)
    ox, oy, cell = grid_layout(grid_rect, maze)
    c = (pos[0] - ox) // cell
    r = (pos[1] - oy) // cell
    if maze.in_bounds(r, c):
        return r, c
    return None


def draw_maze(surface, font, title, maze, rect, start=None, end=None,
              visited=None, frontier=None, path=None, current=None):
    """Draw one maze panel (title + grid) into `rect`."""
    # Panel background + title
    pygame.draw.rect(surface, COL_PANEL, rect, border_radius=12)
    title_img = font.render(title, True, COL_TEXT)
    surface.blit(title_img, (rect.x + 12, rect.y + 5))

    grid_rect = pygame.Rect(rect.x, rect.y + HEADER, rect.width, rect.height - HEADER)
    ox, oy, cell = grid_layout(grid_rect, maze)

    for r in range(maze.rows):
        for c in range(maze.cols):
            x, y = ox + c * cell, oy + r * cell
            if maze.walls[r][c]:
                pygame.draw.rect(surface, COL_WALL, (x, y, cell, cell))
                continue
            color = COL_OPEN
            cell_pos = (r, c)
            if visited and cell_pos in visited:
                color = COL_VISITED
            if frontier and cell_pos in frontier:
                color = COL_FRONTIER
            if path and cell_pos in path:
                color = COL_PATH
            if start is not None and cell_pos == start:
                color = COL_START
            if end is not None and cell_pos == end:
                color = COL_END
            pygame.draw.rect(surface, color, (x, y, cell, cell))

    if current is not None:
        cr, cc = current
        pygame.draw.rect(surface, COL_CURRENT,
                         (ox + cc * cell, oy + cr * cell, cell, cell))


def draw_legend(surface, font, rect):
    """Small colour legend shown under the sidebar stats."""
    items = [("Start", COL_START), ("Goal", COL_END), ("Visited", COL_VISITED),
             ("Frontier", COL_FRONTIER), ("Path", COL_PATH), ("Wall", COL_WALL)]
    x, y = rect.x, rect.y
    for label, color in items:
        pygame.draw.rect(surface, color, (x, y, 14, 14))
        txt = font.render(label, True, COL_TEXT)
        surface.blit(txt, (x + 18, y))
        x += 96
        if x > rect.x + rect.width - 90:
            x = rect.x
            y += 20