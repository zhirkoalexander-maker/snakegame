def tetris(screen):
    COLS, ROWS = 10, 20
    BLOCK = 30
    TOPLEFT = (WIDTH // 2 - COLS * BLOCK // 2, HEIGHT // 2 - ROWS * BLOCK // 2)
    SHAPES = [
        [[1, 1, 1, 1]],  # I
        [[1, 1], [1, 1]],  # O
        [[0, 1, 0], [1, 1, 1]],  # T
        [[1, 0, 0], [1, 1, 1]],  # J
        [[0, 0, 1], [1, 1, 1]],  # L
        [[1, 1, 0], [0, 1, 1]],  # S
        [[0, 1, 1], [1, 1, 0]],  # Z
    ]
    COLORS = [CYAN := (0,255,255), YELLOW := (255,255,0), PURPLE := (128,0,128), BLUE, ORANGE := (255,140,0), GREEN, RED]

    def new_piece():
        idx = random.randint(0, len(SHAPES)-1)
        shape = SHAPES[idx]
        color = COLORS[idx]
        x = COLS // 2 - len(shape[0]) // 2
        y = 0
        return {'shape': shape, 'color': color, 'x': x, 'y': y}

    def rotate(shape):
        return [list(row) for row in zip(*shape[::-1])]

    def valid(piece, grid, dx=0, dy=0, rot=None):
        shape = piece['shape'] if rot is None else rot
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    nx, ny = piece['x'] + x + dx, piece['y'] + y + dy
                    if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
                        return False
                    if grid[ny][nx]:
                        return False
        return True

    def merge(piece, grid):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    grid[piece['y']+y][piece['x']+x] = piece['color']

    def clear_lines(grid):
        full_rows = [i for i, row in enumerate(grid) if all(cell != 0 for cell in row)]
        if not full_rows:
            return grid, 0
        # Blinking effect: blink the full rows 3 times
        for _ in range(3):
            for blink in [True, False]:
                for y in full_rows:
                    for x in range(COLS):
                        rect = pygame.Rect(TOPLEFT[0]+x*BLOCK, TOPLEFT[1]+y*BLOCK, BLOCK, BLOCK)
                        color = WHITE if blink else grid[y][x]
                        pygame.draw.rect(screen, color, rect)
                pygame.display.flip()
                pygame.time.delay(80)
        # Remove full rows
        new_grid = [row for i, row in enumerate(grid) if i not in full_rows]
        lines = len(full_rows)
        for _ in range(lines):
            new_grid.insert(0, [0]*COLS)
        return new_grid, lines

    grid = [[0]*COLS for _ in range(ROWS)]
    piece = new_piece()
    next_piece = new_piece()
    fall_time = 0
    fall_speed = 600  # замедляем падение фигуры
    score = 0
    running = True
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    game_over = False
    # Для автоудержания стрелок
    move_left = move_right = False
    move_delay = 0
    move_interval = 80  # мс между автошагами
    # Экран проигрыша
    def show_tetris_game_over():
        button_font = pygame.font.SysFont(None, 36)
        buttons = [
            {"text": "Restart", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50), "action": 'restart'},
            {"text": "Menu", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50), "action": 'menu'},
            {"text": "Quit", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50), "action": None}
        ]
        while True:
            screen.fill(BLACK)
            font_big = pygame.font.SysFont(None, 48)
            text = font_big.render("Game Over!", True, RED)
            screen.blit(text, (WIDTH // 2 - 120, HEIGHT // 2 - 60))
            for button in buttons:
                pygame.draw.rect(screen, GRAY, button["rect"])
                text_surf = button_font.render(button["text"], True, BLACK)
                text_rect = text_surf.get_rect(center=button["rect"].center)
                screen.blit(text_surf, text_rect)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in buttons:
                            if button["rect"].collidepoint(event.pos):
                                return button["action"]
            clock.tick(FPS)

    while running:
        dt = clock.tick(FPS)
        fall_time += dt
        if move_left or move_right:
            move_delay += dt
            if move_delay > move_interval:
                move_delay = 0
                if move_left and valid(piece, grid, dx=-1):
                    piece['x'] -= 1
                if move_right and valid(piece, grid, dx=1):
                    piece['x'] += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_LEFT:
                    move_left = True
                    move_delay = 0
                    if valid(piece, grid, dx=-1):
                        piece['x'] -= 1
                elif event.key == pygame.K_RIGHT:
                    move_right = True
                    move_delay = 0
                    if valid(piece, grid, dx=1):
                        piece['x'] += 1
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    rot = rotate(piece['shape'])
                    if valid(piece, grid, rot=rot):
                        piece['shape'] = rot
                elif event.key == pygame.K_SPACE:
                    while valid(piece, grid, dy=1):
                        piece['y'] += 1
                    fall_time = fall_speed
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    move_left = False
                elif event.key == pygame.K_RIGHT:
                    move_right = False
        if not game_over and fall_time > fall_speed:
            fall_time = 0
            if valid(piece, grid, dy=1):
                piece['y'] += 1
            else:
                merge(piece, grid)
                grid, lines = clear_lines(grid)
                score += lines * 100
                piece = next_piece
                next_piece = new_piece()
                if not valid(piece, grid):
                    game_over = True
        # Draw
        screen.fill(BLACK)
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(TOPLEFT[0]+x*BLOCK, TOPLEFT[1]+y*BLOCK, BLOCK, BLOCK)
                pygame.draw.rect(screen, GRAY, rect, 1)
                if grid[y][x]:
                    pygame.draw.rect(screen, grid[y][x], rect)
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(TOPLEFT[0]+(piece['x']+x)*BLOCK, TOPLEFT[1]+(piece['y']+y)*BLOCK, BLOCK, BLOCK)
                    pygame.draw.rect(screen, piece['color'], rect)
        for y, row in enumerate(next_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(WIDTH-150+x*BLOCK, 100+y*BLOCK, BLOCK, BLOCK)
                    pygame.draw.rect(screen, next_piece['color'], rect)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (WIDTH-180, 30))
        if game_over:
            result = show_tetris_game_over()
            if result == 'restart':
                return tetris(screen)
            elif result == 'menu':
                return
            elif result is None:
                return
        pygame.display.flip()
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
        self.level_types = ["With Walls", "No Walls"]
        self.games = ["Snake", "Tetris"]
        self.modes = ["Single", "1v1 Player", "1v1 Bot"]
        self.selected = 0
        self.step = 'game'  # 'game', 'mode', 'level', 'color', 'walls'
        self.selected_game = 0
        self.selected_mode = 0
        self.selected_level = 0
        self.selected_color = 0
        self.selected_level_type = 0

    def draw(self):
        self.screen.fill(BLACK)
        if self.step == 'game':
            title = self.font.render("Choose Game", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 120, HEIGHT // 2 - 120))
            for i, game in enumerate(self.games):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {game}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 70 + i * 40))
        elif self.step == 'mode':
            title = self.font.render("Game Mode", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 100, HEIGHT // 2 - 120))
            for i, mode in enumerate(self.modes):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {mode}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 70 + i * 40))
        elif self.step == 'level':
            title = self.font.render("Выберите уровень", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 120, HEIGHT // 2 - 120))
            for i, level in enumerate(self.levels):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {level['name']}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 70 + i * 40))
        elif self.step == 'color':
            title = self.font.render("Цвет змейки", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 100, HEIGHT // 2 - 120))
            for i, color_name in enumerate(self.color_names):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {color_name}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 70 + i * 40))
        elif self.step == 'walls':
            title = self.font.render("Level Type", True, WHITE)
            self.screen.blit(title, (WIDTH // 2 - 100, HEIGHT // 2 - 120))
            for i, t in enumerate(self.level_types):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {t}", True, color)
                self.screen.blit(text, (WIDTH // 2 - 80, HEIGHT // 2 - 70 + i * 40))
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if self.step == 'game':
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.games)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.games)
                    elif event.key == pygame.K_RETURN:
                        self.selected_game = self.selected
                        if self.games[self.selected_game] == "Snake":
                            self.step = 'mode'
                            self.selected = 0
                        else:
                            return {'game': 'Tetris'}
                        return 'next'
                elif self.step == 'mode':
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.modes)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.modes)
                    elif event.key == pygame.K_RETURN:
                        self.selected_mode = self.selected
                        self.step = 'level'
                        self.selected = 0
                        return 'next'
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
                        self.step = 'mode'
                        self.selected = self.selected_mode
                        return 'back'
                elif self.step == 'color':
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.colors)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.colors)
                    elif event.key == pygame.K_RETURN:
                        self.selected_color = self.selected
                        self.step = 'walls'
                        self.selected = 0
                        return 'next'
                    elif event.key == pygame.K_BACKSPACE:
                        self.step = 'level'
                        self.selected = self.selected_level
                        return 'back'
                elif self.step == 'walls':
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.level_types)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.level_types)
                    elif event.key == pygame.K_RETURN:
                        self.selected_level_type = self.selected
                        return {'delay': self.levels[self.selected_level]['delay'],
                                'color': self.colors[self.selected_color],
                                'walls': self.selected_level_type == 0,
                                'mode': self.modes[self.selected_mode]}
                    elif event.key == pygame.K_BACKSPACE:
                        self.step = 'color'
                        self.selected = self.selected_color
                        return 'back'
        return -1

    def run(self):
        self.step = 'game'
        self.selected = 0
        self.selected_game = 0
        self.selected_mode = 0
        self.selected_level = 0
        self.selected_color = 0
        self.selected_level_type = 0
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
                if result.get('game') == 'Tetris':
                    return 'Tetris',
                return result['delay'], result['color'], result['walls'], result['mode']

