@echo off
chcp 65001 >nul
echo ========================================
echo 发票重命名工具 - Win7 兼容版打包脚本
echo ========================================
echo.

:: 检查 Python Launcher 是否可用
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    :: 使用 Python Launcher 检查 3.8
    py -3.8 --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [✓] 找到 Python 3.8
        py -3.8 --version
        set PYTHON_CMD=py -3.8
        set PIP_CMD=py -3.8 -m pip
        goto :version_ok
    )
)

:: 备用：检查直接安装的 python3.8
if exist "C:\Python38\python.exe" (
    echo [✓] 找到 Python 3.8 (C:\Python38)
    C:\Python38\python.exe --version
    set PYTHON_CMD=C:\Python38\python.exe
    set PIP_CMD=C:\Python38\Scripts\pip.exe
    goto :version_ok
)

:: 备用：检查其他常见路径
if exist "C:\Program Files\Python38\python.exe" (
    echo [✓] 找到 Python 3.8 (Program Files)
    set PYTHON_CMD=C:\Program Files\Python38\python.exe
    set PIP_CMD=C:\Program Files\Python38\Scripts\pip.exe
    goto :version_ok
)

:: 检查 Users 目录下的安装
for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python38*") do (
    if exist "%%d\python.exe" (
        echo [✓] 找到 Python 3.8 (用户目录)
        set PYTHON_CMD=%%d\python.exe
        set PIP_CMD=%%d\Scripts\pip.exe
        goto :version_ok
    )
)

echo [错误] 未找到 Python 3.8
echo.
echo 请确保已安装 Python 3.8.10，安装时勾选 "Add Python to PATH"
echo 下载地址: https://www.python.org/downloads/release/python-3810/
echo.
pause
exit /b 1

:version_ok
echo.
echo.

echo [1/5] 清理旧文件...
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul
if exist "*.spec" del /q *.spec 2>nul
echo     完成
echo.

echo [2/5] 安装Win7兼容依赖...
%PIP_CMD% install -r requirements-win7.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %ERRORLEVEL% neq 0 (
    echo [警告] 安装依赖时出现问题，尝试直接安装...
    %PIP_CMD% install pdfplumber==0.6.2 PyPDF2==2.12.1 pyinstaller==4.10
)
echo     完成
echo.

echo [3/5] 打包程序...
%PYTHON_CMD% -m PyInstaller --clean --onefile --windowed --exclude-module cryptography --name "发票重命名工具_Win7版" invoice_renamer.py
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
