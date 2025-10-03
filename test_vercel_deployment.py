#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Vercel部署的脚本
"""

import asyncio
import aiohttp
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_health_check(url):
    """测试健康检查端点"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ 健康检查成功: {data}")
                    return True
                else:
                    logger.error(f"❌ 健康检查失败: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"❌ 健康检查异常: {e}")
        return False

async def test_websocket_connection(url):
    """测试WebSocket连接"""
    try:
        ws_url = url.replace('http', 'ws') + '/ws'
        logger.info(f"连接WebSocket: {ws_url}")
        
        async with websockets.connect(ws_url) as websocket:
            # 发送注册消息
            register_msg = {
                'type': 'register',
                'device_id': 'test_device_001',
                'username': '测试用户'
            }
            
            await websocket.send(json.dumps(register_msg))
            logger.info("✅ 发送注册消息")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(f"✅ 收到响应: {data}")
            
            # 发送测试消息
            test_msg = {
                'type': 'test_sync',
                'device_id': 'test_device_001',
                'message': 'Vercel测试消息'
            }
            
            await websocket.send(json.dumps(test_msg))
            logger.info("✅ 发送测试消息")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ WebSocket测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 开始测试Vercel部署...")
    print("=" * 50)
    
    # 这里需要替换为你的实际Vercel URL
    # 例如: https://your-app-name.vercel.app
    vercel_url = input("请输入你的Vercel应用URL (例如: https://your-app.vercel.app): ").strip()
    
    if not vercel_url:
        print("❌ 未提供URL，测试终止")
        return
    
    if not vercel_url.startswith('http'):
        vercel_url = 'https://' + vercel_url
    
    print(f"测试URL: {vercel_url}")
    print("-" * 50)
    
    # 测试健康检查
    print("1. 测试健康检查端点...")
    health_ok = await test_health_check(vercel_url)
    
    # 测试WebSocket连接
    print("\n2. 测试WebSocket连接...")
    ws_ok = await test_websocket_connection(vercel_url)
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"WebSocket: {'✅ 通过' if ws_ok else '❌ 失败'}")
    
    if health_ok and ws_ok:
        print("🎉 所有测试通过！Vercel部署成功！")
    else:
        print("⚠️  部分测试失败，请检查部署配置")

if __name__ == "__main__":
    asyncio.run(main())