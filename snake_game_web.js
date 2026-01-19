 const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const CELL_SIZE = 20;
const GRID_WIDTH = canvas.width / CELL_SIZE;
const GRID_HEIGHT = canvas.height / CELL_SIZE;

// Game state
let gameState = 'menu';
let gameMode = 'single';
let snakeColor = '#00ff00';
let gameRunning = false;
let speed = 150;
let normalSpeed = 150;
let fastSpeed = 75;
let gameLoop;
let wallsMode = 'no_walls'; // 'with_walls' or 'no_walls'
let soundEnabled = true;
let currentTheme = 'dark';
let countdown = 0;
let countdownInterval = null;
let highScore = 0;

// Multiplayer
// ВАЖНО: Замените на ваш URL после деплоя сервера на Glitch!
// Инструкция: https://github.com/zhirkoalexander-maker/snakegame/blob/main/QUICKSTART_MULTIPLAYER.md
const SERVER_URL = ''; // Например: 'wss://your-project-name.glitch.me'
let ws = null;
let multiplayerRoomId = null;
let multiplayerPlayerId = null;
let multiplayerPlayers = [];
let playerName = '';

// Menu
let menuStep = 'mode';
const menuSteps = ['mode', 'settings', 'rules', 'color', 'start'];

// Players
let players = [];
let food = {};
let foodType = 'normal'; // normal, golden (removed poison)

// Bot AI
let botDifficulty = 'medium';
let botSpeedupActive = false;
let botLastSpeedup = 0;

// Bot difficulty settings
const BOT_DIFFICULTY = {
    easy: { 
        attackThreshold: 15, 
        lengthAdvantage: 8, 
        speedupChance: 0.05,
        reactionDelay: 200
    },
    medium: { 
        attackThreshold: 12, 
        lengthAdvantage: 3, 
        speedupChance: 0.15,
        reactionDelay: 100
    },
    hard: { 
        attackThreshold: 10, 
        lengthAdvantage: 0, 
        speedupChance: 0.25,
        reactionDelay: 0
    }
};

// Colors and Themes (enhanced contrast)
const COLOR_OPTIONS = [
    { name: 'Green', value: '#00ff00' },
    { name: 'Blue', value: '#0099ff' },
    { name: 'Red', value: '#ff0033' },
    { name: 'Yellow', value: '#ffff00' },
    { name: 'Purple', value: '#ff00ff' },
    { name: 'Orange', value: '#ff9900' }
];

const THEMES = {
    dark: { bg: '#000000', grid: '#0d0d0d', text: '#00ff00', name: 'Dark' },
    light: { bg: '#d0d0d0', grid: '#e8e8e8', text: '#006400', name: 'Light' },
    neon: { bg: '#050510', grid: '#150520', text: '#ff00ff', name: 'Neon' },
    forest: { bg: '#051005', grid: '#0a2010', text: '#00ff00', name: 'Forest' },
    ocean: { bg: '#001020', grid: '#002040', text: '#00aaff', name: 'Ocean' }
};

const COLORS = {
    background: '#000000',
    food: '#ff0000',
    foodGolden: '#ffd700',
    grid: '#1a1a1a',
    player2: '#0099ff',
    bot: '#ff9900'
};

// Sound effects
const sounds = {
    eat: () => playSound(440, 0.1),
    death: () => playSound(110, 0.3),
    golden: () => playSound(880, 0.15)
};

function playSound(freq, duration) {
    if (!soundEnabled) return;
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = freq;
    oscillator.type = 'square';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);
}

// Leaderboard
function getLeaderboard() {
    const data = localStorage.getItem('snakeLeaderboard');
    return data ? JSON.parse(data) : [];
}

function saveScore(score, mode) {
    const leaderboard = getLeaderboard();
    leaderboard.push({
        score: score,
        mode: mode,
        date: new Date().toLocaleDateString()
    });
    leaderboard.sort((a, b) => b.score - a.score);
    localStorage.setItem('snakeLeaderboard', JSON.stringify(leaderboard.slice(0, 10)));
}

function showLeaderboard() {
    gameState = 'leaderboard';
    document.getElementById('menu').classList.add('hidden');
    document.getElementById('leaderboardScreen').classList.remove('hidden');
    
    const leaderboard = getLeaderboard();
    const list = document.getElementById('leaderboardList');
    
    if (leaderboard.length === 0) {
        list.innerHTML = '<p style="color: #aaa;">No records yet. Play to set one!</p>';
    } else {
        list.innerHTML = leaderboard.map((entry, index) => `
            <div class="leaderboard-entry">
                <span style="color: #00ff00; font-weight: bold;">#${index + 1}</span>
                Score: ${entry.score} | ${entry.mode} | ${entry.date}
            </div>
        `).join('');
    }
}

function clearLeaderboard() {
    if (confirm('Clear all records?')) {
        localStorage.removeItem('snakeLeaderboard');
        showLeaderboard();
    }
}

function init() {
    showMenu();
}

function showMenu() {
    gameState = 'menu';
    document.getElementById('menu').classList.remove('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOver').classList.add('hidden');
    document.getElementById('leaderboardScreen').classList.add('hidden');
    renderMenu();
}

function updateScores() {
    document.getElementById('score1').textContent = players[0].score;
    if (players.length > 1) {
        document.getElementById('score2').textContent = players[1].score;
    }
}

