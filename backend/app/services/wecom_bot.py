"""
企业微信智能机器人服务
基于 wecom-aibot-sdk 的 WebSocket 长连接模式
"""

import asyncio
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    from wecom_aibot_sdk import WSClient, generate_req_id
    _WECOM_SDK_AVAILABLE = True
except ImportError:
    _WECOM_SDK_AVAILABLE = False
    WSClient = None
    generate_req_id = None

from app.config import settings

logger = logging.getLogger(__name__)


def _get_db_path() -> str:
    """获取数据库文件路径"""
    url = settings.database_url
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "").replace("sqlite://", "")
    return "data/channels.db"


def _query_competitor_articles(days: int = 7, limit: int = 20) -> List[Dict]:
    """查询友商公众号的最新文章"""
    db_path = _get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            SELECT c.nickname, c.competitor_note, a.title, a.digest, a.link, a.create_time
            FROM articles a
            JOIN channels c ON a.channel_id = c.id
            WHERE c.is_competitor = 1 AND a.create_time >= ?
            ORDER BY a.create_time DESC
            LIMIT ?
            """,
            (since, limit),
        )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        logger.error(f"查询友商文章失败: {e}")
        return []


def _query_competitor_channels() -> List[Dict]:
    """查询所有友商公众号"""
    db_path = _get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nickname, competitor_note, category FROM channels WHERE is_competitor = 1 ORDER BY nickname"
        )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        logger.error(f"查询友商公众号失败: {e}")
        return []


def _search_articles(keyword: str, days: int = 30, limit: int = 10) -> List[Dict]:
    """搜索文章"""
    db_path = _get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            SELECT c.nickname, a.title, a.digest, a.link, a.create_time
            FROM articles a
            JOIN channels c ON a.channel_id = c.id
            WHERE a.create_time >= ? AND (a.title LIKE ? OR a.digest LIKE ?)
            ORDER BY a.create_time DESC
            LIMIT ?
            """,
            (since, f"%{keyword}%", f"%{keyword}%", limit),
        )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        logger.error(f"搜索文章失败: {e}")
        return []


def _format_competitor_report(articles: List[Dict], days: int) -> str:
    """格式化友商动态报告 - 精简版，避免超长"""
    if not articles:
        return f"最近{days}天没有友商公众号的新动态。"

    # 按公众号分组
    by_channel: Dict[str, List[Dict]] = {}
    for a in articles:
        key = a["nickname"]
        if key not in by_channel:
            by_channel[key] = []
        by_channel[key].append(a)

    lines = [f"友商动态（最近{days}天）\n"]

    total_shown = 0
    max_per_channel = 3  # 每个公众号最多显示3篇

    for channel_name, channel_articles in by_channel.items():
        count = len(channel_articles)
        shown = channel_articles[:max_per_channel]
        lines.append(f"【{channel_name}】({count}篇)")
        for a in shown:
            date = a["create_time"][:10] if a["create_time"] else "未知"
            title = a["title"][:30] + ("..." if len(a["title"]) > 30 else "")
            lines.append(f"  {date} {title}")
        if count > max_per_channel:
            lines.append(f"  ...还有{count - max_per_channel}篇")
        total_shown += count
        lines.append("")

    lines.append(f"共{total_shown}篇，来自{len(by_channel)}个公众号")
    result = "\n".join(lines)

    # 硬限制：不超过2000字符
    if len(result) > 2000:
        result = result[:1990] + "\n...（内容过长已截断）"

    return result


def _format_search_results(articles: List[Dict], keyword: str) -> str:
    """格式化搜索结果"""
    if not articles:
        return f"未找到包含「{keyword}」的文章。"

    lines = [f"搜索「{keyword}」的结果\n"]
    for a in articles[:15]:  # 最多15条
        date = a["create_time"][:10] if a["create_time"] else "未知"
        title = a["title"][:30] + ("..." if len(a["title"]) > 30 else "")
        lines.append(f"[{date}] {a['nickname']} - {title}")

    lines.append(f"\n共{len(articles)}篇")
    result = "\n".join(lines)

    if len(result) > 2000:
        result = result[:1990] + "\n...（内容过长已截断）"

    return result


