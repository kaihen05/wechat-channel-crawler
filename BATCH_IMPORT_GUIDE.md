# 批量导入公众号使用指南

## 功能概述

系统现在支持通过Excel表格批量导入公众号，并按照以下四个垂类进行分类：
- 🎮 **游戏** - 游戏开发相关
- 💡 **产品** - 产品设计相关
- 👥 **人力** - 人力资源管理相关
- 💻 **技术** - 技术前沿动态

## 导入步骤

### 1. 下载Excel模板
访问 `http://localhost:8000/manage.html`，点击"批量导入"区域的"点击下载 Excel 模板"链接。

### 2. 填写Excel文件

#### 必填字段
| 字段名 | 说明 | 示例 |
|--------|------|------|
| fakeid | 公众号唯一标识（从微信后台获取） | ojr0j6Kx5T-3vK0v5K0J9g |
| nickname | 公众号名称 | 游戏技术社区 |
| category | 分类（必须为：游戏/产品/人力/技术） | 游戏 |

#### 可选字段
| 字段名 | 说明 | 示例 |
|--------|------|------|
| account_name | 公众号账号名 | gametech |
| avatar_url | 头像URL | https://example.com/avatar.png |

#### 示例数据
```
fakeid                          nickname         category  account_name
ojr0j6Kx5T-3vK0v5K0J9g         游戏技术社区       游戏       gametech
MzAxNTAwOTU3Mw==               产品经理PM        产品       pmchina
MjM5NDk2MzYyMg==               HR人力资源        人力       hrchina
MzIwNDU2NzI0NQ==               技术前沿          技术       techfrontier
```

### 3. 上传Excel文件
在 `http://localhost:8000/manage.html` 的"批量导入"区域：
1. 点击"选择文件"按钮
2. 选择填写好的Excel文件
3. 点击"导入"按钮
4. 等待导入完成

### 4. 查看导入结果
系统会显示：
- 总数：Excel中的公众号数量
- 成功：成功导入的数量
- 跳过：已存在被跳过的数量
- 错误：导入失败的详细信息

## 获取fakeid的方法

### 方法1：通过搜索功能
1. 访问 `http://localhost:8000/manage.html`
2. 在搜索框输入公众号名称
3. 点击"搜索"按钮
4. 在结果中可以查看fakeid（但这个API不直接返回fakeid）

### 方法2：通过浏览器开发者工具（推荐）
1. 登录微信公众号后台
2. 进入公众号管理页面
3. 按F12打开开发者工具
4. 切换到Network标签
5. 刷新页面，找到包含公众号信息的请求
6. 在响应中查找 `fakeid` 字段

## 前端使用

### 按分类浏览
访问 `http://localhost:8000/`，页面顶部会显示四个分类卡片：
- 点击任意分类卡片，只显示该分类下的文章
- 点击"全部文章"按钮，显示所有文章
- 点击分类标签后的 ✕ 按钮清除分类筛选

### 搜索文章
在搜索框输入关键词，系统会：
1. 搜索所有分类下的文章
2. 如果当前有分类筛选，则在当前分类下搜索

## 注意事项

1. **分类必须准确**：category字段只能是"游戏"、"产品"、"人力"、"技术"中的一个
2. **fakeid唯一性**：fakeid是公众号的唯一标识，不能重复
3. **Excel格式**：请使用xlsx格式，xls格式可能不支持
4. **文件大小**：单个Excel文件建议不超过1000行
5. **导入速度**：导入100个公众号大约需要10-30秒

## 常见问题

### Q1: 导入失败，提示"分类错误"
A: 检查Excel中的category字段，确保只使用了"游戏"、"产品"、"人力"、"技术"这四个值

### Q2: 提示"Excel文件缺少必需的列"
A: 确保Excel第一行包含：fakeid、nickname、category三个字段

### Q3: 导入后没有显示公众号
A: 检查fakeid是否正确，或在管理页面点击"刷新"按钮

### Q4: 如何修改公众号的分类？
A: 目前需要先删除后重新添加，或通过数据库直接修改

## API接口

### 导入Excel
```
POST /api/channels/import
Content-Type: multipart/form-data

参数：
- file: Excel文件

返回：
{
  "success": true,
  "message": "成功导入 N 个公众号",
  "stats": {
    "total": 10,
    "success": 8,
    "skipped": 2,
    "errors": 0
  },
  "errors": []
}
```

### 按分类获取文章
```
GET /api/articles?category=游戏&limit=50&skip=0

参数：
- category: 分类（可选）
- limit: 每页数量
- skip: 偏移量
- days: 最近N天（可选）

返回：文章列表
```

### 获取分类列表
```
GET /api/channels/categories

返回：["游戏", "产品", "人力", "技术"]
```
