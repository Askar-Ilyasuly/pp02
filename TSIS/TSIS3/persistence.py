"""
persistence.py  –  Save / load leaderboard and settings.
"""

import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":       True,
    "car_color":   "red",       # red | blue | green | yellow
    "difficulty":  "normal",    # easy | normal | hard
    "username":    "",
}


# ─────────────────────────────────────────────────────────────────────────────
# Settings
# ─────────────────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Fill any missing keys with defaults
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# Leaderboard
# ─────────────────────────────────────────────────────────────────────────────

def load_leaderboard() -> list:
    """Return list of dicts sorted by score descending."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return sorted(data, key=lambda e: e.get("score", 0), reverse=True)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_score(username: str, score: int, distance: int, coins: int):
    """Append a new entry and keep only top 10."""
    entries = load_leaderboard()
    entries.append({
        "name":     username,
        "score":    score,
        "distance": distance,
        "coins":    coins,
    })
    entries = sorted(entries, key=lambda e: e["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)