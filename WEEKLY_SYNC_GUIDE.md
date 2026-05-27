# 每周定时爬虫和Excel导出功能说明

## 🎯 新增功能概述

在原有的公众号渠道资源收集系统基础上，新增了以下功能：

1. **每周定时爬虫** - 每周指定时间自动同步公众号文章
2. **Excel自动导出** - 每周同步后自动导出文章到Excel
3. **导出日志记录** - 记录所有导出操作的历史
4. **灵活的导出选项** - 支持按时间范围、公众号筛选导出

## 📋 配置说明

### 环境变量配置 (`.env` 文件)

```env
# 每天同步配置
DAILY_SCHEDULE_HOUR=9          # 每天几点同步（0-23）
DAILY_SCHEDULE_MINUTE=0        # 每天几分同步（0-59）

# 每周同步配置
WEEKLY_DAY=0                 # 星期几（0=周一，1=周二...6=周日）
WEEKLY_HOUR=9                # 每周几点同步（0-23）
WEEKLY_MINUTE=0              # 每周几分同步（0-59）

# Excel自动导出配置
AUTO_EXPORT_WEEKLY=true       # 是否每周自动导出（true/false）
EXPORT_DIRECTORY=./exports     # Excel文件导出目录
EXPORT_FILENAME_PREFIX=articles  # 导出文件名前缀

# 默认获取前几天的文章
DEFAULT_DAYS=3
```

### 定时任务时间设置说明

#### 每天同步
- `DAILY_SCHEDULE_HOUR`：每天同步的小时（0-23）
- `DAILY_SCHEDULE_MINUTE`：每天同步的分钟（0-59）
- 示例：设置为 `9:0` 表示每天早上9点自动同步

#### 每周同步
- `WEEKLY_DAY`：星期几（0=周一，1=周二，2=周三，3=周四，4=周五，5=周六，6=周日）
- `WEEKLY_HOUR`：每周同步的小时（0-23）
- `WEEKLY_MINUTE`：每周同步的分钟（0-59）
- 示例：设置为 `0,9,0` 表示每周一早上9点自动同步

## 📊 Excel导出功能

### 自动导出

当 `AUTO_EXPORT_WEEKLY=true` 时，系统会在每周同步完成后自动导出Excel文件。

### 手动导出

可以通过API接口手动导出Excel文件。

#### API接口

##### 1. 导出指定时间范围的文章
```
GET /api/export/excel?days=7
```

参数说明：
- `days`：导出最近几天的文章（如7表示最近一周），不填则导出全部
- `channel_id`：指定公众号ID，不填则导出所有公众号
- `filename`：自定义文件名，不填则自动生成

**示例：**
```bash
# 导出最近7天的文章
curl "http://localhost:8000/api/export/excel?days=7"

# 导出指定公众号的文章
curl "http://localhost:8000/api/export/excel?channel_id=1"

# 自定义文件名
curl "http://localhost:8000/api/export/excel?days=7&filename=my_articles.xlsx"
```

##### 2. 导出最近一周的文章
```
GET /api/export/excel/week
```

##### 3. 导出所有文章
```
GET /api/export/excel/all
```

##### 4. 查看导出日志
```
GET /api/export/logs?limit=20&offset=0
```

##### 5. 查看导出统计
```
GET /api/export/stats
```

### Excel文件格式

导出的Excel文件包含以下列：

| 列名 | 说明 |
|------|------|
| 公众号 | 文章所属公众号名称 |
| 标题 | 文章标题 |
| 作者 | 文章作者 |
| 发布时间 | 文章发布时间 |
| 收集时间 | 文章收集时间 |
| 摘要 | 文章摘要（最多200字） |
| 文章链接 | 文章完整链接 |

### Excel文件位置

默认导出目录：`./exports/`

文件命名格式：`articles_YYYYMMDD_HHMMSS.xlsx`

示例：`articles_20260413_143015.xlsx`

## 🚀 使用示例

### 场景1：每周一早上9点自动同步并导出

1. 配置 `.env` 文件：
```env
DAILY_SCHEDULE_HOUR=9
DAILY_SCHEDULE_MINUTE=0
WEEKLY_DAY=0
WEEKLY_HOUR=9
WEEKLY_MINUTE=0
AUTO_EXPORT_WEEKLY=true
```

2. 重启服务

3. 系统会：
   - 每天早上9点自动同步文章
   - 每周一早上9点自动同步并导出Excel到 `./exports/` 目录

