# Vercel部署指南

## 问题解决

原始错误：
```
TypeError: issubclass() arg 1 must be a class
```

这个错误是因为Vercel对Python应用的入口点有特定要求，原来的`railway_sync_server.py`文件不兼容Vercel平台。

## 解决方案

### 1. 创建Vercel兼容的服务器文件

创建了`vercel_sync_server.py`，主要改动：

- 移除了`main()`函数和`if __name__ == "__main__"`块
- 创建全局`app`实例
- 添加必需的`handler`变量
- 简化了应用结构，专门为Vercel优化

### 2. 更新配置文件

#### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "vercel_sync_server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/health",
      "dest": "vercel_sync_server.py"
    },
    {
      "src": "/ws",
      "dest": "vercel_sync_server.py"
    },
    {
      "src": "/",
      "dest": "vercel_sync_server.py"
    }
  ],
  "functions": {
    "vercel_sync_server.py": {
      "maxDuration": 30
    }
  }
}
```

#### requirements.txt
```
aiohttp==3.9.1
```

移除了`websockets`依赖，因为Vercel使用aiohttp的WebSocket支持。

## 部署步骤

### 1. 准备文件
确保以下文件在项目根目录：
- `vercel_sync_server.py` - 主服务器文件
- `vercel.json` - Vercel配置
- `requirements.txt` - Python依赖

### 2. 部署到Vercel

#### 方法1: 使用Vercel CLI
```bash
# 安装Vercel CLI
npm i -g vercel

# 登录Vercel
vercel login

# 部署
vercel

# 生产部署
vercel --prod
```

#### 方法2: 通过GitHub集成
1. 将代码推送到GitHub仓库
2. 在Vercel控制台连接GitHub仓库
3. 自动部署

### 3. 测试部署

使用提供的测试脚本：
```bash
python test_vercel_deployment.py
```

输入你的Vercel应用URL进行测试。

## 功能特性

### 支持的端点
- `GET /` - 根路径，返回健康检查
- `GET /health` - 健康检查端点
- `GET /ws` - WebSocket连接端点

### 支持的消息类型
- `register` - 客户端注册
- `heartbeat` - 心跳检测
- `message_sync` - 消息同步
- `user_sync` - 用户同步
- `group_sync` - 群组同步
- `test_sync` - 测试同步

### 响应格式
```json
{
  "type": "register_success",
  "device_id": "device_001",
  "message": "注册成功",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 注意事项

1. **WebSocket限制**: Vercel对WebSocket连接有超时限制，适合短连接场景
2. **函数超时**: 设置了30秒的最大执行时间
3. **无状态**: 服务器重启后客户端连接会断开，需要重新连接
4. **并发限制**: Vercel免费版有并发连接限制

## 故障排除

### 常见问题

1. **部署失败**
   - 检查`vercel.json`配置是否正确
   - 确保`requirements.txt`中的依赖版本兼容

2. **WebSocket连接失败**
   - 检查URL是否正确（使用wss://而不是ws://）
   - 确认Vercel应用已成功部署

3. **超时错误**
   - 增加`maxDuration`设置
   - 优化代码性能

### 调试方法

1. 查看Vercel控制台的函数日志
2. 使用测试脚本验证各个端点
3. 检查网络连接和防火墙设置

## 性能优化建议

1. **连接管理**: 实现客户端重连机制
2. **消息缓存**: 对于重要消息，考虑持久化存储
3. **负载均衡**: 对于高并发场景，考虑使用多个Vercel函数
4. **监控**: 使用Vercel Analytics监控性能

## 替代方案

如果Vercel的WebSocket限制影响使用，可以考虑：
- Railway (更适合WebSocket应用)
- Fly.io (支持长时间连接)
- Render (免费WebSocket支持)
- 自建服务器 (完全控制)
