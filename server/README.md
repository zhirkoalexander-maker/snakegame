# Snake Multiplayer Server

WebSocket server для онлайн мультиплеера Snake Game.

## Деплой на Glitch

1. Создайте новый проект на [glitch.com](https://glitch.com)
2. Импортируйте из GitHub или загрузите файлы из папки `server/`
3. Glitch автоматически установит зависимости и запустит сервер
4. Скопируйте URL вашего проекта (например, `wss://your-project-name.glitch.me`)
5. Обновите `SERVER_URL` в `snake_game_web.js` на ваш URL

## Локальный запуск

```bash
npm install
npm start
```

Сервер запустится на `http://localhost:3000`

## WebSocket API

### Client -> Server

- `create_room` - Создать новую комнату
- `join_room` - Присоединиться к комнате
- `leave_room` - Покинуть комнату
- `start_game` - Начать игру
- `player_move` - Движение игрока
- `list_rooms` - Список доступных комнат

### Server -> Client

- `room_created` - Комната создана
- `room_joined` - Присоединились к комнате
- `player_joined` - Новый игрок в комнате
- `player_left` - Игрок покинул комнату
- `countdown` - Обратный отсчет перед игрой
- `game_start` - Игра началась
- `game_update` - Обновление состояния игры
- `game_over` - Игра окончена
- `rooms_list` - Список комнат
- `error` - Ошибка

## Особенности

- До 4 игроков в одной комнате
- Автоматическое удаление пустых комнат
- Синхронизация игры ~150ms (6-7 FPS)
- Проверка коллизий на сервере
- Health check endpoint на `/`
