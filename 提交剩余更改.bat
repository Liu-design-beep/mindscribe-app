@echo off
cd /d "%~dp0"
git add .
git commit -m "Update: 清理临时文件并添加推送脚本"
git push
pause

