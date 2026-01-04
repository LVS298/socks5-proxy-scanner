#!/usr/bin/env python3
"""
SOCKS5 Proxy Scanner
自动化SOCKS5代理扫描与验证工具
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"
__description__ = "自动化SOCKS5代理扫描与验证工具"

# 导出主要模块
from .main import main
from .scanner import Socks5Scanner
from .validator import ProxyValidator
from .utils import (
    Color,
    Timer,
    PerformanceMonitor,
    is_valid_ip,
    is_valid_port,
    parse_proxy,
    format_proxy,
    load_proxy_file,
    save_proxy_file,
    check_internet_connection,
    format_file_size,
    format_time,
    create_timestamp,
    ensure_dir,
    safe_json_dump,
    safe_json_load,
    retry_on_failure,
    print_table,
    validate_url,
    extract_domain,
)

__all__ = [
    # 主模块
    "main",
    "Socks5Scanner",
    "ProxyValidator",
    
    # 工具类和函数
    "Color",
    "Timer",
    "PerformanceMonitor",
    
    # 网络工具
    "is_valid_ip",
    "is_valid_port",
    "parse_proxy",
    "format_proxy",
    "validate_url",
    "extract_domain",
    
    # 文件工具
    "load_proxy_file",
    "save_proxy_file",
    "ensure_dir",
    "safe_json_dump",
    "safe_json_load",
    
    # 格式工具
    "format_file_size",
    "format_time",
    "create_timestamp",
    "print_table",
    
    # 网络工具
    "check_internet_connection",
    
    # 装饰器
    "retry_on_failure",
]

# 包初始化时打印欢迎信息（可选）
def _print_welcome():
    import sys
    if '--version' in sys.argv or '-V' in sys.argv:
        print(f"SOCKS5 Proxy Scanner v{__version__}")
        sys.exit(0)
    
    if '--help' in sys.argv or '-h' in sys.argv:
        from .main import get_help_text
        print(get_help_text())
        sys.exit(0)

# 自动导入检查
try:
    import requests
    import yaml
    REQUIRED_MODULES = True
except ImportError as e:
    print(f"警告: 缺少依赖模块 {e}")
    print("请运行: pip install -r requirements.txt")
    REQUIRED_MODULES = False

# 版本兼容性检查
import sys
if sys.version_info < (3, 7):
    print("错误: 需要 Python 3.7 或更高版本")
    sys.exit(1)

# 导出包信息
PACKAGE_INFO = {
    'name': 'socks5-proxy-scanner',
    'version': __version__,
    'author': __author__,
    'license': __license__,
    'python_requires': '>=3.7',
    'dependencies': ['requests>=2.28.0', 'PyYAML>=6.0'],
}

def get_info():
    """获取包信息"""
    return PACKAGE_INFO.copy()

def check_dependencies():
    """检查依赖是否安装"""
    missing = []
    try:
        import requests
    except ImportError:
        missing.append('requests')
    
    try:
        import yaml
    except ImportError:
        missing.append('PyYAML')
    
    return missing

# 包初始化时执行
if __name__ != "__main__":
    _print_welcome()