# config.py — Global configuration constants for the Snake Game

# ─── Window ───────────────────────────────────────────────────────────────────
WINDOW_TITLE   = "Snake Game — TSIS4"
WINDOW_WIDTH   = 800
WINDOW_HEIGHT  = 650
FPS            = 60

# ─── Grid ─────────────────────────────────────────────────────────────────────
CELL_SIZE      = 20          # px per grid cell
GRID_COLS      = 30          # (WINDOW_WIDTH  - 2*BORDER) // CELL_SIZE
GRID_ROWS      = 25          # (WINDOW_HEIGHT - HUD_HEIGHT - 2*BORDER) // CELL_SIZE
BORDER         = 20          # px border around the arena
HUD_HEIGHT     = 50          # px reserved at the top for score / level / etc.

# Derived arena pixel bounds (top-left corner of the playfield)
ARENA_X        = BORDER
ARENA_Y        = BORDER + HUD_HEIGHT
ARENA_W        = GRID_COLS * CELL_SIZE
ARENA_H        = GRID_ROWS * CELL_SIZE

# ─── Gameplay ──────────────────────────────────────────────────────────────────
INITIAL_SPEED       = 8      # grid cells per second
SPEED_INCREMENT     = 1      # extra cells/s added each level
FOOD_PER_LEVEL      = 5      # food eaten to advance a level
INITIAL_SNAKE_LEN   = 4

# ─── Power-up timing (milliseconds) ───────────────────────────────────────────
POWERUP_DURATION_MS  = 5_000   # how long a collected power-up lasts
POWERUP_FIELD_MS     = 8_000   # how long a power-up stays on the field
POWERUP_SPAWN_CHANCE = 0.15    # probability per food-eat event

# ─── Obstacle ─────────────────────────────────────────────────────────────────
OBSTACLE_START_LEVEL    = 3
OBSTACLES_PER_LEVEL     = 5   # extra blocks added each new level ≥ 3

# ─── Colors ───────────────────────────────────────────────────────────────────
BLACK        = (0,   0,   0  )
WHITE        = (255, 255, 255)
DARK_GRAY    = (30,  30,  30 )
GRAY         = (80,  80,  80 )
LIGHT_GRAY   = (160, 160, 160)
GREEN        = (0,   200, 80 )
DARK_GREEN   = (0,   140, 50 )
RED          = (220, 50,  50 )
DARK_RED     = (140, 0,   0  )
YELLOW       = (255, 220, 0  )
ORANGE       = (255, 140, 0  )
CYAN         = (0,   220, 220)
PURPLE       = (160, 0,   220)
BLUE         = (30,  120, 255)
GOLD         = (255, 200, 50 )

# Food colors
FOOD_COLORS = {
    "normal":  (255, 80,  80 ),   # red-ish
    "bonus":   (255, 200, 0  ),   # gold (2× points)
    "poison":  (120, 0,   30 ),   # dark crimson
}

# Power-up colors
POWERUP_COLORS = {
    "speed":   (255, 140, 0  ),   # orange
    "slow":    (0,   180, 255),   # light blue
    "shield":  (180, 0,   255),   # violet
}

# Obstacle / HUD
OBSTACLE_COLOR   = (100, 100, 110)
HUD_BG_COLOR     = (15,  15,  20 )
ARENA_BG_COLOR   = (10,  10,  14 )
BORDER_COLOR     = (40,  40,  50 )
GRID_LINE_COLOR  = (20,  20,  28 )

# ─── Database ─────────────────────────────────────────────────────────────────
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "snakegame"
DB_USER     = "postgres"
DB_PASSWORD = "A_ilyas2203"          # change to your local password

# ─── Settings defaults ────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "snake_color": list(GREEN),
    "grid_overlay": False,
    "sound": False,
}
SETTINGS_FILE = "settings.json"