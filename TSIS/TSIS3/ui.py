"""
ui.py  –  All non-gameplay Pygame screens for TSIS 3 Racer.
Screens: MainMenu, Settings, Leaderboard, GameOver, UsernameEntry.
Each screen's run() method returns a string action tag.
"""

import pygame
from persistence import (
    load_leaderboard, load_settings, save_settings, DEFAULT_SETTINGS
)

# ─────────────────────────────────────────────────────────────────────────────
# Colour palette
# ─────────────────────────────────────────────────────────────────────────────

BG        = (15,  15,  25)
PANEL     = (28,  28,  45)
ACCENT    = (255, 200, 0)
TEXT      = (230, 230, 240)
SUBTEXT   = (140, 140, 160)
BTN_IDLE  = (45,  45,  70)
BTN_HOV   = (70,  70, 110)
BTN_PRESS = (255, 200,  0)
RED_CAR   = (220,  50,  50)
BLUE_CAR  = (50,  100, 220)
GREEN_CAR = (50,  200, 100)
YEL_CAR   = (240, 200,  30)
DANGER    = (220,  60,  60)
OK        = (60,  200, 100)

CAR_COLOR_MAP = {
    "red":    RED_CAR,
    "blue":   BLUE_CAR,
    "green":  GREEN_CAR,
    "yellow": YEL_CAR,
}


# ─────────────────────────────────────────────────────────────────────────────
# Shared widget helpers
# ─────────────────────────────────────────────────────────────────────────────

def _font(size, bold=False):
    try:
        return pygame.font.SysFont("segoeui", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_button(surface, rect, label, font, hovered=False, pressed=False):
    color = BTN_PRESS if pressed else (BTN_HOV if hovered else BTN_IDLE)
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, ACCENT if hovered else SUBTEXT, rect, 2, border_radius=8)
    txt_color = BG if pressed else TEXT
    t = font.render(label, True, txt_color)
    surface.blit(t, t.get_rect(center=rect.center))


