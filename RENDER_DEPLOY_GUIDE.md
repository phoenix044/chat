# Render部署指南

## 部署步骤

### 1. 准备代码
- 确保所有文件已推送到GitHub
- 仓库必须是Public

### 2. 在Render中部署
1. 访问 render.com
2. 注册账号（使用GitHub登录）
3. 点击 "New" -> "Web Service"
4. 连接GitHub仓库
5. 选择你的仓库
6. 配置设置：
   - Name: chat-sync-server
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: python railway_sync_server.py
   - Plan: Free

### 3. 环境变量
- PORT: 8766 (可选，Render会自动设置)

### 4. 部署
- 点击 "Create Web Service"
- 等待部署完成
- 获取公网URL

## 配置说明

### 健康检查
- 路径: /health
- 返回: JSON格式的服务器状态

### WebSocket连接
- 路径: /ws
- 协议: WSS (HTTPS)

## 客户端配置

```dart
// 在 lib/providers/sync_manager.dart 中
final RxString serverAddress = 'your-app-name.onrender.com'.obs;
final RxBool useSSL = true.obs;
```

## 优势
- 免费750小时/月
- 自动部署
- 支持自定义域名
- 稳定可靠

---
创建时间: 2025-10-03 21:14:11
