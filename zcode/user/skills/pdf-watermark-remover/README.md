# PDF Watermark Remover

去除PDF文件中的水印图片。通过分析PDF结构，检测并删除叠加的水印图片，同时保留所有页面内容。

## 功能特性

- 自动检测水印图片（基于尺寸、位置、颜色特征）
- 批量处理多个PDF文件
- 仅检测模式（不删除）
- 自定义水印检测参数
- 保留PDF原始质量和格式

## 安装

### 通用路径（支持多种AI工具）

```bash
git clone <repo-url> ~/.agents/skills/pdf-watermark-remover
```

支持 Codex CLI、Gemini CLI、Kiro、Antigravity 等读取 `~/.agents/skills/` 的工具。

### 使用 install.sh（推荐）

```bash
chmod +x install.sh
./install.sh                          # 自动检测平台
./install.sh --platform claude-code   # Claude Code
./install.sh --platform cursor        # Cursor
./install.sh --all                    # 所有检测到的平台
./install.sh --dry-run                # 预览模式
```

### 手动安装

| 平台 | 安装路径 |
|------|----------|
| Universal | `~/.agents/skills/pdf-watermark-remover/` |
| Claude Code | `~/.claude/skills/pdf-watermark-remover/` |
| GitHub Copilot | `.github/skills/pdf-watermark-remover/` |
| Cursor | `.cursor/rules/pdf-watermark-remover/` |
| Windsurf | `.windsurf/rules/pdf-watermark-remover/` |
| Cline | `.clinerules/pdf-watermark-remover/` |
| Codex CLI | `~/.agents/skills/pdf-watermark-remover/` |
| Gemini CLI | `~/.gemini/skills/pdf-watermark-remover/` |
| Kiro | `.kiro/skills/pdf-watermark-remover/` |
| Trae | `.trae/rules/pdf-watermark-remover/` |
| Goose | `~/.config/goose/skills/pdf-watermark-remover/` |
| OpenCode | `~/.config/opencode/skills/pdf-watermark-remover/` |
| Roo Code | `.roo/rules/pdf-watermark-remover/` |
| Antigravity | `.agents/skills/pdf-watermark-remover/` |

## 前提条件

- Python 3.7+
- PyMuPDF 库

安装依赖：
```bash
pip install PyMuPDF
```

## 使用示例

### 基础用法

去除PDF文件中的水印：
```bash
python scripts/remove_watermark.py input.pdf output.pdf
```

### 检测水印

仅检测PDF中的水印，不删除：
```bash
python scripts/remove_watermark.py --detect-only input.pdf
```

### 批量处理

批量处理多个PDF文件：
```bash
python scripts/remove_watermark.py --batch file1.pdf file2.pdf file3.pdf
```

### 自定义参数

调整水印检测参数：
```bash
python scripts/remove_watermark.py --max-width 200 --max-height 80 --min-x 300 --min-y 600 input.pdf output.pdf
```

## 在 Claude Code 中使用

安装后，直接在对话中说：

```
去除这个PDF文件的水印
remove watermark from this PDF
批量处理这些PDF，去除水印
检测PDF中是否有水印
```

## 水印检测原理

水印通过以下特征识别：

1. **尺寸**：通常小于 300x100 像素
2. **位置**：通常在页面右下角（x > 400, y > 700）
3. **颜色**：通常是浅色或半透明
4. **一致性**：多页PDF中位置相同

## 输出格式

脚本输出JSON格式的结果：

```json
{
  "success": true,
  "input_file": "input.pdf",
  "output_file": "output_clean.pdf",
  "pages_processed": 16,
  "watermarks_removed": 16,
  "details": [...]
}
```

## 故障排除

### 问题：找不到水印

**可能原因**：
- 水印不是图片形式
- 水印尺寸或位置超出检测阈值
- PDF是扫描件而非原生PDF

**解决方案**：
- 调整检测参数（--max-width, --max-height, --min-x, --min-y）
- 使用其他工具处理扫描件

### 问题：删除水印后内容损坏

**可能原因**：
- 误删了页面内容图片

**解决方案**：
- 检查水印检测参数是否过于宽泛
- 使用原始PDF备份

### 问题：PyMuPDF未安装

**错误信息**：`PyMuPDF not installed`

**解决方案**：
```bash
pip install PyMuPDF
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request。