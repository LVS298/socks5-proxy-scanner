#!/usr/bin/env python3
"""
工具函数模块
提供通用的辅助函数和工具类
"""

import os
import sys
import json
import time
import socket
import ipaddress
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import requests

# 设置日志
logger = logging.getLogger(__name__)


class Color:
    """控制台颜色工具类"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @classmethod
    def red(cls, text: str) -> str:
        return f"{cls.RED}{text}{cls.END}"
    
    @classmethod
    def green(cls, text: str) -> str:
        return f"{cls.GREEN}{text}{cls.END}"
    
    @classmethod
    def yellow(cls, text: str) -> str:
        return f"{cls.YELLOW}{text}{cls.END}"
    
    @classmethod
    def blue(cls, text: str) -> str:
        return f"{cls.BLUE}{text}{cls.END}"
    
    @classmethod
    def bold(cls, text: str) -> str:
        return f"{cls.BOLD}{text}{cls.END}"
    
    @classmethod
    def progress_bar(cls, current: int, total: int, length: int = 40) -> str:
        """生成进度条"""
        percent = current / total
        filled = int(length * percent)
        bar = '█' * filled + '░' * (length - filled)
        percent_text = f"{percent*100:6.2f}%"
        return f"[{bar}] {percent_text} ({current}/{total})"


def is_valid_ip(ip_str: str) -> bool:
    """验证IP地址是否有效"""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def is_valid_port(port: Union[int, str]) -> bool:
    """验证端口是否有效"""
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (ValueError, TypeError):
        return False


def parse_proxy(proxy_str: str) -> Tuple[Optional[str], Optional[int]]:
    """
    解析代理字符串
    
    Args:
        proxy_str: 代理字符串，格式如 "ip:port" 或 "socks5://ip:port"
    
    Returns:
        (ip, port) 元组，如果解析失败返回 (None, None)
    """
    try:
        # 移除协议前缀
        if '://' in proxy_str:
            proxy_str = proxy_str.split('://')[1]
        
        # 分割IP和端口
        if ':' in proxy_str:
            ip, port_str = proxy_str.split(':', 1)
            port = int(port_str)
            
            if is_valid_ip(ip) and is_valid_port(port):
                return ip, port
    except (ValueError, AttributeError):
        pass
    
    return None, None


def format_proxy(ip: str, port: int, protocol: str = 'socks5') -> str:
    """格式化代理字符串"""
    return f"{protocol}://{ip}:{port}"


def load_proxy_file(file_path: str) -> List[str]:
    """从文件加载代理列表"""
    proxies = []
    
    if not os.path.exists(file_path):
        logger.error(f"代理文件不存在: {file_path}")
        return proxies
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxies.append(line)
        
        logger.info(f"从文件加载了 {len(proxies)} 个代理: {file_path}")
    except Exception as e:
        logger.error(f"加载代理文件失败 {file_path}: {e}")
    
    return proxies


def save_proxy_file(proxies: List[str], file_path: str, 
                   header: str = "", mode: str = 'w') -> bool:
    """保存代理列表到文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, mode, encoding='utf-8') as f:
            if header:
                f.write(header + '\n')
            for proxy in proxies:
                f.write(proxy + '\n')
        
        logger.info(f"保存了 {len(proxies)} 个代理到: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存代理文件失败 {file_path}: {e}")
        return False


def check_internet_connection() -> bool:
    """检查网络连接"""
    test_urls = [
        'https://www.google.com',
        'https://www.baidu.com',
        'https://cloudflare.com'
    ]
    
    for url in test_urls:
        try:
            response = requests.head(url, timeout=5, verify=False)
            if response.status_code < 500:
                return True
        except:
            continue
    
    return False


def get_ip_info(ip: str) -> Dict[str, Any]:
    """获取IP地址信息（地理位置、运营商等）"""
    try:
        # 使用ip-api.com获取IP信息（免费，有限制）
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'countryCode': data.get('countryCode', ''),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'org': data.get('org', 'Unknown'),
                    'as': data.get('as', ''),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                }
    except:
        pass
    
    return {}


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_time(seconds: float) -> str:
    """格式化时间"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}小时"
    else:
        days = seconds / 86400
        return f"{days:.1f}天"


def create_timestamp() -> str:
    """创建时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir(directory: str) -> bool:
    """确保目录存在"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败 {directory}: {e}")
        return False


def safe_json_dump(data: Any, file_path: str, indent: int = 2) -> bool:
    """安全地将数据保存为JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败 {file_path}: {e}")
        return False


