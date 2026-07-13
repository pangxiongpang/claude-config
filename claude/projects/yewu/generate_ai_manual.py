#!/usr/bin/env python3
"""
AI 配置手册生成器
扫描所有用户级和项目级 AI 配置，生成 AI 配置手册.md 写入 Obsidian。

用法:
    python generate_ai_manual.py          # 正常生成（有哈希缓存）
    python generate_ai_manual.py --force  # 强制重新生成
    python generate_ai_manual.py --check  # 仅检查是否有变化
"""

import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 路径配置
# ═══════════════════════════════════════════════════════════════

# Obsidian 输出路径
OUTPUT_PATH = Path.home() / "OneDrive" / "obsidian" / "胖胖熊" / "AI配置手册.md"

# 缓存文件（记录上次生成的哈希，避免无意义覆盖）
CACHE_PATH = Path(__file__).parent / ".manual_cache.json"

# 项目级配置（D 盘）
PROJECT_DIR = Path("D:/AI/1.业务/.claude")
PROJECT_SKILLS_DIR = PROJECT_DIR / "skills"
PROJECT_HIDDEN_SKILLS_DIR = PROJECT_DIR / ".claude" / "skills"

# 用户级配置（C 盘）
USER_CLAUDE_DIR = Path.home() / ".claude"
USER_CLAUDE_SKILLS_DIR = USER_CLAUDE_DIR / "skills"
USER_OPENCODE_CONFIG = Path.home() / ".config" / "opencode" / "opencode.jsonc"

# ZCode 配置路径
ZCODE_USER_DIR = Path.home() / ".zcode"
ZCODE_USER_SKILLS_DIR = ZCODE_USER_DIR / "skills"
ZCODE_PROJECT_DIR = Path("D:/AI/1.业务/.zcode")
ZCODE_PROJECT_SKILLS_DIR = ZCODE_PROJECT_DIR / ".zcode" / "skills"
ZCODE_PROJECT_AGENT_MD = ZCODE_PROJECT_DIR / "Agent.md"
ZCODE_USER_AGENTS_MD = ZCODE_USER_DIR / "AGENTS.md"

# Windows 控制台编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def log(msg: str):
    print(f"  {msg}")


def sha256_file(path: Path) -> str:
    """计算文件的 SHA256 哈希"""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except Exception:
        return ""
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(cache: dict):
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def read_file_safe(path: Path, max_lines: int = 0) -> str:
    """安全读取文件内容"""
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if max_lines > 0:
            lines = text.splitlines()
            text = "\n".join(lines[:max_lines])
            if len(lines) > max_lines:
                text += f"\n...（共 {len(lines)} 行，仅显示前 {max_lines} 行）"
        return text
    except Exception as e:
        return f"（读取失败: {e}）"


