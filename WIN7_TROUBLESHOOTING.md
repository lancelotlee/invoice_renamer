# Windows 7 运行故障排查

## 快速诊断步骤

### 1. 确认错误类型

| 错误提示 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `无法启动此程序，因为计算机中丢失 api-ms-win-crt-runtime-l1-1-0.dll` | 缺少 VC++ 运行时 | 安装 Visual C++ Redistributable |
| `应用程序无法正常启动 (0xc000007b)` | 32/64位冲突或缺少.NET | 安装 .NET Framework 4.8 |
| `找不到入口点 SetDefaultDllDirectories` | Win7 未打 SP1 补丁 | 安装 Windows 7 SP1 |
| 直接闪退无提示 | Python 版本不兼容 | 使用 Python 3.8 重新打包 |

---

## 详细解决方案

### 问题1：丢失 api-ms-win-crt-runtime-l1-1-0.dll

**原因**：Win7 缺少 Universal C Runtime (CRT)

**解决**：
1. 安装 Windows 更新：
   - KB2999226 (Universal C Runtime)
   - KB3118401 (其他更新)

2. 或安装 Visual C++ Redistributable：
   ```
   https://aka.ms/vs/17/release/vc_redist.x64.exe
   https://aka.ms/vs/17/release/vc_redist.x86.exe
   ```

### 问题2：0xc000007b 错误

**原因**：
- 32位/64位 DLL 混合
- 缺少 .NET Framework

**解决**：
1. 安装 .NET Framework 4.8
   ```
   https://dotnet.microsoft.com/download/dotnet-framework/net48
   ```

2. 使用 Dependencies 工具检查缺失的 DLL：
   ```
   https://github.com/lucasg/Dependencies
   ```

### 问题3：Python 相关错误

**如果报错包含 Python 版本信息**（如 `python39.dll` 未找到）：

说明打包时使用了 **Python 3.9+**，这是不兼容 Win7 的。

**解决**：按以下步骤重新打包

```cmd
:: 1. 卸载高版本 Python，安装 Python 3.8.10
:: 下载: https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe

:: 2. 安装 Win7 兼容依赖
pip install pdfplumber==0.6.2 PyInstaller==4.10

:: 3. 重新打包
pyinstaller --onefile --windowed --name "发票重命名工具_Win7版" invoice_renamer.py
```

---

## Win7 系统环境检查清单

在 Win7 上运行前，请确认：

- [ ] Windows 7 Service Pack 1 已安装
- [ ] .NET Framework 4.5 或更高版本已安装
- [ ] Visual C++ 2015-2022 Redistributable 已安装
- [ ] 系统盘有足够空间（至少 100MB）

### 检查系统版本

```cmd
winver
```

应显示 "Version 6.1 (Build 7601: Service Pack 1)"

---

## 替代运行方式

如果打包的exe无法运行，可以尝试：

### 方式A：安装 Python 直接运行

1. Win7 上安装 Python 3.8.10
2. 安装依赖：`pip install pdfplumber PyPDF2`
3. 运行：`python invoice_renamer.py`

### 方式B：使用 C# 版本

```cmd
cd csharp
:: 使用 MSBuild 编译（需要安装 Visual Studio Build Tools）
msbuild InvoiceRenamer.csproj /p:Configuration=Release
:: 或使用 csc 编译（Win7自带）
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe ^
    /target:winexe /out:"发票重命名工具.exe" ^
    /reference:System.dll,System.Windows.Forms.dll,System.Drawing.dll ^
    MainForm.cs MainForm.Designer.cs Program.cs
```

---

## 在 Win10 上为 Win7 打包（交叉编译）

### 方法1：使用虚拟环境

```cmd
:: 安装 Python 3.8.10 到自定义目录
:: 创建隔离环境
C:\Python38\python.exe -m venv venv-win7
venv-win7\Scripts\activate

:: 安装依赖
pip install -r requirements-win7.txt

:: 打包
pyinstaller --onefile --windowed --name "发票重命名工具_Win7版" invoice_renamer.py
```

### 方法2：使用 Docker（高级）

创建 `Dockerfile.win7`：

```dockerfile
FROM python:3.8.10-windowsservercore-ltsc2016

WORKDIR /app
COPY . /app

RUN pip install pdfplumber==0.6.2 PyInstaller==4.10
RUN pyinstaller --onefile --windowed invoice_renamer.py

CMD ["dist\invoice_renamer.exe"]
```

---

## 最小化依赖版本

如果仍然有问题，可以尝试使用更旧的稳定版本：

```txt
# requirements-win7-minimal.txt
pdfplumber==0.5.28
PyPDF2==1.26.0
PyInstaller==3.6
Pillow==7.2.0
```

这些版本在 Win7 上经过广泛测试，兼容性最好。

---

## 获取帮助

如果以上方法都无效：

1. 在 Win7 上打开命令提示符
2. 运行程序捕获错误：
   ```cmd
   发票重命名工具_Win7版.exe 2> error.log
   ```
3. 查看 `error.log` 文件内容
4. 根据错误信息搜索解决方案
