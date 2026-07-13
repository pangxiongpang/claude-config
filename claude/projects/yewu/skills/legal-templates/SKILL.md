---
name: 法律文书模板库
description: 起诉状/答辩状/代理词/仲裁申请书/律师函/法律意见书等文书模板，按需调用
---

# 法律文书模板库

按需调用的文书模板集合。由 `legal-pre-trial` 等流程 skill 在需要时调用，也可独立使用。

## 触发方式

| 命令 | 行为 |
|------|------|
| `/legal templates 起诉状` | 调用起诉状模板 |
| `/legal templates 答辩状` | 调用答辩状模板 |
| `/legal templates 代理词` | 调用代理词模板 |
| `/legal templates 仲裁申请书` | 调用仲裁申请书模板 |
| `/legal templates 律师函` | 调用律师函模板 |
| `/legal templates 法律意见书` | 调用法律意见书模板 |
| `/legal templates 上诉状` | 调用上诉状模板 |
| `/legal templates 再审申请书` | 调用再审申请书模板 |
| `/legal templates 反诉状` | 调用反诉状模板 |

## 模板索引

| 模板 | 文件 | 说明 |
|------|------|------|
| 起诉状 | `civil-complaint.md` | 三段式结构+违约金四要素+排版规范 |
| 答辩状 | `civil-answer.md` | 答辩意见前置+论证分层+禁忌 |
| 代理词 | `defense-statement.md` | 审判长审判员格式+落款规范 |
| 仲裁申请书 | `arbitration.md` | 术语转换规则 |
| 律师函 | `demand-letter.md` | 编号+委托声明+事实+法律依据+要求+后果 |
| 法律意见书 | `legal-opinion.md` | 出具依据+事实+法律分析+结论 |
| 上诉状 | `appeal.md` | 公文格式+撤销/改判范围 |
| 再审申请书 | `re-trial.md` | 五步法 |
| 反诉状 | `counterclaim.md` | 当事人标注+标的合计 |

## 通用排版规范

- 标题：宋体加粗二号居中
- 正文：仿宋小三号
- 行距：28磅，段前段后0
- 首行缩进：2字符

## 注意事项

- 模板为初稿框架，需根据具体案件调整
- 法条引用需核实是否现行有效（调用 `law-validation`）
- 当事人信息需脱敏处理
- 所有文书需经执业律师审核后正式使用
