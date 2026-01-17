class Snake:
    def __init__(self, start_pos, direction, color, controls=None, is_bot=False):
        self.body = [start_pos]
        self.direction = direction
        self.next_direction = direction  # Буфер для следующего направления
        self.direction_changed = False  # Флаг для предотвращения множественных изменений
        self.color = color
        self.controls = controls or {}
        self.is_bot = is_bot
        self.grow_pending = 0
        self.alive = True
        self.score = 0

    def get_head(self):
        return self.body[0]

    def set_direction(self, key):
        if key in self.controls and not self.direction_changed:
            new_dir = self.controls[key]
            # Запретить разворот назад (проверяем против текущего direction)
            if (new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]):
                self.next_direction = new_dir
                self.direction_changed = True

    def move(self, wrap_around=False, field_width=None, field_height=None):
        if field_width is None:
            field_width = 600  # WIDTH
        if field_height is None:
            field_height = 600  # HEIGHT
        # Применяем буферизованное направление
        self.direction = self.next_direction
        self.direction_changed = False  # Сбрасываем флаг после применения
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
        # Нормализуем координаты головы к сетке
        head_grid = ((head[0] // CELL_SIZE) * CELL_SIZE, (head[1] // CELL_SIZE) * CELL_SIZE)
        # Серые стены убивают только если walls_enabled=True
        if walls_enabled and head_grid in walls:
            self.alive = False
            return
        # Границы убивают только если wrap_around == False
        if not wrap_around:
            if field_width is None:
                field_width = 600
            if field_height is None:
                field_height = 600
            if head[0] < 0 or head[0] >= field_width or head[1] < 0 or head[1] >= field_height:
                self.alive = False
                return
        # Проверка столкновения с собой
        if head in self.body[1:]:
            self.alive = False
            return
        # Проверка столкновения с другими змеями
        for snake in snakes:
            if snake is not self:
                if head == snake.get_head():
                    self.alive = False
                    return
                elif head in snake.body[1:]:
                    self.alive = False
                    return

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            # Рисуем строго по сетке
            x = (segment[0] // CELL_SIZE) * CELL_SIZE
            y = (segment[1] // CELL_SIZE) * CELL_SIZE
            
            # Сужение к концу хвоста
            body_length = len(self.body)
            scale_factor = 1.0 - (i / body_length) * 0.5  # От 1.0 до 0.5
            segment_size = int(CELL_SIZE * scale_factor)
            offset = (CELL_SIZE - segment_size) // 2
            
            # Основной цвет с затемнением для тела
            if i == 0:
                # Голова - ярче
                color = self.color
                # Рисуем обводку
                pygame.draw.rect(screen, (0, 0, 0), (x, y, CELL_SIZE, CELL_SIZE), 2)
                # Основной прямоугольник
                pygame.draw.rect(screen, color, (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
                # Блик
                highlight_color = tuple(min(255, c + 60) for c in color)
                pygame.draw.rect(screen, highlight_color, (x + 4, y + 4, CELL_SIZE // 3, CELL_SIZE // 3))
                # Глаза
                eye_color = (255, 255, 255)
                pygame.draw.circle(screen, eye_color, (x + 6, y + 8), 3)
                pygame.draw.circle(screen, eye_color, (x + CELL_SIZE - 6, y + 8), 3)
                pygame.draw.circle(screen, (0, 0, 0), (x + 6, y + 8), 1)
                pygame.draw.circle(screen, (0, 0, 0), (x + CELL_SIZE - 6, y + 8), 1)
            else:
                # Тело - темнее и сужается
                color = tuple(max(0, c - 30) for c in self.color)
                # Обводка
                pygame.draw.rect(screen, (0, 0, 0), (x + offset, y + offset, segment_size, segment_size), 1)
                # Основной прямоугольник со скругленными углами
                pygame.draw.rect(screen, color, (x + offset + 1, y + offset + 1, segment_size - 2, segment_size - 2), border_radius=4)
                # Небольшой блик (только если сегмент достаточно большой)
                if segment_size > 10:
                    highlight_color = tuple(min(255, c + 30) for c in color)
                    highlight_size = max(2, segment_size // 4)
                    pygame.draw.rect(screen, highlight_color, (x + offset + 3, y + offset + 3, highlight_size, highlight_size), border_radius=2)

import pygame
import random
import os
import asyncio
import sys
import json
from pathlib import Path

# Проверяем, запущено ли в браузере
RUNNING_IN_BROWSER = sys.platform == "emscripten"

# Настройки игры
WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20
FPS = 60
FOOD_TYPES = ['normal', 'gold', 'poison']

# Цвета
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)
PURPLE = (153, 0, 255)

# Темы
THEMES = {
    'classic': {'bg': BLACK, 'grid': (20, 20, 20)},
    'forest': {'bg': (13, 38, 13), 'grid': (26, 58, 26)},
    'ocean': {'bg': (0, 26, 51), 'grid': (0, 51, 102)},
    'neon': {'bg': (10, 10, 26), 'grid': (26, 0, 51)},
    'sunset': {'bg': (51, 25, 0), 'grid': (76, 38, 0)}
}

# Настройки
SETTINGS_FILE = Path.home() / '.snake_game_settings.json'
LEADERBOARD_FILE = Path.home() / '.snake_game_leaderboard.json'

def load_settings():
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {'theme': 'classic', 'sound': True}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except:
        pass

def load_leaderboard():
    try:
        if LEADERBOARD_FILE.exists():
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_leaderboard(leaderboard):
    try:
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(leaderboard, f)
    except:
        pass

def add_score_to_leaderboard(score, mode):
    leaderboard = load_leaderboard()
    from datetime import datetime
    leaderboard.append({
        'score': score,
        'mode': mode,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    save_leaderboard(leaderboard[:10])

# Звуковые эффекты
def play_sound(sound_type):
    settings = load_settings()
    if not settings.get('sound', True):
        return
    try:
        # Определяем параметры звука по типу
        sound_params = {
            'eat': (440, 0.1),
            'golden': (880, 0.15),
            'poison': (220, 0.2),
            'death': (110, 0.3)
        }
        freq, duration = sound_params.get(sound_type, (440, 0.1))
        
        # Создаем простой звук
        sample_rate = 22050
        samples = int(sample_rate * duration)
        arr = []
        for i in range(samples):
            val = int(32767 * 0.3 * (1 if (i * freq * 2 / sample_rate) % 1 < 0.5 else -1))
            arr.append([val, val])
        sound = pygame.sndarray.make_sound(arr)
        sound.play()
    except:
        pass  # Звук не обязателен

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
        self.walls_types = ["With walls", "No walls", "Teleport"]
        self.selected = 0
        self.step = 'start'  # 'start', 'mode', 'walls', 'level', 'color', 'controls', 'settings', 'leaderboard'
        self.selected_mode = 0
        self.selected_walls = 0
        self.selected_level = 0
        self.settings = load_settings()
        self.current_theme = self.settings.get('theme', 'classic')
        # Фоновая игра для меню
        self.background_game = None
        self.bg_last_move = 0
        # Настройки управления
        self.default_controls_p1 = {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'speedup': pygame.K_RSHIFT
        }
        self.default_controls_p2 = {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'speedup': pygame.K_LSHIFT
        }
        self.controls_p1 = self.default_controls_p1.copy()
        self.controls_p2 = self.default_controls_p2.copy()
        self.waiting_for_key = None  # ('p1', 'up'), ('p2', 'down'), etc.
        self.fullscreen = False

    def draw(self):
        # Получаем текущий размер окна
        screen_rect = self.screen.get_rect()
        center_x = screen_rect.centerx
        center_y = screen_rect.centery
        self.screen.fill(BLACK)
        
        # Отрисовываем фоновую игру
        if self.background_game is None or not any(s.alive for s in self.background_game.snakes):
            # Создаём новую фоновую игру с одним ботом
            bg_game = SnakeGame(100, GREEN, mode='single', walls_type='No walls', theme='classic', settings=self.settings)
            bg_game.screen = self.screen
            # Делаем змею ботом
            bg_game.snakes[0].is_bot = True
            bg_game.snakes[0].controls = {}
            self.background_game = bg_game
            self.bg_last_move = pygame.time.get_ticks()
        
        # Обновляем фоновую игру
        current_time = pygame.time.get_ticks()
        if current_time - self.bg_last_move > 100:
            self.background_game.move()
            self.bg_last_move = current_time
        
        # Рисуем только змей и еду без UI (без score)
        for snake in self.background_game.snakes:
            if snake.alive:
                snake.draw(self.screen)
        
        # Рисуем еду
        fx, fy = self.background_game.food['pos']
        if self.background_game.food['type'] == 'gold':
            food_color = GOLD
            darker_gold = (200, 170, 0)
        else:
            food_color = RED
            darker_gold = (180, 0, 0)
        
        shadow_color = (50, 50, 50)
        pygame.draw.circle(self.screen, shadow_color, (fx + CELL_SIZE // 2 + 2, fy + CELL_SIZE - 3), CELL_SIZE // 3)
        pygame.draw.circle(self.screen, darker_gold, (fx + CELL_SIZE // 2 + 1, fy + CELL_SIZE // 2 + 1), CELL_SIZE // 2 - 2)
        pygame.draw.circle(self.screen, food_color, (fx + CELL_SIZE // 2, fy + CELL_SIZE // 2), CELL_SIZE // 2 - 2)
        pygame.draw.circle(self.screen, (0, 0, 0), (fx + CELL_SIZE // 2, fy + CELL_SIZE // 2), CELL_SIZE // 2 - 2, 2)
        highlight_color = (255, 255, 255)
        pygame.draw.circle(self.screen, highlight_color, (fx + CELL_SIZE // 2 - 3, fy + CELL_SIZE // 2 - 4), 4)
        leaf_color = (0, 150, 0)
        leaf_points = [
            (fx + CELL_SIZE // 2, fy + 3),
            (fx + CELL_SIZE // 2 + 5, fy),
            (fx + CELL_SIZE // 2 + 3, fy + 6)
        ]
        pygame.draw.polygon(self.screen, leaf_color, leaf_points)
        
        # Затемняем фон
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Сохраняем прямоугольники для кликабельных элементов
        self.clickable_rects = []
        if self.step == 'start':
            # Начальный экран
            # Рисуем декоративную змею над заголовком
            snake_y = center_y - 150
            snake_segments = [
                (center_x - 120, snake_y),
                (center_x - 90, snake_y),
                (center_x - 60, snake_y - 20),
                (center_x - 30, snake_y - 30),
                (center_x, snake_y - 20),
                (center_x + 30, snake_y - 30),
                (center_x + 60, snake_y - 20),
                (center_x + 90, snake_y),
                (center_x + 120, snake_y)
            ]
            
            # Рисуем тело змеи с градиентом
            for i, pos in enumerate(snake_segments):
                size = 28 - i * 2
                color_val = 255 - i * 20
                segment_color = (0, max(100, color_val), 0)
                pygame.draw.circle(self.screen, (0, 0, 0), pos, size // 2 + 2)  # Обводка
                pygame.draw.circle(self.screen, segment_color, pos, size // 2)
                # Блик
                pygame.draw.circle(self.screen, (150, 255, 150), (pos[0] - 3, pos[1] - 3), size // 6)
            
            # Голова змеи
            head_pos = snake_segments[0]
            pygame.draw.circle(self.screen, (0, 0, 0), head_pos, 16)
            pygame.draw.circle(self.screen, GREEN, head_pos, 14)
            # Глаза
            pygame.draw.circle(self.screen, (255, 255, 255), (head_pos[0] - 5, head_pos[1] - 3), 4)
            pygame.draw.circle(self.screen, (255, 255, 255), (head_pos[0] + 5, head_pos[1] - 3), 4)
            pygame.draw.circle(self.screen, (0, 0, 0), (head_pos[0] - 5, head_pos[1] - 3), 2)
            pygame.draw.circle(self.screen, (0, 0, 0), (head_pos[0] + 5, head_pos[1] - 3), 2)
            # Язык
            tongue_points = [
                (head_pos[0] - 15, head_pos[1] + 5),
                (head_pos[0] - 20, head_pos[1] + 3),
                (head_pos[0] - 18, head_pos[1] + 5),
                (head_pos[0] - 22, head_pos[1] + 7)
            ]
            pygame.draw.lines(self.screen, RED, False, tongue_points, 2)
            
            # Заголовок с эффектом тени
            title_font = pygame.font.SysFont(None, 72)
            # Тень
            title_shadow = title_font.render("SUPER SNAKE GAME", True, (0, 100, 0))
            shadow_rect = title_shadow.get_rect(center=(center_x + 3, center_y - 77))
            self.screen.blit(title_shadow, shadow_rect)
            # Основной текст
            title = title_font.render("SUPER SNAKE GAME", True, GREEN)
            title_rect = title.get_rect(center=(center_x, center_y - 80))
            self.screen.blit(title, title_rect)
            
            # Декоративные яблоки в углах
            apple_positions = [
                (center_x - 250, center_y - 200),
                (center_x + 250, center_y - 200),
                (center_x - 250, center_y + 150),
                (center_x + 250, center_y + 150)
            ]
            for apple_pos in apple_positions:
                # Тень
                pygame.draw.circle(self.screen, (50, 0, 0), (apple_pos[0] + 2, apple_pos[1] + 2), 12)
                # Яблоко
                pygame.draw.circle(self.screen, (180, 0, 0), (apple_pos[0], apple_pos[1]), 12)
                pygame.draw.circle(self.screen, RED, (apple_pos[0], apple_pos[1]), 10)
                # Блик
                pygame.draw.circle(self.screen, (255, 200, 200), (apple_pos[0] - 3, apple_pos[1] - 3), 3)
                # Листик
                leaf = [
                    (apple_pos[0], apple_pos[1] - 10),
                    (apple_pos[0] + 4, apple_pos[1] - 12),
                    (apple_pos[0] + 2, apple_pos[1] - 8)
                ]
                pygame.draw.polygon(self.screen, (0, 150, 0), leaf)
            
            # Кнопка Start
            start_button = pygame.Rect(center_x - 100, center_y + 20, 200, 60)
            pygame.draw.rect(self.screen, GREEN, start_button)
            start_text = self.font.render("Start", True, BLACK)
            start_text_rect = start_text.get_rect(center=start_button.center)
            self.screen.blit(start_text, start_text_rect)
            self.clickable_rects.append(('start', start_button))
            
            # Кнопка Exit
            exit_button = pygame.Rect(center_x - 100, center_y + 90, 200, 50)
            pygame.draw.rect(self.screen, RED, exit_button)
            exit_text = self.small_font.render("Exit", True, BLACK)
            exit_text_rect = exit_text.get_rect(center=exit_button.center)
            self.screen.blit(exit_text, exit_text_rect)
            self.clickable_rects.append(('exit', exit_button))
            
            # Кнопка Settings
            settings_button = pygame.Rect(center_x - 230, center_y + 155, 100, 40)
            pygame.draw.rect(self.screen, GRAY, settings_button)
            settings_txt = self.small_font.render("⚙️", True, WHITE)
            self.screen.blit(settings_txt, settings_txt.get_rect(center=settings_button.center))
            self.clickable_rects.append(('settings', settings_button))
            
            # Кнопка Leaderboard
            leader_button = pygame.Rect(center_x + 130, center_y + 155, 100, 40)
            pygame.draw.rect(self.screen, GOLD, leader_button)
            leader_txt = self.small_font.render("🏆", True, BLACK)
            self.screen.blit(leader_txt, leader_txt.get_rect(center=leader_button.center))
            self.clickable_rects.append(('leaderboard', leader_button))
            
            # Подзаголовок
            subtitle_font = pygame.font.SysFont(None, 28)
            subtitle = subtitle_font.render("Press ENTER to start", True, WHITE)
            subtitle_rect = subtitle.get_rect(center=(center_x, center_y + 210))
            self.screen.blit(subtitle, subtitle_rect)
            
            # Кнопка настроек
            settings_text = subtitle_font.render("Press C to configure controls", True, GRAY)
            settings_rect = settings_text.get_rect(center=(center_x, center_y + 185))
            self.screen.blit(settings_text, settings_rect)
        elif self.step == 'mode':
            title = self.font.render("Choose Game Mode", True, WHITE)
            self.screen.blit(title, (center_x - 170, center_y - 100))
            for i, mode in enumerate(self.modes):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {mode}", True, color)
                text_rect = pygame.Rect(center_x - 100, center_y - 50 + i * 40, 200, 35)
                self.screen.blit(text, (center_x - 80, center_y - 50 + i * 40))
                self.clickable_rects.append(('mode', i, text_rect))
        elif self.step == 'walls':
            title = self.font.render("Choose Walls", True, WHITE)
            self.screen.blit(title, (center_x - 120, center_y - 100))
            for i, wtype in enumerate(self.walls_types):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {wtype}", True, color)
                text_rect = pygame.Rect(center_x - 100, center_y - 50 + i * 40, 200, 35)
                self.screen.blit(text, (center_x - 80, center_y - 50 + i * 40))
                self.clickable_rects.append(('walls', i, text_rect))
        elif self.step == 'level':
            title = self.font.render("Choose Level", True, WHITE)
            self.screen.blit(title, (center_x - 120, center_y - 100))
            for i, level in enumerate(self.levels):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {level['name']}", True, color)
                text_rect = pygame.Rect(center_x - 100, center_y - 50 + i * 40, 200, 35)
                self.screen.blit(text, (center_x - 80, center_y - 50 + i * 40))
                self.clickable_rects.append(('level', i, text_rect))
        elif self.step == 'color':
            title = self.font.render("Choose Snake Color", True, WHITE)
            self.screen.blit(title, (center_x - 150, center_y - 100))
            for i, color_name in enumerate(self.color_names):
                color = GREEN if i == self.selected else WHITE
                text = self.small_font.render(f"{i+1}. {color_name}", True, color)
                text_rect = pygame.Rect(center_x - 100, center_y - 50 + i * 40, 200, 35)
                self.screen.blit(text, (center_x - 80, center_y - 50 + i * 40))
                self.clickable_rects.append(('color', i, text_rect))
        elif self.step == 'controls':
            title = self.font.render("Configure Controls", True, WHITE)
            title_rect = title.get_rect(center=(center_x, center_y - 200))
            self.screen.blit(title, title_rect)
            
            # Player 1 controls
            p1_title = self.small_font.render("Player 1:", True, GREEN)
            self.screen.blit(p1_title, (center_x - 250, center_y - 140))
            
            directions = [('up', 'Up'), ('down', 'Down'), ('left', 'Left'), ('right', 'Right'), ('speedup', 'Speedup')]
            for idx, (dir_key, dir_name) in enumerate(directions):
                key_name = pygame.key.name(self.controls_p1[dir_key])
                color = RED if self.waiting_for_key == ('p1', dir_key) else WHITE
                text = self.small_font.render(f"{dir_name}: {key_name}", True, color)
                button_rect = pygame.Rect(center_x - 250, center_y - 100 + idx * 35, 200, 30)
                pygame.draw.rect(self.screen, GRAY, button_rect, 2)
                self.screen.blit(text, (center_x - 240, center_y - 95 + idx * 35))
                self.clickable_rects.append(('control', 'p1', dir_key, button_rect))
            
            # Player 2 controls
            p2_title = self.small_font.render("Player 2:", True, BLUE)
            self.screen.blit(p2_title, (center_x + 50, center_y - 140))
            
            for idx, (dir_key, dir_name) in enumerate(directions):
                key_name = pygame.key.name(self.controls_p2[dir_key])
                color = RED if self.waiting_for_key == ('p2', dir_key) else WHITE
                text = self.small_font.render(f"{dir_name}: {key_name}", True, color)
                button_rect = pygame.Rect(center_x + 50, center_y - 100 + idx * 35, 200, 30)
                pygame.draw.rect(self.screen, GRAY, button_rect, 2)
                self.screen.blit(text, (center_x + 60, center_y - 95 + idx * 35))
                self.clickable_rects.append(('control', 'p2', dir_key, button_rect))
            
            # Инструкции
            inst_font = pygame.font.SysFont(None, 28)
            if self.waiting_for_key:
                inst_text = inst_font.render("Press any key to assign...", True, GOLD)
            else:
                inst_text = inst_font.render("Click on a control to change it", True, WHITE)
            inst_rect = inst_text.get_rect(center=(center_x, center_y + 90))
            self.screen.blit(inst_text, inst_rect)
            
            reset_text = inst_font.render("Press R to reset to defaults", True, GRAY)
            reset_rect = reset_text.get_rect(center=(center_x, center_y + 120))
            self.screen.blit(reset_text, reset_rect)
            
            back_text = inst_font.render("Press ESC or BACKSPACE to go back", True, GRAY)
            back_rect = back_text.get_rect(center=(center_x, center_y + 150))
            self.screen.blit(back_text, back_rect)
        elif self.step == 'settings':
            title = self.font.render("Settings", True, WHITE)
            title_rect = title.get_rect(center=(center_x, center_y - 200))
            self.screen.blit(title, title_rect)
            
            # Theme selection
            theme_text = self.small_font.render("Theme:", True, WHITE)
            self.screen.blit(theme_text, (center_x - 250, center_y - 140))
            
            for i, theme_name in enumerate(THEMES.keys()):
                color = GREEN if self.current_theme == theme_name else WHITE
                text = self.small_font.render(f"{i+1}. {theme_name.title()}", True, color)
                button_rect = pygame.Rect(center_x - 250, center_y - 100 + i * 35, 200, 30)
                pygame.draw.rect(self.screen, GRAY, button_rect, 2)
                self.screen.blit(text, (center_x - 240, center_y - 95 + i * 35))
                self.clickable_rects.append(('theme', theme_name, button_rect))
            
            # Sound toggle
            sound_status = "ON" if self.settings['sound'] else "OFF"
            sound_color = GREEN if self.settings['sound'] else RED
            sound_text = self.small_font.render(f"Sound: {sound_status}", True, sound_color)
            sound_button = pygame.Rect(center_x + 50, center_y - 100, 200, 40)
            pygame.draw.rect(self.screen, GRAY, sound_button, 2)
            self.screen.blit(sound_text, (center_x + 60, center_y - 90))
            self.clickable_rects.append(('sound_toggle', sound_button))
            
            # Back button
            back_button = pygame.Rect(center_x - 100, center_y + 150, 200, 50)
            pygame.draw.rect(self.screen, GRAY, back_button)
            back_text = self.small_font.render("Back", True, WHITE)
            self.screen.blit(back_text, back_text.get_rect(center=back_button.center))
            self.clickable_rects.append(('back_to_menu', back_button))
            
        elif self.step == 'leaderboard':
            title = self.font.render("Leaderboard", True, GOLD)
            title_rect = title.get_rect(center=(center_x, center_y - 200))
            self.screen.blit(title, title_rect)
            
            leaderboard = load_leaderboard()
            if leaderboard:
                for i, entry in enumerate(leaderboard[:10]):
                    rank_color = GOLD if i == 0 else (GRAY if i < 3 else WHITE)
                    text = self.small_font.render(
                        f"{i+1}. {entry['name']}: {entry['score']}", 
                        True, 
                        rank_color
                    )
                    self.screen.blit(text, (center_x - 150, center_y - 150 + i * 30))
            else:
                no_scores = self.small_font.render("No scores yet!", True, GRAY)
                self.screen.blit(no_scores, no_scores.get_rect(center=(center_x, center_y)))
            
            # Clear button
            clear_button = pygame.Rect(center_x - 220, center_y + 150, 120, 40)
            pygame.draw.rect(self.screen, RED, clear_button)
            clear_text = self.small_font.render("Clear", True, WHITE)
            self.screen.blit(clear_text, clear_text.get_rect(center=clear_button.center))
            self.clickable_rects.append(('clear_leaderboard', clear_button))
            
            # Back button
            back_button = pygame.Rect(center_x + 100, center_y + 150, 120, 40)
            pygame.draw.rect(self.screen, GRAY, back_button)
            back_text = self.small_font.render("Back", True, WHITE)
            self.screen.blit(back_text, back_text.get_rect(center=back_button.center))
            self.clickable_rects.append(('back_to_menu', back_button))
            
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Обработка кликов по всем кликабельным элементам
                for item in self.clickable_rects:
                    if item[0] == 'start':
                        if item[1].collidepoint(event.pos):
                            self.step = 'mode'
                            self.selected = 0
                            return 'next'
                    elif item[0] == 'exit':
                        if item[1].collidepoint(event.pos):
                            return None
                    elif item[0] == 'settings':
                        if item[1].collidepoint(event.pos):
                            self.step = 'settings'
                            return 'next'
                    elif item[0] == 'leaderboard':
                        if item[1].collidepoint(event.pos):
                            self.step = 'leaderboard'
                            return 'next'
                    elif item[0] == 'theme':
                        if item[2].collidepoint(event.pos):
                            self.current_theme = item[1]
                            self.settings['theme'] = item[1]
                            save_settings(self.settings)
                            return 'next'
                    elif item[0] == 'sound_toggle':
                        if item[1].collidepoint(event.pos):
                            self.settings['sound'] = not self.settings['sound']
                            save_settings(self.settings)
                            return 'next'
                    elif item[0] == 'back_to_menu':
                        if item[1].collidepoint(event.pos):
                            self.step = 'start'
                            return 'next'
                    elif item[0] == 'clear_leaderboard':
                        if item[1].collidepoint(event.pos):
                            save_leaderboard([])
                            return 'next'
                    elif item[0] == 'mode':
                        if item[2].collidepoint(event.pos):
                            self.selected_mode = item[1]
                            self.step = 'walls'
                            self.selected = 0
                            return 'next'
                    elif item[0] == 'walls':
                        if item[2].collidepoint(event.pos):
                            self.selected_walls = item[1]
                            self.step = 'level'
                            self.selected = 0
                            return 'next'
                    elif item[0] == 'level':
                        if item[2].collidepoint(event.pos):
                            self.selected_level = item[1]
                            self.step = 'color'
                            self.selected = 0
                            return 'next'
                    elif item[0] == 'color':
                        if item[2].collidepoint(event.pos):
                            return {
                                'mode': self.modes[self.selected_mode],
                                'walls': self.walls_types[self.selected_walls],
                                'delay': self.levels[self.selected_level]['delay'],
                                'color': self.colors[item[1]],
                                'controls_p1': self.controls_p1,
                                'controls_p2': self.controls_p2
                            }
                    elif item[0] == 'control':
                        if item[3].collidepoint(event.pos):
                            # Клик на кнопку настройки клавиши
                            player, direction = item[1], item[2]
                            self.waiting_for_key = (player, direction)
                            return 'waiting'
            elif event.type == pygame.KEYDOWN:
                # Обработка ввода клавиши в меню настроек
                if self.waiting_for_key is not None:
                    player, direction = self.waiting_for_key
                    if player == 'p1':
                        self.controls_p1[direction] = event.key
                    else:
                        self.controls_p2[direction] = event.key
                    self.waiting_for_key = None
                    return 'key_set'
                if self.step == 'controls':
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                        self.step = 'start'
                        return 'back'
                    elif event.key == pygame.K_r:
                        # Сброс к дефолтным настройкам
                        self.controls_p1 = self.default_controls_p1.copy()
                        self.controls_p2 = self.default_controls_p2.copy()
                        return 'reset'
                if event.key == pygame.K_f:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((WIDTH, HEIGHT))
                if self.step == 'start':
                    # На начальном экране Enter = Start
                    if event.key == pygame.K_RETURN:
                        self.step = 'mode'
                        self.selected = 0
                        return 'next'
                    elif event.key == pygame.K_c:
                        # Открыть меню настройки управления
                        self.step = 'controls'
                        self.selected = 0
                        return 'controls'
                elif self.step == 'mode':
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
                            'color': self.colors[self.selected],
                            'controls_p1': self.controls_p1,
                            'controls_p2': self.controls_p2
                        }
                    elif event.key == pygame.K_BACKSPACE:
                        self.step = 'level'
                        self.selected = self.selected_level
                        return 'back'
        return -1

    async def run(self):
        self.step = 'start'
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
            elif result in ['next', 'back', 'controls', 'waiting', 'key_set', 'reset']:
                await asyncio.sleep(0)
                continue
            elif isinstance(result, dict):
                return result
            await asyncio.sleep(0)

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
    def __init__(self, move_delay, snake_color, mode='single', bot_color=BLUE, walls_type="Frame walls", controls_p1=None, controls_p2=None, theme='classic', settings=None):
        # Запретить совпадение цветов змеи и бота
        if bot_color == snake_color:
            alt_colors = [c for c in [GREEN, BLUE, RED, (255,255,0), (255,0,255), (0,255,255)] if c != snake_color]
            bot_color = alt_colors[0]
        self.move_delay = move_delay
        self.snake_color = snake_color
        self.mode = mode
        self.bot_color = bot_color
        self.theme = theme
        self.theme_colors = THEMES.get(theme, THEMES['classic'])
        self.settings = settings or load_settings()
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
        # Создаем словарь управления из настроек
        if controls_p1 is None:
            controls_p1 = {
                'up': pygame.K_UP,
                'down': pygame.K_DOWN,
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'speedup': pygame.K_RSHIFT
            }
        if controls_p2 is None:
            controls_p2 = {
                'up': pygame.K_w,
                'down': pygame.K_s,
                'left': pygame.K_a,
                'right': pygame.K_d,
                'speedup': pygame.K_LSHIFT
            }
        
        # Сохраняем клавиши ускорения
        self.speedup_keys = [controls_p1.get('speedup', pygame.K_RSHIFT), 
                            controls_p2.get('speedup', pygame.K_LSHIFT)]
        
        # Конвертируем в формат для Snake
        p1_controls = {
            controls_p1['up']: (0, -CELL_SIZE),
            controls_p1['down']: (0, CELL_SIZE),
            controls_p1['left']: (-CELL_SIZE, 0),
            controls_p1['right']: (CELL_SIZE, 0)
        }
        p2_controls = {
            controls_p2['up']: (0, -CELL_SIZE),
            controls_p2['down']: (0, CELL_SIZE),
            controls_p2['left']: (-CELL_SIZE, 0),
            controls_p2['right']: (CELL_SIZE, 0)
        }
        
        if mode == 'single':
            # Объединяем оба набора для одиночной игры
            controls = {**p1_controls, **p2_controls}
            self.snakes.append(Snake((WIDTH // 2, HEIGHT // 2), (CELL_SIZE, 0), snake_color, controls=controls))
        elif mode == 'pvp':
            self.snakes.append(Snake((WIDTH // 4, HEIGHT // 2), (CELL_SIZE, 0), snake_color, controls=p2_controls))
            self.snakes.append(Snake((3*WIDTH // 4, HEIGHT // 2), (-CELL_SIZE, 0), self.bot_color, controls=p1_controls))
        elif mode == 'bot':
            # Объединяем оба набора для режима с ботом
            controls = {**p1_controls, **p2_controls}
            self.snakes.append(Snake((WIDTH // 4, HEIGHT // 2), (CELL_SIZE, 0), snake_color, controls=controls))
            self.snakes.append(Snake((3*WIDTH // 4, HEIGHT // 2), (-CELL_SIZE, 0), self.bot_color, is_bot=True))
        self.food = self.random_food()
        self.game_over = False
        self.game_started = True
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
                if event.key == pygame.K_ESCAPE:
                    # Возврат в меню
                    self.game_started = False
                    return
                for snake in self.snakes:
                    if not snake.is_bot:
                        snake.set_direction(event.key)

    def move(self):
        # Определяем размеры поля по текущему окну
        # Размер поля всегда равен размеру окна
        field_width = self.screen.get_width()
        field_height = self.screen.get_height()
        # Серые стены убивают только в режиме "With walls"
        walls_enabled = (self.walls_type == 'With walls')
        # wrap_around если "No walls" или "Teleport"
        wrap_around = (self.walls_type in ('No walls', 'Teleport'))
        # Бот управляет собой
        for snake in self.snakes:
            if snake.is_bot and snake.alive:
                self.bot_move(snake)
        # Двигаем всех живых змей
        for snake in self.snakes:
            if snake.alive:
                # wrap_around если walls_type == 'No walls' или 'Teleport'
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
                food_type = self.food['type']
                
                if food_type == 'gold':
                    points = 30
                    growth = 3
                    if self.settings['sound']:
                        play_sound('golden')
                elif food_type == 'poison':
                    points = -10
                    growth = -2  # Уменьшаем змею
                    if self.settings['sound']:
                        play_sound('poison')
                else:  # normal
                    points = 10
                    growth = 1
                    if self.settings['sound']:
                        play_sound('eat')
                
                snake.score += points
                if growth > 0:
                    snake.grow(growth)
                else:
                    # Уменьшаем змею (убираем сегменты с конца)
                    for _ in range(abs(growth)):
                        if len(snake.body) > 1:
                            snake.body.pop()
                
                self.food = self.random_food()
        if not any(s.alive for s in self.snakes):
            if self.settings['sound']:
                play_sound('death')
            self.game_over = True
        heads = [snake.get_head() for snake in self.snakes if snake.alive]
        for i, snake in enumerate(self.snakes):
            if not snake.alive:
                continue
            for j, other in enumerate(self.snakes):
                if i != j and other.alive and snake.get_head() == other.get_head():
                    snake.alive = False
                    other.alive = False
                    if self.settings['sound']:
                        play_sound('death')
        if self.mode in ('single', 'bot', 'pvp'):
            if not self.snakes[0].alive or (len(self.snakes) > 1 and not self.snakes[1].alive):
                if self.settings['sound']:
                    play_sound('death')
                self.game_over = True

    def draw(self):
        # Применяем цвет фона из темы
        bg_color = self.theme_colors['background']
        self.screen.fill(bg_color)
        
        # Рисуем сетку с цветом из темы
        grid_color = self.theme_colors['grid']
        for x in range(0, self.screen.get_width(), CELL_SIZE):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.screen.get_height()))
        for y in range(0, self.screen.get_height(), CELL_SIZE):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.screen.get_width(), y))
        
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
            # Основной цвет стены
            wall_color = (100, 100, 100)
            darker_gray = (70, 70, 70)
            lighter_gray = (130, 130, 130)
            
            # Основной квадрат
            pygame.draw.rect(self.screen, wall_color, (wall[0], wall[1], CELL_SIZE, CELL_SIZE))
            # Темная обводка
            pygame.draw.rect(self.screen, darker_gray, (wall[0], wall[1], CELL_SIZE, CELL_SIZE), 2)
            # Светлые линии (кирпичный эффект)
            pygame.draw.line(self.screen, lighter_gray, (wall[0], wall[1] + CELL_SIZE // 2), (wall[0] + CELL_SIZE, wall[1] + CELL_SIZE // 2), 1)
            pygame.draw.line(self.screen, lighter_gray, (wall[0] + CELL_SIZE // 2, wall[1]), (wall[0] + CELL_SIZE // 2, wall[1] + CELL_SIZE), 1)
            # Диагональные линии для текстуры
            pygame.draw.line(self.screen, darker_gray, (wall[0] + 2, wall[1] + 2), (wall[0] + 6, wall[1] + 6), 1)
            pygame.draw.line(self.screen, darker_gray, (wall[0] + CELL_SIZE - 6, wall[1] + 2), (wall[0] + CELL_SIZE - 2, wall[1] + 6), 1)
        # Рисуем змей
        for snake in self.snakes:
            snake.draw(self.screen)
        # Рисуем еду
        fx = (self.food['pos'][0] // CELL_SIZE) * CELL_SIZE
        fy = (self.food['pos'][1] // CELL_SIZE) * CELL_SIZE
        
        if self.food['type'] == 'gold':
            # Золотое яблоко
            food_color = GOLD
            darker_color = (200, 170, 0)
        elif self.food['type'] == 'poison':
            # Фиолетовое яблоко (яд)
            food_color = PURPLE
            darker_color = (100, 0, 150)
        else:
            # Красное яблоко
            food_color = RED
            darker_color = (180, 0, 0)
        
        # Тень
        shadow_color = (50, 50, 50)
        pygame.draw.circle(self.screen, shadow_color, (fx + CELL_SIZE // 2 + 2, fy + CELL_SIZE - 3), CELL_SIZE // 3)
        
        # Основное яблоко (круг) с градиентом
        pygame.draw.circle(self.screen, darker_color, (fx + CELL_SIZE // 2 + 1, fy + CELL_SIZE // 2 + 1), CELL_SIZE // 2 - 2)
        pygame.draw.circle(self.screen, food_color, (fx + CELL_SIZE // 2, fy + CELL_SIZE // 2), CELL_SIZE // 2 - 2)
        
        # Темная обводка
        pygame.draw.circle(self.screen, (0, 0, 0), (fx + CELL_SIZE // 2, fy + CELL_SIZE // 2), CELL_SIZE // 2 - 2, 2)
        
        # Блик
        highlight_color = (255, 255, 255)
        pygame.draw.circle(self.screen, highlight_color, (fx + CELL_SIZE // 2 - 3, fy + CELL_SIZE // 2 - 4), 4)
        
        # Листик
        leaf_color = (0, 150, 0)
        leaf_points = [
            (fx + CELL_SIZE // 2, fy + 3),
            (fx + CELL_SIZE // 2 + 5, fy),
            (fx + CELL_SIZE // 2 + 3, fy + 6)
        ]
        pygame.draw.polygon(self.screen, leaf_color, leaf_points)
        
        # High Score в левом верхнем углу
        font = pygame.font.SysFont(None, 36)
        leaderboard = load_leaderboard()
        high_score = leaderboard[0]['score'] if leaderboard else 0
        high_score_text = font.render(f"High Score: {high_score}", True, GOLD)
        self.screen.blit(high_score_text, (10, 10))
        
        # Score текущих игроков
        for i, snake in enumerate(self.snakes):
            if self.mode == "bot":
                label = "Player" if i == 0 else "Bot"
            else:
                label = f"P{i+1}"
            text = font.render(f"{label}: {snake.score}", True, snake.color)
            self.screen.blit(text, (10, 50 + i * 35))
        pygame.display.flip()

    def bot_move(self, snake):
        # Бот: идёт к еде, умеет обходить стены
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
        if random.random() < 0.2 and player.alive:
            target = (px, py)
        else:
            target = (fx, fy)
        
        # Нормализуем координаты стен к сетке
        walls_grid = set()
        for wall in self.walls:
            wall_grid = ((wall[0] // CELL_SIZE) * CELL_SIZE, (wall[1] // CELL_SIZE) * CELL_SIZE)
            walls_grid.add(wall_grid)
        
        # Оцениваем каждое направление
        valid_moves = []
        for d in options:
            nx, ny = head[0] + d[0], head[1] + d[1]
            pos_grid = ((nx // CELL_SIZE) * CELL_SIZE, (ny // CELL_SIZE) * CELL_SIZE)
            
            # Проверка разворота на 180 градусов
            if (d[0] == -snake.direction[0] and d[1] == -snake.direction[1]):
                continue
            
            # Проверка стены
            if pos_grid in walls_grid:
                continue
            
            # Проверка столкновения с собой
            if (nx, ny) in snake.body:
                continue
                
            # Проверка границ (если есть)
            field_width = self.screen.get_width()
            field_height = self.screen.get_height()
            if self.walls_type != 'No walls':
                if nx < 0 or nx >= field_width or ny < 0 or ny >= field_height:
                    continue
            
            # Рассчитываем расстояние до цели
            dist = abs(target[0] - nx) + abs(target[1] - ny)
            valid_moves.append((d, dist))
        
        # Выбираем лучший ход из валидных
        if valid_moves:
            valid_moves.sort(key=lambda x: x[1])
            best = valid_moves[0][0]
        
        snake.next_direction = best

    async def get_player_name(self):
        """Запрашивает имя игрока для таблицы лидеров"""
        name = ""
        input_active = True
        font = pygame.font.SysFont(None, 48)
        small_font = pygame.font.SysFont(None, 32)
        
        while input_active:
            self.screen.fill(BLACK)
            center_x = self.screen.get_width() // 2
            center_y = self.screen.get_height() // 2
            
            # Заголовок
            title = font.render("Enter Your Name:", True, WHITE)
            title_rect = title.get_rect(center=(center_x, center_y - 80))
            self.screen.blit(title, title_rect)
            
            # Поле ввода
            input_box = pygame.Rect(center_x - 150, center_y - 20, 300, 50)
            pygame.draw.rect(self.screen, WHITE, input_box, 2)
            name_surface = small_font.render(name, True, WHITE)
            self.screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))
            
            # Инструкции
            hint = small_font.render("Press ENTER to submit, ESC to skip", True, GRAY)
            hint_rect = hint.get_rect(center=(center_x, center_y + 60))
            self.screen.blit(hint, hint_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name:
                        return name
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 15 and event.unicode.isprintable():
                        name += event.unicode
            
            await asyncio.sleep(0)
        
        return name

    async def show_game_over(self):
        # Сохраняем результат в таблицу лидеров
        if self.mode == 'single' and self.snakes[0].score > 0:
            # Запрашиваем имя игрока
            name = await self.get_player_name()
            if name:
                add_score_to_leaderboard(name, self.snakes[0].score)
        
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
                win_text = "PLAYER 1 WINS"
                win_color = self.snakes[0].color
            elif self.snakes[1].alive and not self.snakes[0].alive:
                winner = 1
                win_text = "BOT WINS"
                win_color = self.snakes[1].color
            elif not self.snakes[0].alive and not self.snakes[1].alive:
                if self.snakes[0].score > self.snakes[1].score:
                    winner = 0
                    win_text = "PLAYER 1 WINS"
                    win_color = self.snakes[0].color
                elif self.snakes[1].score > self.snakes[0].score:
                    winner = 1
                    win_text = "BOT WINS"
                    win_color = self.snakes[1].color
                else:
                    winner = None
                    win_text = "DRAW"
                    win_color = WHITE
        elif self.mode == "pvp":
            if scores[0] > scores[1]:
                winner = 0
                win_text = "PLAYER 1 WINS"
                win_color = self.snakes[0].color
            elif scores[1] > scores[0]:
                winner = 1
                win_text = "PLAYER 2 WINS"
                win_color = self.snakes[1].color
            else:
                winner = None
                win_text = "DRAW"
                win_color = WHITE

        button_font = pygame.font.SysFont(None, 36)
        
        while True:
            self.screen.fill(BLACK)
            # Получаем текущие размеры окна для центрирования
            screen_w = self.screen.get_width()
            screen_h = self.screen.get_height()
            center_x = screen_w // 2
            center_y = screen_h // 2
            
            # Создаём кнопки с учётом текущего размера окна
            buttons = [
                {"text": "Restart", "rect": pygame.Rect(center_x - 100, center_y + 20, 200, 50), "action": 'restart'},
                {"text": "Menu", "rect": pygame.Rect(center_x - 100, center_y + 80, 200, 50), "action": 'menu'},
                {"text": "Quit", "rect": pygame.Rect(center_x - 100, center_y + 140, 200, 50), "action": None}
            ]
            
            font = pygame.font.SysFont(None, 48)
            # Крупно и по центру — PLAYER WINS/LOSE/DRAW
            if win_text is not None:
                big_font = pygame.font.SysFont(None, 96)
                text = big_font.render(win_text, True, win_color)
                text_rect = text.get_rect(center=(center_x, center_y - 120))
                self.screen.blit(text, text_rect)
            # Выводим счет всех змей
            score_font = pygame.font.SysFont(None, 36)
            y_offset = center_y - 40
            for i, snake in enumerate(self.snakes):
                if self.mode == "bot":
                    label = "Player" if i == 0 else "Bot"
                else:
                    label = f"P{i+1}"
                score_text = score_font.render(f"{label} Score: {snake.score}", True, snake.color)
                score_rect = score_text.get_rect(center=(center_x, y_offset + i * 40))
                self.screen.blit(score_text, score_rect)

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
            await asyncio.sleep(0)
            self.clock.tick(FPS)

    async def run(self):
        while not self.game_over:
            current_time = pygame.time.get_ticks()
            self.handle_events()
            # Проверка на возврат в меню по Escape
            if not self.game_started:
                return 'menu'
            # Ускорение змейки при удержании клавиш ускорения
            speedup = False
            keys = pygame.key.get_pressed()
            for speedup_key in self.speedup_keys:
                if keys[speedup_key]:
                    speedup = True
                    break
            delay = self.move_delay // 2 if speedup else self.move_delay
            if current_time - self.last_move_time > delay:
                self.move()
                self.last_move_time = current_time
            self.draw()
            await asyncio.sleep(0)
            self.clock.tick(FPS)

        return await self.show_game_over()

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    menu = Menu(screen)
    # Сохраняем последний выбранный режим
    last_result = None
    while True:
        if last_result is None:
            result = await menu.run()
            if result is None:
                break
            last_result = result
        mode = last_result['mode'].lower()
        walls = last_result['walls']
        delay = last_result['delay']
        color = last_result['color']
        controls_p1 = last_result.get('controls_p1')
        controls_p2 = last_result.get('controls_p2')
        theme = menu.current_theme
        settings = menu.settings
        while True:
            game = SnakeGame(delay, color, mode=mode, bot_color=BLUE, walls_type=walls, 
                           controls_p1=controls_p1, controls_p2=controls_p2, theme=theme, settings=settings)
            game.screen = screen
            game_result = await game.run()
            if game_result == 'restart':
                await asyncio.sleep(0)
                continue  # Перезапуск игры с теми же параметрами
            elif game_result == 'menu':
                last_result = None  # Вернуться в меню выбора
                break
            else:
                return  # Выход из main
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