function restartGame() {
    startGame();
}

function renderMenu() {
    const menuContent = document.getElementById('menuContent');
    
    if (menuStep === 'mode') {
        menuContent.innerHTML = `
            <h3 style="color: #00ff00; margin-bottom: 20px;">Select Game Mode</h3>
            <div class="menu-option" onclick="selectMode('single')">
                <h4>🎯 Single Player</h4>
                <p>Play alone and collect food</p>
            </div>
            <div class="menu-option" onclick="selectMode('bot')">
                <h4>🤖 Player vs Bot</h4>
                <p>Challenge AI opponent!</p>
            </div>
            <div class="menu-option" onclick="selectMode('pvp')">
                <h4>👥 Player vs Player</h4>
                <p>Compete with a friend!</p>
            </div>
            <div class="menu-option" onclick="selectMode('multiplayer')">
                <h4>🌐 Online Multiplayer</h4>
                <p>Play with others online!</p>
            </div>
            <div class="buttons" style="margin-top: 20px;">
                <button class="btn-secondary" onclick="showLeaderboard()">🏆 Leaderboard</button>
                <button class="btn-secondary" onclick="menuStep='settings'; renderMenu()">⚙️ Settings</button>
                <button class="btn-secondary" onclick="menuStep='rules'; renderMenu()">📖 Rules</button>
            </div>
        `;
    } else if (menuStep === 'settings') {
        menuContent.innerHTML = `
            <h3 style="color: #00ff00; margin-bottom: 20px;">⚙️ SETTINGS</h3>
            
            <div style="text-align: left; max-width: 500px; margin: 0 auto;">
                <h4 style="color: #00ff00; margin: 15px 0 10px; text-align: center;">🎨 VISUAL</h4>
                <div class="menu-option" onclick="nextTheme()">
                    <h4>Theme: ${THEMES[currentTheme].name}</h4>
                    <p>Click to change</p>
                </div>
                
                <h4 style="color: #00ff00; margin: 25px 0 10px; text-align: center;">🔊 AUDIO</h4>
                <div class="menu-option" onclick="toggleSound()">
                    <h4>Sound: ${soundEnabled ? 'ON' : 'OFF'}</h4>
                    <p>Toggle sound effects</p>
                </div>
                
                <h4 style="color: #00ff00; margin: 25px 0 10px; text-align: center;">🎮 GAMEPLAY</h4>
                <div class="menu-option" onclick="toggleWalls()">
                    <h4>Walls: ${wallsMode === 'with_walls' ? 'Enabled' : 'Disabled'}</h4>
                    <p>${wallsMode === 'with_walls' ? 'Hit walls = death' : 'Teleport through edges'}</p>
                </div>
                
                <div class="menu-option" onclick="nextBotDifficulty()">
                    <h4>Bot Difficulty: ${botDifficulty.toUpperCase()}</h4>
                    <p>Click to change (Easy / Medium / Hard)</p>
                </div>
            </div>
            
            <div class="buttons" style="margin-top: 30px;">
                <button class="btn-secondary" onclick="menuStep='mode'; renderMenu()">← Back</button>
            </div>
        `;
    } else if (menuStep === 'rules') {
        menuContent.innerHTML = `
            <div style="text-align: left; max-width: 600px; margin: 0 auto;">
                <h3 style="color: #00ff00; margin-bottom: 20px; text-align: center;">📖 GAME RULES</h3>
                
                <h4 style="color: #00ff00; margin-top: 20px;">🎯 OBJECTIVE</h4>
                <p style="color: #aaa; line-height: 1.6;">
                    Eat food to grow your snake and earn points. Avoid hitting walls, 
                    yourself, or your opponent. The longer you survive, the higher your score!
                </p>
                
                <h4 style="color: #00ff00; margin-top: 20px;">🎮 CONTROLS</h4>
                <p style="color: #aaa; line-height: 1.6;">
                    <strong>Player 1:</strong> Arrow Keys to move, Space to speed up<br>
                    <strong>Player 2:</strong> WASD to move, Ctrl to speed up
                </p>
                
                <h4 style="color: #00ff00; margin-top: 20px;">🍎 FOOD TYPES</h4>
                <p style="color: #aaa; line-height: 1.6;">
                    <span style="color: #ff0000;">● Red Apple:</span> +10 points<br>
                    <span style="color: #ffd700;">● Golden Apple:</span> +30 points, grow by 3 segments
                </p>
                
                <h4 style="color: #00ff00; margin-top: 20px;">🕹️ GAME MODES</h4>
                <p style="color: #aaa; line-height: 1.6;">
                    <strong>Single Player:</strong> Classic snake game<br>
                    <strong>Player vs Bot:</strong> Compete against AI<br>
                    <strong>Player vs Player:</strong> Local multiplayer
                </p>
            </div>
            
            <div class="buttons" style="margin-top: 30px;">
                <button class="btn-secondary" onclick="menuStep='mode'; renderMenu()">← Back</button>
            </div>
        `;
    } else if (menuStep === 'color') {
        menuContent.innerHTML = `
            <h3 style="color: #00ff00; margin-bottom: 20px;">Select Snake Color</h3>
            <div class="color-picker">
                ${COLOR_OPTIONS.map(color => `
                    <div class="color-option ${snakeColor === color.value ? 'selected' : ''}" 
                         style="background: ${color.value};"
                         onclick="selectColor('${color.value}')"
                         title="${color.name}">
                    </div>
                `).join('')}
            </div>
            <div class="buttons" style="margin-top: 30px;">
                <button class="btn-secondary" onclick="menuStep='mode'; renderMenu()">← Back</button>
                <button class="btn-primary" onclick="startGame()">Start Game! 🎮</button>
            </div>
        `;
    }
}

