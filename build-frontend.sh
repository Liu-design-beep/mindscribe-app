#!/bin/bash
# 前端构建脚本 - 用于 Cloudflare Pages 部署

set -e

echo "开始构建前端..."

# 创建构建输出目录
DIST_DIR="dist"
mkdir -p "$DIST_DIR"

# 复制前端文件到构建目录
echo "复制前端文件..."
cp -r 程序/frontend/* "$DIST_DIR/"

# 检查是否有需要处理的文件
if [ ! -f "$DIST_DIR/index.html" ]; then
    echo "错误: 未找到 index.html 文件"
    exit 1
fi

# 如果前端代码中有硬编码的 API URL，可以在这里进行替换
# 例如：将 localhost:8000 替换为环境变量中的后端 URL
if [ -n "$VITE_API_URL" ]; then
    echo "替换 API URL 为: $VITE_API_URL"
    find "$DIST_DIR" -type f \( -name "*.js" -o -name "*.html" \) -exec sed -i "s|http://localhost:8000|$VITE_API_URL|g" {} +
fi

echo "前端构建完成！"
echo "构建输出目录: $DIST_DIR"
ls -la "$DIST_DIR"

