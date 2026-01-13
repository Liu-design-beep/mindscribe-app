#!/bin/bash

# 确保输出目录存在
# Cloudflare 配置的输出目录是 app/frontend
mkdir -p app/frontend
mkdir -p app/frontend/static

# 复制前端文件 (HTML, CSS, JS)
# 从 app/web/frontend 复制到 app/frontend
echo "Copying frontend files..."
if [ -d "app/web/frontend" ]; then
    cp -r app/web/frontend/* app/frontend/
else
    echo "Warning: app/web/frontend directory not found!"
fi

# 复制静态资源 (图片, 视频)
# 从 app/web/static 复制到 app/frontend/static
# 这样前端代码中的 /static/portfolio/... 路径就能正确匹配到 app/frontend/static/portfolio/...
echo "Copying static assets..."
if [ -d "app/web/static" ]; then
    cp -r app/web/static/* app/frontend/static/
else
    echo "Warning: app/web/static directory not found!"
fi

echo "Build complete! Contents of app/frontend:"
ls -R app/frontend
