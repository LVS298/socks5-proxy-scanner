#!/bin/bash
# Linux/macOS 运行脚本

# 设置环境变量
export QUAKE_API_KEY="${QUAKE_API_KEY:-}"
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# 创建必要目录
mkdir -p config results data

# 检查配置文件
if [ ! -f "config/config.yaml" ]; then
    echo "警告: 未找到配置文件"
    echo "请复制 config.example.yaml 并修改:"
    echo "  cp config/config.example.yaml config/config.yaml"
    read -p "是否使用默认配置继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 运行扫描器
python src/main.py "$@"