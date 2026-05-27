# 快速开始指南

## 一、项目初始化（5分钟）

### 1. 安装 Python 依赖

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
copy .env.example .env
```

用记事本编辑 `.env` 文件，填入微信凭证。

## 二、获取微信凭证（10分钟）

### 步骤 1：登录公众号后台
1. 打开浏览器，访问：https://mp.weixin.qq.com
2. 使用微信扫码登录

### 步骤 2：获取 Token
1. 登录后，查看浏览器地址栏
2. 找到 URL 中的 `token` 参数（例如：`token=1234567890`）
3. 复制这个数字

### 步骤 3：获取 Cookie
1. 按 F12 打开开发者工具
2. 切换到 "Network"（网络）标签
3. 刷新页面
4. 点击任意请求
5. 在 "Headers" 中找到 "Cookie"
6. 复制整个 Cookie 值

### 步骤 4：填入配置文件

编辑 `.env` 文件：

```env
WECHAT_TOKEN=你复制的token
WECHAT_COOKIE=你复制的cookie
```

## 三、启动服务（1分钟）

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
python run.py
```

看到以下输出表示启动成功：

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     初始化数据库...
INFO:     数据库初始化完成
INFO:     启动定时任务调度器...
INFO:     定时任务调度器已启动
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 四、使用 API（5分钟）

### 方式 1：使用浏览器（推荐）

1. 打开浏览器访问：http://localhost:8000/docs
2. 你会看到完整的 API 文档界面
3. 点击任意接口即可测试

### 方式 2：使用 curl 命令

#### 1. 验证凭证状态
```bash
curl http://localhost:8000/api/auth/credentials/status
```

#### 2. 搜索公众号
```bash
curl "http://localhost:8000/api/channels/search?keyword=腾讯"
```

#### 3. 添加公众号（使用搜索结果的 fakeid）
```bash
curl -X POST "http://localhost:8000/api/channels" \
  -H "Content-Type: application/json" \
  -d '{
    "fakeid": "MzIwNDM4NjY5Mg==",
    "nickname": "测试公众号"
  }'
```

#### 4. 手动同步文章
```bash
curl -X POST "http://localhost:8000/api/articles/sync"
```

#### 5. 查看文章列表
```bash
curl http://localhost:8000/api/articles?limit=10
```

## 五、定时任务说明

系统默认配置为每天上午 9 点自动同步文章。

### 修改同步时间

编辑 `.env` 文件：

```env
SCHEDULE_HOUR=9     # 改为你想要的小时（0-23）
SCHEDULE_MINUTE=0    # 改为你想要的分钟（0-59）
```

重启服务后生效。

## 六、常见问题

### Q: 提示 "未配置微信凭证"
A: 检查 `.env` 文件中的 `WECHAT_TOKEN` 和 `WECHAT_COOKIE` 是否填写正确。

### Q: 搜索公众号没结果
A: 可能是凭证过期了，重新获取 token 和 cookie。

### Q: 同步失败
A: 
1. 检查凭证是否过期
2. 查看控制台日志了解详细错误
3. 确保网络连接正常

### Q: 数据库在哪里？
A: 位于 `backend/data/channels.db`，定期备份这个文件即可。

## 七、下一步

- 阅读 `README.md` 了解更多功能和配置
- 访问 http://localhost:8000/docs 查看完整 API 文档
- 根据需求修改 `.env` 配置

## 八、安全提醒

⚠️ **重要**：
- 使用小号公众号，不要使用主号
- 定期更新凭证（建议每天早上）
- 不要修改请求频率限制配置
- 系统已内置安全保护，请勿绕过限制

## 需要帮助？

如果遇到问题：
1. 查看控制台日志输出
2. 检查 `.env` 配置是否正确
3. 确认微信凭证是否过期
4. 参考 `README.md` 文档
