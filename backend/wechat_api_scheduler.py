"""
定时任务配置 - 微信 API 阅读量更新
基于 APICallLimiter 实现智能调度
"""

from app.services.api_limiter import get_limiter
from app.services.wechat_crawler import WeChatCrawler
from app.database import SessionLocal
from app.models import Article, Channel
from app.config import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WeChatAPIScheduler:
    """微信 API 定时任务调度器"""
    
    def __init__(self, strategy: str = "conservative"):
        """
        初始化调度器
        
        参数:
            strategy: 调用策略 (conservative/balanced/aggressive)
        """
        self.limiter = get_limiter(strategy)
        self.strategy = strategy
        
        logger.info(f"微信 API 调度器初始化完成，策略: {strategy}")
    
    def daily_update_task(self):
        """
        日常更新任务
        更新最近 7 天的文章阅读量
        """
        logger.info("=" * 60)
        logger.info("开始执行日常更新任务")
        logger.info("=" * 60)
        
        # 计算日期范围
        end_date = datetime.now()
        begin_date = end_date - timedelta(days=7)
        
        # 检查是否可以调用
        can_call, reason = self.limiter.can_call()
        if not can_call:
            logger.warning(f"无法执行日常更新: {reason}")
            return False
        
        # 执行更新
        success = self._update_articles(
            begin_date=begin_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            task_name="日常更新"
        )
        
        # 记录统计
        stats = self.limiter.get_stats()
        logger.info(f"当前统计: {stats['daily_calls']}/{stats['daily_limit']} 次调用")
        
        return success
    
    def morning_update_task(self):
        """
        早晨更新任务
        更新最近 3 天的文章阅读量
        """
        logger.info("=" * 60)
        logger.info("开始执行早晨更新任务")
        logger.info("=" * 60)
        
        # 计算日期范围
        end_date = datetime.now()
        begin_date = end_date - timedelta(days=3)
        
        # 检查是否可以调用
        can_call, reason = self.limiter.can_call()
        if not can_call:
            logger.warning(f"无法执行早晨更新: {reason}")
            return False
        
        # 执行更新
        success = self._update_articles(
            begin_date=begin_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            task_name="早晨更新"
        )
        
        return success
    
    def evening_update_task(self):
        """
        晚间更新任务
        更新最近 1 天的文章阅读量
        """
        logger.info("=" * 60)
        logger.info("开始执行晚间更新任务")
        logger.info("=" * 60)
        
        # 计算日期范围
        end_date = datetime.now()
        begin_date = end_date - timedelta(days=1)
        
        # 检查是否可以调用
        can_call, reason = self.limiter.can_call()
        if not can_call:
            logger.warning(f"无法执行晚间更新: {reason}")
            return False
        
        # 执行更新
        success = self._update_articles(
            begin_date=begin_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            task_name="晚间更新"
        )
        
        return success
    
    def _update_articles(self, begin_date: str, end_date: str, task_name: str) -> bool:
        """
        更新文章阅读量
        
        参数:
            begin_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            task_name: 任务名称
        
        返回:
            是否成功
        """
        logger.info(f"{task_name}: 更新日期范围 {begin_date} - {end_date}")
        
        if not settings.wechat_appid or not settings.wechat_appsecret:
            logger.error("未配置微信 API 凭证")
            return False
        
        try:
            db = SessionLocal()
            
            # 查询指定日期范围的文章
            articles = db.query(Article).filter(
                Article.create_time >= datetime.strptime(begin_date, "%Y%m%d"),
                Article.create_time <= datetime.strptime(end_date, "%Y%m%d") + timedelta(days=1)
            ).all()
            
            logger.info(f"找到 {len(articles)} 篇文章")
            
            if not articles:
                logger.warning("没有找到需要更新的文章")
                return True
            
            # 创建爬虫实例
            crawler = WeChatCrawler(
                appid=settings.wechat_appid,
                appsecret=settings.wechat_appsecret
            )
            
            updated_count = 0
            failed_count = 0
            
            for article in articles:
                # 检查是否可以调用
                can_call, reason = self.limiter.can_call()
                if not can_call:
                    logger.warning(f"达到调用限制，停止更新: {reason}")
                    break
                
                try:
                    if not article.msgid:
                        logger.debug(f"文章 '{article.title[:30]}...' 没有 msgid，跳过")
                        failed_count += 1
                        continue
                    
                    # 调用 API 获取阅读统计
                    stats = crawler.get_article_read_stats(
                        data_id=article.msgid,
                        begin_date=begin_date,
                        end_date=end_date
                    )
                    
                    if stats and len(stats) > 0:
                        total_read = sum(item.get("int_page_read_user", 0) for item in stats)
                        
                        if article.read_num != total_read:
                            article.read_num = total_read
                            updated_count += 1
                            logger.info(f"更新文章 '{article.title[:30]}...' 阅读量: {total_read}")
                    
                    # 记录调用
                    self.limiter.record_call(success=True)
                    
                    # 延迟
                    import time
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"更新文章 '{article.title[:30]}...' 失败: {e}")
                    self.limiter.record_call(success=False, error=str(e))
                    failed_count += 1
            
            db.commit()
            
            # 更新公众号累计阅读量
            self._update_channel_totals(db)
            
            logger.info(f"{task_name} 完成: 更新 {updated_count} 篇，失败 {failed_count} 篇")
            
            return True
            
        except Exception as e:
            logger.error(f"{task_name} 失败: {e}")
            return False
        finally:
            if 'db' in locals():
                db.close()
    
    def _update_channel_totals(self, db):
        """更新所有公众号的累计阅读量"""
        from sqlalchemy import func
        
        channels = db.query(Channel).all()
        
        for channel in channels:
            total_reads = db.query(func.sum(Article.read_num)).filter(
                Article.channel_id == channel.id
            ).scalar() or 0
            
            if channel.total_read_num != total_reads:
                channel.total_read_num = total_reads
                logger.debug(f"更新公众号 '{channel.nickname}' 累计阅读量: {total_reads}")
        
        db.commit()


