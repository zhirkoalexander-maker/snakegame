const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Single global game room for 2 players
let gameRoom = {
  players: [],
  food: null,
  isPlaying: false,
  countdown: null
};

function addPlayer(ws, playerName) {
  if (gameRoom.players.length >= 2) {
    return false; // Room full
  }
  
  const player = {
    ws: ws,
    id: `player_${Date.now()}_${Math.random()}`,
    name: playerName || `Player ${gameRoom.players.length + 1}`,
    snake: null,
    score: 0,
    alive: true
  };
  
  gameRoom.players.push(player);
  return player;
}

function removePlayer(ws) {
  const index = gameRoom.players.findIndex(p => p.ws === ws);
  if (index !== -1) {
    gameRoom.players.splice(index, 1);
  }
  
  // Don't stop game - let remaining player continue or wait for new player
}

function broadcast(message, excludeWs = null) {
  const data = JSON.stringify(message);
  gameRoom.players.forEach(player => {
    if (player.ws !== excludeWs && player.ws.readyState === WebSocket.OPEN) {
      player.ws.send(data);
    }
  });
}

function startCountdown() {
  if (gameRoom.countdown) return;
  
  let count = 3;
  gameRoom.countdown = setInterval(() => {
    broadcast({ type: 'countdown', count });
    
    if (count === 0) {
      clearInterval(gameRoom.countdown);
      gameRoom.countdown = null;
      startGame();
    }
    count--;
  }, 1000);
}

function startGame() {
  gameRoom.isPlaying = true;
  
  // Initialize game state
  gameRoom.food = generateFood();
  
  // Initialize snakes for each player
  const startPositions = [
    { x: 5, y: 5 },
    { x: 15, y: 15 }
  ];
  
  gameRoom.players.forEach((player, index) => {
    const pos = startPositions[index];
    player.snake = [pos];
    player.alive = true;
    player.score = 0;
    player.direction = index === 0 ? 'right' : 'left';
  });
  
  broadcast({
    type: 'game_start',
    players: gameRoom.players.map(p => ({
      id: p.id,
      name: p.name,
      snake: p.snake,
      direction: p.direction,
      score: p.score,
      alive: p.alive
    })),
    food: gameRoom.food
  });
}

function generateFood() {
  return {
    x: Math.floor(Math.random() * 20),
    y: Math.floor(Math.random() * 20)
  };
}

function handleMove(playerId, direction) {
  if (!gameRoom.isPlaying) return;
  
  const player = gameRoom.players.find(p => p.id === playerId);
  if (!player || !player.alive) return;
  
  // Update direction
  const opposite = {
    'up': 'down',
    'down': 'up',
    'left': 'right',
    'right': 'left'
  };
  
  if (direction !== opposite[player.direction]) {
    player.direction = direction;
  }
}

function updateGame() {
  if (!gameRoom.isPlaying) return;
  
  const gridSize = 20;
  let gameOver = false;
  
  // Move each alive snake
  gameRoom.players.forEach(player => {
    if (!player.alive) return;
    
    const head = { ...player.snake[0] };
    
    // Calculate new head position
    switch (player.direction) {
      case 'up': head.y--; break;
      case 'down': head.y++; break;
      case 'left': head.x--; break;
      case 'right': head.x++; break;
    }
    
    // Check wall collision
    if (head.x < 0 || head.x >= gridSize || head.y < 0 || head.y >= gridSize) {
      player.alive = false;
      return;
    }
    
    // Check self collision
    if (player.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
      player.alive = false;
      return;
    }
    
    // Check collision with other snakes
    for (let other of gameRoom.players) {
      if (other.id !== player.id && other.alive) {
        if (other.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
          player.alive = false;
          return;
        }
      }
    }
    
    // Add new head
    player.snake.unshift(head);
    
    // Check food collision
    if (head.x === gameRoom.food.x && head.y === gameRoom.food.y) {
      player.score++;
      gameRoom.food = generateFood();
    } else {
      // Remove tail if no food eaten
      player.snake.pop();
    }
  });
  
  // Check if game over (only one or zero players alive)
  const alivePlayers = gameRoom.players.filter(p => p.alive);
  if (alivePlayers.length <= 1) {
    gameOver = true;
  }
  
  // Broadcast game state
  broadcast({
    type: 'game_update',
    players: gameRoom.players.map(p => ({
      id: p.id,
      name: p.name,
      snake: p.snake,
      direction: p.direction,
      score: p.score,
      alive: p.alive
    })),
    food: gameRoom.food
  });
  
  if (gameOver) {
    endGame();
  }
}

function endGame() {
  gameRoom.isPlaying = false;
  
  // Determine winner
  const winner = gameRoom.players.reduce((max, p) => 
    (p.score > max.score) ? p : max
  , gameRoom.players[0]);
  
  broadcast({
    type: 'game_over',
    winner: {
      id: winner.id,
      name: winner.name,
      score: winner.score
    },
    scores: gameRoom.players.map(p => ({
      id: p.id,
      name: p.name,
      score: p.score
    }))
  });
}

function getRoomState() {
  return {
    playerCount: gameRoom.players.length,
    isPlaying: gameRoom.isPlaying,
    players: gameRoom.players.map(p => ({
      id: p.id,
      name: p.name,
      score: p.score
    }))
  };
}

// WebSocket connection handler
wss.on('connection', (ws) => {
  console.log('New client connected');
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      switch (data.type) {
        case 'join':
          handleJoin(ws, data);
          break;
          
        case 'start_game':
          handleStartGame(ws);
          break;
          
        case 'player_move':
          handlePlayerMove(ws, data);
          break;
      }
    } catch (error) {
      console.error('Error handling message:', error);
    }
  });
  
  ws.on('close', () => {
    console.log('Client disconnected');
    removePlayer(ws);
    
    // Notify remaining player
    if (gameRoom.players.length > 0) {
      broadcast({
        type: 'player_left',
        roomState: getRoomState()
      });
    }
  });
});

function handleJoin(ws, data) {
  const player = addPlayer(ws, data.playerName);
  
  if (!player) {
    ws.send(JSON.stringify({
      type: 'error',
      message: 'Room is full (2 players max)'
    }));
    return;
  }
  
  ws.send(JSON.stringify({
    type: 'joined',
    playerId: player.id,
    roomState: getRoomState()
  }));
  
  // Notify other player
  broadcast({
    type: 'player_joined',
    player: {
      id: player.id,
      name: player.name
    },
    roomState: getRoomState()
  }, ws);
}

function handleStartGame(ws) {
  if (gameRoom.isPlaying) return;
  
  if (gameRoom.players.length < 2) {
    ws.send(JSON.stringify({
      type: 'error',
      message: 'Need 2 players to start'
    }));
    return;
  }
  
  startCountdown();
}

function handlePlayerMove(ws, data) {
  handleMove(data.playerId, data.direction);
}

// Game loop - update game
setInterval(() => {
  if (gameRoom.isPlaying) {
    updateGame();
  }
}, 150); // ~6-7 FPS for game updates

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'online',
    players: gameRoom.players.length,
    isPlaying: gameRoom.isPlaying
  });
});

const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';

server.listen(PORT, HOST, () => {
  console.log(`Snake Multiplayer Server running on ${HOST}:${PORT}`);
  console.log('Simple 2-player mode');
});
