# 微信 API 配置故障排查清单

## 问题：提示"未配置微信公众号 API 凭证"

### ✅ 快速检查清单

请按顺序检查以下项目：

#### 1. 检查 .env 文件是否存在

```bash
cd backend
dir .env  # Windows
ls -la .env  # Linux/Mac
```

- [ ] .env 文件存在
- [ ] 文件在 `backend` 目录下
- [ ] 文件名是 `.env`（不是 `.env.txt`）

**如果文件不存在：**
```bash
# 复制示例文件
copy .env.example .env  # Windows
cp .env.example .env  # Linux/Mac

# 或者使用配置向导
python setup_wechat_api.py
```

---

#### 2. 检查 .env 文件内容

```bash
type .env  # Windows
cat .env  # Linux/Mac
```

- [ ] 包含 `WECHAT_APPID=` 行
- [ ] 包含 `WECHAT_APPSECRET=` 行
- [ ] 等号后面有值（不是空的）
- [ ] 没有多余的空格

**正确的格式：**
```bash
WECHAT_APPID=wx1234567890abcdef
WECHAT_APPSECRET=1234567890abcdefghijklmnopqrstuvwxyz
```

**错误的格式：**
```bash
# ❌ 错误：有引号
WECHAT_APPID="wx1234567890abcdef"

# ❌ 错误：有空格
WECHAT_APPID = wx1234567890abcdef

# ❌ 错误：变量名错误
WechatAppId=wx1234567890abcdef

# ❌ 错误：值为空
WECHAT_APPID=
```

---

#### 3. 检查 AppID 和 AppSecret 格式

- [ ] AppID 以 `wx` 开头
- [ ] AppID 总共 18 个字符
- [ ] AppSecret 总共 32 个字符

**验证格式：**
```bash
# 检查 AppID 长度
python -c "appid='你的AppID'; print(f'长度: {len(appid)}')"  # 应该输出 18

# 检查 AppSecret 长度
python -c "secret='你的AppSecret'; print(f'长度: {len(secret)}')"  # 应该输出 32
```

---

#### 4. 检查 Python 能否读取配置

```bash
cd backend
python -c "from app.config import settings; print('AppID:', settings.wechat_appid); print('AppSecret:', settings.wechat_appsecret)"
```

- [ ] AppID 有输出（不是空）
- [ ] AppSecret 有输出（不是空）

**如果输出为空：**
- 检查是否安装了 `pydantic-settings`
- 检查 `config.py` 中的 `env_file` 配置
- 尝试直接在 `config.py` 中设置

---

#### 5. 检查是否重启了服务器

- [ ] 配置修改后已停止服务器
- [ ] 已重新启动服务器

**重启服务器：**
```bash
# 停止当前服务器（在运行服务器的终端按 Ctrl + C）

# 重新启动
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

#### 6. 运行配置检查脚本

```bash
cd backend
python setup_wechat_api.py check
```

- [ ] 脚本输出显示配置正确
- [ ] 没有错误信息

---

### 🔧 常见解决方案

#### 方案 1: 使用配置向导（最简单）

```bash
cd backend
python setup_wechat_api.py
```

按照提示输入 AppID 和 AppSecret。

---

#### 方案 2: 直接修改 config.py

如果 .env 文件不生效，直接修改 `backend/app/config.py`：

```python
class Settings(BaseSettings):
    # ... 其他配置 ...

    # 微信公众号 API 凭证
    wechat_appid: str = "wx1234567890abcdef"  # 👈 直接填在这里
    wechat_appsecret: str = "1234567890abcdefghijklmnopqrstuvwxyz"  # 👈 直接填在这里
```

保存后重启服务器。

---

#### 方案 3: 检查 Pydantic 版本

```bash
cd backend
pip install pydantic-settings
```

---

#### 方案 4: 重新创建 .env 文件

```bash
cd backend
# 备份旧文件
move .env .env.backup  # Windows
mv .env .env.backup  # Linux/Mac

# 使用配置向导创建新的
python setup_wechat_api.py
```

---

### 📋 完整配置步骤（从头开始）

如果你完全不确定配置是否正确，请按以下步骤重新配置：

#### 步骤 1: 获取凭证

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「设置与开发」->「基本配置」
3. 记录 AppID 和 AppSecret

#### 步骤 2: 使用配置向导

```bash
cd backend
python setup_wechat_api.py
```

输入你的 AppID 和 AppSecret。

#### 步骤 3: 验证配置

```bash
cd backend
python setup_wechat_api.py check
```

确认配置正确。

#### 步骤 4: 重启服务器

```bash
# 停止当前服务器（Ctrl + C）

# 重新启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 步骤 5: 测试功能

```bash
cd backend
python test_wechat_api.py
```

---

### ❓ 仍然无法解决？

请检查以下内容：

1. **公众号类型是否正确**
   - 必须是认证服务号或认证订阅号
   - 未认证的公众号没有 API 权限

2. **AppSecret 是否过期**
   - AppSecret 长期有效
   - 但可以手动重置
   - 重置后需要更新配置

3. **网络连接是否正常**
   - 确保能访问 `api.weixin.qq.com`
   - 检查防火墙设置

4. **查看详细日志**

```bash
cd backend
# 查看日志文件
type logs\*.log  # Windows
cat logs/*.log  # Linux/Mac
```

5. **查看微信官方文档**

访问：[微信公众平台文档](https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_appID_and_App_Secret.html)

---

### 📞 获取更多帮助

如果以上方法都无法解决问题：

1. 查看 [HOW_TO_CONFIG_WECHAT_API.md](./HOW_TO_CONFIG_WECHAT_API.md) - 详细配置说明
2. 查看 [WECHAT_API_READ_NUM.md](./WECHAT_API_READ_NUM.md) - 功能使用说明
3. 检查日志文件（`backend/logs/`）
4. 确认公众号类型和权限

---

### ✅ 配置成功的标志

如果配置成功，你应该看到：

**测试脚本输出：**
```
============================================================
微信 API 功能测试
============================================================

测试 1: 获取 access token 并更新文章阅读量
使用 AppID: wx1234567890abcdef
测试获取 access token...
成功获取 access token: 32_xxxxxxxxxxxxxxxxxxxxxxxxxx...
```

**Web 界面：**
- 不再提示"未配置微信公众号 API 凭证"
- 可以正常使用「通过微信 API 更新阅读量」功能

---

**记住：配置修改后必须重启服务器！** 🔄
