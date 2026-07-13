"""
威科先行自动化检索脚本
用法: python legal_search.py "关键词" [法律法规|裁判文书] [--detail]
"""

import sys
import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Windows 编码修复
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 配置
LOGIN_URL = "https://oa.hiwayslaw.com/Account/Login"
WK_URL = "https://oa.hiwayslaw.com/CommonTools/CaseLaw/WkInfo"
USERNAME = "xionghaochen"
PASSWORD = "xionghaochen"

async def login(page):
    """登录律智荟"""
    await page.goto(LOGIN_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)

    # 截图调试
    await page.screenshot(path="debug_login.png")
    print(f"当前URL: {page.url}")

    # 用户名和密码输入框（跳过第一个租户名称字段）
    username_input = page.locator('input[type="text"]').nth(1)
    password_input = page.locator('input[type="password"]').first

    await username_input.fill(USERNAME)
    await password_input.fill(PASSWORD)
    await page.click('button:has-text("登录")')

    # 等待页面跳转
    await page.wait_for_timeout(5000)
    await page.screenshot(path="debug_after_login.png")
    print(f"登录后URL: {page.url}")

async def dismiss_popups(page):
    """关闭威科先行的各种弹窗和引导遮罩"""
    try:
        # 等待页面稳定
        await page.wait_for_timeout(2000)

        # 方法1: 点击关闭按钮（常见选择器）
        close_selectors = [
            'button.close', '.close-btn', '[aria-label="Close"]',
            '.modal-close', '.popup-close', '.guide-close',
            'i.icon-close', 'span.close', '.ant-modal-close',
            'button:has-text("关闭")', 'button:has-text("我知道了")',
            'button:has-text("跳过")', 'button:has-text("知道了")',
        ]
        for sel in close_selectors:
            try:
                btn = page.locator(sel).first
                if await btn.is_visible(timeout=500):
                    await btn.click()
                    print(f"  关闭弹窗: {sel}")
                    await page.wait_for_timeout(500)
            except:
                pass

        # 方法2: 按Escape关闭弹窗
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(500)

        # 方法3: 通过JavaScript移除遮罩层
        await page.evaluate('''() => {
            // 移除guide-mask和各种遮罩
            const masks = document.querySelectorAll('.guide-mask, .modal-mask, .overlay, [class*="mask"], [class*="overlay"]');
            masks.forEach(m => m.remove());

            // 移除可能的弹窗容器
            const popups = document.querySelectorAll('.guide-modal, .welcome-modal, .popup, [class*="guide"]');
            popups.forEach(p => {
                if (p.style.position === 'fixed' || p.classList.toString().includes('guide')) {
                    p.remove();
                }
            });
        }''')
        print("  已通过JS移除遮罩层")
        await page.wait_for_timeout(500)

    except Exception as e:
        print(f"  关闭弹窗异常: {e}")

