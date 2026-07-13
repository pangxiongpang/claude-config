# 故障排除指南

## 常见问题及解决方案

### 1. 安装问题

#### 问题：PyMuPDF未安装
**错误信息**：
```
{"error": "PyMuPDF not installed. Run: pip install PyMuPDF", "error_type": "dependency"}
```

**解决方案**：
```bash
pip install PyMuPDF
```

如果使用conda：
```bash
conda install -c conda-forge pymupdf
```

#### 问题：Python版本不兼容
**错误信息**：
```
{"check": "Python version", "required": "3.7+", "found": "3.6.x", "ok": false}
```

**解决方案**：
- 升级Python到3.7或更高版本
- 使用pyenv管理Python版本

### 2. 文件问题

#### 问题：文件不存在
**错误信息**：
```
{"error": "Input file not found: /path/to/file.pdf", "error_type": "validation"}
```

**解决方案**：
- 检查文件路径是否正确
- 使用绝对路径
- 确认文件存在

#### 问题：PDF格式错误
**错误信息**：
```
{"error": "Invalid PDF structure", "error_type": "runtime"}
```

**解决方案**：
- 确认文件是有效的PDF
- 尝试用PDF阅读器打开文件
- 可能是损坏的PDF文件

#### 问题：PDF是扫描件
**现象**：检测不到水印
**原因**：扫描件中的水印是页面内容的一部分，不是独立的图片对象

**解决方案**：
- 使用OCR工具处理扫描件
- 使用图像处理工具去除水印

### 3. 水印检测问题

#### 问题：检测不到水印
**可能原因**：
1. 水印不是图片形式（可能是文本或矢量图形）
2. 水印尺寸超出检测阈值
3. 水印位置不在预设区域

**解决方案**：
```bash
# 调整检测参数
python scripts/remove_watermark.py --max-width 500 --max-height 200 --min-x 300 --min-y 600 input.pdf
```

#### 问题：误删页面内容
**原因**：页面内容图片被误判为水印

**解决方案**：
- 减小检测范围
- 使用更严格的尺寸和位置阈值
- 手动检查PDF结构

### 4. 处理问题

#### 问题：处理速度慢
**原因**：PDF文件过大或页数过多

**解决方案**：
- 处理单页或少量页面
- 使用更快的存储设备
- 关闭其他程序释放内存

#### 问题：内存不足
**错误信息**：
```
MemoryError: Unable to allocate array
```

**解决方案**：
- 处理较小的PDF文件
- 分批处理
- 增加系统内存

#### 问题：输出文件损坏
**原因**：保存过程中出现错误

**解决方案**：
- 检查磁盘空间
- 确保有写入权限
- 尝试保存到不同位置

### 5. 批量处理问题

#### 问题：部分文件处理失败
**原因**：某些文件格式特殊或损坏

**解决方案**：
- 检查失败文件的具体错误
- 单独处理有问题的文件
- 跳过损坏的文件

#### 问题：输出文件名冲突
**原因**：多个输入文件生成相同的输出文件名

**解决方案**：
- 使用不同的输出目录
- 指定唯一的输出文件名

### 6. 系统问题

#### 问题：权限不足
**错误信息**：
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**：
- 使用管理员权限运行
- 检查文件权限
- 选择有写入权限的目录

#### 问题：路径过长（Windows）
**错误信息**：
```
OSError: [Errno 2] No such file or directory
```

**解决方案**：
- 使用较短的文件路径
- 启用Windows长路径支持
- 使用相对路径

## 调试技巧

### 1. 检查PDF结构
```python
import fitz

doc = fitz.open("input.pdf")
for page_num in range(min(3, len(doc))):  # 只检查前3页
    page = doc.load_page(page_num)
    images = page.get_images(full=True)
    print(f"Page {page_num + 1}: {len(images)} images")
    for img in images:
        print(f"  - xref: {img[0]}, size: {img[2]}x{img[3]}")
doc.close()
```

### 2. 测试水印检测
```python
from scripts.remove_watermark import PDFWatermarkRemover

remover = PDFWatermarkRemover("input.pdf")
result = remover.detect_only()
print(result)
```

### 3. 逐步处理
1. 先用`--detect-only`模式检查
2. 确认水印检测正确
3. 再执行删除操作

## 获取帮助

如果以上方法都无法解决问题：

1. 检查错误信息中的具体错误类型
2. 查看PyMuPDF官方文档
3. 在GitHub上搜索类似问题
4. 提交详细的错误报告，包括：
   - 操作系统和版本
   - Python版本
   - PyMuPDF版本
   - 完整的错误信息
   - PDF文件的基本信息