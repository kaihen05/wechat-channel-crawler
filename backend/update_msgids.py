#!/usr/bin/env python
"""从文章链接中提取 msgid 并更新数据库"""
from app.database import SessionLocal
from app.models import Article
import re
from urllib.parse import urlparse, parse_qs

def extract_msgid_from_link(link):
    """从文章链接中提取 msgid"""
    if not link:
        return None
    
    try:
        # 解析 URL 参数
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        
        # 尝试获取 mid 参数（通常就是 msgid）
        mid = params.get('mid', [None])[0]
        if mid:
            return mid
        
        # 尝试从 URL 路径中提取
        # 有些链接可能是 /s/xxxxx 或 /s?msgid=xxxxx 格式
        msgid_match = re.search(r'msgid=([^&]+)', link)
        if msgid_match:
            return msgid_match.group(1)
        
        return None
    except Exception as e:
        print(f"解析链接失败: {e}")
        return None

def update_msgids():
    """更新所有文章的 msgid"""
    db = SessionLocal()
    try:
        # 查询 msgid 为空或 None 的文章
        articles = db.query(Article).filter(
            (Article.msgid == None) | (Article.msgid == "")
        ).all()
        print(f"找到 {len(articles)} 篇没有 msgid 的文章")
        
        updated_count = 0
        for article in articles:
            msgid = extract_msgid_from_link(article.link)
            if msgid:
                article.msgid = msgid
                updated_count += 1
                print(f"更新文章: {article.title[:40]} -> msgid: {msgid}")
            else:
                print(f"无法提取 msgid: {article.title[:40]}")
                print(f"  Link: {article.link}")
        
        db.commit()
        print(f"\n成功更新 {updated_count} 篇文章的 msgid")
        
    except Exception as e:
        print(f"更新失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_msgids()