def _draw_title(surface, text, y, font):
    t = font.render(text, True, ACCENT)
    surface.blit(t, t.get_rect(centerx=surface.get_width() // 2, top=y))


class SimpleButton:
    def __init__(self, rect, label):
        self.rect  = pygame.Rect(rect)
        self.label = label

    def draw(self, surface, font):
        mp = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mp)
        _draw_button(surface, self.rect, self.label, font, hovered)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ─────────────────────────────────────────────────────────────────────────────
# Username Entry
# ─────────────────────────────────────────────────────────────────────────────

def run_username_entry(screen, settings: dict) -> str:
    """Show a name-entry screen; returns the entered name."""
    W, H   = screen.get_size()
    title  = _font(52, bold=True)
    body   = _font(28)
    small  = _font(20)
    clock  = pygame.time.Clock()
    name   = settings.get("username", "")
    box    = pygame.Rect(W // 2 - 160, H // 2 - 20, 320, 44)
    ok_btn = SimpleButton((W // 2 - 80, H // 2 + 60, 160, 44), "START")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 18:
                    name += event.unicode
            if ok_btn.clicked(event) and name.strip():
                return name.strip()

        screen.fill(BG)
        _draw_title(screen, "ENTER YOUR NAME", H // 4, title)
        # input box
        pygame.draw.rect(screen, PANEL, box, border_radius=6)
        pygame.draw.rect(screen, ACCENT, box, 2, border_radius=6)
        t = body.render(name + "|", True, TEXT)
        screen.blit(t, t.get_rect(midleft=(box.left + 10, box.centery)))
        ok_btn.draw(screen, body)
        hint = small.render("Press Enter or click START", True, SUBTEXT)
        screen.blit(hint, hint.get_rect(centerx=W // 2, top=box.bottom + 12))
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────────────────────────────────────

def run_main_menu(screen) -> str:
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    W, H  = screen.get_size()
    title = _font(64, bold=True)
    btn_f = _font(26, bold=True)
    clock = pygame.time.Clock()

    buttons = [
        SimpleButton((W // 2 - 110, H // 2 - 80, 220, 50), "PLAY"),
        SimpleButton((W // 2 - 110, H // 2 -  10, 220, 50), "LEADERBOARD"),
        SimpleButton((W // 2 - 110, H // 2 +  60, 220, 50), "SETTINGS"),
        SimpleButton((W // 2 - 110, H // 2 + 130, 220, 50), "QUIT"),
    ]
    actions = ["play", "leaderboard", "settings", "quit"]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            for btn, act in zip(buttons, actions):
                if btn.clicked(event):
                    return act

        screen.fill(BG)
        # decorative road stripe
        for i in range(0, H, 40):
            pygame.draw.rect(screen, PANEL, (W // 2 - 3, i, 6, 20))

        _draw_title(screen, "RACER", H // 6, title)
        sub = _font(20).render("TSIS 3  ·  Extended Edition", True, SUBTEXT)
        screen.blit(sub, sub.get_rect(centerx=W // 2, top=H // 6 + 72))

        for btn in buttons:
            btn.draw(screen, btn_f)

        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
# Settings Screen
# ─────────────────────────────────────────────────────────────────────────────

def run_settings(screen, settings: dict) -> dict:
    """Mutates and returns settings dict; shows settings screen."""
    W, H    = screen.get_size()
    title_f = _font(48, bold=True)
    body_f  = _font(24)
    small_f = _font(20)
    clock   = pygame.time.Clock()

    back_btn = SimpleButton((W // 2 - 80, H - 80, 160, 44), "BACK")

    # Cycle helpers
    colors      = ["red", "blue", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]

    def next_val(lst, cur):
        return lst[(lst.index(cur) + 1) % len(lst)]

    color_btn = SimpleButton((W // 2 + 10, 200, 140, 36), "CHANGE")
    diff_btn  = SimpleButton((W // 2 + 10, 260, 140, 36), "CHANGE")
    sound_btn = SimpleButton((W // 2 + 10, 320, 140, 36), "TOGGLE")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if back_btn.clicked(event):
                save_settings(settings)
                return settings
            if color_btn.clicked(event):
                settings["car_color"] = next_val(colors, settings["car_color"])
            if diff_btn.clicked(event):
                settings["difficulty"] = next_val(difficulties, settings["difficulty"])
            if sound_btn.clicked(event):
                settings["sound"] = not settings["sound"]

        screen.fill(BG)
        _draw_title(screen, "SETTINGS", 60, title_f)

        rows = [
            ("Car Color",  settings["car_color"].capitalize()),
            ("Difficulty", settings["difficulty"].capitalize()),
            ("Sound",      "ON" if settings["sound"] else "OFF"),
        ]
        btns = [color_btn, diff_btn, sound_btn]

        for i, ((label, val), btn) in enumerate(zip(rows, btns)):
            y = 200 + i * 60
            lbl = body_f.render(label, True, TEXT)
            screen.blit(lbl, (W // 2 - 200, y + 6))

            # Color preview swatch
            if label == "Car Color":
                pygame.draw.rect(screen, CAR_COLOR_MAP[settings["car_color"]], (W // 2 - 10, y + 4, 18, 28), border_radius=4)
                val_surf = body_f.render(f"  {val}", True, ACCENT)
                screen.blit(val_surf, (W // 2 + 10, y + 6))
            else:
                val_surf = body_f.render(val, True, ACCENT)
                screen.blit(val_surf, (W // 2 - 10, y + 6))

            btn.draw(screen, small_f)

        back_btn.draw(screen, body_f)
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
# Leaderboard Screen
# ─────────────────────────────────────────────────────────────────────────────

def run_leaderboard(screen):
    W, H    = screen.get_size()
    title_f = _font(48, bold=True)
    row_f   = _font(22)
    hdr_f   = _font(20, bold=True)
    clock   = pygame.time.Clock()
    back    = SimpleButton((W // 2 - 70, H - 70, 140, 44), "BACK")
    entries = load_leaderboard()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if back.clicked(event):
                return

        screen.fill(BG)
        _draw_title(screen, "TOP 10", 40, title_f)

        # Header
        cols = [80, 230, 380, 510]
        hdrs = ["RANK", "NAME", "SCORE", "DISTANCE"]
        for x, h in zip(cols, hdrs):
            screen.blit(hdr_f.render(h, True, ACCENT), (x, 120))
        pygame.draw.line(screen, SUBTEXT, (70, 148), (W - 70, 148), 1)

        for i, entry in enumerate(entries[:10]):
            y = 158 + i * 36
            color = ACCENT if i == 0 else TEXT
            vals = [
                f"#{i+1}",
                entry.get("name", "?")[:14],
                str(entry.get("score", 0)),
                f"{entry.get('distance', 0)} m",
            ]
            for x, v in zip(cols, vals):
                screen.blit(row_f.render(v, True, color), (x, y))

        if not entries:
            no = row_f.render("No scores yet — play a game!", True, SUBTEXT)
            screen.blit(no, no.get_rect(centerx=W // 2, top=200))

        back.draw(screen, row_f)
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────────────────────
# Game Over Screen
# ─────────────────────────────────────────────────────────────────────────────

def run_game_over(screen, score, distance, coins) -> str:
    """Returns 'retry' or 'menu'."""
    W, H    = screen.get_size()
    title_f = _font(58, bold=True)
    stat_f  = _font(26)
    btn_f   = _font(26, bold=True)
    clock   = pygame.time.Clock()

    retry_btn = SimpleButton((W // 2 - 170, H // 2 + 80, 150, 50), "RETRY")
    menu_btn  = SimpleButton((W // 2 +  20, H // 2 + 80, 150, 50), "MENU")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if retry_btn.clicked(event):
                return "retry"
            if menu_btn.clicked(event):
                return "menu"

        screen.fill(BG)
        t = title_f.render("GAME OVER", True, DANGER)
        screen.blit(t, t.get_rect(centerx=W // 2, top=H // 5))

        stats = [
            ("Score",    str(score)),
            ("Distance", f"{distance} m"),
            ("Coins",    str(coins)),
        ]
        for i, (label, val) in enumerate(stats):
            y = H // 2 - 50 + i * 44
            lbl = stat_f.render(f"{label}:", True, SUBTEXT)
            val_s = stat_f.render(val, True, ACCENT)
            screen.blit(lbl, (W // 2 - 160, y))
            screen.blit(val_s, (W // 2 + 20, y))

        retry_btn.draw(screen, btn_f)
        menu_btn.draw(screen, btn_f)
        pygame.display.flip()
        clock.tick(60)