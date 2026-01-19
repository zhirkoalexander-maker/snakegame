const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Game rooms storage
const rooms = new Map();
const playerRooms = new Map(); // Maps player WebSocket to room ID

class GameRoom {
  constructor(roomId) {
    this.roomId = roomId;
    this.players = [];
    this.gameState = null;
    this.isPlaying = false;
    this.countdown = null;
  }

  addPlayer(ws, playerName) {
    if (this.players.length >= 4) {
      return false; // Room full
    }
    
    const player = {
      ws: ws,
      id: `player_${Date.now()}_${Math.random()}`,
      name: playerName || `Player ${this.players.length + 1}`,
      snake: null,
      score: 0,
      alive: true
    };
    
    this.players.push(player);
    playerRooms.set(ws, this.roomId);
    return player;
  }

  removePlayer(ws) {
    const index = this.players.findIndex(p => p.ws === ws);
    if (index !== -1) {
      this.players.splice(index, 1);
      playerRooms.delete(ws);
    }
    
    // If no players left, mark for deletion
    if (this.players.length === 0) {
      return true; // Room should be deleted
    }
    
    // If game was playing and only one player left, end game
    if (this.isPlaying && this.players.length === 1) {
      this.endGame();
    }
    
    return false;
  }

  broadcast(message, excludeWs = null) {
    const data = JSON.stringify(message);
    this.players.forEach(player => {
      if (player.ws !== excludeWs && player.ws.readyState === WebSocket.OPEN) {
        player.ws.send(data);
      }
    });
  }

  startCountdown() {
    if (this.countdown) return;
    
    let count = 3;
    this.countdown = setInterval(() => {
      this.broadcast({ type: 'countdown', count });
      
      if (count === 0) {
        clearInterval(this.countdown);
        this.countdown = null;
        this.startGame();
      }
      count--;
    }, 1000);
  }

  startGame() {
    this.isPlaying = true;
    
    // Initialize game state
    this.gameState = {
      food: this.generateFood(),
      startTime: Date.now()
    };
    
    // Initialize snakes for each player
    const gridSize = 20;
    const startPositions = [
      { x: 5, y: 5 },
      { x: gridSize - 5, y: gridSize - 5 },
      { x: 5, y: gridSize - 5 },
      { x: gridSize - 5, y: 5 }
    ];
    
    this.players.forEach((player, index) => {
      const pos = startPositions[index];
      player.snake = [pos];
      player.alive = true;
      player.score = 0;
      player.direction = index % 2 === 0 ? 'right' : 'left';
    });
    
    this.broadcast({
      type: 'game_start',
      players: this.players.map(p => ({
        id: p.id,
        name: p.name,
        snake: p.snake,
        direction: p.direction,
        score: p.score,
        alive: p.alive
      })),
      food: this.gameState.food
    });
  }

  generateFood() {
    // Simple random food generation
    return {
      x: Math.floor(Math.random() * 20),
      y: Math.floor(Math.random() * 20)
    };
  }

  handleMove(playerId, direction) {
    if (!this.isPlaying) return;
    
    const player = this.players.find(p => p.id === playerId);
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

  update() {
    if (!this.isPlaying) return;
    
    const gridSize = 20;
    let gameOver = false;
    
    // Move each alive snake
    this.players.forEach(player => {
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
      for (let other of this.players) {
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
      if (head.x === this.gameState.food.x && head.y === this.gameState.food.y) {
        player.score++;
        this.gameState.food = this.generateFood();
      } else {
        // Remove tail if no food eaten
        player.snake.pop();
      }
    });
    
    // Check if game over (only one or zero players alive)
    const alivePlayers = this.players.filter(p => p.alive);
    if (alivePlayers.length <= 1) {
      gameOver = true;
    }
    
    // Broadcast game state
    this.broadcast({
      type: 'game_update',
      players: this.players.map(p => ({
        id: p.id,
        name: p.name,
        snake: p.snake,
        direction: p.direction,
        score: p.score,
        alive: p.alive
      })),
      food: this.gameState.food
    });
    
    if (gameOver) {
      this.endGame();
    }
  }

  endGame() {
    this.isPlaying = false;
    
    // Determine winner
    const winner = this.players.reduce((max, p) => 
      (p.score > max.score) ? p : max
    , this.players[0]);
    
    this.broadcast({
      type: 'game_over',
      winner: {
        id: winner.id,
        name: winner.name,
        score: winner.score
      },
      scores: this.players.map(p => ({
        id: p.id,
        name: p.name,
        score: p.score
      }))
    });
  }

  getState() {
    return {
      roomId: this.roomId,
      playerCount: this.players.length,
      isPlaying: this.isPlaying,
      players: this.players.map(p => ({
        id: p.id,
        name: p.name,
        score: p.score
      }))
    };
  }
}

// WebSocket connection handler
wss.on('connection', (ws) => {
  console.log('New client connected');
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      switch (data.type) {
        case 'create_room':
          handleCreateRoom(ws, data);
          break;
          
        case 'join_room':
          handleJoinRoom(ws, data);
          break;
          
        case 'leave_room':
          handleLeaveRoom(ws);
          break;
          
        case 'start_game':
          handleStartGame(ws);
          break;
          
        case 'player_move':
          handlePlayerMove(ws, data);
          break;
          
        case 'list_rooms':
          handleListRooms(ws);
          break;
      }
    } catch (error) {
      console.error('Error handling message:', error);
    }
  });
  
