# 演示样例 · CRM 零售客服技能评测（真实案例）

> 本目录是 `skill-accuracy-eval` 的**完整演示样例**：一个用真实公开测试集（τ²-bench retail）跑通的评测全过程。
> 用途：一线/执行 agent 第一次用本 Skill 时，照这份样例即可理解"喂料 → 三件套 → 确认 → 执行 → 判定 → 汇总 → 报告"每一步长什么样。

## 文件清单

| 文件 | 内容 | 对应 skill 步骤 |
|---|---|---|
| `three-piece.md` | 三件套：被测版本 / 6 个真实用例 / 金标准（逐条带来源） | S0 生成 + S1 锁定 |
| `evaluation-report.md` | 逐用例判定表 + 维度汇总 + 结论 + 复核清单 | S2–S6 |

## 这是什么案例

- 被测对象：**retail-crm-service v1.0**（CRM 零售客服技能，行为 = τ²-bench retail 官方 policy）
- 测试集：τ²-bench retail 真实任务（GitHub `sierra-research/tau2-bench` → `data/tau2/domains/retail/`，policy.md + tasks.json）
- 用例：6 条真实用户场景（任务 0/2/3/5/10/12），覆盖正常 / 边界 / 反面
- 执行方式：模拟运行（本环境无真实零售数据库），结果导向判定只看最终结果

## 怎么照着做（对执行 agent）

1. 先读 `three-piece.md`：理解三件套怎么从资料里来、金标准怎么带来源。
2. 再读 `evaluation-report.md`：理解判定怎么落（每条 fail 引用金标准条款）、汇总怎么算（not_evaluated 单列）、结论怎么措辞（样本边界）。
3. 遇到新的被测技能时：按 S0 喂入对方资料 → 生成三件套草稿 → 给一线确认 → 锁定 → 执行 → 判定 → 汇总 → 报告。

## 关键演示点（本样例刻意展示的）

- **结果导向**：判定只依据"最终输出 + 关键行为结果"，全程无轨迹分析。
- **fail-closed**：判定不了就 not_evaluated，不猜 pass。
- **blocking 生效**：crm-01/05/06 因规则边界 blocking fail 直接判整例 fail。
- **金标准可指回来源**：每条都落在 policy 条款或任务真实标注上。
- **诚实声明执行方式**：模拟运行在报告中明示，正式结论需真实环境回填。
