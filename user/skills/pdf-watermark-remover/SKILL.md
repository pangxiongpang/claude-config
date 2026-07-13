---
name: pdf-watermark-remover
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
license: MIT
metadata:
  author: Claude Code
  version: 1.0.0
  created: 2026-05-25
  last_reviewed: 2026-05-25
  review_interval_days: 90
  dependencies:
    - url: https://pypi.org/project/PyMuPDF/
      name: PyMuPDF
      type: library
activation: /pdf-watermark-remover
provenance:
  maintainer: Claude Code
  version: 1.0.0
  created: 2026-05-25
---

# /pdf-watermark-remover — PDF Watermark Removal Tool

You are an expert PDF processing specialist. Your job is to remove watermarks from PDF files by analyzing the PDF structure, detecting overlay images that serve as watermarks, and deleting them while preserving all page content.

## Trigger

User invokes `/pdf-watermark-remover` followed by their input:

```
/pdf-watermark-remover Remove the watermark from document.pdf
/pdf-watermark-remover Clean this PDF - remove all watermarks
/pdf-watermark-remover Batch process these PDFs and remove watermarks
```

The user can also activate naturally without the prefix:

```
Remove watermark from this PDF
Delete the watermark images from this document
Clean this PDF - it has watermarks
Batch remove watermarks from multiple PDFs
Detect watermarks in this PDF
```

## When to Use This Skill

This skill activates when users ask to:
- Remove watermarks from PDF files
- Delete watermark images or overlays
- Clean PDF documents by removing watermarks
- Batch process multiple PDFs for watermark removal
- Detect and identify watermarks in PDFs

**Does NOT activate for:**
- Adding watermarks to PDFs
- Editing PDF text content
- Merging or splitting PDFs
- Converting PDF formats
- Compressing PDF files

## How It Works

The skill uses a three-step process:

### Step 1: PDF Structure Analysis
- Opens the PDF using PyMuPDF (fitz)
- Analyzes each page for embedded images
- Identifies potential watermarks based on characteristics

### Step 2: Watermark Detection
Watermarks are identified by these characteristics:
- **Size**: Typically smaller than page content (width < 300px, height < 100px)
- **Position**: Usually in corners (x > 400, y > 700 for bottom-right)
- **Color**: Often light-colored or semi-transparent
- **Consistency**: Same watermark across multiple pages

### Step 3: Watermark Removal
- Deletes the watermark image objects from the PDF
- Preserves all page content and formatting
- Maintains PDF structure and metadata

## Available Scripts

### `scripts/remove_watermark.py`
Main script for watermark removal. Supports:
- Single file processing
- Batch processing
- Watermark detection only mode
- Custom watermark region specification

**Usage:**
```bash
python scripts/remove_watermark.py input.pdf output.pdf
python scripts/remove_watermark.py --detect-only input.pdf
python scripts/remove_watermark.py --batch *.pdf
```

## Available Analyses

### Watermark Detection
Identifies watermarks in PDF files based on:
- Image size analysis
- Position detection
- Color characteristics
- Cross-page consistency

### Watermark Removal
Removes detected watermarks using:
- Direct image deletion
- Structure preservation
- Quality maintenance

## Error Handling

The skill handles these common errors:
- **File not found**: Returns clear error message with file path
- **Invalid PDF**: Reports PDF format issues
- **No watermarks found**: Informs user and suggests manual inspection
- **Removal failure**: Reports specific failure reason

## Keywords for Detection

**Entities**: PDF, document, file, watermark, image, overlay
**Actions**: remove, delete, clean, eliminate, detect, identify, batch
**Positions**: bottom-right, corner, edge, overlay
**Characteristics**: light-colored, semi-transparent, small image

**Activation examples:**
- "Remove the watermark from this PDF"
- "Delete watermark images from document.pdf"
- "Batch remove watermarks from multiple PDFs"
- "Detect if this PDF has watermarks"

**Does NOT activate for:**
- "Add watermark to this PDF"
- "Edit PDF text"
- "Merge PDF files"
- "Convert PDF to images"

## Usage Examples

### Example 1: Basic Watermark Removal
**User**: "Remove the watermark from document.pdf"
**Flow**: 
1. Analyzes PDF structure
2. Detects watermark images
3. Deletes watermarks
4. Saves clean PDF
**Output**: "Successfully removed 16 watermarks from document.pdf. Saved to document_clean.pdf"

### Example 2: Batch Processing
**User**: "Clean all these PDFs - remove watermarks"
**Flow**:
1. Processes each PDF in sequence
2. Detects and removes watermarks from each
3. Saves each with "_clean" suffix
**Output**: "Processed 5 PDFs, removed watermarks from all files"

### Example 3: Watermark Detection
**User**: "Does this PDF have watermarks?"
**Flow**:
1. Analyzes PDF structure
2. Identifies potential watermarks
3. Reports findings
**Output**: "Found 1 watermark on each of 16 pages. Watermark is 196x66 pixels located at bottom-right corner"

## Prerequisites

- Python 3.7+
- PyMuPDF (fitz) library
- No API keys required

Install dependencies:
```bash
pip install PyMuPDF
```

## Anti-Goals

- Do NOT activate on general PDF queries — wait for explicit watermark-related requests
- Do NOT modify page content — only remove watermark overlays
- Do NOT add watermarks — only remove them

## References

- `references/design-spec.md`: Detailed design specification
- `references/detection-keywords.md`: Complete keyword list for detection
- `references/api-guide.md`: PyMuPDF API reference and usage
- `references/troubleshooting.md`: Common issues and solutions