# 确保你在正确的目录
cd /path/to/socks5-proxy-scanner

# 查看当前目录内容
ls -la

# 创建快速测试脚本
cat > quick_test.py << 'EOF'
import sys
import os

print("=" * 60)
print("SOCKS5代理扫描器 - 快速功能验证")
print("=" * 60)

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print(f"Python路径已添加: {current_dir}")

# 测试导入
print("\n1. 测试模块导入...")
try:
    from src.scanner import Socks5Scanner
    from src.validator import ProxyValidator
    print("✅ 模块导入成功")
    print(f"   扫描器类: {Socks5Scanner}")
    print(f"   验证器类: {ProxyValidator}")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n尝试从 src 目录导入...")
    sys.path.insert(0, os.path.join(current_dir, 'src'))
    try:
        from scanner import Socks5Scanner
        from validator import ProxyValidator
        print("✅ 从src目录导入成功")
    except ImportError as e2:
        print(f"❌ 仍然失败: {e2}")
        sys.exit(1)
except Exception as e:
    print(f"❌ 其他错误: {e}")
    sys.exit(1)

# 测试配置
print("\n2. 测试配置加载...")
try:
    import yaml
    config_file = 'config.yaml'
    if not os.path.exists(config_file):
        print(f"⚠️  配置文件不存在: {config_file}")
        # 尝试从config目录查找
        config_file = 'config/config.example.yaml'
        if os.path.exists(config_file):
            print(f"   使用示例配置文件: {config_file}")
        else:
            print("❌ 找不到任何配置文件")
            sys.exit(1)
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("✅ 配置加载成功")
    print(f"   测试源数量: {len(config.get('test_sources', []))}个")
    print(f"   扫描线程数: {config.get('scan', {}).get('max_workers', 20)}")
    print(f"   扫描模式: {config.get('scan', {}).get('mode', 'free')}")
    
    # 显示前3个测试源
    test_sources = config.get('test_sources', [])
    if test_sources:
        print(f"   前3个测试源:")
        for i, source in enumerate(test_sources[:3], 1):
            print(f"     {i}. {source[:60]}...")
    
except yaml.YAMLError as e:
    print(f"❌ YAML格式错误: {e}")
    sys.exit(1)
except FileNotFoundError as e:
    print(f"❌ 文件未找到: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    sys.exit(1)

# 测试类实例化
print("\n3. 测试类实例化...")
try:
    scanner = Socks5Scanner(config)
    validator = ProxyValidator(config)
    print("✅ 类实例化成功")
    print(f"   扫描器: {scanner}")
    print(f"   验证器: {validator}")
except Exception as e:
    print(f"❌ 实例化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试主函数
print("\n4. 测试主函数...")
try:
    from src.main import main
    print("✅ 主函数导入成功")
    
    # 检查main是否是函数
    if callable(main):
        print("✅ 主函数可调用")
    else:
        print("⚠️  主函数不可调用")
except ImportError:
    print("⚠️  无法导入main，尝试从src.main导入...")
    try:
        sys.path.insert(0, os.path.join(current_dir, 'src'))
        from main import main
        print("✅ 从src.main导入成功")
    except ImportError as e:
        print(f"❌ 导入main失败: {e}")
except Exception as e:
    print(f"❌ 主函数测试失败: {e}")

print("\n" + "=" * 60)
print("🎉 快速功能验证完成！")
print("=" * 60)
print("\n如果所有测试都通过✅，可以运行完整扫描：")
print("  python src/main.py --config config.yaml --threads 20")
print("\n如果遇到问题，请检查：")
print("  1. 是否安装了依赖: pip install requests pyyaml")
print("  2. 配置文件是否存在: ls -la config.yaml")
print("  3. 是否在项目根目录运行")
print("=" * 60)
EOF

# 给脚本执行权限（可选）
chmod +x quick_test.py