# Snake Game

Classic snake game for desktop and web.

[GitHub](https://github.com/zhirkoalexander-maker/snakegame) | [Website](index.html)

## Web Version

Open `index.html` in any browser. Supports single player, vs AI, and local PvP.

## Desktop Version

Python + Pygame. Includes 5 themes, leaderboard, and AI bot.

**Install:**
```bash
pip install pygame numpy
```

**Run:**
```bash
python snake_game_desktop.py
```

## Game Modes

- Single Player
- vs AI Bot
- Local PvP

## Features

- 5 themes
- Sound effects
- Leaderboard (desktop)
- Speed boost
- Wall/No-wall modes

## Controls

- **Arrow Keys / WASD** - Move
- **Space / Shift** - Speed boost
- **Escape** - Menu
- **C** - Configure (desktop)

## Setup

```bash
git clone https://github.com/zhirkoalexander-maker/snakegame.git
cd snakegame
python3 -m venv .venv
source .venv/bin/activate
pip install pygame numpy
python snake_game_desktop.py
```