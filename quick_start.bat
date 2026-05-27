@echo off
chcp 65001 >nul
echo ========================================
echo   快速启动服务（跳过检查）
echo ========================================
echo.
echo API文档: http://localhost:8000/docs
echo 按Ctrl+C停止服务
echo ========================================
echo.

cd /d "%~dp0backend"
python run.py

pause
