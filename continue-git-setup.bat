@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo 继续 Git 仓库设置
echo ========================================
echo.

REM 检查 Git 用户信息
git config --global user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [需要配置] Git 用户信息未设置
    echo 请先运行 configure-git-user.bat 配置用户信息
    pause
    exit /b 1
)

echo [步骤 1] 检查 Git 状态...
git status
echo.

echo [步骤 2] 提交代码...
git commit -m "Initial commit: 灵辑应用 - 前后端分离架构"
if %errorlevel% neq 0 (
    echo [错误] 提交失败
    pause
    exit /b 1
)
echo ✓ 代码提交成功
echo.

echo [步骤 3] 重命名分支为 main...
git branch -M main
echo ✓ 分支已重命名为 main
echo.

echo [步骤 4] 添加远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/Liu-design-beep/mindscribe-app.git
if %errorlevel% neq 0 (
    echo [错误] 添加远程仓库失败
    pause
    exit /b 1
)
echo ✓ 远程仓库已添加
git remote -v
echo.

echo [步骤 5] 准备推送到 GitHub...
echo.
echo ========================================
echo 重要提示：
echo ========================================
echo 推送时需要 GitHub 认证：
echo - 用户名：您的 GitHub 用户名
echo - 密码：使用 Personal Access Token（不是密码）
echo.
echo 生成 Token: GitHub - Settings - Developer settings - Personal access tokens
echo.
echo ========================================
echo.
echo 是否现在推送代码到 GitHub? (Y/N)
set /p push_confirm=
if /i "%push_confirm%"=="Y" (
    echo.
    echo [步骤 6] 推送代码到 GitHub...
    git push -u origin main
    if %errorlevel% neq 0 (
        echo.
        echo [错误] 推送失败
        echo 可能的原因：
        echo 1. 未配置 GitHub 认证
        echo 2. 远程仓库已存在内容（需要先拉取）
        echo 3. 网络连接问题
        echo.
        echo 如果远程仓库已有内容，请先执行：
        echo   git pull origin main --allow-unrelated-histories
        echo   git push -u origin main
    ) else (
        echo.
        echo ✓✓✓ 代码推送成功！✓✓✓
        echo 请在 GitHub 上查看: https://github.com/Liu-design-beep/mindscribe-app
    )
) else (
    echo.
    echo 已跳过推送步骤
    echo 您可以稍后手动执行: git push -u origin main
)

echo.
echo ========================================
echo 完成！
echo ========================================
pause

