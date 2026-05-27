from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Article(Base):
    """文章模型"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content_url = Column(String(500), nullable=False)
    link = Column(String(500), nullable=False)
    digest = Column(Text)
    author = Column(String(100))
    cover_url = Column(String(500))
    create_time = Column(DateTime, nullable=False)
    collected_at = Column(DateTime, server_default=func.now(), nullable=False)
    read_num = Column(Integer, default=0)  # 浏览量
    msgid = Column(String(100), default="")  # 文章消息ID，用于微信公众号 API
    
    # 关联公众号
    channel = relationship("Channel", backref="articles")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:30]}...', read_num={self.read_num})>"