function toggleWalls() {
    wallsMode = wallsMode === 'with_walls' ? 'no_walls' : 'with_walls';
    renderMenu();
}

function nextTheme() {
    const themes = Object.keys(THEMES);
    const currentIndex = themes.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themes.length;
    currentTheme = themes[nextIndex];
    
    const themeColors = THEMES[currentTheme];
    COLORS.background = themeColors.bg;
    COLORS.grid = themeColors.grid;
    renderMenu();
}

function nextBotDifficulty() {
    const difficulties = ['easy', 'medium', 'hard'];
    const currentIndex = difficulties.indexOf(botDifficulty);
    const nextIndex = (currentIndex + 1) % difficulties.length;
    botDifficulty = difficulties[nextIndex];
    renderMenu();
}

function toggleSound() {
    soundEnabled = !soundEnabled;
    renderMenu();
}

function selectTheme(theme) {
    currentTheme = theme;
    document.body.className = theme;
    const themeColors = THEMES[theme];
    COLORS.background = themeColors.bg;
    COLORS.grid = themeColors.grid;
    renderMenu();
}

function selectMode(mode) {
    gameMode = mode;
    if (mode === 'multiplayer') {
        showMultiplayerMenu();
    } else {
        menuStep = 'color';
        renderMenu();
    }
}

function selectColor(color) {
    snakeColor = color;
    renderMenu();
}

function startGame() {
    gameState = 'playing';
    document.getElementById('menu').classList.add('hidden');
    document.getElementById('leaderboardScreen').classList.add('hidden');
    document.getElementById('gameScreen').classList.remove('hidden');
    document.getElementById('gameOver').classList.add('hidden');
    
    // Setup players
    players = [];
    if (gameMode === 'single') {
        players.push(createSnake(15, 15, 1, 0, snakeColor, {
            up: 'ArrowUp',
            down: 'ArrowDown',
            left: 'ArrowLeft',
            right: 'ArrowRight',
            speed: ' '
        }, false));
        document.getElementById('score2Display').classList.add('hidden');
        document.getElementById('finalScore2Display').classList.add('hidden');
    } else if (gameMode === 'bot') {
        players.push(createSnake(10, 15, 1, 0, snakeColor, {
            up: 'ArrowUp',
            down: 'ArrowDown',
            left: 'ArrowLeft',
            right: 'ArrowRight',
            speed: ' '
        }, false));
        players.push(createSnake(20, 15, -1, 0, COLORS.bot, {}, true));
        document.getElementById('score2Display').classList.remove('hidden');
        document.getElementById('finalScore2Display').classList.remove('hidden');
    } else if (gameMode === 'pvp') {
        players.push(createSnake(10, 15, 1, 0, snakeColor, {
            up: 'ArrowUp',
            down: 'ArrowDown',
            left: 'ArrowLeft',
            right: 'ArrowRight',
            speed: 'Shift'
        }, false));
        players.push(createSnake(20, 15, -1, 0, COLORS.player2, {
            up: 'w',
            down: 's',
            left: 'a',
            right: 'd',
            speed: 'Control'
        }, false));
        document.getElementById('score2Display').classList.remove('hidden');
        document.getElementById('finalScore2Display').classList.remove('hidden');
    }
    
    spawnFood();
    speed = normalSpeed;
    
    // 3-second countdown
    countdown = 3;
    gameRunning = false;
    draw();
    drawCountdown();
    
    countdownInterval = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            drawCountdown();
        } else {
            clearInterval(countdownInterval);
            gameRunning = true;
            if (gameLoop) clearInterval(gameLoop);
            gameLoop = setInterval(update, 50); // Fast update loop, individual player speeds handled in update()
        }
    }, 1000);
    
    updateScores();
}

function createSnake(x, y, dx, dy, color, controls, isBot = false) {
    return {
        body: [
            { x: x, y: y },
            { x: x - dx, y: y - dy },
            { x: x - dx * 2, y: y - dy * 2 }
        ],
        direction: { x: dx, y: dy },
        nextDirection: { x: dx, y: dy },
        color: color,
        controls: controls,
        score: 0,
        alive: true,
        speedUp: false,
        isBot: isBot,
        moveCounter: 0,
        moveInterval: normalSpeed
    };
}

function spawnFood() {
    let allSnakeCells = [];
    players.forEach(player => {
        allSnakeCells = allSnakeCells.concat(player.body);
    });
    
    // Random food type (only normal and golden, no poison)
    const rand = Math.random();
    if (rand < 0.8) {
        foodType = 'normal';
    } else {
        foodType = 'golden';
    }
    
    do {
        food = {
            x: Math.floor(Math.random() * GRID_WIDTH),
            y: Math.floor(Math.random() * GRID_HEIGHT)
        };
    } while (allSnakeCells.some(cell => cell.x === food.x && cell.y === food.y));
}

