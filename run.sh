#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/src/backend"
FRONTEND_DIR="$ROOT_DIR/src/frontend"

cleanup() {
  echo
  echo "Stopping services..."
  jobs -p | xargs -r kill
}
trap cleanup EXIT INT TERM

echo "Starting backend..."
cd "$BACKEND_DIR"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting frontend..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

npm run dev &
FRONTEND_PID=$!

echo
echo "Project is starting..."
echo "Backend:  http://localhost:8000"
echo "Frontend: check Vite output below for exact URL"
echo

wait