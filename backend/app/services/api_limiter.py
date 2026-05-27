"""
微信公众号 API 调用频率限制器
"""
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class APICallLimiter:
    """API 调用频率限制器"""
    
    def __init__(
        self,
        max_calls_per_hour: int = 30,
        max_calls_per_day: int = 400,
        strategy: str = "conservative"
    ):
        """
        初始化限制器
        
        参数:
            max_calls_per_hour: 每小时最大调用次数
            max_calls_per_day: 每日最大调用次数
            strategy: 调用策略 (conservative/balanced/aggressive)
        """
        self.max_calls_per_hour = max_calls_per_hour
        self.max_calls_per_day = max_calls_per_day
        self.strategy = strategy
        
        # 计数器
        self.hourly_count = 0
        self.daily_count = 0
        
        # 时间戳
        self.last_hour_reset = datetime.now()
        self.last_day_reset = datetime.now()
        
        # 调用历史（用于监控）
        self.call_history = []
        
        logger.info(f"API 调用限制器初始化完成")
        logger.info(f"  策略: {strategy}")
        logger.info(f"  每小时限制: {max_calls_per_hour}")
        logger.info(f"  每日限制: {max_calls_per_day}")
    
    def can_call(self) -> tuple[bool, Optional[str]]:
        """
        检查是否可以调用 API
        
        返回:
            (是否可以调用, 原因)
        """
        now = datetime.now()
        
        # 重置计数器
        self._reset_counters(now)
        
        # 检查每小时限制
        if self.hourly_count >= self.max_calls_per_hour:
            logger.warning(f"已达到每小时调用限制: {self.hourly_count}/{self.max_calls_per_hour}")
            return False, f"已达到每小时调用限制，请等待 {(self.last_hour_reset - now).seconds} 秒"
        
        # 检查每日限制
        if self.daily_count >= self.max_calls_per_day:
            logger.warning(f"已达到每日调用限制: {self.daily_count}/{self.max_calls_per_day}")
            return False, f"已达到每日调用限制，请等待 {(self.last_day_reset - now).seconds} 秒"
        
        # 检查是否需要延迟（基于策略）
        delay = self._get_delay(now)
        if delay > 0:
            logger.info(f"根据策略需要延迟 {delay} 秒")
            return False, f"需要延迟 {delay} 秒"
        
        return True, None
    
    def record_call(self, success: bool = True, error: Optional[str] = None):
        """
        记录一次 API 调用
        
        参数:
            success: 是否成功
            error: 错误信息（如果失败）
        """
        now = datetime.now()
        
        self.hourly_count += 1
        self.daily_count += 1
        
        # 记录到历史
        self.call_history.append({
            "timestamp": now,
            "success": success,
            "error": error
        })
        
        # 只保留最近 1000 条记录
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-1000:]
        
        if success:
            logger.info(f"API 调用记录成功 (今日: {self.daily_count}, 本小时: {self.hourly_count})")
        else:
            logger.error(f"API 调用失败: {error}")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        now = datetime.now()
        self._reset_counters(now)
        
        # 计算成功率
        successful_calls = sum(1 for call in self.call_history if call["success"])
        total_calls = len(self.call_history)
        success_rate = successful_calls / total_calls if total_calls > 0 else 0
        
        # 计算预计达到限制时间
        hours_until_limit = (
            (self.max_calls_per_day - self.daily_count) / max(1, self.hourly_count)
            if self.hourly_count > 0 else 999
        )
        
        return {
            "strategy": self.strategy,
            "hourly_calls": self.hourly_count,
            "hourly_limit": self.max_calls_per_hour,
            "daily_calls": self.daily_count,
            "daily_limit": self.max_calls_per_day,
            "hourly_remaining": self.max_calls_per_hour - self.hourly_count,
            "daily_remaining": self.max_calls_per_day - self.daily_count,
            "success_rate": round(success_rate * 100, 2),
            "total_calls": total_calls,
            "hours_until_limit": round(hours_until_limit, 2),
            "last_reset_hour": self.last_hour_reset.strftime("%Y-%m-%d %H:%M:%S"),
            "last_reset_day": self.last_day_reset.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _reset_counters(self, now: datetime):
        """重置计数器"""
        # 重置每小时计数器
        if (now - self.last_hour_reset).seconds >= 3600:
            self.hourly_count = 0
            self.last_hour_reset = now
            logger.debug("重置每小时计数器")
        
        # 重置每日计数器
        if (now - self.last_day_reset).days >= 1:
            self.daily_count = 0
            self.last_day_reset = now
            logger.debug("重置每日计数器")
    
    def _get_delay(self, now: datetime) -> int:
        """根据策略获取需要的延迟时间"""
        # 计算距离上次调用的时间
        if not self.call_history:
            return 0
        
        last_call = self.call_history[-1]["timestamp"]
        time_since_last = (now - last_call).total_seconds()
        
        if self.strategy == "conservative":
            # 保守策略：至少间隔 10 秒
            min_interval = 10
        elif self.strategy == "balanced":
            # 平衡策略：至少间隔 5 秒
            min_interval = 5
        else:  # aggressive
            # 激进策略：至少间隔 2 秒
            min_interval = 2
        
        delay = max(0, min_interval - time_since_last)
        return int(delay)
    
    def wait_until_can_call(self):
        """等待直到可以调用 API"""
        while True:
            can_call, reason = self.can_call()
            if can_call:
                return
            
            if "延迟" in reason:
                import re
                delay_match = re.search(r'(\d+) 秒', reason)
                if delay_match:
                    delay = int(delay_match.group(1))
                    logger.info(f"等待 {delay} 秒...")
                    import time
                    time.sleep(delay)
                else:
                    break
            else:
                # 达到限制，无法继续
                break


# 预定义的策略配置
STRATEGIES = {
    "conservative": {
        "max_calls_per_hour": 20,
        "max_calls_per_day": 300,
        "description": "保守策略：每小时 20 次，每天 300 次"
    },
    "balanced": {
        "max_calls_per_hour": 30,
        "max_calls_per_day": 400,
        "description": "平衡策略：每小时 30 次，每天 400 次"
    },
    "aggressive": {
        "max_calls_per_hour": 50,
        "max_calls_per_day": 500,
        "description": "激进策略：每小时 50 次，每天 500 次"
    }
}


def get_limiter(strategy: str = "conservative") -> APICallLimiter:
    """
    获取配置好的限制器
    
    参数:
        strategy: 调用策略
    
    返回:
        APICallLimiter 实例
    """
    config = STRATEGIES.get(strategy, STRATEGIES["conservative"])
    
    return APICallLimiter(
        max_calls_per_hour=config["max_calls_per_hour"],
        max_calls_per_day=config["max_calls_per_day"],
        strategy=strategy
    )
