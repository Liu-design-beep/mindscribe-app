@echo off
REM 设置UTF-8编码
chcp 65001 >nul

echo ========================================
echo    停止所有服务器
echo ========================================
echo.

REM 查找并关闭占用8000端口的进程（后端）
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo 正在停止后端服务器 (PID: %%a)...
    taskkill /PID %%a /F >nul 2>&1
)

REM 查找并关闭占用8080端口的进程（前端）
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    echo 正在停止前端服务器 (PID: %%a)...
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo 所有服务器已停止！
echo.
pause




