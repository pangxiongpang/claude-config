# AI配置手册

> 更新时间：2026-07-16 19:58
> 自动生成：`D:\AI\1.业务\.claude\generate_ai_manual.py`
> 扫描范围：用户级 + 项目级全部 AI 配置

---

## 一、配置文件清单

| 来源 | 路径 | 类型 |
|------|------|------|
| **项目级 CLAUDE.md** | `D:\AI\1.业务\.claude\CLAUDE.md` | ✅ 核心指令 |
| **项目级 Skills** | `D:\AI\1.业务\.claude\skills` | ✅ 技能目录 |
| **项目级隐藏 Skills** | `D:\AI\1.业务\.claude\.claude\skills` | ❌ GitHub 安装技能 |
| **项目级 skills-lock** | `D:\AI\1.业务\.claude\skills-lock.json` | ❌ 技能注册表 |
| **用户级 CLAUDE.md** | `C:\Users\11828\.claude\CLAUDE.md` | ✅ 全局指令 |
| **用户级 .claude Skills** | `C:\Users\11828\.claude\skills` | ✅ Claude Code 技能 |
| **用户级 openCode 配置** | `C:\Users\11828\.config\opencode\opencode.jsonc` | ✅ JSON 配置 |
| **用户级 Claude MCP 配置** | `C:\Users\11828\.claude\.mcp.json` | ✅ MCP 服务器 |

---

## 二、项目级 CLAUDE.md（核心指令）

```markdown
# 项目指令

## 用户身份

- 姓名：熊淏晨
- 律所：上海市海华永泰（泰州）律师事务所
- 职业：律师

---

## 核心原则（最高优先级）

以下原则优先于本文件所有其他规则：

- **熊淏晨的思路很多时候可能是错的，我有义务直接纠正他，不能一味附和。**
- 不得因为他是客户/用户就回避指出错误、风险或更优方案。
- 风险审查必须全面，发现问题必须指出，不论是否在原始委托范围内。
- 展示所有可行方案，包括保守的和有创意的，不局限于最保守的选项。
- 每种方案标注风险程度、风险点、前提条件、适用场景。
- 只展示真正可行的方案；若只剩一条路，明确说明，不强行凑数。
- 在明显有问题的地方直言纠偏，不一味附和。
- 有多种合理解读时，说明假设、权衡和建议方案，必要时让客户决策。
- 推测必须明确标注为推测，并说明推测依据；不得将推测表述为既定事实。

---

## 操作规则（⚠️ 易忘规则集中在此）

### 1. 北大法宝 MCP 权限（强制，优先级等同核心原则）

**所有北大法宝 MCP 工具（`mcp__pkulaw-*`），每次调用前必须征得用户明确允许，不得自动发起。** 即使用户要求使用北大法宝，也需在具体调用前向用户确认并等待许可。

### 2. 文件读取规则（强制）

| 格式 | 读取方式 | 备注 |
|------|---------|------|
| `.docx` | `/docx` skill | 失败时改用 mineru |
| `.xlsx` | `/xlsx` skill | 失败时改用 mineru |
| `.pptx` | `/pptx` skill | 失败时改用 mineru |
| `.pdf` | mineru | 直接使用 |
| 图片 | mineru | 直接使用 |

MinerU: `mineru -p <文件> -o <输出目录>/mineru_output -m auto -b pipeline`

禁止直接用 Read 工具读取 docx/pdf/pptx/xlsx。

### 3. Playwright 使用后清理

使用 Playwright 浏览器完成任务后，立即删除 `.playwright-mcp/` 临时文件：
```
rm -rf .playwright-mcp/
```

### 4. Mimo 命令参数

免费通道被风控，调用 `mimo run` 时必须加：
```
mimo run -m xiaomi/mimo-v2.5-pro
```

### 5. Git Bash + Python 中文路径编码预防

当通过 Bash 执行 Python 脚本处理含中文路径的文件时：
1. 先把文件复制到纯 ASCII 路径（如 `C:\Users\11828\`）再执行
2. 生成含中文文本的 JSON 时，用 Python `json.dump(ensure_ascii=False)`
3. Jinja2 模板中禁止使用中文变量名
4. 写 JSON 后立即验证：`python -c "import json; json.load(open(path))"`

### 6. Obsidian 操作规则

操作 Obsidian 前必须先读 `obsidian-cli` skill（`C:\Users\11828\.claude\skills\obsidian-cli\SKILL.md`），然后使用 `obsidian` CLI 执行操作，禁止直接读写文件。操作前还需读 vault 根目录的 `CLAUDE.md` 和 `schema.md`。

### 7. 法条核实规则

分析案子时自动核实法条是否现行有效，调用 `law-validation` skill：
```
python "D:/AI/1.业务/.claude/skills/law-validation/law_validate.py" "法条名称" 条号
```

### 8. Skill 搜索规则

找 skill 时同时搜两个位置：全局 `~/.claude/skills/` 和项目 `<项目目录>/.claude/skills/`。

### 9. 会话启动检查（强制，优先级等同核心原则）

**收到新任务后、开始工作前，必须先读 `memory/MEMORY.md`。** 当前只有 Whisper 一条记忆，直接扫一眼即可。若将来有新增记忆，任务涉及相关主题时记得去读具体文件。

### 10. AI 配置手册维护

AI 配置手册自动生成脚本：

```bash
python D:/AI/1.业务/.claude/generate_ai_manual.py       # 正常更新
python D:/AI/1.业务/.claude/generate_ai_manual.py --force  # 强制重新生成
```

更新完配置手册后，同步到 GitHub 配置仓库：

```bash
cd D:/AI/claude-config
git add -A
git commit -m "chore: 同步 AI 配置手册"
git push
```

### 11. Claude Code 配置仓库同步

配置仓库：`https://github.com/pangxiongpang/claude-config`

