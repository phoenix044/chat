#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI兼容的同步服务器
用于部署到支持WSGI的平台
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict
from aiohttp import web, WSMsgType
# from aiohttp_wsgi import WSGIHandler  # 暂时注释掉，使用原生aiohttp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyncServer:
    def __init__(self):
        self.clients: Dict[str, Dict] = {}
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
                        
                        if message_type == 'register' and device_id:
                            client_id = device_id
                            self.clients[client_id] = {
                                'websocket': ws,
                                'username': data.get('username', 'Unknown'),
                                'connected_at': datetime.now()
                            }
                            
                            response = {
                                'type': 'register_success',
                                'device_id': device_id,
                                'message': '注册成功',
                                'timestamp': datetime.now().isoformat()
                            }
                            await ws.send_str(json.dumps(response))
                            logger.info(f"客户端注册成功: {client_id}")
                        
                        self.stats['messages_processed'] += 1
                        
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            'type': 'error',
                            'message': 'Invalid JSON format'
                        }))
                    except Exception as e:
                        logger.error(f"处理消息时出错: {e}")
                        
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                self.stats['active_connections'] -= 1
                logger.info(f"客户端已移除: {client_id}")
        
        return ws

# 创建服务器实例
sync_server = SyncServer()

# 创建aiohttp应用
app = web.Application()

# 添加路由
app.router.add_get('/health', sync_server.health_check)
app.router.add_get('/ws', sync_server.websocket_handler)
app.router.add_get('/', sync_server.health_check)

# 为了兼容某些部署平台
handler = None

if __name__ == "__main__":
    # 获取端口
    port = int(os.environ.get('PORT', 8766))
    
    # 启动服务器
    web.run_app(app, host='0.0.0.0', port=port)
