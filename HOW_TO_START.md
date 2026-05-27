# 如何启动服务

## 🚀 快速启动（推荐）

### 方法1：使用启动脚本（最简单）

1. 双击 `start.bat` 文件
2. 等待服务启动
3. 打开浏览器访问：http://localhost:8000/docs

### 方法2：使用快速启动脚本

1. 双击 `quick_start.bat` 文件
2. 等待服务启动
3. 打开浏览器访问：http://localhost:8000/docs

### 方法3：使用命令行

打开 PowerShell，执行：

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
python run.py
```

## ✅ 启动成功的标志

看到以下输出表示启动成功：

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     初始化数据库...
INFO:     数据库初始化完成
INFO:     启动定时任务调度器...
INFO:     每天定时任务已启动，每天 09:00 执行
INFO:     每周定时任务已启动，每周一 09:00 执行
INFO:     每周自动导出已启用
INFO:     定时任务调度器已启动
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 🌐 访问API文档

启动成功后，在浏览器中访问：

- **API文档**：http://localhost:8000/docs
- **根路径**：http://localhost:8000
- **健康检查**：http://localhost:8000/health

## 🛑 停止服务

在运行服务的窗口中按 `Ctrl+C` 即可停止服务。

## ❓ 常见问题

### Q1: 双击bat文件没有反应？

A: 右键点击bat文件，选择"以管理员身份运行"。

### Q2: 提示"Python不是内部或外部命令"？

A: 说明Python没有添加到PATH。需要：
1. 找到Python安装路径
2. 将Python安装目录添加到系统PATH环境变量
3. 或使用完整路径运行

### Q3: 提示端口8000被占用？

A: 修改 `backend/.env` 文件中的 `PORT` 配置为其他端口（如8001）

### Q4: 访问不到 http://localhost:8000？

A: 检查以下几点：
1. 确认服务已启动（查看窗口输出）
2. 确认没有错误信息
3. 尝试访问 http://127.0.0.1:8000
4. 检查防火墙设置

### Q5: 启动失败，提示模块未找到？

A: 重新安装依赖：

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
pip install -r requirements.txt
```

## 📝 首次使用配置

首次启动前，需要配置微信凭证：

1. 编辑 `backend/.env` 文件
2. 填入 `WECHAT_TOKEN` 和 `WECHAT_COOKIE`
3. 重启服务

详细配置方法请参考 `INSTALL_GUIDE.md`。

## 🎯 启动后做什么？

1. 访问 http://localhost:8000/docs 查看API文档
2. 测试搜索公众号功能
3. 添加你关注的公众号
4. 执行文章同步
5. 导出Excel查看结果

## 💡 小贴士

- 保持启动窗口打开，不要关闭
- 可以最小化窗口，让它在后台运行
- 定期查看日志输出了解系统状态
- 记得每天更新微信凭证

## 🔧 故障排查

如果仍然无法访问，请检查：

1. **Python版本**：必须是 Python 3.9 或更高
2. **依赖安装**：确认所有依赖都已安装
3. **配置文件**：确认 `.env` 文件存在且格式正确
4. **端口占用**：确认8000端口没有被其他程序占用
5. **防火墙**：确认防火墙允许Python访问网络

查看详细日志可以帮助诊断问题，所有日志都会显示在启动窗口中。
