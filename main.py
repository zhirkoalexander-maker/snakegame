class Snake:
    def __init__(self, start_pos, direction, color, controls=None, is_bot=False):
        self.body = [start_pos]
        self.direction = direction
        self.next_direction = direction  # Буфер для следующего направления
        self.color = color
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
            # Запретить разворот назад (используем next_direction для проверки)
            if (new_dir[0] != -self.next_direction[0] or new_dir[1] != -self.next_direction[1]):
                self.next_direction = new_dir

    def move(self, wrap_around=False, field_width=None, field_height=None):
        if field_width is None:
            field_width = 600  # WIDTH
        if field_height is None:
            field_height = 600  # HEIGHT
        # Применяем буферизованное направление
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        if wrap_around:
            new_head = (new_head[0] % field_width, new_head[1] % field_height)
        # Если не растём, удаляем хвост перед проверкой коллизии, чтобы не умирать на месте после еды
        if self.grow_pending == 0:
            tail = self.body.pop()
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        # Если не растём, хвост уже удалён выше

    def grow(self, n=1):
        self.grow_pending += n

    def check_collision(self, walls, snakes, walls_enabled=True, field_width=None, field_height=None, wrap_around=False):
        head = self.get_head()
        # Серые стены убивают всегда
        if walls_enabled and head in walls:
            self.alive = False
        # Границы убивают только если wrap_around == False
        if not wrap_around:
            if field_width is None:
                field_width = 600
            if field_height is None:
                field_height = 600
            if head[0] < 0 or head[0] >= field_width or head[1] < 0 or head[1] >= field_height:
                self.alive = False
        if head in self.body[1:]:
            self.alive = False
        for snake in snakes:
            if snake is not self:
                if head == snake.get_head():
                    self.alive = False
                elif head in snake.body[1:]:
                    self.alive = False

    def draw(self, screen):
        for segment in self.body:
            # Рисуем строго по сетке
            x = (segment[0] // CELL_SIZE) * CELL_SIZE
            y = (segment[1] // CELL_SIZE) * CELL_SIZE
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
        self.colors = [GREEN, BLUE, RED, (255,255,0), (255,0,255), (0,255,255), (255,128,0), (128,0,255), (0,255,128)]
        self.color_names = ["Green", "Blue", "Red", "Yellow", "Magenta", "Cyan", "Orange", "Purple", "Aqua"]
        self.modes = ["Single", "PvP", "Bot"]
        self.walls_types = ["With walls", "No walls"]
        self.selected = 0
        self.step = 'mode'  # 'mode', 'walls', 'level', 'color'
        self.selected_mode = 0
        self.selected_walls = 0
        self.selected_level = 0

    def draw(self):
        # Получаем текущий размер окна
        screen_rect = self.screen.get_rect()
        center_x = screen_rect.centerx
        center_y = screen_rect.centery
        self.screen.fill(BLACK)
        if self.step == 'mode':
            title = self.font.render("Choose Game Mode", True, WHITE)
            self.screen.blit(title, (center_x - 170, center_y - 100))
            for i, mode in enumerate(self.modes):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {mode}", True, color)
                self.screen.blit(text, (center_x - 80, center_y - 50 + i * 40))
        elif self.step == 'walls':
            title = self.font.render("Choose Walls", True, WHITE)
            self.screen.blit(title, (center_x - 120, center_y - 100))
            for i, wtype in enumerate(self.walls_types):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {wtype}", True, color)
                self.screen.blit(text, (center_x - 80, center_y - 50 + i * 40))
        elif self.step == 'level':
            title = self.font.render("Choose Level", True, WHITE)
            self.screen.blit(title, (center_x - 120, center_y - 100))
            for i, level in enumerate(self.levels):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {level['name']}", True, color)
                self.screen.blit(text, (center_x - 80, center_y - 50 + i * 40))
        elif self.step == 'color':
            title = self.font.render("Choose Snake Color", True, WHITE)
            self.screen.blit(title, (center_x - 150, center_y - 100))
            for i, color_name in enumerate(self.color_names):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {color_name}", True, color)
                self.screen.blit(text, (center_x - 80, center_y - 50 + i * 40))
        # Кнопки увеличения/уменьшения размера окна (зум)
        button_font = pygame.font.SysFont(None, 28)
        plus_rect = pygame.Rect(self.screen.get_width() - 90, 10, 35, 35)
        minus_rect = pygame.Rect(self.screen.get_width() - 50, 10, 35, 35)
        pygame.draw.rect(self.screen, GRAY, plus_rect)
        pygame.draw.rect(self.screen, GRAY, minus_rect)
        plus_text = button_font.render("+", True, BLACK)
        minus_text = button_font.render("-", True, BLACK)
        self.screen.blit(plus_text, plus_rect.move(10, 2))
        self.screen.blit(minus_text, minus_rect.move(10, 2))
        # Обработка кликов по кнопкам
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if plus_rect.collidepoint(event.pos):
                pygame.display.set_mode((self.screen.get_width() + 100, self.screen.get_height() + 100), pygame.RESIZABLE)
                pygame.display.flip()
            elif minus_rect.collidepoint(event.pos):
                pygame.display.set_mode((max(300, self.screen.get_width() - 100), max(300, self.screen.get_height() - 100)), pygame.RESIZABLE)
                pygame.display.flip()
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((WIDTH, HEIGHT))
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
            # Центрируем меню при любом размере окна
            screen_rect = self.screen.get_rect()
            self.center_x = screen_rect.centerx
            self.center_y = screen_rect.centery
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
    def handle_zoom(self):
        # Обновить self.screen после изменения размера окна
        self.screen = pygame.display.get_surface()
        self.regenerate_walls()
        self.food = self.random_food()

    def regenerate_walls(self):
        # Перегенерировать стены при изменении размера окна
        self.walls = []
        if self.walls_type == "With walls":
            screen_w = (self.screen.get_width() // CELL_SIZE)
            screen_h = (self.screen.get_height() // CELL_SIZE)
            wall_count = 0
            if self.move_delay >= 200:  # Easy
                wall_count = 30
            elif self.move_delay >= 100:  # Medium
                wall_count = 60
            else:  # Hard
                wall_count = 120
            forbidden = [
                (screen_w // 2 * CELL_SIZE, screen_h // 2 * CELL_SIZE),
                (screen_w // 4 * CELL_SIZE, screen_h // 2 * CELL_SIZE),
                (3 * screen_w // 4 * CELL_SIZE, screen_h // 2 * CELL_SIZE)
            ]
            for _ in range(wall_count):
                while True:
                    x = random.randint(0, screen_w - 1) * CELL_SIZE
                    y = random.randint(0, screen_h - 1) * CELL_SIZE
                    if (x, y) not in forbidden and x != 0 and y != 0 and x != (screen_w-1)*CELL_SIZE and y != (screen_h-1)*CELL_SIZE:
                        self.walls.append((x, y))
                        break
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
        # Генерация стен: случайно по всему полю, не по периметру, с учетом размера окна
        self.walls = []
        if walls_type == "With walls":
            # Получаем размер окна
            screen_w = (pygame.display.get_surface().get_width() // CELL_SIZE)
            screen_h = (pygame.display.get_surface().get_height() // CELL_SIZE)
            wall_count = 0
            if self.move_delay >= 200:  # Easy
                wall_count = 30
            elif self.move_delay >= 100:  # Medium
                wall_count = 60
            else:  # Hard
                wall_count = 120
            forbidden = [
                (screen_w // 2 * CELL_SIZE, screen_h // 2 * CELL_SIZE),
                (screen_w // 4 * CELL_SIZE, screen_h // 2 * CELL_SIZE),
                (3 * screen_w // 4 * CELL_SIZE, screen_h // 2 * CELL_SIZE)
            ]
            for _ in range(wall_count):
                while True:
                    x = random.randint(0, screen_w - 1) * CELL_SIZE
                    y = random.randint(0, screen_h - 1) * CELL_SIZE
                    if (x, y) not in forbidden and x != 0 and y != 0 and x != (screen_w-1)*CELL_SIZE and y != (screen_h-1)*CELL_SIZE:
                        self.walls.append((x, y))
                        break
        # Игроки
        self.snakes = []
        if mode == 'single':
            controls = {
                pygame.K_UP: (0, -CELL_SIZE), pygame.K_DOWN: (0, CELL_SIZE),
                pygame.K_LEFT: (-CELL_SIZE, 0), pygame.K_RIGHT: (CELL_SIZE, 0),
                pygame.K_w: (0, -CELL_SIZE), pygame.K_s: (0, CELL_SIZE),
                pygame.K_a: (-CELL_SIZE, 0), pygame.K_d: (CELL_SIZE, 0)
            }
            self.snakes.append(Snake((WIDTH // 2, HEIGHT // 2), (CELL_SIZE, 0), snake_color, controls=controls))
        elif mode == 'pvp':
            self.snakes.append(Snake((WIDTH // 4, HEIGHT // 2), (CELL_SIZE, 0), snake_color, controls={pygame.K_w:(0,-CELL_SIZE),pygame.K_s:(0,CELL_SIZE),pygame.K_a:(-CELL_SIZE,0),pygame.K_d:(CELL_SIZE,0)}))
            self.snakes.append(Snake((3*WIDTH // 4, HEIGHT // 2), (-CELL_SIZE, 0), self.bot_color, controls={pygame.K_UP:(0,-CELL_SIZE),pygame.K_DOWN:(0,CELL_SIZE),pygame.K_LEFT:(-CELL_SIZE,0),pygame.K_RIGHT:(CELL_SIZE,0)}))
        elif mode == 'bot':
            controls = {
                pygame.K_UP: (0, -CELL_SIZE), pygame.K_DOWN: (0, CELL_SIZE),
                pygame.K_LEFT: (-CELL_SIZE, 0), pygame.K_RIGHT: (CELL_SIZE, 0),
                pygame.K_w: (0, -CELL_SIZE), pygame.K_s: (0, CELL_SIZE),
                pygame.K_a: (-CELL_SIZE, 0), pygame.K_d: (CELL_SIZE, 0)
            }
            self.snakes.append(Snake((WIDTH // 4, HEIGHT // 2), (CELL_SIZE, 0), snake_color, controls=controls))
            self.snakes.append(Snake((3*WIDTH // 4, HEIGHT // 2), (-CELL_SIZE, 0), self.bot_color, is_bot=True))
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
        # Определяем размеры поля по текущему окну
        # Размер поля всегда равен размеру окна
        field_width = self.screen.get_width()
        field_height = self.screen.get_height()
        # Серые стены убивают всегда
        walls_enabled = len(self.walls) > 0
        # wrap_around только если нет стен (границ)
        wrap_around = (self.walls_type == 'No walls')
        # Бот управляет собой
        for snake in self.snakes:
            if snake.is_bot and snake.alive:
                self.bot_move(snake)
        # Двигаем всех живых змей
        for snake in self.snakes:
            if snake.alive:
                # wrap_around только если walls_type == 'No walls'
                    snake.move(wrap_around=wrap_around, field_width=field_width, field_height=field_height)
        # Проверяем коллизии только для живых змей
        for snake in self.snakes:
            if not snake.alive:
                continue
            snake.check_collision(
                self.walls,
                [s for s in self.snakes if s.alive],
                walls_enabled=walls_enabled,
                field_width=field_width,
                field_height=field_height,
                wrap_around=wrap_around
            )
        # Проверяем сбор яблока только живыми змеями
        for snake in self.snakes:
            if not snake.alive:
                continue
            head = snake.get_head()
            head_grid = (head[0] // CELL_SIZE * CELL_SIZE, head[1] // CELL_SIZE * CELL_SIZE)
            food_grid = (self.food['pos'][0] // CELL_SIZE * CELL_SIZE, self.food['pos'][1] // CELL_SIZE * CELL_SIZE)
            if head_grid == food_grid:
                points = 3 if self.food['type'] == 'gold' else 1
                snake.score += points
                growth = 3 if self.food['type'] == 'gold' else 1
                snake.grow(growth)
                self.food = self.random_food()
        if not any(s.alive for s in self.snakes):
            self.game_over = True
        heads = [snake.get_head() for snake in self.snakes if snake.alive]
        for i, snake in enumerate(self.snakes):
            if not snake.alive:
                continue
            for j, other in enumerate(self.snakes):
                if i != j and other.alive and snake.get_head() == other.get_head():
                    snake.alive = False
                    other.alive = False
        if self.mode in ('single', 'bot', 'pvp'):
            if not self.snakes[0].alive or (len(self.snakes) > 1 and not self.snakes[1].alive):
                self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)
        # Кнопки увеличения/уменьшения размера окна (работают и в меню, и в игре)
        button_font = pygame.font.SysFont(None, 28)
        plus_rect = pygame.Rect(self.screen.get_width() - 90, 10, 35, 35)
        minus_rect = pygame.Rect(self.screen.get_width() - 50, 10, 35, 35)
        pygame.draw.rect(self.screen, GRAY, plus_rect)
        pygame.draw.rect(self.screen, GRAY, minus_rect)
        plus_text = button_font.render("+", True, BLACK)
        minus_text = button_font.render("-", True, BLACK)
        self.screen.blit(plus_text, plus_rect.move(10, 2))
        self.screen.blit(minus_text, minus_rect.move(10, 2))
        # Обработка кликов по кнопкам
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if plus_rect.collidepoint(event.pos):
                pygame.display.set_mode((self.screen.get_width() + 100, self.screen.get_height() + 100), pygame.RESIZABLE)
                self.handle_zoom()
            elif minus_rect.collidepoint(event.pos):
                pygame.display.set_mode((max(300, self.screen.get_width() - 100), max(300, self.screen.get_height() - 100)), pygame.RESIZABLE)
                self.handle_zoom()
        # Рисуем стены
        for wall in self.walls:
            pygame.draw.rect(self.screen, GRAY, (wall[0], wall[1], CELL_SIZE, CELL_SIZE))
        # Рисуем змей
        for snake in self.snakes:
            snake.draw(self.screen)
        # Рисуем еду
        fx = (self.food['pos'][0] // CELL_SIZE) * CELL_SIZE
        fy = (self.food['pos'][1] // CELL_SIZE) * CELL_SIZE
        food_color = GOLD if self.food['type'] == 'gold' else RED
        pygame.draw.rect(self.screen, food_color, (fx, fy, CELL_SIZE, CELL_SIZE))
        font = pygame.font.SysFont(None, 36)
        for i, snake in enumerate(self.snakes):
            text = font.render(f"P{i+1} Score: {snake.score}", True, snake.color)
            self.screen.blit(text, (10, 10 + i * 30))
        pygame.display.flip()

    def bot_move(self, snake):
        # Бот: идёт к еде, иногда пытается подрезать игрока
        head = snake.get_head()
        fx, fy = self.food['pos']
        player = self.snakes[0]
        px, py = player.get_head()
        options = [
            (CELL_SIZE, 0), (-CELL_SIZE, 0), (0, CELL_SIZE), (0, -CELL_SIZE)
        ]
        best = snake.direction
        min_dist = float('inf')
        # 20% шанс попытаться подрезать игрока
        import random
        if random.random() < 0.2:
            target = (px, py)
        else:
            target = (fx, fy)
        for d in options:
            nx, ny = head[0] + d[0], head[1] + d[1]
            pos = (nx, ny)
            if pos in self.walls:
                continue
            # Не врезаться в себя
            if pos in snake.body:
                continue
            dist = abs(target[0] - nx) + abs(target[1] - ny)
            if dist < min_dist:
                min_dist = dist
                best = d
        snake.direction = best
        # Удаляем отладочный print для бота
        # print(f"BOT DEBUG: alive={snake.alive}, score={snake.score}, head={snake.get_head()}, body={snake.body}")

    def show_game_over(self):
        # Определяем победителя и причину
        winner = None
        win_text = None
        win_color = WHITE
        scores = [snake.score for snake in self.snakes]
        # Для одиночного режима — если жив, то YOU WIN, если мертв — YOU LOSE
        if self.mode == "single":
            if self.snakes[0].alive:
                winner = 0
                win_text = "YOU WIN"
                win_color = self.snakes[0].color
            else:
                winner = None
                win_text = "YOU LOSE"
                win_color = RED
        elif self.mode == "bot":
            if self.snakes[0].alive and not self.snakes[1].alive:
                winner = 0
                win_text = "YOU WIN"
                win_color = self.snakes[0].color
            elif self.snakes[1].alive and not self.snakes[0].alive:
                winner = 1
                win_text = "YOU LOSE"
                win_color = self.snakes[1].color
            elif not self.snakes[0].alive and not self.snakes[1].alive:
                if self.snakes[0].score > self.snakes[1].score:
                    winner = 0
                    win_text = "YOU WIN"
                    win_color = self.snakes[0].color
                elif self.snakes[1].score > self.snakes[0].score:
                    winner = 1
                    win_text = "YOU LOSE"
                    win_color = self.snakes[1].color
                else:
                    winner = None
                    win_text = "DRAW"
                    win_color = WHITE
        elif self.mode == "pvp":
            if scores[0] > scores[1]:
                winner = 0
                win_text = "YOU WIN"
                win_color = self.snakes[0].color
            elif scores[1] > scores[0]:
                winner = 1
                win_text = "YOU WIN"
                win_color = self.snakes[1].color
            else:
                winner = None
                win_text = "DRAW"
                win_color = WHITE

        button_font = pygame.font.SysFont(None, 36)
        buttons = [
            {"text": "Restart", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50), "action": 'restart'},
            {"text": "Menu", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50), "action": 'menu'},
            {"text": "Quit", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50), "action": None}
        ]

        while True:
            self.screen.fill(BLACK)
            font = pygame.font.SysFont(None, 48)
            # Крупно и по центру — YOU WIN/LOSE/DRAW
            if win_text is not None:
                big_font = pygame.font.SysFont(None, 96)
                text = big_font.render(win_text, True, win_color)
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
                self.screen.blit(text, text_rect)
            # Выводим счет всех змей
            score_font = pygame.font.SysFont(None, 36)
            for i, snake in enumerate(self.snakes):
                score_text = score_font.render(f"P{i+1} Score: {snake.score}", True, snake.color)
                self.screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 - 40 + i * 30))
            # Для PvP — показать цвет победителя
            if self.mode == "pvp" and winner is not None:
                winner_text = score_font.render(f"Winner: Player {winner+1}", True, self.snakes[winner].color)
                self.screen.blit(winner_text, (WIDTH // 2 - 100, HEIGHT // 2 + 40 + len(self.snakes)*30))
            # Для бота — показать счет победителя/проигравшего
            if self.mode == "bot" and winner is not None:
                score_text = score_font.render(f"Winner: {self.snakes[winner].score}  Loser: {self.snakes[1-winner].score}", True, win_color)
                self.screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 + 100 + len(self.snakes)*30))

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
            # Ускорение змейки при удержании пробела
            speedup = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                speedup = True
            delay = self.move_delay // 2 if speedup else self.move_delay
            if current_time - self.last_move_time > delay:
                self.move()
                self.last_move_time = current_time
            self.draw()
            self.clock.tick(FPS)

        return self.show_game_over()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    menu = Menu(screen)
    # Сохраняем последний выбранный режим
    last_result = None
    while True:
        if last_result is None:
            result = menu.run()
            if result is None:
                break
            last_result = result
        mode = last_result['mode'].lower()
        walls = last_result['walls']
        delay = last_result['delay']
        color = last_result['color']
        while True:
            game = SnakeGame(delay, color, mode=mode, bot_color=BLUE, walls_type=walls)
            game.screen = screen
            game_result = game.run()
            if game_result == 'restart':
                continue  # Перезапуск игры с теми же параметрами
            elif game_result == 'menu':
                last_result = None  # Вернуться в меню выбора
                break
            else:
                return  # Выход из main

if __name__ == "__main__":
    main()
