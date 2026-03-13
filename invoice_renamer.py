import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import json
from datetime import datetime

# 导入PDF处理库
import pdfplumber
PDFPLUMBER_AVAILABLE = True

# 可选的备用库
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class InvoiceRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("发票重命名工具 v1.0")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # 配置文件路径
        self.config_file = Path.home() / '.invoice_renamer_config.json'
        self.config = self.load_config()
        
        # 日志文件路径 - 按日期生成
        self.log_dir = Path.home() / '.invoice_renamer_logs'
        self.log_dir.mkdir(exist_ok=True)
        self.current_log_file = self.log_dir / f"invoice_renamer_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        # 发票类型配置
        self.invoice_types = {
            "数电票（仅发票号码）": {
                # 全面数字化的电子发票
                # 格式：仅20位发票号码，无发票代码
                "code_pattern": r'发票号码[：:\s]*(\d{20})',
                "number_pattern": r'发票号码[：:\s]*(\d{20})',
                "combined_pattern": r'(\d{20})',
                "no_prefix_pattern": r'\b(\d{20})\b',
            },
            "传统票（代码+号码）": {
                # 纸质发票、电子发票（PDF/OFD/XML）
                # 格式：发票代码(10-12位) + 发票号码(8位)
                "code_pattern": r'发票代码[\s:：]*([\d]{10,12})',
                "number_pattern": r'发票号码[\s:：]*([\d]{8})',
                "combined_pattern": r'(\d{12})[—\-](\d{8})',
                "no_prefix_pattern": r'No[.:]?\s*(\d{8,20})',
            },
        }
        
        self.setup_ui()
        self.load_paths_to_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置grid权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 发票类型选择
        ttk.Label(main_frame, text="发票类型:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.invoice_type_var = tk.StringVar(value="数电票（仅发票号码）")
        self.invoice_type_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.invoice_type_var,
            values=list(self.invoice_types.keys()),
            state="readonly",
            width=30
        )
        self.invoice_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 输入模式选择（目录/文件）
        ttk.Label(main_frame, text="输入模式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.input_mode_var = tk.StringVar(value="directory")
        ttk.Radiobutton(mode_frame, text="选择目录", variable=self.input_mode_var, 
                       value="directory", command=self.on_input_mode_change).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="选择PDF文件", variable=self.input_mode_var,
                       value="files", command=self.on_input_mode_change).pack(side=tk.LEFT)
        
        # 输入路径
        ttk.Label(main_frame, text="输入路径:").grid(row=2, column=0, sticky=tk.W, pady=5)
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        self.input_path_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_path_var)
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_btn = ttk.Button(input_frame, text="浏览", command=self.browse_input)
        self.browse_btn.grid(row=0, column=1)
        
        # 输出目录
        ttk.Label(main_frame, text="输出目录:").grid(row=3, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="浏览", command=self.browse_output).grid(row=0, column=1)
        
        # 选项
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="5")
        options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.move_files_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="移动文件（而非复制）", variable=self.move_files_var).pack(side=tk.LEFT, padx=5)
        
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="覆盖已存在文件", variable=self.overwrite_var).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 开始按钮
        self.start_btn = ttk.Button(main_frame, text="开始处理", command=self.start_processing)
        self.start_btn.grid(row=6, column=0, columnspan=2, pady=10)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 作者信息
        author_label = ttk.Label(main_frame, text="Author: LiSongling", foreground="gray", font=("Microsoft YaHei", 9))
        author_label.grid(row=9, column=0, columnspan=2, sticky=tk.E, pady=(2, 0))
        
        # 存储选中的PDF文件列表
        self.selected_pdf_files = []
    
    def check_dependencies(self):
        """检查依赖库是否安装"""
        # pdfplumber 是必需的，已在顶部导入
        pass
    
    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_paths_to_ui(self):
        """将保存的路径加载到界面"""
        if 'last_input_dir' in self.config:
            self.input_path_var.set(self.config['last_input_dir'])
        if 'last_output_dir' in self.config:
            self.output_path_var.set(self.config['last_output_dir'])
        # 加载上次使用的发票类型
        if 'last_invoice_type' in self.config:
            saved_type = self.config['last_invoice_type']
            if saved_type in self.invoice_types:
                self.invoice_type_var.set(saved_type)
    
    def on_input_mode_change(self):
        """输入模式改变时的处理"""
        self.input_path_var.set("")
        self.selected_pdf_files = []
    
    def browse_input(self):
        """选择输入 - 根据模式选择目录或PDF文件"""
        mode = self.input_mode_var.get()
        
        if mode == "directory":
            # 目录模式
            current_input = self.input_path_var.get().strip()
            initial_dir = current_input if current_input and os.path.isdir(current_input) else self.config.get('last_input_dir', '')
            path = filedialog.askdirectory(
                title="选择包含PDF发票的目录",
                initialdir=initial_dir if initial_dir and os.path.isdir(initial_dir) else None
            )
            if path:
                self.input_path_var.set(path)
                self.config['last_input_dir'] = path
                self.save_config()
        else:
            # 文件模式 - 选择PDF文件
            current_input = self.input_path_var.get().strip()
            initial_dir = os.path.dirname(current_input) if current_input and os.path.exists(current_input) else self.config.get('last_input_dir', '')
            
            filetypes = [("PDF文件", "*.pdf"), ("所有文件", "*.*")]
            files = filedialog.askopenfilenames(
                title="选择PDF发票文件（可多选）",
                initialdir=initial_dir if initial_dir and os.path.isdir(initial_dir) else None,
                filetypes=filetypes
            )
            if files:
                self.selected_pdf_files = list(files)
                # 显示选中的文件数量和第一个文件路径
                if len(files) == 1:
                    self.input_path_var.set(files[0])
                else:
                    self.input_path_var.set(f"已选择 {len(files)} 个PDF文件")
                # 保存目录到配置
                first_file_dir = os.path.dirname(files[0])
                self.config['last_input_dir'] = first_file_dir
                self.save_config()
    
    def browse_output(self):
        """选择输出目录"""
        # 优先使用界面当前值，否则使用配置保存的值
        current_output = self.output_path_var.get().strip()
        initial_dir = current_output if current_output and os.path.isdir(current_output) else self.config.get('last_output_dir', '')
        path = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=initial_dir if initial_dir and os.path.isdir(initial_dir) else None
        )
        if path:
            self.output_path_var.set(path)
            self.config['last_output_dir'] = path
            self.save_config()
    
    def log(self, message):
        """添加日志 - 同时输出到界面和文件"""
        # 添加到界面
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # 写入到日志文件（追加模式）
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            # 如果写入日志失败，只在控制台输出（不干扰用户界面）
            print(f"写入日志文件失败: {e}")
    
    def extract_text_from_pdf(self, pdf_path):
        """从PDF中提取文本"""
        text = ""
        
        # 优先使用pdfplumber
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages[:3]:  # 读取前3页
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
            except Exception as e:
                self.log(f"  pdfplumber读取失败: {e}")
        
        # 备用：使用PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages[:3]:
                        text += page.extract_text() or ""
                return text
            except Exception as e:
                self.log(f"  PyPDF2读取失败: {e}")
        
        return text
    
    def is_likely_invoice(self, text):
        """检查文本是否包含发票相关关键词，用于验证是否是真正的发票"""
        invoice_keywords = [
            '发票', 'invoice', '发票代码', '发票号码', '电子发票',
            '增值税', '普通发票', '专用发票', '数电票', '全电发票'
        ]
        text_lower = text.lower()
        return any(keyword in text for keyword in invoice_keywords)
    
    def extract_invoice_number(self, text, invoice_type):
        """根据发票类型提取发票编号"""
        patterns = self.invoice_types.get(invoice_type, self.invoice_types["数电票（仅发票号码）"])
        
        # 首先验证是否是发票文档
        is_invoice_doc = self.is_likely_invoice(text)
        
        # 如果用户选择了数电票，但PDF里有传统票格式（发票代码+发票号码），优先使用传统票逻辑
        if invoice_type == "数电票（仅发票号码）":
            # 检查是否有传统票的特征（发票代码+发票号码）
            traditional_patterns = self.invoice_types["传统票（代码+号码）"]
            code_match = re.search(traditional_patterns["code_pattern"], text)
            number_match = re.search(traditional_patterns["number_pattern"], text)
            if code_match and number_match:
                # 发现传统票格式，使用传统票逻辑
                if code_match.group(1) == number_match.group(1):
                    return number_match.group(1)
                return f"{code_match.group(1)}{number_match.group(1)}"
        
        # 如果用户选择了传统票，但PDF里没有代码只有20位号码（数电票格式），使用数电票逻辑
        if invoice_type == "传统票（代码+号码）":
            # 检查是否有数电票的特征（20位发票号码，没有发票代码）
            digital_patterns = self.invoice_types["数电票（仅发票号码）"]
            # 先尝试匹配传统票格式
            code_match = re.search(patterns["code_pattern"], text)
            if not code_match:
                # 没有代码，尝试匹配数电票的20位号码
                number_match = re.search(digital_patterns["number_pattern"], text)
                if number_match:
                    return number_match.group(1)
        
        # 尝试组合格式（代码-号码）
        # 传统票：直接尝试匹配代码-号码格式
        # 数电票：只有在确认是发票文档时才尝试匹配20位数字
        if invoice_type == "传统票（代码+号码）" or is_invoice_doc:
            combined_match = re.search(patterns["combined_pattern"], text)
            if combined_match:
                # 如果只有一个捕获组（如数电票只有号码），直接返回
                if len(combined_match.groups()) == 1:
                    return combined_match.group(1)
                # 纯数字无分隔符
                return f"{combined_match.group(1)}{combined_match.group(2)}"
        
        # 尝试分别提取代码和号码（这些模式都有"发票"前缀，不需要额外检查）
        code_match = re.search(patterns["code_pattern"], text)
        number_match = re.search(patterns["number_pattern"], text)
        
        if code_match and number_match:
            # 如果代码和号码相同（只有号码的情况），只返回号码
            if code_match.group(1) == number_match.group(1):
                return number_match.group(1)
            # 纯数字无分隔符
            return f"{code_match.group(1)}{number_match.group(1)}"
        
        # 只有号码的情况（如数电票）- 这些模式都有"发票"前缀
        if number_match:
            return number_match.group(1)
        
        # 尝试No.前缀格式（只有在确认是发票文档时才尝试）
        if is_invoice_doc:
            no_match = re.search(patterns["no_prefix_pattern"], text)
            if no_match:
                return no_match.group(1)
        
        # 通用匹配：查找12位数字-8位数字格式（传统票格式，不需要发票关键词）
        general_match = re.search(r'(\d{12})[—\-](\d{8})', text)
        if general_match:
            # 纯数字无分隔符
            return f"{general_match.group(1)}{general_match.group(2)}"
        
        # 查找发票号码（8-20位数字，需要明确的发票关键词前缀）
        number_only = re.search(r'发票号码[：:\s]*(\d{8,20})', text)
        if number_only:
            return number_only.group(1)
        
        # 最后尝试：直接查找20位数字（数电票格式）
        # 但只有在确认是发票文档时才匹配，避免误识别报告编号等
        if is_invoice_doc:
            digital_match = re.search(r'\b(\d{20})\b', text)
            if digital_match:
                return digital_match.group(1)
        
        return None
    
    def clean_filename(self, filename):
        """清理文件名，移除非法字符"""
        # Windows非法字符: < > : " / \ | ? *
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    def process_files(self):
        """处理文件的主逻辑"""
        input_path = self.input_path_var.get().strip()
        output_dir = self.output_path_var.get().strip()
        invoice_type = self.invoice_type_var.get()
        move_files = self.move_files_var.get()
        overwrite = self.overwrite_var.get()
        input_mode = self.input_mode_var.get()
        
        # 保存当前发票类型到配置
        self.config['last_invoice_type'] = invoice_type
        self.save_config()
        
        # 验证输出目录
        if not output_dir:
            messagebox.showerror("错误", "请输入输出目录")
            self.start_btn.config(state=tk.NORMAL)
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 根据输入模式获取PDF文件列表
        pdf_files = []
        input_dir = ""
        
        if input_mode == "directory":
            # 目录模式
            if not input_path or not os.path.isdir(input_path):
                messagebox.showerror("错误", "请输入有效的输入目录")
                self.start_btn.config(state=tk.NORMAL)
                return
            input_dir = input_path
            pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        else:
            # 文件模式
            if not self.selected_pdf_files:
                messagebox.showerror("错误", "请选择PDF文件")
                self.start_btn.config(state=tk.NORMAL)
                return
            # 使用选中的文件列表（存储完整路径）
            pdf_files = self.selected_pdf_files  # 完整路径列表
            # 从第一个文件获取输入目录（用于移动模式）
            input_dir = os.path.dirname(self.selected_pdf_files[0]) if move_files else ""
        
        if not pdf_files:
            messagebox.showinfo("提示", "输入目录中没有PDF文件")
            self.start_btn.config(state=tk.NORMAL)
            return
        
        self.log(f"\n{'='*50}")
        self.log(f"开始处理，共 {len(pdf_files)} 个PDF文件")
        # 根据发票类型显示格式说明
        if "数电票" in invoice_type:
            self.log(f"发票类型: {invoice_type} → 格式: 20位发票号码")
        else:
            self.log(f"发票类型: {invoice_type} → 格式: 12位代码+8位号码（纯数字）")
        self.log(f"{'='*50}\n")
        
        success_count = 0
        fail_count = 0
        
        for i, pdf_path in enumerate(pdf_files):
            filename = os.path.basename(pdf_path)
            self.progress_var.set((i + 1) / len(pdf_files) * 100)
            self.status_var.set(f"正在处理: {filename}")
            
            self.log(f"[{i+1}/{len(pdf_files)}] {filename}")
            
            try:
                # 提取文本
                text = self.extract_text_from_pdf(pdf_path)
                
                if not text.strip():
                    self.log(f"  ✗ 无法提取文本（可能是扫描件或图片PDF）")
                    fail_count += 1
                    continue
                
                # 提取发票编号
                invoice_no = self.extract_invoice_number(text, invoice_type)
                
                if not invoice_no:
                    self.log(f"  ✗ 无法识别发票编号")
                    fail_count += 1
                    continue
                
                # 生成新文件名
                new_filename = self.clean_filename(f"{invoice_no}.pdf")
                output_path = os.path.join(output_dir, new_filename)
                
                # 处理重名
                if os.path.exists(output_path) and not overwrite:
                    counter = 1
                    name, ext = os.path.splitext(new_filename)
                    while os.path.exists(output_path):
                        new_filename = f"{name}_{counter}{ext}"
                        output_path = os.path.join(output_dir, new_filename)
                        counter += 1
                
                # 复制或移动文件
                if move_files:
                    if overwrite and os.path.exists(output_path):
                        os.remove(output_path)
                    shutil.move(pdf_path, output_path)
                    self.log(f"  ✓ {filename} → {new_filename} (已移动)")
                else:
                    if overwrite and os.path.exists(output_path):
                        os.remove(output_path)
                    shutil.copy2(pdf_path, output_path)
                    self.log(f"  ✓ {filename} → {new_filename} (已复制)")
                
                # 文件模式下，如果是移动操作，需要从列表中更新路径（虽然实际上已经移动了）
                if move_files and input_mode == "files":
                    self.selected_pdf_files[i] = output_path
                
                success_count += 1
                
            except Exception as e:
                self.log(f"  ✗ 处理失败: {str(e)}")
                fail_count += 1
        
        self.progress_var.set(100)
        self.status_var.set(f"处理完成: 成功 {success_count}, 失败 {fail_count}")
        self.log(f"\n{'='*50}")
        self.log(f"处理完成!")
        self.log(f"成功: {success_count} 个")
        self.log(f"失败: {fail_count} 个")
        self.log(f"{'='*50}\n")
        
        messagebox.showinfo("完成", f"处理完成!\n成功: {success_count} 个\n失败: {fail_count} 个")
        self.start_btn.config(state=tk.NORMAL)
    
    def start_processing(self):
        """开始处理（在后台线程中运行）"""
        self.start_btn.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()


def main():
    root = tk.Tk()
    app = InvoiceRenamerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
