#!/usr/bin/env python3
"""
SOCKS5代理扫描器 - 安装配置文件
"""

from setuptools import setup, find_packages
import os
import re

# 读取版本信息
def get_version():
    """从 __init__.py 中读取版本号"""
    version_file = os.path.join(os.path.dirname(__file__), 'src', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if match:
            return match.group(1)
    return '0.1.0'


# 读取README
def read_readme():
    """读取README文件"""
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "SOCKS5代理扫描器 - 自动化代理扫描与验证工具"


# 读取依赖
def read_requirements():
    """读取requirements.txt文件"""
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []


setup(
    name="socks5-proxy-scanner",
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    description="自动化SOCKS5代理扫描与验证工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/socks5-proxy-scanner",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/socks5-proxy-scanner/issues",
        "Documentation": "https://github.com/yourusername/socks5-proxy-scanner/wiki",
        "Source Code": "https://github.com/yourusername/socks5-proxy-scanner",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Security",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "flake8>=4.0",
            "black>=22.0",
            "mypy>=0.9",
        ],
        "full": [
            "rich>=13.0",
            "colorama>=0.4.6",
            "tqdm>=4.65.0",
            "chardet>=5.1.0",
            "pyyaml>=6.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "socks5-scanner=main:main",
            "proxy-scan=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "../config/*.example.yaml",
            "../config/*.example.txt",
        ],
    },
    data_files=[
        ("config", [
            "config/config.example.yaml",
            "config/sources.example.txt",
        ]),
        ("docs", [
            "docs/usage.md",
        ]),
    ],
    scripts=[
        "scripts/run.sh",
        "scripts/install.sh",
    ],
    keywords=[
        "socks5",
        "proxy",
        "scanner",
        "validator",
        "iptv",
        "streaming",
        "network",
        "security",
        "automation",
    ],
    license="MIT",
    platforms=["any"],
    zip_safe=False,
)

# 创建 __init__.py 文件（如果不存在）
init_file = os.path.join(os.path.dirname(__file__), 'src', '__init__.py')
if not os.path.exists(init_file):
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write('''"""
SOCKS5 Proxy Scanner
自动化SOCKS5代理扫描与验证工具
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"

# 导出主要模块
from .main import main
from .scanner import Socks5Scanner
from .validator import ProxyValidator
from .utils import *

__all__ = [
    "main",
    "Socks5Scanner",
    "ProxyValidator",
    "Color",
    "Timer",
    "PerformanceMonitor",
]
''')

print(f"包配置完成，版本: {get_version()}")
