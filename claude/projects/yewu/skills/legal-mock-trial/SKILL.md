---
name: legal-mock-trial
description: >-
  庭审模拟对抗推演。3 个并行 Agent（对方律师+法官+判决预判师）模拟对抗，发现弱点、查漏补缺。
  触发：模拟庭审、对抗推演、预演、庭前准备。可独立调用，也可由 legal-litigation-skill 自动触发。
license: MIT
metadata:
  author: 熊淏晨（上海市海华永泰（泰州）律师事务所）
  version: 2.0.0
  created: 2026-06-30
  last_reviewed: 2026-07-18
  review_interval_days: 90
---

# /legal-mock-trial — 庭审模拟对抗推演

在正式开庭前，启动 3 个并行 Agent 模拟对抗，发现我方弱点、调整策略。

**重要提示：** 本 skill 不提供法律建议，提供对抗推演框架。所有输出仍需专业律师审核。

---

## 一、结构化输入

调用方（通常是 `legal-litigation-skill`）提供以下结构化上下文：

```yaml
mock_trial_input:
  case_info:
    case_cause: "案由"
    case_type: "确认之诉 | 给付之诉 | 形成之诉"
    our_role: "原告 | 被告"

  pleading:
    claims:             # 诉讼请求列表
      - content: ""
        legal_basis: []
    facts:              # 主张的关键事实
      - fact: ""
        evidence_id: ""

  evidence:
    our_evidence:       # 我方证据
      - name: ""
        purpose: ""
    opponent_evidence:  # 对方证据（如有）
      - name: ""

  strategy:
    key_arguments: []       # 核心论点
    anticipated_defenses: [] # 预判对方抗辩
    known_weaknesses: []     # 已知弱点（自评）

  previous_mock_trial_id: "" # 可选：引用前次模拟做对比
```

---

## 二、Agent 1 — 对方律师

```yaml
agent: opposing_counsel
backstory: >
  你是一名执业 20 年的商事诉讼律师，以攻击犀利、逻辑严密著称。
  你代理过 200+ 件类似案件，深知法官的裁判思维和对方律师的常见漏洞。
  你从不留情面——每一个事实陈述、每一份证据、每一条法律适用，
  你都会从最刁钻的角度提出质疑。你的委托人指望你赢，你不能让他们失望。
  请尽最大努力攻击我方的每一个主张，不要客气。
attack_dimensions:
  1. 证据攻击 — 逐份质疑我方证据的三性（真实性、合法性、关联性）
  2. 法律适用攻击 — 指出我方法律适用的错误或不利解释
  3. 事实逻辑攻击 — 指出我方事实主张中的逻辑漏洞和矛盾
  4. 程序攻击 — 指出程序瑕疵（举证期限、诉讼时效、主体资格等）
  5. 新增抗辩 — 提出我方未预想到的抗辩理由
output_schema: AttackReport
```

**输出 Schema：**

```yaml
AttackReport:
  attacks:
    - id: 1
      category: "证据攻击 | 法律适用 | 事实逻辑 | 程序 | 新增抗辩"
      target: "被攻击的主张/证据"
      argument: "具体攻击论述"
      severity: "🔴 高 | 🟡 中 | 🟢 低"
      likely_to_succeed: "非常可能 | 可能 | 不太可能"
      judge_attention: "高 | 中 | 低"
      our_countermeasure: "我方如何反驳"
  summary:
    total_attacks: 0
    high_severity_count: 0
    top_3_threats:
      - id: 0
        reason: "为什么是最危险的攻击"
```

---

## 三、Agent 2 — 法官

```yaml
agent: judge
backstory: >
  你是一名在民商事审判庭工作了 15 年的员额法官，年均结案 300+ 件。
  你对证据审查极严——任何没有原件/其他证据印证的单一证据，
  你都不会轻易采信。你最反感律师在法庭上"讲故事"而不是"摆证据"。
  你会在庭前仔细阅卷，列出所有需要当庭查明的问题。
  你的发问不是走过场——每一个问题都是为了填补心证缺口。
question_dimensions:
  1. 程序性问题 — 管辖、主体资格、诉讼请求是否明确
  2. 事实查明问题 — 关键事实的时间、地点、经过、原因
  3. 证据关联问题 — 某份证据与待证事实的关系
  4. 法律适用问题 — 为何适用某法条、如何理解某概念
  5. 释明问题 — 法官可能释明变更诉讼请求或补充证据
output_schema: JudgeQuestionList
```

**输出 Schema：**

```yaml
JudgeQuestionList:
  questions:
    - id: 1
      category: "程序 | 事实查明 | 证据 | 法律适用 | 释明"
      question: "法官可能问的问题"
      suggested_answer: "建议回答要点"
      trap_warning: "回答时的陷阱/注意事项"
      importance: "🔴 critical | 🟡 important | 🟢 normal"
  pre_trial_concerns:
    - "法官阅卷后最可能关注的疑点"
  missing_preparation:
    - "我方尚未准备充分但法官可能追问的点"
```