// Bot AI with autonomous speedup and attack strategies
function botMove(bot) {
    if (!bot.alive) return;
    
    const head = bot.body[0];
    const foodDist = { 
        x: food.x - head.x, 
        y: food.y - head.y 
    };
    const distanceToFood = Math.sqrt(foodDist.x * foodDist.x + foodDist.y * foodDist.y) * CELL_SIZE;
    
    // Get bot difficulty settings
    const difficulty = BOT_DIFFICULTY[botDifficulty];
    
    // Find human player
    const humanPlayer = players.find(p => !p.isBot && p.alive);
    let strategy = 'food'; // 'food' or 'attack'
    
    if (humanPlayer) {
        const playerHead = humanPlayer.body[0];
        const playerDist = {
            x: playerHead.x - head.x,
            y: playerHead.y - head.y
        };
        const distanceToPlayer = Math.sqrt(playerDist.x * playerDist.x + playerDist.y * playerDist.y);
        
        // Strategy decision - attack based on difficulty
        if (distanceToPlayer < difficulty.attackThreshold && 
            bot.body.length > humanPlayer.body.length + difficulty.lengthAdvantage) {
            strategy = 'attack';
        }
    }
    
    // Bot can decide to speedup when chasing player or food
    const shouldSpeedup = Math.random() < difficulty.speedupChance;
    if (shouldSpeedup && !bot.speedUp) {
        if (strategy === 'attack' || distanceToFood > 150) {
            bot.speedUp = true;
            setTimeout(() => { bot.speedUp = false; }, 800 + Math.random() * 600);
        }
    }
    
    // Get possible directions
    let possibleDirs = [];
    if (bot.direction.y === 0) {
        possibleDirs.push({ x: 0, y: -1 }, { x: 0, y: 1 });
    } else {
        possibleDirs.push({ x: -1, y: 0 }, { x: 1, y: 0 });
    }
    
    // Sort directions based on strategy
    if (strategy === 'attack' && humanPlayer) {
        // Move towards player's head to cut them off
        const playerHead = humanPlayer.body[0];
        const playerNextPos = {
            x: playerHead.x + humanPlayer.direction.x * 3,
            y: playerHead.y + humanPlayer.direction.y * 3
        };
        
        possibleDirs.sort((a, b) => {
            const aDist = Math.abs(playerNextPos.x - (head.x + a.x)) + 
                         Math.abs(playerNextPos.y - (head.y + a.y));
            const bDist = Math.abs(playerNextPos.x - (head.x + b.x)) + 
                         Math.abs(playerNextPos.y - (head.y + b.y));
            return aDist - bDist;
        });
    } else {
        // Default: go for food
        possibleDirs.sort((a, b) => {
            const aDist = Math.abs(foodDist.x - a.x) + Math.abs(foodDist.y - a.y);
            const bDist = Math.abs(foodDist.x - b.x) + Math.abs(foodDist.y - b.y);
            return aDist - bDist;
        });
    }
    
    // Try each direction and pick the safest
    for (let dir of possibleDirs) {
        const newHead = { x: head.x + dir.x, y: head.y + dir.y };
        
        // Handle wall wrapping
        if (wallsMode !== 'with_walls') {
            if (newHead.x < 0) newHead.x = GRID_WIDTH - 1;
            if (newHead.x >= GRID_WIDTH) newHead.x = 0;
            if (newHead.y < 0) newHead.y = GRID_HEIGHT - 1;
            if (newHead.y >= GRID_HEIGHT) newHead.y = 0;
        }
        
        // Check if safe
        let safe = true;
        
        // Wall collision
        if (wallsMode === 'with_walls') {
            if (newHead.x < 0 || newHead.x >= GRID_WIDTH || 
                newHead.y < 0 || newHead.y >= GRID_HEIGHT) {
                safe = false;
            }
        }
        
        // Self collision
        if (safe && bot.body.some(seg => seg.x === newHead.x && seg.y === newHead.y)) {
            safe = false;
        }
        
        // Player collision
        if (safe && humanPlayer) {
            if (humanPlayer.body.some(seg => seg.x === newHead.x && seg.y === newHead.y)) {
                safe = false;
            }
        }
        
        if (safe) {
            bot.nextDirection = dir;
            break;
        }
    }
}

