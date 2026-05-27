"""
更新现有公众号的累计阅读量
"""
from app.database import SessionLocal
from app.models import Channel, Article
from sqlalchemy import func

def update_channel_read_numbers():
    """更新所有公众号的累计阅读量"""
    db = SessionLocal()

    try:
        print("开始更新公众号累计阅读量...")

        channels = db.query(Channel).all()

        for channel in channels:
            # 计算该公众号所有文章的总阅读量
            total_reads = db.query(func.sum(Article.read_num)).filter(
                Article.channel_id == channel.id
            ).scalar() or 0

            # 更新公众号的累计阅读量
            channel.total_read_num = total_reads

            print(f"公众号: {channel.nickname}, 累计阅读量: {total_reads}")

        db.commit()
        print("\n[OK] 累计阅读量更新完成！")

    except Exception as e:
        print(f"[ERROR] 更新失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_channel_read_numbers()
