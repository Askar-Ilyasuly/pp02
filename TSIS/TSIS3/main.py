"""
main.py  –  Entry point for TSIS 3 Racer.
Manages the screen-flow: Menu → Username → Game → GameOver → loop.
"""

import pygame
import sys

from persistence import load_settings, save_settings, save_score
from ui import (
    run_main_menu,
    run_username_entry,
    run_settings,
    run_leaderboard,
    run_game_over,
)
from racer import GameSession, SCREEN_W, SCREEN_H


def main():
    pygame.init()
    pygame.display.set_caption("Racer – TSIS 3")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    settings = load_settings()

    while True:
        # ── Main menu ─────────────────────────────────────────────────────
        action = run_main_menu(screen)

        if action == "quit":
            break

        elif action == "leaderboard":
            run_leaderboard(screen)
            continue

        elif action == "settings":
            settings = run_settings(screen, settings)
            continue

        elif action == "play":
            # ── Username entry ─────────────────────────────────────────────
            username = run_username_entry(screen, settings)
            settings["username"] = username
            save_settings(settings)

            # ── Game loop ──────────────────────────────────────────────────
            while True:
                session = GameSession(settings)
                result  = "playing"

                while result == "playing":
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save_settings(settings)
                            pygame.quit()
                            sys.exit()
                        session.handle_event(event)

                    result = session.update()
                    session.draw(screen)
                    pygame.display.flip()
                    clock.tick(60)

                # ── Game over ──────────────────────────────────────────────
                save_score(
                    username,
                    session.score,
                    session.distance,
                    session.coins_cnt,
                )

                go_action = run_game_over(
                    screen,
                    session.score,
                    session.distance,
                    session.coins_cnt,
                )

                if go_action == "retry":
                    continue   # inner while: new session, same username
                else:
                    break      # go back to main menu

    save_settings(settings)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()