function update() {
    if (!gameRunning) return;
    
    let alivePlayers = players.filter(p => p.alive);
    
    // Game over conditions
    if (alivePlayers.length === 0) {
        gameOver();
        return;
    }
    
    // In bot or PvP mode, end game if only one player alive
    if (gameMode === 'bot' || gameMode === 'pvp') {
        if (alivePlayers.length === 1) {
            gameOver();
            return;
        }
    }
    
    players.forEach(player => {
        if (!player.alive) return;
        
        // Update move counter with fixed timestep
        player.moveCounter += 50; // Fixed 50ms per update
        
        // Determine player's move speed
        const playerSpeed = player.speedUp ? fastSpeed : normalSpeed;
        
        // Skip move if not enough time passed for this player
        if (player.moveCounter < playerSpeed) {
            return;
        }
        
        player.moveCounter = 0;
        
        // Bot AI
        if (player.isBot) {
            botMove(player);
        }
        
        // Apply buffered direction
        player.direction = { ...player.nextDirection };
        
        // New head position
        let head = {
            x: player.body[0].x + player.direction.x,
            y: player.body[0].y + player.direction.y
        };
        
        // Wall handling
        if (wallsMode === 'with_walls') {
            // Check wall collision - death if hit wall
            if (head.x < 0 || head.x >= GRID_WIDTH || head.y < 0 || head.y >= GRID_HEIGHT) {
                player.alive = false;
                sounds.death();
                return;
            }
        } else {
            // Teleport through edges
            if (head.x < 0) head.x = GRID_WIDTH - 1;
            if (head.x >= GRID_WIDTH) head.x = 0;
            if (head.y < 0) head.y = GRID_HEIGHT - 1;
            if (head.y >= GRID_HEIGHT) head.y = 0;
        }
        
        // Check self collision
        if (player.body.some(segment => segment.x === head.x && segment.y === head.y)) {
            player.alive = false;
            sounds.death();
            return;
        }
        
        // Check collision with other players
        players.forEach(other => {
            if (other !== player && other.alive) {
                if (other.body.some(segment => segment.x === head.x && segment.y === head.y)) {
                    player.alive = false;
                    sounds.death();
                }
            }
        });
        
        if (!player.alive) return;
        
        player.body.unshift(head);
        
        // Check food collision
        if (head.x === food.x && head.y === food.y) {
            if (foodType === 'normal') {
                player.score += 10;
                sounds.eat();
            } else if (foodType === 'golden') {
                player.score += 30;
                sounds.golden();
                // Grow by 3 segments
                player.body.push(player.body[player.body.length - 1]);
                player.body.push(player.body[player.body.length - 1]);
            }
            
            // Update high score
            if (player.score > highScore) {
                highScore = player.score;
            }
            
            updateScores();
            spawnFood();
        } else {
            player.body.pop();
        }
    });
    
    draw();
}

function draw() {
    // Clear canvas
    ctx.fillStyle = COLORS.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    for (let x = 0; x < GRID_WIDTH; x++) {
        for (let y = 0; y < GRID_HEIGHT; y++) {
            ctx.strokeRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        }
    }
    
    // Draw High Score
    ctx.fillStyle = '#00ff00';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('High Score: ' + highScore, 10, 20);
    
    // Draw player indicators
    if (players.length > 0 && gameRunning) {
        ctx.textAlign = 'right';
        ctx.font = 'bold 14px Arial';
        
        // Player 1 indicator
        if (players[0] && players[0].alive) {
            ctx.fillStyle = players[0].color;
            ctx.fillText('● Player 1', canvas.width - 10, 20);
        }
        
        // Player 2 / Bot indicator
        if (players.length > 1 && players[1] && players[1].alive) {
            ctx.fillStyle = players[1].color;
            const label = players[1].isBot ? '● Bot' : '● Player 2';
            ctx.fillText(label, canvas.width - 10, 40);
        }
        
        ctx.textAlign = 'left';
    }
    
    // Draw walls if enabled
    if (wallsMode === 'with_walls') {
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 4;
        ctx.strokeRect(2, 2, canvas.width - 4, canvas.height - 4);
    }
    
    // Draw players with textures
    players.forEach((player, playerIndex) => {
        if (!player.alive) return;
        
        player.body.forEach((segment, index) => {
            const x = segment.x * CELL_SIZE;
            const y = segment.y * CELL_SIZE;
            
            if (index === 0) {
                // Draw head with eyes
                ctx.fillStyle = player.color;
                ctx.fillRect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2);
                
                // Head shine
                ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
                ctx.fillRect(x + 3, y + 3, CELL_SIZE - 10, CELL_SIZE - 10);
                
                // Eyes
                ctx.fillStyle = '#000';
                const eyeSize = 3;
                const eyeOffset = 5;
                
                // Determine eye position based on direction
                if (player.direction.x === 1) { // Right
                    ctx.fillRect(x + CELL_SIZE - eyeOffset - eyeSize, y + 5, eyeSize, eyeSize);
                    ctx.fillRect(x + CELL_SIZE - eyeOffset - eyeSize, y + CELL_SIZE - 8, eyeSize, eyeSize);
                } else if (player.direction.x === -1) { // Left
                    ctx.fillRect(x + eyeOffset, y + 5, eyeSize, eyeSize);
                    ctx.fillRect(x + eyeOffset, y + CELL_SIZE - 8, eyeSize, eyeSize);
                } else if (player.direction.y === -1) { // Up
                    ctx.fillRect(x + 5, y + eyeOffset, eyeSize, eyeSize);
                    ctx.fillRect(x + CELL_SIZE - 8, y + eyeOffset, eyeSize, eyeSize);
                } else { // Down
                    ctx.fillRect(x + 5, y + CELL_SIZE - eyeOffset - eyeSize, eyeSize, eyeSize);
                    ctx.fillRect(x + CELL_SIZE - 8, y + CELL_SIZE - eyeOffset - eyeSize, eyeSize, eyeSize);
                }
            } else {
                // Draw body with scale pattern
                ctx.fillStyle = player.color + 'cc';
                ctx.fillRect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2);
                
                // Scale texture
                ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
                ctx.beginPath();
                ctx.arc(x + CELL_SIZE / 2, y + CELL_SIZE / 2, CELL_SIZE / 3, 0, Math.PI * 2);
                ctx.fill();
                
                // Additional pattern lines
                ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(x + 2, y + CELL_SIZE / 2);
                ctx.lineTo(x + CELL_SIZE - 2, y + CELL_SIZE / 2);
                ctx.stroke();
            }
        });
    });
    
    // Draw food
    let foodColor = foodType === 'golden' ? COLORS.foodGolden : COLORS.food;
    
    ctx.fillStyle = foodColor;
    ctx.beginPath();
    ctx.arc(
        food.x * CELL_SIZE + CELL_SIZE / 2,
        food.y * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE / 2 - 2,
        0,
        Math.PI * 2
    );
    ctx.fill();
    
    // Highlight on food
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.beginPath();
    ctx.arc(
        food.x * CELL_SIZE + CELL_SIZE / 2 - 3,
        food.y * CELL_SIZE + CELL_SIZE / 2 - 3,
        3,
        0,
        Math.PI * 2
    );
    ctx.fill();
    
    // Draw food type indicator
    if (foodType === 'golden') {
        ctx.fillStyle = '#fff';
        ctx.font = '12px Arial';
        ctx.fillText('★', food.x * CELL_SIZE + 5, food.y * CELL_SIZE + 15);
    }
}