用途：备份和同步所有 skill、agent、MCP 配置、记忆等。

操作：
- **用户说「同步配置」** → 完成以下步骤：
  1. 提交 `D:\AI\claude-config` 的修改
  2. 推送到 GitHub
- **用户说「更新AI配置手册」** → 运行配置手册脚本 → 同步到 GitHub
- **换电脑时** → 把仓库链接给 agent，按照 SETUP.md 的指引自动恢复

---

## 工作方式

- 处理非简单法律任务时，先读完相关材料，再给出分析或修改方案。
- 若任务涉及多份文件、复杂案件分析或预计跨多轮执行，先给出简短工作计划。
- 复杂法律任务应判断是否使用专项 skill（如 legal-review、legal-mock-trial 等）。
- 对多步骤或长期任务，明确工作范围、完成标准和停止条件；遇到权限、范围或风险不明确时，停止并确认。
- 修改文书时，不做无关的形式改动；但风险审查必须全面。
- 优先复用事务所已有的模板、文书和工作模式。

---

## 案例检索规则

- 默认使用 `法律检索` skill（触发词：检索案例、查找判例、搜索类似案件、查判例、案例检索）。

```

---

## 三、MCP 服务器配置

### openCode 通用配置
```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow"
}
```

### CLAUDE.md 中提及的 MCP 规则

- 1. 北大法宝 MCP 权限（强制，优先级等同核心原则）
- **所有北大法宝 MCP 工具（`mcp__pkulaw-*`），每次调用前必须征得用户明确允许，不得自动发起。** 即使用户要求使用北大法宝，也需在具体调用前向用户确认并等待许可。
- 用途：备份和同步所有 skill、agent、MCP 配置、记忆等。

### Claude 用户级 MCP 服务器
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "chromium", "--isolated"]
    },
    "pkulaw-law-search": {
      "url": "https://apim-gateway.pkulaw.com/mcp-law-search-service/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    },
    "pkulaw-law-keyword": {
      "url": "https://apim-gateway.pkulaw.com/mcp-law/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    },
    "pkulaw-case-semantic": {
      "url": "https://apim-gateway.pkulaw.com/mcp-case-search-service/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    },
    "pkulaw-case-keyword": {
      "url": "https://apim-gateway.pkulaw.com/mcp-case/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    },
    "pkulaw-law-item-keyword": {
      "url": "https://apim-gateway.pkulaw.com/mcp-fatiao/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    },
    "pkulaw-law-recognition": {
      "url": "https://apim-gateway.pkulaw.com/law_recognition/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    },
    "pkulaw-case-number-id": {
      "url": "https://apim-gateway.pkulaw.com/case_number_recognition/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    },
    "pkulaw-citation-valid": {
      "url": "https://apim-gateway.pkulaw.com/pku_citation_validator/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    },
    "pkulaw-doc-link": {
      "url": "https://apim-gateway.pkulaw.com/add-doc-link/mcp",
      "headers": {
        "Authorization": "Bearer 68c953b5-2914-3db2-b72f-76e24cadd0b8"
      }
    }
  }
}

```

---

## 四、项目级 Skills — 项目级 Skills（D:\AI\1.业务\.claude\skills）