  ws.on('close', () => {
    console.log('Client disconnected');
    handleLeaveRoom(ws);
  });
});

function handleCreateRoom(ws, data) {
  const roomId = `room_${Date.now()}`;
  const room = new GameRoom(roomId);
  const player = room.addPlayer(ws, data.playerName);
  
  rooms.set(roomId, room);
  
  ws.send(JSON.stringify({
    type: 'room_created',
    roomId: roomId,
    playerId: player.id,
    roomState: room.getState()
  }));
}

function handleJoinRoom(ws, data) {
  const room = rooms.get(data.roomId);
  
  if (!room) {
    ws.send(JSON.stringify({
      type: 'error',
      message: 'Room not found'
    }));
    return;
  }
  
  const player = room.addPlayer(ws, data.playerName);
  
  if (!player) {
    ws.send(JSON.stringify({
      type: 'error',
      message: 'Room is full'
    }));
    return;
  }
  
  ws.send(JSON.stringify({
    type: 'room_joined',
    roomId: room.roomId,
    playerId: player.id,
    roomState: room.getState()
  }));
  
  // Notify other players
  room.broadcast({
    type: 'player_joined',
    player: {
      id: player.id,
      name: player.name
    },
    roomState: room.getState()
  }, ws);
}

function handleLeaveRoom(ws) {
  const roomId = playerRooms.get(ws);
  if (!roomId) return;
  
  const room = rooms.get(roomId);
  if (!room) return;
  
  const shouldDelete = room.removePlayer(ws);
  
  if (shouldDelete) {
    rooms.delete(roomId);
  } else {
    room.broadcast({
      type: 'player_left',
      roomState: room.getState()
    });
  }
}

function handleStartGame(ws) {
  const roomId = playerRooms.get(ws);
  if (!roomId) return;
  
  const room = rooms.get(roomId);
  if (!room || room.isPlaying) return;
  
  if (room.players.length < 2) {
    ws.send(JSON.stringify({
      type: 'error',
      message: 'Need at least 2 players to start'
    }));
    return;
  }
  
  room.startCountdown();
}

function handlePlayerMove(ws, data) {
  const roomId = playerRooms.get(ws);
  if (!roomId) return;
  
  const room = rooms.get(roomId);
  if (!room) return;
  
  room.handleMove(data.playerId, data.direction);
}

function handleListRooms(ws) {
  const roomList = Array.from(rooms.values())
    .filter(room => !room.isPlaying && room.players.length < 4)
    .map(room => room.getState());
  
  ws.send(JSON.stringify({
    type: 'rooms_list',
    rooms: roomList
  }));
}

// Game loop - update all active games
setInterval(() => {
  rooms.forEach(room => {
    if (room.isPlaying) {
      room.update();
    }
  });
}, 150); // ~6-7 FPS for game updates

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'online',
    rooms: rooms.size,
    totalPlayers: Array.from(rooms.values()).reduce((sum, room) => sum + room.players.length, 0)
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Snake Multiplayer Server running on port ${PORT}`);
});
