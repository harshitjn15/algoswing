#!/bin/bash

# AlgoSwing Development Starter Script

echo "Starting AlgoSwing Development Environment..."

# Start Backend
echo "Starting Backend on http://localhost:8000"
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start Frontend
echo "Starting Frontend on http://localhost:3000"
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "Both servers are running."
echo "Press Ctrl+C to stop both servers."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT
wait $BACKEND_PID $FRONTEND_PID
