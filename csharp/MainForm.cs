using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;

namespace InvoiceRenamer
{
    public partial class MainForm : Form
    {
        private Dictionary<string, InvoiceTypeConfig> invoiceTypes;
        
        public MainForm()
        {
            InitializeComponent();
            InitializeInvoiceTypes();
        }
        
        private void InitializeInvoiceTypes()
        {
            invoiceTypes = new Dictionary<string, InvoiceTypeConfig>();
            
            invoiceTypes["增值税普通发票"] = new InvoiceTypeConfig
            {
                CodePattern = @"发票代码[：:\s]*(\d{10,12})",
                NumberPattern = @"发票号码[：:\s]*(\d{8,20})",
                CombinedPattern = @"(\d{12})[—\-](\d{8,20})",
                NoPrefixPattern = @"No[.:]?\s*(\d{8,20})"
            };
            
            invoiceTypes["增值税专用发票"] = new InvoiceTypeConfig
            {
                CodePattern = @"发票代码[：:\s]*(\d{10,12})",
                NumberPattern = @"发票号码[：:\s]*(\d{8,20})",
                CombinedPattern = @"(\d{12})[—\-](\d{8,20})",
                NoPrefixPattern = @"No[.:]?\s*(\d{8,20})"
            };
            
            invoiceTypes["电子普通发票"] = new InvoiceTypeConfig
            {
                CodePattern = @"发票代码[：:\s]*(\d{12})",
                NumberPattern = @"发票号码[：:\s]*(\d{8,20})",
                CombinedPattern = @"(\d{12})[—\-](\d{8,20})",
                NoPrefixPattern = @"No[.:]?\s*(\d{20})"
            };
            
            invoiceTypes["电子专用发票"] = new InvoiceTypeConfig
            {
                CodePattern = @"发票代码[：:\s]*(\d{12})",
                NumberPattern = @"发票号码[：:\s]*(\d{8,20})",
                CombinedPattern = @"(\d{12})[—\-](\d{8,20})",
                NoPrefixPattern = @"No[.:]?\s*(\d{20})"
            };
            
            invoiceTypes["机动车发票"] = new InvoiceTypeConfig
            {
                CodePattern = @"发票代码[：:\s]*(\d{12})",
                NumberPattern = @"发票号码[：:\s]*(\d{8})",
                CombinedPattern = @"(\d{12})[—\-](\d{8})",
                NoPrefixPattern = @"No[.:]?\s*(\d{8})"
            };
            
            cmbInvoiceType.Items.AddRange(invoiceTypes.Keys.ToArray());
            cmbInvoiceType.SelectedIndex = 0;
        }
        
        private void btnBrowseInput_Click(object sender, EventArgs e)
        {
            using (var fbd = new FolderBrowserDialog { Description = "选择包含PDF发票的目录" })
            {
                if (fbd.ShowDialog() == DialogResult.OK)
                    txtInputPath.Text = fbd.SelectedPath;
            }
        }
        
        private void btnBrowseOutput_Click(object sender, EventArgs e)
        {
            using (var fbd = new FolderBrowserDialog { Description = "选择输出目录" })
            {
                if (fbd.ShowDialog() == DialogResult.OK)
                    txtOutputPath.Text = fbd.SelectedPath;
            }
        }
        
        private void btnStart_Click(object sender, EventArgs e)
        {
            if (!ValidateInputs()) return;
            
            btnStart.Enabled = false;
            txtLog.Clear();
            progressBar.Value = 0;
            
            System.Threading.ThreadPool.QueueUserWorkItem(_ => ProcessFiles());
        }
        
