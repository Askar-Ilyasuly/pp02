"""
racer.py  –  Core gameplay for TSIS 3 Racer.
Handles: road scrolling, player car, traffic, obstacles,
power-ups, coins, scoring, HUD rendering.
"""

import pygame
import random
import math

# ─────────────────────────────────────────────────────────────────────────────
# Colours
# ─────────────────────────────────────────────────────────────────────────────
BG_SKY    = (30,  30,  50)
ROAD_COL  = (50,  50,  50)
LANE_COL  = (200, 200, 0)
GRASS_L   = (30,  90,  30)
GRASS_R   = (30,  90,  30)
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0)
YELLOW    = (255, 215,  0)
ORANGE    = (255, 140,  0)
RED       = (220,  40,  40)
GREEN     = (50,  200,  80)
CYAN      = (0,   200, 255)
PURPLE    = (160,  40, 200)
GRAY      = (120, 120, 120)
DARK_GRAY = (70,   70,  70)
OIL_COL   = (20,   10,  40)
NITRO_COL = (0,   240, 255)
SHIELD_C  = (100, 160, 255)
REPAIR_C  = (100, 230, 100)
BARRIER_C = (255,  80,  30)

CAR_COLORS = {
    "red":    (220,  50,  50),
    "blue":   (50,  100, 220),
    "green":  (50,  200, 100),
    "yellow": (240, 200,  30),
}

# ─────────────────────────────────────────────────────────────────────────────
# Layout
# ─────────────────────────────────────────────────────────────────────────────
SCREEN_W  = 700
SCREEN_H  = 660
NUM_LANES = 5
ROAD_L    = 100
ROAD_R    = 600
ROAD_W    = ROAD_R - ROAD_L
LANE_W    = ROAD_W // NUM_LANES

