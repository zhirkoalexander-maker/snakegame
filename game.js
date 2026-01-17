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
let wallsEnabled = true;
let soundEnabled = true;
let currentTheme = 'dark';

// Menu
let menuStep = 'mode';
const menuSteps = ['mode', 'settings', 'color', 'start'];

// Players
let players = [];
let food = {};
let foodType = 'normal'; // normal, golden, poison

// Bot AI
let botDifficulty = 'medium';

// Colors and Themes
const COLOR_OPTIONS = [
    { name: 'Green', value: '#00ff00' },
    { name: 'Blue', value: '#0099ff' },
    { name: 'Red', value: '#ff0033' },
    { name: 'Yellow', value: '#ffff00' },
    { name: 'Purple', value: '#ff00ff' },
    { name: 'Orange', value: '#ff9900' }
];

const THEMES = {
    dark: { bg: '#000000', grid: '#1a1a1a', text: '#00ff00' },
    light: { bg: '#ffffff', grid: '#e0e0e0', text: '#00aa00' },
    neon: { bg: '#0a0a1a', grid: '#1a0033', text: '#ff00ff' },
    forest: { bg: '#0d1f0d', grid: '#1a3a1a', text: '#00ff00' },
    ocean: { bg: '#001a33', grid: '#003366', text: '#00aaff' }
};

const COLORS = {
    background: '#000000',
    food: '#ff0000',
    foodGolden: '#ffd700',
    foodPoison: '#9900ff',
    grid: '#1a1a1a',
    player2: '#0099ff',
    bot: '#ff9900'
};

// Sound effects
const sounds = {
    eat: () => playSound(400, 0.1),
    death: () => playSound(200, 0.3),
    golden: () => playSound(600, 0.15),
    poison: () => playSound(150, 0.2)
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
            <div class="buttons" style="margin-top: 20px;">
                <button class="btn-secondary" onclick="showLeaderboard()">🏆 Leaderboard</button>
                <button class="btn-secondary" onclick="menuStep='settings'; renderMenu()">⚙️ Settings</button>
            </div>
        `;
    } else if (menuStep === 'settings') {
        menuContent.innerHTML = `
            <h3 style="color: #00ff00; margin-bottom: 20px;">Settings</h3>
            <div class="menu-option" onclick="toggleWalls()">
                <h4>🧱 Walls: ${wallsEnabled ? 'ON' : 'OFF'}</h4>
                <p>${wallsEnabled ? 'Hit walls = death' : 'Teleport through walls'}</p>
            </div>
            <div class="menu-option" onclick="toggleSound()">
                <h4>🔊 Sound: ${soundEnabled ? 'ON' : 'OFF'}</h4>
                <p>Toggle sound effects</p>
            </div>
            <h4 style="color: #00ff00; margin: 20px 0;">Select Theme</h4>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
                ${Object.keys(THEMES).map(theme => `
                    <div class="theme-option ${currentTheme === theme ? 'selected' : ''}" 
                         style="background: ${THEMES[theme].bg}; border: 2px solid ${THEMES[theme].text};"
                         onclick="selectTheme('${theme}')">
                        <div style="color: ${THEMES[theme].text}; text-transform: capitalize;">${theme}</div>
                    </div>
                `).join('')}
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
    wallsEnabled = !wallsEnabled;
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
    menuStep = 'color';
    renderMenu();
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
    gameRunning = true;
    speed = normalSpeed;
    
    if (gameLoop) clearInterval(gameLoop);
    gameLoop = setInterval(update, speed);
    
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
        isBot: isBot
    };
}

function spawnFood() {
    let allSnakeCells = [];
    players.forEach(player => {
        allSnakeCells = allSnakeCells.concat(player.body);
    });
    
    // Random food type
    const rand = Math.random();
    if (rand < 0.7) {
        foodType = 'normal';
    } else if (rand < 0.85) {
        foodType = 'golden';
    } else {
        foodType = 'poison';
    }
    
    do {
        food = {
            x: Math.floor(Math.random() * GRID_WIDTH),
            y: Math.floor(Math.random() * GRID_HEIGHT)
        };
    } while (allSnakeCells.some(cell => cell.x === food.x && cell.y === food.y));
}