def read_skill_description(skill_dir: Path) -> str:
    """从 SKILL.md 中提取 skill 的名称和描述"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "（无 SKILL.md）"

    # 尝试从 frontmatter 取 description
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
    desc = match.group(1).strip().strip('"') if match else ""

    # 取第一行标题作为名称
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    name = title_match.group(1).strip() if title_match else skill_dir.name

    return f"{name}：{desc}" if desc else name


def format_file_tree(path: Path, max_depth: int = 2) -> str:
    """生成目录树文本"""
    if not path.exists() or not path.is_dir():
        return "（目录不存在）"
    lines = []
    try:
        for i, entry in enumerate(sorted(path.iterdir())):
            if i >= 30:
                lines.append(f"  ...（共超过 30 项）")
                break
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"  {entry.name}{suffix}")
    except PermissionError:
        lines.append("  （无权限访问）")
    except Exception as e:
        lines.append(f"  （读取错误: {e}）")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# 扫描函数
# ═══════════════════════════════════════════════════════════════

def scan_overview() -> str:
    """扫描配置文件清单"""
    sections = []

    sections.append("## 一、配置文件清单\n")
    sections.append("| 来源 | 路径 | 类型 |")
    sections.append("|------|------|------|")

    items = [
        ("项目级 CLAUDE.md", str(PROJECT_DIR / "CLAUDE.md"), "核心指令"),
        ("项目级 Skills", str(PROJECT_SKILLS_DIR), "技能目录"),
        ("项目级隐藏 Skills", str(PROJECT_HIDDEN_SKILLS_DIR), "GitHub 安装技能"),
        ("项目级 skills-lock", str(PROJECT_DIR / "skills-lock.json"), "技能注册表"),
        ("用户级 CLAUDE.md", str(USER_CLAUDE_DIR / "CLAUDE.md"), "全局指令"),
        ("用户级 .claude Skills", str(USER_CLAUDE_SKILLS_DIR), "Claude Code 技能"),
        ("用户级 openCode 配置", str(USER_OPENCODE_CONFIG), "JSON 配置"),
        ("用户级 Claude MCP 配置", str(USER_CLAUDE_DIR / ".mcp.json"), "MCP 服务器"),
    ]

    for name, p, kind in items:
        exists = "✅" if Path(p).exists() else "❌"
        sections.append(f"| **{name}** | `{p}` | {exists} {kind} |")

    sections.append("")
    return "\n".join(sections)


def scan_claude_md() -> str:
    """扫描项目级 CLAUDE.md"""
    path = PROJECT_DIR / "CLAUDE.md"
    if not path.exists():
        return "## 二、项目级 CLAUDE.md\n\n（不存在）\n"
    content = read_file_safe(path)
    return f"## 二、项目级 CLAUDE.md（核心指令）\n\n```markdown\n{content}\n```\n"


def scan_mcp_config() -> str:
    """扫描 MCP 配置"""
    # 从 skills-lock.json 中提取 MCP 相关信息
    # 实际上 MCP 配置可能在 opencode.jsonc 或其他地方
    sections = ["## 三、MCP 服务器配置\n"]

    # 尝试读取 opencode.jsonc（可能有 MCP 配置）
    if USER_OPENCODE_CONFIG.exists():
        cfg_content = read_file_safe(USER_OPENCODE_CONFIG)
        # 检查是否包含 MCP 相关字段
        if "mcp" in cfg_content.lower() or "server" in cfg_content.lower():
            sections.append(f"### openCode MCP 配置\n```json\n{cfg_content}\n```\n")
        else:
            sections.append(f"### openCode 通用配置\n```json\n{cfg_content}\n```\n")

    # 检查 CLAUDE.md 中是否有 MCP 使用说明
    claude_content = read_file_safe(PROJECT_DIR / "CLAUDE.md")
    mcp_lines = []
    for l in claude_content.splitlines():
        stripped = l.strip().lstrip("#").strip()
        if ("北大法宝" in stripped or "pkulaw" in stripped.lower() or "MCP" in stripped) and stripped:
            mcp_lines.append(stripped)
    if mcp_lines:
        sections.append("### CLAUDE.md 中提及的 MCP 规则\n")
        for line in mcp_lines:
            sections.append(f"- {line}")
        sections.append("")

    # 用户级 Claude MCP 配置
    claude_mcp = USER_CLAUDE_DIR / ".mcp.json"
    if claude_mcp.exists():
        mcp_content = claude_mcp.read_text(encoding="utf-8", errors="replace")
        sections.append("### Claude 用户级 MCP 服务器\n```json\n" + mcp_content + "\n```\n")

    # 检查项目级是否有独立的 MCP 配置文件
    for pattern in ["*.toml", "mcp*.json", "mcp*.yaml", "mcp*.yml"]:
        for f in PROJECT_DIR.glob(pattern):
            content = read_file_safe(f, max_lines=30)
            sections.append(f"### {f.name}\n```\n{content}\n```\n")

    if len(sections) == 1:
        sections.append("（未找到独立的 MCP 配置文件。MCP 服务器可能通过 AI 平台界面配置。）\n")

    return "\n".join(sections)


CN_NUMS = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]

def scan_skills(name: str, skill_dir: Path, is_project: bool = True, section_num: int = 4) -> str:
    """扫描 Skills 目录。目录不存在时返回空字符串（跳过该章节）。"""
    if not skill_dir.exists():
        return ""

    sections = []
    cn = CN_NUMS[section_num] if section_num < len(CN_NUMS) else str(section_num)
    label = "项目级" if is_project else "用户级"
    sections.append(f"## {cn}、{label} Skills — {name}（{skill_dir}）\n")

    skills = []
    broken_links = []
    for d in skill_dir.iterdir():
        # Windows 上损坏的目录链接：is_dir() 可能返回 False
        # 尝试用 stat 和 lstat 判断
        try:
            is_dir_like = d.is_dir()
            is_broken_link = False
            if not is_dir_like:
                # 检查是否是损坏的符号链接/交接点
                try:
                    is_broken_link = d.is_symlink() and not d.exists()
                except Exception:
                    # 某些 Windows 场景下 is_symlink() 可能抛出异常
                    is_broken_link = False
        except PermissionError:
            continue

        if is_dir_like:
            skills.append(d)
        elif is_broken_link:
            broken_links.append(d.name)

    if not skills and not broken_links:
        # 兜底：用 os.scandir 获取所有名称
        try:
            all_entries = [e.name for e in os.scandir(skill_dir)]
            if all_entries:
                sections.append(f"> ⚠️ 扫描到 {len(all_entries)} 个条目，但均无法通过 Python pathlib 正常识别（可能是损坏的符号链接）\n")
                sections.append(f"> 条目：`{'`, `'.join(all_entries)}`\n")
            else:
                sections.append("（空目录）\n")
        except Exception:
            sections.append("（无 Skills）\n")
        return "\n".join(sections)

    if broken_links:
        sections.append(f"> ⚠️ 以下 {len(broken_links)} 个技能链接已损坏（目标路径不存在）\n")

    sections.append("| Skill | 用途 | 路径 |")
    sections.append("|-------|------|------|")

    for s in skills:
        desc = read_skill_description(s)
        # 截断过长的描述
        if len(desc) > 80:
            desc = desc[:77] + "..."
        sections.append(f"| `{s.name}` | {desc} | `{s}` |")

    if broken_links:
        sections.append(f"\n> 损坏链接：`{'`, `'.join(broken_links)}`\n")

    sections.append("")
    return "\n".join(sections)


def scan_opencode_config(section_num: int = 7) -> str:
    """扫描 openCode 配置详情"""
    cn = CN_NUMS[section_num] if section_num < len(CN_NUMS) else str(section_num)
    sections = [f"## {cn}、openCode / Claude Code 平台配置\n"]

    # openCode config
    if USER_OPENCODE_CONFIG.exists():
        cfg_content = read_file_safe(USER_OPENCODE_CONFIG)
        sections.append(f"### openCode 配置\n```json\n{cfg_content}\n```\n")

    # 用户级 CLAUDE.md
    user_claude = USER_CLAUDE_DIR / "CLAUDE.md"
    if user_claude.exists():
        claude_content = read_file_safe(user_claude, max_lines=100)  # 全文展示（通常仅 30+ 行）
        sections.append(f"### 用户级 CLAUDE.md（全局指令）\n```markdown\n{claude_content}\n```\n")

    # 用户级 .claude skills
    if USER_CLAUDE_SKILLS_DIR.exists():
        skills = sorted([d for d in USER_CLAUDE_SKILLS_DIR.iterdir() if d.is_dir()])
        if skills:
            sections.append("### 用户级 Claude Code Skills\n")
            sections.append("| Skill | 路径 |")
            sections.append("|-------|------|")
            for s in skills:
                sections.append(f"| `{s.name}` | `{s}` |")
            sections.append("")

    return "\n".join(sections)


def scan_other_projects(section_num: int = 8) -> str:
    """扫描其他 AI 项目目录"""
    cn = CN_NUMS[section_num] if section_num < len(CN_NUMS) else str(section_num)
    sections = [f"## {cn}、其他 AI 项目目录\n"]
    ai_dir = Path("D:/AI")

    if not ai_dir.exists():
        sections.append("（D:/AI 目录不存在）\n")
        return "\n".join(sections)

    for item in sorted(ai_dir.iterdir()):
        if item.is_dir():
            # 检查是否包含 AI 配置
            has_config = False
            config_indicators = [item / ".claude", item / "CLAUDE.md"]
            for ci in config_indicators:
                if ci.exists():
                    has_config = True
                    break

            marker = " 🤖" if has_config else ""
            sections.append(f"- **{item.name}/**{marker}")

    sections.append("\n> 🤖 = 包含 AI 配置文件\n")
    return "\n".join(sections)


def scan_zcode_config(section_num: int = 9) -> str:
    """扫描 ZCode AI 助手配置（用户级 + 项目级）"""
    cn = CN_NUMS[section_num] if section_num < len(CN_NUMS) else str(section_num)
    sections = [f"## {cn}、ZCode AI 助手配置\n"]

    # ── 用户级 ZCode ──
    sections.append("### 用户级 ZCode（~/.zcode/）\n")

    if ZCODE_USER_AGENTS_MD.exists():
        content = read_file_safe(ZCODE_USER_AGENTS_MD, max_lines=50)
        sections.append(f"**AGENTS.md（用户级指令）**\n```markdown\n{content}\n```\n")
    else:
        sections.append("- AGENTS.md：❌ 不存在\n")

    # 用户级 ZCode Skills
    if ZCODE_USER_SKILLS_DIR.exists():
        user_skills = sorted([d for d in ZCODE_USER_SKILLS_DIR.iterdir() if d.is_dir() or d.is_symlink()])
        if user_skills:
            sections.append("**用户级 Skills**\n")
            sections.append("| Skill | 类型 | 路径 |")
            sections.append("|-------|------|------|")
            for s in user_skills:
                is_link = s.is_symlink()
                link_target = os.readlink(str(s)) if is_link else ""
                link_info = f" → {link_target}" if link_target else ""
                typ = "符号链接" if is_link else "本地目录"
                sections.append(f"| `{s.name}` | {typ}{link_info} | `{s}` |")
            sections.append("")
    else:
        sections.append("- Skills：❌ 不存在\n")

    # ── 项目级 ZCode ──
    sections.append("### 项目级 ZCode（D:/AI/1.业务/.zcode/）\n")

    if ZCODE_PROJECT_AGENT_MD.exists():
        content = read_file_safe(ZCODE_PROJECT_AGENT_MD, max_lines=50)
        sections.append(f"**Agent.md（项目级指令）**\n```markdown\n{content}\n```\n")
    else:
        sections.append("- Agent.md：❌ 不存在\n")

    if ZCODE_PROJECT_SKILLS_DIR.exists():
        proj_skills = sorted([d for d in ZCODE_PROJECT_SKILLS_DIR.iterdir() if d.is_dir() or d.is_symlink()])
        if proj_skills:
            sections.append("**项目级 Skills**\n")
            sections.append("| Skill | 类型 | 路径 |")
            sections.append("|-------|------|------|")
            for s in proj_skills:
                is_link = s.is_symlink()
                link_target = os.readlink(str(s)) if is_link else ""
                link_info = f" → {link_target}" if link_target else ""
                typ = "符号链接" if is_link else "本地目录"
                sections.append(f"| `{s.name}` | {typ}{link_info} | `{s}` |")
            sections.append("")
    else:
        sections.append("- Skills：❌ 不存在\n")

    # ── ZCode 版本信息 ──
    v2_config = ZCODE_USER_DIR / "v2" / "config.json"
    if v2_config.exists():
        try:
            cfg = json.loads(v2_config.read_text(encoding="utf-8"))
            providers = cfg.get("provider", {})
            active_providers = []
            for name, p in providers.items():
                if p.get("enabled", False):
                    model_info = ", ".join(list(p.get("models", {}).keys())[:3])
                    active_providers.append(f"- **{p.get('name', name)}**：{model_info}")
            if active_providers:
                sections.append("### 启用的 AI 提供商\n")
                sections.extend(active_providers)
                sections.append("")
        except Exception:
            pass

    return "\n".join(sections)


# ═══════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════

def generate() -> str:
    """生成完整的配置手册 Markdown"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    parts = [
        "# AI配置手册\n",
        f"> 更新时间：{now}",
        f"> 自动生成：`{__file__}`",
        f"> 扫描范围：用户级 + 项目级全部 AI 配置\n",
        "---\n",
        scan_overview(),
        "---\n",
        scan_claude_md(),
        "---\n",
        scan_mcp_config(),
        "---\n",
    ]

    # 动态编号章节（从四开始，实际生成才递增）
    sec = [4]
    for name, sdir, is_proj in [
        ("项目级 Skills", PROJECT_SKILLS_DIR, True),
        ("项目级隐藏 Skills（GitHub 安装）", PROJECT_HIDDEN_SKILLS_DIR, True),
    ]:
        content = scan_skills(name, sdir, is_project=is_proj, section_num=sec[0])
        if content:
            parts.append(content)
            parts.append("---\n")
            sec[0] += 1  # 只有实际输出时才递增编号

    parts.append(scan_opencode_config(section_num=sec[0]))
    sec[0] += 1
    parts.append("---\n")
    parts.append(scan_other_projects(section_num=sec[0]))
    parts.append("---\n")
    parts.append(scan_zcode_config(section_num=sec[0] + 1))
    parts.append("---\n")
    parts.append("> 本文档由 `generate_ai_manual.py` 自动生成，手动编辑将在下次更新时被覆盖。\n")

    return "\n".join(parts)


def main():
    force = "--force" in sys.argv
    check_only = "--check" in sys.argv

    print("🔍 AI配置手册生成器")
    print(f"   项目目录: {PROJECT_DIR}")
    print(f"   输出路径: {OUTPUT_PATH}")
    print()

    # 生成内容
    content = generate()
    content_hash = sha256_text(content)

    # 加载缓存
    cache = load_cache()
    last_hash = cache.get("content_hash", "")

    if content_hash == last_hash and not force:
        print("✅ 配置无变化，跳过写入（使用 --force 强制重新生成）")
        if check_only:
            print("   状态: 无变化")
            return
        return

    if check_only:
        print("   状态: 有变化（需要更新）")
        return

    # 确保输出目录存在
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"✅ 已写入: {OUTPUT_PATH}")
    print(f"   大小: {len(content)} 字符")

    # 更新缓存
    cache["content_hash"] = content_hash
    cache["last_generated"] = datetime.now().isoformat()
    save_cache(cache)
    print(f"   缓存已更新")


if __name__ == "__main__":
    main()