LANE_CENTERS = [ROAD_L + LANE_W * i + LANE_W // 2 for i in range(NUM_LANES)]

CAR_W, CAR_H   = 36, 60
ENEMY_W, ENEMY_H = 36, 58

COIN_R   = 10
STRIPE_H = 40

DIFF_PARAMS = {
    "easy":   {"base_speed": 4,  "max_speed": 10, "spawn_rate": 0.012},
    "normal": {"base_speed": 6,  "max_speed": 16, "spawn_rate": 0.022},
    "hard":   {"base_speed": 9,  "max_speed": 24, "spawn_rate": 0.035},
}

POWERUP_TIMEOUT = 300   # frames before uncollected power-up vanishes
NITRO_DURATION  = 180   # 3 s at 60 fps
SHIELD_DURATION = -1    # until hit
REPAIR_DURATION = -1    # instant


# ─────────────────────────────────────────────────────────────────────────────
# Drawing helpers
# ─────────────────────────────────────────────────────────────────────────────

def _font(size, bold=False):
    try:
        return pygame.font.SysFont("segoeui", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def draw_car(surface, x, y, color, shadow=False):
    if shadow:
        pygame.draw.ellipse(surface, (20, 20, 20, 80),
                            (x - CAR_W // 2 + 4, y + CAR_H - 8, CAR_W - 8, 12))
    # body
    pygame.draw.rect(surface, color,
                     (x - CAR_W // 2, y, CAR_W, CAR_H), border_radius=8)
    # windshield
    pygame.draw.rect(surface, (180, 220, 255),
                     (x - CAR_W // 2 + 5, y + 8, CAR_W - 10, 14), border_radius=4)
    # wheels
    wc = (30, 30, 30)
    for wx, wy in [(x - CAR_W // 2 - 3, y + 6),
                   (x + CAR_W // 2 - 7, y + 6),
                   (x - CAR_W // 2 - 3, y + CAR_H - 18),
                   (x + CAR_W // 2 - 7, y + CAR_H - 18)]:
        pygame.draw.rect(surface, wc, (wx, wy, 10, 14), border_radius=3)


def draw_enemy_car(surface, x, y, color):
    pygame.draw.rect(surface, color,
                     (x - ENEMY_W // 2, y, ENEMY_W, ENEMY_H), border_radius=7)
    pygame.draw.rect(surface, (200, 230, 255),
                     (x - ENEMY_W // 2 + 5, y + ENEMY_H - 22, ENEMY_W - 10, 14),
                     border_radius=4)
    wc = (30, 30, 30)
    for wx, wy in [(x - ENEMY_W // 2 - 3, y + 6),
                   (x + ENEMY_W // 2 - 7, y + 6),
                   (x - ENEMY_W // 2 - 3, y + ENEMY_H - 18),
                   (x + ENEMY_W // 2 - 7, y + ENEMY_H - 18)]:
        pygame.draw.rect(surface, wc, (wx, wy, 10, 13), border_radius=3)


# ─────────────────────────────────────────────────────────────────────────────
# Game objects
# ─────────────────────────────────────────────────────────────────────────────

class RoadStripe:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def update(self, speed):
        self.y += speed

    def draw(self, surface):
        pygame.draw.rect(surface, LANE_COL, (self.x - 2, self.y, 4, STRIPE_H // 2))


class Coin:
    WEIGHTS = {1: (YELLOW, 0.6), 3: (ORANGE, 0.3), 5: (CYAN, 0.1)}

    def __init__(self, lane, y):
        self.lane  = lane
        self.x     = LANE_CENTERS[lane]
        self.y     = y
        val_list   = list(self.WEIGHTS.keys())
        weights    = [self.WEIGHTS[v][1] for v in val_list]
        self.value = random.choices(val_list, weights=weights)[0]
        self.color = self.WEIGHTS[self.value][0]
        self.alive = True

    def update(self, speed):
        self.y += speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, int(self.y)), COIN_R)
        f = _font(12, bold=True)
        t = f.render(str(self.value), True, BLACK)
        surface.blit(t, t.get_rect(center=(self.x, int(self.y))))


class Obstacle:
    """Oil spill, pothole, or barrier."""
    TYPES = ["oil", "pothole", "barrier"]

    def __init__(self, lane, y, kind=None):
        self.lane  = lane
        self.x     = LANE_CENTERS[lane]
        self.y     = float(y)
        self.kind  = kind or random.choice(self.TYPES)
        self.alive = True
        self.w     = LANE_W - 6
        self.h     = 20 if self.kind != "oil" else 28

    def update(self, speed):
        self.y += speed

    def draw(self, surface):
        if self.kind == "oil":
            r = pygame.Rect(self.x - self.w // 2, int(self.y) - self.h // 2,
                            self.w, self.h)
            pygame.draw.ellipse(surface, OIL_COL, r)
            pygame.draw.ellipse(surface, PURPLE, r, 2)
        elif self.kind == "pothole":
            r = pygame.Rect(self.x - self.w // 2, int(self.y) - self.h // 2,
                            self.w, self.h)
            pygame.draw.ellipse(surface, DARK_GRAY, r)
            pygame.draw.ellipse(surface, GRAY, r, 2)
        else:  # barrier
            r = pygame.Rect(self.x - self.w // 2, int(self.y) - self.h // 2,
                            self.w, self.h)
            pygame.draw.rect(surface, BARRIER_C, r, border_radius=4)
            pygame.draw.rect(surface, WHITE, r, 2, border_radius=4)

    def rect(self):
        return pygame.Rect(self.x - self.w // 2, int(self.y) - self.h // 2,
                           self.w, self.h)


class NitroStrip:
    """Speed boost strip spanning a lane."""
    def __init__(self, lane, y):
        self.lane  = lane
        self.x     = LANE_CENTERS[lane]
        self.y     = float(y)
        self.w     = LANE_W - 4
        self.h     = 16
        self.alive = True

    def update(self, speed):
        self.y += speed

    def draw(self, surface):
        r = pygame.Rect(self.x - self.w // 2, int(self.y) - self.h // 2,
                        self.w, self.h)
        pygame.draw.rect(surface, NITRO_COL, r, border_radius=3)
        f = _font(11)
        t = f.render("NITRO", True, BLACK)
        surface.blit(t, t.get_rect(center=r.center))

    def rect(self):
        return pygame.Rect(self.x - self.w // 2, int(self.y) - self.h // 2,
                           self.w, self.h)


class EnemyCar:
    COLORS = [(180, 40, 40), (40, 40, 180), (40, 160, 40),
              (160, 100, 40), (160, 40, 160)]

    def __init__(self, lane, y, speed):
        self.lane  = lane
        self.x     = LANE_CENTERS[lane]
        self.y     = float(y)
        self.speed = speed
        self.color = random.choice(self.COLORS)
        self.alive = True

    def update(self, road_speed):
        self.y += road_speed * 0.6   # enemy moves slower than road

    def draw(self, surface):
        draw_enemy_car(surface, self.x, int(self.y), self.color)

    def rect(self):
        return pygame.Rect(self.x - ENEMY_W // 2, int(self.y), ENEMY_W, ENEMY_H)


class PowerUp:
    KINDS = {
        "nitro":  (NITRO_COL,  "N"),
        "shield": (SHIELD_C,   "S"),
        "repair": (REPAIR_C,   "R"),
    }

    def __init__(self, lane, y):
        self.lane  = lane
        self.x     = LANE_CENTERS[lane]
        self.y     = float(y)
        self.kind  = random.choice(list(self.KINDS.keys()))
        self.alive = True
        self.timer = POWERUP_TIMEOUT
        self.r     = 14

    def update(self, speed):
        self.y     += speed
        self.timer -= 1
        if self.timer <= 0:
            self.alive = False

    def draw(self, surface):
        col, letter = self.KINDS[self.kind]
        # pulsing ring
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 4
        pygame.draw.circle(surface, col, (self.x, int(self.y)),
                           int(self.r + pulse), 2)
        pygame.draw.circle(surface, col, (self.x, int(self.y)), self.r)
        f = _font(14, bold=True)
        t = f.render(letter, True, BLACK)
        surface.blit(t, t.get_rect(center=(self.x, int(self.y))))

    def rect(self):
        return pygame.Rect(self.x - self.r, int(self.y) - self.r,
                           self.r * 2, self.r * 2)


# ─────────────────────────────────────────────────────────────────────────────
# Main game session
# ─────────────────────────────────────────────────────────────────────────────

class GameSession:
    """
    Call update() and draw() each frame.
    Returns 'playing', 'dead' from update().
    """

    def __init__(self, settings: dict):
        self.settings  = settings
        diff           = settings.get("difficulty", "normal")
        p              = DIFF_PARAMS[diff]
        self.base_spd  = p["base_speed"]
        self.max_spd   = p["max_speed"]
        self.spawn_r   = p["spawn_rate"]
        self.road_spd  = float(self.base_spd)

        car_col_name   = settings.get("car_color", "red")
        self.car_color = CAR_COLORS.get(car_col_name, CAR_COLORS["red"])

        self.player_lane = NUM_LANES // 2
        self.player_x    = float(LANE_CENTERS[self.player_lane])
        self.player_y    = SCREEN_H - 120
        self.target_x    = self.player_x

        # Road stripes
        self.stripes = []
        for lane in range(1, NUM_LANES):
            lx = ROAD_L + LANE_W * lane
            for yy in range(-STRIPE_H, SCREEN_H, STRIPE_H * 2):
                self.stripes.append(RoadStripe(lx, yy))

        # Game objects
        self.coins     = []
        self.obstacles = []
        self.enemies   = []
        self.powerups  = []
        self.nitro_strips = []

        # State
        self.score     = 0
        self.coins_cnt = 0
        self.distance  = 0       # in "meters"
        self.frame     = 0

        # Power-up state
        self.active_pu      = None   # "nitro" | "shield" | None
        self.pu_timer       = 0
        self.shield_active  = False
        self.nitro_active   = False

        # Crash flash
        self.crash_flash = 0

        # Fonts
        self.hud_f  = _font(20, bold=True)
        self.pu_f   = _font(18)
        self.big_f  = _font(28, bold=True)

    # ── Input ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.player_lane = max(0, self.player_lane - 1)
                self.target_x    = LANE_CENTERS[self.player_lane]
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.player_lane = min(NUM_LANES - 1, self.player_lane + 1)
                self.target_x    = LANE_CENTERS[self.player_lane]

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self) -> str:
        self.frame += 1

        # Speed scaling with distance
        progress      = min(self.distance / 5000, 1.0)
        self.road_spd = self.base_spd + (self.max_spd - self.base_spd) * progress
        if self.nitro_active:
            self.road_spd = min(self.road_spd * 1.6, self.max_spd * 1.5)

        self.distance += int(self.road_spd * 0.4)

        # Smooth player horizontal movement
        dx = self.target_x - self.player_x
        self.player_x += dx * 0.18

        # Power-up timer
        if self.nitro_active:
            self.pu_timer -= 1
            if self.pu_timer <= 0:
                self.nitro_active = False
                self.active_pu    = None

        # Road stripes
        for s in self.stripes:
            s.update(self.road_spd)
            if s.y > SCREEN_H:
                s.y -= STRIPE_H * 2 * NUM_LANES  # recycle

        # ── Spawning ─────────────────────────────────────────────────────────
        spawn_scale = 1 + progress * 2   # more spawns as difficulty increases

        # Coins
        if random.random() < 0.04 * spawn_scale:
            lane = random.randint(0, NUM_LANES - 1)
            self.coins.append(Coin(lane, -20))

        # Obstacles
        if random.random() < self.spawn_r * spawn_scale:
            lane = random.randint(0, NUM_LANES - 1)
            # Don't spawn on player lane if very close
            if lane != self.player_lane or random.random() > 0.3:
                self.obstacles.append(Obstacle(lane, -30))

        # Enemy traffic
        if random.random() < self.spawn_r * 0.7 * spawn_scale:
            lane = random.randint(0, NUM_LANES - 1)
            if lane != self.player_lane:
                self.enemies.append(EnemyCar(lane, -70, self.road_spd))

        # Power-ups (rare)
        if random.random() < 0.004 and len(self.powerups) < 2:
            lane = random.randint(0, NUM_LANES - 1)
            self.powerups.append(PowerUp(lane, -20))

        # Nitro strips (occasional road event)
        if random.random() < 0.003 and len(self.nitro_strips) < 2:
            lane = random.randint(0, NUM_LANES - 1)
            self.nitro_strips.append(NitroStrip(lane, -20))

        # ── Update objects ────────────────────────────────────────────────────
        for obj_list in [self.coins, self.obstacles, self.enemies,
                         self.powerups, self.nitro_strips]:
            for obj in obj_list:
                obj.update(self.road_spd)

        # ── Player rect ───────────────────────────────────────────────────────
        px = int(self.player_x)
        py = self.player_y
        player_rect = pygame.Rect(px - CAR_W // 2 + 4, py + 8,
                                  CAR_W - 8, CAR_H - 16)

        # ── Coin collection ───────────────────────────────────────────────────
        for c in self.coins:
            if not c.alive:
                continue
            cr = pygame.Rect(c.x - COIN_R, int(c.y) - COIN_R, COIN_R*2, COIN_R*2)
            if player_rect.colliderect(cr):
                self.score     += c.value * 10
                self.coins_cnt += c.value
                c.alive         = False

        # ── Power-up collection ───────────────────────────────────────────────
        for pu in self.powerups:
            if not pu.alive:
                continue
            if player_rect.colliderect(pu.rect()):
                self._apply_powerup(pu.kind)
                pu.alive = False

        # ── Nitro strip collection ────────────────────────────────────────────
        for ns in self.nitro_strips:
            if not ns.alive:
                continue
            if player_rect.colliderect(ns.rect()):
                self._apply_powerup("nitro")
                ns.alive = False

        # ── Obstacle collision ────────────────────────────────────────────────
        for obs in self.obstacles:
            if not obs.alive:
                continue
            if player_rect.colliderect(obs.rect()):
                if self.shield_active:
                    self.shield_active = False
                    self.active_pu     = None
                    obs.alive          = False
                elif obs.kind == "oil":
                    # Slow down instead of instant death
                    self.road_spd = max(self.base_spd, self.road_spd * 0.5)
                    obs.alive = False
                else:
                    return "dead"

        # ── Enemy collision ───────────────────────────────────────────────────
        for en in self.enemies:
            if not en.alive:
                continue
            if player_rect.colliderect(en.rect()):
                if self.shield_active:
                    self.shield_active = False
                    self.active_pu     = None
                    en.alive           = False
                else:
                    return "dead"

        # ── Cleanup off-screen ────────────────────────────────────────────────
        for lst in [self.coins, self.obstacles, self.enemies,
                    self.powerups, self.nitro_strips]:
            lst[:] = [o for o in lst if o.alive and o.y < SCREEN_H + 80]

        # Distance bonus
        if self.frame % 60 == 0:
            self.score += 5

        return "playing"

    def _apply_powerup(self, kind):
        if kind == "nitro":
            self.nitro_active = True
            self.pu_timer     = NITRO_DURATION
            self.active_pu    = "nitro"
        elif kind == "shield":
            self.shield_active = True
            self.active_pu     = "shield"
        elif kind == "repair":
            # Clear nearest obstacle ahead
            if self.obstacles:
                self.obstacles[0].alive = False
            self.active_pu = None

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface):
        # Sky / background
        surface.fill(BG_SKY)

        # Grass
        pygame.draw.rect(surface, GRASS_L, (0, 0, ROAD_L, SCREEN_H))
        pygame.draw.rect(surface, GRASS_R, (ROAD_R, 0, SCREEN_W - ROAD_R, SCREEN_H))

        # Road
        pygame.draw.rect(surface, ROAD_COL, (ROAD_L, 0, ROAD_W, SCREEN_H))

        # Road edges
        pygame.draw.rect(surface, WHITE, (ROAD_L, 0, 4, SCREEN_H))
        pygame.draw.rect(surface, WHITE, (ROAD_R - 4, 0, 4, SCREEN_H))

        # Lane stripes
        for s in self.stripes:
            s.draw(surface)

        # Road objects
        for ns in self.nitro_strips:
            ns.draw(surface)
        for obs in self.obstacles:
            obs.draw(surface)
        for c in self.coins:
            c.draw(surface)
        for pu in self.powerups:
            pu.draw(surface)
        for en in self.enemies:
            en.draw(surface)

        # Shield aura
        px, py = int(self.player_x), self.player_y
        if self.shield_active:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.006)) * 6
            pygame.draw.ellipse(surface, SHIELD_C,
                                (px - CAR_W // 2 - 10 - int(pulse),
                                 py - 10 - int(pulse),
                                 CAR_W + 20 + int(pulse * 2),
                                 CAR_H + 20 + int(pulse * 2)), 3)

        # Player car
        draw_car(surface, px, py, self.car_color)

        # ── HUD ──────────────────────────────────────────────────────────────
        self._draw_hud(surface)

    def _draw_hud(self, surface):
        hf = self.hud_f
        # Score
        surface.blit(hf.render(f"Score: {self.score}", True, (255,255,255)),
                     (ROAD_R + 10, 20))
        surface.blit(hf.render(f"Coins: {self.coins_cnt}", True, YELLOW),
                     (ROAD_R + 10, 50))
        surface.blit(hf.render(f"Dist:  {self.distance}m", True, (180,255,180)),
                     (ROAD_R + 10, 80))

        spd_pct = int((self.road_spd - self.base_spd) /
                       max(1, self.max_spd - self.base_spd) * 100)
        surface.blit(hf.render(f"Speed: {spd_pct}%", True, (255,200,100)),
                     (ROAD_R + 10, 110))

        # Controls hint (first 5 s)
        if self.frame < 300:
            f = self.pu_f
            surface.blit(f.render("← → or A D", True, (180,180,200)), (10, 20))
            surface.blit(f.render("to steer",    True, (180,180,200)), (10, 42))

        # Active power-up
        if self.active_pu:
            col_map = {"nitro": NITRO_COL, "shield": SHIELD_C}
            col     = col_map.get(self.active_pu, (200, 255, 200))
            label   = self.active_pu.upper()
            if self.active_pu == "nitro":
                secs = max(0, self.pu_timer // 60)
                label += f"  {secs}s"
            t = self.big_f.render(label, True, col)
            surface.blit(t, t.get_rect(centerx=(ROAD_L + ROAD_R) // 2, top=10))

        # Difficulty badge
        diff = self.settings.get("difficulty", "normal").upper()
        d    = self.pu_f.render(diff, True, (140, 140, 160))
        surface.blit(d, (10, SCREEN_H - 30))