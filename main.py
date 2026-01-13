import pygame
import random

# Настройки игры
WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20
FPS = 60
FOOD_TYPES = ['normal', 'gold']

# Цвета
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 36)
        self.levels = [
            {"name": "Easy", "delay": 200},
            {"name": "Medium", "delay": 100},
            {"name": "Hard", "delay": 50}
        ]
        self.colors = [GREEN, BLUE, RED]
        self.color_names = ["Green", "Blue", "Red"]
        self.selected = 0
        self.step = 'level'  # 'level' or 'color'

    def draw(self):
        self.screen.fill(BLACK)
        if self.step == 'level':
            title = self.font.render("Choose Level", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 120, HEIGHT // 2 - 100))
            for i, level in enumerate(self.levels):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {level['name']}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 50 + i * 40))
        elif self.step == 'color':
            title = self.font.render("Choose Snake Color", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 150, HEIGHT // 2 - 100))
            for i, color_name in enumerate(self.color_names):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {color_name}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 50 + i * 40))
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.levels if self.step == 'level' else self.colors)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.levels if self.step == 'level' else self.colors)
                elif event.key == pygame.K_RETURN:
                    if self.step == 'level':
                        self.step = 'color'
                        self.selected = 0
                        return 'next'
                    elif self.step == 'color':
                        return {'delay': self.levels[self.selected_level]['delay'], 'color': self.colors[self.selected]}
                elif event.key == pygame.K_BACKSPACE and self.step == 'color':
                    self.step = 'level'
                    self.selected = self.selected_level
                    return 'back'
        return -1

    def run(self):
        self.step = 'level'
        self.selected = 0
        self.selected_level = 0
        while True:
            self.draw()
            result = self.handle_events()
            if result is None:
                return None
            elif result == 'next':
                self.selected_level = self.selected
                continue
            elif result == 'back':
                continue
            elif isinstance(result, dict):
                return result['delay'], result['color']

class SnakeGame:
    def __init__(self, move_delay, snake_color):
        self.move_delay = move_delay
        self.snake_color = snake_color
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        self.snake = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = (CELL_SIZE, 0)  # Вправо
        self.food = self.random_food()
        self.score = 0
        self.game_over = False
        self.last_move_time = 0

    def random_food(self):
        x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        food_type = random.choice(FOOD_TYPES)
        return {'pos': (x, y), 'type': food_type}

    def add_segment(self):
        # Добавляем новый сегмент в конец змеи
        if self.snake:
            tail = self.snake[-1]
            new_segment = (tail[0], tail[1])  # Пока на месте хвоста, но move сдвинет
            self.snake.append(new_segment)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != (0, CELL_SIZE):
                    self.direction = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and self.direction != (0, -CELL_SIZE):
                    self.direction = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and self.direction != (CELL_SIZE, 0):
                    self.direction = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-CELL_SIZE, 0):
                    self.direction = (CELL_SIZE, 0)

    def move(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Проверяем столкновения
        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT or
            new_head in self.snake):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Проверяем еду
        if new_head == self.food['pos']:
            points = 3 if self.food['type'] == 'gold' else 1
            self.score += points
            growth = 3 if self.food['type'] == 'gold' else 1
            for _ in range(growth):
                self.add_segment()
            self.food = self.random_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BLACK)

        # Рисуем змею
        for segment in self.snake:
            pygame.draw.rect(self.screen, self.snake_color, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

        # Рисуем еду
        food_color = GOLD if self.food['type'] == 'gold' else RED
        pygame.draw.rect(self.screen, food_color, (self.food['pos'][0], self.food['pos'][1], CELL_SIZE, CELL_SIZE))

        # Рисуем счет
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 10))

        pygame.display.flip()

    def show_game_over(self):
        button_font = pygame.font.SysFont(None, 36)
        buttons = [
            {"text": "Restart", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50), "action": 'restart'},
            {"text": "Menu", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50), "action": 'menu'},
            {"text": "Quit", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50), "action": None}
        ]

        while True:
            self.screen.fill(BLACK)
            font = pygame.font.SysFont(None, 48)
            text = font.render(f"Game Over! Score: {self.score}", True, WHITE)
            self.screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))

            for button in buttons:
                pygame.draw.rect(self.screen, GRAY, button["rect"])
                text_surf = button_font.render(button["text"], True, BLACK)
                text_rect = text_surf.get_rect(center=button["rect"].center)
                self.screen.blit(text_surf, text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левый клик
                        for button in buttons:
                            if button["rect"].collidepoint(event.pos):
                                return button["action"]
            self.clock.tick(FPS)

    def run(self):
        while not self.game_over:
            current_time = pygame.time.get_ticks()
            self.handle_events()

            if current_time - self.last_move_time > self.move_delay:
                self.move()
                self.last_move_time = current_time

            self.draw()
            self.clock.tick(FPS)

        return self.show_game_over()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    menu = Menu(screen)
    while True:
        result = menu.run()
        if result is None:
            break
        delay, color = result
        game = SnakeGame(delay, color)
        game.screen = screen
        game_result = game.run()
        if game_result == 'restart':
            continue  # Начать игру заново с тем же уровнем и цветом
        elif game_result == 'menu':
            continue  # Вернуться в меню
        else:
            break  # Выход
    pygame.quit()

if __name__ == "__main__":
    main()