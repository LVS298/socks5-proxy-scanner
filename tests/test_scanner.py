#!/usr/bin/env python3
"""
单元测试 - SOCKS5代理扫描器
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import (
    is_valid_ip,
    is_valid_port,
    parse_proxy,
    format_proxy,
    load_proxy_file,
    save_proxy_file,
    Color,
    Timer,
    PerformanceMonitor,
)
from scanner import Socks5Scanner
from validator import ProxyValidator


class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_is_valid_ip(self):
        """测试IP验证"""
        self.assertTrue(is_valid_ip("192.168.1.1"))
        self.assertTrue(is_valid_ip("8.8.8.8"))
        self.assertTrue(is_valid_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
        self.assertFalse(is_valid_ip("256.256.256.256"))
        self.assertFalse(is_valid_ip("not-an-ip"))
    
    def test_is_valid_port(self):
        """测试端口验证"""
        self.assertTrue(is_valid_port(8080))
        self.assertTrue(is_valid_port(1))
        self.assertTrue(is_valid_port(65535))
        self.assertFalse(is_valid_port(0))
        self.assertFalse(is_valid_port(65536))
        self.assertFalse(is_valid_port("not-a-port"))
    
    def test_parse_proxy(self):
        """测试代理解析"""
        # 标准格式
        ip, port = parse_proxy("192.168.1.1:1080")
        self.assertEqual(ip, "192.168.1.1")
        self.assertEqual(port, 1080)
        
        # 带协议前缀
        ip, port = parse_proxy("socks5://192.168.1.1:1080")
        self.assertEqual(ip, "192.168.1.1")
        self.assertEqual(port, 1080)
        
        # 无效格式
        ip, port = parse_proxy("invalid:proxy:format")
        self.assertIsNone(ip)
        self.assertIsNone(port)
        
        ip, port = parse_proxy("256.256.256.256:99999")
        self.assertIsNone(ip)
        self.assertIsNone(port)
    
    def test_format_proxy(self):
        """测试代理格式化"""
        proxy = format_proxy("192.168.1.1", 1080)
        self.assertEqual(proxy, "socks5://192.168.1.1:1080")
        
        proxy = format_proxy("192.168.1.1", 1080, "http")
        self.assertEqual(proxy, "http://192.168.1.1:1080")
    
    def test_proxy_file_operations(self):
        """测试代理文件读写"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# 测试代理文件\n")
            f.write("192.168.1.1:1080\n")
            f.write("192.168.1.2:1080\n")
            f.write("192.168.1.3:1080\n")
            temp_file = f.name
        
        try:
            # 测试加载
            proxies = load_proxy_file(temp_file)
            self.assertEqual(len(proxies), 3)
            self.assertIn("192.168.1.1:1080", proxies)
            
            # 测试保存
            new_proxies = ["10.0.0.1:8080", "10.0.0.2:8080"]
            save_path = temp_file + ".new"
            result = save_proxy_file(new_proxies, save_path, "测试头")
            self.assertTrue(result)
            self.assertTrue(os.path.exists(save_path))
            
            # 验证保存的内容
            with open(save_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("测试头", content)
                self.assertIn("10.0.0.1:8080", content)
            
        finally:
            # 清理临时文件
            for file_path in [temp_file, save_path]:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_color_class(self):
        """测试颜色工具类"""
        colored_text = Color.red("错误信息")
        self.assertIn("错误信息", colored_text)
        
        bold_text = Color.bold("重要信息")
        self.assertIn("重要信息", bold_text)
    
    def test_timer_context(self):
        """测试计时器上下文管理器"""
        with Timer() as timer:
            import time
            time.sleep(0.1)
        
        self.assertGreater(timer.get_elapsed(), 0)
    
    def test_performance_monitor(self):
        """测试性能监控器"""
        monitor = PerformanceMonitor()
        
        monitor.start_operation("test1")
        import time
        time.sleep(0.05)
        monitor.end_operation("test1")
        
        report = monitor.get_report()
        self.assertIn("test1", report)
        self.assertGreater(report["test1"], 0)


class TestScanner(unittest.TestCase):
    """测试扫描器"""
    
    def setUp(self):
        """测试前设置"""
        self.config = {
            'scan': {
                'max_workers': 2,
                'timeout': 2,
                'mode': 'free',
            },
            'test_sources': [
                'http://example.com/test1.m3u8',
                'http://example.com/test2.m3u8',
            ],
            'provinces': ['北京', '上海'],
            'operators': ['中国移动', '中国电信'],
        }
        self.scanner = Socks5Scanner(self.config)
    
    def test_scanner_initialization(self):
        """测试扫描器初始化"""
        self.assertEqual(self.scanner.timeout, 2)
        self.assertEqual(len(self.scanner.PROVINCES), 2)
        self.assertEqual(len(self.scanner.OPERATORS), 2)
        self.assertEqual(self.scanner.config, self.config)
    
    @patch('scanner.requests.get')
    def test_fetch_free_proxies(self, mock_get):
        """测试获取免费代理"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "127.0.0.1:1080\n127.0.0.2:1080\n127.0.0.3:1080"
        mock_get.return_value = mock_response
        
        # 调用方法
        proxies = self.scanner.fetch_free_proxies()
        
        # 验证结果
        self.assertGreaterEqual(len(proxies), 3)
        self.assertIn("127.0.0.1:1080", proxies)
        
        # 验证请求被调用
        self.assertTrue(mock_get.called)
    
    @patch('scanner.Socks5Scanner.fetch_free_proxies')
    @patch('scanner.ProxyValidator')
    def test_run_full_scan(self, mock_validator_class, mock_fetch_proxies):
        """测试完整扫描流程"""
        # 模拟获取代理
        mock_fetch_proxies.return_value = [
            "127.0.0.1:1080",
            "127.0.0.2:1080",
            "127.0.0.3:1080",
        ]
        
        # 模拟验证器
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        
        # 模拟验证结果
        mock_results = {
            'all': [
                {'proxy': '127.0.0.1:1080', 'source': 'free', 'working': True},
                {'proxy': '127.0.0.2:1080', 'source': 'free', 'working': True},
            ],
            'valid': [],
            'working': [],
            'stats': {
                'total': 3,
                'valid': 2,
                'working': 2,
                'failed': 1,
            }
        }
        mock_validator.validate_proxies.return_value = mock_results
        
        # 运行扫描
        with tempfile.TemporaryDirectory() as temp_dir:
            self.scanner.run_full_scan(
                max_workers=2,
                mode='free',
                output_dir=temp_dir
            )
            
            # 验证方法被调用
            self.assertTrue(mock_fetch_proxies.called)
            self.assertTrue(mock_validator.validate_proxies.called)
            self.assertTrue(mock_validator.save_results.called)
    
    def test_print_statistics(self):
        """测试统计信息打印"""
        results = {
            'stats': {
                'total': 100,
                'valid': 80,
                'working': 60,
                'failed': 40,
            }
        }
        
        # 这里主要测试没有异常发生
        try:
            self.scanner._print_statistics(results)
        except Exception as e:
            self.fail(f"_print_statistics 抛出异常: {e}")


class TestValidator(unittest.TestCase):
    """测试验证器"""
    
    def setUp(self):
        """测试前设置"""
        self.config = {
            'scan': {'timeout': 2},
            'test_sources': ['http://example.com/test.m3u8'],
        }
        self.validator = ProxyValidator(self.config)
    
    def test_validator_initialization(self):
        """测试验证器初始化"""
        self.assertEqual(self.validator.timeout, 2)
        self.assertEqual(len(self.validator.test_sources), 1)
    
    @patch('validator.ProxyValidator._test_socks5_connection')
    @patch('validator.ProxyValidator._test_proxy_with_source')
    def test_validate_proxies(self, mock_test_source, mock_test_connection):
        """测试代理验证"""
        # 模拟代理列表
        proxies = [
            {'proxy': '127.0.0.1:1080', 'source': 'test'},
            {'proxy': '127.0.0.2:1080', 'source': 'test'},
            {'proxy': '127.0.0.3:1080', 'source': 'test'},
        ]
        
        # 模拟连接测试结果
        def mock_connection(proxy):
            return proxy in ['127.0.0.1:1080', '127.0.0.2:1080']
        mock_test_connection.side_effect = mock_connection
        
        # 模拟源访问测试结果
        def mock_source(proxy, source):
            return proxy == '127.0.0.1:1080'
        mock_test_source.side_effect = mock_source
        
        # 运行验证
        results = self.validator.validate_proxies(proxies, max_workers=2)
        
        # 验证结果
        self.assertEqual(results['stats']['total'], 3)
        self.assertEqual(results['stats']['valid'], 2)
        self.assertEqual(results['stats']['working'], 1)
        self.assertEqual(results['stats']['failed'], 2)
        
        # 验证可用代理
        working_proxies = results['working']
        self.assertEqual(len(working_proxies), 1)
        self.assertEqual(working_proxies[0]['proxy'], '127.0.0.1:1080')
    
    @patch('socket.socket')
    def test_test_socks5_connection(self, mock_socket):
        """测试SOCKS5连接测试"""
        # 模拟成功的SOCKS5连接
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        
        # 模拟成功的握手响应
        mock_sock.recv.return_value = b'\x05\x00'
        
        # 测试有效代理
        result = self.validator._test_socks5_connection("127.0.0.1:1080")
        self.assertTrue(result)
        
        # 验证socket操作被调用
        mock_sock.connect.assert_called_with(('127.0.0.1', 1080))
        mock_sock.send.assert_called_with(b'\x05\x01\x00')
        mock_sock.close.assert_called()
    
    @patch('requests.head')
    def test_test_proxy_with_source(self, mock_head):
        """测试代理源访问"""
        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'video/mp4'}
        mock_head.return_value = mock_response
        
        # 测试代理访问
        result = self.validator._test_proxy_with_source(
            "127.0.0.1:1080", 
            "http://example.com/test.m3u8"
        )
        self.assertTrue(result)
        
        # 验证请求参数
        mock_head.assert_called_once()
        call_kwargs = mock_head.call_args[1]
        self.assertEqual(call_kwargs['proxies']['http'], 'socks5://127.0.0.1:1080')
        self.assertEqual(call_kwargs['timeout'], 10)
    
    def test_save_results(self):
        """测试结果保存"""
        results = {
            'all': [
                {'proxy': '127.0.0.1:1080', 'source': 'test', 'working': True,
                 'accessible_sources': ['http://example.com/test.m3u8']},
                {'proxy': '127.0.0.2:1080', 'source': 'test', 'working': False},
            ],
            'valid': [],
            'working': [],
            'stats': {
                'total': 2,
                'valid': 1,
                'working': 1,
                'failed': 1,
            }
        }
        
        # 保存到临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            self.validator.save_results(results, temp_dir, "20230101_120000")
            
            # 验证文件被创建
            json_file = os.path.join(temp_dir, 'socks5_results_20230101_120000.json')
            txt_file = os.path.join(temp_dir, 'working_proxies_20230101_120000.txt')
            
            self.assertTrue(os.path.exists(json_file))
            self.assertTrue(os.path.exists(txt_file))
            
            # 验证JSON内容
            with open(json_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                self.assertEqual(saved_data['stats']['total'], 2)
            
            # 验证TXT内容
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('127.0.0.1:1080', content)
                self.assertIn('成功率', content)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end(self):
        """端到端测试"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建配置文件
            config_file = os.path.join(temp_dir, 'config.yaml')
            config_content = """
scan:
  max_workers: 2
  timeout: 2
  mode: free
test_sources:
  - http://example.com/test.m3u8
provinces:
  - 北京
  - 上海
operators:
  - 中国移动
output:
  directory: ./results
  save_json: true
  save_txt: true
"""
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # 创建代理文件
            proxy_file = os.path.join(temp_dir, 'test_proxies.txt')
            with open(proxy_file, 'w', encoding='utf-8') as f:
                f.write("127.0.0.1:1080\n")
                f.write("192.168.1.1:1080\n")
            
            # 测试工具函数
            proxies = load_proxy_file(proxy_file)
            self.assertEqual(len(proxies), 2)
            
            # 测试代理解析
            for proxy in proxies:
                ip, port = parse_proxy(proxy)
                self.assertIsNotNone(ip)
                self.assertIsNotNone(port)
                self.assertTrue(is_valid_ip(ip))
                self.assertTrue(is_valid_port(port))
            
            # 清理
            if os.path.exists(config_file):
                os.remove(config_file)
            if os.path.exists(proxy_file):
                os.remove(proxy_file)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTest(unittest.makeSuite(TestUtils))
    suite.addTest(unittest.makeSuite(TestScanner))
    suite.addTest(unittest.makeSuite(TestValidator))
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    # 运行测试
    success = run_tests()
    
    # 退出码
    sys.exit(0 if success else 1)
