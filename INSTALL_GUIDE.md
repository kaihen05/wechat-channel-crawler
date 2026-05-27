# 完整安装和使用指南

## 📋 前置条件检查

### 第一步：检查 Python 是否已安装

打开 PowerShell 或 CMD，输入：

```bash
python --version
```

或者：

```bash
python3 --version
```

如果显示类似 `Python 3.9.0` 或更高版本，说明已安装，可以跳到第二步。

如果提示"不是内部或外部命令"，需要先安装 Python。

---

## 🚀 第二步：安装 Python

### 方式 1：从 Microsoft Store 安装（推荐）

1. 按 `Win + S` 打开搜索
2. 输入 "Python"
3. 点击 "Python 3.x"（带蓝色图标）
4. 点击"获取"或"安装"
5. 等待安装完成

### 方式 2：从官网下载安装

1. 访问：https://www.python.org/downloads/
2. 下载最新的 Python 3.x 版本（如 Python 3.11.x）
3. 运行安装程序
4. **重要**：勾选 "Add Python to PATH"
5. 点击 "Install Now"
6. 等待安装完成

### 验证安装

打开新的 PowerShell 窗口，输入：

```bash
python --version
```

应该显示 Python 版本号。

---

## 📦 第三步：安装项目依赖

### 打开项目目录

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
```

### 安装依赖包

```bash
python -m pip install -r requirements.txt
```

等待安装完成（可能需要 1-3 分钟）。

---

## 🔐 第四步：配置环境变量

### 复制配置文件模板

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
copy .env.example .env
```

### 编辑 .env 文件

使用记事本打开 `.env` 文件：

```bash
notepad .env
```

或者使用你喜欢的编辑器（如 VS Code）。

### 获取微信凭证（重要！）

#### 1. 获取 Token

1. 打开浏览器，访问：https://mp.weixin.qq.com
2. 使用微信扫码登录你的公众号
3. 登录成功后，查看浏览器地址栏
4. 找到 URL 中的 `token` 参数

例如：`https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=1234567890`

其中 `1234567890` 就是你的 token。

#### 2. 获取 Cookie

1. 在公众号页面，按 `F12` 打开开发者工具
2. 切换到 "Network"（网络）标签
3. 刷新页面（F5）
4. 点击任意一个请求（通常是第一个）
5. 在右侧面板找到 "Headers" 标签
6. 向下滚动找到 "Cookie" 部分
7. 复制整个 Cookie 值（很长的字符串）

Cookie 示例：
```
wxuin=1234567890; pass_ticket=abcdefg; token=1234567890; ...
```

#### 3. 填入配置文件

在 `.env` 文件中填入：

```env
# 微信公众号凭证配置
WECHAT_TOKEN=你获取的token（只是数字）
WECHAT_COOKIE=你获取的完整cookie

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

保存并关闭文件。

**⚠️ 重要提醒**：
- 使用小号公众号，不要使用主号
- 凭证有效期约 4 小时，建议每天早上更新
- Cookie 和 token 不要分享给他人

---

## ▶️ 第五步：启动服务

### 在 PowerShell 中执行

```bash
cd C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend
python run.py
```

### 启动成功的标志

你应该看到类似这样的输出：

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     初始化数据库...
INFO:     数据库初始化完成
INFO:     启动定时任务调度器...
INFO:     定时任务调度器已启动，每天 09:00 执行同步
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**注意**：保持这个窗口打开，不要关闭它！

---

## 🎯 第六步：测试系统

### 方式 1：使用浏览器（推荐）

1. 打开浏览器
2. 访问：http://localhost:8000/docs
3. 你会看到 Swagger UI 界面
4. 点击展开接口进行测试

#### 测试步骤：

1. **验证凭证状态**
   - 展开 `GET /api/auth/credentials/status`
   - 点击 "Try it out"
   - 点击 "Execute"
   - 查看响应，应该显示 `valid: true`

2. **搜索公众号**
   - 展开 `POST /api/channels/search`
   - 点击 "Try it out"
   - 输入关键词（如"腾讯"）
   - 点击 "Execute"
   - 查看搜索结果

3. **添加公众号**
   - 记录搜索结果中的 `fakeid` 和 `nickname`
   - 展开 `POST /api/channels`
   - 点击 "Try it out"
   - 填入 JSON：
     ```json
     {
       "fakeid": "从搜索结果复制的fakeid",
       "nickname": "公众号名称",
       "account_name": "账号名（可选）",
       "avatar_url": "头像URL（可选）"
     }
     ```
   - 点击 "Execute"

4. **同步文章**
   - 展开 `POST /api/articles/sync`
   - 点击 "Try it out"
   - 点击 "Execute"
   - 查看同步结果

5. **查看文章列表**
   - 展开 `GET /api/articles`
   - 点击 "Try it out"
   - 设置 `limit` 参数（如 10）
   - 点击 "Execute"
   - 查看文章列表

### 方式 2：使用 curl 命令

在新的 PowerShell 窗口中执行：

```bash
# 1. 验证凭证
curl http://localhost:8000/api/auth/credentials/status