def safe_json_load(file_path: str) -> Optional[Any]:
    """安全地加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载JSON文件失败 {file_path}: {e}")
        return None


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.debug(f"重试 {attempt + 1}/{max_retries}: {func.__name__} 失败: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
            
            logger.error(f"所有重试失败: {func.__name__}")
            raise last_exception
        return wrapper
    return decorator


class Timer:
    """计时器上下文管理器"""
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
    
    def get_elapsed(self) -> float:
        return getattr(self, 'elapsed', 0)


def print_table(data: List[List[str]], headers: List[str] = None,
               col_widths: List[int] = None, title: str = ""):
    """打印表格"""
    if not data:
        return
    
    # 自动计算列宽
    if col_widths is None:
        col_widths = []
        if headers:
            for i, header in enumerate(headers):
                max_len = len(header)
                for row in data:
                    if i < len(row):
                        max_len = max(max_len, len(str(row[i])))
                col_widths.append(max_len + 2)
        else:
            for i in range(len(data[0])):
                max_len = max(len(str(row[i])) for row in data)
                col_widths.append(max_len + 2)
    
    # 打印标题
    if title:
        print(f"\n{Color.bold(Color.blue(title))}")
    
    # 打印表头
    if headers:
        header_line = "│"
        for i, header in enumerate(headers):
            header_line += f" {header:<{col_widths[i]}} │"
        print("┌" + "─" * (sum(col_widths) + len(headers) * 3 - 1) + "┐")
        print(header_line)
        print("├" + "─" * (sum(col_widths) + len(headers) * 3 - 1) + "┤")
    
    # 打印数据行
    for row in data:
        row_line = "│"
        for i, cell in enumerate(row):
            if i < len(col_widths):
                row_line += f" {str(cell):<{col_widths[i]}} │"
        print(row_line)
    
    # 打印底部边框
    print("└" + "─" * (sum(col_widths) + len(headers) * 3 - 1) + "┘")


def get_user_input(prompt: str, default: str = "", 
                  valid_options: List[str] = None) -> str:
    """获取用户输入"""
    while True:
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        user_input = input(full_prompt).strip()
        
        if not user_input and default:
            return default
        
        if valid_options and user_input not in valid_options:
            print(f"无效输入，请从 {valid_options} 中选择")
            continue
        
        return user_input


def validate_url(url: str) -> bool:
    """验证URL是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_domain(url: str) -> str:
    """从URL提取域名"""
    try:
        return urlparse(url).netloc
    except:
        return ""


def get_file_encoding(file_path: str) -> str:
    """检测文件编码"""
    import chardet
    
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024)
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8')
    except:
        return 'utf-8'


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    def start_operation(self, name: str):
        """开始记录操作"""
        self.metrics[name] = {
            'start': time.time(),
            'end': None,
            'duration': None
        }
    
    def end_operation(self, name: str):
        """结束记录操作"""
        if name in self.metrics:
            self.metrics[name]['end'] = time.time()
            self.metrics[name]['duration'] = (
                self.metrics[name]['end'] - self.metrics[name]['start']
            )
    
    def get_report(self) -> Dict[str, float]:
        """获取性能报告"""
        report = {}
        for name, data in self.metrics.items():
            if data['duration'] is not None:
                report[name] = data['duration']
        
        report['total'] = time.time() - self.start_time
        return report
    
    def print_report(self):
        """打印性能报告"""
        report = self.get_report()
        print(f"\n{Color.bold('性能报告:')}")
        for name, duration in report.items():
            if name != 'total':
                print(f"  {name}: {duration:.2f}秒")
        print(f"  总计: {report.get('total', 0):.2f}秒")


# 测试函数
if __name__ == "__main__":
    # 测试工具函数
    print("测试工具函数:")
    print(f"有效IP: {is_valid_ip('8.8.8.8')}")
    print(f"无效IP: {is_valid_ip('256.256.256.256')}")
    print(f"有效端口: {is_valid_port(8080)}")
    print(f"无效端口: {is_valid_port(999999)}")
    
    ip, port = parse_proxy("socks5://127.0.0.1:1080")
    print(f"解析代理: {ip}:{port}")
    
    print(f"文件大小: {format_file_size(1024*1024*5)}")
    print(f"格式化时间: {format_time(3661)}")
    
    # 测试表格打印
    test_data = [
        ["Alice", "25", "Engineer"],
        ["Bob", "30", "Designer"],
        ["Charlie", "28", "Developer"]
    ]
    test_headers = ["Name", "Age", "Job"]
    print_table(test_data, test_headers, title="测试表格")