function drawCountdown() {
    draw();
    
    // Full screen overlay
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Countdown number
    ctx.fillStyle = '#00ff00';
    ctx.font = 'bold 120px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(countdown.toString(), canvas.width / 2, canvas.height / 2);
    
    ctx.textBaseline = 'alphabetic';
}

function gameOver() {
    gameRunning = false;
    clearInterval(gameLoop);
    sounds.death();
    
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOver').classList.remove('hidden');
    
    // Save to leaderboard (only player scores, not bot)
    if (gameMode === 'bot') {
        // In bot mode, save only the player's score (index 0)
        saveScore(players[0].score, gameMode);
    } else {
        // In single or pvp mode, save the max score
        const maxScore = Math.max(...players.map(p => p.score));
        saveScore(maxScore, gameMode);
    }
    
    if (gameMode !== 'single') {
        const alivePlayers = players.filter(p => p.alive);
        let winner = 'Draw';
        if (alivePlayers.length > 0) {
            const winnerIndex = players.indexOf(alivePlayers[0]);
            winner = gameMode === 'bot' ? (winnerIndex === 0 ? 'You' : 'Bot') : 'Player ' + (winnerIndex + 1);
        }
        document.getElementById('winner').textContent = winner + ' wins!';
    } else {
        document.getElementById('winner').textContent = 'Game Over';
    }
    
    document.getElementById('finalScore1').textContent = players[0].score;
    if (players.length > 1) {
        document.getElementById('finalScore2').textContent = players[1].score;
    }
}

function backToMenu() {
    menuStep = 'mode';
    gameState = 'menu';
    document.getElementById('menu').classList.remove('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOver').classList.add('hidden');
    document.getElementById('leaderboardScreen').classList.add('hidden');
    renderMenu();
}

// Controls
const pressedKeys = {};

document.addEventListener('keydown', (e) => {
    pressedKeys[e.key] = true;
    
    if (!gameRunning || countdown > 0) return;
    
    players.forEach(player => {
        if (!player.alive || player.isBot) return;
        
        const controls = player.controls;
        
        if (e.key === controls.up && player.direction.y === 0) {
            player.nextDirection = { x: 0, y: -1 };
        } else if (e.key === controls.down && player.direction.y === 0) {
            player.nextDirection = { x: 0, y: 1 };
        } else if (e.key === controls.left && player.direction.x === 0) {
            player.nextDirection = { x: -1, y: 0 };
        } else if (e.key === controls.right && player.direction.x === 0) {
            player.nextDirection = { x: 1, y: 0 };
        } else if (e.key === controls.speed && !player.speedUp) {
            player.speedUp = true;
        }
    });
    
    e.preventDefault();
});

document.addEventListener('keyup', (e) => {
    pressedKeys[e.key] = false;
    
    if (!gameRunning || countdown > 0) return;
    
    players.forEach(player => {
        if (player.isBot) return;
        if (e.key === player.controls.speed && player.speedUp) {
            player.speedUp = false;
        }
    });
    
    e.preventDefault();
});

// ============= MULTIPLAYER FUNCTIONS =============

function showMultiplayerMenu() {
    const menuContent = document.getElementById('menuContent');
    menuContent.innerHTML = `
        <h3 style="color: #00ff00; margin-bottom: 20px;">🌐 Online Multiplayer</h3>
        
        <div style="text-align: center; margin-bottom: 20px;">
            <input type="text" id="playerNameInput" placeholder="Enter your name" 
                   style="padding: 10px; font-size: 16px; border: 2px solid #00ff00; 
                          background: #000; color: #00ff00; border-radius: 5px; width: 250px;"
                   maxlength="15" value="${playerName}">
        </div>
        
        <div class="menu-option" onclick="createRoom()">
            <h4>🎮 Create Room</h4>
            <p>Start a new multiplayer game</p>
        </div>
        
        <div class="menu-option" onclick="showRoomList()">
            <h4>🔍 Join Room</h4>
            <p>Browse available rooms</p>
        </div>
        
        <div id="roomListContainer"></div>
        <div id="multiplayerStatus" style="color: #ffff00; margin-top: 20px;"></div>
        
        <div class="buttons" style="margin-top: 30px;">
            <button class="btn-secondary" onclick="menuStep='mode'; renderMenu()">← Back</button>
        </div>
    `;
}