// Bot AI
function botMove(bot) {
    if (!bot.alive) return;
    
    const head = bot.body[0];
    const foodDist = { x: food.x - head.x, y: food.y - head.y };
    
    // Simple pathfinding
    let possibleDirs = [];
    if (bot.direction.y === 0) {
        possibleDirs.push({ x: 0, y: -1 }, { x: 0, y: 1 });
    } else {
        possibleDirs.push({ x: -1, y: 0 }, { x: 1, y: 0 });
    }
    
    // Sort by distance to food
    possibleDirs.sort((a, b) => {
        const aDist = Math.abs(foodDist.x - a.x) + Math.abs(foodDist.y - a.y);
        const bDist = Math.abs(foodDist.x - b.x) + Math.abs(foodDist.y - b.y);
        return aDist - bDist;
    });
    
    // Try each direction
    for (let dir of possibleDirs) {
        const newHead = { x: head.x + dir.x, y: head.y + dir.y };
        
        // Check if safe
        let safe = true;
        if (wallsEnabled) {
            if (newHead.x < 0 || newHead.x >= GRID_WIDTH || newHead.y < 0 || newHead.y >= GRID_HEIGHT) {
                safe = false;
            }
        }
        if (safe && bot.body.some(seg => seg.x === newHead.x && seg.y === newHead.y)) {
            safe = false;
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
    if (alivePlayers.length === 0 || (gameMode !== 'single' && alivePlayers.length === 1)) {
        gameOver();
        return;
    }
    
    players.forEach(player => {
        if (!player.alive) return;
        
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
        if (!wallsEnabled) {
            // Teleport
            if (head.x < 0) head.x = GRID_WIDTH - 1;
            if (head.x >= GRID_WIDTH) head.x = 0;
            if (head.y < 0) head.y = GRID_HEIGHT - 1;
            if (head.y >= GRID_HEIGHT) head.y = 0;
        } else {
            // Check wall collision
            if (head.x < 0 || head.x >= GRID_WIDTH || head.y < 0 || head.y >= GRID_HEIGHT) {
                player.alive = false;
                sounds.death();
                return;
            }
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
            } else if (foodType === 'poison') {
                player.score = Math.max(0, player.score - 10);
                sounds.poison();
                // Shrink snake
                if (player.body.length > 3) {
                    player.body.pop();
                    player.body.pop();
                }
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
    
    // Draw players
    players.forEach(player => {
        if (!player.alive) return;
        
        player.body.forEach((segment, index) => {
            ctx.fillStyle = index === 0 ? player.color : player.color + 'cc';
            ctx.fillRect(
                segment.x * CELL_SIZE + 1,
                segment.y * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            );
            
            // Highlight on head
            if (index === 0) {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.fillRect(
                    segment.x * CELL_SIZE + 3,
                    segment.y * CELL_SIZE + 3,
                    CELL_SIZE - 10,
                    CELL_SIZE - 10
                );
            }
        });
    });
    
    // Draw food
    let foodColor = COLORS.food;
    if (foodType === 'golden') foodColor = COLORS.foodGolden;
    if (foodType === 'poison') foodColor = COLORS.foodPoison;
    
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
    } else if (foodType === 'poison') {
        ctx.fillStyle = '#fff';
        ctx.font = '12px Arial';
        ctx.fillText('☠', food.x * CELL_SIZE + 5, food.y * CELL_SIZE + 15);
    }
}

function gameOver() {
    gameRunning = false;
    clearInterval(gameLoop);
    sounds.death();
    
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOver').classList.remove('hidden');
    
    // Save to leaderboard
    const maxScore = Math.max(...players.map(p => p.score));
    saveScore(maxScore, gameMode);
    
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
    
    if (!gameRunning) return;
    
    players.forEach(player => {
        if (!player.alive) return;
        
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
            clearInterval(gameLoop);
            speed = fastSpeed;
            gameLoop = setInterval(update, speed);
        }
    });
    
    e.preventDefault();
});

document.addEventListener('keyup', (e) => {
    pressedKeys[e.key] = false;
    
    if (!gameRunning) return;
    
    players.forEach(player => {
        if (e.key === player.controls.speed && player.speedUp) {
            player.speedUp = false;
            clearInterval(gameLoop);
            speed = normalSpeed;
            gameLoop = setInterval(update, speed);
        }
    });
    
    e.preventDefault();
});

// Start
init();
