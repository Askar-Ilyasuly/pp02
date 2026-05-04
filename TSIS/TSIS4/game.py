# game.py — Snake Game core: snake, food, power-ups, obstacles, and all screens
#
# Architecture
# ────────────
#  SnakeGame        — top-level controller (state machine)
#  Snake            — movement, growth, collision
#  FoodManager      — normal, bonus, and poison food items
#  PowerupManager   — speed-boost, slow-motion, shield items
#  ObstacleManager  — static wall blocks (level 3+)
#  SettingsManager  — load/save settings.json
#  Various *Screen  — draw helpers for each game state

import pygame
import random
import json
import os
from dataclasses import dataclass, field
from typing import Optional

import config as C


# ══════════════════════════════════════════════════════════════════════════════
# Helper utilities
# ══════════════════════════════════════════════════════════════════════════════

def _cell_rect(col: int, row: int) -> pygame.Rect:
    """Convert grid coordinates to a pygame.Rect in pixel space."""
    return pygame.Rect(
        C.ARENA_X + col * C.CELL_SIZE,
        C.ARENA_Y + row * C.CELL_SIZE,
        C.CELL_SIZE,
        C.CELL_SIZE,
    )


def _draw_cell(surface: pygame.Surface, col: int, row: int,
               color: tuple, border: int = 2) -> None:
    """Draw a filled cell with a small inset border for a grid look."""
    rect = _cell_rect(col, row).inflate(-border, -border)
    pygame.draw.rect(surface, color, rect, border_radius=3)


def _random_cell(excluded: set[tuple[int, int]]) -> tuple[int, int]:
    """Pick a random grid cell not in *excluded*."""
    while True:
        col = random.randrange(C.GRID_COLS)
        row = random.randrange(C.GRID_ROWS)
        if (col, row) not in excluded:
            return col, row


# ══════════════════════════════════════════════════════════════════════════════
# Settings Manager
# ══════════════════════════════════════════════════════════════════════════════

