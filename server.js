const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Multiple rooms system - each room holds 2 players
let rooms = [];

function findOrCreateRoom() {
  // Find room with less than 2 players
  let room = rooms.find(r => r.players.length < 2 && !r.isPlaying);
  
  if (!room) {
    // Create new room
    room = {
      id: `room_${Date.now()}_${Math.random()}`,
      players: [],
      food: null,
      isPlaying: false,
      countdown: null,
      walls: [],
      wallsMode: 'no_walls'
    };
    rooms.push(room);
    console.log(`Created new room: ${room.id}`);
  }
  
  return room;
}

function addPlayer(ws, playerName, room) {
  if (room.players.length >= 2) {
    return false; // Room full
  }
  
  const player = {
    ws: ws,
    id: `player_${Date.now()}_${Math.random()}`,
    name: playerName || `Player ${room.players.length + 1}`,
    snake: null,
    score: 0,
    alive: true,
    room: room
  };
  
  room.players.push(player);
  console.log(`Player joined room ${room.id}. Players: ${room.players.length}/2`);
  return player;
}

function removePlayer(ws) {
  // Find player's room
  for (let room of rooms) {
    const index = room.players.findIndex(p => p.ws === ws);
    if (index !== -1) {
      room.players.splice(index, 1);
      console.log(`Player left room ${room.id}. Players: ${room.players.length}/2`);
      
      // Stop game if playing and someone left
      if (room.isPlaying && room.players.length < 2) {
        endGame(room);
      }
      
      // Remove empty rooms
      if (room.players.length === 0) {
        rooms = rooms.filter(r => r.id !== room.id);
        console.log(`Removed empty room ${room.id}`);
      }
      break;
    }
  }
}

function broadcast(room, message, excludeWs = null) {
  const data = JSON.stringify(message);
  room.players.forEach(player => {
    if (player.ws !== excludeWs && player.ws.readyState === WebSocket.OPEN) {
      player.ws.send(data);
    }
  });
}

function startCountdown(room) {
  if (room.countdown) return;
  
  let count = 3;
  room.countdown = setInterval(() => {
    count--;
    broadcast(room, { type: 'countdown', count: count });
    
    if (count === 0) {
      clearInterval(room.countdown);
      room.countdown = null;
      startGame(room);
    }
  }, 1000);
}

function startGame(room) {
  room.isPlaying = true;
  
  // Initialize food
  room.food = generateFood(room);
  
  // Initialize snakes
  const GRID_WIDTH = 30;
  const GRID_HEIGHT = 30;
  const centerY = Math.floor(GRID_HEIGHT / 2);
  
  room.players.forEach((player, index) => {
    const startX = index === 0 ? 5 : GRID_WIDTH - 6;
    const dirX = index === 0 ? 1 : -1;
    player.snake = {
      body: [
        { x: startX, y: centerY },
        { x: startX - dirX, y: centerY },
        { x: startX - dirX * 2, y: centerY }
      ],
      direction: { x: dirX, y: 0 }
    };
    player.alive = true;
    player.score = 0;
  });
  
  broadcast(room, {
    type: 'game_start',
    players: room.players.map(p => ({
      id: p.id,
      name: p.name,
      snake: p.snake,
      score: p.score,
      alive: p.alive
    })),
    food: room.food,
    wallsMode: room.wallsMode
  });
}

function generateFood(room) {
  const GRID_WIDTH = 30;
  const GRID_HEIGHT = 30;
  
  let food;
  let attempts = 0;
  do {
    food = {
      x: Math.floor(Math.random() * GRID_WIDTH),
      y: Math.floor(Math.random() * GRID_HEIGHT)
    };
    attempts++;
  } while (attempts < 100 && room.players.some(p => 
    p.snake && p.snake.body.some(seg => seg.x === food.x && seg.y === food.y)
  ));
  
  return food;
}

function handleMove(room, playerId, directionStr) {
  if (!room.isPlaying) return;
  
  const player = room.players.find(p => p.id === playerId);
  if (!player || !player.alive) return;
  
  // Convert string direction to vector
  let direction;
  switch(directionStr) {
    case 'up': direction = { x: 0, y: -1 }; break;
    case 'down': direction = { x: 0, y: 1 }; break;
    case 'left': direction = { x: -1, y: 0 }; break;
    case 'right': direction = { x: 1, y: 0 }; break;
    default: return;
  }
  
  // Validate direction change (can't reverse)
  const currentDir = player.snake.direction;
  if ((direction.x !== 0 && currentDir.x !== 0) || (direction.y !== 0 && currentDir.y !== 0)) {
    return; // Can't reverse direction
  }
  
  player.snake.direction = direction;
}

