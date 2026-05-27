# 字段更新说明

## 新增字段

### 1. 大学名称 (university_name)
- **所属表**: Channel (公众号表)
- **类型**: String(100)
- **默认值**: "" (空字符串)
- **说明**: 用于标识公众号所属大学，如"清华大学"、"北京大学"等

### 2. 浏览量 (read_num)
- **所属表**: Article (文章表)
- **类型**: Integer
- **默认值**: 0
- **说明**: 文章的浏览次数，从微信公众号API获取（如果API支持）

### 3. 分类 (category)
- **所属表**: Channel (公众号表)
- **类型**: String(50)
- **默认值**: "未分类"
- **说明**: 公众号分类，可选值：游戏、产品、人力、技术、综合、未分类
  - **综合**: 专用于校学生会、院学生会、校研究生会、院研究生会等组织

## 数据库变更

### Channel 表
新增字段：
- `university_name`: 大学名称

### Article 表
新增字段：
- `read_num`: 浏览量

## API 变更

### 文章列表 API
**URL**: GET `/api/articles`

**返回字段新增**：
- `university_name`: 公众号所属大学名称
- `read_num`: 文章浏览量

### 公众号创建/更新 API
**URL**: POST `/api/channels`
**URL**: PUT `/api/channels/{id}`

**请求参数新增**：
- `university_name`: 大学名称（可选）

### Excel 导入 API
**URL**: POST `/api/channels/import`

**Excel 列新增**：
- `university_name`: 大学名称（可选列）

## 前端变更

### 文章列表显示
新增显示：
1. **大学名称标签**: 以蓝色标签形式显示在文章卡片中
2. **浏览量**: 以眼睛图标 + 数字的形式显示
3. **分类标签**: 以紫色标签形式显示（已有）

示例显示：
```
[公众号名] [大学名称标签] [作者] 👁️浏览量 🕒时间 [分类标签]
```

## Excel 导入模板更新

### 旧模板 (v1)
必需列：
- fakeid
- nickname
- category

可选列：
- account_name
- avatar_url

### 新模板 (v2)
必需列：
- fakeid
- nickname
- category

可选列：
- account_name
- avatar_url
- **university_name** ⭐ (新增)

### 示例数据
| fakeid | nickname | category | account_name | avatar_url | university_name |
|--------|----------|-----------|--------------|------------|-----------------|
| MzAxNTAwOTU3Mw== | 游戏技术社区 | 游戏 | gametech | https://... | 清华大学 |
| MjM5NDk2MzYyMg== | 产品经理PM | 产品 | pmchina | https://... | 北京大学 |
| MzIwNDU2NzI0NQ== | HR人力资源 | 人力 | hrchina | https://... | 复旦大学 |

## 使用说明

### 1. 添加公众号时指定大学名称

**通过 API**:
```json
{
  "fakeid": "MzAxNTAwOTU3Mw==",
  "nickname": "游戏技术社区",
  "category": "游戏",
  "university_name": "清华大学",
  "account_name": "gametech"
}
```

**通过 Excel 导入**:
1. 下载新模板 `channel_import_template_v2.xlsx`
2. 填写 `university_name` 列
3. 上传导入

### 2. 查看文章时显示大学名称和浏览量

访问 http://localhost:8000/，文章列表会自动显示：
- 大学名称（蓝色标签）
- 浏览量（眼睛图标 + 数字）
- 分类（紫色标签）

### 3. 更新公众号的大学名称

**通过 API**:
```json
PUT /api/channels/{id}
{
  "university_name": "北京大学"
}
```

## 注意事项

1. **数据库迁移**: 已执行迁移，旧数据已清除
2. **浏览量数据**: 微信公众号后台API可能不返回浏览量，默认值为0
3. **大学名称**: 可选字段，不填写时为空字符串
4. **向后兼容**: API 和前端都支持新字段，旧字段继续有效
5. **Excel 导入**: 新模板包含 university_name 列，旧模板仍可使用（但不填大学名称）

## 测试

### 测试 API
```bash
# 获取文章列表（包含新字段）
curl "http://localhost:8000/api/articles?limit=10"

# 添加公众号（包含大学名称）
curl -X POST http://localhost:8000/api/channels \
  -H "Content-Type: application/json" \
  -d '{
    "fakeid": "MzAxNTAwOTU3Mw==",
    "nickname": "测试公众号",
    "category": "游戏",
    "university_name": "清华大学"
  }'
```

### 测试前端
1. 访问 http://localhost:8000/
2. 确认文章列表显示：
   - 大学名称标签（蓝色）
   - 浏览量（眼睛图标）
   - 分类标签（紫色）

## 更新日志

**2026-04-13**:
- ✅ 添加 `university_name` 字段到 Channel 表
- ✅ 添加 `read_num` 字段到 Article 表
- ✅ 更新 API 接口支持新字段
- ✅ 更新前端显示新字段
- ✅ 更新 Excel 导入功能支持 university_name
- ✅ 更新导入文档和模板
- ✅ 执行数据库迁移
