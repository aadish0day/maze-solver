"""Reusable UI widgets built directly on pygame (no extra dependencies)."""

import pygame

COL_TEXT = (232, 232, 240)
COL_MUTED = (150, 155, 165)
COL_ACCENT = (120, 170, 255)
COL_PANEL = (35, 38, 48)
COL_PANEL_HI = (58, 64, 80)
COL_BORDER = (72, 77, 92)
COL_SELECTED = (105, 160, 255)


class Button:
    def __init__(self, rect, label, action=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.hover = False
        self.enabled = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.enabled
            and self.rect.collidepoint(event.pos)
        ):
            if self.action:
                self.action()
            return True
        return False

    def draw(self, surface, font):
        if not self.enabled:
            color = (30, 32, 40)
            border = COL_BORDER
        else:
            color = COL_PANEL_HI if self.hover else COL_PANEL
            border = COL_ACCENT if self.hover else COL_BORDER
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)
        text = font.render(self.label, True, COL_TEXT if self.enabled else COL_MUTED)
        surface.blit(text, text.get_rect(center=self.rect.center))


class RadioGroup:
    def __init__(self, options, rect, row_h=22, default=0, on_change=None):
        x, y, w, _ = rect
        self.options = list(options)
        self.index = default
        self.on_change = on_change
        self.enabled = True
        self.rects = [pygame.Rect(x, y + i * row_h, w, row_h) for i in range(len(options))]

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos) and self.index != i:
                    self.index = i
                    if self.on_change:
                        self.on_change(i)
                    return True
        return False

    def draw(self, surface, font):
        for i, opt in enumerate(self.options):
            r = self.rects[i]
            selected = (i == self.index)
            dot_col = COL_SELECTED if selected else COL_BORDER
            pygame.draw.circle(surface, dot_col, (r.x + 12, r.centery), 7, 2)
            if selected:
                pygame.draw.circle(surface, dot_col, (r.x + 12, r.centery), 3)
            color = COL_SELECTED if selected else (COL_TEXT if self.enabled else COL_MUTED)
            txt = font.render(opt, True, color)
            surface.blit(txt, (r.x + 26, r.y))


class Slider:
    def __init__(self, rect, min_v, max_v, value, fmt=None):
        self.rect = pygame.Rect(rect)
        self.min = min_v
        self.max = max_v
        self.value = value
        self.dragging = False
        self.fmt = fmt or (lambda v: str(v))

    def handle_event(self, event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ):
            self.dragging = True
            self._set_from_pos(event.pos[0])
            return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_pos(event.pos[0])
            return True
        return False

    def _set_from_pos(self, x):
        frac = (x - self.rect.x) / max(self.rect.width, 1)
        frac = max(0.0, min(1.0, frac))
        self.value = round(self.min + frac * (self.max - self.min))

    def draw(self, surface, font):
        pygame.draw.rect(surface, COL_PANEL, self.rect, border_radius=11)
        pygame.draw.rect(surface, COL_BORDER, self.rect, 2, border_radius=11)
        frac = (self.value - self.min) / max(self.max - self.min, 1)
        knob_x = self.rect.x + int(frac * self.rect.width)
        pygame.draw.circle(surface, COL_ACCENT, (knob_x, self.rect.centery), 12)


class CheckBox:
    def __init__(self, rect, label, default=True):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.checked = default
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.checked = not self.checked
            return True
        return False

    def draw(self, surface, font):
        color = COL_SELECTED if self.checked else COL_BORDER
        pygame.draw.rect(surface, color, (self.rect.x, self.rect.y, 15, 15), 2, border_radius=4)
        if self.checked:
            pygame.draw.rect(surface, color, (self.rect.x + 3, self.rect.y + 3, 9, 9), border_radius=2)
        txt = font.render(self.label, True, COL_TEXT if self.enabled else COL_MUTED)
        surface.blit(txt, (self.rect.x + 23, self.rect.y))