function updateGame(room) {
  if (!room.isPlaying) return;
  
  const GRID_WIDTH = 30;
  const GRID_HEIGHT = 30;
  
  room.players.forEach(player => {
    if (!player.alive) return;
    
    const head = player.snake.body[0];
    let newHead = {
      x: head.x + player.snake.direction.x,
      y: head.y + player.snake.direction.y
    };
    
    // Wrap around edges (no walls mode)
    if (newHead.x < 0) newHead.x = GRID_WIDTH - 1;
    if (newHead.x >= GRID_WIDTH) newHead.x = 0;
    if (newHead.y < 0) newHead.y = GRID_HEIGHT - 1;
    if (newHead.y >= GRID_HEIGHT) newHead.y = 0;
    
    // Check self collision (skip head at index 0)
    if (player.snake.body.slice(1).some(seg => seg.x === newHead.x && seg.y === newHead.y)) {
      player.alive = false;
      return;
    }
    
    // Check collision with other snakes
    for (let other of room.players) {
      if (other.id !== player.id && other.alive) {
        if (other.snake.body.some(seg => seg.x === newHead.x && seg.y === newHead.y)) {
          player.alive = false;
          return;
        }
      }
    }
    
    // Move snake
    player.snake.body.unshift(newHead);
    
    // Check food
    if (newHead.x === room.food.x && newHead.y === room.food.y) {
      player.score += 10;
      room.food = generateFood(room);
    } else {
      player.snake.body.pop();
    }
  });
  
  // Check game over - all players must be dead
  const alivePlayers = room.players.filter(p => p.alive);
  if (alivePlayers.length === 0) {
    endGame(room);
    return;
  }
  
  // Broadcast game state
  broadcast(room, {
    type: 'game_update',
    players: room.players.map(p => ({
      id: p.id,
      name: p.name,
      snake: p.snake,
      score: p.score,
      alive: p.alive
    })),
    food: room.food
  });
}

function endGame(room) {
  room.isPlaying = false;
  
  const alivePlayers = room.players.filter(p => p.alive);
  let winner = null;
  if (alivePlayers.length > 0) {
    winner = alivePlayers[0].id;
  }
  
  broadcast(room, {
    type: 'game_over',
    winner: winner,
    scores: room.players.map(p => ({
      id: p.id,
      name: p.name,
      score: p.score
    }))
  });
}

function getRoomState(room) {
  return {
    players: room.players.map(p => ({
      id: p.id,
      name: p.name
    })),
    isPlaying: room.isPlaying,
    playerCount: room.players.length
  };
}

// WebSocket connection handling
wss.on('connection', (ws) => {
  console.log('New WebSocket connection');
  let currentPlayer = null;
  let currentRoom = null;
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      if (data.type === 'join') {
        currentRoom = findOrCreateRoom();
        currentPlayer = addPlayer(ws, data.name, currentRoom);
        
        if (!currentPlayer) {
          ws.send(JSON.stringify({ type: 'error', message: 'Room is full' }));
          return;
        }
        
        ws.send(JSON.stringify({
          type: 'joined',
          playerId: currentPlayer.id,
          roomId: currentRoom.id,
          roomState: getRoomState(currentRoom)
        }));
        
        broadcast(currentRoom, {
          type: 'player_joined',
          player: { id: currentPlayer.id, name: currentPlayer.name },
          roomState: getRoomState(currentRoom)
        }, ws);
        
        // Auto-start when 2 players
        if (currentRoom.players.length === 2 && !currentRoom.isPlaying) {
          setTimeout(() => startCountdown(currentRoom), 1000);
        }
      }
      else if (data.type === 'start_game') {
        if (currentRoom && currentRoom.players.length === 2) {
          startCountdown(currentRoom);
        }
      }
      else if (data.type === 'player_move') {
        if (currentRoom && currentPlayer) {
          handleMove(currentRoom, currentPlayer.id, data.direction);
        }
      }
    } catch (error) {
      console.error('Error handling message:', error);
    }
  });
  
  ws.on('close', () => {
    if (currentPlayer) {
      removePlayer(ws);
      if (currentRoom) {
        broadcast(currentRoom, {
          type: 'player_left',
          playerId: currentPlayer.id,
          roomState: getRoomState(currentRoom)
        });
      }
    }
    console.log('WebSocket connection closed');
  });
});

// Game loop for all active rooms
setInterval(() => {
  rooms.forEach(room => {
    if (room.isPlaying) {
      updateGame(room);
    }
  });
}, 150);

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'online',
    totalRooms: rooms.length,
    activeGames: rooms.filter(r => r.isPlaying).length,
    totalPlayers: rooms.reduce((sum, r) => sum + r.players.length, 0)
  });
});

const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';

server.listen(PORT, HOST, () => {
  console.log(`Snake Multiplayer Server running on ${HOST}:${PORT}`);
  console.log('Multi-room system with 2 players per room');
});
