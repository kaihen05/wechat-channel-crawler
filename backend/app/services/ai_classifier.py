"""
AI分类服务 - 使用DeepSeek API自动分类
"""
import httpx
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AIClassifier:
    """AI分类器"""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url

        # 预定义的分类
        self.predefined_categories = {
            "游戏": ["游戏", "电竞", "游戏开发", "游戏设计", "游戏运营", "游戏美术"],
            "产品": ["产品", "产品经理", "产品设计", "产品运营", "用户体验", "产品思维"],
            "人力": ["人力", "人力资源", "HR", "招聘", "人才", "校园招聘", "就业"],
            "技术": ["技术", "开发", "编程", "算法", "AI", "人工智能", "大数据", "云计算", "前端", "后端"],
            "综合": ["学生会", "研会", "研究生会", "校园", "学生会", "院学生会", "校学生会", "院研会", "校研会"]
        }

    def classify_by_keywords(self, nickname: str) -> Optional[str]:
        """基于关键词的分类"""
        for category, keywords in self.predefined_categories.items():
            for keyword in keywords:
                if keyword in nickname:
                    return category
        return None

    async def classify_by_ai(self, nickname: str, description: str = "") -> Optional[str]:
        """使用AI进行分类"""
        if not self.api_key:
            logger.warning("未配置DeepSeek API key，跳过AI分类")
            return None

        # 先尝试关键词匹配
        keyword_result = self.classify_by_keywords(nickname)
        if keyword_result:
            return keyword_result

        try:
            # 构建提示词
            prompt = f"""请根据公众号名称，将其分类到以下类别之一：游戏、产品、人力、技术、综合。

公众号名称：{nickname}
{f'公众号描述：{description}' if description else ''}

请只返回分类名称（游戏/产品/人力/技术/综合），不要返回其他内容。"""

            # 调用DeepSeek API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": "你是一个专业的公众号分类助手。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 10
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()

                    # 验证返回的分类是否有效
                    valid_categories = ["游戏", "产品", "人力", "技术", "综合"]
                    if content in valid_categories:
                        logger.info(f"AI分类成功: {nickname} -> {content}")
                        return content
                    else:
                        logger.warning(f"AI返回了无效分类: {content}")
                        return "未分类"
                else:
                    logger.error(f"AI分类失败: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"AI分类异常: {e}")
            return None

    async def auto_classify(self, nickname: str, description: str = "") -> str:
        """自动分类（优先关键词，其次AI）"""
        # 先尝试关键词匹配
        keyword_result = self.classify_by_keywords(nickname)
        if keyword_result:
            return keyword_result

        # 使用AI分类
        ai_result = await self.classify_by_ai(nickname, description)
        if ai_result:
            return ai_result

        # 默认返回未分类
        return "未分类"


# 创建全局分类器实例
classifier = AIClassifier()


async def auto_classify_channel(nickname: str, description: str = "") -> str:
    """
    自动分类公众号

    Args:
        nickname: 公众号名称
        description: 公众号描述（可选）

    Returns:
        分类名称
    """
    return await classifier.auto_classify(nickname, description)
