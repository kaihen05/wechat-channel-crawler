#!/usr/bin/env python
"""调试 API 同步阅读量的详细过程"""
from app.services.wechat_crawler import WeChatCrawler
from app.database import SessionLocal
from app.models import Article
from app.config import settings
from datetime import datetime, timedelta
import time

def debug_api_sync():
    """调试 API 同步过程"""
    db = SessionLocal()
    try:
        # 设置日期范围（最近7天）
        today = datetime.now()
        begin_date = (today - timedelta(days=7)).strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")
        
        print(f"=== 调试信息 ===")
        print(f"日期范围: {begin_date} - {end_date}")
        print(f"AppID: {settings.wechat_appid}")
        print(f"AppSecret: {settings.wechat_appsecret[:10]}...")
        print("=" * 80)
        
        # 创建爬虫实例
        crawler = WeChatCrawler(
            appid=settings.wechat_appid,
            appsecret=settings.wechat_appsecret
        )
        
        # 测试获取 access token
        print("\n1. 测试获取 access token...")
        access_token = crawler.get_access_token()
        if access_token:
            print(f"✓ 成功获取 access token: {access_token[:20]}...")
        else:
            print("✗ 获取 access token 失败")
            print("\n可能的原因：")
            print("- IP 未在微信白名单中（最可能）")
            print("- AppID 或 AppSecret 配置错误")
            return
        
        # 获取需要更新的文章
        articles = db.query(Article).filter(
            Article.create_time >= datetime.strptime(begin_date, "%Y%m%d"),
            Article.create_time <= datetime.strptime(end_date, "%Y%m%d") + timedelta(days=1)
        ).all()
        
        print(f"\n2. 找到 {len(articles)} 篇需要更新的文章")
        
        # 统计有 msgid 和没有 msgid 的文章
        with_msgid = [a for a in articles if a.msgid]
        without_msgid = [a for a in articles if not a.msgid or a.msgid == '']
        
        print(f"   有 msgid: {len(with_msgid)} 篇")
        print(f"   无 msgid: {len(without_msgid)} 篇")
        
        if without_msgid:
            print(f"\n没有 msgid 的文章：")
            for a in without_msgid:
                print(f"  - ID: {a.id}, Title: {a.title[:40]}")
        
        # 测试第一篇文章的 API 调用
        if with_msgid:
            print(f"\n3. 测试第一篇文章的 API 调用...")
            test_article = with_msgid[0]
            print(f"   文章: {test_article.title[:50]}")
            print(f"   msgid: {test_article.msgid}")
            
            stats = crawler.get_article_read_stats(
                data_id=test_article.msgid,
                begin_date=begin_date,
                end_date=end_date
            )
            
            if stats:
                print(f"   ✓ API 调用成功")
                print(f"   返回数据: {stats}")
                if len(stats) > 0:
                    total_read = sum(item.get("int_page_read_user", 0) for item in stats)
                    print(f"   总阅读量: {total_read}")
            else:
                print(f"   ✗ API 调用失败")
        
        # 尝试更新所有文章
        print(f"\n4. 尝试更新所有文章...")
        updated_count = 0
        failed_count = 0
        
        for i, article in enumerate(articles[:5], 1):  # 只测试前5篇
            print(f"\n处理 {i}/{5}: {article.title[:40]}")
            print(f"  msgid: {article.msgid or '无'}")
            
            if not article.msgid or article.msgid == '':
                print(f"  ✗ 跳过：没有 msgid")
                failed_count += 1
                continue
            
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
                    print(f"  ✓ 更新成功: {article.read_num} -> {total_read}")
                else:
                    print(f"  ✓ 无需更新 (当前值: {total_read})")
            else:
                print(f"  ✗ API 返回失败")
                failed_count += 1
            
            # 延迟
            if i < 5:
                time.sleep(0.5)
        
        db.commit()
        
        print(f"\n=== 测试结果 ===")
        print(f"处理文章数: 5")
        print(f"成功更新: {updated_count}")
        print(f"失败: {failed_count}")
        
        if failed_count > 0:
            print(f"\n失败原因分析：")
            print(f"1. 如果是 IP 白名单错误：需要在微信后台配置 IP: 111.206.145.24")
            print(f"2. 如果是文章太旧：只能获取最近7天的数据")
            print(f"3. 如果 msgid 不正确：可能需要重新从链接提取")
        
    except Exception as e:
        print(f"\n调试过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_api_sync()
