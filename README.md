# 公众号渠道资源收集系统

📚 用于微信公众号文章的定期收集、管理和检索的工具，特别适合渠道资源收集使用。

## ✨ 功能特性

- 🔍 **精准爬取**：通过微信公众号后台接口获取公众号最新文章（需登录凭证）
- 📱 **公众号管理**：灵活添加、删除、启用/禁用公众号
- 🔄 **定时同步**：每天和每周自动同步最新文章
- 📊 **Excel导出**：支持手动和自动导出文章到Excel
- 📝 **导出日志**：记录所有导出操作历史
- 📊 **文章统计**：查看同步统计信息
- 🌐 **Web API**：完整的RESTful API接口
- 🔐 **凭证管理**：便捷的登录凭证设置和状态查看
- 🛡️ **安全保护**：内置请求频率限制和智能延迟机制

## 🛠️ 技术栈

- **后端**：Python 3.9+ / FastAPI / SQLAlchemy
- **数据库**：SQLite
- **定时任务**：APScheduler
- **HTTP客户端**：httpx
- **Excel处理**：pandas / openpyxl

## 🚀 快速开始

### 1. 环境要求

- Python 3.9 或更高版本
- pip 包管理器

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境变量模板文件：

```bash
cd backend
copy .env.example .env
```

编辑 `backend/.env` 文件：

```env
# 微信公众号凭证配置
WECHAT_TOKEN=你的token
WECHAT_COOKIE=你的cookie

# 定时任务配置（每天几点执行）
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0

# 默认获取前几天的文章
DEFAULT_DAYS=3

# 数据库配置
DATABASE_URL=sqlite:///./data/channels.db

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

### 4. 获取微信登录凭证

1. 打开浏览器，访问 https://mp.weixin.qq.com
2. 使用微信扫码登录你的公众号
3. 从 URL 中获取 `token`（数字）
4. 按 F12 打开开发者工具，从 Network 中获取 `Cookie`
5. 将 token 和 cookie 填入 `.env` 文件

**⚠️ 重要提示**：
- 强烈建议使用小号公众号获取凭证，不要使用主号
- 凭证有效期约 4 小时，需要定期更新
- 系统已内置安全保护机制，请勿尝试绕过限制

### 5. 启动服务

```bash
cd backend
python run.py
```

服务启动后，访问 http://localhost:8000 即可使用。

## 📖 API 文档

启动服务后，访问 http://localhost:8000/docs 查看完整的 API 文档（Swagger UI）。

### 主要接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/auth/credentials` | 设置登录凭证 |
| GET | `/api/auth/credentials/status` | 获取凭证状态 |
| GET | `/api/channels` | 获取所有公众号 |
| POST | `/api/channels` | 添加公众号 |
| POST | `/api/channels/search` | 搜索公众号 |
| PUT | `/api/channels/{id}` | 更新公众号状态 |
| DELETE | `/api/channels/{id}` | 删除公众号 |
| GET | `/api/articles` | 获取文章列表 |
| POST | `/api/articles/sync` | 手动触发同步 |
| GET | `/api/articles/stats` | 获取文章统计 |
| GET | `/api/export/excel` | 导出Excel（支持参数筛选）|
| GET | `/api/export/excel/week` | 导出最近一周的文章 |
| GET | `/api/export/excel/all` | 导出所有文章 |
| GET | `/api/export/logs` | 查看导出日志 |
| GET | `/api/export/stats` | 查看导出统计 |

## 📖 使用示例

### 1. 设置微信凭证

```bash
curl -X POST "http://localhost:8000/api/auth/credentials" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "1234567890",
    "cookie": "your_cookie_here"
  }'
```

### 2. 搜索公众号

```bash
curl -X GET "http://localhost:8000/api/channels/search?keyword=腾讯"
```

### 3. 添加公众号

```bash
curl -X POST "http://localhost:8000/api/channels" \
  -H "Content-Type: application/json" \
  -d '{
    "fakeid": "MzIwNDM4NjY5Mg==",
    "nickname": "腾讯官方",
    "account_name": "tencent",
    "avatar_url": "http://..."
  }'
```

### 4. 同步文章

```bash
curl -X POST "http://localhost:8000/api/articles/sync"
```

### 5. 获取文章列表

```bash
curl -X GET "http://localhost:8000/api/articles?limit=20"
```

### 6. 导出Excel

```bash
# 导出最近一周的文章
curl "http://localhost:8000/api/export/excel?days=7" -o week_articles.xlsx

# 导出所有文章
curl "http://localhost:8000/api/export/excel/all" -o all_articles.xlsx

# 导出指定公众号的文章
curl "http://localhost:8000/api/export/excel?channel_id=1" -o channel_articles.xlsx
```

### 7. 查看导出日志

```bash
curl "http://localhost:8000/api/export/logs"
```

