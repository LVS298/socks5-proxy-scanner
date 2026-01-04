# SOCKS5代理扫描器使用文档

## 目录
- [快速开始](#快速开始)
- [安装指南](#安装指南)
- [配置文件](#配置文件)
- [命令行参数](#命令行参数)
- [使用示例](#使用示例)
- [输出文件](#输出文件)
- [API密钥配置](#api密钥配置)
- [故障排除](#故障排除)
- [高级用法](#高级用法)
- [常见问题](#常见问题)

## 快速开始

### 基本使用
```bash
# 克隆仓库
git clone https://github.com/yourusername/socks5-proxy-scanner.git
cd socks5-proxy-scanner

# 运行安装脚本
./scripts/install.sh

# 快速扫描
python src/main.py --mode free --threads 20
