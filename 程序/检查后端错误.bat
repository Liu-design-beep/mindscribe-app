@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo    检查后端服务器状态
echo ========================================
echo.

echo [1] 检查端口占用情况...
netstat -ano | findstr ":8000 :8080"
echo.

echo [2] 尝试停止现有服务器...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo 已停止现有服务器
echo.

echo [3] 重新启动后端服务器（显示详细日志）...
echo 请查看下方的错误信息！
echo.
python api_server.py
pause




