# 灵辑项目 - Git 仓库初始化脚本 (PowerShell)
# 编码: UTF-8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "灵辑项目 - Git 仓库初始化脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否安装
$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitPath) {
    Write-Host "[错误] 未检测到 Git，请先安装 Git for Windows" -ForegroundColor Red
    Write-Host "下载地址: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

# 进入脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "[步骤 1] 当前目录: $scriptDir" -ForegroundColor Green
Write-Host ""

# 初始化 Git 仓库
Write-Host "[步骤 2] 初始化 Git 仓库..." -ForegroundColor Cyan
if (Test-Path .git) {
    Write-Host "Git 仓库已存在，跳过初始化" -ForegroundColor Yellow
} else {
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] Git 初始化失败" -ForegroundColor Red
        Read-Host "按 Enter 键退出"
        exit 1
    }
    Write-Host "✓ Git 仓库初始化成功" -ForegroundColor Green
}
Write-Host ""

# 配置安全目录
Write-Host "[步骤 2.5] 配置 Git 安全目录..." -ForegroundColor Cyan
$currentDir = (Get-Location).Path
# 将路径中的反斜杠替换为正斜杠（Git 需要）
$currentDir = $currentDir -replace '\\', '/'
git config --global --add safe.directory $currentDir
if ($LASTEXITCODE -ne 0) {
    Write-Host "[警告] 配置安全目录失败，继续尝试..." -ForegroundColor Yellow
} else {
    Write-Host "✓ 安全目录配置成功" -ForegroundColor Green
}
Write-Host ""

# 检查状态
Write-Host "[步骤 3] 检查 Git 状态..." -ForegroundColor Cyan
git status
Write-Host ""

# 添加文件
Write-Host "[步骤 4] 添加所有文件到暂存区..." -ForegroundColor Cyan
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 添加文件失败" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}
Write-Host "✓ 文件已添加到暂存区" -ForegroundColor Green
Write-Host ""

# 提交代码
Write-Host "[步骤 5] 提交代码..." -ForegroundColor Cyan
git commit -m "Initial commit: 灵辑应用 - 前后端分离架构"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[警告] 提交失败，可能是没有文件需要提交或未配置用户信息" -ForegroundColor Yellow
    Write-Host "请先配置 Git 用户信息：" -ForegroundColor Yellow
    Write-Host "  git config --global user.name `"Your Name`"" -ForegroundColor Yellow
    Write-Host "  git config --global user.email `"your.email@example.com`"" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}
Write-Host "✓ 代码提交成功" -ForegroundColor Green
Write-Host ""

# 重命名分支
Write-Host "[步骤 6] 重命名分支为 main..." -ForegroundColor Cyan
git branch -M main
Write-Host "✓ 分支已重命名为 main" -ForegroundColor Green
Write-Host ""

# 添加远程仓库
Write-Host "[步骤 7] 添加远程仓库..." -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin https://github.com/Liu-design-beep/mindscribe-app.git
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 添加远程仓库失败" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}
Write-Host "✓ 远程仓库已添加" -ForegroundColor Green
git remote -v
Write-Host ""

# 提示信息
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "重要提示：" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. 请确保已配置 Git 用户信息：" -ForegroundColor Yellow
Write-Host "   git config --global user.name `"Your Name`"" -ForegroundColor White
Write-Host "   git config --global user.email `"your.email@example.com`"" -ForegroundColor White
Write-Host ""
Write-Host "2. 请确保已配置 GitHub 认证：" -ForegroundColor Yellow
Write-Host "   - 使用 Personal Access Token (推荐)" -ForegroundColor White
Write-Host "   - 或使用 SSH 密钥" -ForegroundColor White
Write-Host ""
Write-Host "3. 推送命令：" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor White
Write-Host ""

# 询问是否推送
$pushConfirm = Read-Host "是否现在推送代码到 GitHub? (Y/N)"
if ($pushConfirm -eq "Y" -or $pushConfirm -eq "y") {
    Write-Host ""
    Write-Host "[步骤 8] 推送代码到 GitHub..." -ForegroundColor Cyan
    git push -u origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[错误] 推送失败" -ForegroundColor Red
        Write-Host "可能的原因：" -ForegroundColor Yellow
        Write-Host "1. 未配置 GitHub 认证" -ForegroundColor Yellow
        Write-Host "2. 远程仓库已存在内容（需要先拉取）" -ForegroundColor Yellow
        Write-Host "3. 网络连接问题" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "如果远程仓库已有内容，请先执行：" -ForegroundColor Yellow
        Write-Host "  git pull origin main --allow-unrelated-histories" -ForegroundColor White
        Write-Host "  git push -u origin main" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "✓✓✓ 代码推送成功！✓✓✓" -ForegroundColor Green
        Write-Host "请在 GitHub 上查看: https://github.com/Liu-design-beep/mindscribe-app" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "已跳过推送步骤" -ForegroundColor Yellow
    Write-Host "您可以稍后手动执行: git push -u origin main" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "初始化完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "按 Enter 键退出"

