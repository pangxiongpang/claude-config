#!/usr/bin/env python3
"""
合同审查报告 PDF 生成器（Playwright HTML→PDF 版）
用 Playwright 渲染 HTML 为 PDF，排版效果好，无需 GTK/wkhtmltopdf。
"""

import sys
import os
import json
import asyncio
from datetime import datetime

try:
    from jinja2 import Template
except ImportError:
    print("ERROR: jinja2 is required. Install with: pip install jinja2")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "templates", "report_cn.html")

GRADE_COLORS = {
    "A+": "#16a34a", "A": "#16a34a", "B": "#65a30d",
    "C": "#d97706", "D": "#dc2626", "F": "#991b1b",
}
RISK_LABELS = {"high": "高风险", "medium": "中风险", "low": "低风险"}


def build_pdf(data, output_path):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = Template(f.read())

    for c in data.get("clauses", []):
        c["risk_label"] = RISK_LABELS.get(c.get("risk", "low"), "低风险")

    grade = data.get("grade", "C")
    html_content = template.render(
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

    # 写临时 HTML 文件
    tmp_html = output_path.replace(".pdf", "_tmp.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 用 Playwright 渲染
    asyncio.run(_render(tmp_html, output_path))

    # 清理临时文件
    if os.path.exists(tmp_html):
        os.remove(tmp_html)

    return output_path


async def _render(html_path, pdf_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        abs_path = os.path.abspath(html_path).replace("\\", "/")
        await page.goto(f"file:///{abs_path}", wait_until="networkidle")
        await page.pdf(path=pdf_path, format="A4", margin={
            "top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"
        }, print_background=True)
        await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate_legal_pdf_html.py <json文件> [输出PDF路径]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "合同审查报告.pdf"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = build_pdf(data, output_path)
    print(f"PDF 已生成: {result}")
