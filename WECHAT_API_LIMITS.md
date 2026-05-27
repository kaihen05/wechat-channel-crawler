# 微信公众号 API 调用限制与最佳实践

## 官方限制说明

### 1. Access Token 限制
- **有效期**：7200 秒（2 小时）
- **获取频率**：每日 2000 次
- **建议**：缓存 token，提前 5 分钟刷新

### 2. 数据统计 API 限制
| 接口 | 每日调用次数 | 时间范围限制 |
|------|-------------|-------------|
| 获取文章阅读统计 | 500 次 | 最长 30 天 |
| 获取用户增减数据 | 500 次 | 最长 30 天 |
| 获取用户累计数据 | 500 次 | 最长 30 天 |

### 3. 公众号类型限制
| 公众号类型 | 数据保留时间 | API 权限 |
|-----------|-------------|---------|
| 认证服务号 | 30 天 | 完整 |
| 认证订阅号 | 7 天 | 完整 |
| 未认证号 | 无 | 无 |

---

## 推荐调用规则

### 每小时调用次数建议

#### 方案 A：保守策略（推荐）
```
每小时调用次数：10-20 次
每日总量：200-400 次
适用场景：日常监控，避免触发限制
```

#### 方案 B：平衡策略
```
每小时调用次数：20-30 次
每日总量：400-600 次
适用场景：需要较频繁更新的场景
```

#### 方案 C：激进策略
```
每小时调用次数：40-50 次
每日总量：800-1000 次
适用场景：一次性大批量更新
注意：接近上限，风险较高
```

---

## 最佳实践

### 1. 批量更新策略
```python
# 推荐：按日期范围批量更新，而不是单篇文章更新

# ✅ 好的做法：一次更新 7 天的数据（1 次 API 调用）
update_range(begin_date="20260401", end_date="20260407")

# ❌ 避免：每篇文章单独调用 API（N 次 API 调用）
for article in articles:
    update_single_article(article)  # 太浪费！
```

### 2. 智能调度策略
```python
# 推荐调用时间表

SCHEDULE = {
    "日常更新": {
        "频率": "每 4 小时一次",
        "时间": ["09:00", "13:00", "17:00", "21:00"],
        "调用次数": "4 次/天",
        "用途": "获取最新文章阅读量"
    },
    "深度更新": {
        "频率": "每天一次",
        "时间": "02:00",
        "调用次数": "1 次/天",
        "用途": "更新过去 7 天的历史数据"
    },
    "紧急更新": {
        "频率": "按需",
        "调用次数": "不超过 10 次/小时",
        "用途": "特殊活动监控"
    }
}
```

### 3. 错误处理与重试
```python
RETRY_STRATEGY = {
    "access_token 过期": {
        "重试次数": 1,
        "延迟": 0,
        "操作": "立即刷新 token 并重试"
    },
    "频率限制 (errcode: 45009)": {
        "重试次数": 3,
        "延迟": "60 秒",
        "操作": "等待后重试"
    },
    "系统繁忙 (errcode: -1)": {
        "重试次数": 3,
        "延迟": "5 秒递增",
        "操作": "指数退避重试"
    },
    "其他错误": {
        "重试次数": 0,
        "操作": "记录日志，跳过"
    }
}
```

---

## 实际调用示例

### 场景 1：日常监控（推荐）
```
目标：监控最近 3 天的新文章

调用计划：
- 09:00 更新 2026/04/13-04/15（1 次）
- 13:00 更新 2026/04/13-04/15（1 次）
- 17:00 更新 2026/04/13-04/15（1 次）
- 21:00 更新 2026/04/13-04/15（1 次）

每日总计：4 次 API 调用
每月总计：120 次 API 调用
```

### 场景 2：周度报告
```
目标：获取过去 7 天的完整数据

调用计划：
- 每周一 02:00 更新上周数据（1 次）

每周总计：1 次 API 调用
每月总计：4 次 API 调用
```

### 场景 3：活动监控
```
目标：监控特定活动期间的阅读量

调用计划：
- 活动期间每 2 小时更新一次
- 每次更新最近 1 天的数据

每日总计：12 次 API 调用
活动期间总计：视活动天数而定
```