| Skill | 用途 | 路径 |
|-------|------|------|
| `config-manual` | 配置手册：扫描全部 AI 配置，生成配置手册 + 同步到 GitHub 仓库 | `D:\AI\1.业务\.claude\skills\config-manual` |
| `law-validation` | 法条核实：核实法条是否现行有效（国家法律法规数据库）。全称或简称均可，名称和条号分开传入。 | `D:\AI\1.业务\.claude\skills\law-validation` |
| `legal-compare` | Side-by-Side Contract Comparison：Side-by-side comparison of two contract vers... | `D:\AI\1.业务\.claude\skills\legal-compare` |
| `legal-evidence` | 证据分析工具：Claim Chart/五维风险评估/不利事实分析，案件证据的系统化分析 | `D:\AI\1.业务\.claude\skills\legal-evidence` |
| `legal-litigation-skill` | /legal-litigation-skill — 诉讼案件全流程管理（Orchestrator）：>- | `D:\AI\1.业务\.claude\skills\legal-litigation-skill` |
| `legal-mock-trial` | 庭审模拟对抗推演：庭审模拟对抗推演。启动3个并行agent（对方律师+法官+判决预判师），在开庭前模拟对抗，发现弱点、查漏补缺。可独立调用，也可由 leg... | `D:\AI\1.业务\.claude\skills\legal-mock-trial` |
| `legal-report-pdf` | /legal-report-pdf — 全能 PDF 报告生成器：全能 PDF 报告生成器。根据不同报告类型选择对应模板，通过 Playwright 将 ... | `D:\AI\1.业务\.claude\skills\legal-report-pdf` |
| `legal-research` | 法律检索：使用威科先行数据库检索法律法规和裁判文书 | `D:\AI\1.业务\.claude\skills\legal-research` |
| `legal-review` | Full Contract Review — Flagship Orchestrator：全功能合同审查引擎。接收合同文件/文本/URL，启动5个并行子代... | `D:\AI\1.业务\.claude\skills\legal-review` |
| `legal-templates` | 法律文书模板库：起诉状/答辩状/代理词/仲裁申请书/律师函/法律意见书等文书模板，按需调用 | `D:\AI\1.业务\.claude\skills\legal-templates` |
| `ppt-master` | PPT Master Skill：> | `D:\AI\1.业务\.claude\skills\ppt-master` |
| `watch` | /watch：Watch a video (URL or local path). Downloads with yt-dlp, extracts aut... | `D:\AI\1.业务\.claude\skills\watch` |

---

## 五、openCode / Claude Code 平台配置

### openCode 配置
```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow"
}
```

### 用户级 CLAUDE.md（全局指令）
```markdown
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

AI 配置手册自动生成脚本：`D:\AI\1.业务\.claude\generate_ai_manual.py`

```bash
python D:/AI/1.业务/.claude/generate_ai_manual.py       # 正常更新
python D:/AI/1.业务/.claude/generate_ai_manual.py --force  # 强制重新生成
```
```

### 用户级 Claude Code Skills

| Skill | 路径 |
|-------|------|
| `agent-orchestrator-skill` | `C:\Users\11828\.claude\skills\agent-orchestrator-skill` |
| `agent-skill-creator` | `C:\Users\11828\.claude\skills\agent-skill-creator` |
| `docx-official` | `C:\Users\11828\.claude\skills\docx-official` |
| `find-skills` | `C:\Users\11828\.claude\skills\find-skills` |
| `obsidian-cli` | `C:\Users\11828\.claude\skills\obsidian-cli` |
| `pdf-official` | `C:\Users\11828\.claude\skills\pdf-official` |
| `pdf-watermark-remover` | `C:\Users\11828\.claude\skills\pdf-watermark-remover` |
| `pptx-official` | `C:\Users\11828\.claude\skills\pptx-official` |
| `xlsx-official` | `C:\Users\11828\.claude\skills\xlsx-official` |

---

## 六、其他 AI 项目目录

