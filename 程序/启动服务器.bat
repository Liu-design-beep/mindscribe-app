@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting Smart Clip API Server...
echo Using web/api_server.py (new version)
echo.
python -m uvicorn web.api_server:app --host 0.0.0.0 --port 8001
pause