---

## 系统配置建议

### 配置文件示例
```python
# backend/app/config.py

class Settings(BaseSettings):
    # ... 其他配置 ...
    
    # API 调用限制配置
    wechat_api_max_calls_per_day: int = 400  # 每日最大调用次数
    wechat_api_max_calls_per_hour: int = 30  # 每小时最大调用次数
    wechat_api_retry_count: int = 3  # 重试次数
    wechat_api_retry_delay: int = 5  # 重试延迟（秒）
    
    # 缓存配置
    wechat_token_cache_minutes: int = 110  # token 缓存时间（提前 10 分钟刷新）
    
    # 更新策略
    wechat_sync_strategy: str = "conservative"  # conservative/balanced/aggressive
```

### 调用频率控制器
```python
class APICallLimiter:
    """API 调用频率限制器"""
    
    def __init__(self, max_per_hour=30, max_per_day=400):
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.hourly_count = 0
        self.daily_count = 0
        self.last_hour_reset = datetime.now()
        self.last_day_reset = datetime.now()
    
    def can_call(self):
        """检查是否可以调用 API"""
        now = datetime.now()
        
        # 重置计数器
        if (now - self.last_hour_reset).seconds >= 3600:
            self.hourly_count = 0
            self.last_hour_reset = now
        
        if (now - self.last_day_reset).days >= 1:
            self.daily_count = 0
            self.last_day_reset = now
        
        return (self.hourly_count < self.max_per_hour and 
                self.daily_count < self.max_per_day)
    
    def record_call(self):
        """记录一次 API 调用"""
        self.hourly_count += 1
        self.daily_count += 1
```

---

## 监控与告警

### 建议监控指标
```python
MONITORING_METRICS = {
    "api_calls_hourly": "每小时 API 调用次数",
    "api_calls_daily": "每日 API 调用次数",
    "api_errors": "API 错误次数",
    "token_refresh_count": "Token 刷新次数",
    "articles_updated": "成功更新的文章数",
    "update_duration": "更新耗时"
}
```

### 告警阈值
```python
ALERT_THRESHOLDS = {
    "hourly_calls_warning": 25,  # 每小时调用次数超过 25 次警告
    "hourly_calls_critical": 45,  # 每小时调用次数超过 45 次严重警告
    "daily_calls_warning": 350,  # 每日调用次数超过 350 次警告
    "daily_calls_critical": 480,  # 每日调用次数超过 480 次严重警告
    "error_rate_warning": 0.1,  # 错误率超过 10% 警告
    "error_rate_critical": 0.3  # 错误率超过 30% 严重警告
}
```

---

## 常见问题

### Q: 如果超过限制会怎样？
A: 微信会返回错误码 45009，需要等待 1 小时后才能继续调用。

### Q: 可以同时调用多个接口吗？
A: 可以，但要确保总调用次数不超过限制。建议串行调用，避免并发。

### Q: 如何查看当前已使用的调用次数？
A: 微信不提供查询接口，需要在应用层自行统计。

### Q: 不同公众号的 API 限制是独立的吗？
A: 是的，每个公众号有独立的调用限制。

### Q: 测试环境会占用生产环境的调用次数吗？
A: 会，所有调用都计入限制，建议在测试环境使用保守策略。

---

## 总结建议

### 对于你的使用场景

基于你管理的公众号数量（8 个），建议：

```
每日调用策略：
- 上午 09:00：更新最近 7 天数据（1 次）
- 下午 15:00：更新最近 3 天数据（1 次）
- 晚上 21:00：更新最近 1 天数据（1 次）

每日总计：3 次 API 调用
每月总计：90 次 API 调用

优势：
- 远低于限制（500 次/天）
- 数据更新及时
- 有充足的余量应对紧急情况
```

### 紧急情况下
如果需要进行大批量更新：
```
- 单次最多更新 30 天数据（1 次调用）
- 每小时最多 20 次调用
- 建议分几天完成大批量更新
```

---

**记住：保守使用 API，确保系统稳定运行！**
