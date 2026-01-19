# 🐍 Snake Game - Modern Classic Reimagined

A fully-featured Snake game with multiple game modes, themes, sounds, AI opponent, and **online multiplayer**. Available in both **Python Desktop** and **Web Browser** versions.

[![Play Now](https://img.shields.io/badge/Play-Online-brightgreen?style=for-the-badge)](https://zhirkoalexander-maker.github.io/snakegame/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/zhirkoalexander-maker/snakegame)
[![Download](https://img.shields.io/badge/Download-Desktop%20Version-purple?style=for-the-badge)](https://raw.githubusercontent.com/zhirkoalexander-maker/snakegame/main/snake_game_desktop.py)
[![Multiplayer](https://img.shields.io/badge/Online-Multiplayer-red?style=for-the-badge)](https://github.com/zhirkoalexander-maker/snakegame/blob/main/MULTIPLAYER_DEPLOY.md)

---

## 🎮 Game Versions

### 🌐 Web Version (HTML5 + JavaScript)
**Files:** `index.html`, `snake_game_web.js`

Browser-based version with all features including **online multiplayer**:
- **🌐 Online Multiplayer** - Play with friends over the internet! (2-4 players)
  - Create or join rooms
  - Real-time synchronization
  - Lobby system with ready status
  - Automatic game start countdown
- **Responsive Design** - Play on any device
- **No Installation** - Just open and play
- **Fullscreen Mode** - Immersive gameplay
- **Player Indicators** - See who's Player 1, Player 2, or Bot
- **Snake Textures** - Eyes on head, scale pattern on body
- **Theme Support** - 5 visual themes
- **3 Game Modes:**
  - 🎯 Single Player
  - 🤖 Player vs Bot
  - 👥 Player vs Player (Local)
  - 🌐 **Online Multiplayer** (NEW!)
- **Smart Bot AI:**
  - Attack mode - Cuts off player when stronger
  - Food collection - Seeks apples when safe
  - Independent speed - Player boost doesn't affect bot

#### 🎯 Play Web Version:
- **Online:** [https://zhirkoalexander-maker.github.io/snakegame/](https://zhirkoalexander-maker.github.io/snakegame/)
- **Offline:** Open `index.html` in your browser

#### 🌐 Setting up Multiplayer:
See [MULTIPLAYER_DEPLOY.md](MULTIPLAYER_DEPLOY.md) for detailed instructions on deploying the multiplayer server.

---

### 🖥️ Desktop Version (Python + Pygame)
**File:** `snake_game_desktop.py`

Full-featured desktop game with advanced capabilities:
- **5 Visual Themes** - Classic Dark, Forest Green, Ocean Blue, Neon Purple, Sunset Orange
- **Sound Effects** - Eat, Golden Apple, Death sounds
- **Leaderboard** - Top 10 high scores with persistent storage
- **3 Game Modes:**
  - 🎯 Single Player - Classic snake gameplay
  - 🤖 Player vs Bot - Challenge the AI with attack strategies
  - 👥 Player vs Player (PvP) - Local multiplayer
- **Wall Modes:**
  - With Walls - Hit the wall and die
  - No Walls - Teleport through edges
- **Food Types:**
  - 🍎 Normal Apple - +10 points
  - ⭐ Golden Apple - +30 points, +3 body segments
- **Advanced Features:**
  - Customizable controls (press C)
  - Speed boost (Space/Shift)
  - 3-second countdown before game start
  - Bot autonomous speedup and attack AI
  - Modern settings UI with sections
  - Rules screen with game instructions
  - High Score display

#### 🚀 Running Desktop Version:
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if needed)
pip install pygame numpy

# Run the game
python snake_game_desktop.py
```

#### 📋 Requirements:
- Python 3.13+
- pygame 2.6.1+
- numpy 2.4.1+ (for sound generation)

---

### 🌐 Web Version (HTML5 + JavaScript)
**Files:** `index.html`, `snake_game_web.js`

Browser-based version with all core features:
- **Responsive Design** - Play on any device
- **No Installation** - Just open and play
- **Fullscreen Mode** - Immersive gameplay
- **Player Indicators** - See who's Player 1, Player 2, or Bot
- **Snake Textures** - Eyes on head, scale pattern on body
- **Theme Support** - 5 visual themes
- **Smart Bot AI:**
  - Attack mode - Cuts off player when stronger
  - Food collection - Seeks apples when safe
  - Independent speed - Player boost doesn't affect bot

#### 🎯 Play Web Version:
- **Online:** [https://snakegame-alex.netlify.app/](https://snakegame-alex.netlify.app/)
- **Offline:** Open `index.html` in your browser

---

## 🎮 Controls

### Desktop & Web:
- **Arrow Keys** / **WASD** - Move snake
- **Space** / **Shift** - Speed boost
- **C** - Configure controls (desktop only)
- **F** - Fullscreen (web only)
- **Escape** - Pause / Back to menu

### PvP Mode:
- **Player 1:** Arrow Keys + Space
- **Player 2:** WASD + Ctrl

---

## 🌟 Features

### Visual
- 5 High-Contrast Themes
- Animated Snake (eyes, scales, shine)
- Grid Background
- Player Color Indicators
- High Score Display
- Countdown Timer Overlay

### Audio
- Sound Effects (Toggle on/off)
- Eat Apple (440Hz)
- Golden Apple (880Hz)
- Death (110Hz)

### Gameplay
- 3 Game Modes
- 2 Food Types
- Wall/No-Wall Modes
- Speed Boost Mechanic
- Persistent Leaderboard
- Auto-save Settings

### AI (Bot Mode)
- **Attack Strategy** - Pursues player when stronger
- **Food Collection** - Efficient pathfinding
- **Autonomous Speedup** - Independent acceleration
- **Collision Avoidance** - Smart safety checks

---

## 📂 Project Structure

```
helloworld/
├── snake_game_desktop.py    # Python desktop version
├── main.py                   # Desktop entry point
├── index.html                # Web version HTML
├── snake_game_web.js         # Web version JavaScript
├── web/                      # Netlify deployment folder
│   ├── index.html
│   └── snake_game_web.js
├── netlify.toml              # Netlify configuration
├── DEPLOY.md                 # Deployment instructions
├── README.md                 # This file
└── .venv/                    # Python virtual environment
```

---

## 🚀 Installation & Setup

### Desktop Version:

1. **Clone the repository:**
```bash
git clone https://github.com/zhirkoalexander-maker/snakegame.git
cd snakegame
```

2. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install pygame numpy
```

4. **Run the game:**
```bash
python snake_game_desktop.py
```

### Web Version:

**Option 1: Online**
- Visit: https://snakegame-alex.netlify.app/

**Option 2: Local**
- Open `index.html` in any modern browser

**Option 3: Deploy to Netlify**
See [DEPLOY.md](DEPLOY.md) for instructions

---

## 🎨 Themes

1. **Dark** - Classic black background with green grid
2. **Light** - Light gray background for daytime play
3. **Neon** - Purple neon glow
4. **Forest** - Green nature theme
5. **Ocean** - Deep blue underwater theme

---

## 🏆 Leaderboard

- Automatically saves top 10 scores
- Stored locally in `~/.snake_game_leaderboard.json`
- Shows score, game mode, and date
- Clear records option available

---

## 🔧 Settings Storage

Game settings are persisted in `~/.snake_game_settings.json`:
- Selected theme
- Sound on/off
- Wall mode
- Custom key bindings

---

## 🤖 Bot AI Behavior

### Strategy Selection:
- **Attack Mode** - When bot is +3 segments longer than player
  - Predicts player movement
  - Cuts off escape routes
  - Aggressive positioning

- **Food Collection** - Default behavior
  - Optimal pathfinding to food
  - Safety-first approach
  - Avoids risky moves

### Independent Features:
- Autonomous speedup (distance-based)
- Does not react to player speed boost
- Smart collision avoidance

---

## 📱 Browser Compatibility

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## 🔒 Security

- HTTPS enforced on Netlify deployment
- Secure headers configured
- No external dependencies in web version
- Local storage for settings only

---

## 📝 License

This project is open source and available for educational purposes.

---

## 👤 Author

Created with ❤️ using:
- **Desktop:** Python 3.13 + Pygame 2.6.1
- **Web:** HTML5 Canvas + Vanilla JavaScript

---

## 🔗 Links

- **Play Online:** [https://snakegame-alex.netlify.app/](https://snakegame-alex.netlify.app/)
- **GitHub Repository:** [https://github.com/zhirkoalexander-maker/snakegame](https://github.com/zhirkoalexander-maker/snakegame)
- **Deployment Guide:** [DEPLOY.md](DEPLOY.md)

---

## 🎯 Future Enhancements

- [ ] Mobile touch controls
- [ ] Multiplayer online mode
- [ ] More food types and power-ups
- [ ] Level progression system
- [ ] Global leaderboard
- [ ] Achievement system
- [ ] Custom map editor

---

**Enjoy the game! 🐍🎮**