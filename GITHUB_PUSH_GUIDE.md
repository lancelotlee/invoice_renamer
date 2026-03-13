# GitHub 推送指南 - Windows环境

## 问题原因
`127.0.0.1:5435` 是 Git Credential Manager (GCM) 的 OAuth 回调地址。
当 GCM 尝试打开浏览器进行认证但失败时，会出现此问题。

## 解决方案A：使用 Personal Access Token（推荐）

### 步骤1：在GitHub生成Token
1. 访问 https://github.com/settings/tokens/new
2. 输入Token名称（如：InvoiceRenamer）
3. 选择有效期（建议90天）
4. 勾选权限：
   - ✅ `repo` （完全控制仓库）
5. 点击 **Generate token**
6. **立即复制生成的Token**（只显示一次）

### 步骤2：配置Git使用Token
```bash
# 方法1：直接嵌入URL（临时）
git remote set-url origin https://<TOKEN>@github.com/lancelotlee/invoice_renamer.git

# 方法2：使用凭证管理器存储（推荐）
git config --global credential.helper manager
git push origin master
# 提示输入用户名时输入你的GitHub用户名
# 提示输入密码时粘贴Token（不是GitHub密码）
```

### 步骤3：推送代码
```bash
cd F:\PythonWorkspeace\invoice_renamer
git push -u origin master
```

---

## 解决方案B：使用SSH密钥（长期有效）

### 步骤1：生成SSH密钥
```bash
# 打开PowerShell或Git Bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# 连续按三次回车，使用默认路径
```

### 步骤2：添加公钥到GitHub
```bash
# 查看公钥内容
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容
```
1. 访问 https://github.com/settings/keys
2. 点击 **New SSH key**
3. 粘贴公钥内容，保存

### 步骤3：修改远程地址为SSH
```bash
git remote set-url origin git@github.com:lancelotlee/invoice_renamer.git
```

### 步骤4：推送
```bash
git push -u origin master
```

---

## 当前已完成的配置

以下命令已在你的环境中执行：

```bash
# 配置Git凭证管理器
git config --global credential.helper manager

# 禁用浏览器弹窗，使用命令行输入
git config --global credential.modalPrompt false
git config --global credential.githubAuthModes basic

# 设置用户信息
git config --global user.email "user@example.com"
git config --global user.name "User"
```

---

## 快速测试命令

```powershell
# 测试1：检查配置
git config --global --list | Select-String -Pattern "credential"

# 测试2：检查远程地址
git remote -v

# 测试3：推送（会提示输入用户名和密码/Token）
git push -u origin master
```

---

## 常见问题

### Q: 推送时提示 "fatal: unable to access"
A: 检查网络连接，或尝试：
```bash
git config --global http.sslVerify false  # 临时禁用SSL验证（不推荐长期使用）
```

### Q: 提示 "Permission denied"
A: 检查Token权限是否勾选了 `repo`，或检查仓库是否拥有写入权限

### Q: 提示 "rejected: non-fast-forward"
A: 远程仓库有更新，先执行：
```bash
git pull origin master --rebase
```

---

## 推荐的完整操作流程

```powershell
# 1. 进入项目目录
cd F:\PythonWorkspeace\invoice_renamer

# 2. 确保所有文件已添加
git add -A

# 3. 提交
git commit -m "Initial commit: 发票重命名工具 v1.0

- 支持数电票和传统发票识别
- Python + C# 双版本实现
- 自动日志记录功能
- 支持目录批量处理和文件多选"

# 4. 推送（选择以下一种方式）

# 方式A：使用Token（首次会提示输入用户名和Token）
git push -u origin master

# 方式B：如果配置了SSH
git push -u origin master
```
