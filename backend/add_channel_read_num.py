"""
数据库迁移：为channels表添加total_read_num字段
"""
from app.database import engine, Base, SessionLocal
from app.models.channel import Channel
from sqlalchemy import text

def migrate():
    """执行数据库迁移"""
    print("开始数据库迁移...")

    # 创建数据库连接
    db = SessionLocal()

    try:
        # 检查字段是否已存在
        result = db.execute(text("PRAGMA table_info(channels)"))
        columns = [row[1] for row in result.fetchall()]

        if 'total_read_num' in columns:
            print("[OK] 字段 total_read_num 已存在，跳过迁移")
        else:
            # 添加新字段
            print("正在添加 total_read_num 字段...")
            db.execute(text("ALTER TABLE channels ADD COLUMN total_read_num INTEGER DEFAULT 0"))
            db.commit()
            print("[OK] 字段 total_read_num 添加成功")

        # 验证迁移结果
        result = db.execute(text("PRAGMA table_info(channels)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"\n当前channels表包含的字段: {columns}")

        print("\n[OK] 数据库迁移完成！")

    except Exception as e:
        print(f"[ERROR] 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
