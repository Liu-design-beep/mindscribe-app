#!/bin/bash
# 后端构建脚本 - 用于 Render 部署

set -e

echo "开始构建后端..."

# 进入后端目录
cd app/web || exit 1

# 检查 Python 版本
echo "检查 Python 版本..."
python3 --version

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt

# 检查关键文件
echo "检查关键文件..."
if [ ! -f "api_server.py" ]; then
    echo "错误: 未找到 api_server.py 文件"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到 requirements.txt 文件"
    exit 1
fi

# 验证依赖安装
echo "验证依赖安装..."
python3 -c "import fastapi; import uvicorn; import dashscope; print('✅ 所有依赖已安装')"

echo "后端构建完成！"

