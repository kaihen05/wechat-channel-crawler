from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class ExportLog(Base):
    """导出日志模型"""
    __tablename__ = "export_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    article_count = Column(Integer, nullable=False)
    days = Column(Integer)  # 导出天数范围
    channel_id = Column(Integer)  # 导出的公众号ID
    auto_export = Column(Integer, default=0)  # 是否自动导出：0否，1是
    exported_at = Column(DateTime, server_default=func.now(), nullable=False)
    notes = Column(Text)  # 备注
    
    def __repr__(self):
        return f"<ExportLog(id={self.id}, filename='{self.filename}', count={self.article_count})>"
