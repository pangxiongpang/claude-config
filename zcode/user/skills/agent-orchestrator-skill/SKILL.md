---
name: agent-orchestrator-skill
description: >-
  Use when tasks can be delegated to sub-agents (Mimo / OpenCode) for efficiency.
  Triggers on: delegation, sub-agent, outsource, assign task, parallel execution,
  batch processing, document整理, data analysis, automation, 多agent.
license: MIT
activation: /agent-orchestrator-skill
provenance:
  source_references:
    - opencode run (model: deepseek-v4-flash-free)
    - mimo run -m xiaomi/mimo-v2.5-pro
metadata:
  author: Claude
  version: 3.1.0
  created: 2026-06-16
  last_reviewed: 2026-07-01
  review_interval_days: 30
---

# /agent-orchestrator-skill — 多智能体委派

将任务委派给 Mimo 或 OpenCode 独立执行。**它们没有你的 MCP/记忆/规则，必须在 prompt 里注入上下文**。法条/案例检索等 MCP 操作必须自己做，不能委派。

## 选哪个

| 场景 | 用 |
|------|----|
| 简单执行（读文件、批量转换、搜索） | `mimo run -m xiaomi/mimo-v2.5-pro "..."` |
| 复杂分析（需推理判断） | `opencode run "..."` |
| 纯体力活 | `mimo` 加 `ultraspeed` 模型 |

用户指定了就听用户的。

## CLI

```bash
mimo run -m xiaomi/mimo-v2.5-pro "任务"     # 必须指定模型，默认被风控
opencode run "任务"                           # 模型由 OpenCode 自身配置
```

## 工作流

1. **判断**：涉及 MCP/记忆/skill → 自己做；纯执行 → 委派；混合 → 拆开做
2. **派活**：在 prompt 里写明任务、规则、背景、输入输出路径
3. **验收**：检查结果，不合格反馈修改，反复不行自己动手
4. **补充**：委派完成后，自己用法条/案例 MCP 整合

## 超时

默认 120s，复杂任务设 `timeout: 300000`，最多重试 2 次。
