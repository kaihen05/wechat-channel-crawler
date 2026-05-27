"""
数据库迁移脚本 - 添加 university_name 和 read_num 字段
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.models import Channel, Article

def migrate_database():
    """执行数据库迁移"""
    print("开始数据库迁移...")
    print(f"数据库位置: {engine.url}")

    # 删除所有表（会丢失数据！）
    print("\n警告：这将删除所有现有数据！")
    confirm = input("确认继续？(yes/no): ")

    if confirm.lower() != 'yes':
        print("迁移已取消")
        return

    print("\n正在删除旧表...")
    Base.metadata.drop_all(bind=engine)

    print("正在创建新表...")
    Base.metadata.create_all(bind=engine)

    print("\n数据库迁移完成！")
    print("\n新增字段：")
    print("  - Channel.university_name: 大学名称")
    print("  - Article.read_num: 浏览量")

if __name__ == "__main__":
    migrate_database()
