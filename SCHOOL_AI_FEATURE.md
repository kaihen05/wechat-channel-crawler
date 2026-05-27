# 学校识别AI功能说明

## 功能概述

已成功添加自动识别学校的AI功能，并在首页 http://localhost:8000/ 添加了学校选择选项。

## 新增功能

### 1. 学校识别AI服务

**文件位置**: `backend/app/services/ai_university_classifier.py`

**功能特性**:
- 支持80+所中国主要大学的关键词识别
- 支持DeepSeek AI自动识别（需配置API Key）
- 双重识别机制：优先关键词匹配，其次AI识别

**支持的学校**（部分）:
- 清华大学、北京大学
- 复旦大学、上海交通大学
- 浙江大学、中国科学技术大学
- 南京大学、西安交通大学
- 哈尔滨工业大学、华中科技大学
- 武汉大学、中山大学
- 等80+所中国高校

### 2. 新增API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/channels/identify-university` | POST | 自动识别学校 |
| `/api/channels/universities` | GET | 获取所有可用学校列表 |

#### API使用示例

**自动识别学校**:
```bash
curl -X POST "http://localhost:8000/api/channels/identify-university?nickname=清华大学学生会"
```

**响应**:
```json
{
  "nickname": "清华大学学生会",
  "university": "清华大学",
  "method": "关键词"
}
```

**获取学校列表**:
```bash
curl "http://localhost:8000/api/channels/universities"
```

### 3. 首页学校选择功能

**更新文件**: `backend/app/static/index.html`

**新增UI组件**:
- 学校下拉选择框（支持80+所学校）
- 当前学校筛选标签显示
- 清除学校筛选按钮

**功能说明**:
- 在搜索框旁边添加了学校选择下拉框
- 选择学校后，自动筛选该学校的文章
- 显示当前筛选的学校名称
- 可点击✕清除学校筛选

### 4. 文章API增强

**更新文件**: `backend/app/routers/articles.py`

**新增参数**:
- `university`: 按学校名称筛选文章

**使用示例**:
```
GET /api/articles?university=清华大学&limit=50
```

## 测试结果

### 关键词识别测试
```
清华大学学生会 -> 清华大学 ✓
北大就业指导中心 -> 北京大学 ✓
复旦团委 -> 复旦大学 ✓
上交学生会 -> 上海交通大学 ✓
浙大创业园 -> 浙江大学 ✓
华科研究生会 -> 华中科技大学 ✓
```

所有测试通过，关键词识别功能正常工作。

## 使用方法

### 方法1：通过首页筛选
1. 访问 http://localhost:8000/
2. 在搜索框旁边的"全部学校"下拉框中选择目标学校
3. 系统自动筛选该学校的文章

### 方法2：通过API调用
```python
# 自动识别学校
import requests

response = requests.post(
    "http://localhost:8000/api/channels/identify-university",
    params={"nickname": "清华大学学生会"}
)
print(response.json())
# 输出: {"nickname": "清华大学学生会", "university": "清华大学", "method": "关键词"}
```

### 方法3：编程调用
```python
from app.services.ai_university_classifier import auto_classify_university

# 自动识别学校
university = await auto_classify_university("清华大学学生会")
print(university)  # 输出: 清华大学
```

## 配置要求

如果需要使用DeepSeek AI识别（当关键词匹配失败时），需要在 `backend/.env` 中配置：

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

**注意**: 不配置API Key也不影响使用，系统会使用关键词匹配作为主要识别方式。

## 技术实现

### 关键词匹配
- 基于80+所中国高校的别名数据库
- 支持中英文简称和全称
- 实时响应，无API调用延迟

### AI识别
- 使用DeepSeek API进行智能识别
- 当关键词匹配失败时触发
- 支持模糊匹配和上下文理解

## 数据库影响

无需数据库迁移，新功能完全兼容现有数据：
- 文章查询支持按 `university_name` 字段筛选
- 学校下拉框从服务端实时加载
- 无需修改现有数据库表结构

## 保持不变

✓ 所有现有功能保持不变
✓ 分类筛选功能正常工作
✓ 公众号管理界面不变
✓ Excel导入导出功能正常
✓ MCP协议接口正常
✓ 定时任务正常

## 总结

成功添加了学校识别AI功能，支持：
1. 80+所中国主要大学的自动识别
2. 首页学校选择下拉框
3. 按学校筛选文章
4. 关键词和AI双重识别机制
5. 无需数据库迁移
6. 完全兼容现有功能

所有测试通过，功能已就绪！
