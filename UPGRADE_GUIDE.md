# 功能升级指南 - 每周定时和Excel导出

## 🎉 新增功能总结

在原有公众号渠道资源收集系统基础上，新增了以下功能：

1. ✅ **每周定时爬虫** - 每周指定时间自动同步
2. ✅ **Excel自动导出** - 每周同步后自动导出Excel
3. ✅ **导出日志记录** - 记录所有导出操作
4. ✅ **灵活导出** - 支持按时间、公众号筛选导出

## 📦 升级步骤

### 步骤 1：安装新依赖

打开 PowerShell，执行：

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
pip install openpyxl pandas
```

或重新安装所有依赖：

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
pip install -r requirements.txt
```

### 步骤 2：更新配置文件

编辑 `.env` 文件，添加以下配置：

```env
# 每天同步配置
DAILY_SCHEDULE_HOUR=9
DAILY_SCHEDULE_MINUTE=0

# 每周同步配置（0=周一，1=周二...6=周日）
WEEKLY_DAY=0
WEEKLY_HOUR=9
WEEKLY_MINUTE=0

# Excel自动导出配置
AUTO_EXPORT_WEEKLY=true
EXPORT_DIRECTORY=./exports
EXPORT_FILENAME_PREFIX=articles
```

### 步骤 3：重启服务

```bash
# 停止当前运行的服务（Ctrl+C）

# 重新启动
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
python run.py
```

### 步骤 4：验证功能

1. 访问 http://localhost:8000/docs
2. 查看 "Excel导出" 相关的API接口
3. 测试导出功能

## 🎯 使用示例

### 配置每周一早上9点自动同步并导出

在 `.env` 文件中配置：

```env
DAILY_SCHEDULE_HOUR=9
DAILY_SCHEDULE_MINUTE=0
WEEKLY_DAY=0
WEEKLY_HOUR=9
WEEKLY_MINUTE=0
AUTO_EXPORT_WEEKLY=true
```

### 手动导出Excel

#### 导出最近一周的文章

```bash
curl "http://localhost:8000/api/export/excel/week" -o week_articles.xlsx
```

或使用浏览器访问：http://localhost:8000/api/export/excel/week

#### 导出所有文章

```bash
curl "http://localhost:8000/api/export/excel/all" -o all_articles.xlsx
```

#### 导出指定公众号的文章

```bash
curl "http://localhost:8000/api/export/excel?channel_id=1" -o channel_articles.xlsx
```

#### 查看导出日志

```bash
curl "http://localhost:8000/api/export/logs"
```

#### 查看导出统计

```bash
curl "http://localhost:8000/api/export/stats"
```

## 📊 Excel文件格式

导出的Excel文件包含以下列：

- **公众号** - 文章所属公众号名称
- **标题** - 文章标题
- **作者** - 文章作者
- **发布时间** - 文章发布时间
- **收集时间** - 文章收集时间
- **摘要** - 文章摘要（最多200字）
- **文章链接** - 文章完整链接

## 📁 Excel文件位置

默认导出目录：`C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend\exports\`

文件命名格式：`articles_YYYYMMDD_HHMMSS.xlsx`

示例：`articles_20260413_143015.xlsx`

## ⚙️ 配置详解

### 每天同步 vs 每周同步

你可以同时启用每天同步和每周同步：

- **每天同步**：每天早上9点自动同步最新文章
- **每周同步**：每周一早上9点自动同步并导出Excel

配置示例：

```env
# 每天早上9点同步
DAILY_SCHEDULE_HOUR=9
DAILY_SCHEDULE_MINUTE=0

# 每周一早上9点同步并导出
WEEKLY_DAY=0
WEEKLY_HOUR=9
WEEKLY_MINUTE=0
AUTO_EXPORT_WEEKLY=true
```

### 定时任务时间设置

`WEEKLY_DAY` 说明：
- 0 = 周一
- 1 = 周二
- 2 = 周三
- 3 = 周四
- 4 = 周五
- 5 = 周六
- 6 = 周日

### 禁用自动导出

如果你只想定时同步，不想自动导出Excel，设置：

```env
AUTO_EXPORT_WEEKLY=false
```

## 🔍 完整工作流程

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

## ❓ 常见问题

### Q: 升级后原来的数据会丢失吗？

A: 不会。升级只是增加了新功能，不会影响原有的数据库和配置。

### Q: 可以只使用每周同步，不用每天同步吗？

A: 可以。设置 `WEEKLY_DAY` 参数即可，不需要设置每天同步的参数。

### Q: Excel文件导出到哪里了？

A: 默认导出到 `backend/exports/` 目录。你可以通过配置 `EXPORT_DIRECTORY` 修改导出路径。

### Q: 如何查看导出历史？

A: 访问 http://localhost:8000/api/export/logs 查看所有导出记录。

### Q: 自动导出的Excel文件会覆盖旧的吗？

A: 不会。每次导出都会生成新的文件，文件名包含时间戳。

## 📚 相关文档

- **完整功能说明**：[WEEKLY_SYNC_GUIDE.md](WEEKLY_SYNC_GUIDE.md)
- **项目文档**：[README.md](README.md)
- **快速开始**：[QUICKSTART.md](QUICKSTART.md)
- **安装指南**：[INSTALL_GUIDE.md](INSTALL_GUIDE.md)

## ✅ 升级检查清单

升级完成后，确认以下功能正常：

- [ ] 服务启动成功，日志显示定时任务已启动
- [ ] 访问 http://localhost:8000/docs 看到新的导出接口
- [ ] 可以手动导出Excel文件
- [ ] 可以查看导出日志
- [ ] 配置的定时时间正确（查看日志输出）

## 🎉 完成！

升级完成！现在你的系统支持：
- ✅ 每天定时同步
- ✅ 每周定时同步
- ✅ 每周自动导出Excel
- ✅ 灵活的手动导出
- ✅ 完整的导出日志

享受自动化的公众号文章收集和整理吧！
