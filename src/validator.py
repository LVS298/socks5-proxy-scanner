import concurrent.futures
import socket
import time
from typing import List, Dict
import requests
from urllib.parse import urlparse

class ProxyValidator:
    """代理验证器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.test_sources = config.get('test_sources', [])
        self.timeout = config.get('timeout', 5)
        
    def validate_proxies(self, proxies: List[Dict], 
                        max_workers: int = 20) -> Dict:
        """批量验证代理"""
        from concurrent.futures import ThreadPoolExecutor
        
        results = {
            'all': [],
            'valid': [],
            'working': [],
            'stats': {
                'total': len(proxies),
                'valid': 0,
                'working': 0,
                'failed': 0
            }
        }
        
        print(f"使用 {max_workers} 个线程进行验证...")
        
        # 第一步：验证SOCKS5连接性
        def test_connectivity(item: Dict) -> Dict:
            proxy = item['proxy']
            result = item.copy()
            
            if self._test_socks5(proxy):
                result['valid'] = True
                results['stats']['valid'] += 1
            else:
                result['valid'] = False
                results['stats']['failed'] += 1
            
            return result
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(test_connectivity, p) for p in proxies]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result['valid']:
                        results['valid'].append(result)
                except:
                    pass
        
        # 第二步：测试内网源访问
        if self.test_sources and results['valid']:
            print(f"测试 {len(results['valid'])} 个有效代理的内网访问能力...")
            
            def test_source_access(proxy_info: Dict) -> Dict:
                proxy = proxy_info['proxy']
                accessible_sources = []
                
                for source in self.test_sources:
                    if self._test_with_source(proxy, source):
                        accessible_sources.append(source)
                
                proxy_info['accessible_sources'] = accessible_sources
                if accessible_sources:
                    proxy_info['working'] = True
                    results['stats']['working'] += 1
                else:
                    proxy_info['working'] = False
                    results['stats']['failed'] += 1
                
                return proxy_info
            
            with ThreadPoolExecutor(max_workers=min(max_workers, 10)) as executor:
                futures = [executor.submit(test_source_access, p) 
                         for p in results['valid']]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        if result['working']:
                            results['working'].append(result)
                        results['all'].append(result)
                    except:
                        pass
        
        return results
    
    def _test_socks5(self, proxy: str, timeout: int = 3) -> bool:
        """测试SOCKS5代理连接"""
        try:
            ip, port = proxy.split(':')
            port = int(port)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            
            # SOCKS5握手
            sock.send(b'\x05\x01\x00')
            response = sock.recv(2)
            
            if response == b'\x05\x00':
                sock.close()
                return True
        except:
            pass
        return False
    
    def _test_with_source(self, proxy: str, source_url: str) -> bool:
        """测试代理是否能访问源"""
        try:
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            
            # 仅请求头部，节省带宽
            resp = requests.head(source_url, 
                               proxies=proxies, 
                               timeout=10,
                               verify=False,
                               allow_redirects=True)
            
            if resp.status_code in [200, 302, 307]:
                return True
        except:
            pass
        return False
    
    def save_results(self, results: Dict, output_dir: str, timestamp: str):
        """保存结果到文件"""
        import os
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存JSON格式
        json_file = os.path.join(output_dir, f'results_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 保存纯文本格式
        txt_file = os.path.join(output_dir, f'proxies_{timestamp}.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"# 扫描时间: {timestamp}\n")
            f.write(f"# 总代理: {results['stats']['total']}\n")
            f.write(f"# 有效代理: {results['stats']['valid']}\n")
            f.write(f"# 可用代理: {results['stats']['working']}\n\n")
            
            for proxy_info in results.get('working', []):
                f.write(f"{proxy_info['proxy']}\n")
        
        print(f"\n结果已保存到:")
        print(f"  JSON格式: {json_file}")
        print(f"  TXT格式: {txt_file}")