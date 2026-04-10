@echo off
setlocal

set ROOT_DIR=%~dp0
set BACKEND_DIR=%ROOT_DIR%src\backend_dummy
set FRONTEND_DIR=%ROOT_DIR%src\frontend

echo Starting dummy backend...
cd /d "%BACKEND_DIR%"
start "backend" cmd /k python -m uvicorn main:app --reload --port 8000

echo Starting frontend...
cd /d "%FRONTEND_DIR%"

if not exist package.json (
    echo ERROR: package.json not found in %FRONTEND_DIR%
    pause
    exit /b 1
)

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

start "frontend" cmd /k npm run dev

echo.
echo Dummy backend: http://localhost:8000
echo Frontend:      http://localhost:5173
echo.