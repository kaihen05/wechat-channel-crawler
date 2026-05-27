# 微信公众号 API 调用规则与最佳实践

## 📋 快速参考

### 推荐配置

**对于你的使用场景（8 个公众号）：**

```
策略: Conservative（保守）
每小时调用: 20 次
每日调用: 300 次
实际建议: 每日 3 次（远低于限制）
```

### 调用频率建议

| 时间 | 任务 | 调用次数 | 说明 |
|------|------|----------|------|
| 09:00 | 更新最近 7 天 | 1 次 | 深度更新 |
| 15:00 | 更新最近 3 天 | 1 次 | 中度更新 |
| 21:00 | 更新最近 1 天 | 1 次 | 快速更新 |
| **总计** | | **3 次/天** | **90 次/月** |

---

## 🚦 API 限制说明

### 官方限制

1. **Access Token**
   - 有效期：7200 秒（2 小时）
   - 获取频率：2000 次/天
   - 建议：缓存 token，提前 5 分钟刷新

2. **数据统计 API**
   - 获取文章阅读统计：500 次/天
   - 获取用户增减数据：500 次/天
   - 时间范围：最长 30 天

### 公众号类型限制

| 类型 | 数据保留时间 | API 权限 |
|------|-------------|---------|
| 认证服务号 | 30 天 | ✅ 完整 |
| 认证订阅号 | 7 天 | ✅ 完整 |
| 未认证号 | 无 | ❌ 无权限 |

---

## 📊 三种调用策略

### 1. 保守策略（推荐）

```python
策略名称: Conservative
每小时限制: 20 次
每日限制: 300 次
适用场景: 日常监控，稳定可靠
```

**优点：**
- ✅ 远低于官方限制（500 次/天）
- ✅ 有充足的余量应对突发情况
- ✅ 不会触发频率限制
- ✅ 适合长期运行

**缺点：**
- ❌ 更新频率较低
- ❌ 可能错过短期数据变化

---

### 2. 平衡策略

```python
策略名称: Balanced
每小时限制: 30 次
每日限制: 400 次
适用场景: 需要较频繁更新的场景
```

**优点：**
- ✅ 更新频率适中
- ✅ 仍有安全余量
- ✅ 适合大多数场景

**缺点：**
- ⚠️ 接近限制边界
- ⚠️ 需要监控调用次数

---

### 3. 激进策略

```python
策略名称: Aggressive
每小时限制: 50 次
每日限制: 500 次
适用场景: 一次性大批量更新
```

**优点：**
- ✅ 更新频率最高
- ✅ 数据最及时

**缺点：**
- ❌ 接近官方限制
- ❌ 容易触发频率限制
- ❌ 风险较高

---

## 💡 最佳实践

### 1. 使用频率限制器

```python
from app.services.api_limiter import get_limiter

# 创建限制器
limiter = get_limiter("conservative")

# 检查是否可以调用
can_call, reason = limiter.can_call()
if can_call:
    # 执行 API 调用
    result = call_wechat_api()
    limiter.record_call(success=True)
else:
    print(f"无法调用: {reason}")
```

### 2. 使用定时任务

```python
from app.wechat_api_scheduler import get_scheduler

# 创建调度器
scheduler = get_scheduler("conservative")

# 执行日常更新
scheduler.daily_update_task()
```

### 3. 批量更新而非单次调用

```python
# ✅ 好的做法：批量更新
update_articles(begin_date="20260401", end_date="20260407")

# ❌ 避免：单篇文章更新
for article in articles:
    update_single_article(article)  # 太浪费！
```

### 4. 错误处理与重试

```python
def call_with_retry(max_retries=3):
    for attempt in range(max_retries):
        can_call, reason = limiter.can_call()
        if not can_call:
            if "限制" in reason:
                break  # 达到限制，无法继续
            time.sleep(5)  # 延迟后重试
            continue
        
        try:
            result = call_api()
            limiter.record_call(success=True)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
                continue
            raise
```

---

## 📈 监控与告警

### 关键指标

```python
监控指标:
- 每小时 API 调用次数
- 每日 API 调用次数
- API 错误率
- 成功更新的文章数
- 更新耗时
```

### 告警阈值

```python
警告阈值:
- 每小时调用 > 25 次（保守）或 40 次（平衡）
- 每日调用 > 350 次
- 错误率 > 10%
- 成功率 < 90%

严重阈值:
- 每小时调用 > 45 次
- 每日调用 > 480 次
- 错误率 > 30%
```

---

## 🔄 定时任务配置

### 保守策略时间表

```python
时间表:
09:00 - 更新最近 7 天数据
15:00 - 更新最近 3 天数据
21:00 - 更新最近 1 天数据

总计: 3 次/天
```

### 平衡策略时间表

```python
时间表:
08:00 - 更新最近 3 天数据
12:00 - 更新最近 3 天数据
16:00 - 更新最近 1 天数据
20:00 - 更新最近 1 天数据

总计: 4 次/天
```

---

## ❓ 常见问题

### Q: 如果超过限制会怎样？
**A:** 微信会返回错误码 45009，需要等待 1 小时后才能继续调用。

### Q: 可以同时调用多个接口吗？
**A:** 可以，但要确保总调用次数不超过限制。建议串行调用。

### Q: 如何查看当前已使用的调用次数？
**A:** 使用 `limiter.get_stats()` 获取统计信息。

### Q: 不同公众号的 API 限制是独立的吗？
**A:** 是的，每个公众号有独立的调用限制。

### Q: 测试环境会占用生产环境的调用次数吗？
**A:** 会，所有调用都计入限制，建议在测试环境使用保守策略。

---

## 🎯 推荐配置

### 对于你的使用场景（8 个公众号）

```python
# 配置建议
strategy = "conservative"  # 保守策略
daily_calls = 3  # 每日 3 次调用
schedule = ["09:00", "15:00", "21:00"]  # 调用时间
update_range = [7, 3, 1]  # 更新天数范围

# 预期效果
monthly_calls = 90  # 每月 90 次调用
limit_remaining = 410  # 距离限制还有 410 次
margin = 82%  # 安全余量 82%
```

---

## 📚 相关文件

### 文档
- `WECHAT_API_LIMITS.md` - 详细限制说明
- `WECHAT_API_READ_NUM.md` - 使用说明
- `WECHAT_API_QUICKSTART.md` - 快速开始

### 代码
- `backend/app/services/api_limiter.py` - 频率限制器
- `backend/app/services/wechat_crawler.py` - 微信爬虫
- `backend/wechat_api_scheduler.py` - 定时任务调度器
- `backend/api_limiter_example.py` - 使用示例

---

## ⚠️ 重要提醒

1. **保守使用**：建议使用保守策略，确保系统稳定
2. **监控调用**：定期查看调用统计，避免超限
3. **错误处理**：实现完善的错误处理和重试机制
4. **测试先行**：在生产环境使用前，先在测试环境测试

---

## 🎉 总结

**一句话建议：**

> "使用保守策略，每日 3 次更新，安全稳定有余量！"

**实施步骤：**

1. 配置频率限制器（保守策略）
2. 设置定时任务（09:00, 15:00, 21:00）
3. 监控调用统计
4. 定期检查日志

**预期效果：**

- ✅ 每月仅使用 90 次调用（限制的 18%）
- ✅ 数据更新及时
- ✅ 系统稳定可靠
- ✅ 有充足的余量应对突发情况

---

**记住：保守使用 API，确保系统稳定运行！** 🚀
