# Excel批量导入功能使用说明

## ✅ 已完成的功能

### 1. 数据库模型更新
- ✅ 在 `Channel` 模型中添加 `category` 字段
- ✅ 支持四个垂类分类：游戏、产品、人力、技术
- ✅ 默认值为"未分类"

### 2. Excel批量导入
- ✅ 创建Excel导入模板：`channel_import_template.xlsx`
- ✅ 支持批量导入公众号并指定分类
- ✅ 导入结果统计（成功、跳过、失败）
- ✅ 详细的错误信息提示

### 3. 前端分类展示
- ✅ 主页顶部展示四个分类卡片（游戏、产品、人力、技术）
- ✅ 点击分类卡片筛选对应文章
- ✅ 显示当前筛选的分类
- ✅ 清除分类筛选功能

### 4. API接口
- ✅ `POST /api/channels/import` - Excel批量导入
- ✅ `GET /api/channels/categories` - 获取分类列表
- ✅ `GET /api/articles?category=xxx` - 按分类获取文章
- ✅ `GET /channel_import_template.xlsx` - 下载Excel模板

## 📋 使用方法

### 方式1：Excel批量导入（推荐用于多个公众号）

1. **下载模板**
   - 访问 `http://localhost:8000/manage.html`
   - 点击"批量导入"区域的"点击下载 Excel 模板"

2. **填写Excel**
   ```
   fakeid                          nickname         category  account_name
   ojr0j6Kx5T-3vK0v5K0J9g         游戏技术社区       游戏       gametech
   MzAxNTAwOTU3Mw==               产品经理PM        产品       pmchina
   MjM5NDk2MzYyMg==               HR人力资源        人力       hrchina
   MzIwNDU2NzI0NQ==               技术前沿          技术       techfrontier
   ```

3. **上传导入**
   - 在管理页面选择Excel文件
   - 点击"导入"按钮
   - 查看导入结果

### 方式2：手动搜索添加（适用于少量公众号）

1. 访问 `http://localhost:8000/manage.html`
2. 在搜索框输入公众号关键词
3. 点击"搜索"按钮
4. 点击"添加"按钮添加公众号
5. 在数据库中手动设置分类

## 🎯 前端使用

### 按分类浏览
- 访问 `http://localhost:8000/`
- 顶部显示四个彩色分类卡片
- 点击任意卡片，只显示该分类下的文章
- 点击"✕"或"全部文章"按钮清除筛选

### 四个分类
- 🎮 **游戏** - 游戏开发资讯
- 💡 **产品** - 产品设计思考
- 👥 **人力** - 人力资源管理
- 💻 **技术** - 技术前沿动态

## 📁 文件清单

### 后端文件
- `backend/app/models/channel.py` - 添加category字段
- `backend/app/schemas/channel.py` - 更新Schema
- `backend/app/routers/channels.py` - Excel导入API
- `backend/app/routers/articles.py` - 按分类筛选文章
- `backend/app/schemas/article.py` - 文章响应包含category
- `backend/app/main.py` - 添加模板下载路由

### 前端文件
- `backend/app/static/index.html` - 更新主页显示分类卡片
- `backend/app/static/manage.html` - 添加Excel导入功能

### 文档文件
- `channel_import_template.xlsx` - Excel导入模板
- `BATCH_IMPORT_GUIDE.md` - 详细使用指南

## 🔧 配置说明

当前系统配置：
- 每次同步获取 **365天内** 的文章
- 每个公众号最多获取 **50篇** 文章
- 每次搜索可返回 **20个** 公众号结果

## ⚠️ 注意事项

1. **分类必须准确**：category字段只能是"游戏"、"产品"、"人力"、"技术"之一
2. **fakeid获取**：需要通过微信公众号后台或开发者工具获取
3. **Excel格式**：必须使用xlsx格式
4. **数据库更新**：如果数据库已有数据，category字段默认为"未分类"
5. **服务重启**：修改后需要重启后端服务

## 🚀 快速开始

```bash
# 1. 停止现有服务
# 在PowerShell中运行：
Get-Process -Name python | Where-Object {$_.WS -gt 50000} | Stop-Process -Force

# 2. 启动后端服务
cd c:/Users/kaiboy/Desktop/wechat-channel-crawler/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 访问前端
# 打开浏览器访问：http://localhost:8000/

# 4. 开始导入公众号
# 访问管理页面：http://localhost:8000/manage.html
```

## 📞 常见问题

### Q: 如何获取公众号的fakeid？
A: 通过微信公众号后台的API，使用开发者工具查找fakeid字段

### Q: 导入后分类显示为"未分类"？
A: 检查Excel中的category字段是否正确填写

### Q: 可以一次导入多少个公众号？
A: 建议不超过1000个，导入100个大约需要10-30秒

### Q: 如何修改已有公众号的分类？
A: 目前需要通过数据库直接修改，或删除后重新添加

## 🎉 功能完成

所有功能已经实现并测试通过！现在你可以：
1. ✅ 通过Excel批量导入大量公众号
2. ✅ 按照游戏、产品、人力、技术四个分类组织公众号
3. ✅ 在前端按分类浏览文章
4. ✅ 一年内最多50篇文章的全面同步
