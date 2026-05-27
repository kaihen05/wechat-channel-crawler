# 微信 API 凭证配置 - 完整指南

## 📚 文档索引

### 配置指南
1. **[HOW_TO_CONFIG_WECHAT_API.md](./HOW_TO_CONFIG_WECHAT_API.md)** - 详细配置说明
   - 如何获取 AppID 和 AppSecret
   - 两种配置方法（.env 和 config.py）
   - 验证和测试步骤
   - 常见问题解答

2. **[TROUBLESHOOTING_WECHAT_API.md](./TROUBLESHOOTING_WECHAT_API.md)** - 故障排查清单
   - 快速检查清单
   - 常见解决方案
   - 完整配置步骤
   - 配置成功的标志

### 功能说明
3. **[WECHAT_API_READ_NUM.md](./WECHAT_API_READ_NUM.md)** - 功能使用说明
4. **[WECHAT_API_QUICKSTART.md](./WECHAT_API_QUICKSTART.md)** - 快速开始指南
5. **[WECHAT_API_LIMITS.md](./WECHAT_API_LIMITS.md)** - API 调用限制说明
6. **[WECHAT_API_CALL_RULES.md](./WECHAT_API_CALL_RULES.md)** - 调用规则与最佳实践

---

## 🚀 快速开始（3 步配置）

### 步骤 1: 获取凭证

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「设置与开发」->「基本配置」
3. 获取 AppID 和 AppSecret

### 步骤 2: 配置系统

**方法 A: 使用配置向导（推荐）**
```bash
cd backend
python setup_wechat_api.py
```

**方法 B: 手动配置**
```bash
# 编辑 backend/.env 文件
WECHAT_APPID=你的AppID
WECHAT_APPSECRET=你的AppSecret
```

### 步骤 3: 重启服务器

```bash
# 停止当前服务器（Ctrl + C）

# 重新启动
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤 4: 验证配置

```bash
cd backend
python test_wechat_api.py
```

---

## 🛠️ 配置工具

### 1. 配置向导脚本
```bash
cd backend
python setup_wechat_api.py          # 交互式配置
python setup_wechat_api.py check    # 检查当前配置
```

### 2. 测试脚本
```bash
cd backend
python test_wechat_api.py           # 测试 API 连接
```

### 3. 配置示例文件
```bash
backend/.env.example                # 环境变量示例
```

---

## ✅ 配置检查清单

配置完成后，请检查以下项目：

- [ ] 已创建或编辑 `.env` 文件
- [ ] 已添加 `WECHAT_APPID` 配置
- [ ] 已添加 `WECHAT_APPSECRET` 配置
- [ ] AppID 格式正确（wx 开头，18 位）
- [ ] AppSecret 格式正确（32 位）
- [ ] 已保存文件
- [ ] 已重启服务器
- [ ] 运行测试脚本验证
- [ ] 检查日志没有错误

---

## ❓ 常见问题速查

### 问题 1: 提示"未配置微信公众号 API 凭证"

**快速解决：**
```bash
cd backend
python setup_wechat_api.py
```

**详细说明：** 查看 [HOW_TO_CONFIG_WECHAT_API.md](./HOW_TO_CONFIG_WECHAT_API.md)

---

### 问题 2: 配置后仍然报错

**检查清单：**
1. 文件位置是否正确（应该在 `backend/.env`）
2. 文件名是否正确（必须带点 `.env`）
3. 配置格式是否正确（没有引号，没有空格）
4. 是否重启了服务器
5. 运行检查脚本：`python setup_wechat_api.py check`

**详细说明：** 查看 [TROUBLESHOOTING_WECHAT_API.md](./TROUBLESHOOTING_WECHAT_API.md)

---

### 问题 3: 如何获取 AppID 和 AppSecret？

**步骤：**
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「设置与开发」->「基本配置」
3. 查看开发者ID (AppID)
4. 重置/启用开发者密码 (AppSecret)

**详细说明：** 查看 [HOW_TO_CONFIG_WECHAT_API.md](./HOW_TO_CONFIG_WECHAT_API.md#步骤-2获取-appid-和-appsecret)

---

### 问题 4: 忘记了 AppSecret 怎么办？

**解决方法：**
1. 登录微信公众平台
2. 进入「设置与开发」->「基本配置」
3. 点击 AppSecret 旁边的「重置」
4. 扫码验证身份
5. 获取新的 AppSecret
6. 更新配置文件

---

### 问题 5: 使用的公众号不是认证的，能用这个功能吗？

**答案：** 不能。

**要求：**
- ✅ 认证服务号（推荐）
- ✅ 认证订阅号
- ❌ 未认证服务号
- ❌ 未认证订阅号

**如何查看：** 登录微信公众平台，查看账号信息，确认是否有「已认证」标识。

---

## 📊 配置示例

### .env 文件示例

```bash
# 微信公众号 API 凭证
WECHAT_APPID=wx1234567890abcdef
WECHAT_APPSECRET=1234567890abcdefghijklmnopqrstuvwxyz