### 场景2：手动导出最近一周的文章

使用浏览器访问：http://localhost:8000/api/export/excel/week

或使用命令行：
```bash
curl "http://localhost:8000/api/export/excel/week" -o week_articles.xlsx
```

### 场景3：导出特定公众号的所有文章

```bash
curl "http://localhost:8000/api/export/excel?channel_id=1" -o channel_articles.xlsx
```

### 场景4：查看导出历史

```bash
curl "http://localhost:8000/api/export/logs"
```

## 📁 新增文件

### 后端文件

1. **服务层**
   - `backend/app/services/excel_export.py` - Excel导出服务
   - `backend/app/services/scheduler.py` - 更新支持每周定时任务

2. **数据模型**
   - `backend/app/models/export_log.py` - 导出日志模型

3. **API路由**
   - `backend/app/routers/export.py` - Excel导出API接口

4. **配置更新**
   - `backend/app/config.py` - 新增每周同步和Excel导出配置
   - `backend/requirements.txt` - 新增Excel相关依赖

## 🔧 安装新依赖

由于新增了Excel导出功能，需要安装额外的依赖：

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
pip install openpyxl pandas
```

或重新安装所有依赖：

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
pip install -r requirements.txt
```

## ⚠️ 注意事项

1. **定时任务配置**：
   - 每天同步和每周同步可以同时启用
   - 每周同步后如果启用了自动导出，会自动生成Excel文件

2. **Excel导出目录**：
   - 默认导出到 `./exports/` 目录
   - 确保该目录有写入权限
   - 定期清理旧文件避免占用磁盘空间

3. **自动导出**：
   - 自动导出的Excel文件保存在服务器上
   - 可以通过访问导出日志查看文件路径

4. **文件大小限制**：
   - 文章摘要限制在200字以内
   - 单次导出大量文章可能需要较长时间

5. **性能考虑**：
   - 建议分批导出大量数据
   - 可以设置 `days` 参数限制导出时间范围

## 📈 导出日志系统

### 查看导出历史

访问：http://localhost:8000/api/export/logs

响应示例：
```json
[
  {
    "id": 1,
    "filename": "articles_20260413_143015.xlsx",
    "filepath": "./exports/articles_20260413_143015.xlsx",
    "article_count": 150,
    "days": 7,
    "channel_id": null,
    "auto_export": false,
    "exported_at": "2026-04-13T14:30:15",
    "notes": null
  }
]
```

### 查看导出统计

访问：http://localhost:8000/api/export/stats

响应示例：
```json
{
  "total_exports": 10,
  "total_articles": 1500,
  "auto_exports": 4,
  "manual_exports": 6,
  "last_export": "2026-04-13T14:30:15"
}
```

## 🎯 完整工作流程

### 每周自动化流程

1. **定时触发**（每周一 9:00）
   - 调度器触发每周同步任务

2. **同步文章**
   - 调用同步接口获取所有启用公众号的最新文章
   - 保存到数据库

3. **等待完成**（60秒）
   - 确保同步完全完成

4. **自动导出Excel**
   - 导出最近一周的文章
   - 生成Excel文件到 `./exports/` 目录
   - 记录导出日志

5. **完成**
   - 日志输出导出结果
   - 文件可供下载

## 💡 使用建议

1. **定时任务时间**：
   - 建议设置在业务低峰期（如早上或晚上）
   - 避免设置在整点，分散负载

2. **导出频率**：
   - 每周导出一次即可满足日常需求
   - 可根据需要调整频率

3. **文件管理**：
   - 定期清理旧的Excel文件
   - 建议保留最近1-3个月的导出记录

4. **备份策略**：
   - 定期备份 `./exports/` 目录
   - 将重要导出文件移动到永久存储位置

## 🔍 故障排查

### 定时任务没有执行

1. 检查 `.env` 配置是否正确
2. 查看服务日志输出
3. 确认服务正在运行

### Excel导出失败

1. 检查 `./exports/` 目录是否存在且有写权限
2. 查看错误日志
3. 确认已安装 `openpyxl` 和 `pandas` 包

### 自动导出没有生成文件

1. 检查 `AUTO_EXPORT_WEEKLY=true` 是否设置
2. 确认每周同步任务是否正常执行
3. 查看导出日志记录

## 📚 更多信息

- 完整API文档：http://localhost:8000/docs
- 主项目文档：README.md
- 快速开始指南：QUICKSTART.md
