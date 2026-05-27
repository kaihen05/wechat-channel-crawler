# 微信 API 阅读量功能更新总结

## 更新时间
2026-04-15

## 更新内容

### 1. 配置文件更新 (`backend/app/config.py`)
- 新增配置项：
  - `wechat_appid`: 微信公众号 AppID
  - `wechat_appsecret`: 微信公众号 AppSecret
  - `wechat_access_token`: Access Token 缓存

### 2. 爬虫服务更新 (`backend/app/services/wechat_crawler.py`)
- `WeChatCrawler` 类新增构造参数：`appid`, `appsecret`
- 新增方法：
  - `get_access_token()`: 获取微信 API access token
  - `get_article_read_stats()`: 通过 API 获取文章阅读统计
  - `get_user_summary()`: 获取用户增减数据
- 更新 `get_articles()` 方法：提取并返回 msgid

### 3. 数据库模型更新 (`backend/app/models/article.py`)
- `Article` 模型新增字段：
  - `msgid`: 文章消息ID，用于微信公众号 API

### 4. API 路由更新 (`backend/app/routers/articles.py`)
- 新增端点：
  - `POST /api/articles/sync-read-nums-from-api`: 通过微信 API 更新文章阅读量
- 更新文章同步逻辑：保存 msgid 字段

### 5. 前端界面更新 (`backend/app/static/manage.html`)
- 新增界面部分：「🔑 通过微信 API 更新阅读量」
- 新增 JavaScript 函数：
  - `syncReadNumbersFromAPI()`: 调用 API 更新阅读量
- 新增日期选择器：选择要更新的日期范围

### 6. 数据库迁移
- 创建迁移脚本：`backend/migrate_add_msgid.py`
- 自动添加 `msgid` 字段到 `articles` 表

### 7. 测试脚本
- 创建测试脚本：`backend/test_wechat_api.py`
- 用于测试 access token 获取和阅读量更新功能

### 8. 文档
- 创建使用说明：`WECHAT_API_READ_NUM.md`
- 详细说明配置步骤、使用方法、限制和故障排查

## 备份信息

修改前的重要文件已备份到：
- `backup_before_read_num_fix/backup_20260415_150738/`
  - channels.py
  - articles.py
  - manage.html
  - index.html

## 功能特性

### 优点
1. **真实数据**：通过官方 API 获取真实的阅读量数据
2. **批量更新**：支持批量更新指定日期范围内的文章
3. **自动化**：可以集成到定时任务中定期更新
4. **友好界面**：提供 Web 界面，无需手动调用 API

### 限制
1. **权限要求**：需要公众号管理权限
2. **数据范围**：只能获取自己管理的公众号数据
3. **时间限制**：通常只能获取近 7-30 天的数据
4. **频率限制**：API 调用次数有限制

## 使用流程

1. **配置凭证**：在 `.env` 文件中设置 AppID 和 AppSecret
2. **同步文章**：确保文章包含 msgid（从微信后台同步）
3. **运行迁移**：执行数据库迁移添加 msgid 字段
4. **更新阅读量**：通过 Web 界面或 API 更新阅读量

## 兼容性

- 向后兼容：不影响现有功能
- 新字段默认值：msgid 默认为空字符串
- API 端点：新增端点，不影响现有端点

## 技术细节

### API 调用流程
1. 获取 access token（有效期 7200 秒）
2. 使用 token 调用数据统计 API
3. 解析响应，提取阅读量数据
4. 更新数据库

### 数据存储
- msgid 存储在 Article 模型
- read_num 存储在 Article 模型
- total_read_num 存储在 Channel 模型（自动计算）

### 错误处理
- API 调用失败时记录日志
- 部分失败不影响其他文章
- 返回详细的错误信息

## 后续优化建议

1. **缓存优化**：缓存 access token，避免频繁请求
2. **批量请求**：支持批量调用 API 提高效率
3. **定时任务**：集成到定时任务中自动更新
4. **错误重试**：添加失败重试机制
5. **进度显示**：前端显示更新进度

## 注意事项

1. **安全性**：AppSecret 是敏感信息，不要泄露
2. **性能**：大量文章更新可能需要较长时间
3. **准确性**：API 数据可能有 1-2 小时延迟
4. **监控**：注意 API 调用次数，避免超限

## 测试建议

1. **功能测试**：使用测试脚本验证 API 连接
2. **性能测试**：测试大量文章更新的性能
3. **错误测试**：测试各种错误情况的处理
4. **兼容测试**：确保不影响现有功能

## 相关文件清单

### 修改的文件
- backend/app/config.py
- backend/app/services/wechat_crawler.py
- backend/app/models/article.py
- backend/app/routers/articles.py
- backend/app/static/manage.html

### 新增的文件
- backend/migrate_add_msgid.py
- backend/test_wechat_api.py
- WECHAT_API_READ_NUM.md
- WECHAT_API_UPDATE_SUMMARY.md (本文件)
- backup_current_code.py
- backup_before_read_num_fix/ (备份目录)

## 总结

本次更新为系统增加了通过微信公众号官方 API 获取真实阅读量的能力。虽然有一定的限制，但对于有公众号管理权限的用户来说，这是获取准确阅读量的最佳方案。

系统提供了完整的配置、使用和测试工具，用户可以根据需要选择使用。同时保留了原有的手动设置和计算功能，确保系统的灵活性和向后兼容性。
