# 🚀 微信公众号聚合器 MCP Server 配置指南

## 📋 MCP Server 信息

**名称**: `wechat-aggregator`（微信公众号聚合器）  
**MCP 地址**: `http://localhost:8000/api/mcp`  
**传输方式**: HTTP  
**版本**: v1.0.0

---

## 🛠️ 可用工具列表

### 1️⃣ list_articles - 获取文章列表

获取系统中所有文章，支持按公众号和时间筛选。

**接口地址**: `GET /api/mcp/articles/list`

**参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `skip` | int | 否 | 0 | 跳过数量(分页) |
| `limit` | int | 否 | 50 | 返回数量(1-200) |
| `account_id` | int | 否 | - | 公众号ID |
| `days` | int | 否 | - | 最近N天 |

**返回示例**:
```json
{
  "success": true,
  "data": [
    {
      "article_id": 123,
      "account_id": 5,
      "account_name": "清华社团",
      "title": "2024春季招新开始啦！",
      "link": "https://mp.weixin.qq.com/s/xxx",
      "author": "张三",
      "digest": "欢迎加入我们...",
      "create_time": "2024-03-15T10:30:00",
      "collected_at": "2024-03-15T10:35:00",
      "cover_url": "https://..."
    }
  ],
  "total": 50
}
```

**使用场景**:
- 查看最新发布的文章
- 获取某个公众号的所有文章
- 查看最近N天的文章

---

### 2️⃣ search_articles - 搜索文章

在文章标题、摘要、作者和公众号名称中搜索关键词。

**接口地址**: `GET /api/mcp/articles/search`

**参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `keyword` | string | ✅ | - | 搜索关键词 |
| `skip` | int | 否 | 0 | 跳过数量(分页) |
| `limit` | int | 否 | 50 | 返回数量(1-200) |

**返回示例**:
```json
{
  "success": true,
  "data": [...],
  "total": 25,
  "keyword": "招新"
}
```

**使用场景**:
- 搜索包含特定关键词的文章
- 查找特定作者的文章
- 搜索特定主题的内容

---

### 3️⃣ get_article - 获取文章详情

获取单篇文章的完整信息。

**接口地址**: `GET /api/mcp/articles/{article_id}`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `article_id` | int | ✅ | 文章ID |

**返回示例**:
```json
{
  "success": true,
  "data": {
    "article_id": 123,
    "account_id": 5,
    "account_name": "清华社团",
    "title": "2024春季招新开始啦！",
    "link": "https://mp.weixin.qq.com/s/xxx",
    "content_url": "https://mp.weixin.qq.com/s/...",
    "author": "张三",
    "digest": "欢迎加入我们...",
    "cover_url": "https://...",
    "create_time": "2024-03-15T10:30:00",
    "collected_at": "2024-03-15T10:35:00",
    "channel": {
      "id": 5,
      "fakeid": "MjM5...",
      "nickname": "清华社团",
      "account_name": "清华社团联合会",
      "round_head_img": "https://...",
      "is_active": true,
      "last_sync_at": "2024-03-15T09:00:00"
    }
  }
}
```

**使用场景**:
- 查看文章的完整信息
- 获取文章所属公众号的详细信息
- 点击文章查看详情

---

### 4️⃣ list_accounts - 获取公众号列表

获取系统中所有已添加的公众号。

**接口地址**: `GET /api/mcp/accounts/list`

**参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `skip` | int | 否 | 0 | 跳过数量(分页) |
| `limit` | int | 否 | 50 | 返回数量(1-200) |
| `university_id` | int | 否 | - | 大学ID(预留字段) |

**返回示例**:
```json
{
  "success": true,
  "data": [
    {
      "account_id": 5,
      "fakeid": "MjM5...",
      "nickname": "清华社团",
      "account_name": "清华社团联合会",
      "round_head_img": "https://...",
      "is_active": true,
      "article_count": 150,
      "last_sync_at": "2024-03-15T09:00:00",
      "created_at": "2024-01-01T08:00:00"
    }
  ],
  "total": 10
}
```

**使用场景**:
- 查看所有已添加的公众号
- 筛选活跃的公众号
- 按大学分类查看公众号(未来功能)

---

### 5️⃣ get_account - 获取公众号详情

获取单个公众号的完整信息，包括最新文章。

