---
name: 配置手册
description: 扫描全部 AI 配置，生成配置手册 + 同步到 GitHub 仓库
---

# 配置手册

## 功能

扫描全部 AI 配置（用户级 + 项目级），自动生成 **AI配置手册.md** 写进 Obsidian，
并将所有配置同步到 GitHub 仓库（`pangxiongpang/claude-config`）。

## 使用场景

- 改了 CLAUDE.md / AGENTS.md / Agent.md，想同步更新手册和远程仓库
- 新增/修改了 Skill
- 修改了 MCP 配置（注意：真实 token 自动替换为占位符，不上传）
- 换电脑前执行一次，确保远程仓库最新

## 执行命令

一条龙完成（生成手册到 Obsidian + 同步所有配置到 GitHub）：

```bash
python D:/AI/claude-config/sync_to_repo.py
```

如需单独生成手册（不同步仓库）：
```bash
python D:/AI/1.业务/.claude/generate_ai_manual.py --force
```

## 流程

`sync_to_repo.py` 自动执行三步：
1. 调用 `generate_ai_manual.py --force` 生成 **AI配置手册.md** → Obsidian
2. 将规范文件、skills、MCP 等全部配置同步到 `D:/AI/claude-config` 仓库
3. git commit + push 到 GitHub

## 工作原理

`generate_ai_manual.py` 会扫描以下内容，生成 Markdown 手册并写入 Obsidian：

| 来源 | 内容 |
|------|------|
| 项目级 `CLAUDE.md` | 项目核心指令全文 |
| 项目级 Skills | `D:\AI\1.业务\.claude\skills\` - 12 个技能 |
| 项目级隐藏 Skills | `D:\AI\1.业务\.claude\.claude\skills\` - GitHub 安装技能 |
| 用户级 `.claude` Skills | `C:\Users\11828\.claude\skills\` - 9 个技能 |
| 用户级 CLAUDE.md | 全局指令 |
| ZCode 用户级 | AGENTS.md + skills |
| ZCode 项目级 | Agent.md |
| openCode 配置 | `opencode.jsonc` |
| 记忆系统 | Reasonix 全局/项目记忆 |
| 其他 AI 项目 | D:\AI 下所有项目 |

`sync_to_repo.py` 将配置同步到 `D:\AI\claude-config` 仓库的 `claude/` 和 `zcode/` 目录，
分隔存储，自动提交推送。`.mcp.json` 中的北大法宝 token 入库时替换为 `YOUR_PKULAW_TOKEN` 占位符。

脚本有内置哈希缓存（SHA256），无变化时跳过写入。
