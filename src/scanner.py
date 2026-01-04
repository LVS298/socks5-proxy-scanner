import os
import sys
import time
import json
from typing import List, Dict, Optional
import requests
from .validator import ProxyValidator

class Socks5Scanner:
    """GitHub友好的SOCKS5扫描器"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # 从配置文件读取或使用默认值
        self.PROVINCES = config.get('provinces', [
            "北京", "上海", "广东", "浙江", "江苏", 
            "山东", "河南", "四川", "河北", "湖南"
        ])
        
        self.OPERATORS = config.get('operators', [
            "中国移动", "中国电信", "中国联通"
        ])
        
        # API配置（从环境变量获取）
        self.QUAKE_API_KEY = os.getenv('QUAKE_API_KEY', '')
        self.QUAKE_API_URL = "https://quake.360.net/api/v3/search/quake_service"
        
        # 免费代理源（GitHub公开源）
        self.FREE_PROXY_SOURCES = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5.txt",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all"
        ]
        
        self.validator = ProxyValidator(config)
        
    def _load_custom_sources(self) -> List[str]:
        """加载自定义源文件"""
        sources_file = self.config.get('sources_file', 'config/sources.txt')
        if os.path.exists(sources_file):
            with open(sources_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return []
    
    def scan_free_proxies(self) -> List[str]:
        """扫描免费代理源"""
        import concurrent.futures
        
        all_proxies = set()
        
        def fetch_source(url: str) -> List[str]:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                resp = requests.get(url, headers=headers, timeout=15, verify=False)
                if resp.status_code == 200:
                    proxies = []
                    for line in resp.text.split('\n'):
                        line = line.strip()
                        if ':' in line:
                            parts = line.split(':')
                            if len(parts) == 2 and parts[1].isdigit():
                                proxies.append(f"{parts[0]}:{parts[1]}")
                    return proxies
            except:
                pass
            return []
        
        print("正在从免费源收集代理...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_source, url): url 
                      for url in self.FREE_PROXY_SOURCES}
            
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    proxies = future.result()
                    if proxies:
                        print(f"  {url}: 收集到 {len(proxies)} 个代理")
                        all_proxies.update(proxies)
                except Exception as e:
                    print(f"  {url}: 收集失败 - {e}")
        
        return list(all_proxies)
    
    def scan_quake_proxies(self) -> List[Dict]:
        """使用360 Quake API扫描（需要API密钥）"""
        if not self.QUAKE_API_KEY:
            print("警告：未设置QUAKE_API_KEY环境变量，跳过Quake扫描")
            return []
        
        # 这里简化实现，实际需要调用Quake API
        print("Quake扫描需要有效的API密钥")
        return []
    
    def run_full_scan(self, max_workers: int = 20, 
                     mode: str = 'free',
                     output_dir: str = './results'):
        """运行完整扫描流程"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        print(f"\n开始扫描 ({mode}模式)")
        print("-" * 40)
        
        proxies = []
        
        # 根据模式选择扫描方式
        if mode in ['quake', 'both']:
            quake_results = self.scan_quake_proxies()
            proxies.extend(quake_results)
        
        if mode in ['free', 'both']:
            free_proxies = self.scan_free_proxies()
            proxies.extend([{'proxy': p, 'source': 'free'} for p in free_proxies])
        
        if not proxies:
            print("未找到任何代理")
            return
        
        print(f"\n总共收集到 {len(proxies)} 个代理")
        print("开始验证代理有效性...")
        
        # 验证代理
        results = self.validator.validate_proxies(
            proxies, 
            max_workers=max_workers
        )
        
        # 保存结果
        self.validator.save_results(
            results, 
            output_dir=output_dir,
            timestamp=timestamp
        )
        
        # 打印统计信息
        self._print_stats(results)
    
    def _print_stats(self, results: Dict):
        """打印统计信息"""
        print("\n" + "="*40)
        print("扫描统计:")
        print(f"总代理数: {results['stats']['total']}")
        print(f"有效代理: {results['stats']['valid']}")
        print(f"可用代理: {results['stats']['working']}")
        print(f"失败代理: {results['stats']['failed']}")
        print("="*40)