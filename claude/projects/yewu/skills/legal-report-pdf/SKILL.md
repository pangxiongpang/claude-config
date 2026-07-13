---
name: legal-report-pdf
description: 全能 PDF 报告生成器。根据不同报告类型选择对应模板，通过 Playwright 将 HTML+CSS 渲染为专业排版 PDF。支持合同审查报告、法律分析报告等类型，CSS 渐变、卡片布局均正常渲染。
---

# /legal-report-pdf — 全能 PDF 报告生成器

## 触发方式

`/legal-report-pdf` 或自然语言："帮我生成一份 PDF 报告"、"导出报告"

## 依赖

```bash
pip install jinja2 playwright
playwright install chromium
```

## 使用方法

```bash
# 合同审查报告
python "scripts/generate_pdf.py" data.json --type contract

# 法律分析报告
python "scripts/generate_pdf.py" data.json --type legal_analysis -o 报告.pdf
```

## 报告类型

### contract — 合同审查报告

必填字段：`contract_name`, `score`, `grade`, `grade_label`, `details`, `executive_summary`, `risks`, `clauses`, `obligations`, `negotiation_priorities`, `missing_protections`, `next_steps`

- `clauses[]`: `name`, `section`, `risk`(high/medium/low), `summary`, `risk_explanation`, `recommendation`
- `obligations[]`: `party`, `content`, `deadline`, `consequence`

```json
{
  "contract_name": "某采购合同审查报告",
  "score": 72,
  "grade": "C",
  "grade_label": "中等风险",
  "clauses": [
    {"name": "违约责任", "section": "第12条", "risk": "high",
     "summary": "违约金过高", "risk_explanation": "...", "recommendation": "..."}
  ]
}
```

### legal_analysis — 法律分析报告

必填字段：`report_title`, `client_info`, `service_target`, `report_date`, `case_info`, `project_structure`, `known_facts`, `core_issues`, `legal_relations`, `payment_analysis`, `recovery_paths`, `risk_counts`, `risk_items`, `urgent_actions`, `conclusions`, `most_urgent`

- `legal_relations[]`: `title`, `subtitle`, `legal_basis`, `analysis`, `conclusion`
- `recovery_paths[]`: `priority`(primary/secondary/tertiary), `tag`, `title`, `legal_basis`, `feasibility`, `prerequisites`, `risks`
- `risk_items[]`: `level`(高/中/低), `item`, `description`
- `urgent_actions[]`: `title`, `steps`, `importance`

```json
{
  "report_title": "法律分析报告标题",
  "case_info": {"服务对象": "...", "项目类型": "..."},
  "legal_relations": [{"title": "法律关系一", "subtitle": "...", "legal_basis": "...", "analysis": "..."}]
}
```

### dd — 尽职调查报告（预留）

计划支持，尚未实现。

## 输出

默认输出到当前目录 `合同审查报告.pdf` 或 `法律分析报告.pdf`。可用 `-o` 指定输出路径。

## 模板

模板位于 `templates/{type}/` 目录下：
- `templates/contract/report_cn.html`
- `templates/legal_analysis/analysis_report.html`

## 开发注意事项

### 中文路径编码问题

当前环境（Windows + Git Bash）下，含中文的文件路径可能被解析为乱码。如果遇到文件找不到的错误：

1. 先将脚本和数据文件复制到纯 ASCII 路径再执行：
   ```bash
   cp scripts/generate_pdf.py "C:/Users/11828/"
   cp data.json "C:/Users/11828/"
   cd "C:/Users/11828/"
   python generate_pdf.py data.json --type contract
   ```

2. 或者直接用 Python 的绝对路径调用。

### JSON 中文引号

JSON 中的中文引号（" "）必须使用 `json.dump(ensure_ascii=False)` 生成，**不要**用 Write 工具手写 JSON，否则 `"` 可能被写成 ASCII 双引号破坏 JSON 结构。

### 模板变量名

Jinja2 模板中 **禁止** 使用中文变量名（如 `{% for 变量 in list %}`），必须使用英文变量名。

### 新增报告类型

1. 在 `templates/` 下创建 `{type}/` 目录，放入 Jinja2 HTML 模板
2. 在 `scripts/generate_pdf.py` 中补充：
   - `TEMPLATE_MAP` — 模板路径映射
   - `TYPE_LABEL` — 类型中文名
   - `REQUIRED_FIELDS` — 校验规则
   - 编写渲染函数，加入 `RENDER_FUNCS`

## 旧脚本兼容

旧脚本 `generate_legal_pdf_html.py` 仍保留，可单独使用（仅支持合同审查）。