class SettingsManager:
    """Load from / save to settings.json."""

    def __init__(self):
        self.data = dict(C.DEFAULT_SETTINGS)
        self._load()

    def _load(self):
        if os.path.exists(C.SETTINGS_FILE):
            try:
                with open(C.SETTINGS_FILE, "r") as f:
                    loaded = json.load(f)
                self.data.update(loaded)
            except Exception:
                pass

    def save(self):
        with open(C.SETTINGS_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    # Convenience properties
    @property
    def snake_color(self) -> tuple:
        return tuple(self.data["snake_color"])

    @snake_color.setter
    def snake_color(self, value: tuple):
        self.data["snake_color"] = list(value)

    @property
    def grid_overlay(self) -> bool:
        return bool(self.data["grid_overlay"])

    @grid_overlay.setter
    def grid_overlay(self, value: bool):
        self.data["grid_overlay"] = value

    @property
    def sound(self) -> bool:
        return bool(self.data["sound"])

    @sound.setter
    def sound(self, value: bool):
        self.data["sound"] = value


# ══════════════════════════════════════════════════════════════════════════════
# Snake
# ══════════════════════════════════════════════════════════════════════════════

class Snake:
    """Represents the player's snake."""

    DIRECTIONS = {
        pygame.K_UP:    (0,  -1),
        pygame.K_DOWN:  (0,   1),
        pygame.K_LEFT:  (-1,  0),
        pygame.K_RIGHT: (1,   0),
        pygame.K_w:     (0,  -1),
        pygame.K_s:     (0,   1),
        pygame.K_a:     (-1,  0),
        pygame.K_d:     (1,   0),
    }

    def __init__(self):
        self.reset()

    def reset(self):
        # Start in the middle, facing right
        mid_col = C.GRID_COLS // 2
        mid_row = C.GRID_ROWS // 2
        self.body: list[tuple[int, int]] = [
            (mid_col - i, mid_row) for i in range(C.INITIAL_SNAKE_LEN)
        ]
        self.direction   = (1, 0)
        self._next_dir   = (1, 0)
        self.shield_active = False
        self._grew       = False  # set when we should grow on next move

    # ── Input ──────────────────────────────────────────────────────────────────

    def handle_key(self, key: int):
        if key in self.DIRECTIONS:
            nd = self.DIRECTIONS[key]
            # Prevent 180° reversal
            if (nd[0] + self.direction[0], nd[1] + self.direction[1]) != (0, 0):
                self._next_dir = nd

    # ── Movement ───────────────────────────────────────────────────────────────

    def move(self) -> tuple[int, int]:
        """Advance the snake one cell.  Returns the new head position."""
        self.direction = self._next_dir
        head = (self.body[0][0] + self.direction[0],
                self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        if not self._grew:
            self.body.pop()
        self._grew = False
        return head

    def grow(self, segments: int = 1):
        """Queue growth by duplicating the tail."""
        for _ in range(segments):
            self.body.append(self.body[-1])

    def shorten(self, segments: int = 2):
        """Remove segments from the tail."""
        for _ in range(segments):
            if len(self.body) > 1:
                self.body.pop()

    # ── Collision ──────────────────────────────────────────────────────────────

    @property
    def head(self) -> tuple[int, int]:
        return self.body[0]

    def hits_wall(self) -> bool:
        col, row = self.head
        return not (0 <= col < C.GRID_COLS and 0 <= row < C.GRID_ROWS)

    def hits_self(self) -> bool:
        return self.head in self.body[1:]

    def hits_obstacle(self, obstacles: set[tuple[int, int]]) -> bool:
        return self.head in obstacles

    def occupied(self) -> set[tuple[int, int]]:
        return set(self.body)

    # ── Rendering ──────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, color: tuple, shield_active: bool):
        head_color = C.CYAN if shield_active else color
        dark = tuple(max(0, c - 60) for c in color)
        for i, (col, row) in enumerate(self.body):
            c = head_color if i == 0 else (color if i % 2 == 0 else dark)
            _draw_cell(surface, col, row, c)
        # Eyes on the head
        hc, hr = self.body[0]
        hr_rect = _cell_rect(hc, hr)
        eye_r = 3
        dx, dy = self.direction
        if dx == 1:    # right
            eyes = [(hr_rect.right-5, hr_rect.top+4), (hr_rect.right-5, hr_rect.bottom-6)]
        elif dx == -1: # left
            eyes = [(hr_rect.left+4, hr_rect.top+4), (hr_rect.left+4, hr_rect.bottom-6)]
        elif dy == -1: # up
            eyes = [(hr_rect.left+4, hr_rect.top+4), (hr_rect.right-6, hr_rect.top+4)]
        else:          # down
            eyes = [(hr_rect.left+4, hr_rect.bottom-6), (hr_rect.right-6, hr_rect.bottom-6)]
        for ex, ey in eyes:
            pygame.draw.circle(surface, C.WHITE, (ex, ey), eye_r)
            pygame.draw.circle(surface, C.BLACK, (ex, ey), eye_r-1)


# ══════════════════════════════════════════════════════════════════════════════
# Food item
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class FoodItem:
    col:     int
    row:     int
    kind:    str        # "normal" | "bonus" | "poison"
    points:  int
    spawn_time: int     # pygame.time.get_ticks() at creation
    ttl_ms:  int = 0    # 0 = permanent until eaten; >0 = disappear after ttl_ms

    @property
    def pos(self) -> tuple[int, int]:
        return (self.col, self.row)

    def is_expired(self, now: int) -> bool:
        return self.ttl_ms > 0 and (now - self.spawn_time) >= self.ttl_ms


class FoodManager:
    """Manages normal food, bonus food, and poison food."""

    def __init__(self):
        self.items: list[FoodItem] = []

    def occupied(self) -> set[tuple[int, int]]:
        return {f.pos for f in self.items}

    def spawn_normal(self, excluded: set):
        col, row = _random_cell(excluded | self.occupied())
        self.items.append(FoodItem(col, row, "normal", 10, pygame.time.get_ticks(), ttl_ms=0))

    def spawn_bonus(self, excluded: set):
        col, row = _random_cell(excluded | self.occupied())
        self.items.append(FoodItem(col, row, "bonus", 25, pygame.time.get_ticks(), ttl_ms=7000))

    def spawn_poison(self, excluded: set):
        col, row = _random_cell(excluded | self.occupied())
        self.items.append(FoodItem(col, row, "poison", 0, pygame.time.get_ticks(), ttl_ms=6000))

    def tick(self, now: int):
        """Remove expired food items."""
        self.items = [f for f in self.items if not f.is_expired(now)]

    def check_eat(self, head: tuple[int, int]) -> Optional[FoodItem]:
        for f in self.items:
            if f.pos == head:
                self.items.remove(f)
                return f
        return None

    def draw(self, surface: pygame.Surface):
        now = pygame.time.get_ticks()
        for f in self.items:
            color = C.FOOD_COLORS[f.kind]
            # Pulse effect based on time remaining
            if f.ttl_ms > 0:
                remaining = f.ttl_ms - (now - f.spawn_time)
                if remaining < 2000 and (now // 250) % 2 == 0:
                    color = C.WHITE  # blink when about to expire
            _draw_cell(surface, f.col, f.row, color)
            # Icon decoration
            cx = C.ARENA_X + f.col * C.CELL_SIZE + C.CELL_SIZE // 2
            cy = C.ARENA_Y + f.row * C.CELL_SIZE + C.CELL_SIZE // 2
            r  = C.CELL_SIZE // 4
            if f.kind == "bonus":
                pygame.draw.circle(surface, C.WHITE, (cx, cy), r)
            elif f.kind == "poison":
                pygame.draw.line(surface, C.RED, (cx-r, cy-r), (cx+r, cy+r), 2)
                pygame.draw.line(surface, C.RED, (cx+r, cy-r), (cx-r, cy+r), 2)


# ══════════════════════════════════════════════════════════════════════════════
# Power-up item
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PowerupItem:
    col:        int
    row:        int
    kind:       str     # "speed" | "slow" | "shield"
    spawn_time: int

    @property
    def pos(self) -> tuple[int, int]:
        return (self.col, self.row)

    def is_expired(self, now: int) -> bool:
        return (now - self.spawn_time) >= C.POWERUP_FIELD_MS


class PowerupManager:
    """Manages one on-field power-up and one active effect."""

    KINDS = ("speed", "slow", "shield")

    def __init__(self):
        self.field_item:   Optional[PowerupItem] = None
        self.active_kind:  Optional[str]  = None
        self.active_until: int = 0       # get_ticks() deadline

    def occupied(self) -> set[tuple[int, int]]:
        return {self.field_item.pos} if self.field_item else set()

    def try_spawn(self, excluded: set):
        """Randomly spawn a power-up if none is on the field."""
        if self.field_item is None and random.random() < C.POWERUP_SPAWN_CHANCE:
            col, row = _random_cell(excluded | self.occupied())
            kind = random.choice(self.KINDS)
            self.field_item = PowerupItem(col, row, kind, pygame.time.get_ticks())

    def tick(self, now: int):
        if self.field_item and self.field_item.is_expired(now):
            self.field_item = None
        if self.active_kind and now >= self.active_until:
            self.active_kind = None

    def check_collect(self, head: tuple[int, int]) -> Optional[str]:
        if self.field_item and self.field_item.pos == head:
            kind = self.field_item.kind
            self.field_item = None
            self.active_kind  = kind
            self.active_until = pygame.time.get_ticks() + C.POWERUP_DURATION_MS
            return kind
        return None

    def speed_multiplier(self) -> float:
        if self.active_kind == "speed": return 1.6
        if self.active_kind == "slow":  return 0.55
        return 1.0

    def shield_up(self) -> bool:
        return self.active_kind == "shield"

    def consume_shield(self):
        """Call when shield absorbs a collision."""
        self.active_kind = None

    def draw(self, surface: pygame.Surface):
        now = pygame.time.get_ticks()
        if not self.field_item:
            return
        f = self.field_item
        color = C.POWERUP_COLORS[f.kind]
        # Blink in last 2 s
        remaining = C.POWERUP_FIELD_MS - (now - f.spawn_time)
        if remaining < 2000 and (now // 200) % 2 == 0:
            color = C.WHITE
        _draw_cell(surface, f.col, f.row, color)
        # Symbol
        cx = C.ARENA_X + f.col * C.CELL_SIZE + C.CELL_SIZE // 2
        cy = C.ARENA_Y + f.row * C.CELL_SIZE + C.CELL_SIZE // 2
        r  = C.CELL_SIZE // 4
        if f.kind == "speed":
            pygame.draw.polygon(surface, C.WHITE, [(cx-r, cy-r), (cx+r, cy), (cx-r, cy+r)])
        elif f.kind == "slow":
            pygame.draw.rect(surface, C.WHITE, (cx-r, cy-r, r, r*2))
            pygame.draw.rect(surface, C.WHITE, (cx+1, cy-r, r, r*2))
        elif f.kind == "shield":
            pygame.draw.polygon(surface, C.WHITE,
                                [(cx, cy-r), (cx+r, cy-r//2), (cx+r, cy+r//2),
                                 (cx, cy+r), (cx-r, cy+r//2), (cx-r, cy-r//2)])


# ══════════════════════════════════════════════════════════════════════════════
# Obstacle Manager
# ══════════════════════════════════════════════════════════════════════════════

class ObstacleManager:
    """Randomly places static wall blocks from level 3 onward."""

    def __init__(self):
        self.blocks: set[tuple[int, int]] = set()

    def place_for_level(self, level: int, snake_occupied: set[tuple[int, int]]):
        """Add blocks for the given level (cumulative)."""
        if level < C.OBSTACLE_START_LEVEL:
            return
        count = C.OBSTACLES_PER_LEVEL
        attempts = 0
        while count > 0 and attempts < 500:
            attempts += 1
            col = random.randrange(C.GRID_COLS)
            row = random.randrange(C.GRID_ROWS)
            pos = (col, row)
            # Don't place on snake or existing blocks or within 3 cells of head
            hc, hr = next(iter(snake_occupied))
            if pos in snake_occupied:
                continue
            if pos in self.blocks:
                continue
            if abs(col - hc) <= 3 and abs(row - hr) <= 3:
                continue
            self.blocks.add(pos)
            count -= 1

    def reset(self):
        self.blocks.clear()

    def draw(self, surface: pygame.Surface):
        for (col, row) in self.blocks:
            rect = _cell_rect(col, row)
            pygame.draw.rect(surface, C.OBSTACLE_COLOR, rect, border_radius=2)
            pygame.draw.rect(surface, C.GRAY, rect, 1, border_radius=2)


# ══════════════════════════════════════════════════════════════════════════════
# UI Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _get_font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("consolas,monospace", size, bold=bold)


def _draw_text(surface, text, font, color, cx, cy, anchor="center"):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if anchor == "center":
        rect.center = (cx, cy)
    elif anchor == "topleft":
        rect.topleft = (cx, cy)
    elif anchor == "midleft":
        rect.midleft = (cx, cy)
    surface.blit(surf, rect)


class Button:
    """Simple clickable button."""

    def __init__(self, text: str, cx: int, cy: int, w: int = 200, h: int = 44):
        self.text  = text
        self.rect  = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self._font = _get_font(20, bold=True)

    def draw(self, surface: pygame.Surface, hovered: bool = False):
        color = C.CYAN   if hovered else C.DARK_GRAY
        border= C.WHITE  if hovered else C.GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)
        tc = C.BLACK if hovered else C.WHITE
        _draw_text(surface, self.text, self._font, tc,
                   self.rect.centerx, self.rect.centery)

    def is_hovered(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def is_clicked(self, pos: tuple[int, int], event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and self.rect.collidepoint(pos))


# ══════════════════════════════════════════════════════════════════════════════
# Main Game Controller
# ══════════════════════════════════════════════════════════════════════════════

class SnakeGame:
    """
    Top-level state machine.

    States: "menu" | "playing" | "gameover" | "leaderboard" | "settings"
    """

    def __init__(self, db, settings: SettingsManager):
        self.db       = db
        self.settings = settings
        self.screen   = pygame.display.get_surface()
        self.clock    = pygame.time.Clock()
        self.state    = "menu"

        # Fonts
        self.font_big   = _get_font(52, bold=True)
        self.font_med   = _get_font(28, bold=True)
        self.font_small = _get_font(18)
        self.font_tiny  = _get_font(14)

        # Menu username input
        self.username      = ""
        self.username_active = False

        # Game objects (created on play start)
        self.snake     : Optional[Snake]         = None
        self.food_mgr  : Optional[FoodManager]   = None
        self.pu_mgr    : Optional[PowerupManager] = None
        self.obs_mgr   : Optional[ObstacleManager] = None

        # Gameplay state
        self.score         = 0
        self.level         = 1
        self.food_eaten    = 0
        self.personal_best = 0
        self.speed         = C.INITIAL_SPEED
        self._move_accum   = 0.0   # accumulated time for movement (s)
        self._last_ticks   = 0

        # Leaderboard cache
        self._leaderboard: list[dict] = []

        # Settings screen state
        self._color_options = [C.GREEN, C.CYAN, C.YELLOW, C.ORANGE, C.PURPLE, C.WHITE]
        self._color_idx     = 0
        self._find_color_idx()

        # Menu buttons
        self._menu_buttons = [
            Button(" PLAY",         C.WINDOW_WIDTH // 2, 340),
            Button("  LEADERBOARD", C.WINDOW_WIDTH // 2, 395),
            Button("  SETTINGS",     C.WINDOW_WIDTH // 2, 450),
            Button("  QUIT",         C.WINDOW_WIDTH // 2, 505),
        ]
        # Game-over buttons
        self._go_buttons = [
            Button("  RETRY",        C.WINDOW_WIDTH // 2, 430),
            Button("  MAIN MENU",    C.WINDOW_WIDTH // 2, 485),
        ]
        # Leaderboard / settings back button
        self._back_btn = Button("← BACK", C.WINDOW_WIDTH // 2, 600)
        # Settings buttons
        self._sett_grid_btn  = Button("Toggle Grid",  C.WINDOW_WIDTH // 2, 300)
        self._sett_sound_btn = Button("Toggle Sound", C.WINDOW_WIDTH // 2, 360)
        self._sett_color_btn = Button("Next Color",   C.WINDOW_WIDTH // 2, 420)
        self._sett_save_btn  = Button("Save & Back",  C.WINDOW_WIDTH // 2, 500)

    # ── Color helper ───────────────────────────────────────────────────────────

    def _find_color_idx(self):
        sc = self.settings.snake_color
        for i, c in enumerate(self._color_options):
            if list(c) == list(sc):
                self._color_idx = i
                return
        self._color_idx = 0

    # ══════════════════════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════════════════════

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(C.FPS) / 1000.0   # seconds since last frame
            mouse_pos = pygame.mouse.get_pos()
            events    = pygame.event.get()

            for ev in events:
                if ev.type == pygame.QUIT:
                    running = False

            # Dispatch to current state
            if self.state == "menu":
                self._update_menu(events, mouse_pos)
                self._draw_menu(mouse_pos)
            elif self.state == "playing":
                self._update_game(events, dt)
                self._draw_game()
            elif self.state == "gameover":
                self._update_gameover(events, mouse_pos)
                self._draw_gameover(mouse_pos)
            elif self.state == "leaderboard":
                self._update_leaderboard(events, mouse_pos)
                self._draw_leaderboard(mouse_pos)
            elif self.state == "settings":
                self._update_settings(events, mouse_pos)
                self._draw_settings(mouse_pos)

            pygame.display.flip()

        pygame.quit()

    # ══════════════════════════════════════════════════════════════════════════
    # MENU state
    # ══════════════════════════════════════════════════════════════════════════

    def _update_menu(self, events, mouse_pos):
        for ev in events:
            # Username text input
            if ev.type == pygame.KEYDOWN:
                if self.username_active:
                    if ev.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif ev.key == pygame.K_RETURN:
                        self.username_active = False
                    elif len(self.username) < 20 and ev.unicode.isprintable():
                        self.username += ev.unicode
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Toggle username box focus
                box = pygame.Rect(C.WINDOW_WIDTH//2 - 120, 268, 240, 36)
                self.username_active = box.collidepoint(mouse_pos)

            # Buttons
            labels = ["play", "leaderboard", "settings", "quit"]
            for btn, action in zip(self._menu_buttons, labels):
                if btn.is_clicked(mouse_pos, ev):
                    if action == "play":
                        if self.username.strip():
                            self._start_game()
                        else:
                            self.username_active = True
                    elif action == "leaderboard":
                        self._leaderboard = self.db.get_top10()
                        self.state = "leaderboard"
                    elif action == "settings":
                        self.state = "settings"
                    elif action == "quit":
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _draw_menu(self, mouse_pos):
        s = self.screen
        s.fill(C.ARENA_BG_COLOR)

        # Title
        _draw_text(s, "🐍 SNAKE", self.font_big, C.GREEN,
                   C.WINDOW_WIDTH // 2, 120)
        _draw_text(s, "TSIS 4  — Database Edition", self.font_small, C.LIGHT_GRAY,
                   C.WINDOW_WIDTH // 2, 175)

        # Username input
        _draw_text(s, "Enter username:", self.font_small, C.LIGHT_GRAY,
                   C.WINDOW_WIDTH // 2, 248)
        box = pygame.Rect(C.WINDOW_WIDTH//2 - 120, 268, 240, 36)
        border_c = C.CYAN if self.username_active else C.GRAY
        pygame.draw.rect(s, C.DARK_GRAY, box, border_radius=6)
        pygame.draw.rect(s, border_c, box, 2, border_radius=6)
        disp = self.username + ("|" if self.username_active and
                                 pygame.time.get_ticks() // 500 % 2 else "")
        _draw_text(s, disp, self.font_small, C.WHITE,
                   box.centerx, box.centery)

        # Menu buttons
        for btn in self._menu_buttons:
            btn.draw(s, btn.is_hovered(mouse_pos))

        # DB status
        db_txt = "DB: connected" if self.db.available else "DB: offline (scores not saved)"
        db_c   = C.GREEN if self.db.available else C.ORANGE
        _draw_text(s, db_txt, self.font_tiny, db_c,
                   C.WINDOW_WIDTH // 2, C.WINDOW_HEIGHT - 16)

    # ══════════════════════════════════════════════════════════════════════════
    # Start game
    # ══════════════════════════════════════════════════════════════════════════

    def _start_game(self):
        self.score      = 0
        self.level      = 1
        self.food_eaten = 0
        self.speed      = C.INITIAL_SPEED
        self._move_accum = 0.0
        self._last_ticks = pygame.time.get_ticks()

        self.snake    = Snake()
        self.food_mgr = FoodManager()
        self.pu_mgr   = PowerupManager()
        self.obs_mgr  = ObstacleManager()

        self.personal_best = self.db.get_personal_best(self.username)

        # Spawn initial food
        excl = self.snake.occupied()
        self.food_mgr.spawn_normal(excl)
        self.food_mgr.spawn_bonus(excl | self.food_mgr.occupied())
        self.food_mgr.spawn_poison(excl | self.food_mgr.occupied())

        self.state = "playing"

    # ══════════════════════════════════════════════════════════════════════════
    # PLAYING state
    # ══════════════════════════════════════════════════════════════════════════

    def _update_game(self, events, dt: float):
        now = pygame.time.get_ticks()

        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.state = "menu"
                    return
                self.snake.handle_key(ev.key)

        # Tick managers
        self.food_mgr.tick(now)
        self.pu_mgr.tick(now)

        # Effective speed (cells/s) modified by power-up
        eff_speed = self.speed * self.pu_mgr.speed_multiplier()

        # Accumulate time; move when enough time has passed
        self._move_accum += dt
        step = 1.0 / eff_speed
        if self._move_accum < step:
            return
        self._move_accum -= step

        # Move snake
        head = self.snake.move()

        # ── Collision checks ───────────────────────────────────────────────────
        wall_hit     = self.snake.hits_wall()
        self_hit     = self.snake.hits_self()
        obstacle_hit = self.snake.hits_obstacle(self.obs_mgr.blocks)

        if wall_hit or self_hit or obstacle_hit:
            if self.pu_mgr.shield_up():
                self.pu_mgr.consume_shield()
                # Teleport head back to previous safe position (just undo)
                self.snake.body[0] = self.snake.body[1]
            else:
                self._game_over()
                return

        # ── Food check ────────────────────────────────────────────────────────
        eaten = self.food_mgr.check_eat(head)
        if eaten:
            if eaten.kind == "poison":
                self.snake.shorten(2)
                if len(self.snake.body) <= 1:
                    self._game_over()
                    return
            else:
                self.score      += eaten.points
                self.food_eaten += 1
                self.snake.grow()

            # Respawn food
            excl = (self.snake.occupied() | self.obs_mgr.blocks |
                    self.food_mgr.occupied() | self.pu_mgr.occupied())
            if eaten.kind == "normal":
                self.food_mgr.spawn_normal(excl)
                # Occasionally spawn bonus/poison
                if random.random() < 0.3:
                    self.food_mgr.spawn_bonus(excl | self.food_mgr.occupied())
                if random.random() < 0.2:
                    self.food_mgr.spawn_poison(excl | self.food_mgr.occupied())
            elif eaten.kind == "bonus":
                self.food_mgr.spawn_bonus(excl)
            elif eaten.kind == "poison":
                self.food_mgr.spawn_poison(excl)

            # Level-up
            if self.food_eaten >= self.level * C.FOOD_PER_LEVEL:
                self.level += 1
                self.speed  = C.INITIAL_SPEED + (self.level - 1) * C.SPEED_INCREMENT
                self.obs_mgr.place_for_level(self.level, self.snake.occupied())

            # Try spawning power-up
            excl2 = (self.snake.occupied() | self.obs_mgr.blocks |
                     self.food_mgr.occupied())
            self.pu_mgr.try_spawn(excl2)

        # ── Power-up pickup ───────────────────────────────────────────────────
        collected = self.pu_mgr.check_collect(head)
        # (effect applied automatically in PowerupManager)

    def _game_over(self):
        self.db.save_session(self.username, self.score, self.level)
        self.personal_best = max(self.personal_best, self.score)
        self.state = "gameover"

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _draw_game(self):
        s = self.screen
        s.fill(C.HUD_BG_COLOR)

        # ── HUD bar ───────────────────────────────────────────────────────────
        pygame.draw.rect(s, C.DARK_GRAY,
                         (0, 0, C.WINDOW_WIDTH, C.BORDER + C.HUD_HEIGHT))
        _draw_text(s, f"Score: {self.score}", self.font_small, C.WHITE, 10, 18, "topleft")
        _draw_text(s, f"Level: {self.level}", self.font_small, C.CYAN,
                   C.WINDOW_WIDTH // 2, 18)
        _draw_text(s, f"Best: {self.personal_best}", self.font_small, C.GOLD,
                   C.WINDOW_WIDTH - 10, 18, anchor="midleft")

        # Active power-up indicator
        if self.pu_mgr.active_kind:
            remaining = max(0, self.pu_mgr.active_until - pygame.time.get_ticks())
            secs = remaining / 1000
            pu_color = C.POWERUP_COLORS[self.pu_mgr.active_kind]
            _draw_text(s, f"[{self.pu_mgr.active_kind.upper()} {secs:.1f}s]",
                       self.font_small, pu_color, C.WINDOW_WIDTH // 2, 42)

        # ── Arena border ──────────────────────────────────────────────────────
        arena_rect = pygame.Rect(C.ARENA_X - 2, C.ARENA_Y - 2,
                                 C.ARENA_W + 4, C.ARENA_H + 4)
        pygame.draw.rect(s, C.BORDER_COLOR, arena_rect, 2, border_radius=4)
        pygame.draw.rect(s, C.ARENA_BG_COLOR,
                         pygame.Rect(C.ARENA_X, C.ARENA_Y, C.ARENA_W, C.ARENA_H))

        # Optional grid overlay
        if self.settings.grid_overlay:
            for col in range(C.GRID_COLS + 1):
                x = C.ARENA_X + col * C.CELL_SIZE
                pygame.draw.line(s, C.GRID_LINE_COLOR,
                                 (x, C.ARENA_Y), (x, C.ARENA_Y + C.ARENA_H))
            for row in range(C.GRID_ROWS + 1):
                y = C.ARENA_Y + row * C.CELL_SIZE
                pygame.draw.line(s, C.GRID_LINE_COLOR,
                                 (C.ARENA_X, y), (C.ARENA_X + C.ARENA_W, y))

        # ── Game objects ──────────────────────────────────────────────────────
        self.obs_mgr.draw(s)
        self.food_mgr.draw(s)
        self.pu_mgr.draw(s)
        self.snake.draw(s, self.settings.snake_color, self.pu_mgr.shield_up())

    # ══════════════════════════════════════════════════════════════════════════
    # GAME OVER state
    # ══════════════════════════════════════════════════════════════════════════

    def _update_gameover(self, events, mouse_pos):
        for ev in events:
            if self._go_buttons[0].is_clicked(mouse_pos, ev):   # Retry
                self._start_game()
            elif self._go_buttons[1].is_clicked(mouse_pos, ev): # Menu
                self.state = "menu"

    def _draw_gameover(self, mouse_pos):
        s = self.screen
        s.fill(C.ARENA_BG_COLOR)

        _draw_text(s, "GAME OVER", self.font_big, C.RED,
                   C.WINDOW_WIDTH // 2, 180)
        _draw_text(s, f"Player: {self.username}", self.font_med, C.WHITE,
                   C.WINDOW_WIDTH // 2, 255)
        _draw_text(s, f"Score:  {self.score}", self.font_med, C.YELLOW,
                   C.WINDOW_WIDTH // 2, 295)
        _draw_text(s, f"Level:  {self.level}", self.font_med, C.CYAN,
                   C.WINDOW_WIDTH // 2, 330)
        _draw_text(s, f"Personal Best: {self.personal_best}", self.font_med, C.GOLD,
                   C.WINDOW_WIDTH // 2, 370)

        saved_msg = "Result saved to database." if self.db.available else "DB offline — not saved."
        _draw_text(s, saved_msg, self.font_tiny, C.LIGHT_GRAY,
                   C.WINDOW_WIDTH // 2, 405)

        for btn in self._go_buttons:
            btn.draw(s, btn.is_hovered(mouse_pos))

    # ══════════════════════════════════════════════════════════════════════════
    # LEADERBOARD state
    # ══════════════════════════════════════════════════════════════════════════

    def _update_leaderboard(self, events, mouse_pos):
        for ev in events:
            if self._back_btn.is_clicked(mouse_pos, ev):
                self.state = "menu"

    def _draw_leaderboard(self, mouse_pos):
        s = self.screen
        s.fill(C.ARENA_BG_COLOR)

        _draw_text(s, " LEADERBOARD", self.font_big, C.GOLD,
                   C.WINDOW_WIDTH // 2, 50)

        if not self.db.available:
            _draw_text(s, "Database offline — no data available.",
                       self.font_med, C.ORANGE, C.WINDOW_WIDTH // 2, 200)
        elif not self._leaderboard:
            _draw_text(s, "No scores yet. Be the first!",
                       self.font_med, C.LIGHT_GRAY, C.WINDOW_WIDTH // 2, 200)
        else:
            headers = ("Rank", "Username", "Score", "Level", "Date")
            col_x   = (60, 170, 380, 500, 620)
            y = 110
            for i, hdr in enumerate(headers):
                _draw_text(s, hdr, self.font_small, C.CYAN, col_x[i], y, "topleft")
            pygame.draw.line(s, C.GRAY, (40, y + 22), (C.WINDOW_WIDTH - 40, y + 22), 1)

            for rank, row in enumerate(self._leaderboard, 1):
                y += 38
                rank_c  = C.GOLD if rank == 1 else C.LIGHT_GRAY
                date_str= str(row["played_at"])[:10] if row["played_at"] else "—"
                cells = (str(rank), row["username"], str(row["score"]),
                         str(row["level_reached"]), date_str)
                for i, cell in enumerate(cells):
                    _draw_text(s, cell, self.font_small, rank_c, col_x[i], y, "topleft")

        self._back_btn.draw(s, self._back_btn.is_hovered(mouse_pos))

    # ══════════════════════════════════════════════════════════════════════════
    # SETTINGS state
    # ══════════════════════════════════════════════════════════════════════════

    def _update_settings(self, events, mouse_pos):
        for ev in events:
            if self._sett_grid_btn.is_clicked(mouse_pos, ev):
                self.settings.grid_overlay = not self.settings.grid_overlay
            elif self._sett_sound_btn.is_clicked(mouse_pos, ev):
                self.settings.sound = not self.settings.sound
            elif self._sett_color_btn.is_clicked(mouse_pos, ev):
                self._color_idx = (self._color_idx + 1) % len(self._color_options)
                self.settings.snake_color = self._color_options[self._color_idx]
            elif self._sett_save_btn.is_clicked(mouse_pos, ev):
                self.settings.save()
                self.state = "menu"

    def _draw_settings(self, mouse_pos):
        s = self.screen
        s.fill(C.ARENA_BG_COLOR)

        _draw_text(s, "⚙  SETTINGS", self.font_big, C.CYAN,
                   C.WINDOW_WIDTH // 2, 80)

        # Grid toggle
        g_val = "ON" if self.settings.grid_overlay else "OFF"
        g_c   = C.GREEN if self.settings.grid_overlay else C.RED
        _draw_text(s, f"Grid overlay: {g_val}", self.font_med, g_c,
                   C.WINDOW_WIDTH // 2, 250)
        self._sett_grid_btn.draw(s, self._sett_grid_btn.is_hovered(mouse_pos))

        # Sound toggle
        snd_val = "ON" if self.settings.sound else "OFF"
        snd_c   = C.GREEN if self.settings.sound else C.RED
        _draw_text(s, f"Sound: {snd_val}", self.font_med, snd_c,
                   C.WINDOW_WIDTH // 2, 310)
        self._sett_sound_btn.draw(s, self._sett_sound_btn.is_hovered(mouse_pos))

        # Color preview
        preview_color = self._color_options[self._color_idx]
        preview_rect  = pygame.Rect(C.WINDOW_WIDTH // 2 - 30, 380, 60, 24)
        pygame.draw.rect(s, preview_color, preview_rect, border_radius=4)
        pygame.draw.rect(s, C.WHITE, preview_rect, 1, border_radius=4)
        _draw_text(s, "Snake color:", self.font_med, C.WHITE,
                   C.WINDOW_WIDTH // 2, 370)
        self._sett_color_btn.draw(s, self._sett_color_btn.is_hovered(mouse_pos))

        self._sett_save_btn.draw(s, self._sett_save_btn.is_hovered(mouse_pos))