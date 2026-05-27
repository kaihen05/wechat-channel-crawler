"""
学校识别AI服务 - 使用DeepSeek API自动识别学校
"""
import httpx
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AIUniversityClassifier:
    """AI学校分类器"""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url

        # 中国主要大学关键词库
        self.university_keywords = {
            "清华大学": ["清华", "Tsinghua"],
            "北京大学": ["北大", "Peking University", "Beijing"],
            "复旦大学": ["复旦", "Fudan"],
            "上海交通大学": ["上海交大", "上交", "SJTU", "交大"],
            "浙江大学": ["浙大", "Zhejiang"],
            "中国科学技术大学": ["中科大", "USTC"],
            "南京大学": ["南大", "Nanjing University"],
            "西安交通大学": ["西安交大", "XJTU"],
            "哈尔滨工业大学": ["哈工大", "HIT"],
            "华中科技大学": ["华科", "HUST"],
            "武汉大学": ["武大", "Wuhan University"],
            "中山大学": ["中大", "Sun Yat-sen", "SYSU"],
            "四川大学": ["川大", "Sichuan"],
            "中国人民大学": ["人大", "RUC"],
            "南开大学": ["南开", "Nankai"],
            "天津大学": ["天大", "Tianjin University"],
            "同济大学": ["同济"],
            "华东师范大学": ["华师大", "ECNU"],
            "厦门大学": ["厦大", "Xiamen"],
            "山东大学": ["山大", "Shandong"],
            "华南理工大学": ["华工", "SCUT"],
            "北京师范大学": ["北师大", "BNU"],
            "吉林大学": ["吉大", "Jilin"],
            "中南大学": ["中南", "CSU"],
            "东南大学": ["东南", "Southeast"],
            "大连理工大学": ["大工", "DUT"],
            "重庆大学": ["重大", "Chongqing"],
            "北京航空航天大学": ["北航", "Beihang", "BUAA"],
            "北京理工大学": ["北理", "BIT"],
            "西北工业大学": ["西工大", "NPU", "NWPU"],
            "兰州大学": ["兰大", "Lanzhou"],
            "中国农业大学": ["中国农大", "CAU"],
            "电子科技大学": ["电子科大", "UESTC"],
            "中央民族大学": ["民大", "MUC"],
            "东北大学": ["东北大学", "NEU"],
            "北京科技大学": ["北科", "USTB"],
            "华东理工大学": ["华理", "ECUST"],
            "南京航空航天大学": ["南航", "NUAA"],
            "上海大学": ["上大", "Shanghai University"],
            "北京交通大学": ["北交", "BJTU"],
            "哈尔滨工程大学": ["哈工程", "HEU"],
            "南京理工大学": ["南理", "NJUST"],
            "西北大学": ["西北大学", "Northwest"],
            "东华大学": ["东华"],
            "苏州大学": ["苏大", "Soochow"],
            "西南大学": ["西南大学", "Southwest"],
            "华中师范大学": ["华师", "CCNU"],
            "湖南大学": ["湖大", "Hunan University"],
            "郑州大学": ["郑大", "Zhengzhou"],
            "福州大学": ["福大", "Fuzhou"],
            "合肥工业大学": ["合工大", "HFUT"],
            "南昌大学": ["昌大", "Nanchang"],
            "武汉理工大学": ["武理", "WUT"],
            "中国海洋大学": ["中国海大", "OUC"],
            "西北农林科技大学": ["西农", "NWAFU"],
            "中国地质大学": ["地大", "CUG"],
            "北京工业大学": ["北工大", "BJUT"],
            "北京邮电大学": ["北邮", "BUPT"],
            "北京林业大学": ["北林", "BFU"],
            "东北林业大学": ["东林", "NEFU"],
            "北京化工大学": ["北化", "BUCT"],
            "北京中医药大学": ["北中医", "BUCM"],
            "对外经济贸易大学": ["对外经贸", "UIBE"],
            "中央财经大学": ["央财", "CUFE"],
            "上海财经大学": ["上财", "SUFE"],
            "西南财经大学": ["西财", "SWUFE"],
            "中南财经政法大学": ["中南财经", "ZUEL"],
            "中国政法大学": ["法大", "CUPL"],
            "西南政法大学": ["西政", "SWUPL"],
            "北京外国语大学": ["北外", "BFSU"],
            "上海外国语大学": ["上外", "SISU"],
            "中国传媒大学": ["中传", "CUC"],
            "北京语言大学": ["北语", "BLCU"],
            "外交学院": ["外交"],
            "国际关系学院": ["国关"],
            "中国人民公安大学": ["公大", "CPSU"],
            "北京体育大学": ["北体", "BSU"],
            "中央音乐学院": ["央音", "CCOM"],
            "中央美术学院": ["央美", "CAFA"],
            "中央戏剧学院": ["中戏", "CAD"],
            "北京电影学院": ["北影", "BFA"],
        }

    def classify_by_keywords(self, nickname: str) -> Optional[str]:
        """基于关键词的学校识别"""
        nickname_lower = nickname.lower()
        for university, keywords in self.university_keywords.items():
            for keyword in keywords:
                if keyword.lower() in nickname_lower:
                    return university
        return None

    async def classify_by_ai(self, nickname: str, description: str = "") -> Optional[str]:
        """使用AI进行学校识别"""
        if not self.api_key:
            logger.warning("未配置DeepSeek API key，跳过AI学校识别")
            return None

        # 先尝试关键词匹配
        keyword_result = self.classify_by_keywords(nickname)
        if keyword_result:
            return keyword_result

        try:
            # 构建提示词
            university_list = list(self.university_keywords.keys())
            universities_str = "、".join(university_list[:30])  # 列出前30个主要大学

            prompt = f"""请根据公众号名称，识别它属于哪所中国高校。

可识别的大学包括：{universities_str} 等

公众号名称：{nickname}
{f'公众号描述：{description}' if description else ''}

如果无法确定具体学校，请返回"其他高校"。
请只返回学校名称，不要返回其他内容。"""

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
                            {"role": "system", "content": "你是一个专业的中国高校识别助手。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 20
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()

                    # 清理可能的引号
                    content = content.strip('"\'').strip()

                    logger.info(f"AI学校识别成功: {nickname} -> {content}")
                    return content
                else:
                    logger.error(f"AI学校识别失败: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"AI学校识别异常: {e}")
            return None

    async def auto_classify(self, nickname: str, description: str = "") -> str:
        """自动学校识别（优先关键词，其次AI）"""
        # 先尝试关键词匹配
        keyword_result = self.classify_by_keywords(nickname)
        if keyword_result:
            return keyword_result

        # 使用AI识别
        ai_result = await self.classify_by_ai(nickname, description)
        if ai_result:
            return ai_result

        # 默认返回其他高校
        return "其他高校"

    def get_all_universities(self) -> list:
        """获取所有大学列表"""
        return sorted(list(self.university_keywords.keys()))


# 创建全局分类器实例
university_classifier = AIUniversityClassifier()


async def auto_classify_university(nickname: str, description: str = "") -> str:
    """
    自动识别学校

    Args:
        nickname: 公众号名称
        description: 公众号描述（可选）

    Returns:
        学校名称
    """
    return await university_classifier.auto_classify(nickname, description)