function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) return Promise.resolve();
    
    // Проверка, что URL сервера установлен
    if (!SERVER_URL || SERVER_URL === '') {
        document.getElementById('multiplayerStatus').innerHTML = `
            <div style="color: #ff9900; text-align: left; max-width: 500px; margin: 20px auto; padding: 15px; background: #221100; border: 2px solid #ff9900; border-radius: 5px;">
                <h4 style="color: #ff9900; margin: 0 0 10px 0;">⚠️ Сервер не настроен</h4>
                <p style="margin: 5px 0; font-size: 14px;">Для игры в онлайн мультиплеер нужно:</p>
                <ol style="margin: 10px 0; padding-left: 20px; font-size: 14px;">
                    <li>Задеплоить сервер на Glitch (5 минут)</li>
                    <li>Обновить SERVER_URL в коде</li>
                    <li>Запушить изменения</li>
                </ol>
                <p style="margin: 10px 0 0 0; font-size: 14px;">
                    📖 <a href="https://github.com/zhirkoalexander-maker/snakegame/blob/main/QUICKSTART_MULTIPLAYER.md" 
                         target="_blank" style="color: #00ff00; text-decoration: underline;">
                         Инструкция по настройке
                    </a>
                </p>
            </div>
        `;
        return Promise.reject(new Error('Server URL not configured'));
    }
    
    return new Promise((resolve, reject) => {
        document.getElementById('multiplayerStatus').textContent = '🔄 Connecting to server...';
        document.getElementById('multiplayerStatus').style.color = '#ffff00';
        
        ws = new WebSocket(SERVER_URL);
        
        ws.onopen = () => {
            document.getElementById('multiplayerStatus').textContent = '✅ Connected to server';
            document.getElementById('multiplayerStatus').style.color = '#00ff00';
            resolve();
        };
        
        ws.onerror = () => {
            document.getElementById('multiplayerStatus').innerHTML = `
                <div style="color: #ff0000;">
                    ❌ Не удалось подключиться к серверу
                    <br><small>Проверьте, что сервер запущен на Glitch</small>
                </div>
            `;
            reject(new Error('WebSocket connection failed'));
        };
        
        ws.onclose = () => {
            if (gameMode === 'multiplayer' && gameState === 'playing') {
                endGame();
                alert('Lost connection to server');
            }
        };
        
        ws.onmessage = (event) => {
            handleServerMessage(JSON.parse(event.data));
        };
    });
}

function createRoom() {
    playerName = document.getElementById('playerNameInput').value.trim() || 'Player';
    
    connectWebSocket().then(() => {
        ws.send(JSON.stringify({
            type: 'create_room',
            playerName: playerName
        }));
    }).catch(err => {
        // Ошибка уже отображена в connectWebSocket
    });
}

function showRoomList() {
    playerName = document.getElementById('playerNameInput').value.trim() || 'Player';
    
    connectWebSocket().then(() => {
        ws.send(JSON.stringify({
            type: 'list_rooms'
        }));
    }).catch(err => {
        // Ошибка уже отображена в connectWebSocket
    });
}

function joinRoom(roomId) {
    ws.send(JSON.stringify({
        type: 'join_room',
        roomId: roomId,
        playerName: playerName
    }));
}

function leaveRoom() {
    if (ws && multiplayerRoomId) {
        ws.send(JSON.stringify({
            type: 'leave_room'
        }));
    }
    multiplayerRoomId = null;
    multiplayerPlayerId = null;
    multiplayerPlayers = [];
    showMultiplayerMenu();
}

function startMultiplayerGame() {
    if (!multiplayerRoomId) return;
    
    ws.send(JSON.stringify({
        type: 'start_game'
    }));
}

function handleServerMessage(data) {
    switch (data.type) {
        case 'room_created':
            multiplayerRoomId = data.roomId;
            multiplayerPlayerId = data.playerId;
            showLobby(data.roomState);
            break;
            
        case 'room_joined':
            multiplayerRoomId = data.roomId;
            multiplayerPlayerId = data.playerId;
            showLobby(data.roomState);
            break;
            
        case 'player_joined':
            showLobby(data.roomState);
            break;
            
        case 'player_left':
            if (gameState === 'lobby') {
                showLobby(data.roomState);
            }
            break;
            
        case 'rooms_list':
            displayRoomList(data.rooms);
            break;
            
        case 'countdown':
            showCountdown(data.count);
            break;
            
        case 'game_start':
            startMultiplayerGameClient(data);
            break;
            
        case 'game_update':
            updateMultiplayerGame(data);
            break;
            
        case 'game_over':
            endMultiplayerGame(data);
            break;
            
        case 'error':
            alert(data.message);
            break;
    }
}

function showLobby(roomState) {
    gameState = 'lobby';
    const menuContent = document.getElementById('menuContent');
    
    const playersList = roomState.players.map(p => 
        `<div style="padding: 8px; background: #001100; margin: 5px 0; border-radius: 5px;">
            ${p.name} ${p.id === multiplayerPlayerId ? '(You)' : ''}
        </div>`
    ).join('');
    
    menuContent.innerHTML = `
        <h3 style="color: #00ff00; margin-bottom: 20px;">🎮 Lobby</h3>
        <p style="color: #ffff00;">Room ID: ${roomState.roomId}</p>
        <p style="color: #00ff00;">Players: ${roomState.playerCount}/4</p>
        
        <div style="margin: 20px 0;">
            ${playersList}
        </div>
        
        ${roomState.playerCount >= 2 ? 
            '<button class="btn" onclick="startMultiplayerGame()">🚀 Start Game</button>' : 
            '<p style="color: #ffff00;">Waiting for players... (need at least 2)</p>'}
        
        <div class="buttons" style="margin-top: 30px;">
            <button class="btn-secondary" onclick="leaveRoom()">← Leave Room</button>
        </div>
    `;
}

