#!/bin/bash

echo "===== Telegram翻译机器人 Python 3.11 环境设置 ====="
echo

# 检查Python 3.11是否已安装
if python3 -c "import platform; import sys; sys.exit(0 if platform.python_version().startswith('3.11') else 1)" &> /dev/null; then
    echo "[√] 已检测到Python 3.11版本"
else
    echo "[×] 未检测到Python 3.11版本"
    echo
    echo "请安装Python 3.11:"
    echo "- Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
    echo "- macOS: brew install python@3.11"
    echo "- 其他系统请参考: https://www.python.org/downloads/release/python-3118/"
    echo
    exit 1
fi

# 创建虚拟环境
echo
echo "正在创建Python 3.11虚拟环境..."
if [ -d "venv" ]; then
    echo "[!] 检测到已存在的虚拟环境，将重新创建"
    rm -rf venv
fi
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[×] 创建虚拟环境失败"
    exit 1
fi
echo "[√] 虚拟环境创建成功"

# 激活虚拟环境并安装依赖
echo
echo "正在安装项目依赖..."
source venv/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[×] 安装依赖失败"
    exit 1
fi
echo "[√] 依赖安装成功"

echo
echo "===== 设置完成 ====="
echo
echo "您现在可以通过以下命令启动翻译机器人:"
echo
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 运行机器人: python src/simple.py"
echo
echo "建议使用simple.py版本，兼容性最好" 