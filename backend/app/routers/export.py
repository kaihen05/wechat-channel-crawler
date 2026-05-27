from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.services.excel_export import excel_export_service
from app.models import ExportLog
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["Excel导出"])


@router.get("/excel")
async def export_excel(
    days: Optional[int] = Query(None, description="导出最近几天的文章，不填则导出全部"),
    channel_id: Optional[int] = Query(None, description="导出指定公众号的文章"),
    filename: Optional[str] = Query(None, description="自定义文件名"),
    auto: str = Query("false", description="是否自动导出（内部使用）"),
    db: Session = Depends(get_db)
):
    """
    导出文章到Excel文件
    
    参数说明：
    - days: 导出最近几天的文章（如7表示最近一周），不填则导出全部
    - channel_id: 指定公众号ID，不填则导出所有公众号
    - filename: 自定义文件名，不填则自动生成
    - auto: 内部使用，表示是否为自动导出
    """
    try:
        result = excel_export_service.export_articles_to_excel(
            db=db,
            days=days,
            channel_id=channel_id,
            filename=filename
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # 返回文件下载
        return FileResponse(
            path=result["filepath"],
            filename=result["filename"],
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出Excel异常: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/excel/week")
async def export_week(
    filename: Optional[str] = Query(None, description="自定义文件名"),
    db: Session = Depends(get_db)
):
    """
    导出最近一周的文章
    """
    result = excel_export_service.export_recent_week(db=db, filename=filename)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # 返回文件下载
    return FileResponse(
        path=result["filepath"],
        filename=result["filename"],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/excel/all")
async def export_all(
    filename: Optional[str] = Query(None, description="自定义文件名"),
    db: Session = Depends(get_db)
):
    """
    导出所有文章
    """
    result = excel_export_service.export_all_articles(db=db, filename=filename)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # 返回文件下载
    return FileResponse(
        path=result["filepath"],
        filename=result["filename"],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/logs")
async def get_export_logs(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """
    获取导出日志
    """
    logs = db.query(ExportLog).order_by(
        ExportLog.exported_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [{
        "id": log.id,
        "filename": log.filename,
        "filepath": log.filepath,
        "article_count": log.article_count,
        "days": log.days,
        "channel_id": log.channel_id,
        "auto_export": bool(log.auto_export),
        "exported_at": log.exported_at.isoformat(),
        "notes": log.notes
    } for log in logs]


@router.get("/stats")
async def get_export_stats(db: Session = Depends(get_db)):
    """
    获取导出统计信息
    """
    total_exports = db.query(ExportLog).count()
    total_articles = db.query(ExportLog).with_entities(
        db.func.sum(ExportLog.article_count)
    ).scalar() or 0
    
    auto_exports = db.query(ExportLog).filter(
        ExportLog.auto_export == 1
    ).count()
    
    # 最近的导出
    recent_export = db.query(ExportLog).order_by(
        ExportLog.exported_at.desc()
    ).first()
    
    return {
        "total_exports": total_exports,
        "total_articles": total_articles,
        "auto_exports": auto_exports,
        "manual_exports": total_exports - auto_exports,
        "last_export": recent_export.exported_at.isoformat() if recent_export else None
    }
