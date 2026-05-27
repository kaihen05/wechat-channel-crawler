from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse, HTMLResponse
from app.database import init_db
from app.config import settings
from app.routers import auth, channels, articles, export, mcp, login, analysis
from app.services.scheduler import scheduler
from app.routers.login import verify_token, is_admin, get_token_payload
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="公众号渠道资源收集系统",
    description="用于微信公众号文章的定期收集和管理",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(login.router)  # 登录路由放最前面
app.include_router(auth.router)
app.include_router(channels.router)
app.include_router(articles.router)
app.include_router(export.router)
app.include_router(mcp.router)
app.include_router(analysis.router)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 不需要认证的路径白名单（页面和静态资源）
PUBLIC_PATHS = {
    "/", "/login.html",
    "/api/auth/login", "/api/auth/status",
    "/health",
}

# 需要超级管理者权限的页面（admin only）
ADMIN_ONLY_PAGES = {
    "/manage.html", "/config.html",
}

# 需要超级管理者权限的 API 路径前缀（写操作）
ADMIN_ONLY_API_PREFIXES = (
    "/api/channels",  # 管理公众号（增删改）
)

PUBLIC_PATH_PREFIXES = (
    "/static/",  # 静态资源
)

# GET 请求免认证的前缀（读取接口公开）
PUBLIC_GET_PREFIXES = (
    "/api/channels",
    "/api/articles",
    "/api/mcp",
    "/api/bot",
    "/api/analysis",
)

# 所有方法免认证的前缀（管理后台需要读写）— 已移到 ADMIN_ONLY
# PUBLIC_ALL_PREFIXES 已废弃，管理API需要admin权限

# POST 请求免认证的路径
PUBLIC_POST_PATHS = {
    "/api/channels/search",  # 搜索公众号不需要登录
}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """认证中间件：未登录则跳转到登录页，管理页面需要超级管理者权限"""
    # 使用 scope["path"] 获取路径，避免代理环境下 request.url.path 返回完整 URL
    path = request.scope.get("path", request.url.path)
    method = request.method
    
    # 白名单路径直接放行（支持所有方法，包括 HEAD 健康检查）
    if path in PUBLIC_PATHS:
        return await call_next(request)
    if any(path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES):
        return await call_next(request)
    
    # HEAD 请求等同于 GET，用于健康检查
    if method == "HEAD":
        return await call_next(request)
    
    # GET 请求对公开前缀放行
    if method == "GET" and any(path.startswith(prefix) for prefix in PUBLIC_GET_PREFIXES):
        return await call_next(request)

    # 特定 POST 路径放行
    if method == "POST" and path in PUBLIC_POST_PATHS:
        return await call_next(request)
    
    # 以下需要登录
    if not verify_token(request):
        # API 请求返回 401
        if path.startswith("/api/"):
            return JSONResponse(status_code=401, content={"detail": "未登录或登录已过期"})
        # 页面请求重定向到登录页
        return RedirectResponse(url="/login.html", status_code=302)
    
    # 已登录，检查管理员权限
    # 管理页面需要 admin 角色
    if path in ADMIN_ONLY_PAGES and not is_admin(request):
        # 非管理员访问管理页面，重定向到首页
        return RedirectResponse(url="/?forbidden=1", status_code=302)
    
    # 管理 API（非GET请求）需要 admin 角色
    if (method != "GET" and 
        any(path.startswith(prefix) for prefix in ADMIN_ONLY_API_PREFIXES) and
        not is_admin(request)):
        return JSONResponse(status_code=403, content={"detail": "需要超级管理者权限"})
    
    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库和定时任务"""
    logger.info("初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")

    # 如果数据库为空，自动导入种子数据
    import sqlite3
    try:
        conn = sqlite3.connect("data/channels.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM channels")
        count = c.fetchone()[0]
        if count == 0:
            logger.info("数据库为空，开始导入种子数据...")
            import os
            seed_file = "data/seed_data.sql"
            if os.path.exists(seed_file):
                with open(seed_file, "r", encoding="utf-8") as f:
                    sql = f.read()
                # 适配新的 competitor_keywords 字段
                sql = sql.replace(
                    "university_name, category, is_active, created_at, updated_at, last_sync_at, total_read_num)",
                    "university_name, category, is_active, is_competitor, competitor_keywords, competitor_note, created_at, updated_at, last_sync_at, total_read_num)"
                )
                for cat in ["游戏", "综合", "人力", "产品", "技术"]:
                    sql = sql.replace(f"'{cat}', 1, '2026-", f"'{cat}', 1, 0, '', '', '2026-")
                c.executescript(sql)
                conn.commit()
                c.execute("SELECT COUNT(*) FROM channels")
                ch_count = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM articles")
                art_count = c.fetchone()[0]
                logger.info(f"种子数据导入完成: {ch_count} 个公众号, {art_count} 篇文章")
            else:
                logger.warning(f"种子数据文件不存在: {seed_file}")
        conn.close()
    except Exception as e:
        logger.error(f"导入种子数据失败: {e}")

    logger.info("启动定时任务调度器...")
    scheduler.start()
    logger.info("定时任务调度器已启动")

    # 启动企业微信机器人
    if settings.wecom_bot_enabled and settings.wecom_bot_id and settings.wecom_bot_secret:
        logger.info("启动企业微信智能机器人...")
        from app.services.wecom_bot import init_bot
        await init_bot(settings.wecom_bot_id, settings.wecom_bot_secret)
        logger.info("企业微信智能机器人已启动")
    else:
        logger.info("企业微信智能机器人未启用或未配置凭证")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时停止定时任务"""
    # 关闭企业微信机器人
    from app.services.wecom_bot import shutdown_bot
    await shutdown_bot()
    logger.info("企业微信智能机器人已关闭")
    
    logger.info("停止定时任务调度器...")
    scheduler.stop()
    logger.info("定时任务调度器已停止")


