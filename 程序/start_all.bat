@echo off
REM 设置UTF-8编码
chcp 65001 >nul

REM 切换到脚本所在目录
cd /d "%~dp0"

echo ========================================
echo    启动智能剪贴板助手
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo [1/3] 正在启动后端服务器...
echo.
start "后端服务器 - 请勿关闭" cmd /k "python api_server.py"

REM 等待3秒让后端启动
timeout /t 3 /nobreak >nul

echo [2/3] 正在启动前端服务器...
echo.
start "前端服务器 - 请勿关闭" cmd /k "cd frontend && python -m http.server 8080"

REM 等待2秒让前端启动
timeout /t 2 /nobreak >nul

echo [3/3] 正在打开浏览器...
echo.
start http://localhost:8080

echo.
echo ========================================
echo    启动完成！
echo ========================================
echo.
echo 后端API地址: http://127.0.0.1:8000
echo 前端界面地址: http://localhost:8080
echo.
echo 重要提示：
echo - 不要关闭弹出的两个命令行窗口
echo - 如需停止服务，关闭那两个窗口即可
echo - 浏览器已自动打开前端界面
echo.
pause




