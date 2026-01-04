#!/bin/bash
# 安装脚本

echo "安装 SOCKS5代理扫描器..."

# 创建虚拟环境（可选）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 设置配置文件
if [ ! -f "config/config.yaml" ] && [ -f "config/config.example.yaml" ]; then
    echo "创建配置文件..."
    cp config/config.example.yaml config/config.yaml
    echo "请编辑 config/config.yaml 配置测试源"
fi

# 设置运行权限
chmod +x scripts/run.sh
chmod +x scripts/install.sh

echo "安装完成！"
echo ""
echo "使用方法:"
echo "  ./scripts/run.sh --mode free --threads 20"
echo "  ./scripts/run.sh --test-only --proxy-file proxies.txt"
echo ""
echo "更多帮助: ./scripts/run.sh --help"
