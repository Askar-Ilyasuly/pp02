
import pygame, sys
from pygame.locals import *
import random, time

# ───────────────────────────────────────────
#  Инициализация
# ───────────────────────────────────────────
pygame.init()
FPS = 60
FramePerSec = pygame.time.Clock()

# Цвета
BLACK  = (0,   0,   0  )
WHITE  = (255, 255, 255)
RED    = (255, 0,   0  )
YELLOW = (255, 220, 0  )
GRAY   = (50,  50,  50 )

# Размеры экрана
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

# Игровые переменные
SPEED = 5
SCORE = 0   # Пройденные машины (слева)
COINS = 0   # Монеты (справа)

# Шрифты
font_small = pygame.font.SysFont("Verdana", 20)
font_large = pygame.font.SysFont("Verdana", 60)

# Настройка экрана
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("F1 Racer")

# Загрузка фона
background = pygame.image.load("AnimatedStreet.png")


# ───────────────────────────────────────────
#  Вспомогательная функция: текст с тенью
# ───────────────────────────────────────────
def draw_text_shadow(surface, text, font, x, y, color=WHITE, shadow_color=BLACK):
    """Рисует текст с тёмной тенью — хорошо виден на любом фоне."""
    shadow_surf = font.render(text, True, shadow_color)
    text_surf   = font.render(text, True, color)
    surface.blit(shadow_surf, (x + 2, y + 2))   # тень чуть правее и ниже
    surface.blit(text_surf,   (x,     y    ))


# ───────────────────────────────────────────
#  Класс Coin (монета)
# ───────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Рисуем монету программно — жёлтый круг
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
        pygame.draw.circle(self.image, (200, 160, 0), (10, 10), 10, 2)  # обводка
        self.rect = self.image.get_rect()
        self._respawn()

    def _respawn(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn()


# ───────────────────────────────────────────
#  Класс Enemy (вражеская машина)
# ───────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect  = self.image.get_rect()
        self._respawn()

    def _respawn(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1          # +1 за каждую объехавшую машину
            self._respawn()


# ───────────────────────────────────────────
#  Класс Player (игрок)
# ───────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect  = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        keys = pygame.key.get_pressed()
        if self.rect.left > 0 and keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and keys[K_RIGHT]:
            self.rect.move_ip(5, 0)


# ───────────────────────────────────────────
#  Создание объектов
# ───────────────────────────────────────────
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies     = pygame.sprite.Group(E1)
coins       = pygame.sprite.Group(C1)
all_sprites = pygame.sprite.Group(P1, E1, C1)

# Таймер увеличения скорости (каждую секунду)
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)


# ───────────────────────────────────────────
#  Главный игровой цикл
# ───────────────────────────────────────────
while True:

    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # --- Фон ---


    DISPLAYSURF.blit(background, (0, 0))

    # --- Счётчики (текст с тенью, хорошо виден на любом фоне) ---
    draw_text_shadow(DISPLAYSURF, f"Cars: {SCORE}", font_small, 10,  10)
    draw_text_shadow(DISPLAYSURF, f"Coins: {COINS}", font_small, 290, 10)

    # --- Движение и отрисовка всех спрайтов ---
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # --- Подбор монет ---
    collected = pygame.sprite.spritecollide(P1, coins, False)
    for coin in collected:
        COINS += 1
        coin._respawn()     # монета появляется заново сверху

    # --- Проверка столкновения с врагом ---
    if pygame.sprite.spritecollideany(P1, enemies):
        # pygame.mixer.Sound('crash.wav').play()  # раскомментируй если есть звук
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        draw_text_shadow(DISPLAYSURF, "GAME OVER", font_large, 30, 220)
        draw_text_shadow(DISPLAYSURF, f"Cars:  {SCORE}", font_small, 130, 310)
        draw_text_shadow(DISPLAYSURF, f"Coins: {COINS}", font_small, 130, 340)
        pygame.display.update()
        time.sleep(3)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)
