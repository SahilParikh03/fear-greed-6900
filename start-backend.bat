@echo off
echo ===================================
echo Fear ^& Greed Index 6900 - Backend
echo ===================================
echo.
echo Starting FastAPI backend with Binance WebSocket...
echo.

cd /d "%~dp0"
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

pause
