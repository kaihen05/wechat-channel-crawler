from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import httpx
from app.config import settings
from app.database import SessionLocal
from app.models import Channel
import logging
import asyncio
import os
import time

logger = logging.getLogger(__name__)

# 批次状态文件
BATCH_STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sync_batch_state.txt")


def _load_batch_state():
    """加载批次状态"""
    try:
        if os.path.exists(BATCH_STATE_FILE):
            with open(BATCH_STATE_FILE, "r") as f:
                content = f.read().strip()
                parts = content.split(",")
                if len(parts) >= 2:
                    return int(parts[0]), int(parts[1])  # cycle_pos, total_batches
    except Exception as e:
        logger.warning(f"加载批次状态失败: {e}")
    return 0, 0  # 默认从头开始


def _save_batch_state(cycle_pos: int, total_batches: int):
    """保存批次状态"""
    try:
        os.makedirs(os.path.dirname(BATCH_STATE_FILE), exist_ok=True)
        with open(BATCH_STATE_FILE, "w") as f:
            f.write(f"{cycle_pos},{total_batches}")
    except Exception as e:
        logger.error(f"保存批次状态失败: {e}")


class SyncScheduler:
    """定时同步任务调度器"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.api_base_url = f"http://127.0.0.1:{settings.port}"
        self._batch_size = settings.sync_batch_size
        self._cycle_hours = settings.sync_cycle_hours
        self._batch_interval = settings.sync_batch_interval_minutes

    def start(self):
        """启动调度器"""
        # ========== 分批次轮转同步任务（每分钟检查一次） ==========
        self.scheduler.add_job(
            self.batch_sync_job,
            IntervalTrigger(minutes=self._batch_interval),
            id="batch_sync_articles",
            name="分批次轮转同步公众号文章",
            replace_existing=True,
            max_instances=1  # 避免重复执行
        )
        logger.info(f"分批次轮转同步已启动: 每 {self._batch_interval} 分钟同步一批，每 {self._cycle_hours} 小时完成全量轮转")

        # 添加每天定时同步任务
        self.scheduler.add_job(
            self.daily_sync_job,
            CronTrigger(
                hour=settings.daily_schedule_hour,
                minute=settings.daily_schedule_minute
            ),
            id="daily_sync_articles",
            name="每天同步公众号文章",
            replace_existing=True
        )

        # 添加每周定时同步任务
        self.scheduler.add_job(
            self.weekly_sync_job,
            CronTrigger(
                day_of_week=settings.weekly_day,
                hour=settings.weekly_hour,
                minute=settings.weekly_minute
            ),
            id="weekly_sync_articles",
            name="每周同步公众号文章",
            replace_existing=True
        )

        # 如果启用了每周自动导出，添加导出任务
        if settings.auto_export_weekly:
            self.scheduler.add_job(
                self.weekly_export_job,
                CronTrigger(
                    day_of_week=settings.weekly_day,
                    hour=settings.weekly_hour,
                    minute=settings.weekly_minute,
                ),
            )

        self.scheduler.start()
        logger.info(f"每天定时任务已启动，每天 {settings.daily_schedule_hour:02d}:{settings.daily_schedule_minute:02d} 执行")
        logger.info(f"每周定时任务已启动，每周{['一','二','三','四','五','六','日'][settings.weekly_day]} {settings.weekly_hour:02d}:{settings.weekly_minute:02d} 执行")
        if settings.auto_export_weekly:
            logger.info(f"每周自动导出已启用")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("定时任务已停止")

    async def batch_sync_job(self):
        """分批次轮转同步任务"""
        cycle_pos, total_batches = _load_batch_state()

        # 获取当前数据库中的有效公众号数，重新计算总批次数
        db = SessionLocal()
        try:
            total_channels = db.query(Channel).filter(Channel.is_active == True).count()
        finally:
            db.close()

        if total_channels == 0:
            logger.warning("没有启用的公众号，跳过批次同步")
            return

        # 计算总批次数（向上取整）
        total_batches = (total_channels + self._batch_size - 1) // self._batch_size

        logger.info(f"[批次同步] 第 {cycle_pos + 1}/{total_batches} 批，cycle_pos={cycle_pos}，全量 {total_channels} 个公众号")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "batch_index": cycle_pos,
                    "total_batches": total_batches,
                    "batch_size": self._batch_size
                }
                response = await client.post(
                    f"{self.api_base_url}/api/articles/sync-batch",
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"[批次同步] 完成: {result.get('message', '')}")
                else:
                    logger.error(f"[批次同步] 失败: {response.status_code}")

        except Exception as e:
            logger.error(f"[批次同步] 异常: {e}")

        # 更新 cycle_pos（环形）
        cycle_pos = (cycle_pos + 1) % total_batches
        _save_batch_state(cycle_pos, total_batches)

    async def daily_sync_job(self):
        """每天同步任务（仅同步友商监控公众号）"""
        logger.info("开始执行每天定时同步任务...")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.api_base_url}/api/articles/sync")

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"每天同步完成: {result['message']}")
                else:
                    logger.error(f"每天同步失败: {response.status_code}")

        except Exception as e:
            logger.error(f"每天同步任务异常: {e}")

    async def weekly_sync_job(self):
        """每周同步任务"""
        logger.info("开始执行每周定时同步任务...")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.api_base_url}/api/articles/sync")

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"每周同步完成: {result['message']}")
                else:
                    logger.error(f"每周同步失败: {response.status_code}")

        except Exception as e:
            logger.error(f"每周同步任务异常: {e}")

    async def weekly_export_job(self):
        """每周导出Excel任务"""
        logger.info("开始执行每周Excel导出任务...")

        try:
            # 等待同步完成后再导出
            await asyncio.sleep(60)  # 等待60秒

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(
                    f"{self.api_base_url}/api/export/excel",
                    params={"auto": "true"}
                )

                if response.status_code == 200:
                    logger.info(f"每周Excel导出完成")
                else:
                    logger.error(f"每周Excel导出失败: {response.status_code}")

        except Exception as e:
            logger.error(f"每周Excel导出任务异常: {e}")


# 导入asyncio
import asyncio


# 导入asyncio
import asyncio


# 全局调度器实例
scheduler = SyncScheduler()