function displayRoomList(rooms) {
    const container = document.getElementById('roomListContainer');
    
    if (rooms.length === 0) {
        container.innerHTML = `
            <div style="color: #ffff00; margin-top: 20px;">
                No rooms available. Create one!
            </div>
        `;
        return;
    }
    
    const roomItems = rooms.map(room => `
        <div class="menu-option" onclick="joinRoom('${room.roomId}')">
            <h4>Room ${room.roomId.slice(-6)}</h4>
            <p>Players: ${room.playerCount}/4</p>
        </div>
    `).join('');
    
    container.innerHTML = `
        <h4 style="color: #00ff00; margin-top: 20px;">Available Rooms:</h4>
        ${roomItems}
    `;
}

function showCountdown(count) {
    document.getElementById('menu').classList.add('hidden');
    document.getElementById('gameScreen').classList.remove('hidden');
    gameState = 'countdown';
    
    ctx.fillStyle = COLORS.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#00ff00';
    ctx.font = '72px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(count || 'GO!', canvas.width / 2, canvas.height / 2);
}

function startMultiplayerGameClient(data) {
    gameState = 'playing';
    gameRunning = true;
    multiplayerPlayers = data.players;
    food = data.food;
    
    // Start render loop
    gameLoop = setInterval(renderMultiplayerGame, 50);
}

function updateMultiplayerGame(data) {
    multiplayerPlayers = data.players;
    food = data.food;
}

function renderMultiplayerGame() {
    // Draw background
    ctx.fillStyle = COLORS.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= GRID_WIDTH; i++) {
        ctx.beginPath();
        ctx.moveTo(i * CELL_SIZE, 0);
        ctx.lineTo(i * CELL_SIZE, canvas.height);
        ctx.stroke();
    }
    for (let i = 0; i <= GRID_HEIGHT; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * CELL_SIZE);
        ctx.lineTo(canvas.width, i * CELL_SIZE);
        ctx.stroke();
    }
    
    // Draw food
    ctx.fillStyle = COLORS.food;
    ctx.fillRect(food.x * CELL_SIZE, food.y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
    
    // Draw snakes
    const colors = ['#00ff00', '#0099ff', '#ff9900', '#ff00ff'];
    multiplayerPlayers.forEach((player, index) => {
        if (!player.alive) return;
        
        ctx.fillStyle = colors[index % colors.length];
        player.snake.forEach(segment => {
            ctx.fillRect(segment.x * CELL_SIZE, segment.y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        });
    });
    
    // Draw scores
    ctx.fillStyle = '#00ff00';
    ctx.font = '16px monospace';
    ctx.textAlign = 'left';
    multiplayerPlayers.forEach((player, index) => {
        const color = colors[index % colors.length];
        const status = player.alive ? '✓' : '✗';
        ctx.fillStyle = color;
        ctx.fillText(`${player.name}: ${player.score} ${status}`, 10, 20 + index * 20);
    });
}

function endMultiplayerGame(data) {
    gameRunning = false;
    gameState = 'gameOver';
    clearInterval(gameLoop);
    
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOver').classList.remove('hidden');
    
    const gameOverContent = document.getElementById('gameOverContent');
    
    const scoresList = data.scores.map((s, i) => 
        `<div style="padding: 8px; margin: 5px 0; background: ${i === 0 ? '#003300' : '#001100'}; border-radius: 5px;">
            ${i + 1}. ${s.name}: ${s.score} ${s.id === data.winner.id ? '🏆' : ''}
        </div>`
    ).join('');
    
    gameOverContent.innerHTML = `
        <h2 style="color: #00ff00;">Game Over!</h2>
        <h3 style="color: #ffff00;">Winner: ${data.winner.name}</h3>
        <p style="color: #00ff00;">Score: ${data.winner.score}</p>
        
        <div style="margin-top: 20px;">
            <h4 style="color: #00ff00;">Final Scores:</h4>
            ${scoresList}
        </div>
        
        <div class="buttons" style="margin-top: 30px;">
            <button class="btn" onclick="leaveRoom()">← Back to Lobby</button>
            <button class="btn-secondary" onclick="showMenu()">Main Menu</button>
        </div>
    `;
}

// Send player moves to server
document.addEventListener('keydown', (e) => {
    if (gameMode === 'multiplayer' && gameRunning && multiplayerPlayerId) {
        let direction = null;
        
        if (e.key === 'ArrowUp' || e.key === 'w') direction = 'up';
        else if (e.key === 'ArrowDown' || e.key === 's') direction = 'down';
        else if (e.key === 'ArrowLeft' || e.key === 'a') direction = 'left';
        else if (e.key === 'ArrowRight' || e.key === 'd') direction = 'right';
        
        if (direction && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'player_move',
                playerId: multiplayerPlayerId,
                direction: direction
            }));
        }
    }
});

// Start
init();