**接口地址**: `GET /api/mcp/accounts/{account_id}`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `account_id` | int | ✅ | 公众号ID |

**返回示例**:
```json
{
  "success": true,
  "data": {
    "account_id": 5,
    "fakeid": "MjM5...",
    "nickname": "清华社团",
    "account_name": "清华社团联合会",
    "round_head_img": "https://...",
    "is_active": true,
    "article_count": 150,
    "last_sync_at": "2024-03-15T09:00:00",
    "created_at": "2024-01-01T08:00:00",
    "recent_articles": [
      {
        "article_id": 123,
        "title": "2024春季招新开始啦！",
        "create_time": "2024-03-15T10:30:00"
      }
    ]
  }
}
```

**使用场景**:
- 查看公众号的详细信息
- 查看某个公众号的最新文章
- 了解公众号的同步状态

---

### 6️⃣ list_universities - 获取大学列表

获取系统中所有大学列表。

**接口地址**: `GET /api/mcp/universities/list`

**参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `skip` | int | 否 | 0 | 跳过数量(分页) |
| `limit` | int | 否 | 50 | 返回数量(1-200) |

**返回示例**:
```json
{
  "success": true,
  "data": [],
  "total": 0,
  "message": "大学分类功能暂未实现,敬请期待"
}
```

**注意**: 当前版本暂未实现大学分类功能，此接口返回空列表。

---

### 7️⃣ get_university - 获取大学详情

获取单个大学的详细信息。

**接口地址**: `GET /api/mcp/universities/{university_id}`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `university_id` | int | ✅ | 大学ID |

**注意**: 当前版本暂未实现大学分类功能，此接口返回 404。

---

## 💬 自然语言查询示例

配置 MCP Server 后，您可以使用自然语言查询公众号文章：

### 📅 时间相关查询
- "查一下最近7天的文章"
- "查看今天的文章"
- "获取最近30天的所有文章"

### 🔍 搜索相关查询
- "搜索包含招新的文章"
- "查找关键词为'春招'的文章"
- "搜索'活动'相关的文章"

### 📊 统计相关查询
- "获取所有公众号列表"
- "查看有多少个公众号"
- "列出所有活跃的公众号"

### 📖 详情相关查询
- "获取文章ID为123的详情"
- "查看公众号ID为5的详细信息"
- "显示某个公众号的最新文章"

---

## 🔧 快速测试

### 1. 获取 MCP Server 信息
```bash
curl http://localhost:8000/api/mcp/info
```

### 2. 获取文章列表
```bash
curl "http://localhost:8000/api/mcp/articles/list?limit=10"
```

### 3. 搜索文章
```bash
curl "http://localhost:8000/api/mcp/articles/search?keyword=招新"
```

### 4. 获取公众号列表
```bash
curl "http://localhost:8000/api/mcp/accounts/list"
```

---

## 📝 配置步骤

### 第一步: 启动服务
```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
python run.py
```

### 第二步: 配置 MCP Client

在您的 MCP 客户端中添加以下配置：

**MCP 配置信息**:
```
名称: wechat-aggregator
类型: HTTP
URL: http://localhost:8000/api/mcp
```

### 第三步: 开始使用

配置完成后，您就可以使用自然语言查询公众号文章了！

---

## 🎯 使用场景

1. **渠道资源收集**: 自动收集各高校社团公众号的最新动态
2. **招新信息监控**: 实时跟踪各大社团的招新信息
3. **活动信息聚合**: 汇总各高校的社团活动信息
4. **内容分析**: 分析公众号发布的内容趋势和热点
5. **数据导出**: 将收集的数据导出为 Excel 进行深入分析

---

## ⚠️ 注意事项

1. **服务可用性**: MCP Server 需要先启动后端服务才能访问
2. **数据更新**: 数据通过定时任务自动同步，也可以手动触发同步
3. **搜索范围**: 搜索会在标题、摘要、作者和公众号名称中匹配
4. **分页支持**: 所有列表接口都支持分页，建议合理设置 limit 参数
5. **大学功能**: 大学分类功能暂未实现，相关接口返回空数据或404

---

## 🔗 相关链接

- **API 文档**: http://localhost:8000/docs
- **MCP 信息**: http://localhost:8000/api/mcp/info
- **主项目**: http://localhost:8000

---

## 📞 技术支持

如有问题，请查看项目 README 或联系技术支持团队。
