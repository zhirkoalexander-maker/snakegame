const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const finalScoreElement = document.getElementById('finalScore');
const gameOverElement = document.getElementById('gameOver');

const CELL_SIZE = 20;
const GRID_WIDTH = canvas.width / CELL_SIZE;
const GRID_HEIGHT = canvas.height / CELL_SIZE;

let snake = [];
let direction = { x: 1, y: 0 };
let nextDirection = { x: 1, y: 0 };
let food = {};
let score = 0;
let gameRunning = false;
let speed = 150;
let normalSpeed = 150;
let fastSpeed = 75;
let gameLoop;

// Цвета
const COLORS = {
    background: '#000000',
    snake: '#00ff00',
    snakeHead: '#00cc00',
    food: '#ff0000',
    grid: '#1a1a1a'
};

function init() {
    snake = [
        { x: 15, y: 15 },
        { x: 14, y: 15 },
        { x: 13, y: 15 }
    ];
    direction = { x: 1, y: 0 };
    nextDirection = { x: 1, y: 0 };
    score = 0;
    speed = normalSpeed;
    gameRunning = true;
    gameOverElement.classList.remove('show');
    
    spawnFood();
    updateScore();
    
    if (gameLoop) clearInterval(gameLoop);
    gameLoop = setInterval(update, speed);
}

function spawnFood() {
    do {
        food = {
            x: Math.floor(Math.random() * GRID_WIDTH),
            y: Math.floor(Math.random() * GRID_HEIGHT)
        };
    } while (snake.some(segment => segment.x === food.x && segment.y === food.y));
}

function update() {
    if (!gameRunning) return;
    
    // Применяем буферизованное направление
    direction = { ...nextDirection };
    
    // Новая позиция головы
    const head = {
        x: snake[0].x + direction.x,
        y: snake[0].y + direction.y
    };
    
    // Проверка столкновения со стенами
    if (head.x < 0 || head.x >= GRID_WIDTH || head.y < 0 || head.y >= GRID_HEIGHT) {
        gameOver();
        return;
    }
    
    // Проверка столкновения с собой
    if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
        gameOver();
        return;
    }
    
    snake.unshift(head);
    
    // Проверка поедания еды
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        updateScore();
        spawnFood();
    } else {
        snake.pop();
    }
    
    draw();
}

function draw() {
    // Очистка canvas
    ctx.fillStyle = COLORS.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Рисуем сетку
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    for (let x = 0; x < GRID_WIDTH; x++) {
        for (let y = 0; y < GRID_HEIGHT; y++) {
            ctx.strokeRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        }
    }
    
    // Рисуем змею
    snake.forEach((segment, index) => {
        ctx.fillStyle = index === 0 ? COLORS.snakeHead : COLORS.snake;
        ctx.fillRect(
            segment.x * CELL_SIZE + 1,
            segment.y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        );
        
        // Блик на голове
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
    
    // Рисуем еду
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
    
    // Блик на еде
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
    finalScoreElement.textContent = score;
    gameOverElement.classList.add('show');
}

function updateScore() {
    scoreElement.textContent = score;
}

function restartGame() {
    init();
}

// Управление
document.addEventListener('keydown', (e) => {
    if (!gameRunning && e.key !== ' ') return;
    
    switch(e.key) {
        case 'ArrowUp':
            if (direction.y === 0) nextDirection = { x: 0, y: -1 };
            e.preventDefault();
            break;
        case 'ArrowDown':
            if (direction.y === 0) nextDirection = { x: 0, y: 1 };
            e.preventDefault();
            break;
        case 'ArrowLeft':
            if (direction.x === 0) nextDirection = { x: -1, y: 0 };
            e.preventDefault();
            break;
        case 'ArrowRight':
            if (direction.x === 0) nextDirection = { x: 1, y: 0 };
            e.preventDefault();
            break;
        case ' ':
            // Ускорение
            if (gameRunning) {
                clearInterval(gameLoop);
                speed = fastSpeed;
                gameLoop = setInterval(update, speed);
            }
            e.preventDefault();
            break;
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key === ' ' && gameRunning) {
        clearInterval(gameLoop);
        speed = normalSpeed;
        gameLoop = setInterval(update, speed);
        e.preventDefault();
    }
});

// Запуск игры
init();
