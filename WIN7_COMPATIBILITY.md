# Windows 7 兼容性解决方案

## 问题原因

当前项目使用的 Python 版本和 PyInstaller 版本**不支持 Windows 7**：

| 组件 | 当前要求 | Win7兼容版本 |
|------|----------|--------------|
| Python | 3.9+ | **Python 3.8.10** (最后一个支持Win7的版本) |
| PyInstaller | 6.x | **PyInstaller 4.10** (最后一个支持Win7的版本) |

## Win7 兼容的打包步骤

### 1. 安装 Python 3.8.10（Win7最后支持的版本）

下载地址：https://www.python.org/downloads/release/python-3810/

选择：**Windows installer (64-bit)** 或 **Windows installer (32-bit)**

安装时勾选：☑️ **Add Python to PATH**

### 2. 验证 Python 版本

```cmd
python --version
# 应显示 Python 3.8.10
```

### 3. 安装兼容的依赖版本

```cmd
pip install pdfplumber==0.6.2
pip install PyInstaller==4.10
pip install PyPDF2==2.12.1
```

### 4. 使用兼容配置打包

创建 `build_win7.bat`：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo Win7 兼容版打包脚本
echo ========================================
echo.

:: 检查Python版本
python --version | findstr "3.8" >nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 需要 Python 3.8.x 版本
    echo 当前版本:
    python --version
    pause
    exit /b 1
)

echo [1/4] 清理旧文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec

echo [2/4] 安装依赖...
pip install pdfplumber==0.6.2 PyPDF2==2.12.1 pyinstaller==4.10 -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [3/4] 打包程序...
pyinstaller --onefile --windowed --name "发票重命名工具-Win7版" invoice_renamer.py

echo [4/4] 复制说明文档...
if exist "dist\发票重命名工具-Win7版.exe" (
    copy "发票类型说明.md" "dist\"
    echo.
    echo ========================================
    echo 打包成功！
    echo ========================================
    echo 输出文件: dist\发票重命名工具-Win7版.exe
) else (
    echo.
    echo [错误] 打包失败
)

echo.
pause
```

### 5. 在 Win7 系统上运行

将打包好的 `发票重命名工具-Win7版.exe` 复制到 Win7 系统即可运行。

---

## 依赖版本对照表

| 包名 | Win10+ 版本 | Win7 兼容版本 |
|------|-------------|---------------|
| Python | 3.9+ | **3.8.10** |
| PyInstaller | 6.x | **4.10** |
| pdfplumber | 最新 | **0.6.2** |
| PyPDF2 | 最新 | **2.12.1** |
| pdfminer.six | 自动 | **20211012** |
| charset-normalizer | 最新 | **2.0.12** |
| chardet | 最新 | **4.0.0** |

---

## 替代方案

### 方案A：使用 C# 版本（推荐）

C# 版本使用 .NET Framework，天然支持 Windows 7：

```
cd csharp
msbuild InvoiceRenamer.csproj /p:Configuration=Release
```

输出：`bin\Release\发票重命名工具.exe`

### 方案B：直接在 Win7 安装 Python 运行

在 Win7 系统上：
1. 安装 Python 3.8.10
2. 安装依赖：`pip install pdfplumber PyPDF2`
3. 直接运行：`python invoice_renamer.py`

### 方案C：使用 Nuitka 打包（实验性）

```cmd
pip install nuitka
python -m nuitka --onefile --windows-disable-console invoice_renamer.py
```

---

## Win7 运行要求

- Windows 7 SP1 (Service Pack 1)
- 安装 KB2533623 更新（通用 C 运行时）
- .NET Framework 4.5+（如果使用C#版本）

---

## 常见问题

### Q: 提示 "无法启动此程序，因为计算机中丢失 api-ms-win-crt-runtime-l1-1-0.dll"
A: 安装 Visual C++ Redistributable for Visual Studio 2015-2022
下载：https://aka.ms/vs/17/release/vc_redist.x64.exe

### Q: 提示 "应用程序无法正常启动 (0xc000007b)"
A: 安装 .NET Framework 4.8
下载：https://dotnet.microsoft.com/download/dotnet-framework/net48

### Q: Python 3.8 安装失败
A: 确保 Win7 已安装 SP1 和 KB2533623 更新