class WeComBot:
    """企业微信智能机器人管理器"""

    def __init__(self, bot_id: str, secret: str):
        self.bot_id = bot_id
        self.secret = secret
        self._client: Optional[WSClient] = None
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """启动机器人 WebSocket 长连接"""
        if not _WECOM_SDK_AVAILABLE:
            logger.warning("wecom_aibot_sdk 未安装，企业微信机器人功能不可用")
            return
        if not self.bot_id or not self.secret:
            logger.warning("企业微信机器人未配置 Bot ID 或 Secret，跳过启动")
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"企业微信机器人启动中... Bot ID: {self.bot_id[:8]}***")

    async def _run(self):
        """运行 WebSocket 连接（由 SDK 内部管理重连）"""
        try:
            self._client = WSClient(
                bot_id=self.bot_id,
                secret=self.secret,
                heartbeat_interval=25000,
                max_reconnect_attempts=-1,  # 无限重连
            )

            # 注册事件处理器
            self._client.on("authenticated", self._on_authenticated)
            self._client.on("connected", self._on_connected)
            self._client.on("disconnected", self._on_disconnected)
            self._client.on("error", self._on_error)
            self._client.on("message", self._on_any_message)
            self._client.on("message.text", self._on_text_message)
            self._client.on("message.image", self._on_image_message)
            self._client.on("event.enter_chat", self._on_enter_chat)

            await self._client.connect()
        except Exception as e:
            logger.error(f"企业微信机器人运行异常: {e}")
            if self._running:
                logger.info("将在 5 秒后重新创建连接...")
                await asyncio.sleep(5)
                self._task = asyncio.create_task(self._run())

    async def stop(self):
        """停止机器人"""
        self._running = False
        if self._client:
            try:
                await self._client.disconnect()
            except Exception as e:
                logger.error(f"断开企业微信机器人连接失败: {e}")
            self._client = None
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("企业微信机器人已停止")

    # ========== 事件处理器 ==========

    def _on_connected(self):
        logger.info("企业微信机器人 WebSocket 连接已建立")

    def _on_authenticated(self):
        logger.info("企业微信机器人认证成功，等待接收消息...")

    def _on_disconnected(self, reason: str):
        logger.warning(f"企业微信机器人连接断开: {reason}")

    def _on_error(self, error: Exception):
        logger.error(f"企业微信机器人错误: {error}")

    async def _on_any_message(self, frame: dict):
        """收到任意类型的消息"""
        headers = frame.get("headers", {})
        body = frame.get("body", {})
        msg_type = body.get("msgtype", "unknown")
        logger.info(f"收到消息 [type={msg_type}] headers={headers}")

    async def _on_text_message(self, frame: dict):
        """收到文本消息 - 核心处理逻辑"""
        headers = frame.get("headers", {})
        body = frame.get("body", {})
        text_info = body.get("text", {})

        chatid = text_info.get("chatid", "")
        userid = text_info.get("userid", "")
        content = text_info.get("content", "")

        logger.info(f"收到文本消息: chatid={chatid}, userid={userid}, content={content}")

        stream_id = str(uuid.uuid4())

        try:
            reply_text = await self._handle_message(content, userid, chatid)
            logger.info(f"回复内容长度: {len(reply_text)} 字符, 前100字: {reply_text[:100]}")

            # 使用一次性流式回复：内容 + finish 合并发送
            await self._client.reply_stream(
                frame,
                stream_id=stream_id,
                content=reply_text,
                finish=True,
            )

            logger.info(f"已回复消息给 {userid} in {chatid}")
        except Exception as e:
            logger.error(f"回复消息失败: {e}", exc_info=True)

    async def _on_image_message(self, frame: dict):
        """收到图片消息"""
        body = frame.get("body", {})
        image_info = body.get("image", {})
        logger.info(f"收到图片消息: chatid={image_info.get('chatid', '')}")

    async def _on_enter_chat(self, frame: dict):
        """收到进入会话事件 - 发送欢迎语"""
        try:
            welcome_body = {
                "msgtype": "text",
                "text": {
                    "content": (
                        "你好！我是公众号聚合助手\n\n"
                        "你可以发送以下命令：\n"
                        "· 友商动态 — 查看友商公众号最近3个月文章\n"
                        "· 搜索 关键词 — 搜索文章\n"
                        "· 帮助 — 查看完整使用指南\n\n"
                        "直接发文字也可以搜索文章哦！"
                    ),
                },
            }
            await self._client.reply_welcome(frame, welcome_body)
            logger.info("已发送欢迎语")
        except Exception as e:
            logger.error(f"发送欢迎语失败: {e}")

    # ========== 业务逻辑 ==========

    async def _handle_message(self, content: str, userid: str, chatid: str) -> str:
        """处理用户消息并返回回复内容"""
        original = content.strip()
        logger.info(f"原始消息: {repr(original)}")

        # 清理：去掉 @机器人名 前缀、中文/英文引号、首尾空格
        content = original
        # 去掉 @xxx 前缀（企业微信 @ 机器人后消息内容会包含 @机器人名）
        import re
        content = re.sub(r'^@[^\s]+\s*', '', content)
        # 去掉中文/英文引号
        content = content.replace('"', '').replace('"', '').replace("'", "").replace("'", "")
        content = content.strip()

        logger.info(f"清洗后: {repr(content)}")

        if not content:
            return "请输入命令，发送「帮助」查看使用指南"

        # === 命令解析 ===
        cmd = content.lower()

        # 帮助命令
        if cmd in ["帮助", "help", "？", "?", "菜单"]:
            return (
                "使用指南\n\n"
                "📋 友商监控\n"
                "· 友商动态 — 查看友商公众号最近3个月文章\n"
                "· 友商动态 30 — 查看最近30天\n"
                "· 友商列表 — 查看所有已标记的友商公众号\n\n"
                "🔍 文章搜索\n"
                "· 搜索 关键词 — 搜索文章（如：搜索 招新）\n\n"
                "💡 直接发文字也可以搜索文章"
            )

        # 友商列表
        if cmd in ["友商列表", "友商公众号", "友商名单"]:
            return self._handle_competitor_list()

        # 友商动态 - 支持模糊匹配（语音/手写可能识别不准）
        youshan_keywords = ["友商", "忧伤", "有商", "右商", "友伤", "幽商", "游商", "竞品", "对手", "动态"]
        is_youshan = any(kw in cmd for kw in youshan_keywords)
        if cmd.startswith("友商动态") or cmd.startswith("友商") or is_youshan:
            days = 90  # 默认查询3个月
            # 解析天数：支持 "友商动态30" "友商动态 30天" "友商动态 30" 等格式
            import re
            num_match = re.search(r'(\d+)', content)
            if num_match:
                try:
                    days = int(num_match.group(1))
                    days = max(1, min(days, 365))  # 限制 1-365 天
                except ValueError:
                    pass
            logger.info(f"查询友商动态: days={days}, 原始内容: {repr(content)}")
            return self._handle_competitor_report(days)

        # 搜索文章
        if cmd.startswith("搜索") or cmd.startswith("search"):
            keyword = content[2:].strip() if content.startswith("搜索") else content[6:].strip()
            if not keyword:
                return "请输入搜索关键词，例如：`搜索 招新`"
            return self._handle_search(keyword)

        # 默认：当作搜索关键词
        return self._handle_search(content)

    def _handle_competitor_list(self) -> str:
        """处理友商列表查询"""
        channels = _query_competitor_channels()
        if not channels:
            return "暂未标记任何友商公众号。"

        lines = ["友商公众号列表\n"]
        for i, ch in enumerate(channels, 1):
            note = f"({ch['competitor_note']})" if ch.get("competitor_note") else ""
            cat = ch.get("category", "")
            lines.append(f"{i}. {ch['nickname']} {note} [{cat}]")

        lines.append(f"\n共{len(channels)}个公众号")
        return "\n".join(lines)

    def _handle_competitor_report(self, days: int) -> str:
        """处理友商动态查询"""
        articles = _query_competitor_articles(days=days, limit=30)
        return _format_competitor_report(articles, days)

    def _handle_search(self, keyword: str) -> str:
        """处理文章搜索"""
        articles = _search_articles(keyword, days=30, limit=10)
        return _format_search_results(articles, keyword)

    # ========== 主动推送 ==========

    async def send_alert(self, text: str, chatid: str = "") -> bool:
        """主动推送消息到指定会话"""
        if not self._client or not self._client.is_connected:
            logger.warning("机器人未连接，无法主动推送")
            return False

        try:
            body = {
                "msgtype": "markdown",
                "markdown": {"content": text},
            }
            await self._client.send_message(chatid, body)
            logger.info(f"主动推送消息成功: chatid={chatid}")
            return True
        except Exception as e:
            logger.error(f"主动推送消息失败: {e}")
            return False

    async def push_competitor_daily(self, chatid: str = "") -> bool:
        """每日友商动态推送"""
        articles = _query_competitor_articles(days=1, limit=20)
        if not articles:
            logger.info("今日无友商动态，跳过推送")
            return True

        report = f"📋 **友商日报 - {datetime.now().strftime('%m月%d日')}**\n\n"
        report += _format_competitor_report(articles, 1)
        return await self.send_alert(report, chatid)

    @property
    def is_connected(self) -> bool:
        """检查机器人是否已连接"""
        return self._client is not None and self._client.is_connected


# 全局单例
_bot_instance: Optional[WeComBot] = None


def get_bot() -> Optional[WeComBot]:
    """获取机器人实例"""
    return _bot_instance


async def init_bot(bot_id: str, secret: str) -> WeComBot:
    """初始化并启动机器人"""
    global _bot_instance
    _bot_instance = WeComBot(bot_id, secret)
    await _bot_instance.start()
    return _bot_instance


async def shutdown_bot():
    """关闭机器人"""
    global _bot_instance
    if _bot_instance:
        await _bot_instance.stop()
        _bot_instance = None
