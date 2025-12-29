@echo off
chcp 65001 >nul
echo ========================================
echo Git 用户信息配置
echo ========================================
echo.

echo 请输入您的姓名（用于 Git 提交记录）:
set /p git_name=
if "%git_name%"=="" (
    echo [错误] 姓名不能为空
    pause
    exit /b 1
)

echo.
echo 请输入您的邮箱（用于 Git 提交记录）:
set /p git_email=
if "%git_email%"=="" (
    echo [错误] 邮箱不能为空
    pause
    exit /b 1
)

echo.
echo 正在配置 Git 用户信息...
git config --global user.name "%git_name%"
git config --global user.email "%git_email%"

if %errorlevel% equ 0 (
    echo.
    echo ✓ Git 用户信息配置成功！
    echo.
    echo 用户名: %git_name%
    echo 邮箱: %git_email%
    echo.
    echo 现在可以继续执行 Git 操作了。
    echo 您可以重新运行 init-git-repo.bat 或手动执行：
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

