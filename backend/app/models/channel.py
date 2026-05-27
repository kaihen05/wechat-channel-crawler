from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Channel(Base):
    """公众号模型"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    fakeid = Column(String(100), unique=True, index=True, nullable=False)
    nickname = Column(String(100), nullable=False)
    account_name = Column(String(100))
    avatar_url = Column(String(500))
    university_name = Column(String(100))  # 学校名称
    category = Column(String(50), default="未分类")
    is_active = Column(Boolean, default=True, nullable=False)
    is_competitor = Column(Boolean, default=False, nullable=False)  # 是否为友商公众号
    competitor_keywords = Column(String(500), default="")  # 检测关键词（逗号分隔，如：网易游戏,腾讯,雷火）
    competitor_note = Column(Text, default="")  # 备注
    total_read_num = Column(Integer, default=0)  # 累计阅读量
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_sync_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Channel(id={self.id}, nickname='{self.nickname}', category='{self.category}', is_competitor={self.is_competitor})>"