async def search_wk(page, keyword, search_type="裁判文书"):
    """在威科先行执行搜索"""
    # 跳转到威科先行（SSO 跳转）
    print(f"正在跳转到: {WK_URL}")
    try:
        await page.goto(WK_URL, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"跳转警告: {e}")

    await page.wait_for_timeout(8000)
    print(f"威科先行URL: {page.url}")

    # 关闭弹窗
    print("检查并关闭弹窗...")
    await dismiss_popups(page)

    # 点击搜索类型（法律法规/裁判文书）
    print(f"点击: {search_type}")
    type_selector = f'div.home-lnk-column-item:has-text("{search_type}")'
    try:
        await page.click(type_selector, timeout=10000)
    except Exception as e:
        print(f"点击失败，尝试再次关闭弹窗: {e}")
        await dismiss_popups(page)
        await page.wait_for_timeout(1000)
        try:
            await page.click(type_selector, timeout=10000)
        except Exception as e2:
            print(f"再次点击失败: {e2}")
            # 尝试直接导航到裁判文书页面
            await page.goto("https://law.wkinfo.com.cn/judgment-documents/list", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

    await page.wait_for_timeout(2000)

    # 再次关闭可能出现的弹窗
    await dismiss_popups(page)

    # 输入关键词搜索
    print(f"输入关键词: {keyword}")
    try:
        await page.fill('#keyword', keyword)
    except:
        # 尝试其他输入框选择器
        await page.fill('input[type="text"], input[placeholder*="搜索"], input[placeholder*="关键词"]', keyword)
    await page.wait_for_timeout(1000)

    # 点击搜索按钮
    print("点击搜索")
    try:
        await page.click('button.wkb-btn-green')
    except:
        # 尝试其他搜索按钮
        await page.click('button:has-text("搜索"), button[type="submit"]')

    # 等待结果加载
    print("等待结果...")
    await page.wait_for_timeout(5000)
    await page.screenshot(path="debug_search_result.png")
    print(f"搜索结果URL: {page.url}")

async def extract_results(page):
    """提取搜索结果URL列表"""
    results = await page.evaluate('''() => {
        const links = document.querySelectorAll('a[href*="judgment-documents/detail"], a[href*="case-analysis/detail"]');
        const seen = new Set();
        const results = [];

        for (const link of links) {
            const href = link.href;
            if (seen.has(href)) continue;
            seen.add(href);

            const text = link.textContent?.trim() || '';
            // 过滤掉"查看详情→"这种纯操作链接
            if (text === '查看详情→' || text.length < 10) continue;

            results.push({
                title: text.substring(0, 200),
                url: href,
                type: href.includes('judgment-documents') ? 'judgment' : 'case-analysis'
            });
        }

        return results;
    }''')
    return results

async def fetch_details_playwright(page, results):
    """用 Playwright（已登录状态）批量抓取详情页内容"""
    print(f"\n开始抓取 {len(results)} 条详情页...")

    for i, r in enumerate(results):
        try:
            print(f"  抓取 {i+1}/{len(results)}: {r['title'][:40]}...")
            await page.goto(r['url'], wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            # 等待正文容器加载
            try:
                await page.wait_for_selector('.detail-content, .judgment-content, .case-content, article, .content-area', timeout=10000)
            except:
                pass

            # 提取正文内容
            content = await page.evaluate('''() => {
                // 尝试多种选择器
                const selectors = [
                    '.detail-content',
                    '.judgment-content',
                    '.case-content',
                    'article',
                    '.content-area',
                    '.article-content',
                    '#content',
                    '.main-content',
                    '[class*="content"]',
                    '[class*="detail"]'
                ];

                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el && el.textContent.trim().length > 200) {
                        return el.innerText.trim();
                    }
                }

                // 兜底：取 body 中最长的文本块
                const body = document.body.innerText;
                return body.trim();
            }''')

            r['content'] = content if content else ''
            print(f"    ✓ 获取 {len(r['content'])} 字符")

        except Exception as e:
            print(f"    失败: {e}")
            r['content'] = ''

    return results

OUTPUT_DIR = Path(r"C:\Users\11828\OneDrive\obsidian\胖胖熊\案件\raw\案件\案例")

def sanitize_filename(name):
    for c in '<>:"/\\|?*':
        name = name.replace(c, '')
    return name.strip()[:100]

def save_to_obsidian(results):
    """保存案例全文到Obsidian"""
    if not results:
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    for r in results:
        content = r.get('content', '')
        if not content or len(content) < 500:
            continue
        safe_title = sanitize_filename(r['title'])
        filepath = OUTPUT_DIR / f"{safe_title}.md"
        md = f"""---
来源: 威科先行
标题: {r['title']}
---

{content}
"""
        filepath.write_text(md, encoding='utf-8')
        saved += 1
        print(f"  已保存: {filepath.name} ({len(content)}字符)")
    print(f"共保存 {saved} 个案例到 {OUTPUT_DIR}")

async def main():
    if len(sys.argv) < 2:
        print("用法: python legal_search.py \"关键词\" [法律法规|裁判文书] [--detail]")
        sys.exit(1)

    keyword = sys.argv[1]
    search_type = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "裁判文书"
    fetch_detail = '--detail' in sys.argv

    print(f"开始检索: {keyword} ({search_type})")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 登录
            print("正在登录...")
            await login(page)

            # 搜索
            print(f"正在搜索: {keyword}")
            await search_wk(page, keyword, search_type)

            # 提取结果
            print("正在提取结果...")
            results = await extract_results(page)

            # 抓取详情页（可选）
            if fetch_detail and results:
                results = await fetch_details_playwright(page, results)
                save_to_obsidian(results)

            # 输出结果
            output = {
                "keyword": keyword,
                "search_type": search_type,
                "count": len(results),
                "results": results
            }

            # 保存到文件
            output_file = Path(f"search_result_{keyword}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)

            print(f"\n检索完成! 共 {len(results)} 条结果")
            print(f"结果已保存到: {output_file}")

            # 打印前5条
            for i, r in enumerate(results[:5], 1):
                print(f"\n{i}. {r['title'][:80]}...")
                print(f"   URL: {r['url'][:100]}...")

        except Exception as e:
            print(f"错误: {e}")
            sys.exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
