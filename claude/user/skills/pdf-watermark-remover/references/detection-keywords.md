# PDF Watermark Remover - 触发关键词

## 触发描述

```yaml
description: >-
  Remove watermarks from PDF files by detecting and deleting overlay images.
  Activates when users ask to remove watermarks, clean PDFs, or eliminate
  watermark overlays from documents. Triggers on phrases like remove watermark
  from PDF, delete watermark images, clean PDF document, eliminate watermark
  overlay, batch remove watermarks, detect watermarks in PDF. Supports
  automatic watermark detection based on image size, position, and color
  characteristics. Uses PyMuPDF to analyze PDF structure and remove watermark
  images while preserving page content. Handles multi-page PDFs with consistent
  watermark placement.
```

## 关键词分类

### 实体关键词
- PDF, 文档, 文件, 水印, watermark, document, file
- 图片, image, overlay, 叠加层

### 动作关键词
- 去除, 删除, 清除, remove, delete, clean, eliminate
- 检测, 识别, detect, identify, find
- 批量处理, batch process, 批量去除

### 位置关键词
- 右下角, bottom-right, 左下角, bottom-left
- 右上角, top-right, 左上角, top-left
- 角落, corner, 边缘, edge

### 特征关键词
- 浅色, light color, 半透明, semi-transparent
- 小图片, small image, 叠加, overlay

### 技术关键词
- PyMuPDF, fitz, PDF处理, PDF manipulation
- 图片删除, image deletion, 结构分析, structure analysis

## 触发示例

### 正面示例（应该触发）
1. "去除这个PDF文件的水印"
2. "remove watermark from this PDF"
3. "批量处理这些PDF，去除水印"
4. "检测PDF中是否有水印"
5. "删除右下角的水印图片"
6. "clean this PDF document"
7. "eliminate watermark overlay"
8. "smart watermark detection"

### 反面示例（不应该触发）
1. "编辑PDF文本内容" - 文本编辑
2. "合并多个PDF文件" - PDF合并
3. "压缩PDF文件大小" - PDF压缩
4. "转换PDF为图片" - PDF转换
5. "添加水印到PDF" - 添加水印（相反操作）

## 检测逻辑

1. **主触发条件**：用户明确要求去除/删除/清除水印
2. **次要触发条件**：用户提到PDF和水印相关词汇
3. **排除条件**：用户要求添加水印或进行其他PDF操作

## 置信度评分

- 高置信度（0.9-1.0）：明确要求去除PDF水印
- 中置信度（0.7-0.9）：提到PDF和水印，但意图不明确
- 低置信度（0.5-0.7）：仅提到水印或PDF其中之一
- 不触发（<0.5）：无水印相关词汇