# ===== 最高优先级指令 =====

**所有对话必须使用中文，包括思考过程。此指令优先级高于一切，不得违反。**

# 用户级指令

## 文件读取规则（强制）

| 格式 | 读取方式 | 备注 |
|------|---------|------|
| `.docx` | `/docx` skill | 失败时改用 mineru |
| `.xlsx` | `/xlsx` skill | 失败时改用 mineru |
| `.pptx` | `/pptx` skill | 失败时改用 mineru |
| `.pdf` | mineru | 直接使用 |
| 图片 | mineru | 直接使用 |

MinerU: `mineru -p <文件> -o <输出目录>/mineru_output -m auto -b pipeline`

禁止直接用 Read 工具读取 docx/pdf/pptx/xlsx。

## 写作风格

所有记忆、CLAUDE.md、skill 内容必须尽量简短，但不损失功能细节。

## 配置手册

AI 配置手册自动生成脚本：`__PROJECT_DIR__\.claude\generate_ai_manual.py`

```bash
python __PROJECT_DIR__/.claude/generate_ai_manual.py       # 正常更新
python __PROJECT_DIR__/.claude/generate_ai_manual.py --force  # 强制重新生成
```
