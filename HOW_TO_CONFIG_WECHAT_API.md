# 如何配置微信公众号 API 凭证

## 错误说明

当你看到以下错误时：

```
错误: 未配置微信公众号 API 凭证，请在配置文件中设置 wechat_appid 和 wechat_appsecret
```

这是因为系统没有找到微信 API 的 AppID 和 AppSecret 配置。

---

## 解决方法

### 方法 1: 使用 .env 文件（推荐）

#### 步骤 1: 创建或编辑 .env 文件

在 `backend` 目录下创建或编辑 `.env` 文件：

```bash
cd backend
notepad .env  # 或使用其他编辑器
```

#### 步骤 2: 添加配置

在 `.env` 文件中添加以下内容：

```bash
# 微信公众号 API 凭证
WECHAT_APPID=你的AppID
WECHAT_APPSECRET=你的AppSecret
```

#### 步骤 3: 保存文件

保存 `.env` 文件。

---

### 方法 2: 直接修改 config.py 文件

#### 步骤 1: 打开配置文件

打开 `backend/app/config.py` 文件。

#### 步骤 2: 修改配置

找到以下配置项并填入你的凭证：

```python
class Settings(BaseSettings):
    # 微信凭证
    wechat_token: str = ""
    wechat_cookie: str = ""
    
    # 微信公众号 API 凭证（用于获取真实阅读量）
    wechat_appid: str = "你的AppID"  # 👈 填入这里
    wechat_appsecret: str = "你的AppSecret"  # 👈 填入这里
    wechat_access_token: str = ""
```

#### 步骤 3: 保存文件

保存 `config.py` 文件。

---

## 如何获取 AppID 和 AppSecret

### 步骤 1: 登录微信公众平台

