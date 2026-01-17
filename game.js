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

// Menu
let menuStep = 'mode';
const menuSteps = ['mode', 'color', 'start'];

// Players
let players = [];
let food = {};

// Colors
const COLOR_OPTIONS = [
    { name: 'Green', value: '#00ff00' },
    { name: 'Blue', value: '#0099ff' },
    { name: 'Red', value: '#ff0033' },
    { name: 'Yellow', value: '#ffff00' },
    { name: 'Purple', value: '#ff00ff' },
    { name: 'Orange', value: '#ff9900' }
];

const COLORS = {
    background: '#000000',
    food: '#ff0000',
    grid: '#1a1a1a',
    player2: '#0099ff'
};

function init() {
    showMenu();
}

function showMenu() {
    gameState = 'menu';
    document.getElementById('menu').classList.remove('hidden');
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOver').classList.add('hidden');
    renderMenu();
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
            <div class="menu-option" onclick="selectMode('pvp')">
                <h4>👥 Player vs Player</h4>
                <p>Compete with a friend!</p>
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
        }));
        document.getElementById('score2Display').classList.add('hidden');
        document.getElementById('finalScore2Display').classList.add('hidden');
    } else if (gameMode === 'pvp') {
        players.push(createSnake(10, 15, 1, 0, snakeColor, {
            up: 'ArrowUp',
            down: 'ArrowDown',
            left: 'ArrowLeft',
            right: 'ArrowRight',
            speed: 'Shift'
        }));
        players.push(createSnake(20, 15, -1, 0, COLORS.player2, {
            up: 'w',
            down: 's',
            left: 'a',
            right: 'd',
            speed: 'Control'
        }));
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

function createSnake(x, y, dx, dy, color, controls) {
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
        speedUp: false
    };
}

function spawnFood() {
    let allSnakeCells = [];
    players.forEach(player => {
        allSnakeCells = allSnakeCells.concat(player.body);
    });
    
    do {
        food = {
            x: Math.floor(Math.random() * GRID_WIDTH),
            y: Math.floor(Math.random() * GRID_HEIGHT)
        };
    } while (allSnakeCells.some(cell => cell.x === food.x && cell.y === food.y));
}

function update() {
    if (!gameRunning) return;
    
    let alivePlayers = players.filter(p => p.alive);
    if (alivePlayers.length === 0 || (gameMode === 'pvp' && alivePlayers.length === 1)) {
        gameOver();
        return;
    }
    
    players.forEach(player => {
        if (!player.alive) return;
        
        // Apply buffered direction
        player.direction = { ...player.nextDirection };
        
        // New head position
        const head = {
            x: player.body[0].x + player.direction.x,
            y: player.body[0].y + player.direction.y
        };
        
        // Check wall collision
        if (head.x < 0 || head.x >= GRID_WIDTH || head.y < 0 || head.y >= GRID_HEIGHT) {
            player.alive = false;
            return;
        }
        
        // Check self collision
        if (player.body.some(segment => segment.x === head.x && segment.y === head.y)) {
            player.alive = false;
            return;
        }
        
        // Check collision with other players
        players.forEach(other => {
            if (other !== player && other.alive) {
                if (other.body.some(segment => segment.x === head.x && segment.y === head.y)) {
                    player.alive = false;
                }
            }
        });
        
        if (!player.alive) return;
        
        player.body.unshift(head);
        
        // Check food collision
        if (head.x === food.x && head.y === food.y) {
            player.score += 10;
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
    ctx.fillStyle = COLORS.food;
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
}

function gameOver() {
    gameRunning = false;
    clearInterval(gameLoop);
    
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOver').classList.remove('hidden');
    
    if (gameMode === 'pvp') {
        const alivePlayers = players.filter(p => p.alive);
        const winner = alivePlayers.length > 0 ? 'Player ' + (players.indexOf(alivePlayers[0]) + 1) : 'Draw';
        document.getElementById('winner').textContent = winner;
    } else {
        document.getElementById('winner').textContent = 'Game Over';
    }
    
    document.getElementById('finalScore1').textContent = players[0].score;
    if (players.length > 1) {
        document.getElementById('finalScore2').textContent = players[1].score;
    }
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

function backToMenu() {
    menuStep = 'mode';
    showMenu();
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
