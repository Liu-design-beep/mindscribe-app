#!/bin/bash

# 创建输出目录
mkdir -p dist
mkdir -p dist/static

# 复制前端文件 (HTML, CSS, JS) 到根目录
# 注意：现在文件都在 app/web/frontend 下
cp -r app/web/frontend/* dist/

# 复制静态资源 (图片, 视频) 到 static 目录
# 注意：现在文件都在 app/web/static 下
cp -r app/web/static/* dist/static/

echo "Build complete! Contents of dist:"
ls -R dist
