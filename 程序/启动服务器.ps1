# 灵辑 API 服务器启动脚本 (PowerShell)
# 使用方法：右键点击此文件，选择"使用 PowerShell 运行"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "灵辑 API 服务器启动中..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 检查Python是否安装
Write-Host "[检查] 正在检查Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[成功] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未检测到Python，请先安装Python 3.8+" -ForegroundColor Red
    Write-Host "请访问 https://www.python.org/ 下载安装Python" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

# 检查依赖是否安装
Write-Host "[检查] 正在检查依赖包..." -ForegroundColor Yellow
try {
    python -c "import fastapi" 2>&1 | Out-Null
    Write-Host "[成功] 依赖包已安装" -ForegroundColor Green
} catch {
    Write-Host "[提示] 检测到缺少依赖包，正在安装..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 依赖包安装失败，请手动运行: pip install -r requirements.txt" -ForegroundColor Red
        Read-Host "按 Enter 键退出"
        exit 1
    }
}

Write-Host "[启动] 正在启动API服务器..." -ForegroundColor Green
Write-Host "[提示] 使用 web/api_server.py (新版本，包含完整功能)" -ForegroundColor Yellow
Write-Host ""
Write-Host "API文档地址: http://127.0.0.1:8001/docs" -ForegroundColor Cyan
Write-Host "API根路径: http://127.0.0.1:8001/" -ForegroundColor Cyan
Write-Host "聊天接口: http://127.0.0.1:8001/api/chat" -ForegroundColor Cyan
Write-Host "文档列表: http://127.0.0.1:8001/api/documents" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 启动服务器（使用 web/api_server.py 新版本）
python -m uvicorn web.api_server:app --host 0.0.0.0 --port 8001

Read-Host "按 Enter 键退出"


