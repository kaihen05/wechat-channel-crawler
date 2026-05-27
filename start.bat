@echo off
chcp 65001 >nul
echo ========================================
echo   公众号渠道资源收集系统 - 启动脚本
echo ========================================
echo.
echo [1/3] 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo [错误] Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo [2/3] 进入项目目录...
cd /d "%~dp0backend"
if %errorlevel% neq 0 (
    echo [错误] 无法进入backend目录
    pause
    exit /b 1
)

echo.
echo [3/3] 启动服务...
echo.
echo ========================================
echo   服务正在启动...
echo   API文档: http://localhost:8000/docs
echo   按Ctrl+C停止服务
echo ========================================
echo.

python run.py

pause