## 📁 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 主应用
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # 数据模型
│   │   │   ├── channel.py       # 公众号模型
│   │   │   ├── article.py       # 文章模型
│   │   │   └── export_log.py   # 导出日志模型
│   │   ├── schemas/             # Pydantic 模式
│   │   │   ├── channel.py       # 公众号模式
│   │   │   └── article.py       # 文章模式
│   │   ├── routers/             # API 路由
│   │   │   ├── auth.py          # 认证路由
│   │   │   ├── channels.py      # 公众号管理
│   │   │   ├── articles.py      # 文章管理
│   │   │   └── export.py       # Excel导出路由
│   │   └── services/            # 业务服务
│   │       ├── wechat_crawler.py # 微信公众号爬虫
│   │       ├── excel_export.py   # Excel导出服务
│   │       └── scheduler.py      # 定时任务
│   ├── data/                    # 数据库文件目录
│   ├── exports/                 # Excel导出目录
│   ├── requirements.txt         # 依赖列表
│   ├── .env.example             # 环境变量模板
│   └── run.py                   # 启动脚本
├── README.md                   # 项目文档
├── QUICKSTART.md               # 快速开始指南
├── INSTALL_GUIDE.md           # 安装和使用指南
└── WEEKLY_SYNC_GUIDE.md       # 每周定时和Excel导出说明
```

## 🔧 配置说明

### 基础配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `WECHAT_TOKEN` | 微信公众号后台token | - |
| `WECHAT_COOKIE` | 微信公众号后台cookie | - |
| `DEFAULT_DAYS` | 默认获取天数 | 3 |
| `HOST` | 服务器地址 | 0.0.0.0 |
| `PORT` | 服务器端口 | 8000 |

### 定时任务配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DAILY_SCHEDULE_HOUR` | 每天同步小时 | 9 |
| `DAILY_SCHEDULE_MINUTE` | 每天同步分钟 | 0 |
| `WEEKLY_DAY` | 每周同步星期几（0=周一）| 0 |
| `WEEKLY_HOUR` | 每周同步小时 | 9 |
| `WEEKLY_MINUTE` | 每周同步分钟 | 0 |

### Excel导出配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `AUTO_EXPORT_WEEKLY` | 是否每周自动导出 | true |
| `EXPORT_DIRECTORY` | Excel导出目录 | ./exports |
| `EXPORT_FILENAME_PREFIX` | 导出文件名前缀 | articles |

## 🛡️ 安全保护机制

本系统内置严格的安全保护，最大程度降低封号风险：

| 保护措施 | 配置值 | 说明 |
|----------|--------|------|
| **请求间隔** | 5-15 秒 | 随机延迟，模拟人类行为 |
| **搜索延迟** | 8-20 秒 | 搜索公众号后的额外等待 |
| **每小时限制** | 30 次 | 防止高频请求 |
| **每日限制** | 100 次 | 每日总请求上限 |
| **单次同步** | 5 个公众号 | 单次操作限制 |
| **每号限制** | 10 篇文章 | 每个公众号最大获取数 |

### 安全特性

- ✅ **请求审计**：所有请求记录日志，可追溯
- ✅ **配额管理**：自动限制请求频率
- ✅ **智能延迟**：随机延迟模拟正常用户行为
- ✅ **智能缓存**：避免重复获取相同文章

## ⚠️ 注意事项

1. **登录凭证**：需要使用微信公众号后台的登录凭证，凭证有效期约 4 小时
2. **强烈建议**：使用小号公众号获取凭证，**不要使用主号**
3. **请求限制**：系统已内置严格限制，请勿尝试绕过
4. **法律合规**：本工具仅供学习研究使用，请遵守相关法律法规
5. **风险自担**：使用本工具的风险由用户自行承担
6. **数据备份**：SQLite 数据库文件位于 `backend/data/` 目录，请定期备份

## 📝 开发计划

- [x] 基础爬虫功能（微信公众号后台接口）
- [x] Web API 接口
- [x] 凭证管理功能
- [x] 每天定时同步功能
- [x] 每周定时同步功能
- [x] Excel 导出功能
- [x] Excel 自动导出
- [x] 导出日志记录
- [x] 安全保护机制
- [ ] Web 管理界面
- [ ] 邮件通知
- [ ] 更多 AI 模型支持
- [ ] Docker 部署支持

## 📚 相关文档

- **快速开始**：查看 [QUICKSTART.md](QUICKSTART.md)
- **安装指南**：查看 [INSTALL_GUIDE.md](INSTALL_GUIDE.md)
- **每周定时和Excel导出**：查看 [WEEKLY_SYNC_GUIDE.md](WEEKLY_SYNC_GUIDE.md)

## 🔍 常见问题

### Q: 凭证多久需要更新一次？
A: 一般 4 小时左右，建议每天早上手动更新一次凭证。

### Q: 如何查看系统日志？
A: 日志会直接输出到控制台，包含同步状态和错误信息。

### Q: 可以同时添加多少个公众号？
A: 系统内置安全机制，单次同步最多 5 个公众号。

### Q: 同步失败怎么办？
A: 检查凭证是否过期，尝试更新 token 和 cookie 后重新同步。

## 📄 许可证

MIT License

## 🤝 致谢

本项目参考了 "高校社团公众号聚合器" 项目的设计思路。
