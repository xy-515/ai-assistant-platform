#!/bin/bash
# One-click startup: FastAPI + Vue
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "======================================================="
echo "  AI Assistant Platform — Starting..."
echo "======================================================="

# Backend
echo "[1/2] Starting FastAPI backend (port 8000)..."
cd "$ROOT/backend"
python -m uvicorn main:app --port 8000 &
BACKEND_PID=$!

# Frontend
echo "[2/2] Starting Vue frontend (port 5173)..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

sleep 3
echo ""
echo "======================================================="
echo "  Backend:  http://localhost:8000/docs"
echo "  Frontend: http://localhost:5173"
echo "======================================================="
echo ""
echo "Press Ctrl+C to stop all services..."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
