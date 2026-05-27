#!/usr/bin/env python
"""
添加测试文章，用于展示公众号累计阅读量功能
"""
import sys
sys.path.insert(0, './')

from app.database import SessionLocal
from app.models import Article, Channel
from datetime import datetime

def add_test_article():
    """添加测试文章"""
    db = SessionLocal()
    try:
        # 找到"测试技术公众号"
        channel = db.query(Channel).filter(Channel.id == 2).first()
        if not channel:
            print("[ERROR] 未找到测试技术公众号")
            return

        print(f"[OK] 找到公众号: {channel.nickname}")
        print(f"   累计阅读量: {channel.total_read_num}")

        # 检查是否已经有测试文章
        existing = db.query(Article).filter(
            Article.title == "测试文章 - 公众号累计阅读量功能"
        ).first()

        if existing:
            print("[INFO] 测试文章已存在，跳过创建")
            # 更新文章时间，让它显示在前面
            existing.create_time = datetime.now()
            db.commit()
            print("[OK] 已更新测试文章的时间，现在应该在首页显示")
        else:
            # 创建一个新文章（设置较新的时间，让它出现在首页）
            new_article = Article(
                channel_id=channel.id,
                title="测试文章 - 公众号累计阅读量功能",
                content_url="http://test.com/test_read_num_feature",
                link="http://test.com/test_read_num_feature",
                digest="这是一个测试文章，用于展示公众号累计阅读量功能。你应该能看到绿色的'公众号阅读: 67890'标签。",
                author="测试作者",
                create_time=datetime.now(),
                read_num=100
            )
            db.add(new_article)
            db.commit()
            print("[OK] 测试文章创建成功！")

        print("\n" + "=" * 80)
        print("下一步操作：")
        print("=" * 80)
        print("1. 访问 http://localhost:8000/")
        print("2. 在文章列表中找到标题为'测试文章 - 公众号累计阅读量功能'的文章")
        print("3. 应该能看到绿色的'公众号阅读: 67890'标签")
        print("\n如果没有看到标签，请重启服务器:")
        print("  - 在运行服务器的窗口按 Ctrl+C")
        print("  - 然后运行 start.bat 或 python run.py")

    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_article()
