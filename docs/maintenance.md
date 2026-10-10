# 仓库维护说明

> 面向维护者。检查工具仅用于维护本仓库，使用 Skill 无需运行检查，也无需安装这些维护依赖。`package.json` 的 `files` 白名单不含 `scripts/` 与 `docs/`，检查脚本与维护说明不随技能包分发。

## 回归检查

```bash
npm run check                          # 等价：python scripts/check_regression.py
python scripts/check_regression.py --selftest   # 自检：篡改临时副本证明能捕捉回归
```

- 依赖（维护者自备，不自动安装）：Python 3.8+、PyYAML（`pip install pyyaml`）、Node ≥ 14。
- 覆盖五项：① frontmatter 真实 YAML 解析 / name-description schema / 三处版本同步；② markdown 表格列数（忽略代码围栏与转义竖线）；③ CRM 逐例三维度重算与报告汇总 / 量化演示 / 复跑勘误对账；④ 安装器 5 组边界（Node vm 假 fs：缺参 / 空串 / 空白 / flag / 合法路径，不真实安装）；⑤ 文件与章节引用存在性（真实解析引用目标）。
- 自检在 `tempfile` 临时目录副本上故意篡改示例汇总数 / 模板列 / 安装守卫，验证三项关键回归均被捕捉；不改真实文件、不提交临时目录。
- 限度：**文本级回归检查，不是语义审计，也不是正式评测的替代**；评分政策变更、判定口径修订仍需人工复核。

## 事实源治理（最小规则）

改动进事实源；复制版只同步摘要与条数，**不整段复制**；速查页须标注「摘要 + 权威源」。

| 主题 | 事实源 | 复制版（改动须同步） |
|---|---|---|
| 评测角色体系（分层角色表：常驻 / 可选触发 / 干系人 + 分离强度） | `SKILL.md` §五 | `assets/sop-overview.md`、`assets/sop-overview-graphic/terms-and-docs.html`（速查摘要） |
| 确认门完整动作 / 评测资产落盘复用 | `references/confirmation-gate.md` | `references/evaluation-framework.md` §4.4（仅摘要+引用）、HTML 速查 |
| 判定细则 / 覆盖口径 / 黄金集规范 / 汇总达标 | `references/evaluation-framework.md` | `SKILL.md` 要点行、`assets/sop-overview.md`、HTML |
| S1–S6 执行细则 / 对比与回填 | `references/execution-flow.md` | `assets/sop-overview.md`、HTML |
| 资料自检 9 项 | `references/input-check.md` | `assets/three-piece-sample.md` §〇、HTML |
| 常见错误条目 | `references/gotchas.md` | `SKILL.md` §十（仅条数）、HTML gotchas 列表（同步条数与措辞） |
| fork 治理 / 版本登记表 | `fork-sop.md` | `SKILL.md` §十二要点、HTML |
| 演示样例数字 | `assets/examples/crm-retail/evaluation-report.md` 逐例判定 | 汇总表、`cases/crm-retail/quantified-threshold-demo.md`、`cases/crm-retail/re-run-2026-09-28.md`（勘误口径） |

## 版本同步约定

三处一致，任一变更三处同改：`SKILL.md` `metadata.version` = `package.json` `version` = `fork-sop.md` 版本表首行；`terms-and-docs.html` 页内 kicker / 页脚 / 版本历史表同步当前版本。检查入口第 ① 项自动核对。
