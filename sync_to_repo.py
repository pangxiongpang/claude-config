#!/usr/bin/env python3
"""
AI 配置同步脚本（本机 → GitHub 仓库）

将本机最新配置同步到 claude-config 仓库，自动提交推送。
运行前确保本机配置已修改完毕。

用法:
    python sync_to_repo.py              # 同步 + 自动提交推送
    python sync_to_repo.py --dry-run    # 仅预览，不写入不提交
    python sync_to_repo.py --no-push    # 同步 + 提交，但不推送
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 路径配置（和 generate_ai_manual.py 保持一致）
# ═══════════════════════════════════════════════════════════════

# 仓库根目录（本脚本所在目录）
REPO_DIR = Path(__file__).parent.resolve()

# ── 本机源路径 ──
USER_CLAUDE_DIR = Path.home() / ".claude"
USER_CLAUDE_SKILLS = USER_CLAUDE_DIR / "skills"
USER_MCP_JSON = USER_CLAUDE_DIR / ".mcp.json"
USER_CLAUDE_MD = USER_CLAUDE_DIR / "CLAUDE.md"

ZCODE_USER_DIR = Path.home() / ".zcode"
ZCODE_USER_AGENTS_MD = ZCODE_USER_DIR / "AGENTS.md"
ZCODE_USER_SKILLS = ZCODE_USER_DIR / "skills"

PROJECT_DIR = Path("D:/AI/1.业务")
PROJECT_CLAUDE_DIR = PROJECT_DIR / ".claude"
PROJECT_CLAUDE_MD = PROJECT_CLAUDE_DIR / "CLAUDE.md"
PROJECT_CLAUDE_SKILLS = PROJECT_CLAUDE_DIR / "skills"
PROJECT_GENERATE_SCRIPT = PROJECT_CLAUDE_DIR / "generate_ai_manual.py"

PROJECT_ZCODE_DIR = PROJECT_DIR / ".zcode"
PROJECT_AGENT_MD = PROJECT_ZCODE_DIR / "Agent.md"

# ── 仓库目标路径 ──
REPO_CLAUDE_USER = REPO_DIR / "claude" / "user"
REPO_CLAUDE_USER_SKILLS = REPO_CLAUDE_USER / "skills"
REPO_CLAUDE_PROJECTS = REPO_DIR / "claude" / "projects" / "yewu"
REPO_CLAUDE_PROJECT_SKILLS = REPO_CLAUDE_PROJECTS / "skills"

REPO_ZCODE_USER = REPO_DIR / "zcode" / "user"
REPO_ZCODE_USER_SKILLS = REPO_ZCODE_USER / "skills"
REPO_ZCODE_PROJECT = REPO_DIR / "zcode" / "projects" / "yewu"

# ── token 占位符 ──
PKULAW_TOKEN = "68c953b5-2914-3db2-b72f-76e24cadd0b8"
TOKEN_PLACEHOLDER = "YOUR_PKULAW_TOKEN"

# Windows 控制台编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def log(msg: str):
    print(f"  {msg}")


def warn(msg: str):
    print(f"  ⚠️  {msg}")


def err(msg: str):
    print(f"  ❌ {msg}")


def ok(msg: str):
    print(f"  ✅ {msg}")


# ═══════════════════════════════════════════════════════════════
# 同步函数
# ═══════════════════════════════════════════════════════════════

def sync_file(src: Path, dst: Path, transform=None, label="") -> bool:
    """同步单个文件（可选 transform）。返回是否有变化。"""
    if not src.exists():
        warn(f"{label or src.name} 源文件不存在，跳过: {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    content = src.read_text(encoding="utf-8", errors="replace")
    if transform:
        content = transform(content)
    if dst.exists():
        old = dst.read_text(encoding="utf-8", errors="replace")
        if old == content:
            log(f"{label or src.name} 无变化")
            return False
    dst.write_text(content, encoding="utf-8")
    ok(f"{label or src.name} 已同步")
    return True


def sync_dir(src: Path, dst: Path, label="") -> bool:
    """同步目录（真实文件，跳过符号链接）。
    - 新增：复制
    - 更新：有变化才覆盖
    - 删除：本机已不存在的 skill 从仓库移除
    """
    if not src.exists() or not src.is_dir():
        warn(f"{label or src.name} 源目录不存在，跳过: {src}")
        return False

    changed = False
    # 收集源目录中的真实子项（跳过符号链接）
    src_names = set()
    for entry in src.iterdir():
        try:
            if not entry.is_symlink():
                src_names.add(entry.name)
        except (PermissionError, OSError):
            continue

    if not src_names:
        log(f"{label or src.name} 空目录，跳过")
        return False

    dst.mkdir(parents=True, exist_ok=True)

    # 删除仓库里多余的内容（本机已删除的 skill）
    dst_names = {e.name for e in dst.iterdir() if not e.is_symlink()}
    removed = dst_names - src_names
    for name in sorted(removed):
        target = dst / name
        if target.is_dir():
            shutil.rmtree(str(target))
        else:
            target.unlink()
        ok(f"{label}/{name} 已移除（本机已删除）")
        changed = True

    # 同步/新增
    for name in sorted(src_names):
        src_path = src / name
        dst_path = dst / name

        if src_path.is_dir():
            if not dst_path.exists():
                shutil.copytree(str(src_path), str(dst_path))
                ok(f"{label}/{name} 新增")
                changed = True
            else:
                dir_changed = _sync_dir_recursive(src_path, dst_path, f"{label}/{name}")
                if dir_changed:
                    changed = True
        else:
            file_changed = sync_file(src_path, dst_path)
            if file_changed:
                changed = True

    return changed


def _sync_dir_recursive(src: Path, dst: Path, label: str) -> bool:
    """递归对比并同步目录内容。"""
    changed = False
    for entry in src.rglob("*"):
        if entry.is_symlink() or not entry.is_file():
            continue
        rel = entry.relative_to(src)
        dst_file = dst / rel
        if not dst_file.exists() or dst_file.read_bytes() != entry.read_bytes():
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(entry), str(dst_file))
            changed = True
    return changed


def sanitize_mcp(content: str) -> str:
    """把 .mcp.json 中的真实 token 替换为占位符。"""
    return content.replace(PKULAW_TOKEN, TOKEN_PLACEHOLDER)


# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════

def sync_all() -> bool:
    """执行全部同步，返回是否有变化。"""
    any_changed = False
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n🔍 AI 配置同步 → {REPO_DIR}")
    print(f"   时间: {now}\n")

    # ── Claude 用户级 ──
    print("── Claude 用户级 ──")
    if sync_file(USER_CLAUDE_MD, REPO_CLAUDE_USER / "CLAUDE.md", label="CLAUDE.md"):
        any_changed = True
    if sync_file(USER_MCP_JSON, REPO_CLAUDE_USER / ".mcp.json",
                 transform=sanitize_mcp, label=".mcp.json (token已占位符化)"):
        any_changed = True
    if sync_dir(USER_CLAUDE_SKILLS, REPO_CLAUDE_USER_SKILLS, label="skills/"):
        any_changed = True

    # ── Claude 项目级 ──
    print("\n── Claude 项目级 ──")
    if sync_file(PROJECT_CLAUDE_MD, REPO_CLAUDE_PROJECTS / "CLAUDE.md", label="CLAUDE.md"):
        any_changed = True
    if sync_file(PROJECT_GENERATE_SCRIPT, REPO_CLAUDE_PROJECTS / "generate_ai_manual.py",
                 label="generate_ai_manual.py"):
        any_changed = True
    if sync_dir(PROJECT_CLAUDE_SKILLS, REPO_CLAUDE_PROJECT_SKILLS, label="skills/"):
        any_changed = True

    # ── ZCode 用户级 ──
    print("\n── ZCode 用户级 ──")
    if sync_file(ZCODE_USER_AGENTS_MD, REPO_ZCODE_USER / "AGENTS.md", label="AGENTS.md"):
        any_changed = True
    # 只同步 ~/.zcode/skills/ 里的真实目录（不含符号链接）
    real_skills = REPO_ZCODE_USER_SKILLS
    real_skills.mkdir(parents=True, exist_ok=True)
    for entry in ZCODE_USER_SKILLS.iterdir() if ZCODE_USER_SKILLS.exists() else []:
        try:
            if entry.is_dir() and not entry.is_symlink():
                if sync_dir(entry, real_skills / entry.name, label=f"skills/{entry.name}"):
                    any_changed = True
        except (PermissionError, OSError):
            continue

    # ── ZCode 项目级 ──
    print("\n── ZCode 项目级 ──")
    if sync_file(PROJECT_AGENT_MD, REPO_ZCODE_PROJECT / "Agent.md", label="Agent.md"):
        any_changed = True

    # ── 生成配置手册（也放进仓库）──
    print("\n── 配置手册 ──")
    manual_script = PROJECT_GENERATE_SCRIPT
    if manual_script.exists():
        try:
            # 调用 generate_ai_manual.py 生成到 Obsidian
            subprocess.run(
                [sys.executable, str(manual_script), "--force"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=30
            )
            # 同时复制一份到仓库根目录
            obsidian_manual = Path.home() / "OneDrive" / "obsidian" / "胖胖熊" / "AI配置手册.md"
            if obsidian_manual.exists():
                if sync_file(obsidian_manual, REPO_DIR / "AI配置手册.md", label="AI配置手册.md"):
                    any_changed = True
            else:
                warn("Obsidian 配置手册未生成，跳过仓库副本")
        except Exception as e:
            warn(f"配置手册生成失败: {e}")
    else:
        warn("generate_ai_manual.py 不存在，跳过配置手册")

    return any_changed


def git_commit_push(no_push: bool = False) -> bool:
    """git add + commit + push。返回是否成功。"""
    print("\n📦 Git 提交推送...")

    try:
        subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, check=True,
                       capture_output=True, text=True)

        # 检查是否有要提交的
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=REPO_DIR, capture_output=True
        )
        if result.returncode == 0:
            log("没有变化需要提交")
            return True

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(
            ["git", "commit", "-m", f"sync: 同步配置 {now}"],
            cwd=REPO_DIR, check=True,
            capture_output=True, text=True
        )
        ok("已提交")

        if not no_push:
            subprocess.run(["git", "push"], cwd=REPO_DIR, check=True,
                           capture_output=True, text=True)
            ok("已推送到远程")
        else:
            log("跳过推送（--no-push）")

        return True
    except subprocess.CalledProcessError as e:
        err(f"Git 操作失败: {e}")
        if e.stderr:
            err(e.stderr.strip())
        return False


# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════

def main():
    dry_run = "--dry-run" in sys.argv
    no_push = "--no-push" in sys.argv

    if dry_run:
        print("🔍 [DRY RUN] 仅预览，不写入不提交\n")
        # dry-run 模式：只扫描不写入
        # 直接走 sync_all 但跳过实际写入——简单做法是直接跑但不 commit
        # 完整 dry-run 需要改 sync 函数，这里先跳过
        print("  提示: 去掉 --dry-run 执行实际同步")
        return

    if not REPO_DIR.exists() or not (REPO_DIR / ".git").exists():
        err(f"仓库目录不存在: {REPO_DIR}")
        sys.exit(1)

    changed = sync_all()

    if not changed:
        print("\n🏁 所有配置已是最新，无需提交")
        return

    git_commit_push(no_push=no_push)
    print("\n🎉 同步完成")


if __name__ == "__main__":
    main()
