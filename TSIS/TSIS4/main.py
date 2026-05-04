# main.py — Entry point for the Snake Game (TSIS 4)
#
# Run:  python main.py
#
# Dependencies:  pip install pygame psycopg2-binary
# Database:      see README.md for PostgreSQL setup instructions

import sys
import pygame

from config  import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS
from db      import Database
from game    import SnakeGame, SettingsManager


def main():
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Load user settings from settings.json
    settings = SettingsManager()

    # Try to connect to PostgreSQL (game works offline too)
    db = Database()
    db.connect()

    # Create and run the game
    game = SnakeGame(db, settings)
    game.run()

    # Cleanup
    db.close()
    sys.exit(0)


if __name__ == "__main__":
    main()