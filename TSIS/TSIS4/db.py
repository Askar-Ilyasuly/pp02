# db.py — Database layer using psycopg2
#
# Handles all PostgreSQL interactions:
#   • Schema creation
#   • Saving game sessions
#   • Fetching leaderboard / personal best

import psycopg2
import psycopg2.extras
from datetime import datetime
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


# ─── SQL ──────────────────────────────────────────────────────────────────────
_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id) ON DELETE CASCADE,
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""

_TOP10_SQL = """
SELECT p.username, gs.score, gs.level_reached, gs.played_at
FROM   game_sessions gs
JOIN   players p ON p.id = gs.player_id
ORDER  BY gs.score DESC
LIMIT  10;
"""

_PERSONAL_BEST_SQL = """
SELECT MAX(score)
FROM   game_sessions gs
JOIN   players p ON p.id = gs.player_id
WHERE  p.username = %s;
"""

_INSERT_PLAYER_SQL = """
INSERT INTO players (username)
VALUES (%s)
ON CONFLICT (username) DO NOTHING;
"""

_GET_PLAYER_ID_SQL = "SELECT id FROM players WHERE username = %s;"

_INSERT_SESSION_SQL = """
INSERT INTO game_sessions (player_id, score, level_reached, played_at)
VALUES (%s, %s, %s, %s);
"""


class Database:
    """Thin wrapper around a psycopg2 connection for the Snake game."""

    def __init__(self):
        self.conn = None
        self._available = False

    # ── Connection ─────────────────────────────────────────────────────────────

    def connect(self):
        """Open the connection and ensure the schema exists.
        Returns True on success, False if the DB is unreachable."""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=3,
            )
            self.conn.autocommit = False
            self._create_schema()
            self._available = True
            print("[DB] Connected successfully.")
        except Exception as exc:
            print(f"[DB] Could not connect: {exc}")
            self.conn = None
            self._available = False
        return self._available

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    @property
    def available(self):
        return self._available

    # ── Schema ─────────────────────────────────────────────────────────────────

    def _create_schema(self):
        with self.conn.cursor() as cur:
            cur.execute(_SCHEMA_SQL)
        self.conn.commit()

    # ── Public API ─────────────────────────────────────────────────────────────

    def save_session(self, username: str, score: int, level_reached: int) -> bool:
        """Upsert player, then insert a game session row.  Returns True on success."""
        if not self._available:
            return False
        try:
            with self.conn.cursor() as cur:
                # Ensure the player exists
                cur.execute(_INSERT_PLAYER_SQL, (username,))
                cur.execute(_GET_PLAYER_ID_SQL, (username,))
                row = cur.fetchone()
                if row is None:
                    return False
                player_id = row[0]
                cur.execute(_INSERT_SESSION_SQL, (player_id, score, level_reached, datetime.now()))
            self.conn.commit()
            return True
        except Exception as exc:
            print(f"[DB] save_session error: {exc}")
            self.conn.rollback()
            return False

    def get_top10(self) -> list[dict]:
        """Return the top-10 all-time scores as a list of dicts."""
        if not self._available:
            return []
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(_TOP10_SQL)
                rows = cur.fetchall()
            return [dict(r) for r in rows]
        except Exception as exc:
            print(f"[DB] get_top10 error: {exc}")
            return []

    def get_personal_best(self, username: str) -> int:
        """Return the player's all-time best score (0 if none)."""
        if not self._available:
            return 0
        try:
            with self.conn.cursor() as cur:
                cur.execute(_PERSONAL_BEST_SQL, (username,))
                row = cur.fetchone()
            return row[0] if row and row[0] is not None else 0
        except Exception as exc:
            print(f"[DB] get_personal_best error: {exc}")
            return 0