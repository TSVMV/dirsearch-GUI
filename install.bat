@echo off
REM dirsearchx 安装脚本（Windows）
setlocal

echo [1/4] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 未找到 python，请先安装 Python 3.9+
    exit /b 1
)

echo [2/4] 克隆 dirsearch 到 vendor（若不存在）...
if not exist "vendor\dirsearch\dirsearch.py" (
    git clone --depth 1 https://github.com/maurosoria/dirsearch.git vendor\dirsearch
    if errorlevel 1 (
        echo dirsearch 克隆失败，请检查网络
        exit /b 1
    )
) else (
    echo 已存在 vendor\dirsearch，跳过克隆
)

echo [3/4] 安装 dirsearchx...
python -m pip install --upgrade pip >nul
python -m pip install .
if errorlevel 1 (
    echo 安装失败
    exit /b 1
)

echo [4/4] 验证...
python -c "from dirsearchx.core import config; h,v=config.check_dirsearch(); print('dirsearch @', h.path, '|', v)"
if errorlevel 1 (
    echo 验证失败
    exit /b 1
)

echo.
echo 完成。启动方式：
echo   dirsearch-gui          桌面 GUI
echo   dirsearch-cli -u http://target/ -t 30   透传命令行
endlocal
