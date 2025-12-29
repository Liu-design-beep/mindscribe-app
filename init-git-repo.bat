@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo 灵辑项目 - Git 仓库初始化脚本
echo ========================================
echo.

REM 检查 Git 是否安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git，请先安装 Git for Windows
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [步骤 1] 检查当前目录...
cd /d "%~dp0"
echo 当前目录: %CD%
echo.

echo [步骤 2] 初始化 Git 仓库...
if exist .git (
    echo Git 仓库已存在，跳过初始化
) else (
    git init
    if %errorlevel% neq 0 (
        echo [错误] Git 初始化失败
        pause
        exit /b 1
    )
    echo ✓ Git 仓库初始化成功
)
echo.

echo [步骤 2.5] 配置 Git 安全目录...
REM 获取当前目录的完整路径
set "CURRENT_DIR=%CD%"
REM 将路径中的反斜杠替换为正斜杠（Git 需要）
set "CURRENT_DIR=%CURRENT_DIR:\=/%"
git config --global --add safe.directory "%CURRENT_DIR%"
if %errorlevel% neq 0 (
    echo [警告] 配置安全目录失败，继续尝试...
) else (
    echo ✓ 安全目录配置成功
)
echo.

echo [步骤 3] 检查 Git 状态...
git status
echo.

echo [步骤 4] 添加所有文件到暂存区...
git add .
if %errorlevel% neq 0 (
    echo [错误] 添加文件失败
    pause
    exit /b 1
)
echo ✓ 文件已添加到暂存区
echo.

echo [步骤 5] 检查 Git 用户配置...
git config --global user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [需要配置] Git 用户信息未设置
    echo.
    echo 请输入您的姓名（用于 Git 提交记录）:
    set /p git_name=
    if not "!git_name!"=="" (
        git config --global user.name "!git_name!"
        echo ✓ 用户名已设置: !git_name!
    )
    echo.
    echo 请输入您的邮箱（用于 Git 提交记录）:
    set /p git_email=
    if not "!git_email!"=="" (
        git config --global user.email "!git_email!"
        echo ✓ 邮箱已设置: !git_email!
    )
    echo.
)

REM 再次检查是否配置成功
git config --global user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Git 用户信息未配置，无法提交
    echo.
    echo 请手动执行以下命令配置：
    echo   git config --global user.name "Your Name"
    echo   git config --global user.email "your.email@example.com"
    echo.
    echo 然后重新运行此脚本
    pause
    exit /b 1
)

echo [步骤 6] 提交代码...
git commit -m "Initial commit: 灵辑应用 - 前后端分离架构"
if %errorlevel% neq 0 (
    echo [警告] 提交失败
    echo 可能的原因：
    echo 1. 没有文件需要提交
    echo 2. Git 用户信息未正确配置
    echo.
    pause
    exit /b 1
)
echo ✓ 代码提交成功
echo.

echo [步骤 7] 重命名分支为 main...
git branch -M main
echo ✓ 分支已重命名为 main
echo.

echo [步骤 8] 添加远程仓库...
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

echo [步骤 9] 准备推送到 GitHub...
echo.
echo ========================================
echo 重要提示：
echo ========================================
echo 1. 请确保已配置 Git 用户信息：
echo    git config --global user.name "Your Name"
echo    git config --global user.email "your.email@example.com"
echo.
echo 2. 请确保已配置 GitHub 认证：
echo    使用 Personal Access Token (推荐)
echo    或使用 SSH 密钥
echo.
echo 3. 推送命令：
echo    git push -u origin main
echo.
echo ========================================
echo.
echo 是否现在推送代码到 GitHub? (Y/N)
set /p push_confirm=
if /i "%push_confirm%"=="Y" (
    echo.
    echo [步骤 10] 推送代码到 GitHub...
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
    echo 您可以稍后手动执行推送命令
)

echo.
echo ========================================
echo 初始化完成！
echo ========================================
pause

