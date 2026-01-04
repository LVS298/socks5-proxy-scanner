cat > README.md << 'EOF'
# 🔍 SOCKS5 Proxy Scanner

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-OpenSource-purple.svg)](https://github.com)

一个自动化扫描、验证和分类SOCKS5代理的工具，特别适用于内网源访问。

## ✨ 功能特性

- ✅ **多源扫描**：支持免费代理源
- ✅ **智能验证**：SOCKS5连接性测试 + 内网源访问测试
- ✅ **自动分类**：按有效性、省份、运营商分类
- ✅ **多线程**：快速扫描验证，支持高并发
- ✅ **安全可靠**：API密钥通过环境变量管理
- ✅ **简单易用**：一键运行，开箱即用

## 🚀 快速开始

### 安装依赖
```bash
# 安装Python依赖
pip install requests pyyaml
