import pygame
import random

colorBLACK  = (0,   0,   0)
colorWHITE  = (255, 255, 255)
colorGRAY   = (40,  40,  40)
colorRED    = (220, 50,  50)
colorYELLOW = (240, 200, 60)
colorGREEN  = (60,  200, 90)
colorCYAN   = (80,  220, 220)
colorORANGE = (255, 150, 30)

pygame.init()

WIDTH  = 600
HEIGHT = 660     
CELL   = 30

GRID_COLS = WIDTH  // CELL
GRID_ROWS = HEIGHT // CELL

PLAY_ROWS = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

font_big   = pygame.font.SysFont("consolas", 26, bold=True)
font_small = pygame.font.SysFont("consolas", 18)


FOODS_PER_LEVEL   = 3
BASE_FPS          = 5
SPEED_INCREMENT   = 2


def draw_grid():
    """Draw a subtle grid over the play area."""
    for row in range(PLAY_ROWS):
        for col in range(GRID_COLS):
            pygame.draw.rect(
                screen, colorGRAY,
                (col * CELL, row * CELL, CELL, CELL), 1
            )

def draw_hud(score: int, level: int, fps: int):
    hud_y = PLAY_ROWS * CELL

    pygame.draw.rect(screen, (15, 15, 15), (0, hud_y, WIDTH, HEIGHT - hud_y))
    pygame.draw.line(screen, colorCYAN, (0, hud_y), (WIDTH, hud_y), 2)

    score_surf = font_big.render(f"SCORE: {score}", True, colorCYAN)
    level_surf = font_big.render(f"LEVEL: {level}", True, colorORANGE)
    speed_surf = font_small.render(f"speed {fps} fps", True, colorGRAY)

    screen.blit(score_surf, (10,  hud_y + 8))
    screen.blit(level_surf, (220, hud_y + 8))
    screen.blit(speed_surf, (430, hud_y + 18))


def draw_overlay(lines: list[str], color=(255, 255, 255)):
    overlay = pygame.Surface((WIDTH, PLAY_ROWS * CELL), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    total_h = len(lines) * 44
    start_y = (PLAY_ROWS * CELL - total_h) // 2

    for i, line in enumerate(lines):
        surf = font_big.render(line, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, start_y + i * 44))
        screen.blit(surf, rect)

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"


class Snake:
    def __init__(self):
        
        mid = PLAY_ROWS // 2
        self.body: list[Point] = [
            Point(10, mid),
            Point(9,  mid),
            Point(8,  mid),
        ]
        self.dx = 1
        self.dy = 0
        self.alive = True      


    def set_direction(self, dx: int, dy: int):
        if dx == -self.dx and dy == -self.dy:
            return
        self.dx = dx
        self.dy = dy

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy

        head = self.body[0]
        if not (0 <= head.x < GRID_COLS and 0 <= head.y < PLAY_ROWS):
            self.alive = False
            return

        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                self.alive = False
                return

    def grow(self):
        tail = self.body[-1]
        self.body.append(Point(tail.x, tail.y))

    def occupies(self, x: int, y: int) -> bool:
        return any(s.x == x and s.y == y for s in self.body)

    def check_food(self, food: "Food") -> bool:
     
        head = self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            self.grow()
            return True
        return False

    def draw(self):
       
        head = self.body[0]
        pygame.draw.rect(
            screen, colorRED,
            (head.x * CELL + 1, head.y * CELL + 1, CELL - 2, CELL - 2)
        )
        for seg in self.body[1:]:
            pygame.draw.rect(
                screen, colorYELLOW,
                (seg.x * CELL + 2, seg.y * CELL + 2, CELL - 4, CELL - 4)
            )
# Food
class Food:
    def __init__(self):
        self.pos = Point(15, 10)

    def generate_random_pos(self, snake: Snake):
       
        while True:
            x = random.randint(0, GRID_COLS - 1)
            y = random.randint(0, PLAY_ROWS - 1)
            if not snake.occupies(x, y):
                self.pos.x = x
                self.pos.y = y
                return
    def draw(self):
        pygame.draw.rect(
            screen, colorGREEN,
            (self.pos.x * CELL + 2, self.pos.y * CELL + 2, CELL - 4, CELL - 4)
        )

def reset_game():
  
    snake = Snake()
    food  = Food()
    food.generate_random_pos(snake)
    return snake, food, 0, 1, BASE_FPS, 0

clock = pygame.time.Clock()

snake, food, score, level, current_fps, foods_eaten = reset_game()

game_over   = False
level_up    = False
level_flash = 0    

running = True
while running:

 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_over:
       
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    snake.set_direction(1, 0)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    snake.set_direction(-1, 0)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    snake.set_direction(0, 1)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    snake.set_direction(0, -1)
            else:
 
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    snake, food, score, level, current_fps, foods_eaten = reset_game()
                    game_over = False

    if not game_over:
        snake.move()

        if not snake.alive:
            game_over = True
        else:
     
            if snake.check_food(food):
                score       += 10
                foods_eaten += 1
                food.generate_random_pos(snake)

                if foods_eaten >= FOODS_PER_LEVEL:
                    level       += 1
                    foods_eaten  = 0
                    current_fps += SPEED_INCREMENT   
                    level_flash  = int(current_fps * 1.5)  

        
        if level_flash > 0:
            level_flash -= 1

    
    screen.fill(colorBLACK)
    draw_grid()
    food.draw()
    snake.draw()

    
    draw_hud(score, level, current_fps)

    if level_flash > 0 and not game_over:
        draw_overlay(
            [f"LEVEL {level}!", f"Speed ×{level}"],
            colorORANGE
        )

    if game_over:
        draw_overlay(
            ["GAME OVER", f"Score: {score}", "ENTER to restart"],
            colorRED
        )
    pygame.display.flip()
    clock.tick(current_fps)   

pygame.quit()