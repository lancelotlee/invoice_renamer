# Git 上传指南

## 📁 必须上传的核心文件

### 主程序（Python版本）
| 文件/目录 | 说明 | 必需 |
|-----------|------|------|
| `invoice_renamer.py` | 主程序源代码 | ✅ |
| `requirements.txt` | Python依赖列表 | ✅ |
| `README.md` | 项目说明文档 | ✅ |
| `发票类型说明.md` | 发票类型说明文档 | ✅ |

### C#备用实现（可选但建议保留）
| 文件/目录 | 说明 | 必需 |
|-----------|------|------|
| `csharp/Program.cs` | C#程序入口 | ✅ |
| `csharp/MainForm.cs` | C#主窗体逻辑 | ✅ |
| `csharp/MainForm.Designer.cs` | C#窗体设计 | ✅ |
| `csharp/InvoiceRenamer.csproj` | C#项目文件 | ✅ |
| `csharp/App.config` | C#配置文件 | ✅ |
| `csharp/README.md` | C#版本说明 | ✅ |

---

## 🚫 已排除的文件（无需上传）

### 构建生成文件
| 文件/目录 | 排除原因 |
|-----------|----------|
| `build/` | PyInstaller构建临时目录 |
| `dist/` | PyInstaller输出目录（包含exe） |
| `hooks/` | PyInstaller自动生成钩子 |
| `*.spec` | PyInstaller配置文件（可重新生成） |
| `__pycache__/` | Python字节码缓存 |
| `*.pyc` / `*.pyo` | Python编译文件 |

### 项目辅助文件
| 文件 | 排除原因 |
|------|----------|
| `build_exe.bat` | Windows批处理构建脚本 |
| `build_exe_simple.bat` | 简化版构建脚本 |
| `create_png.py` | 临时图标生成工具 |
| `test.txt` | 测试文件 |
| `BUILD_OPTIONS.md` | 构建选项文档 |
| `README_PACKAGE.md` | 打包说明文档 |
| `发票类型说明.html` | Markdown生成的HTML版本 |

### 用户数据（运行时生成）
| 文件/目录 | 排除原因 |
|-----------|----------|
| `.invoice_renamer_config.json` | 用户配置文件（在用户主目录） |
| `.invoice_renamer_logs/` | 日志文件（在用户主目录） |

---

## 📝 上传步骤

### 1. 初始化Git仓库（如果还没有）
```bash
cd invoice_renamer
git init
```

### 2. 添加.gitignore（已提供）
```bash
# .gitignore文件已在当前目录中
git add .gitignore
```

### 3. 添加核心文件
```bash
# 主程序文件
git add invoice_renamer.py
git add requirements.txt
git add README.md
git add 发票类型说明.md

# C#版本（可选）
git add csharp/

# Git上传指南
git add GIT_UPLOAD_GUIDE.md
```

### 4. 提交
```bash
git commit -m "Initial commit: 发票重命名工具 v1.0"
```

### 5. 推送到远程仓库（可选）
```bash
git remote add origin <你的仓库地址>
git push -u origin main
```

---

## 📊 文件大小对比

上传前清理后的预估大小：

| 项目 | 大小 | 说明 |
|------|------|------|
| 核心代码 | ~30 KB | Python主程序 + 配置 |
| C#代码 | ~10 KB | 备用实现 |
| 文档 | ~5 KB | README等 |
| **总计** | **~45 KB** | 非常轻量 |

未清理前（包含构建文件）：
| 项目 | 大小 | 说明 |
|------|------|------|
| build/ + dist/ | 50+ MB | PyInstaller生成的exe |
| 其他临时文件 | ~10 KB | 可忽略 |
| **总计** | **50+ MB** | 不适合Git管理 |

---

## 🔧 重新生成排除的文件

### 生成PyInstaller配置
```bash
pyi-makespec --onefile --windowed --name "InvoiceRenamer" invoice_renamer.py
```

### 构建exe
```bash
pip install pyinstaller pdfplumber
pyinstaller InvoiceRenamer.spec
```

### 生成HTML说明文档（可选）
使用Markdown转换工具将 `.md` 转为 `.html`

---

## ✅ 检查清单

上传前确认：
- [ ] `.gitignore` 已添加
- [ ] 核心代码文件已添加
- [ ] 没有包含 `build/` 目录
- [ ] 没有包含 `dist/` 目录
- [ ] 没有包含 `__pycache__/` 目录
- [ ] 没有包含 `.spec` 文件
