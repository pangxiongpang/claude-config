#!/usr/bin/env python3
"""
全能 PDF 报告生成器
将 JSON 数据渲染为 HTML 后通过 Playwright 输出 PDF。

用法:
  python generate_pdf.py data.json --type contract
  python generate_pdf.py data.json --type legal_analysis -o 报告.pdf

支持的报告类型:
  contract        - 合同审查报告
  legal_analysis  - 法律分析报告
"""

import argparse
import sys
import os
import json
import asyncio
from datetime import datetime

try:
    from jinja2 import Template
except ImportError:
    print("错误：缺少 jinja2，请运行: pip install jinja2")
    sys.exit(1)

# ============================================================
# 路径与模板映射
# ============================================================
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(SKILL_DIR, "templates")

TEMPLATE_MAP = {
    "contract": "contract/report_cn.html",
    "legal_analysis": "legal_analysis/analysis_report.html",
}

TYPE_LABEL = {
    "contract": "合同审查报告",
    "legal_analysis": "法律分析报告",
}

# ============================================================
# JSON 字段校验
# ============================================================
REQUIRED_FIELDS = {
    "contract": ["contract_name", "score", "grade", "clauses"],
    "legal_analysis": ["report_title", "case_info", "legal_relations", "recovery_paths"],
}


def validate_json(data, report_type):
    missing = [f for f in REQUIRED_FIELDS.get(report_type, []) if f not in data]
    if missing:
        print("错误：JSON 缺少必需字段:")
        for f in missing:
            print(f"  - {f}")
        sys.exit(1)


# ============================================================
# 合同审查渲染
# ============================================================
GRADE_COLORS = {
    "A+": "#16a34a", "A": "#16a34a", "B": "#65a30d",
    "C": "#d97706", "D": "#dc2626", "F": "#991b1b",
}
RISK_LABELS = {"high": "高风险", "medium": "中风险", "low": "低风险"}


def render_contract(data, template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    for c in data.get("clauses", []):
        c["risk_label"] = RISK_LABELS.get(c.get("risk", "low"), "低风险")

    grade = data.get("grade", "C")
    return template.render(
        contract_name=data.get("contract_name", "合同审查报告"),
        report_date=datetime.now().strftime("%Y年%m月%d日"),
        score=data.get("score", 0),
        grade=grade,
        grade_color=GRADE_COLORS.get(grade, "#d97706"),
        grade_label=data.get("grade_label", ""),
        details=data.get("details", {}),
        executive_summary=data.get("executive_summary", ""),
        risks=data.get("risks", {}),
        clauses=data.get("clauses", []),
        obligations=data.get("obligations", []),
        negotiation_priorities=data.get("negotiation_priorities", []),
        missing_protections=data.get("missing_protections", []),
        next_steps=data.get("next_steps", []),
    )


# ============================================================
# 法律分析渲染
# ============================================================
def render_legal_analysis(data, template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())
    return template.render(**data)


# ============================================================
# HTML → PDF（Playwright）
# ============================================================
async def _html_to_pdf(html_path, pdf_path):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("错误：缺少 playwright，请运行: pip install playwright && playwright install chromium")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        abs_path = os.path.abspath(html_path).replace("\\", "/")
        await page.goto(f"file:///{abs_path}", wait_until="networkidle")
        await page.pdf(
            path=pdf_path,
            format="A4",
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
            print_background=True,
        )
        await browser.close()


def build_pdf(html_content, output_path):
    output_path = os.path.abspath(output_path)
    tmp_html = output_path.replace(".pdf", "_tmp.html")

    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    try:
        asyncio.run(_html_to_pdf(tmp_html, output_path))
    finally:
        if os.path.exists(tmp_html):
            os.remove(tmp_html)

    return output_path


# ============================================================
# 入口
# ============================================================
RENDER_FUNCS = {
    "contract": render_contract,
    "legal_analysis": render_legal_analysis,
}


def main():
    parser = argparse.ArgumentParser(
        description="全能 PDF 报告生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python generate_pdf.py review.json --type contract\n"
            "  python generate_pdf.py analysis.json --type legal_analysis -o 报告.pdf\n"
        ),
    )
    parser.add_argument("json_file", help="JSON 数据文件路径")
    parser.add_argument(
        "--type", "-t",
        choices=list(TEMPLATE_MAP.keys()),
        default="contract",
        help="报告类型（默认: contract）",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出 PDF 路径（默认: 当前目录/报告类型.pdf）",
    )

    args = parser.parse_args()

    # 检查 JSON 文件
    if not os.path.exists(args.json_file):
        print(f"错误：找不到文件: {args.json_file}")
        sys.exit(1)

    # 读取 JSON
    with open(args.json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 校验
    validate_json(data, args.type)

    # 默认输出路径
    if args.output:
        output_path = args.output
    else:
        output_path = os.path.join(os.getcwd(), TYPE_LABEL.get(args.type, "报告.pdf"))

    # 模板路径
    template_rel = TEMPLATE_MAP[args.type]
    template_path = os.path.join(TEMPLATE_DIR, template_rel)
    if not os.path.exists(template_path):
        print(f"错误：找不到模板: {template_path}")
        sys.exit(1)

    # 渲染 HTML
    render_func = RENDER_FUNCS[args.type]
    html_content = render_func(data, template_path)

    # 生成 PDF
    result = build_pdf(html_content, output_path)
    print(f"PDF 已生成: {result}")


if __name__ == "__main__":
    main()