访问：[https://mp.weixin.qq.com/](https://mp.weixin.qq.com/)

使用你的公众号管理员账号登录。

### 步骤 2: 进入基本配置

1. 点击左侧菜单「设置与开发」
2. 点击「基本配置」

### 步骤 3: 获取 AppID

在「开发者ID (AppID)」栏目下，你可以看到 AppID。

**示例：**
```
AppID: wx1234567890abcdef
```

### 步骤 4: 获取 AppSecret

在「开发者密码 (AppSecret)」栏目下：

1. 点击「重置」或「启用」按钮
2. 扫码验证身份（需要管理员扫码）
3. 获取 AppSecret

**重要：**
- ⚠️ AppSecret 只显示一次，请立即保存！
- ⚠️ 如果忘记，需要重新生成
- ⚠️ 不要分享给他人

**示例：**
```
AppSecret: 1234567890abcdefghijklmnopqrstuvwxyz
```

---

## 验证配置

### 方法 1: 运行测试脚本

```bash
cd backend
python test_wechat_api.py
```

如果配置正确，你会看到：

```
============================================================
微信 API 功能测试
============================================================

测试 1: 获取 access token 并更新文章阅读量
使用 AppID: wx1234567890abcdef
测试获取 access token...
成功获取 access token: 32_xxxxxxxxxxxxxxxxxxxxxxxxxx...
```

如果配置错误，你会看到：

```
未配置微信 API 凭证！
请在 backend/.env 或 backend/app/config.py 中设置：
  WECHAT_APPID=your_appid
  WECHAT_APPSECRET=your_appsecret
```

### 方法 2: 检查环境变量

```bash
cd backend
python -c "from app.config import settings; print('AppID:', settings.wechat_appid); print('AppSecret:', settings.wechat_appsecret)"
```

如果输出为空，说明配置未生效。

---

## 重启服务器

配置完成后，**必须重启服务器**才能生效。

### 步骤:

1. 停止当前运行的服务器
   - 在运行服务器的终端按 `Ctrl + C`

2. 重新启动服务器
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 常见问题

### Q1: 配置后仍然报错怎么办？

**A:** 检查以下几点：

1. **文件位置是否正确**
   - `.env` 文件应该在 `backend` 目录下
   - 路径应该是 `backend/.env`

2. **文件名是否正确**
   - 必须是 `.env`（注意前面的点）
   - 不能是 `.env.txt` 或其他名称

3. **配置是否正确**
   - 确认变量名是 `WECHAT_APPID`（大写）
   - 确认没有多余的空格

4. **是否重启了服务器**
   - 配置修改后必须重启服务器

5. **检查 .env 文件内容**
   ```bash
   cd backend
   type .env  # Windows
   cat .env   # Linux/Mac
   ```

---

### Q2: AppID 和 AppSecret 的格式是什么？

**A:**

- **AppID 格式**：`wx` 开头，后面跟 16 个字符
  - 示例：`wx1234567890abcdef`

- **AppSecret 格式**：32 个字符
  - 示例：`1234567890abcdefghijklmnopqrstuvwxyz`

---

### Q3: 忘记了 AppSecret 怎么办？

**A:** 需要重新生成：

1. 登录微信公众平台
2. 进入「设置与开发」->「基本配置」
3. 在「开发者密码 (AppSecret)」栏目下点击「重置」
4. 扫码验证身份
5. 获取新的 AppSecret
6. 更新配置文件

---

### Q4: 使用的公众号不是服务号或认证订阅号，能用这个功能吗？

**A:** 不能。需要满足以下条件：

- ✅ 认证服务号：可以（推荐）
- ✅ 认证订阅号：可以
- ❌ 未认证订阅号：不能
- ❌ 未认证服务号：不能

**如何查看公众号类型：**
1. 登录微信公众平台
2. 查看账号信息
3. 确认是否有「已认证」标识

---

### Q5: 配置了还是提示"未配置"，怎么办？

**A:** 尝试以下步骤：

1. **确认 Python 能读取配置**
   ```bash
   cd backend
   python -c "from app.config import settings; print('AppID:', settings.wechat_appid)"
   ```

2. **如果输出为空，检查 Pydantic 版本**
   ```bash
   pip install pydantic-settings
   ```

3. **尝试直接在 config.py 中设置**
   - 不使用 .env 文件
   - 直接在 `Settings` 类中设置默认值

---

## 安全提醒

### ⚠️ 重要事项

1. **不要泄露 AppSecret**
   - 不要提交到代码仓库（git）
   - 不要分享给他人
   - 不要在公开场所显示

2. **保护 .env 文件**
   - 将 .env 添加到 .gitignore
   ```
   echo ".env" >> .gitignore
   ```

3. **定期更换凭证**
   - 建议每 3-6 个月更换一次 AppSecret
   - 怀疑泄露时立即更换

---

## 配置示例

### .env 文件示例

```bash
# 基础配置
DATABASE_URL=sqlite:///./data/channels.db
HOST=0.0.0.0
PORT=8000

# 微信凭证
WECHAT_TOKEN=your_wechat_token
WECHAT_COOKIE=your_wechat_cookie

# 微信公众号 API 凭证
WECHAT_APPID=wx1234567890abcdef
WECHAT_APPSECRET=1234567890abcdefghijklmnopqrstuvwxyz
```

### config.py 文件示例

```python
class Settings(BaseSettings):
    # 微信凭证
    wechat_token: str = ""
    wechat_cookie: str = ""
    
    # 微信公众号 API 凭证
    wechat_appid: str = "wx1234567890abcdef"
    wechat_appsecret: str = "1234567890abcdefghijklmnopqrstuvwxyz"
    wechat_access_token: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

---

## 验证清单

配置完成后，请检查以下项目：

- [ ] 已创建或编辑 `.env` 文件
- [ ] 已添加 `WECHAT_APPID` 配置
- [ ] 已添加 `WECHAT_APPSECRET` 配置
- [ ] AppID 格式正确（wx 开头）
- [ ] AppSecret 格式正确（32 位）
- [ ] 已保存文件
- [ ] 已重启服务器
- [ ] 运行测试脚本验证
- [ ] 检查日志没有错误

---

## 下一步

配置成功后：

1. **运行测试脚本**
   ```bash
   cd backend
   python test_wechat_api.py
   ```

2. **通过 Web 界面使用**
   - 访问 `http://localhost:8000/manage.html`
   - 使用「通过微信 API 更新阅读量」功能

3. **查看详细文档**
   - [WECHAT_API_READ_NUM.md](./WECHAT_API_READ_NUM.md)
   - [WECHAT_API_QUICKSTART.md](./WECHAT_API_QUICKSTART.md)

---

## 需要帮助？

如果仍然遇到问题：

1. 检查日志文件（`backend/logs/`）
2. 确认公众号类型是否正确
3. 尝试使用另一个已认证的公众号
4. 查看微信官方文档

---

**记住：AppSecret 是敏感信息，请妥善保管！** 🔒
