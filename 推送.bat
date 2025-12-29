@echo off
cd /d "%~dp0"
git add .gitignore
git commit -m "Merge remote and local: resolve .gitignore conflict"
git push -u origin main
pause

