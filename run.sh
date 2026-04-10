#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/src/backend_dummy"
FRONTEND_DIR="$ROOT_DIR/src/frontend"

cleanup() {
  echo
  echo "Stopping services..."
  jobs -p | xargs -r kill || true
}
trap cleanup EXIT INT TERM

echo "Starting dummy backend..."
cd "$BACKEND_DIR"
python -m uvicorn main:app --reload --port 8000 &

echo "Starting frontend..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

npm run dev &

echo
echo "Dummy backend: http://localhost:8000"
echo "Frontend:      http://localhost:5173"
echo

wait