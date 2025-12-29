@echo off
chcp 65001 >nul
echo ========================================
echo 正在打开灵辑网页...
echo ========================================
echo.

REM 检查后端服务器是否在运行（检查8001端口）
echo [检查] 正在检查后端服务器状态...
netstat -an | findstr ":8001" | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到后端服务器在运行！
    echo.
    echo 提示：如果后端服务器未启动，网页功能将无法使用。
    echo 请确保已运行 "启动服务器.bat" 并看到 "Uvicorn running" 提示。
    echo.
    timeout /t 3 >nul
) else (
    echo [检查] 后端服务器正在运行 (端口 8001)
    echo.
)

cd /d "%~dp0frontend"

REM 使用Chrome打开并自动打开开发者工具（如果Chrome可用）
where chrome >nul 2>&1
if %errorlevel% == 0 (
    start chrome --auto-open-devtools-for-tabs "file:///%~dp0frontend\index.html"
    echo Chrome浏览器已打开，开发者工具应该自动显示
) else (
    REM 如果没有Chrome，尝试Edge
    where msedge >nul 2>&1
    if %errorlevel% == 0 (
        start msedge --auto-open-devtools-for-tabs "file:///%~dp0frontend\index.html"
        echo Edge浏览器已打开，开发者工具应该自动显示
    ) else (
        REM 如果都没有，使用默认浏览器
        start index.html
        echo.
        echo 提示：按F12可以打开开发者工具查看调试信息
    )
)

echo.
echo ========================================
echo 网页已在浏览器中打开！
echo ========================================
echo.
echo 【重要提示】如何查看错误信息：
echo.
echo 1. 如果开发者工具没有自动打开，请按 F12 键
echo 2. 在开发者工具中，点击 "Console"（控制台）标签页
echo 3. 红色的文字就是错误信息
echo 4. 白色的文字是正常的调试信息
echo.
echo 其他提示：
echo - 如果后端API在本地运行，请先启动后端服务器
echo - 默认API地址：https://mindscribe-api-8zop.onrender.com
echo - 如需使用本地API，请修改 frontend/app.js 中的 API_CONFIG.baseURL
echo.
pause

