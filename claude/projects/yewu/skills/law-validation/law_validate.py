"""
法条核实脚本
用法: python law_validate.py "法条名称" [条号]
示例: python law_validate.py "工伤保险条例" "17"
       python law_validate.py "民法典" "577"

功能：通过国家法律法规数据库核实法条是否现行有效
搜索流程：首页输入 → 按Enter → 新标签页search → 读取结果
"""

import sys
import asyncio
from playwright.async_api import async_playwright

# Windows 编码修复
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FLK_URL = "https://flk.npc.gov.cn"

# 优先使用 MCP 已安装的 chromium（如果有）
import os
MCP_CHROMIUM_PATH = "C:/Users/11828/AppData/Local/ms-playwright/chromium-1229/chrome-win64/chrome.exe"
PYTHON_CHROMIUM_PATH = "C:/Users/11828/AppData/Local/ms-playwright/chromium-1223/chrome-win64/chrome.exe"

BROWSER_PATH = MCP_CHROMIUM_PATH if os.path.exists(MCP_CHROMIUM_PATH) else PYTHON_CHROMIUM_PATH if os.path.exists(PYTHON_CHROMIUM_PATH) else None


async def search_and_check(browser_context, search_query, law_name, article_number):
    """
    在国家法律法规数据库搜索法条并判断时效性。
    正确流程：输入搜索词 → 按 Enter → 新标签页 → 读取结果
    """
    page = await browser_context.new_page()

    # 1. 打开首页
    await page.goto(FLK_URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3000)

    # 2. 输入搜索词（例："工伤保险条例第17条"，不加空格）
    inp = page.locator('input[placeholder="请输入"]')
    await inp.fill(search_query)
    await page.wait_for_timeout(1000)

    # 3. 按 Enter —— 这会打开一个新标签页到 /search
    async with browser_context.expect_page(timeout=15000) as search_page_info:
        await inp.press("Enter")

    # 4. 切换到搜索结果标签页
    search_page = await search_page_info.value
    await search_page.wait_for_load_state("domcontentloaded", timeout=30000)
    await search_page.wait_for_timeout(3000)

    # 5. 读取搜索结果页面的全部文本
    body_text = await search_page.evaluate('() => document.body.innerText || document.body.textContent')

    await page.close()
    await search_page.close()

    return body_text


def parse_results(body_text, law_name):
    """从搜索结果文本中解析有效/已修改/已废止信息"""
    lines = body_text.split('\n')

    # 先尝试找国家级的（名称完全匹配，不包含省/自治区/直辖市前缀）
    national_candidates = []
    local_candidates = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行和明显不是结果的行
        if not line or '检索条件' in line or '排序' in line or '清空条件' in line or '页/条' in line:
            i += 1
            continue

        # 检查是否包含法规名称 + 状态 (有效/已修改/已废止)
        # 结果格式: 工伤保险条例有效  或 工伤保险条例已修改
        if law_name in line:
            status = None
            if '有效' in line:
                status = '有效'
            elif '已修改' in line:
                status = '已修改'
            elif '已废止' in line:
                status = '已废止'
            elif '失效' in line:
                status = '失效'

            if status:
                # 收集上下几行信息
                detail_lines = []
                for j in range(max(0, i - 1), min(len(lines), i + 4)):
                    detail_lines.append(lines[j].strip())
                detail_text = ' '.join(filter(None, detail_lines))

                # 是否国家级（名称中没有"省/市/自治区"等地域名称）
                is_national = not any(
                    kw in detail_text for kw in
                    ['省', '市', '自治区', '自治州', '经济特区', '县', '区']
                )

                entry = {
                    'status': status,
                    'detail': detail_text[:300],
                    'line': line[:100]
                }

                if is_national:
                    national_candidates.append(entry)
                else:
                    local_candidates.append(entry)

        i += 1

    # 优先返回国家级匹配
    if national_candidates:
        return national_candidates[0]
    elif local_candidates:
        return local_candidates[0]

    return None


async def main():
    if len(sys.argv) < 2:
        print("用法: python law_validate.py \"法条全称\" [条号]")
        print("示例: python law_validate.py \"工伤保险条例\" \"17\"")
        print("       python law_validate.py \"中华人民共和国民法典\" \"577\"")
        sys.exit(1)

    law_name = sys.argv[1]
    article_number = sys.argv[2] if len(sys.argv) > 2 else None

    # 搜索词格式：名称+第X条（中间不加空格）
    search_query = f"{law_name}第{article_number}条" if article_number else law_name

    print(f"核实: {law_name}" + (f" 第{article_number}条" if article_number else ""))

    async with async_playwright() as p:
        launch_kwargs = {"headless": True}
        if BROWSER_PATH:
            launch_kwargs["executable_path"] = BROWSER_PATH
        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context()

        try:
            body_text = await search_and_check(
                context, search_query, law_name, article_number
            )

            result = parse_results(body_text, law_name)

            if not result:
                # 尝试用简称再搜一次（去掉"中华人民共和国"前缀）
                short_name = law_name.replace("中华人民共和国", "")
                if short_name != law_name:
                    print(f"未找到，尝试简称搜索: {short_name}")
                    search_query2 = f"{short_name}第{article_number}条" if article_number else short_name
                    body_text = await search_and_check(
                        context, search_query2, short_name, article_number
                    )
                    result = parse_results(body_text, short_name)

            if not result:
                print("状态: 未找到")
                sys.exit(1)

            status = result['status']
            if status == '有效':
                print("状态: ✅ 现行有效")
            elif status == '已修改':
                print("状态: ⚠️ 已被修改（注意适用版本）")
            else:
                print(f"状态: ❌ {status}")

            print(f"匹配: {result['detail'][:200]}")

            if article_number and status == '有效':
                print(f"\n条文: 请用北大法宝 MCP 获取第{article_number}条具体内容")

        except Exception as e:
            print(f"错误: {e}")
            print("提示: 可能需要更新 Playwright 浏览器 (npx playwright install chromium)")
            sys.exit(1)
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
