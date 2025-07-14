#!/bin/bash

echo "🚀 Starting Backend and Frontend Servers..."

# Start backend in background
echo "📡 Starting Flask Backend..."
cd app/backend
source venv/bin/activate
flask --app main run --debug &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "⚛️  Starting React Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Both servers are starting..."
echo "📡 Backend: http://localhost:5000"
echo "⚛️  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait 