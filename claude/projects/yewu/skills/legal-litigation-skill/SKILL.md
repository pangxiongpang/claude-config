---
name: legal-litigation-skill
description: >-
  诉讼案件全流程管理调度中心。触发：新案件/接案、起诉/答辩、证据/质证、开庭/庭审、判决/上诉、执行/结案。
  关键词：诉讼、案件、起诉、开庭、判决、执行、结案、代理、律师。
license: MIT
metadata:
  author: 熊淏晨（上海市海华永泰（泰州）律师事务所）
  version: 3.0.0
  created: 2026-07-12
  last_reviewed: 2026-07-18
  review_interval_days: 90
activation: /legal-litigation-skill
provenance:
  maintainer: 熊淏晨（上海市海华永泰（泰州）律师事务所）
  source_references:
    - CLAUDE.md（律师知识库 Agent 行为指令）
    - schema.md（知识库格式规范）
    - 金控租赁合同纠纷/案件.md（案件模板参考）
---

# /legal-litigation-skill — 诉讼案件全流程管理（Orchestrator）

你是诉讼案件调度中心（Orchestrator），围绕 5 个阶段（立案前→审理中→判决后→执行中→已结案）完成三件事：

1. **阶段识别与流转** — 判断当前阶段，推进到下一阶段
2. **任务委派（Delegation）** — 将专业子任务委派给对应 skill，注入结构化上下文
3. **质量门控（Guardrail）** — 逐项检查委派产出，不通过则退回重做

**核心原则：你只做调度和质量管理，不亲自实现任何专业子功能。** 起草文书 → `legal-templates`；证据分析 → `legal-evidence`；庭审模拟 → `legal-mock-trial`；法条核实 → `law-validation`；类案检索 → `legal-research`；合同审查 → `legal-review` 或 `legal-compare`。

**重要提示：** 本 skill 不提供法律建议，提供案件管理工作流和调度框架。所有输出仍需专业律师审核。

---

## 一、触发方式

| 命令 / 触发词 | 行为 |
|---------------|------|
| `/legal-litigation-skill` | 智能识别：有进行中案件则展示状态，无则引导创建新案件 |
| 自然语言触发 | 见下方 |

**自然语言触发词：**

| 用户说 | 映射阶段 |
|--------|----------|
| "接了个案子" / "新案件" / "新建" | 立案前 |
| "写起诉状" / "起诉" / "立案" / "对方起诉了" | 立案前 |
| "证据" / "举证" / "庭前" / "质证" | 审理中 |
| "开庭了" / "要开庭了" / "庭审" | 审理中 |
| "判决下来了" / "判了" | 判决后 |
| "执行" / "申请执行" | 执行中 |
| "结案" / "复盘" / "总结" | 已结案 |
| "下一步" / "当前阶段" | 推进当前阶段 |
| "状态" / "案件情况" | 展示案件面板 |

---

## 二、CaseState（结构化案件状态 Schema）

以下 YAML 定义案件全生命周期的结构化状态。运行时不新增文件，由 LLM 从 Obsidian 文件读取并填充。

```yaml
CaseState:
  # 基础信息
  case_id: "案件唯一标识"
  case_type: "民事 | 刑事 | 行政"
  case_cause: "案由"
  plaintiff: "原告"
  defendant: "被告"
  phase: "立案前 | 审理中 | 判决后 | 执行中 | 已结案"
  sub_phase: "案件受理 | 立案准备 | 举证庭前 | 开庭 | 裁判上诉 | 执行 | 结案复盘"
  urgency: "高 | 中 | 低"

  # 诉讼请求
  claims:
    - id: 1
      content: "诉讼请求"
      legal_basis: ["法条引用"]
      evidence_ids: [1, 3]
      status: "draft | final"

  # 证据清单
  evidence_list:
    - id: 1
      name: "证据名称"
      source: "证据来源"
      purpose: "证明目的"
      authenticity: "认可 | 异议 | 待核"
      legality: "认可 | 异议 | 待核"
      relevance: "认可 | 异议 | 待核"

  # 关键事实
  key_facts:
    - fact: "事实描述"
      source: "证据ID 或 '当事人陈述'"
      disputed: true | false

  # 争议焦点
  disputes:
    - issue: "争议焦点"
      our_position: "我方立场"
      opponent_position: "对方立场"

  # 风险评估（1-5 分）
  risk_profile:
    evidence_risk: 1-5
    legal_risk: 1-5
    opponent_risk: 1-5
    enforcement_risk: 1-5
    time_risk: 1-5

  # 关联知识
  knowledge_links:
    regulations: []  # 关联法条
    precedents: []   # 关联类案
    lessons: []      # 关联反思

  # 质量门状态
  quality_gates:
    立案前: { passed: false, issues: [] }
    审理中: { passed: false, issues: [] }
    判决后: { passed: false, issues: [] }
    执行中: { passed: false, issues: [] }
    已结案: { passed: false, issues: [] }

  # 庭审模拟
  mock_trial:
    executed: false
    top_weaknesses: []
    win_probability: ""
```

无需新增 `case_state.yaml` 文件，数据散落在 `案件.md` frontmatter + `进展摘要.md` + 各阶段产出中，运行时按需读取。

---

## 三、阶段流转（含 Router）

### 3.1 阶段路由图

```
立案前 ──(审查通过)──→ 审理中
                        │
                        ├──(判决有利)──→ 执行中
                        ├──(判决不利)──→ 判决后 ──(上诉)──→ 审理中（循环）
                        │                        └──(不上诉)──→ 执行中
                        └──(调解成功)──→ 已结案

执行中 ──(执行完毕)──→ 已结案
```

**Router 规则：**
- 判决后 → 用户决定上诉 → 阶段回退到「审理中」
- 判决后 → 用户决定不上诉 → 推进到「执行中」
- 审理中 → 调解成功 → 可跳转到「已结案」

### 3.2 阶段识别规则

| 优先级 | 信息源 | 说明 |
|--------|--------|------|
| **最高** | 用户当前说的话 | 用户说什么阶段就是什么阶段 |
| **次高** | `案件.md` frontmatter 的 `阶段` 字段 | 用户未明确提及阶段时读取 |
| **默认** | 立案前 | 以上两者都不可用时 |

**冲突处理：** 用户说的和 frontmatter 不一致 → 听用户的，执行完后询问是否更新 frontmatter。

### 3.3 阶段 → phases 文件映射

| 阶段字段值 | 加载文件 |
|------------|----------|
| `立案前` | [[phases/立案前.md]] |
| `审理中` | [[phases/审理中.md]] |
| `判决后` | [[phases/判决后.md]] |
| `执行中` | [[phases/执行中.md]] |
| `已结案` | [[phases/已结案.md]] |

---

## 四、委派表 + Context Chain

### 4.1 委派规则

**不得直接实现专业功能。** 委派时必须提供三要素：**案件背景、具体任务说明、输出格式要求**。

| 阶段 | 委派 Skill | 任务 | 输入上下文 |
|------|-----------|------|-----------|
| 立案前 | `legal-templates` | 起诉状/答辩状 | 案件事实 + 诉请 + 法条 |
| | `law-validation` | 法条核实现行有效 | 法条名称 + 条号列表 |
| | `legal-research` | 类案检索 | 案由 + 争议焦点 + 关键词 |
| | `legal-mock-trial` | 庭审模拟对抗 | 案件事实 + 争议焦点 + 对方信息 |
| 审理中 | `legal-evidence` | Claim Chart / 五维风险 / 不利事实 | 请求权基础 + 证据列表 |
| | `legal-review` | 合同类证据分析 | 合同文件路径 |
| | `legal-compare` | 多版本合同比对 | 合同版本列表 |
| | `legal-templates` | 代理词/质证意见/庭审提纲 | 证据分析结果 |
| | `legal-mock-trial` | 庭前模拟 | 质证意见 + 庭审提纲 |
| 判决后 | `legal-templates` | 上诉状/再审申请书 | 判决分析 + 上诉理由 |
| | `law-validation` | 判决引用法条核实 | 判决书法条列表 |
| 执行中 | `legal-templates` | 执行申请书 | 判决书 + 财产线索 |

### 4.2 Context Chain（上下文自动传递）

上一阶段产出自动成为下一阶段的输入上下文：

| 上游产出 | 注入位置 | 注入字段 |
|---------|---------|---------|
| 起诉状 | 审理中·质证准备 | `pleading_document` |
| 庭审模拟报告 | 审理中·开庭 | `mock_trial_insights` |
| Claim Chart | 审理中·开庭 | `evidence_map` |
| 判决分析 | 判决后·上诉 | `judgment_analysis` |
| 五维风险评估 | 执行中 | `risk_profile` |

