---
name: 配置手册
description: 自动扫描全部 AI 配置（用户级+项目级），生成 AI 配置手册.md 到 Obsidian
---

# 配置手册

## 功能

扫描全部 AI 配置（用户级 + 项目级），自动生成 **AI配置手册.md** 写进 Obsidian 笔记库。

## 使用场景

- 你改了 CLAUDE.md 指令，想同步更新配置手册
- 新增/修改了 Skill，想记录最新清单
- 新增了 MCP 插件（如北大法宝），想更新记录
- 随时想查看当前所有配置的一览总表

## 执行命令

```bash
python D:/AI/1.业务/.claude/generate_ai_manual.py
```

带 `--force` 参数可强制重新生成（跳过哈希检查）：

```bash
python D:/AI/1.业务/.claude/generate_ai_manual.py --force
```

带 `--check` 参数仅检查是否有变化（不写入）：

```bash
python D:/AI/1.业务/.claude/generate_ai_manual.py --check
```

## 工作原理

该脚本会扫描以下内容，生成 Markdown 手册并写入 Obsidian：

| 来源 | 内容 |
|------|------|
| 项目级 `CLAUDE.md` | 项目核心指令全文 |
| 项目级 Skills | `D:\AI\1.业务\.claude\skills\` - 11 个技能 |
| 项目级隐藏 Skills | `D:\AI\1.业务\.claude\.claude\skills\` - GitHub 安装技能 |
| 用户级 `.claude` Skills | `C:\Users\11828\.claude\skills\` - 9 个技能 |
| 用户级 CLAUDE.md | 全局指令 |
| openCode 配置 | `opencode.jsonc` |
| 记忆系统 | Reasonix 全局/项目记忆 |
| 其他 AI 项目 | D:\AI 下所有项目 |

脚本有内置哈希缓存（SHA256），配置无变化时跳过写入，避免 Obsidian 产生无意义版本。
