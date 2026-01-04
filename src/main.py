#!/usr/bin/env python3
"""
SOCKS5代理扫描器 - 主程序
GitHub部署友好版本
"""

import os
import sys
import argparse
import yaml
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scanner import Socks5Scanner
from src.validator import ProxyValidator

def load_config(config_file=None):
    """加载配置文件"""
    # 默认配置文件路径
    default_configs = [
        'config/config.yaml',
        'config/config.example.yaml',
        os.path.join(Path.home(), '.config/socks5-scanner/config.yaml')
    ]
    
    config_file = config_file or next((f for f in default_configs if os.path.exists(f)), None)
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            return {}
    else:
        print("未找到配置文件，使用默认配置")
        return {
            'scan': {
                'max_workers': 10,
                'timeout': 5,
                'test_sources': [
                    "http://example.com/test1.m3u8",
                    "http://example.com/test2.m3u8"
                ]
            },
            'output': {
                'format': 'txt',
                'directory': './results',
                'save_json': True
            }
        }

def main():
    parser = argparse.ArgumentParser(description='SOCKS5代理扫描器')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--mode', '-m', choices=['quake', 'free', 'both'], 
                       default='free', help='扫描模式')
    parser.add_argument('--province', '-p', nargs='+', help='指定省份')
    parser.add_argument('--operator', '-o', nargs='+', 
                       choices=['移动', '电信', '联通', 'all'], 
                       default=['all'], help='指定运营商')
    parser.add_argument('--output', '-O', help='输出目录')
    parser.add_argument('--test-only', action='store_true', 
                       help='仅测试现有代理列表')
    parser.add_argument('--proxy-file', help='代理列表文件（测试模式使用）')
    parser.add_argument('--threads', '-t', type=int, default=20, 
                       help='线程数')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 创建输出目录
    output_dir = args.output or config.get('output', {}).get('directory', './results')
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*60)
    print("SOCKS5代理扫描器")
    print(f"模式: {args.mode}")
    print(f"线程数: {args.threads}")
    print(f"输出目录: {output_dir}")
    print("="*60)
    
    # 初始化扫描器
    scanner = Socks5Scanner(config)
    
    # 设置API密钥（从环境变量读取，安全）
    api_key = os.getenv('QUAKE_API_KEY')
    if api_key:
        scanner.QUAKE_API_KEY = api_key
    
    if args.test_only:
        # 仅测试模式
        if not args.proxy_file:
            print("错误：测试模式需要指定代理文件")
            sys.exit(1)
            
        validator = ProxyValidator(config)
        results = validator.test_proxy_file(args.proxy_file)
        validator.save_results(results, output_dir)
    else:
        # 扫描模式
        # 设置省份和运营商过滤
        if args.province:
            scanner.PROVINCES = args.province
        
        if args.operator != ['all']:
            operator_map = {
                '移动': '中国移动',
                '电信': '中国电信',
                '联通': '中国联通'
            }
            scanner.OPERATORS = [operator_map.get(op, op) for op in args.operator]
        
        # 运行扫描
        scanner.run_full_scan(
            max_workers=args.threads,
            mode=args.mode,
            output_dir=output_dir
        )

if __name__ == "__main__":
    main()