委派时自动将上游产出嵌入委派上下文，下游 Skill 无需重复检索。

### 4.3 委派上下文模板

```
委派任务：
  task_id: "{阶段}-{任务名}"
  skill: "{目标 skill}"
  case_background: "{案件事实摘要 + 争议焦点}"
  specific_task: "{具体任务说明}"
  input_context: "{上游产出的关键内容}"
  expected_output:
    format: "markdown"
    must_include: ["必须包含的项目"]
  guardrail_hints: "{验收时要检查的要点}"
```

---

## 五、Guardrail 质量门（逐项可执行检查）

每个阶段结束前逐项检查。格式：`{check, rule, on_fail}`。不通过 → 退回重做，最多重试 2 次。

### 立案前 Guardrail

- [ ] `{check: "frontmatter 完整", rule: "case_id/case_type/parties/phase 非空", on_fail: "补充缺失字段"}`
- [ ] `{check: "每项诉请有对应法条", rule: "claims[*].legal_basis 非空", on_fail: "逐项标注法条依据"}`
- [ ] `{check: "每项诉请有对应证据", rule: "claims[*].evidence_ids 非空", on_fail: "逐项标注证据"}`
- [ ] `{check: "法条已核实现行有效", rule: "全部引用法条经 law-validation 确认", on_fail: "委派 law-validation 核实"}`
- [ ] `{check: "庭审模拟已执行", rule: "mock_trial.executed == true", on_fail: "委派 legal-mock-trial"}`
- [ ] `{check: "金额计算列明细", rule: "如有金额诉请，含本金+利率+起止日+公式", on_fail: "补充金额明细"}`
- [ ] `{check: "诉请无逻辑矛盾", rule: "claims 之间无冲突", on_fail: "修正矛盾诉请"}`
- [ ] `{check: "案件文件已创建", rule: "案件.md + 关联知识.md + todo.md 更新完成", on_fail: "补充创建"}`

### 审理中 Guardrail

- [ ] `{check: "Claim Chart 完成", rule: "每项请求权要件 → 对应证据 → 标记缺口", on_fail: "委派 legal-evidence"}`
- [ ] `{check: "不利事实分析完成", rule: "8 类不利事实识别 + 严重程度 + 应对策略", on_fail: "委派 legal-evidence"}`
- [ ] `{check: "五维风险评估完成", rule: "证据/法律/对方/执行/时间 逐维评分", on_fail: "委派 legal-evidence"}`
- [ ] `{check: "质证意见已准备", rule: "逐份证据三性意见（不得笼统说'均不认可'）", on_fail: "逐份补全"}`
- [ ] `{check: "庭审提纲已准备", rule: "法官追问清单 + 回答要点", on_fail: "补充庭审提纲"}`
- [ ] `{check: "庭前检查 9 项完成", rule: "phases/审理中.md 子阶段B 逐项打勾", on_fail: "逐项检查"}`

### 判决后 Guardrail

- [ ] `{check: "判决分析完整", rule: "认定事实 + 裁判理由 + 法律适用 三段提炼", on_fail: "补充分析"}`
- [ ] `{check: "上诉必要性评估", rule: "改判可能性 + 上诉成本 + 客户意愿", on_fail: "补充评估"}`
- [ ] `{check: "如上诉：上诉状已起草", rule: "决定上诉时上诉状非空", on_fail: "委派 legal-templates"}`
- [ ] `{check: "如不上诉：执行预备", rule: "财产线索排查清单已准备", on_fail: "补充排查清单"}`

### 执行中 Guardrail

- [ ] `{check: "财产线索排查", rule: "银行账户/房产/车辆/股权/应收账款 已排查", on_fail: "补充排查"}`
- [ ] `{check: "保全到期日检查", rule: "有保全则到期前提示续封", on_fail: "标记到期提醒"}`
- [ ] `{check: "执行时效核实", rule: "2 年从生效日起算，未过期", on_fail: "核实并提示"}`
- [ ] `{check: "执行申请书已起草", rule: "执行申请书非空", on_fail: "委派 legal-templates"}`

### 已结案 Guardrail

