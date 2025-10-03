#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway优化版同步服务器
支持HTTP健康检查和WebSocket连接
"""

import asyncio
import websockets
import json
import logging
import os
from datetime import datetime
from typing import Dict, Set
import uuid
from aiohttp import web, WSMsgType
import aiohttp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RailwaySyncServer:
    def __init__(self, host='0.0.0.0', port=None):
        self.host = host
        # 支持云部署环境变量 PORT
        self.port = port or int(os.environ.get('PORT', 8766))
        self.clients: Dict[str, Dict] = {}
        self.message_history: Dict[str, list] = {}
        self.app = None
        self.running = False
        
        # 统计信息
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_processed': 0,
            'start_time': datetime.now()
        }
    
    async def health_check(self, request):
        """健康检查端点"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': str(datetime.now() - self.stats['start_time']).split('.')[0],
            'active_connections': self.stats['active_connections'],
            'total_connections': self.stats['total_connections']
        })
    
    async def websocket_handler(self, request):
        """WebSocket处理器"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        client_id = None
        client_info = None
        
        try:
            self.stats['total_connections'] += 1
            self.stats['active_connections'] += 1
            
            logger.info(f"新WebSocket连接: {request.remote}")
            
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        message_type = data.get('type')
                        device_id = data.get('device_id')
                        
                        if not device_id:
                            await self.send_error(ws, "Missing device_id")
                            continue
                        
                        if message_type == 'register':
                            client_id = device_id
                            client_info = {
                                'websocket': ws,
                                'username': data.get('username', 'Unknown'),
                                'connected_at': datetime.now(),
                                'last_heartbeat': datetime.now()
                            }
                            self.clients[client_id] = client_info
                            
                            # 发送注册成功响应
                            response = {
                                'type': 'register_success',
                                'device_id': device_id,
                                'message': '注册成功',
                                'timestamp': datetime.now().isoformat()
                            }
                            await ws.send_str(json.dumps(response))
                            logger.info(f"客户端注册成功: {client_id} ({client_info['username']})")
                            
                            # 通知其他客户端
                            await self.broadcast_user_joined(client_id, client_info['username'])
                            
                        elif message_type == 'heartbeat':
                            if client_id and client_id in self.clients:
                                self.clients[client_id]['last_heartbeat'] = datetime.now()
                                logger.debug(f"收到心跳: {client_id}")
                            
                        elif message_type == 'message_sync':
                            await self.handle_message_sync(ws, data)
                            
                        elif message_type == 'user_sync':
                            await self.handle_user_sync(ws, data)
                            
                        elif message_type == 'group_sync':
                            await self.handle_group_sync(ws, data)
                            
                        elif message_type == 'test_sync':
                            await self.handle_test_sync(ws, data)
                            
                        else:
                            await self.send_error(ws, f"Unknown message type: {message_type}")
                        
                        self.stats['messages_processed'] += 1
                        
                    except json.JSONDecodeError:
                        await self.send_error(ws, "Invalid JSON format")
                    except Exception as e:
                        logger.error(f"处理消息时出错: {e}")
                        await self.send_error(ws, f"Server error: {str(e)}")
                        
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket错误: {ws.exception()}')
                    
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                self.stats['active_connections'] -= 1
                logger.info(f"客户端已移除: {client_id}")
        
        return ws
    
    async def handle_message_sync(self, websocket, data):
        """处理消息同步"""
        message_data = data.get('data')
        if not message_data:
            await self.send_error(websocket, "Missing message data")
            return
        
        # 广播消息给所有其他客户端
        await self.broadcast_to_others(websocket, {
            'type': 'message_sync',
            'data': message_data,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"消息同步: {message_data.get('id', 'unknown')}")
    
    async def handle_user_sync(self, websocket, data):
        """处理用户同步"""
        user_data = data.get('data')
        if not user_data:
            await self.send_error(websocket, "Missing user data")
            return
        
        # 广播用户信息给所有其他客户端
        await self.broadcast_to_others(websocket, {
            'type': 'user_sync',
            'data': user_data,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"用户同步: {user_data.get('id', 'unknown')}")
    
    async def handle_group_sync(self, websocket, data):
        """处理群组同步"""
        group_data = data.get('data')
        if not group_data:
            await self.send_error(websocket, "Missing group data")
            return
        
        # 广播群组信息给所有其他客户端
        await self.broadcast_to_others(websocket, {
            'type': 'group_sync',
            'data': group_data,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"群组同步: {group_data.get('id', 'unknown')}")
    
    async def handle_test_sync(self, websocket, data):
        """处理测试同步"""
        test_message = data.get('message', '测试消息')
        
        # 广播测试消息给所有其他客户端
        await self.broadcast_to_others(websocket, {
            'type': 'test_sync',
            'message': test_message,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"测试同步: {test_message}")
    
    async def broadcast_to_others(self, sender_websocket, message):
        """广播消息给除发送者外的所有客户端"""
        if not self.clients:
            return
        
        disconnected_clients = []
        
        for client_id, client_info in self.clients.items():
            try:
                if client_info['websocket'] != sender_websocket:
                    await client_info['websocket'].send_str(json.dumps(message))
            except Exception as e:
                logger.error(f"广播消息失败 {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            if client_id in self.clients:
                del self.clients[client_id]
                self.stats['active_connections'] -= 1
    
    async def broadcast_user_joined(self, client_id, username):
        """广播用户加入消息"""
        message = {
            'type': 'user_joined',
            'username': username,
            'client_id': client_id,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_to_others(None, message)
    
    async def send_error(self, websocket, error_message):
        """发送错误消息"""
        error_response = {
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            await websocket.send_str(json.dumps(error_response))
        except Exception as e:
            logger.error(f"发送错误消息失败: {e}")
    
    async def start_server(self):
        """启动服务器"""
        try:
            # 创建aiohttp应用
            self.app = web.Application()
            
            # 添加路由
            self.app.router.add_get('/health', self.health_check)
            self.app.router.add_get('/ws', self.websocket_handler)
            self.app.router.add_get('/', self.health_check)  # 根路径也返回健康检查
            
            # 启动服务器
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            
            self.running = True
            logger.info(f"Railway同步服务器启动成功")
            logger.info(f"监听地址: {self.host}:{self.port}")
            logger.info(f"健康检查: http://{self.host}:{self.port}/health")
            logger.info(f"WebSocket: ws://{self.host}:{self.port}/ws")
            logger.info(f"环境变量 PORT: {os.environ.get('PORT', '未设置')}")
            logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 保持服务器运行
            while self.running:
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            raise
    
    async def stop_server(self):
        """停止服务器"""
        self.running = False
        if self.app:
            await self.app.cleanup()
        logger.info("服务器已停止")
    
    def get_stats(self):
        """获取服务器统计信息"""
        uptime = datetime.now() - self.stats['start_time']
        return {
            **self.stats,
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': str(uptime).split('.')[0]
        }

async def main():
    """主函数"""
    print("🚀 Railway同步服务器启动中...")
    print("=" * 50)
    
    # 创建服务器实例
    server = RailwaySyncServer()
    
    try:
        # 启动服务器
        await server.start_server()
    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭服务器...")
    except Exception as e:
        print(f"服务器运行错误: {e}")
    finally:
        await server.stop_server()
        print("服务器已关闭")

# 为了兼容不同的部署环境，添加这些变量
app = None
handler = None

def create_app():
    """创建应用实例，用于某些部署平台"""
    global app
    server = RailwaySyncServer()
    app = web.Application()
    app.router.add_get('/health', server.health_check)
    app.router.add_get('/ws', server.websocket_handler)
    app.router.add_get('/', server.health_check)
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    asyncio.run(main())