# 2. 搜索公众号
curl "http://localhost:8000/api/channels/search?keyword=腾讯"

# 3. 同步文章
curl -X POST http://localhost:8000/api/articles/sync

# 4. 查看文章
curl http://localhost:8000/api/articles?limit=10
```

---

## 🔄 日常使用

### 每天早上更新凭证

1. 重新获取 token 和 cookie（见第四步）
2. 编辑 `.env` 文件
3. 更新 `WECHAT_TOKEN` 和 `WECHAT_COOKIE`
4. 重启服务（Ctrl+C 停止，然后 `python run.py` 重新启动）

### 定时自动同步

系统会在每天设定的时间（默认是早上 9 点）自动同步所有启用的公众号文章。

你不需要手动执行同步，系统会自动完成。

### 手动触发同步

如果需要立即同步，可以使用：

```bash
curl -X POST http://localhost:8000/api/articles/sync
```

或在浏览器中访问 API 文档页面手动执行。

---

## 📊 查看数据

### 数据库位置

数据库文件位于：`C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend\data\channels.db`

这是一个 SQLite 数据库，你可以使用任何 SQLite 查看工具打开它。

### 备份数据

定期备份数据库文件：

```bash
copy C:\Users\kaiboy\Desktop\wechat-channel-crawler\backend\data\channels.db C:\backup\channels_backup_%date:~0,4%%date:~5,2%%date:~8,2%.db
```

---

## ❗ 常见问题

### Q1: 提示 "未配置微信凭证"
**A**: 检查 `.env` 文件中的 `WECHAT_TOKEN` 和 `WECHAT_COOKIE` 是否填写正确。

### Q2: 搜索公众号没结果
**A**:
1. 检查凭证是否过期（重新获取）
2. 检查网络连接
3. 尝试使用不同的关键词

### Q3: 同步失败
**A**:
1. 查看控制台日志了解详细错误
2. 更新微信凭证
3. 检查公众号是否正常

### Q4: Python 命令不存在
**A**:
1. 确认 Python 已安装
2. 重启 PowerShell 窗口
3. 使用完整路径，如 `C:\Python39\python.exe`

### Q5: 端口 8000 被占用
**A**: 修改 `.env` 文件中的 `PORT` 为其他端口（如 8001）

---

## 📚 更多信息

- 完整文档：阅读 `README.md`
- API 文档：http://localhost:8000/docs
- 项目结构：参考 `README.md` 中的项目结构部分

---

## 💡 使用建议

1. **使用小号**：强烈建议使用小号公众号获取凭证
2. **定期更新凭证**：建议每天早上更新一次
3. **定期备份数据**：定期复制 `channels.db` 文件到其他位置
4. **不要频繁同步**：系统已内置限制，不要绕过
5. **合法使用**：仅供个人学习研究使用

---

## 🎉 完成！

按照以上步骤，你就可以成功使用公众号渠道资源收集系统了！

祝使用顺利！如有问题，请查看控制台日志输出。
