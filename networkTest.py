# network_check.py
import subprocess
import sys

def test_connection():
    """测试各种网络连接方法"""
    print("🔍 网络连接诊断工具")
    print("=" * 40)
    
    tests = [
        ("Ping GitHub", "ping -n 2 github.com"),
        ("nslookup GitHub", "nslookup github.com"),
        ("Git 连接测试", "git ls-remote https://github.com/pybilibilimusic/pybilimusic.git"),
        ("PowerShell 测试", "powershell -Command \"Invoke-WebRequest -Uri https://github.com -TimeoutSec 5\""),
    ]
    
    for test_name, cmd in tests:
        print(f"\n🧪 测试: {test_name}")
        print(f"   命令: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("   ✅ 成功")
            else:
                print(f"   ❌ 失败 (代码: {result.returncode})")
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}...")
        except subprocess.TimeoutExpired:
            print("   ⏰ 超时")
        except Exception as e:
            print(f"   💥 异常: {e}")

def main():
    test_connection()
    
    print("\n💡 建议解决方案:")
    print("1. 暂时关闭防火墙/杀毒软件")
    print("2. 使用手机热点网络")
    print("3. 使用 VPN")
    print("4. 稍后重试")

if __name__ == "__main__":
    main()
