
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
SCORE = 0   # монеты
CARS  = 0   # пройденные машины

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("F1 Racer")

font_big   = pygame.font.SysFont("Arial", 60)
font_small = pygame.font.SysFont("Arial", 30)
game_over_text = font_big.render("Game Over", True, BLACK)

background = pygame.image.load(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\AnimatedStreet.png")
player_img = pygame.image.load(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\Player.png")
enemy_img  = pygame.image.load(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\Enemy.png")

coin_sound  = pygame.mixer.Sound(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\coin.wav")
crash_sound = pygame.mixer.Sound(r"C:\Users\Askar\Desktop\pp2 (1)\practice-10\racer\crash.wav")
coin_sound.set_volume(1.0)
crash_sound.set_volume(1.0)


# ──────────────────────────────────────────
#  Вспомогательная функция: текст с тенью
# ──────────────────────────────────────────
def draw_text_shadow(surface, text, font, x, y, color=WHITE, shadow=BLACK):
    surface.blit(font.render(text, True, shadow), (x + 2, y + 2))
    surface.blit(font.render(text, True, color),  (x,     y    ))


class Coin(pygame.sprite.Sprite):
    RADIUS  = 12
    OUTLINE = (230, 230, 0)

    def __init__(self):
        super().__init__()
        side = self.RADIUS * 2
        self.image = pygame.Surface((side, side), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.OUTLINE, (self.RADIUS, self.RADIUS), self.RADIUS)
        pygame.draw.circle(self.image, YELLOW,       (self.RADIUS, self.RADIUS), self.RADIUS - 2)
        x = random.randint(40, SCREEN_WIDTH - 40)
        self.rect = self.image.get_rect(center=(x, -20))

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect  = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global CARS
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            CARS += 1   # +1 когда машина проехала мимо
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]  and self.rect.left  > 0:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)


P1 = Player()
E1 = Enemy()

enemies     = pygame.sprite.Group(E1)
coins       = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(P1, E1)


def create_coin():
    c = Coin()
    coins.add(c)
    all_sprites.add(c)


def show_hud():
    # Слева: Cars (пройденные машины)
    draw_text_shadow(DISPLAYSURF, f"Cars: {CARS}",   font_small, 10,  10)
    # Справа: Coins (монеты)
    draw_text_shadow(DISPLAYSURF, f"Coins: {SCORE}", font_small, SCREEN_WIDTH - 130, 10)


INC_SPEED  = pygame.USEREVENT + 1
COIN_SPAWN = pygame.USEREVENT + 2
pygame.time.set_timer(INC_SPEED,  1000)
pygame.time.set_timer(COIN_SPAWN, 1500)



while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == INC_SPEED:
            SPEED += 0.2

    if event.type == COIN_SPAWN:
     if len(coins) == 0:   # <-- проверка
        create_coin()

    DISPLAYSURF.blit(background, (0, 0))

    show_hud()   # <- рисуем оба счётчика

    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Подбор монет
    collected = pygame.sprite.spritecollide(P1, coins, True)
    if collected:
        coin_sound.play()
        SCORE += len(collected)

    # Столкновение с врагом
    if pygame.sprite.spritecollideany(P1, enemies):
        crash_sound.play()
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (60, 180))
        draw_text_shadow(DISPLAYSURF, f"Cars passed: {CARS}",      font_small, 90, 300)
        draw_text_shadow(DISPLAYSURF, f"Coins collected: {SCORE}", font_small, 60, 340)
        pygame.display.update()
        time.sleep(3)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)
