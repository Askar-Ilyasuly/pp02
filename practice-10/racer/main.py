import pygame
import sys
import random
import time
from pygame.locals import *

pygame.init()
pygame.mixer.init()

FPS = 60
FramePerSec = pygame.time.Clock()

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("F1 Racer")

font_big = pygame.font.SysFont("Arial", 60)
font_small = pygame.font.SysFont("Arial", 30)
game_over_text = font_big.render("Game Over", True, BLACK)

background = pygame.image.load(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\AnimatedStreet.png")
player_img = pygame.image.load(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\Player.png")
enemy_img = pygame.image.load(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\Enemy.png")
coin_sound = pygame.mixer.Sound(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\coin.wav")
crash_sound = pygame.mixer.Sound(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\crash.wav")
coin_sound.set_volume(1.0)
crash_sound.set_volume(1.0)


class Coin(pygame.sprite.Sprite):
    RADIUS = 12
    OUTLINE = (230, 230, 0)

    def __init__(self):
        super().__init__()

        side = self.RADIUS * 2
        self.image = pygame.Surface((side, side), pygame.SRCALPHA)

        pygame.draw.circle(self.image, self.OUTLINE, (self.RADIUS, self.RADIUS), self.RADIUS)
        pygame.draw.circle(self.image, YELLOW, (self.RADIUS, self.RADIUS), self.RADIUS - 2)

        x = random.randint(40, SCREEN_WIDTH - 40)
        y = -20
        self.rect = self.image.get_rect(center=(x, y))

    def move(self):
        
        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):

        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)

        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)


P1 = Player()
E1 = Enemy()

enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

def create_coin():
    """Create and add new coin to groups."""
    new_coin = Coin()
    coins.add(new_coin)
    all_sprites.add(new_coin)


def show_score():
    """Show collected coins in top right corner."""
    score_text = font_small.render(f"Coins: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(score_text, (SCREEN_WIDTH - 120, 10))



INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

COIN_SPAWN = pygame.USEREVENT + 2
pygame.time.set_timer(COIN_SPAWN, 1500)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == INC_SPEED:
            SPEED += 0.2

        if event.type == COIN_SPAWN:
            create_coin()

    DISPLAYSURF.blit(background, (0, 0))

    show_score()

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    if pygame.sprite.spritecollideany(P1, enemies):
        crash_sound.play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (60, 220))

        final_score_text = font_small.render(f"Coins collected: {SCORE}", True, BLACK)
        DISPLAYSURF.blit(final_score_text, (90, 320))

        pygame.display.update()
        time.sleep(3)

        pygame.quit()
        sys.exit()

    collected_coins = pygame.sprite.spritecollide(P1, coins, True)
    if collected_coins:
        coin_sound.play()
        SCORE += len(collected_coins)

    pygame.display.update()
    FramePerSec.tick(FPS)