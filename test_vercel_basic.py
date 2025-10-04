#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Vercel基础版部署的脚本
"""

import requests
import json

def test_endpoint(url, endpoint, description):
    """测试指定端点"""
    try:
        full_url = f"{url}{endpoint}"
        response = requests.get(full_url, timeout=10)
        
        print(f"\n{description}:")
        print(f"URL: {full_url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ 响应成功:")
                for key, value in data.items():
                    print(f"   {key}: {value}")
                return True
            except json.JSONDecodeError:
                print("✅ 响应成功 (非JSON格式):")
                print(f"   内容: {response.text[:200]}...")
                return True
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试Vercel基础版部署...")
    print("=" * 60)
    
    # 获取Vercel URL
    vercel_url = input("请输入你的Vercel应用URL (例如: https://your-app.vercel.app): ").strip()
    
    if not vercel_url:
        print("❌ 未提供URL，测试终止")
        return
    
    if not vercel_url.startswith('http'):
        vercel_url = 'https://' + vercel_url
    
    print(f"测试URL: {vercel_url}")
    print("-" * 60)
    
    # 测试端点列表
    test_cases = [
        ("/", "根路径测试"),
        ("/api", "API路径测试"),
        ("/api/health", "API健康检查测试"),
        ("/api/test", "API测试端点测试"),
        ("/health", "健康检查测试（备用）"),
        ("/test", "测试端点测试（备用）")
    ]
    
    results = []
    for endpoint, description in test_cases:
        result = test_endpoint(vercel_url, endpoint, description)
        results.append((description, result))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    all_passed = True
    for description, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{description}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！Vercel基础版部署成功！")
        print("\n📝 说明:")
        print("- 使用api/index.py结构，这是Vercel推荐的方式")
        print("- 使用最简单的函数结构，避免兼容性问题")
        print("- 只使用Python标准库，无外部依赖")
    else:
        print("⚠️  部分测试失败，请检查部署配置")
        print("\n🔧 故障排除建议:")
        print("1. 确认文件结构: api/index.py")
        print("2. 确认vercel.json配置正确")
        print("3. 检查Vercel部署日志")
        print("4. 尝试重新部署")

if __name__ == "__main__":
    main()