# 预定义的定时任务配置
SCHEDULE_CONFIGS = {
    "conservative": {
        "description": "保守策略：每日 3 次更新",
        "tasks": [
            {
                "name": "daily_update",
                "func": WeChatAPIScheduler.daily_update_task,
                "schedule": "09:00",  # 每天 09:00
                "description": "更新最近 7 天数据"
            },
            {
                "name": "morning_update",
                "func": WeChatAPIScheduler.morning_update_task,
                "schedule": "15:00",  # 每天 15:00
                "description": "更新最近 3 天数据"
            },
            {
                "name": "evening_update",
                "func": WeChatAPIScheduler.evening_update_task,
                "schedule": "21:00",  # 每天 21:00
                "description": "更新最近 1 天数据"
            }
        ],
        "total_daily_calls": 3
    },
    "balanced": {
        "description": "平衡策略：每日 4 次更新",
        "tasks": [
            {
                "name": "morning_update",
                "func": WeChatAPIScheduler.morning_update_task,
                "schedule": "08:00",
                "description": "更新最近 3 天数据"
            },
            {
                "name": "noon_update",
                "func": WeChatAPIScheduler.morning_update_task,
                "schedule": "12:00",
                "description": "更新最近 3 天数据"
            },
            {
                "name": "afternoon_update",
                "func": WeChatAPIScheduler.evening_update_task,
                "schedule": "16:00",
                "description": "更新最近 1 天数据"
            },
            {
                "name": "evening_update",
                "func": WeChatAPIScheduler.evening_update_task,
                "schedule": "20:00",
                "description": "更新最近 1 天数据"
            }
        ],
        "total_daily_calls": 4
    }
}


def get_scheduler(strategy: str = "conservative") -> WeChatAPIScheduler:
    """
    获取配置好的调度器
    
    参数:
        strategy: 调用策略
    
    返回:
        WeChatAPIScheduler 实例
    """
    return WeChatAPIScheduler(strategy=strategy)


def print_schedule_config(strategy: str = "conservative"):
    """打印定时任务配置"""
    config = SCHEDULE_CONFIGS.get(strategy, SCHEDULE_CONFIGS["conservative"])
    
    print("\n" + "=" * 60)
    print(f"定时任务配置 - {strategy.upper()} 策略")
    print("=" * 60)
    print(f"\n{config['description']}")
    print(f"预计每日 API 调用次数: {config['total_daily_calls']}")
    
    print("\n任务列表:")
    for task in config["tasks"]:
        print(f"  • {task['schedule']} - {task['name']}")
        print(f"    {task['description']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # 打印配置
    print_schedule_config("conservative")
    print_schedule_config("balanced")
    
    # 测试调度器
    print("\n测试调度器...")
    scheduler = get_scheduler("conservative")
    
    # 手动执行一次早晨更新
    print("\n执行早晨更新任务...")
    result = scheduler.morning_update_task()
    
    # 查看统计
    stats = scheduler.limiter.get_stats()
    print(f"\n调度器统计:")
    print(f"  今日调用: {stats['daily_calls']}/{stats['daily_limit']}")
    print(f"  本小时调用: {stats['hourly_calls']}/{stats['hourly_limit']}")
