@echo off
setlocal

set ROOT_DIR=%~dp0
set FRONTEND_DIR=%ROOT_DIR%src\frontend

echo ===============================
echo Starting Backend (port 9000)...
echo ===============================
cd /d "%ROOT_DIR%"
start "backend" cmd /k uvicorn src.backend.main:app --reload --port 9000

echo ===============================
echo Starting MCP Server (port 8000)...
echo ===============================
cd /d "%ROOT_DIR%"
start "mcp_server" cmd /k uvicorn src.mcp_server.main:app --reload --port 8000

echo ===============================
echo Starting Frontend...
echo ===============================
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
echo ==========================================
echo Backend:    http://localhost:9000
echo MCP Server: http://localhost:8000
echo Frontend:   http://localhost:5173
echo ==========================================
echo.
pause