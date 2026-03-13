# 发票重命名工具

## 功能说明

将PDF发票文件按发票编号重命名，支持多种发票类型。

## 打包步骤（Windows）

### 1. 安装Python和依赖

```bash
# 安装依赖
pip install pdfplumber pyinstaller
```

### 2. 打包成exe

```bash
# 进入项目目录
cd invoice_renamer

# 打包（单文件模式）
pyinstaller --onefile --windowed --name "发票重命名工具" invoice_renamer.py

# 或者打包（包含依赖，启动更快）
pyinstaller --onedir --windowed --name "发票重命名工具" invoice_renamer.py
```

### 3. 找到生成的exe

打包完成后，exe文件位于 `dist/发票重命名工具.exe`

## 使用方法

1. 运行 `发票重命名工具.exe`
2. 选择发票类型（普通发票/专用发票/电子发票等）
3. 选择输入目录（包含PDF发票的文件夹）
4. 选择输出目录（重命名后的文件保存位置）
5. 点击"开始处理"

## 支持的发票类型

- 增值税普通发票
- 增值税专用发票
- 电子普通发票
- 电子专用发票
- 机动车发票

## 注意事项

- 扫描版PDF（图片格式）可能无法识别，需要OCR功能
- 程序会自动处理重名文件（添加序号后缀）
- 支持复制或移动文件两种模式
