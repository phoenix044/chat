#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Vercel简化版部署的脚本
"""

import requests
import json

def test_health_check(url):
    """测试健康检查端点"""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 健康检查成功:")
            print(f"   状态: {data.get('status')}")
            print(f"   平台: {data.get('platform')}")
            print(f"   Python版本: {data.get('python_version_info', {}).get('major')}.{data.get('python_version_info', {}).get('minor')}.{data.get('python_version_info', {}).get('micro')}")
            print(f"   运行时间: {data.get('uptime')}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_root_endpoint(url):
    """测试根端点"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 根端点测试成功:")
            print(f"   消息: {data.get('message')}")
            return True
        else:
            print(f"❌ 根端点测试失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 根端点测试异常: {e}")
        return False

def test_websocket_info(url):
    """测试WebSocket信息端点"""
    try:
        response = requests.get(f"{url}/ws", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ WebSocket信息端点测试成功:")
            print(f"   消息: {data.get('message')}")
            print(f"   建议: {data.get('suggestion')}")
            return True
        else:
            print(f"❌ WebSocket信息端点测试失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ WebSocket信息端点测试异常: {e}")
        return False

def test_test_endpoint(url):
    """测试测试端点"""
    try:
        response = requests.get(f"{url}/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 测试端点成功:")
            print(f"   消息: {data.get('message')}")
            print(f"   方法: {data.get('method')}")
            return True
        else:
            print(f"❌ 测试端点失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试端点异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试Vercel简化版部署...")
    print("=" * 50)
    
    # 获取Vercel URL
    vercel_url = input("请输入你的Vercel应用URL (例如: https://your-app.vercel.app): ").strip()
    
    if not vercel_url:
        print("❌ 未提供URL，测试终止")
        return
    
    if not vercel_url.startswith('http'):
        vercel_url = 'https://' + vercel_url
    
    print(f"测试URL: {vercel_url}")
    print("-" * 50)
    
    # 执行测试
    tests = [
        ("健康检查", lambda: test_health_check(vercel_url)),
        ("根端点", lambda: test_root_endpoint(vercel_url)),
        ("WebSocket信息", lambda: test_websocket_info(vercel_url)),
        ("测试端点", lambda: test_test_endpoint(vercel_url))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}测试:")
        result = test_func()
        results.append((test_name, result))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！Vercel简化版部署成功！")
        print("\n📝 重要说明:")
        print("- 这个版本使用标准HTTP处理函数，避免了aiohttp兼容性问题")
        print("- Vercel不支持真正的WebSocket连接，这是平台限制")
        print("- 如需WebSocket功能，建议使用Railway、Fly.io或Render")
    else:
        print("⚠️  部分测试失败，请检查部署配置")

if __name__ == "__main__":
    main()