---

## 四、Agent 3 — 判决预判师

```yaml
agent: verdict_predictor
backstory: >
  你是一名退休的高级法官，曾在省高院担任审判长 10 年。
  你审理过数千件各类案件，对裁判尺度有精准的把握。
  你不偏袒任何一方——你只认事实和法律。
  你能看穿律师的诉讼技巧，直击案件的本质争议。
  你知道同类案件在不同法院、不同法官手中的裁判倾向差异。
  你预判的结果不是"希望"，而是基于经验数据的最可能结果。
analysis_dimensions:
  1. 胜诉概率 — 三种情景分析（乐观/中性/悲观）
  2. 裁判思路 — 法官最可能的法律适用和逻辑
  3. 判决结果 — 全部支持 / 部分支持 / 驳回
  4. 关键因素 — 影响判决的核心要素
  5. 调解可行性 — 仅给付之诉讨论；确认之诉/形成之诉注明不适用
output_schema: VerdictPrediction
```

**输出 Schema：**

```yaml
VerdictPrediction:
  case_summary:
    case_type: "确认之诉 | 给付之诉 | 形成之诉"  # 必填
    our_role: "原告 | 被告"
  scenarios:
    optimistic:
      win_probability: "百分比"
      likely_outcome: "描述"
      conditions: ["需要满足的条件"]
    neutral:
      win_probability: "百分比"
      likely_outcome: "描述"
    pessimistic:
      win_probability: "百分比"
      likely_outcome: "描述"
  key_factors:
    - factor: "因素名"
      impact: "有利 | 不利 | 中性"
      weight: "高 | 中 | 低"
      controllable: true | false
  mediation:                    # 确认之诉/形成之诉自动输出 "不适用"
    applicable: true | false
    recommended: true | false
    suggested_terms: ""
    bottom_line: ""
  overall_assessment:
    recommended_strategy: "诉讼 | 调解 | 和解"
    confidence_level: "高 | 中 | 低"
```

---

## 五、自动 Merge 规则

三个 Agent 并行完成后，按以下规则自动合并：

```yaml
merge_rules:
  step_1_cross_analysis:
    # 对方攻击 ∩ 法官关注 → 高风险点
    high_risk: "attacks where judge_attention == '高' OR target in judge.concerns"
  
  step_2_blind_spot:
    # 法官关注 - 我方准备 → 盲区
    blind_spots: "judge.concerns + judge.missing_preparation NOT in strategy.key_arguments"
  
  step_3_priority:
    sort_by: ["severity", "controllable == false"]
    top_n: 5
  
  step_4_delta:
    # 如有前次模拟：哪些弱点已修复、哪些仍在、新增了哪些
    if previous_mock_trial_id:
      fixed: "前次 top_weaknesses - 本次 top_weaknesses"
      persistent: "前次 top_weaknesses ∩ 本次 top_weaknesses"
      new: "本次 top_weaknesses - 前次 top_weaknesses"
```

---

## 六、输出 Guardrail

三个 Agent 完成后逐项检查，不通过则退回对应 Agent 重做（最多 2 次）：

- [ ] `{check: "至少发现 3 个攻击点", rule: "len(attacks) >= 3", on_fail: "返回 Agent 1 深入分析"}`
- [ ] `{check: "至少 1 个高严重度攻击", rule: "high_severity_count >= 1", on_fail: "返回 Agent 1 加强攻击力度"}`
- [ ] `{check: "法官发问覆盖 5 个维度", rule: "questions 中 5 个 category 各至少 1 条", on_fail: "返回 Agent 2 补充缺失维度"}`
- [ ] `{check: "预判含三种情景", rule: "optimistic + neutral + pessimistic 均有", on_fail: "返回 Agent 3 补充情景"}`
- [ ] `{check: "确认/形成之诉无调解", rule: "case_type 为确认或形成时 mediation.applicable == false", on_fail: "自动剔除调解内容（硬规则）"}`
- [ ] `{check: "胜诉概率量化", rule: "win_probability 为具体百分比而非模糊描述", on_fail: "返回 Agent 3 量化"}`

---

## 七、汇总输出

Guardrail 全部通过后，生成综合报告写入 Obsidian `案件/{案件名}/庭审模拟报告.md`：

**报告结构：**
1. **案件概况** — 案由、我方角色、诉讼类型
2. **交叉分析** — 高风险点（对方攻击 ∩ 法官关注）
3. **盲区识别** — 我方未准备但法官可能追问的点
4. **判决预判** — 三种情景胜诉概率 + 关键因素
5. **策略调整建议** — 基于模拟结果的攻防调整
6. **优先级排序** — 最需要优先解决的 Top 5 问题
7. **⚠️ 调解核查** — 确认之诉/形成之诉不得含调解建议（即使 Agent 3 输出了也必须剔除）
8. **对比分析**（如有前次模拟）— 已修复 / 仍存在 / 新发现的弱点

同步更新 `办案思路.md` 中的攻防要点。
