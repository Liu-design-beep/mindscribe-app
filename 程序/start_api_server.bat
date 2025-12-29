@echo off
chcp 65001 >nul
REM 灵辑 API 服务器启动脚本 (Windows)
echo ========================================
echo 灵辑 API 服务器启动中...
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 请访问 https://www.python.org/ 下载安装Python
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo [检查] 正在检查依赖包...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [提示] 检测到缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [启动] 正在启动API服务器...
echo.
echo API文档地址: http://127.0.0.1:8000/docs
echo API根路径: http://127.0.0.1:8000/
echo 聊天接口: http://127.0.0.1:8000/api/chat
echo 文档列表: http://127.0.0.1:8000/api/documents
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

REM 启动服务器
python api_server.py

pause

