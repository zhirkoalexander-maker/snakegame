#!/bin/bash
# Скрипт для локального тестирования веб-версии

echo "🐍 Starting local web server for Snake Game..."
echo "📂 Opening http://localhost:8000"
echo "⏱️  First load may take 30-60 seconds (Python loads in browser)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Открываем браузер
open http://localhost:8000 2>/dev/null || xdg-open http://localhost:8000 2>/dev/null || start http://localhost:8000 2>/dev/null

# Запускаем сервер
python3 -m http.server 8000