# 其他配置（可选）
DATABASE_URL=sqlite:///./data/channels.db
HOST=0.0.0.0
PORT=8000
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

## 🔒 安全提醒

### ⚠️ 重要事项

1. **不要泄露 AppSecret**
   - 不要提交到代码仓库（git）
   - 不要分享给他人
   - 不要在公开场所显示

2. **保护 .env 文件**
   ```bash
   # 将 .env 添加到 .gitignore
   echo ".env" >> .gitignore
   ```

3. **定期更换凭证**
   - 建议每 3-6 个月更换一次 AppSecret
   - 怀疑泄露时立即更换

---

## 📞 获取帮助

### 文档资源
- **配置说明：** [HOW_TO_CONFIG_WECHAT_API.md](./HOW_TO_CONFIG_WECHAT_API.md)
- **故障排查：** [TROUBLESHOOTING_WECHAT_API.md](./TROUBLESHOOTING_WECHAT_API.md)
- **快速开始：** [WECHAT_API_QUICKSTART.md](./WECHAT_API_QUICKSTART.md)
- **功能说明：** [WECHAT_API_READ_NUM.md](./WECHAT_API_READ_NUM.md)

### 调试工具
```bash
# 检查配置
cd backend
python setup_wechat_api.py check

# 测试 API
python test_wechat_api.py

# 查看日志
type logs\*.log  # Windows
cat logs/*.log  # Linux/Mac
```

---

## 🎯 配置成功的标志

### 测试脚本输出
```
============================================================
微信 API 功能测试
============================================================

测试 1: 获取 access token 并更新文章阅读量
使用 AppID: wx1234567890abcdef
测试获取 access token...
成功获取 access token: 32_xxxxxxxxxxxxxxxxxxxxxxxxxx...
============================================================
测试完成！
============================================================
```

### Web 界面
- ✅ 不再提示"未配置微信公众号 API 凭证"
- ✅ 可以正常使用「通过微信 API 更新阅读量」功能
- ✅ 更新结果显示成功

---

## 📝 总结

### 最快的配置方法（1 分钟）

```bash
# 1. 运行配置向导
cd backend
python setup_wechat_api.py

# 2. 输入 AppID 和 AppSecret

# 3. 重启服务器
# 停止当前服务器（Ctrl + C）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 测试
python test_wechat_api.py
```

### 关键要点

1. **获取凭证**：登录微信公众平台获取 AppID 和 AppSecret
2. **配置系统**：使用配置向导或手动编辑 .env 文件
3. **重启服务器**：配置修改后必须重启服务器
4. **验证配置**：运行测试脚本确认配置正确

### 重要提醒

- ⚠️ AppSecret 是敏感信息，妥善保管
- ⚠️ 只能用于认证的服务号或订阅号
- ⚠️ 配置修改后必须重启服务器
- ⚠️ 不要将 .env 文件提交到代码仓库

---

**开始配置吧！** 🚀

运行以下命令开始：
```bash
cd backend
python setup_wechat_api.py
```
