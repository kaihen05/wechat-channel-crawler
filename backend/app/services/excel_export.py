from sqlalchemy.orm import Session
from app.models import Article, Channel, ExportLog
from app.config import settings
from datetime import datetime, timedelta
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)


class ExcelExportService:
    """Excel导出服务"""
    
    def __init__(self):
        self.export_dir = settings.export_directory
        self.ensure_export_dir()
    
    def ensure_export_dir(self):
        """确保导出目录存在"""
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_articles_to_excel(
        self,
        db: Session,
        days: int = None,
        channel_id: int = None,
        filename: str = None
    ) -> dict:
        """
        导出文章到Excel
        
        Args:
            db: 数据库会话
            days: 导出最近几天的文章，None表示全部
            channel_id: 导出指定公众号的文章，None表示全部
            filename: 自定义文件名，None表示自动生成
        
        Returns:
            dict: 包含文件路径和统计信息
        """
        try:
            # 构建查询
            query = db.query(Article).join(Channel)
            
            if channel_id:
                query = query.filter(Article.channel_id == channel_id)
            
            if days:
                date_threshold = datetime.now() - timedelta(days=days)
                query = query.filter(Article.create_time >= date_threshold)
            
            articles = query.order_by(Article.create_time.desc()).all()
            
            if not articles:
                return {
                    "success": False,
                    "message": "没有可导出的文章"
                }
            
            # 准备数据
            data = []
            for article in articles:
                data.append({
                    "公众号": article.channel.nickname,
                    "标题": article.title,
                    "作者": article.author or "",
                    "发布时间": article.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "收集时间": article.collected_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "摘要": (article.digest or "")[:200],  # 限制长度
                    "文章链接": article.link
                })
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{settings.export_filename_prefix}_{timestamp}.xlsx"
            
            # 确保文件名以.xlsx结尾
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            filepath = os.path.join(self.export_dir, filename)
            
            # 导出到Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='文章列表')
                
                # 获取工作表对象
                worksheet = writer.sheets['文章列表']
                
                # 调整列宽
                for idx, col in enumerate(df.columns, 1):
                    max_length = max(
                        df[col].astype(str).map(len).max(),
                        len(col)
                    )
                    adjusted_width = min(max_length + 2, 50)  # 限制最大宽度
                    worksheet.column_dimensions[chr(64 + idx)].width = adjusted_width
                
                # 冻结首行
                worksheet.freeze_panes = 'A2'
            
            logger.info(f"成功导出 {len(articles)} 篇文章到 {filepath}")
            
            # 记录导出日志
            try:
                export_log = ExportLog(
                    filename=filename,
                    filepath=filepath,
                    article_count=len(articles),
                    days=days,
                    channel_id=channel_id,
                    auto_export=0
                )
                db.add(export_log)
                db.commit()
                logger.info(f"导出日志已记录")
            except Exception as e:
                logger.warning(f"记录导出日志失败: {e}")
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "count": len(articles),
                "message": f"成功导出 {len(articles)} 篇文章"
            }
            
        except Exception as e:
            logger.error(f"导出Excel失败: {e}")
            return {
                "success": False,
                "message": f"导出失败: {str(e)}"
            }
    
    def export_recent_week(
        self,
        db: Session,
        filename: str = None
    ) -> dict:
        """
        导出最近一周的文章
        
        Args:
            db: 数据库会话
            filename: 自定义文件名
        
        Returns:
            dict: 导出结果
        """
        return self.export_articles_to_excel(
            db=db,
            days=7,
            filename=filename
        )
    
    def export_all_articles(
        self,
        db: Session,
        filename: str = None
    ) -> dict:
        """
        导出所有文章
        
        Args:
            db: 数据库会话
            filename: 自定义文件名
        
        Returns:
            dict: 导出结果
        """
        return self.export_articles_to_excel(
            db=db,
            filename=filename
        )


# 全局服务实例
excel_export_service = ExcelExportService()
