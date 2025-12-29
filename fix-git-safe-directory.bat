@echo off
chcp 65001 >nul
echo 修复 Git 安全目录配置...
echo.

REM 获取当前目录并转换为 Git 需要的格式
cd /d "%~dp0"
set "CURRENT_DIR=%CD%"
set "CURRENT_DIR=%CURRENT_DIR:\=/%"

echo 当前目录: %CURRENT_DIR%
echo.

echo 正在添加安全目录配置...
git config --global --add safe.directory "%CURRENT_DIR%"

if %errorlevel% equ 0 (
    echo.
    echo ✓ 安全目录配置成功！
    echo.
    echo 现在可以继续执行 Git 操作了。
    echo 您可以重新运行 init-git-repo.bat 或手动执行：
    echo   git add .
    echo   git commit -m "Initial commit: 灵辑应用 - 前后端分离架构"
    echo   git branch -M main
    echo   git remote add origin https://github.com/Liu-design-beep/mindscribe-app.git
    echo   git push -u origin main
) else (
    echo.
    echo [错误] 配置失败，请检查 Git 是否已安装
)

echo.
pause