class SnakeGame:
    def __init__(self, move_delay, snake_color, with_walls=True, mode="Single"):
        self.move_delay = move_delay
        self.snake_color = snake_color
        self.with_walls = with_walls
        self.mode = mode
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        # Первая змея (игрок 1)
        self.snake = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = (CELL_SIZE, 0)  # Вправо
        self.score = 0
        self.game_over = False
        self.last_move_time = 0

        # Вторая змея (игрок 2 или бот)
        if self.mode in ("1v1 Player", "1v1 Bot"):
            self.snake2 = [(WIDTH // 2, HEIGHT // 2 - 3 * CELL_SIZE)]
            self.direction2 = (0, CELL_SIZE)  # Вниз
            self.score2 = 0
            self.snake2_color = BLUE
            self.game_over2 = False
        else:
            self.snake2 = None
            self.direction2 = None
            self.score2 = 0
            self.snake2_color = BLUE
            self.game_over2 = False

        # Генерируем случайные стенки в зависимости от сложности
        self.walls = []
        if self.with_walls:
            if move_delay >= 200:
                wall_count = 10  # Easy
                wall_length = 3
            elif move_delay >= 100:
                wall_count = 18  # Medium
                wall_length = 5
            else:
                wall_count = 28  # Hard
                wall_length = 7
            for x in range(0, WIDTH, CELL_SIZE):
                self.walls.append((x, 0))
                self.walls.append((x, HEIGHT - CELL_SIZE))
            for y in range(CELL_SIZE, HEIGHT - CELL_SIZE, CELL_SIZE):
                self.walls.append((0, y))
                self.walls.append((WIDTH - CELL_SIZE, y))
            for _ in range(wall_count):
                orientation = random.choice(['h', 'v'])
                if orientation == 'h':
                    x = random.randint(1, (WIDTH // CELL_SIZE) - wall_length - 1) * CELL_SIZE
                    y = random.randint(1, (HEIGHT // CELL_SIZE) - 2) * CELL_SIZE
                    for l in range(wall_length):
                        self.walls.append((x + l * CELL_SIZE, y))
                else:
                    x = random.randint(1, (WIDTH // CELL_SIZE) - 2) * CELL_SIZE
                    y = random.randint(1, (HEIGHT // CELL_SIZE) - wall_length - 1) * CELL_SIZE
                    for l in range(wall_length):
                        self.walls.append((x, y + l * CELL_SIZE))
        self.food = self.random_food()

    def random_food(self):
        # Генерируем позицию, не совпадающую со стеной и телом змей
        possible = []
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                pos = (x, y)
                if pos in self.walls:
                    continue
                if pos in self.snake:
                    continue
                if self.snake2 is not None and pos in self.snake2:
                    continue
                possible.append(pos)
        if not possible:
            # Нет места для еды
            return {'pos': (-CELL_SIZE, -CELL_SIZE), 'type': 'normal'}
        pos = random.choice(possible)
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
                if self.snake2 is not None:
                    self.game_over2 = True
            elif event.type == pygame.KEYDOWN:
                # Управление первой змеёй (стрелки)
                if event.key == pygame.K_UP and self.direction != (0, CELL_SIZE):
                    self.direction = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and self.direction != (0, -CELL_SIZE):
                    self.direction = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and self.direction != (CELL_SIZE, 0):
                    self.direction = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-CELL_SIZE, 0):
                    self.direction = (CELL_SIZE, 0)
                # Управление второй змеёй (WASD)
                if self.snake2 is not None and self.mode == "1v1 Player":
                    if event.key == pygame.K_w and self.direction2 != (0, CELL_SIZE):
                        self.direction2 = (0, -CELL_SIZE)
                    elif event.key == pygame.K_s and self.direction2 != (0, -CELL_SIZE):
                        self.direction2 = (0, CELL_SIZE)
                    elif event.key == pygame.K_a and self.direction2 != (CELL_SIZE, 0):
                        self.direction2 = (-CELL_SIZE, 0)
                    elif event.key == pygame.K_d and self.direction2 != (-CELL_SIZE, 0):
                        self.direction2 = (CELL_SIZE, 0)

    def move(self):
        # Первая змея
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Вторая змея
        if self.snake2 is not None:
            head2_x, head2_y = self.snake2[0]
            dx2, dy2 = self.direction2
            # Бот: простейшая логика (движение к еде)
            if self.mode == "1v1 Bot":
                fx, fy = self.food['pos']
                # Двигаемся к еде, избегая стен и змей
                options = [
                    (CELL_SIZE, 0), (-CELL_SIZE, 0), (0, CELL_SIZE), (0, -CELL_SIZE)
                ]
                random.shuffle(options)
                best = self.direction2
                min_dist = abs(head2_x - fx) + abs(head2_y - fy)
                for dxx, dyy in options:
                    nx, ny = head2_x + dxx, head2_y + dyy
                    if (nx, ny) in self.walls or (nx, ny) in self.snake or (nx, ny) in self.snake2:
                        continue
                    dist = abs(nx - fx) + abs(ny - fy)
                    if dist < min_dist:
                        min_dist = dist
                        best = (dxx, dyy)
                self.direction2 = best
            new_head2 = (head2_x + self.direction2[0], head2_y + self.direction2[1])
        # Проверяем столкновения первой змеи
        if (self.with_walls and new_head in self.walls) or (new_head in self.snake):
            self.game_over = True
            return
        if self.snake2 is not None and (new_head in self.snake2):
            self.game_over = True
            return
        # Проверяем столкновения второй змеи
        if self.snake2 is not None:
            if (self.with_walls and new_head2 in self.walls) or (new_head2 in self.snake2):
                self.game_over2 = True
                return
            if new_head2 in self.snake:
                self.game_over2 = True
                return
        # Телепорт для обеих змей
        if not self.with_walls:
            new_head = (new_head[0] % WIDTH, new_head[1] % HEIGHT)
            if self.snake2 is not None:
                new_head2 = (new_head2[0] % WIDTH, new_head2[1] % HEIGHT)
        # Движение первой змеи
        self.snake.insert(0, new_head)
        ate = False
        if new_head == self.food['pos']:
            ate = True
            if self.food['type'] == 'gold':
                self.score += 3
                for _ in range(3):
                    self.add_segment()
            else:
                self.score += 1
                self.add_segment()
            self.food = self.random_food()
        else:
            self.snake.pop()
        # Движение второй змеи
        if self.snake2 is not None and not self.game_over2:
            self.snake2.insert(0, new_head2)
            if new_head2 == self.food['pos'] and not ate:
                if self.food['type'] == 'gold':
                    self.score2 += 3
                    for _ in range(3):
                        self.snake2.append(self.snake2[-1])
                else:
                    self.score2 += 1
                    self.snake2.append(self.snake2[-1])
                self.food = self.random_food()
            else:
                self.snake2.pop()

    def draw(self):
        self.screen.fill(BLACK)
        # Рисуем стенки
        if self.with_walls:
            for wall in self.walls:
                pygame.draw.rect(self.screen, GRAY, (wall[0], wall[1], CELL_SIZE, CELL_SIZE))
        # Рисуем первую змею
        for segment in self.snake:
            pygame.draw.rect(self.screen, self.snake_color, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        # Рисуем вторую змею
        if self.snake2 is not None:
            for segment in self.snake2:
                pygame.draw.rect(self.screen, self.snake2_color, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        # Рисуем еду
        food_color = GOLD if self.food['type'] == 'gold' else RED
        pygame.draw.rect(self.screen, food_color, (self.food['pos'][0], self.food['pos'][1], CELL_SIZE, CELL_SIZE))
        # Рисуем счет
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 10))
        if self.snake2 is not None:
            text2 = font.render(f"Score2: {self.score2}", True, BLUE)
            self.screen.blit(text2, (WIDTH - 150, 10))
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
        # Для 1v1: если кто-то проиграл, другой выигрывает
        while True:
            current_time = pygame.time.get_ticks()
            self.handle_events()

            if current_time - self.last_move_time > self.move_delay:
                self.move()
                self.last_move_time = current_time

            self.draw()
            self.clock.tick(FPS)

            # Single mode: обычное завершение
            if self.mode == "Single" and self.game_over:
                return self.show_game_over()
            # 1v1 режим: если кто-то проиграл
            if self.mode in ("1v1 Player", "1v1 Bot"):
                if self.game_over:
                    return self.show_game_over(winner=2)
                if self.game_over2:
                    return self.show_game_over(winner=1)

    def show_game_over(self, winner=None):
        button_font = pygame.font.SysFont(None, 36)
        buttons = [
            {"text": "Restart", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50), "action": 'restart'},
            {"text": "Menu", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50), "action": 'menu'},
            {"text": "Quit", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50), "action": None}
        ]

        while True:
            self.screen.fill(BLACK)
            font = pygame.font.SysFont(None, 48)
            if winner == 1:
                text = font.render("You win! (Player 1)", True, GREEN)
            elif winner == 2:
                text = font.render("You win! (Player 2)", True, BLUE)
            else:
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    menu = Menu(screen)
    while True:
        result = menu.run()
        if result is None:
            break
        if result[0] == 'Tetris':
            tetris(screen)
            continue
        delay, color, with_walls, mode = result
        while True:
            game = SnakeGame(delay, color, with_walls, mode)
            game.screen = screen
            game_result = game.run()
            if game_result == 'restart':
                continue  # Начать игру заново сразу
            elif game_result == 'menu':
                break  # Вернуться в меню
            else:
                return  # Выход


if __name__ == "__main__":
    main()