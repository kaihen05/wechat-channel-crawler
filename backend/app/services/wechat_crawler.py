import httpx
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.config import settings
import logging
import json

logger = logging.getLogger(__name__)


class WeChatSessionError(Exception):
    """微信 session 失效（token/cookie 过期）"""
    pass


class WeChatCrawler:
    """微信公众号后台爬虫"""
    
    def __init__(self, token: str = "", cookie: str = "", appid: str = "", appsecret: str = ""):
        self.token = token
        self.cookie = cookie
        self.appid = appid
        self.appsecret = appsecret
        self.base_url = "https://mp.weixin.qq.com"
        self.api_url = "https://api.weixin.qq.com"
        self.headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 请求计数
        self.request_count = 0
        self.last_request_time = None
        self.hourly_count = 0
        self.last_hour_reset = datetime.now()
        
        # Access token 缓存
        self._access_token = None
        self._token_expires_at = None

        # 批次同步模式（减少批次内的延迟，避免单批次耗时过长）
        self._batch_mode = False
        self._batch_start_time = None
    
    def _random_delay(self, min_sec: int = None, max_sec: int = None):
        """随机延迟（批次模式下缩短延迟以加快同步速度）"""
        min_sec = min_sec or settings.request_interval_min
        max_sec = max_sec or settings.request_interval_max

        # 批次模式：减少延迟（每批次需同步30个账号，不能拖太慢）
        if self._batch_mode:
            min_sec = max(3, min_sec // 3)   # 原来 5s → 3s
            max_sec = max(8, max_sec // 3)   # 原来 15s → 5s

        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"随机延迟 {delay:.2f} 秒")
        time.sleep(delay)

    def _check_rate_limit(self):
        """检查请求频率限制"""
        now = datetime.now()

        # 重置每小时计数器
        if (now - self.last_hour_reset).seconds >= 3600:
            self.hourly_count = 0
            self.last_hour_reset = now

        # 检查每小时限制
        if self.hourly_count >= settings.max_requests_per_hour:
            logger.warning(f"达到每小时请求限制: {self.hourly_count}/{settings.max_requests_per_hour}")
            return False

        return True

    def enter_batch_mode(self):
        """进入批次模式：记录批次开始时间，启用快速同步"""
        self._batch_mode = True
        self._batch_start_time = datetime.now()
        logger.debug("进入批次同步模式")

    def exit_batch_mode(self):
        """退出批次模式：恢复普通模式"""
        if self._batch_mode:
            elapsed = (datetime.now() - self._batch_start_time).total_seconds() if self._batch_start_time else 0
            self._batch_mode = False
            logger.debug(f"退出批次同步模式，批次耗时 {elapsed:.1f}s")

    def get_batch_progress(self) -> dict:
        """获取批次同步进度信息"""
        elapsed = (datetime.now() - self._batch_start_time).total_seconds() if self._batch_start_time else 0
        return {
            "batch_mode": self._batch_mode,
            "elapsed_seconds": elapsed,
            "hourly_count": self.hourly_count,
            "total_requests": self.request_count
        }
    
    def _make_request(self, url: str, params: dict = None, method: str = "GET") -> Optional[Dict]:
        """发送HTTP请求"""
        if not self._check_rate_limit():
            return None
        
        try:
            # 请求前延迟
            if self.last_request_time:
                self._random_delay()
            
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                if method == "GET":
                    response = client.get(
                        url,
                        headers=self.headers,
                        params=params
                    )
                else:
                    response = client.post(
                        url,
                        headers=self.headers,
                        params=params
                    )
                
                self.request_count += 1
                self.hourly_count += 1
                self.last_request_time = datetime.now()
                
                if response.status_code == 200:
                    data = response.json()
                    # 微信内部错误码检测（session 失效等）
                    base_resp = data.get("base_resp") if isinstance(data, dict) else None
                    if base_resp and base_resp.get("ret", 0) != 0:
                        err_msg = base_resp.get("err_msg", "unknown")
                        ret_code = base_resp.get("ret")
                        logger.error(f"微信接口错误: ret={ret_code}, msg={err_msg}")
                        if ret_code in (200003, 200002) or "session" in err_msg.lower():
                            raise WeChatSessionError(f"微信凭证已过期，请重新配置 token 和 cookie (ret={ret_code})")
                        raise Exception(f"微信接口返回错误: {err_msg} (ret={ret_code})")
                    return data
                else:
                    logger.error(f"请求失败: {response.status_code}")
                    return None
                    
        except WeChatSessionError:
            raise  # 向上传递，不被下面的 generic except 吞掉
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return None
    
    def search_accounts(self, keyword: str, limit: int = 5) -> List[Dict]:
        """搜索公众号"""
        url = f"{self.base_url}/cgi-bin/searchbiz"
        
        params = {
            "action": "search_biz",
            "begin": 0,
            "count": limit,
            "query": keyword,
            "token": self.token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": 1
        }
        
        result = self._make_request(url, params)
        if not result:
            return []
        
        # 搜索后额外延迟
        self._random_delay(8, 20)
        
        accounts = []
        for item in result.get("list", []):
            accounts.append({
                "fakeid": item.get("fakeid"),
                "nickname": item.get("nickname"),
                "round_head_img": item.get("round_head_img"),
                "account_name": item.get("account_name")
            })
        
        return accounts
    
    def get_articles(self, fakeid: str, days: int = 3, count: int = 10) -> List[Dict]:
        """获取公众号文章列表（自动翻页，获取所有符合条件的文章）"""
        url = f"{self.base_url}/cgi-bin/appmsg"

        begin_date = datetime.now() - timedelta(days=days)

        all_articles = []
        begin = 0
        page_size = 50  # 微信每次最多返回50条

        while True:
            params = {
                "action": "list_ex",
                "begin": begin,
                "count": page_size,
                "fakeid": fakeid,
                "type": 9,
                "query": "",
                "token": self.token,
                "lang": "zh_CN",
                "f": "json",
                "ajax": 1
            }

            result = self._make_request(url, params)
            if not result:
                break

            app_msg_list = result.get("app_msg_list", [])
            if not app_msg_list:
                # 空列表说明没有更多了
                break

            for item in app_msg_list:
                # 获取 content_url，如果为空则使用 link
                content_url = item.get("content_url") or item.get("link", "")
                link = item.get("link", "")

                # 尝试获取作者，如果没有则使用默认值
                author = item.get("author")
                if not author:
                    author = item.get("item_show_type") or "未知作者"

                # 尝试获取浏览量（可能不存在）
                read_num = item.get("read_num") or item.get("visit_num") or 0

                # 提取 msgid (从 link 或 content_url 中)
                msgid = item.get("msgid", "")
                if not msgid:
                    # 尝试从 URL 中提取 msgid
                    import re
                    msgid_match = re.search(r'msgid=([^&]+)', link or content_url)
                    if msgid_match:
                        msgid = msgid_match.group(1)

                all_articles.append({
                    "title": item.get("title"),
                    "link": link,
                    "create_time": datetime.fromtimestamp(item.get("create_time")),
                    "digest": item.get("digest"),
                    "cover": item.get("cover"),
                    "author": author,
                    "content_url": content_url,
                    "read_num": read_num,
                    "msgid": msgid  # 添加 msgid
                })

            # 如果返回的不够一页，说明是最后一页
            if len(app_msg_list) < page_size:
                break

            begin += page_size

        return all_articles
    
    def get_article_content(self, content_url: str) -> Optional[str]:
        """获取文章详细内容"""
        try:
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.get(content_url, headers=self.headers)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            logger.error(f"获取文章内容失败: {e}")
        
        return None
    
    def test_credentials(self) -> bool:
        """测试凭证是否有效"""
        url = f"{self.base_url}/cgi-bin/home?t=home/index&lang=zh_CN&token={self.token}"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=self.headers)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"凭证测试失败: {e}")
            return False
    
    def get_access_token(self) -> Optional[str]:
        """获取微信公众号 API access token"""
        if not self.appid or not self.appsecret:
            logger.warning("未配置 AppID 或 AppSecret，无法获取 access token")
            return None
        
        # 检查缓存的 token 是否还有效
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                logger.debug("使用缓存的 access token")
                return self._access_token
        
        # 获取新的 token
        url = f"{self.api_url}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.appsecret
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                data = response.json()
                
                if "access_token" in data:
                    self._access_token = data["access_token"]
                    # 提前 5 分钟过期
                    self._token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 300)
                    logger.info("成功获取 access token")
                    return self._access_token
                else:
                    logger.error(f"获取 access token 失败: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"获取 access token 异常: {e}")
            return None
    
    def get_article_read_stats(self, data_id: str, begin_date: str, end_date: str) -> Optional[Dict]:
        """
        通过微信公众号 API 获取文章阅读统计数据
        
        参数:
            data_id: 文章数据ID (从公众号后台获取)
            begin_date: 开始日期，格式 YYYYMMDD
            end_date: 结束日期，格式 YYYYMMDD
        
        返回:
            包含阅读量等数据的字典
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error("无法获取 access token")
            return None
        
        url = f"{self.api_url}/cgi-bin/datacube/getarticleread?access_token={access_token}"
        
        payload = {
            "begin_date": begin_date,
            "end_date": end_date,
            "msgid_list": [data_id]
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                data = response.json()
                
                if "errcode" in data and data["errcode"] == 0:
                    logger.info(f"成功获取文章阅读统计: {data_id}")
                    return data.get("list", [])
                else:
                    logger.error(f"获取文章阅读统计失败: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"获取文章阅读统计异常: {e}")
            return None
    
    def get_user_summary(self, begin_date: str, end_date: str) -> Optional[Dict]:
        """
        获取用户增减数据，可用于估算公众号总阅读量
        
        参数:
            begin_date: 开始日期，格式 YYYYMMDD
            end_date: 结束日期，格式 YYYYMMDD
        """
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"{self.api_url}/cgi-bin/datacube/getusersummary?access_token={access_token}"
        
        payload = {
            "begin_date": begin_date,
            "end_date": end_date
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                data = response.json()
                
                if "errcode" in data and data["errcode"] == 0:
                    logger.info(f"成功获取用户增减数据")
                    return data.get("list", [])
                else:
                    logger.error(f"获取用户增减数据失败: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"获取用户增减数据异常: {e}")
            return None


def test_credentials(token: str, cookie: str) -> Dict:
    """测试微信凭证"""
    crawler = WeChatCrawler(token, cookie)
    is_valid = crawler.test_credentials()
    
    return {
        "valid": is_valid,
        "message": "凭证有效" if is_valid else "凭证无效或已过期",
        "checked_at": datetime.now().isoformat()
    }
