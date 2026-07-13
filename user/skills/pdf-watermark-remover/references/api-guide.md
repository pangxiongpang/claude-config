# PyMuPDF API 参考指南

## 概述

PyMuPDF（也称为fitz）是一个强大的PDF处理库，支持PDF的读取、编辑和写入。本skill使用PyMuPDF来分析PDF结构并删除水印图片。

## 安装

```bash
pip install PyMuPDF
```

## 核心API

### 打开PDF文件

```python
import fitz

# 打开PDF文件
doc = fitz.open("input.pdf")

# 获取页数
page_count = len(doc)

# 获取页面
page = doc.load_page(0)  # 第一页（从0开始）
```

### 获取页面中的图片

```python
# 获取页面中的所有图片
image_list = page.get_images(full=True)

# image_list格式：
# [(xref, smask, width, height, bpc, colorspace, alt. colorspace, name, filter, referencer), ...]

for img in image_list:
    xref = img[0]  # 图片的交叉引用号
    width = img[2]  # 宽度
    height = img[3]  # 高度
```

### 获取图片位置

```python
# 获取图片在页面中的位置
img_rects = page.get_image_rects(xref)

if img_rects:
    rect = img_rects[0]
    print(f"位置: ({rect.x0}, {rect.y0}) - ({rect.x1}, {rect.y1})")
    print(f"尺寸: {rect.width} x {rect.height}")
```

### 提取图片数据

```python
# 提取图片详细信息
base_image = doc.extract_image(xref)

# base_image格式：
# {
#   "width": 宽度,
#   "height": 高度,
#   "ext": 扩展名 (如 "jpeg", "png"),
#   "image": 图片数据 (bytes),
#   "colorspace": 颜色空间,
#   "xref": 交叉引用号
# }
```

### 删除图片

```python
# 删除页面中的图片
page.delete_image(xref)
```

### 保存PDF

```python
# 保存修改后的PDF
doc.save("output.pdf")
doc.close()
```

## 高级用法

### 获取页面尺寸

```python
# 获取页面矩形
page_rect = page.rect

# page_rect格式：
# (x0, y0, x1, y1) = (左边, 上边, 右边, 下边)
```

### 遍历所有页面

```python
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    # 处理页面...
```

### 获取PDF元数据

```python
metadata = doc.metadata
print(f"标题: {metadata.get('title', '')}")
print(f"作者: {metadata.get('author', '')}")
```

## 常见问题

### 问题1：图片删除失败

**原因**：图片被其他对象引用
**解决方案**：确保图片没有被页面内容引用

### 问题2：文件损坏

**原因**：删除图片后PDF结构不完整
**解决方案**：使用doc.save()保存时检查错误

### 问题3：编码问题

**原因**：PDF使用特殊编码
**解决方案**：使用fitz.open()时指定编码参数

## 性能优化

1. **批量处理**：一次打开PDF，处理所有页面后再关闭
2. **内存管理**：及时关闭文档释放内存
3. **缓存**：对于重复处理，缓存PDF对象

## 参考资源

- PyMuPDF官方文档: https://pymupdf.readthedocs.io/
- GitHub仓库: https://github.com/pymupdf/PyMuPDF
- 示例代码: https://github.com/pymupdf/PyMuPDF/tree/master/recipes