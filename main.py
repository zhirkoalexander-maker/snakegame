class Snake:
    def __init__(self, start_pos, direction, color, texture=None, controls=None, is_bot=False):
        self.body = [start_pos]
        self.direction = direction
        self.color = color
        self.texture = texture
        self.controls = controls or {}
        self.is_bot = is_bot
        self.grow_pending = 0
        self.alive = True
        self.score = 0

    def get_head(self):
        return self.body[0]

    def set_direction(self, key):
        if key in self.controls:
            new_dir = self.controls[key]
            # Запретить разворот назад
            if (new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]):
                self.direction = new_dir

    def move(self, wrap_around=False):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        if wrap_around:
            new_head = ((new_head[0]) % WIDTH, (new_head[1]) % HEIGHT)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, n=1):
        self.grow_pending += n

    def check_collision(self, walls, snakes, walls_enabled=True):
        head = self.get_head()
        if walls_enabled and head in walls:
            self.alive = False
        if walls_enabled and (head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT):
            self.alive = False
        if head in self.body[1:]:
            self.alive = False
        for snake in snakes:
            if snake is not self:
                # Если врезались голова в голову — умирает только self
                if head == snake.get_head():
                    self.alive = False
                # Если врезались в тело другой змеи (не в голову) — умирает только эта змея
                elif head in snake.body[1:]:
                    self.alive = False

    def draw(self, screen):
        for segment in self.body:
            # Рисуем строго по сетке
            x = (segment[0] // CELL_SIZE) * CELL_SIZE
            y = (segment[1] // CELL_SIZE) * CELL_SIZE
            if self.texture:
                screen.blit(self.texture, (x, y))
            else:
                pygame.draw.rect(screen, self.color, (x, y, CELL_SIZE, CELL_SIZE))

import pygame
import random
import os

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
        self.modes = ["Single", "PvP", "Bot"]
        self.walls_types = ["With walls", "No walls"]
        self.selected = 0
        self.step = 'mode'  # 'mode', 'walls', 'level', 'color'
        self.selected_mode = 0
        self.selected_walls = 0
        self.selected_level = 0

    def draw(self):
        self.screen.fill(BLACK)
        if self.step == 'mode':
            title = self.font.render("Choose Game Mode", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 170, HEIGHT // 2 - 100))
            for i, mode in enumerate(self.modes):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {mode}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 50 + i * 40))
        elif self.step == 'walls':
            title = self.font.render("Choose Walls", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 120, HEIGHT // 2 - 100))
            for i, wtype in enumerate(self.walls_types):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {wtype}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 50 + i * 40))
        elif self.step == 'level':
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
                if self.step == 'mode':
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.modes)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.modes)
                    elif event.key == pygame.K_RETURN:
                        self.selected_mode = self.selected
                        self.step = 'walls'
                        self.selected = 0
                        return 'next'
                elif self.step == 'walls':
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.walls_types)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.walls_types)
                    elif event.key == pygame.K_RETURN:
                        self.selected_walls = self.selected
                        self.step = 'level'
                        self.selected = 0
                        return 'next'
                    elif event.key == pygame.K_BACKSPACE:
                        self.step = 'mode'
                        self.selected = self.selected_mode
                        return 'back'
                elif self.step == 'level':
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.levels)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.levels)
                    elif event.key == pygame.K_RETURN:
                        self.selected_level = self.selected
                        self.step = 'color'
                        self.selected = 0
                        return 'next'
                    elif event.key == pygame.K_BACKSPACE:
                        self.step = 'walls'
                        self.selected = self.selected_walls
                        return 'back'
                elif self.step == 'color':
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.colors)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.colors)
                    elif event.key == pygame.K_RETURN:
                        return {
                            'mode': self.modes[self.selected_mode],
                            'walls': self.walls_types[self.selected_walls],
                            'delay': self.levels[self.selected_level]['delay'],
                            'color': self.colors[self.selected]
                        }
                    elif event.key == pygame.K_BACKSPACE:
                        self.step = 'level'
                        self.selected = self.selected_level
                        return 'back'
        return -1

    def run(self):
        self.step = 'mode'
        self.selected = 0
        self.selected_mode = 0
        self.selected_walls = 0
        self.selected_level = 0
        while True:
            self.draw()
            result = self.handle_events()
            if result is None:
                return None
            elif result == 'next':
                continue
            elif result == 'back':
                continue
            elif isinstance(result, dict):
                return result