        private bool ValidateInputs()
        {
            if (string.IsNullOrWhiteSpace(txtInputPath.Text) || !Directory.Exists(txtInputPath.Text))
            {
                MessageBox.Show("请输入有效的输入目录", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }
            
            if (string.IsNullOrWhiteSpace(txtOutputPath.Text))
            {
                MessageBox.Show("请输入输出目录", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }
            
            return true;
        }
        
        private void ProcessFiles()
        {
            string inputDir = txtInputPath.Text;
            string outputDir = txtOutputPath.Text;
            string invoiceType = cmbInvoiceType.SelectedItem.ToString();
            bool moveFiles = chkMoveFiles.Checked;
            bool overwrite = chkOverwrite.Checked;
            
            try
            {
                Directory.CreateDirectory(outputDir);
                
                var pdfFiles = Directory.GetFiles(inputDir, "*.pdf")
                    .Concat(Directory.GetFiles(inputDir, "*.PDF"))
                    .ToArray();
                
                if (pdfFiles.Length == 0)
                {
                    Invoke(new Action(() => MessageBox.Show("输入目录中没有PDF文件", "提示")));
                    return;
                }
                
                Log(new string('=', 50));
                Log(string.Format("开始处理，共 {0} 个PDF文件", pdfFiles.Length));
                Log(string.Format("发票类型: {0}", invoiceType));
                Log(new string('=', 50));
                Log("");
                
                int successCount = 0;
                int failCount = 0;
                
                for (int i = 0; i < pdfFiles.Length; i++)
                {
                    string pdfPath = pdfFiles[i];
                    string filename = Path.GetFileName(pdfPath);
                    
                    Invoke(new Action(() =>
                    {
                        progressBar.Value = (int)((i + 1.0) / pdfFiles.Length * 100);
                        lblStatus.Text = string.Format("正在处理: {0}", filename);
                    }));
                    
                    Log(string.Format("[{0}/{1}] {2}", i + 1, pdfFiles.Length, filename));
                    
                    try
                    {
                        string text = ExtractTextFromPdf(pdfPath);
                        
                        if (string.IsNullOrWhiteSpace(text))
                        {
                            Log("  x 无法提取文本（可能是扫描件或图片PDF）");
                            failCount++;
                            continue;
                        }
                        
                        string invoiceNo = ExtractInvoiceNumber(text, invoiceType);
                        
                        if (string.IsNullOrEmpty(invoiceNo))
                        {
                            Log("  x 无法识别发票编号");
                            Log("  --- 提取的文本内容（前500字符）---");
                            string preview = text.Length > 500 ? text.Substring(0, 500) : text;
                            Log(preview.Replace("\n", " "));
                            Log("  --- 结束 ---");
                            failCount++;
                            continue;
                        }
                        
                        string newFilename = CleanFilename(invoiceNo + ".pdf");
                        string outputPath = Path.Combine(outputDir, newFilename);
                        
                        if (File.Exists(outputPath) && !overwrite)
                        {
                            int counter = 1;
                            string name = Path.GetFileNameWithoutExtension(newFilename);
                            string ext = Path.GetExtension(newFilename);
                            while (File.Exists(outputPath))
                            {
                                newFilename = string.Format("{0}_{1}{2}", name, counter, ext);
                                outputPath = Path.Combine(outputDir, newFilename);
                                counter++;
                            }
                        }
                        
                        if (moveFiles)
                        {
                            if (overwrite && File.Exists(outputPath))
                                File.Delete(outputPath);
                            File.Move(pdfPath, outputPath);
                            Log(string.Format("  v {0} -> {1} (已移动)", filename, newFilename));
                        }
                        else
                        {
                            if (overwrite && File.Exists(outputPath))
                                File.Delete(outputPath);
                            File.Copy(pdfPath, outputPath, overwrite);
                            Log(string.Format("  v {0} -> {1} (已复制)", filename, newFilename));
                        }
                        
                        successCount++;
                    }
                    catch (Exception ex)
                    {
                        Log(string.Format("  x 处理失败: {0}", ex.Message));
                        failCount++;
                    }
                }
                
                Invoke(new Action(() =>
                {
                    progressBar.Value = 100;
                    lblStatus.Text = string.Format("处理完成: 成功 {0}, 失败 {1}", successCount, failCount);
                }));
                
                Log("");
                Log(new string('=', 50));
                Log("处理完成!");
                Log(string.Format("成功: {0} 个", successCount));
                Log(string.Format("失败: {0} 个", failCount));
                Log(new string('=', 50));
                Log("");
                
                Invoke(new Action(() =>
                    MessageBox.Show(string.Format("处理完成!\n成功: {0} 个\n失败: {1} 个", successCount, failCount), 
                        "完成", MessageBoxButtons.OK, MessageBoxIcon.Information)));
            }
            catch (Exception ex)
            {
                Invoke(new Action(() =>
                    MessageBox.Show(string.Format("处理过程中发生错误: {0}", ex.Message), 
                        "错误", MessageBoxButtons.OK, MessageBoxIcon.Error)));
            }
            finally
            {
                Invoke(new Action(() => btnStart.Enabled = true));
            }
        }
        
        private string ExtractTextFromPdf(string pdfPath)
        {
            var sb = new StringBuilder();
            
            try
            {
                byte[] bytes = File.ReadAllBytes(pdfPath);
                string content = Encoding.UTF8.GetString(bytes);
                
                // 方法1: 从stream中提取
                var textMatches = Regex.Matches(content, @"stream\s*(.*?)\s*endstream", RegexOptions.Singleline);
                foreach (Match match in textMatches)
                {
                    string stream = match.Groups[1].Value;
                    // 提取括号中的文本 (PDF文本通常以 (文本) 形式存储)
                    var parenMatches = Regex.Matches(stream, @"\(([^)]+)\)");
                    foreach (Match pm in parenMatches)
                    {
                        string txt = pm.Groups[1].Value;
                        // 过滤掉非打印字符
                        txt = Regex.Replace(txt, @"[^\u4e00-\u9fa5a-zA-Z0-9\-：:发票代码号码No.]", "");
                        if (txt.Length > 3)
                            sb.Append(txt);
                    }
                }
                
                // 方法2: 直接在整个文件中搜索模式
                sb.AppendLine();
                sb.AppendLine(content);
            }
            catch { }
            
            return sb.ToString();
        }
        
        private string ExtractInvoiceNumber(string text, string invoiceType)
        {
            var config = invoiceTypes[invoiceType];
            
            var combinedMatch = Regex.Match(text, config.CombinedPattern);
            if (combinedMatch.Success)
                return string.Format("{0}-{1}", combinedMatch.Groups[1].Value, combinedMatch.Groups[2].Value);
            
            var codeMatch = Regex.Match(text, config.CodePattern);
            var numberMatch = Regex.Match(text, config.NumberPattern);
            if (codeMatch.Success && numberMatch.Success)
                return string.Format("{0}-{1}", codeMatch.Groups[1].Value, numberMatch.Groups[1].Value);
            
            var noMatch = Regex.Match(text, config.NoPrefixPattern);
            if (noMatch.Success)
                return noMatch.Groups[1].Value;
            
            var generalMatch = Regex.Match(text, @"(\d{12})[—\-](\d{8,20})");
            if (generalMatch.Success)
                return string.Format("{0}-{1}", generalMatch.Groups[1].Value, generalMatch.Groups[2].Value);
            
            var numberOnly = Regex.Match(text, @"发票号码[：:\s]*(\d{8,20})");
            if (numberOnly.Success)
                return numberOnly.Groups[1].Value;
            
            return null;
        }
        
        private string CleanFilename(string filename)
        {
            char[] illegalChars = { '<', '>', ':', '"', '/', '\\', '|', '?', '*' };
            foreach (char c in illegalChars)
                filename = filename.Replace(c, '_');
            return filename.Trim();
        }
        
        private void Log(string message)
        {
            Invoke(new Action(() =>
            {
                txtLog.AppendText(message + Environment.NewLine);
                txtLog.ScrollToCaret();
            }));
        }
    }
    
    public class InvoiceTypeConfig
    {
        public string CodePattern { get; set; }
        public string NumberPattern { get; set; }
        public string CombinedPattern { get; set; }
        public string NoPrefixPattern { get; set; }
    }
}
