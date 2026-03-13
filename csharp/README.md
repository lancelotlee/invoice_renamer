# C# 发票重命名工具

## 编译步骤

### 方法一：使用 Visual Studio（推荐）

1. 打开 Visual Studio（2015或更高版本，社区版免费）
2. 选择 "文件" → "新建" → "项目" → "Windows 窗体应用(.NET Framework)"
3. 将以下文件复制到项目目录：
   - `MainForm.cs`
   - `MainForm.Designer.cs`
   - `Program.cs`
   - `App.config`
4. 在解决方案资源管理器中，右键项目 → "添加" → "现有项"，选择上述文件
5. 按 F5 编译运行，或选择 "生成" → "生成解决方案"
6. 生成的 exe 位于 `bin\Release\发票重命名工具.exe`

### 方法二：使用 MSBuild（命令行）

如果已安装 Visual Studio 或 .NET Framework SDK：

```batch
cd csharp
msbuild InvoiceRenamer.csproj /p:Configuration=Release
```

生成的 exe 位于 `bin\Release\发票重命名工具.exe`

### 方法三：使用 csc.exe（最轻量）

如果只有 .NET Framework（Windows自带）：

```batch
cd csharp

# 找到 csc.exe 路径（根据你的.NET版本调整）
set CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe

# 编译
%CSC% /target:winexe /out:"发票重命名工具.exe" /reference:System.dll,System.Windows.Forms.dll,System.Drawing.dll MainForm.cs MainForm.Designer.cs Program.cs
```

## 系统要求

- Windows 7 或更高版本
- .NET Framework 4.5 或更高版本（Windows 8.1/10/11 自带）

## 注意事项

当前版本使用简单的文本提取方式，对于纯图片的扫描件PDF可能无法识别。
如需OCR功能，需要集成第三方PDF解析库（如iTextSharp或PdfPig）。
