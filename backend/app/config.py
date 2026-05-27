from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 微信凭证
    wechat_token: str = ""
    wechat_cookie: str = ""
    
    # 微信公众号 API 凭证（用于获取真实阅读量）
    wechat_appid: str = "wx26b8b484b4bb782d"
    wechat_appsecret: str = "31ee4cdd860946b20d1a6ff6086dc021"
    wechat_access_token: str = ""
    
    # 定时任务 - 每天同步
    daily_schedule_hour: int = 9
    daily_schedule_minute: int = 0
    
    # 定时任务 - 每周同步（星期几，0-6，0=周一）
    weekly_day: int = 0  # 默认周一
    weekly_hour: int = 9
    weekly_minute: int = 0
    
    # Excel 导出配置
    auto_export_weekly: bool = True  # 是否每周自动导出
    export_directory: str = "./exports"  # 导出目录
    export_filename_prefix: str = "articles"  # 导出文件名前缀
    
    # 默认配置
    default_days: int = 365
    
    # 数据库
    database_url: str = "sqlite:///./data/channels.db"
    
    # 服务器
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 同步配置
    request_interval_min: int = 5
    request_interval_max: int = 15
    max_requests_per_hour: int = 30
    max_requests_per_day: int = 100
    max_accounts_per_sync: int = 50
    max_articles_per_account: int = 50

    # 分批次轮转同步配置（解决微信频率限制问题）
    sync_batch_size: int = 30  # 每批同步的公众号数量
    sync_batch_interval_minutes: int = 180  # 每批次之间的间隔（分钟）→ 每3小时全量刷新30个账号
    sync_cycle_hours: int = 3  # 每多少小时完成一次全量轮转

    # AI 配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # 企业微信智能机器人配置
    wecom_bot_id: str = ""  # 机器人 Bot ID
    wecom_bot_secret: str = ""  # 机器人 Secret
    wecom_bot_enabled: bool = True  # 是否启用机器人

    # 登录配置
    access_password: str = "channel2026"  # 普通用户访问密码
    admin_password: str = "admin2026"  # 超级管理者密码
    jwt_secret_key: str = "wechat-channel-secret-key-2026"  # JWT 密钥
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
