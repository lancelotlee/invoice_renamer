@echo off
chcp 65001 >nul
echo ========================================
echo 发票重命名工具 - Win7 兼容版打包脚本
echo ========================================
echo.

:: 检查Python版本
python --version 2>nul | findstr "3.8" >nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 需要 Python 3.8.x 版本才能支持 Windows 7
    echo.
    echo 当前Python版本:
    python --version 2>nul || echo 未安装Python
    echo.
    echo 请下载安装 Python 3.8.10:
    echo https://www.python.org/downloads/release/python-3810/
    echo.
    pause
    exit /b 1
)

echo [✓] Python版本检查通过
python --version
echo.

echo [1/5] 清理旧文件...
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul
if exist "*.spec" del /q *.spec 2>nul
echo     完成
echo.

echo [2/5] 安装Win7兼容依赖...
pip install -r requirements-win7.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo     完成
echo.

echo [3/5] 打包程序...
pyinstaller --onefile --windowed --name "发票重命名工具_Win7版" invoice_renamer.py
echo     完成
echo.

echo [4/5] 复制说明文档...
if exist "dist\发票重命名工具_Win7版.exe" (
    copy "发票类型说明.md" "dist\" >nul
    echo     完成
) else (
    echo     [警告] 未找到exe文件
)
echo.

echo [5/5] 验证输出...
if exist "dist\发票重命名工具_Win7版.exe" (
    echo ========================================
    echo  打包成功！
    echo ========================================
    echo.
    echo 输出文件: 
    echo   dist\发票重命名工具_Win7版.exe
    echo.
    echo 文件大小:
    for %%I in ("dist\发票重命名工具_Win7版.exe") do echo   %%~zI 字节
    echo.
    echo [提示] 此exe文件可在 Windows 7/8/10/11 上运行
    echo.
    echo 按任意键打开输出目录...
    pause >nul
    start dist
) else (
    echo ========================================
    echo  [错误] 打包失败
    echo ========================================
    echo.
    pause
)