class SnakeGame:
    def __init__(self, move_delay, snake_color, mode='single', bot_color=BLUE, walls_type="Frame walls"):
        # Запретить совпадение цветов змеи и бота
        if bot_color == snake_color:
            alt_colors = [c for c in [GREEN, BLUE, RED, (255,255,0), (255,0,255), (0,255,255)] if c != snake_color]
            bot_color = alt_colors[0]
        self.move_delay = move_delay
        self.snake_color = snake_color
        self.mode = mode
        self.bot_color = bot_color
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.screen = None
        # Загрузка текстуры змейки
        self.snake_texture = None
        texture_path = os.path.join(os.path.dirname(__file__), 'snake_texture.png')
        if os.path.exists(texture_path):
            try:
                self.snake_texture = pygame.image.load(texture_path).convert_alpha()
                self.snake_texture = pygame.transform.scale(self.snake_texture, (CELL_SIZE, CELL_SIZE))
            except Exception:
                self.snake_texture = None
        # Генерация стен
        self.walls = []
        if walls_type == "With walls":
            # Случайные стены в зависимости от сложности
            wall_count = 0
            if self.move_delay >= 200:  # Easy
                wall_count = 10
            elif self.move_delay >= 100:  # Medium
                wall_count = 20
            else:  # Hard
                wall_count = 35
            for _ in range(wall_count):
                x = random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE
                y = random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
                forbidden = [(WIDTH // 2, HEIGHT // 2), (WIDTH // 4, HEIGHT // 2), (3*WIDTH // 4, HEIGHT // 2)]
                if (x, y) not in forbidden:
                    self.walls.append((x, y))
        # Игроки
        self.snakes = []
        if mode == 'single':
            # Управление стрелками и WASD
            controls = {
                pygame.K_UP: (0, -CELL_SIZE), pygame.K_DOWN: (0, CELL_SIZE),
                pygame.K_LEFT: (-CELL_SIZE, 0), pygame.K_RIGHT: (CELL_SIZE, 0),
                pygame.K_w: (0, -CELL_SIZE), pygame.K_s: (0, CELL_SIZE),
                pygame.K_a: (-CELL_SIZE, 0), pygame.K_d: (CELL_SIZE, 0)
            }
            self.snakes.append(Snake((WIDTH // 2, HEIGHT // 2), (CELL_SIZE, 0), snake_color, self.snake_texture, controls=controls))
        elif mode == 'pvp':
            self.snakes.append(Snake((WIDTH // 4, HEIGHT // 2), (CELL_SIZE, 0), snake_color, self.snake_texture, controls={pygame.K_w:(0,-CELL_SIZE),pygame.K_s:(0,CELL_SIZE),pygame.K_a:(-CELL_SIZE,0),pygame.K_d:(CELL_SIZE,0)}))
            self.snakes.append(Snake((3*WIDTH // 4, HEIGHT // 2), (-CELL_SIZE, 0), self.bot_color, None, controls={pygame.K_UP:(0,-CELL_SIZE),pygame.K_DOWN:(0,CELL_SIZE),pygame.K_LEFT:(-CELL_SIZE,0),pygame.K_RIGHT:(CELL_SIZE,0)}))
        elif mode == 'bot':
            # Игрок управляет и стрелками, и WASD
            controls = {
                pygame.K_UP: (0, -CELL_SIZE), pygame.K_DOWN: (0, CELL_SIZE),
                pygame.K_LEFT: (-CELL_SIZE, 0), pygame.K_RIGHT: (CELL_SIZE, 0),
                pygame.K_w: (0, -CELL_SIZE), pygame.K_s: (0, CELL_SIZE),
                pygame.K_a: (-CELL_SIZE, 0), pygame.K_d: (CELL_SIZE, 0)
            }
            self.snakes.append(Snake((WIDTH // 4, HEIGHT // 2), (CELL_SIZE, 0), snake_color, self.snake_texture, controls=controls))
            self.snakes.append(Snake((3*WIDTH // 4, HEIGHT // 2), (-CELL_SIZE, 0), self.bot_color, None, is_bot=True))
        self.food = self.random_food()
        self.game_over = False
        self.last_move_time = 0
        self.walls_type = walls_type

    def random_food(self):
        while True:
            x = random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE
            y = random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
            pos = (x, y)
            if pos not in self.walls and all(pos not in s.body for s in self.snakes):
                food_type = random.choice(FOOD_TYPES)
                return {'pos': pos, 'type': food_type}

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
                for snake in self.snakes:
                    if not snake.is_bot:
                        snake.set_direction(event.key)

    def move(self):
        # Определяем, включены ли стены
        walls_enabled = len(self.walls) > 0
        wrap_around = (self.walls_type == 'No walls')
        # Бот управляет собой
        for snake in self.snakes:
            if snake.is_bot and snake.alive:
                self.bot_move(snake)
        # Двигаем всех живых змей
        for snake in self.snakes:
            if snake.alive:
                snake.move(wrap_around=wrap_around)
        # Проверяем коллизии только для живых змей
        for snake in self.snakes:
            if not snake.alive:
                continue
            snake.check_collision(self.walls, [s for s in self.snakes if s.alive], walls_enabled=walls_enabled)
        # Проверяем сбор яблока только живыми змеями
        for snake in self.snakes:
            if not snake.alive:
                continue
            head = snake.get_head()
            # Привести координаты к сетке для сравнения
            head_grid = (head[0] // CELL_SIZE * CELL_SIZE, head[1] // CELL_SIZE * CELL_SIZE)
            food_grid = (self.food['pos'][0] // CELL_SIZE * CELL_SIZE, self.food['pos'][1] // CELL_SIZE * CELL_SIZE)
            # Удаляем отладочный print
            # print(f"DEBUG: head={head}, head_grid={head_grid}, food={self.food['pos']}, food_grid={food_grid}")
            if head_grid == food_grid:
                points = 3 if self.food['type'] == 'gold' else 1
                snake.score += points
                growth = 3 if self.food['type'] == 'gold' else 1
                snake.grow(growth)
                self.food = self.random_food()
        # Если все змеи мертвы — конец игры
        if not any(s.alive for s in self.snakes):
            self.game_over = True
        # Проверяем стыковку голов после движения всех змей
        heads = [snake.get_head() for snake in self.snakes if snake.alive]
        for i, snake in enumerate(self.snakes):
            if not snake.alive:
                continue
            # Если две головы совпали — обе умирают
            for j, other in enumerate(self.snakes):
                if i != j and other.alive and snake.get_head() == other.get_head():
                    snake.alive = False
                    other.alive = False
        # Если игрок или бот погибает (врезается в стену или в себя/другого) — сразу показываем экран смерти
        if self.mode in ('single', 'bot'):
            if not self.snakes[0].alive or (len(self.snakes) > 1 and not self.snakes[1].alive):
                self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)
        # Рисуем стены
        for wall in self.walls:
            pygame.draw.rect(self.screen, GRAY, (wall[0], wall[1], CELL_SIZE, CELL_SIZE))
        # Рисуем змей
        for snake in self.snakes:
            snake.draw(self.screen)
        # Рисуем еду
        food_color = GOLD if self.food['type'] == 'gold' else RED
        # Рисуем яблоко строго по сетке
        fx = (self.food['pos'][0] // CELL_SIZE) * CELL_SIZE
        fy = (self.food['pos'][1] // CELL_SIZE) * CELL_SIZE
        pygame.draw.rect(self.screen, food_color, (fx, fy, CELL_SIZE, CELL_SIZE))
        # Рисуем счет
        font = pygame.font.SysFont(None, 36)
        for i, snake in enumerate(self.snakes):
            text = font.render(f"P{i+1} Score: {snake.score}", True, snake.color)
            self.screen.blit(text, (10, 10 + i * 30))
        pygame.display.flip()

    def bot_move(self, snake):
        # Примитивный бот: идёт к еде, избегает стены
        head = snake.get_head()
        fx, fy = self.food['pos']
        options = [
            (CELL_SIZE, 0), (-CELL_SIZE, 0), (0, CELL_SIZE), (0, -CELL_SIZE)
        ]
        best = snake.direction
        min_dist = float('inf')
        for d in options:
            nx, ny = head[0] + d[0], head[1] + d[1]
            pos = (nx, ny)
            if pos in self.walls:
                continue
            dist = abs(fx - nx) + abs(fy - ny)
            if dist < min_dist:
                min_dist = dist
                best = d
        snake.direction = best
        # Удаляем отладочный print для бота
        # print(f"BOT DEBUG: alive={snake.alive}, score={snake.score}, head={snake.get_head()}, body={snake.body}")

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
            text = font.render("Game Over!", True, WHITE)
            self.screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 80))
            # Выводим счет всех змей
            score_font = pygame.font.SysFont(None, 36)
            for i, snake in enumerate(self.snakes):
                score_text = score_font.render(f"P{i+1} Score: {snake.score}", True, snake.color)
                self.screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 - 40 + i * 30))

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
        # Выбор режима
        mode = 'single'
        # Для теста: клавиша 1 — одиночный, 2 — pvp, 3 — bot
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = 'single'
                elif event.key == pygame.K_2:
                    mode = 'pvp'
                elif event.key == pygame.K_3:
                    mode = 'bot'
        result = menu.run()
        if result is None:
            break
        mode = result['mode'].lower()
        walls = result['walls']
        delay = result['delay']
        color = result['color']
        game = SnakeGame(delay, color, mode=mode, bot_color=BLUE, walls_type=walls)
        game.screen = screen
        game_result = game.run()
        if game_result == 'restart':
            continue  # Начать игру заново с теми же параметрами
        elif game_result == 'menu':
            break  # Вернуться в меню
        else:
            break  # Выход
    pygame.quit()

if __name__ == "__main__":
    main()
