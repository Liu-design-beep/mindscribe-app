# PowerShell 脚本：打开本地网页

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "正在打开灵辑网页..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendPath = Join-Path $scriptPath "frontend"
$htmlFile = Join-Path $frontendPath "index.html"

# 检查文件是否存在
if (Test-Path $htmlFile) {
    Write-Host "正在打开: $htmlFile" -ForegroundColor Green
    Start-Process $htmlFile
    Write-Host ""
    Write-Host "网页已在浏览器中打开！" -ForegroundColor Green
} else {
    Write-Host "错误：找不到 index.html 文件！" -ForegroundColor Red
    Write-Host "路径: $htmlFile" -ForegroundColor Red
}

Write-Host ""
Write-Host "提示：" -ForegroundColor Yellow
Write-Host "- 如果后端API在本地运行，请先启动后端服务器" -ForegroundColor Yellow
Write-Host "- 默认API地址：https://mindscribe-api-8zop.onrender.com" -ForegroundColor Yellow
Write-Host "- 如需使用本地API，请修改 frontend/app.js 中的 API_CONFIG.baseURL" -ForegroundColor Yellow
Write-Host ""
Read-Host "按 Enter 键退出"