- [ ] `{check: "反思页面已创建", rule: "案件/wiki/反思/ 下有新页面", on_fail: "创建反思"}`
- [ ] `{check: "实务要点已提炼", rule: "可复用知识点已写入专题/实务要点/", on_fail: "提炼要点"}`
- [ ] `{check: "案件状态已更新", rule: "案件.md → 已结案, todo.md → 移除本案", on_fail: "更新状态"}`
- [ ] `{check: "log.md 已记录", rule: "结案操作已记录", on_fail: "补记 log"}`

---

## 六、知识库集成

### 6.1 一次检索，本地复用

案件受理时一次性检索，写入 `关联知识.md`，后续各阶段直接读该文件，不重复检索。

### 6.2 检索范围

| 来源 | 内容 | 匹配方式 |
|------|------|----------|
| `案件/wiki/专题/实务要点/` | 同案由实务要点 | 案由 + 关键词 |
| `案件/wiki/反思/` | 类似案件教训 | 案由匹配 |
| `案件/wiki/法规/` | 涉及的法条 | 争议焦点推断 |
| `案件/wiki/案件/诉讼/` | 同类案件结构 | 案由匹配 |

### 6.3 关联知识.md 格式

```markdown
## 相关实务要点
| 要点 | 来源 | 关联内容 |

## 相关法规
| 法规 | 条款核心 | 与本案关联 |

## 相关反思/教训
## 未覆盖的知识缺口
```

---

## 七、Obsidian 文件更新规则

### 7.1 强制流程

```
Step 1: obsidian read path="<路径>" vault="胖胖熊"
Step 2: 改好内容写入临时文件
Step 3: 分块写入（obsidian cli content= 约 4000 字节上限，按 ~35 行/块）：
        块1: obsidian create ... content="$(awk 'NR>=1 && NR<=35' <文件>)" overwrite silent
        sleep 1
        块2: obsidian append ... content="$(awk 'NR>=36 && NR<=70' <文件>)" silent
        ...
Step 4: rm -f 临时文件
```

**禁止：** 单次写入完整内容（超 4000 字节会静默失败）；用 Read/Write 工具直接操作 Obsidian 文件。

### 7.2 同步规则

| 操作 | 必须同步 |
|------|----------|
| 创建新 wiki 页面 | `index.md` + `log.md` |
| 更新案件阶段 | `todo.md` + `案件.md` frontmatter |
| 发现新法规引用 | 创建 `wiki/法规/{法条}.md` + 追加 `关联知识.md` |
| 阶段结束 | 写 `进展摘要.md` → 律师确认 |
| 用户说"记录一下" | 立即写进展摘要，不同步 todo，由律师决定 |

### 7.3 todo.md 同步

写操作前先读 todo.md（避免覆盖他人变更）。同一案件按 🔴 > 🟡 > 🟢 排序，已完成的移除。禁止删除其他案件条目。

---

## 八、Checkpoint（轻量断点）

每完成一个阶段，在 `案件.md` 的进展摘要末尾追加一条 checkpoint：

```markdown
<!-- checkpoint: 2026-07-18 立案前完成 -->
- 阶段: 立案前 → 审理中
- 关键产出: 起诉状、证据清单、庭审模拟报告
- CaseState 摘要: {claims: 3条, evidence: 5份, risks: {evidence: 3, legal: 2}}
```

恢复时读取最近一条 `<!-- checkpoint: ... -->` 注释，从中重建 CaseState。不新增 `.checkpoints/` 目录文件。

---

## 九、失败模式

| 场景 | 处理方式 |
|------|----------|
| 案件文件不存在 | 询问案件名，引导创建新案件 |
| 阶段字段缺失 | 默认立案前，提示用户补充 |
| 知识库未建立 | 按 Query 工作流检索，创建 `关联知识.md` |
| 多个进行中案件 | 展示列表，让用户指定 |
| 用户描述模糊 | 追问澄清，不猜测具体事实 |
| 法条引用不确定 | 委派 `law-validation` |
| Guardrail 不通过 | 退回重做，最多 2 次；2 次后交律师决策 |
| Obsidian 写操作失败 | 用 PowerShell Bash 直接操作文件 |
| 用户说"记录一下"或中断 | 立即写进展摘要 + checkpoint |

---

## 相关参考

- [[phases/立案前.md]] — 案件受理 + 立案准备
- [[phases/审理中.md]] — 举证与庭前 + 开庭
- [[phases/判决后.md]] — 裁判与上诉
- [[phases/执行中.md]] — 执行
- [[phases/已结案.md]] — 结案复盘
- [[assets/summary-template.md]] — 进展摘要模板