# 静态文件目录
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

@app.get("/")
@app.head("/")
async def root():
    """根路径 - 主页"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>微信公众号聚合器</h1><p>首页加载失败，请检查静态文件</p>")


@app.get("/login.html")
async def login_page():
    """登录页面"""
    login_path = os.path.join(STATIC_DIR, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return HTMLResponse("<h1>登录页加载失败</h1>")


@app.get("/manage.html")
async def manage_page():
    """公众号管理页面"""
    manage_path = os.path.join(STATIC_DIR, "manage.html")
    if os.path.exists(manage_path):
        return FileResponse(manage_path)
    return RedirectResponse(url="/login.html")


@app.get("/config.html")
async def config_page():
    """凭证配置页面"""
    config_path = os.path.join(STATIC_DIR, "config.html")
    if os.path.exists(config_path):
        return FileResponse(config_path)
    return RedirectResponse(url="/login.html")


@app.get("/health")
async def health_check():
    """健康检查"""
    from app.services.wecom_bot import get_bot
    bot = get_bot()
    bot_status = "connected" if bot and bot.is_connected else "disconnected" if bot else "not_configured"
    return {"status": "ok", "wecom_bot": bot_status}


@app.get("/api/bot/status")
async def bot_status():
    """企业微信机器人状态"""
    from app.services.wecom_bot import get_bot
    bot = get_bot()
    return {
        "enabled": settings.wecom_bot_enabled,
        "bot_id": settings.wecom_bot_id[:8] + "***" if settings.wecom_bot_id else "",
        "connected": bot.is_connected if bot else False,
    }


@app.get("/test_api.html")
async def test_api_page():
    """API 测试页面"""
    return FileResponse(os.path.join(STATIC_DIR, "test_api.html"))


@app.get("/test_simple.html")
async def test_simple_page():
    """简单测试页面"""
    return FileResponse(os.path.join(STATIC_DIR, "test_simple.html"))


@app.get("/api_status.html")
async def api_status_page():
    """API 状态页面"""
    return FileResponse(os.path.join(STATIC_DIR, "api_status.html"))


@app.get("/IP_WHITELIST_配置指南.md")
async def ip_whitelist_guide():
    """IP 白名单配置指南"""
    return FileResponse(os.path.join(STATIC_DIR, "IP_WHITELIST_配置指南.md"))


@app.get("/当前问题总结.md")
async def current_problem_summary():
    """当前问题总结"""
    return FileResponse(os.path.join(STATIC_DIR, "当前问题总结.md"))


@app.get("/channel_import_template.xlsx")
async def download_template():
    """下载Excel导入模板"""
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "channel_import_template.xlsx")
    if os.path.exists(template_path):
        return FileResponse(template_path, filename="公众号导入模板.xlsx")
    return JSONResponse(status_code=404, content={"detail": "模板文件不存在"})


if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
