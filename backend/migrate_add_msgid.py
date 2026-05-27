"""
数据库迁移脚本：添加 msgid 字段到 articles 表
"""
from app.database import SessionLocal, engine
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def migrate():
    """添加 msgid 字段到 articles 表"""
    db = SessionLocal()
    
    try:
        # 检查字段是否已存在
        result = db.execute(text("PRAGMA table_info(articles)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'msgid' not in columns:
            logger.info("开始迁移：添加 msgid 字段到 articles 表")
            db.execute(text("ALTER TABLE articles ADD COLUMN msgid VARCHAR(100) DEFAULT ''"))
            db.commit()
            logger.info("迁移完成：成功添加 msgid 字段")
        else:
            logger.info("msgid 字段已存在，跳过迁移")
            
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
    print("数据库迁移完成！")
