@echo off
echo ===== Telegram翻译机器人 Python 3.11 环境设置 =====
echo.

REM 检查Python 3.11是否已安装
python -c "import platform; import sys; sys.exit(0 if platform.python_version().startswith('3.11') else 1)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [√] 已检测到Python 3.11版本
) else (
    echo [×] 未检测到Python 3.11版本
    echo.
    echo 请访问以下链接下载并安装Python 3.11:
    echo https://www.python.org/downloads/release/python-3118/
    echo.
    echo 安装时请勾选"Add Python 3.11 to PATH"选项
    echo 安装完成后，请重新运行此脚本
    pause
    exit /b 1
)

REM 创建虚拟环境
echo.
echo 正在创建Python 3.11虚拟环境...
if exist "venv" (
    echo [!] 检测到已存在的虚拟环境，将重新创建
    rmdir /s /q venv
)
python -m venv venv
if %errorlevel% neq 0 (
    echo [×] 创建虚拟环境失败
    pause
    exit /b 1
)
echo [√] 虚拟环境创建成功

REM 激活虚拟环境并安装依赖
echo.
echo 正在安装项目依赖...
call venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [×] 安装依赖失败
    pause
    exit /b 1
)
echo [√] 依赖安装成功

echo.
echo ===== 设置完成 =====
echo.
echo 您现在可以通过以下命令启动翻译机器人:
echo.
echo 1. 激活虚拟环境: call venv\Scripts\activate
echo 2. 运行机器人: python src/simple.py
echo.
echo 建议使用simple.py版本，兼容性最好

pause 