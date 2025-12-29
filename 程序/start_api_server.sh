#!/bin/bash
# 灵辑 API 服务器启动脚本 (Linux/Mac)

echo "========================================"
echo "灵辑 API 服务器启动中..."
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查依赖是否安装
echo "[检查] 正在检查依赖包..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "[提示] 检测到缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖包安装失败，请手动运行: pip3 install -r requirements.txt"
        exit 1
    fi
fi

echo "[启动] 正在启动API服务器..."
echo ""
echo "API文档地址: http://127.0.0.1:8000/docs"
echo "API根路径: http://127.0.0.1:8000/"
echo "聊天接口: http://127.0.0.1:8000/api/chat"
echo "文档列表: http://127.0.0.1:8000/api/documents"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================"
echo ""

# 启动服务器
python3 api_server.py