- **1.业务/** 🤖
- **2.日常/**
- **claude-config/**
- **cli-anything/**
- **CloudMusic/**
- **ffmpeg/**
- **funasr/**
- **Git/**
- **MinerU/**
- **node.js/**
- **加速器/**

> 🤖 = 包含 AI 配置文件

---

## 七、ZCode AI 助手配置

### 用户级 ZCode（~/.zcode/）

**AGENTS.md（用户级指令）**
```markdown
# ===== 最高优先级指令 =====

**所有对话必须使用中文，包括思考过程。此指令优先级高于一切，不得违反。**

# 用户级指令

## 核心原则（最高优先级）

以下原则优先于本文件所有其他规则：

- **用户的思路很多时候可能是错的，我有义务直接纠正他，不能一味附和。**
- 不得因为他是用户就回避指出错误、风险或更优方案。
- 风险审查必须全面，发现问题必须指出，不论是否在原始委托范围内。
- 展示所有可行方案，包括保守的和有创意的，不局限于最保守的选项。
- 每种方案标注风险程度、风险点、前提条件、适用场景。
- 只展示真正可行的方案；若只剩一条路，明确说明，不强行凑数。
- 在明显有问题的地方直言纠偏，不一味附和。
- 有多种合理解读时，说明假设、权衡和建议方案，必要时让用户决策。
- 推测必须明确标注为推测，并说明推测依据；不得将推测表述为既定事实。

---

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

---

## 操作规则（⚠️ 易忘规则集中在此）

### 1. 会话启动检查（强制）

**收到新任务后、开始工作前，必须先读 `memory/MEMORY.md`。** 若记忆文件较多，扫一眼标题即可；若任务涉及相关主题时再去读具体文件。

### 2. Playwright 使用后清理

使用 Playwright 浏览器完成任务后，立即删除 `.playwright-mcp/` 临时文件：
```
rm -rf .playwright-mcp/
```
...（共 89 行，仅显示前 50 行）
```

**用户级 Skills**

| Skill | 类型 | 路径 |
|-------|------|------|
| `agent-orchestrator-skill` | 本地目录 | `C:\Users\11828\.zcode\skills\agent-orchestrator-skill` |
| `agent-skill-creator` | 本地目录 | `C:\Users\11828\.zcode\skills\agent-skill-creator` |
| `find-skills` | 本地目录 | `C:\Users\11828\.zcode\skills\find-skills` |
| `obsidian-cli` | 本地目录 | `C:\Users\11828\.zcode\skills\obsidian-cli` |
| `pdf-watermark-remover` | 本地目录 | `C:\Users\11828\.zcode\skills\pdf-watermark-remover` |
| `pptx-official` | 本地目录 | `C:\Users\11828\.zcode\skills\pptx-official` |
| `stock-analyzer` | 本地目录 | `C:\Users\11828\.zcode\skills\stock-analyzer` |
| `watch` | 本地目录 | `C:\Users\11828\.zcode\skills\watch` |
| `xlsx-official` | 本地目录 | `C:\Users\11828\.zcode\skills\xlsx-official` |

### 项目级 ZCode（D:/AI/1.业务/.zcode/）

**Agent.md（项目级指令）**
```markdown
# 项目指令

## 用户身份

- 姓名：熊淏晨
- 律所：上海市海华永泰（泰州）律师事务所
- 职业：律师

---

## 项目特有规则

### 1. 北大法宝 MCP 权限（强制，优先级等同核心原则）

**所有北大法宝 MCP 工具（`mcp__pkulaw-*`），每次调用前必须征得用户明确允许，不得自动发起。** 即使用户要求使用北大法宝，也需在具体调用前向用户确认并等待许可。

### 2. Mimo 命令参数

免费通道被风控，调用 `mimo run` 时必须加：
```
mimo run -m xiaomi/mimo-v2.5-pro
```

### 3. Obsidian 操作规则

操作 Obsidian 前必须先读 `obsidian-cli` skill（`C:\Users\11828\.claude\skills\obsidian-cli\SKILL.md`），然后使用 `obsidian` CLI 执行操作，禁止直接读写文件。操作前还需读 vault 根目录的 `CLAUDE.md` 和 `schema.md`。

### 4. 法条核实规则

分析案子时自动核实法条是否现行有效，调用 `law-validation` skill：
```
python "D:/AI/1.业务/.claude/skills/law-validation/law_validate.py" "法条名称" 条号
```

### 5. 案例检索规则

- 默认使用 `法律检索` skill（触发词：检索案例、查找判例、搜索类似案件、查判例、案例检索）。

---

## 工作方式（法律业务）

- 处理非简单法律任务时，先读完相关材料，再给出分析或修改方案。
- 涉及多份文件、复杂案件分析或预计跨多轮执行的任务，先给出简短工作计划。
- 复杂法律任务应判断是否使用专项 skill（如 legal-review、legal-mock-trial 等）。
- 对多步骤或长期任务，明确工作范围、完成标准和停止条件；遇到权限、范围或风险不明确时，停止并确认。
- 修改文书时，不做无关的形式改动；但风险审查必须全面。
- 优先复用事务所已有的模板、文书和工作模式。
```

**项目级 Skills**

| Skill | 类型 | 路径 |
|-------|------|------|
| `config-manual` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\config-manual` |
| `law-validation` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\law-validation` |
| `legal-compare` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\legal-compare` |
| `legal-evidence` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\legal-evidence` |
| `legal-litigation-skill` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\legal-litigation-skill` |
| `legal-mock-trial` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\legal-mock-trial` |
| `legal-report-pdf` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\legal-report-pdf` |
| `legal-research` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\legal-research` |
| `legal-review` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\legal-review` |
| `legal-templates` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\legal-templates` |
| `ppt-master` | 本地目录 | `D:\AI\1.业务\.zcode\.zcode\skills\ppt-master` |

### 启用的 AI 提供商

- **Z.ai - Coding Plan**：GLM-5.2, GLM-5-Turbo

---

> 本文档由 `generate_ai_manual.py` 自动生成，手动编辑将在下次更新时被覆盖。
