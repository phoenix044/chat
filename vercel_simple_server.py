#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel简化版同步服务器
使用标准HTTP处理函数，避免aiohttp兼容性问题
"""

import json
import logging
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局状态存储
clients = {}
message_history = {}
stats = {
    'total_connections': 0,
    'active_connections': 0,
    'messages_processed': 0,
    'start_time': datetime.now()
}

def handler(request, response):
    """
    Vercel HTTP处理函数
    """
    try:
        # 解析URL
        parsed_url = urlparse(request['url'])
        path = parsed_url.path
        
        # 设置CORS头
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
        # 处理OPTIONS请求（CORS预检）
        if request['method'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # 路由处理
        if path == '/health' or path == '/':
            return handle_health_check(request, response, headers)
        elif path == '/ws':
            return handle_websocket(request, response, headers)
        elif path == '/test':
            return handle_test(request, response, headers)
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not Found'})
            }
            
    except Exception as e:
        logger.error(f"处理请求时出错: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def handle_health_check(request, response, headers):
    """处理健康检查"""
    import sys
    
    health_data = {
        'status': 'healthy',
        'platform': 'vercel',
        'python_version': sys.version,
        'python_version_info': {
            'major': sys.version_info.major,
            'minor': sys.version_info.minor,
            'micro': sys.version_info.micro
        },
        'timestamp': datetime.now().isoformat(),
        'uptime': str(datetime.now() - stats['start_time']).split('.')[0],
        'active_connections': stats['active_connections'],
        'total_connections': stats['total_connections'],
        'message': 'Vercel同步服务器运行正常'
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(health_data, ensure_ascii=False, indent=2)
    }

def handle_websocket(request, response, headers):
    """处理WebSocket相关请求（模拟）"""
    # 注意：Vercel的Serverless函数不支持真正的WebSocket
    # 这里返回一个说明信息
    
    ws_info = {
        'message': 'Vercel Serverless函数不支持WebSocket连接',
        'suggestion': '请使用支持WebSocket的平台，如Railway、Fly.io或Render',
        'alternatives': [
            'Railway - 支持WebSocket',
            'Fly.io - 支持长时间连接',
            'Render - 免费WebSocket支持',
            '自建服务器 - 完全控制'
        ],
        'current_platform': 'Vercel',
        'limitation': 'Serverless函数有执行时间限制，不适合WebSocket'
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(ws_info, ensure_ascii=False, indent=2)
    }

def handle_test(request, response, headers):
    """处理测试请求"""
    test_data = {
        'message': '测试成功',
        'timestamp': datetime.now().isoformat(),
        'method': request['method'],
        'url': request['url'],
        'headers': request.get('headers', {}),
        'platform': 'Vercel'
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(test_data, ensure_ascii=False, indent=2)
    }

# Vercel需要这个变量
app = handler
