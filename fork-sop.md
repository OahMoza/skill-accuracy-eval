# 从通用评测技能到业务专用评测技能 · SOP

> **读者**：智能体（评测方角色）。本文档是「把通用评测技能（skill-accuracy-eval）fork 成某业务专用评测技能」的**可执行操作手册**，也是后续迭代维护的事实基准。
> **配套**：通用内核定义见 `skills/skill-accuracy-eval/SKILL.md` §十二；验收门槛确认记录见 `skills/skill-accuracy-eval/assets/threshold-approval-template.md`；打分表见 `skills/skill-accuracy-eval/assets/score-sheet-template.md`；量化达标演示见 `cases/crm-retail/quantified-threshold-demo.md`；可视化见 `guides/fork-overview-graphic/`。
> **版本**：本文档随内核版本演进维护，每次改动在文末登记。

---

## 1. 定位与原则

专用评测技能 = **通用内核（禁改）+ 业务定制（可改）**。三条铁则：

1. **通用必须精简且有效**：内核是唯一事实源，不被任何业务的特殊性污染。
2. **分工固定**：业务专家**供资料**；评测方（智能体/改造者）**改造**；发起方**只使用**，不自建专用技能。
3. **结论可比**：所有业务分支共享同一套判定框架与铁律，只有验收门槛、场景、资料、措辞不同。

## 2. 角色分工

| 角色 | 做什么 | 不做什么 |
|---|---|---|
| 业务专家 | 提供业务规则 / 判断口径 / 输入输出要求 / 案例样本 / 字段字典 | 不写评测逻辑，不设验收门槛（只参与讨论） |
| 评测方（智能体） | fork、定制、验收门槛确认、构建用例与黄金集、试运行、交付、维护回流 | 不下「放行 / 回滚」裁决（那是人的决策） |
| 发起方 | 用专用技能评测自己的业务技能，按建议调整 | 不改专用技能本身 |

## 3. 输入清单（开工前收集，缺项要标注）

| 资料 | 用途 | 缺失影响 |
|---|---|---|
| 业务规则 / SOP / 政策文本 | 黄金集业务来源 | 无业务黄金集 → 仅契约一致性评测（禁判达标） |
| 判断口径（看哪些指标 / 条件 / 标准） | 黄金集条款与用例期望 | 用例无法判「对错」 |
| 输入要求 / 输出模板 | 用例输入与期望要点 | 结果正确性不可评 |
| 案例样本（常见 / 复杂 / 易错 / 优秀） | 场景样本集与黄金集（覆盖度按 3 大类 19 子类勾选） | 覆盖度不足 → 「覆盖不足、仅参考」 |
| 字段字典（真实语义字段与关系） | 资料自检与字段核实 | 发起方改错字段无法识别 |
| 运行环境说明（系统 / 接口 / 权限） | 版本锁定与执行方式 | 结论无法复现 |

## 4. 八步流程

### Step 0 · 确认需求与范围
- 确认：哪条业务、给谁用、评测对象（哪个业务技能）、结论给谁做什么决定。
- 确认是否强合规业务（决定是否启用「过程合规」维度，见 §6）。
- 产出：一句话目标 + 范围边界。

### Step 1 · fork 内核
- 复制通用内核（SKILL.md + references/ + assets/ 模板），**不改内核文件本身**。
- 在专用技能的 SKILL.md 头部声明：`base-kernel-version: <内核版本>`。
- 命名：业务化（如 `crm-retail-eval`），与内核同名文件区分。

### Step 2 · 收集并核实业务资料
- 按 §3 清单向业务专家收取资料；读取真实内容（读原文，不用文件名/摘要代替）。
- **字段字典核实**：发起方按总部的通用技能样例打样后常改错真实语义字段，改造前用字段字典逐项核对资料中的字段名与关系；核对不上的标「待确认」，不默认正确。
- 产出：资料清单（版本 + 来源），缺项明示。

### Step 3 · 定制（只动可定制项）
按 §5 清单逐项定制；**不可变条款一行不改**。产出：专用技能草稿。

### Step 4 · 验收门槛声明（线下多人讨论 + 确认记录）
- 验收门槛（分维度目标通过率）必须由业务专家 + 评测方 + 运营**线下讨论**确定，填 `threshold-approval-template.md`，**看评测结果前签认，失败后不得改口径**。
- 含特殊条款：如无法判定上限（上限默认 10%，占比 > 上限时降级）、阻断性一票否决、金额/权限字段零容忍。
- 无业务黄金集的场景：不做达标判定，声明「仅契约一致性评测」。

### Step 5 · 构建场景样本集与黄金集
- 场景样本集 ≥5 条：正常成功 / 边界（缺信息、异常输入）/ 反面（违规、越权请求）；每条用例 = `id / category / subcategory / input / expected_behavior（预期行为方向，非标准答案）/ difficulty`；样本阶段不生成标准答案。
- **覆盖度清单化**：业务场景逐项枚举 + **场景分类显式勾选（3 大类 19 子类：功能类 5 / 非功能类 5（含故障与降级兜底）/ 对抗类 9）**，**场景样本集与黄金集共用同一套分类** + 维度覆盖适用表（必测 / 观察 / 不适用，确认门冻结）；必测子类缺勾选且未声明不适用 → 对应维度降级「覆盖不足、仅参考」，观察项缺 → 仅提示。
- **黄金集按分类标注形态分化**：功能类 → 标准输出+依据；边界类 → 行为方向+边界判定依据；对抗类 → 按业务底线界定违规行为（阻断性）+ 拒绝理由充分性（质量观察项；不编造、忽略注入并继续授权任务等合法响应可按条款通过）。
- **专家点评**：每条黄金集附一句专家点评（解释评分尺度），帮助判定者校准，供报告引用。
- 黄金集**双源**：业务正确性条款只来自业务资料（不照抄技能步骤）；行为契约类可抽自技能自身声明（标「技能契约」）。
- 黄金集逐条指回来源，经业务方**书面确认**后锁定（补充资料 ≠ 确认，补后回到确认门）。

### Step 6 · 试运行与验收（复用 S0–S6 流程）
- **评测资产优先复用（v1.5）**：试运行 / 回归 / 改版对比前先查本业务是否已有锁定评测资产（场景样本集 + 黄金集）；有且覆盖本次评测 → 复用模式（加载锁定资产，跳过喂料与生成，确认门只核版本 + 用途）；无 → 生成模式（完整 S0，锁定后落盘为资产）；需补用例 → 增量模式（加载既有资产 + 只对新增/回填用例走确认）；资产只增不改，回填升级写入新版本（详见 `references/confirmation-gate.md`）。
- 按内核流程执行：确认门 → S1 锁定 → S2 执行（只采最终结果 + 关键行为结果 + 轨迹留痕）→ S3 判定（盲评）→ S4 汇总（通过率 + 达标判定 + 差距分类）→ S5 复核（AI 全量 + 人工抽审联动）→ S6 输出（报告头版本锁定 + 达标行 + 建议节）。
- 角色分离：执行者 / 判定者分设，存疑复核（核验者）等按需启用（子智能体；单 agent 则声明单人自评）；判定不看轨迹，轨迹仅防守性（存疑时证伪）。
- **不达标闭环**：评测技能输出评价报告 + 改进建议（不通过类型 → 建议模板 + AI 润色），**员工自行调整自己的业务技能**，调整后重评。
- **问题回填升级（黄金集自增值）**：评测中发现的问题用例 → 保留原输入 → 专家补标准输出 / 期望行为 + 判断依据 + 专家点评 → 升级为黄金用例 → 纳入回归；对抗类升级为安全回归用例（阻断性单列门禁）；升级后黄金集版本变更，旧结论按版本绑定失效。**前置条件：归因拆分（S3.5）判定为技能行为才允许回填；判定偏差先去改判定口径，不得直接回填（防基准污染）**。
- **稳定性观测（可选扩展，内核已默认多轮）**：S2 已对对抗 / 边界 / 存疑类默认跑 3 轮并折算多数一致（见内核 `references/execution-flow.md` S2「多轮执行与折算」）；本条为 fork 侧的更大规模扩展：多次运行（5 次 / 10+ 次）观察输出分布，结果作为 `可靠性` 维度参考；大规模评测业务可在 fork 时扩展「多次运行 + 通过@k 聚合 + LLM 异常检测」流水线（发起方自评场景不作通用要求）。

### Step 7 · 交付发起方 + 升级回流
- 交付专用技能 + 验收门槛确认记录 + 黄金集版本说明。
- 建立回流机制（见 §8）：内核升级出 diff → 分支应用 + 回归 → 评测方统一「合并上游」。

## 5. 不可变 vs 可定制（fork 边界）

| 类别 | 内容 | 规则 |
|---|---|---|
| **不可变（禁改）** | 三维度框架（结果正确性 / 规则与边界 / 可靠与兜底） | 判定结构不拆不改 |
| | 七条铁律（缺证从严、不裁决但必给建议、双源黄金集、分维度独立表达、样本边界、版本锁定、对比只改一类变量） | 逐条继承 |
| | 结果导向（评分只看最终结果，轨迹仅防守性） | 可否决、不可授分 |
| | 阻断性失败 → 整例不通过（一票否决） | 不被平均分抵消；多轮下**任一轮阻断性失败即不通过**（不适用多数一致） |
| | 评测数据流（黄金集流向红线） | 执行者只见用例 input + 被测技能本体；黄金集只进判定侧；执行者泄题即轮次作废 |
| **可定制（允许）** | 分维度验收门槛数值 | 多人讨论 + 确认记录（看结果前签认） |
| | 场景样本集·黄金集场景分类扩展 | 3 大类 19 子类基础上按业务增补 |
| | 黄金集来源与场景样本集 | 随业务更换；无业务黄金集 → 仅契约一致性 |
| | 报告措辞业务化 | 术语/表述可改，判定口径不改 |
| | 评测资产存放位置与命名 | 通用默认 `cases/<被测技能>/`（场景样本集 / 黄金集文件，即 `场景样本集-<版本>.md` + `黄金集-<版本>.md`，只增不改）；业务可改存放位置，资产复用 / 升级规则不变 |
| | 稳定性观测 / 聚合找异常（可选增强） | 内核已默认 S2 多轮（对抗/边界/存疑 3 轮冷启动）；fork 可调轮次数与批量/冷启动分档线，但**不得关闭对抗类多轮**；更大规模（多次运行 + 通过@k 聚合 + LLM 异常检测）发起方自评非通用要求 |
| **可选新增** | 「过程合规」专用维度 | 仅强合规业务；轨迹成为该维度正式判定输入 |

## 6. 强合规出口（可选专用维度）

强合规业务（金额 / 权限 / 隐私 / 法律状态）fork 时可加**「过程合规」专用维度**：

- 轨迹在该维度内成为**正式判定输入**（不再是防守性参考）；
- 判据必须**可枚举、可复核**（如「必须经用户明确确认才执行」）；
- 评测执行**强制轨迹留痕**：执行者保存轨迹文件 / 日志 / 产物（命名含用例编号），判定者分析；
- 该维度同样适用验收门槛声明与达标判定，阻断性失败一票否决。

## 7. 量化达标判定速查

| 项 | 规则 |
|---|---|
| 触发 | 确认门锁定过验收门槛声明（多人讨论 + 确认记录）；未声明 → 只出分数与证据 |
| 判定 | 逐维度 实测通过率 vs 验收门槛 → 达标 / 未达标 + 差距 |
| 阻断性 | 任一阻断性失败 → 该维度未达标 |
| 防稀释 | 无法判定占比 > 声明上限（上限默认 10%）→ 降级「覆盖不足、仅参考」 |
| 禁判 | 无业务黄金集维度 → 禁判（仅契约一致性，报告头尾声明边界） |
| 差距分类 | 不通过归集到 维度 × 场景分类 × 黄金集条款 |
| 建议 | 不通过类型 → 建议模板 + AI 润色；不下放行 / 回滚裁决 |
| 版本绑定 | 报告头 4 字段（业务资料 / 黄金集 / 运行环境 / 结论有效期）；任一变更旧结论失效 |
| 抽审联动 | 未达标全审 / 擦线（<5%）≥50% / 余量足默认 ≥20% |

## 8. 升级回流（内核 → 各分支）

1. 内核升级：通用技能版本变化 → 产出改动 **diff**；
2. 分支应用：各业务专用技能应用 diff（保持自身定制不变）；
3. 回归：跑该业务的既有场景样本集，确认定制未破坏、新能力已获得；
4. 合并上游：由评测方统一执行，防分支碎片化；各分支 `base-kernel-version` 同步更新；
5. 版本追溯：报告头版本字段记录内核版本 + 分支版本。

## 9. 交付前自检清单

- [ ] 不可变条款逐条未改（三维度 / 七铁律 / 结果导向 / 阻断性一票否决）
- [ ] `base-kernel-version` 已声明
- [ ] 业务资料来自专家，缺项已明示；字段字典核对记录已附
- [ ] 验收门槛：多人讨论 + 确认记录 + 冻结声明（看结果前签认）
- [ ] 场景样本集 ≥5，覆盖度清单（业务场景 + 3 大类 19 子类场景分类）已勾选（场景样本集与黄金集共用），缺类已标注
- [ ] 黄金集双源：业务条款指回业务资料，业务方书面确认
- [ ] 无业务黄金集 → 已声明「仅契约一致性」，禁判达标
- [ ] 报告头 4 字段版本锁定；结论含样本边界说明
- [ ] 强合规业务：已加「过程合规」维度，判据可枚举，轨迹留痕
- [ ] 未达标已给改进建议（不裁决）；回流机制已建立

## 10. 版本与维护约定

- 本文档与内核版本同步维护；任何 fork 边界、流程或模板变更须在此登记并同步到对应模板文件。

| 日期 | 版本 | 变更摘要 | 关联文件 |
|---|---|---|---|
| 2026-10-10 | v1.5.13 | 仓库结构调整（对齐 Agent Skills 标准）：skill 本体移入 `skills/skill-accuracy-eval/`（SKILL.md + references + assets），给人看的指南与可视化移入仓库根 `guides/`（usage-playbook / usage-coach / fork-overview-graphic），sop-overview-graphic 保留在 skill assets（与 sop-overview 速查配套）；install.js 指向新路径、package.json files 白名单改为 skills、check_regression.py 路径与 name 校验同步；判定口径、数字、机制不变 | SKILL.md、package.json、install.js、fork-sop.md、README.md、docs/maintenance.md、scripts/check_regression.py、guides/、skills/ |
| 2026-10-10 | v1.5.12 | 使用剧本与资产复用增强：新增 assets/usage-playbook.md（13 轮完整对话 + 9 个分叉点，与演示样例分工——样例看产物、剧本看对话）；复用模式明确「手上有资产文件即上传复用」+ 复用/重生成「判别一句」；复用确认新增接口契约变化判据（入参调整判据）与原黄金集确认记录随附要求；锁定即落盘为必做步骤（未落盘=未锁定）；score-sheet 复核清单定位 S5 工作待办 + 新增落盘检查项，报告模板 §七改为已完成复核记录 | SKILL.md、package.json、fork-sop.md、README.md、references/confirmation-gate.md、references/execution-flow.md、assets/usage-playbook.md、assets/score-sheet-template.md、assets/three-piece-sample.md、assets/evaluation-report-template.md、assets/sop-overview-graphic/terms-and-docs.html |
| 2026-10-10 | v1.5.11 | 产物形态分层：执行期 md / 交付期 doc·xlsx；三类签认记录（黄金集确认 / 复用确认 / 验收门槛）统一 doc；交付态由 agent 按 md 模板现场生成，二进制不进仓库 | SKILL.md、package.json、fork-sop.md、docs/maintenance.md、README.md、assets/examples/crm-retail/README.md、assets/sop-overview.md、assets/sop-overview-graphic/terms-and-docs.html |
| 2026-10-10 | v1.5.10 | 第二轮全项目润色：演示样例与案例（examples / cases）纳入引号「」统一与装饰性 em dash 清理；v1.5.7–1.5.9 新增文字补齐直角引号与常规标点（修正「卖的是成本」→「付的是成本」、删「换言之」过渡词）；HTML 速查页文本节点引号统一（PNG 内容未变不重渲）；direction-approved 决策留痕按原样保留；判定口径、数字、机制与章节编号不变 | SKILL.md、package.json、fork-sop.md、docs/maintenance.md、references/execution-flow.md、references/evaluation-framework.md、assets/evaluation-report-template.md、assets/examples/crm-retail/、assets/sop-overview.md、assets/sop-overview-graphic/sop-overview.html、assets/sop-overview-graphic/terms-and-docs.html、cases/crm-retail/ |
| 2026-10-10 | v1.5.9 | 评测数据流与多轮机制：黄金集流向红线（执行者 S2 只见用例 input + 被测技能本体，黄金集只进判定侧 S3/S4/S6）；执行者按风险分层分配（正常成功可批量 / 对抗边界每例冷启动）；S2 默认多轮（对抗 / 边界 / 存疑 3 轮冷启动、多数一致折算，任一轮阻断性失败即不通过；泄题轮作废不计配额），折算后的单条判定才进 S4；对比轮次一致性（铁律 7 扩展适用） | SKILL.md、references/execution-flow.md、references/evaluation-framework.md、references/gotchas.md、docs/maintenance.md、assets/sop-overview.md、assets/sop-overview-graphic/、fork-sop.md |
| 2026-10-10 | v1.5.8 | 常见错误新增 3 条红线（16 → 19 条）：① 执行者（S2）泄题——提示词出现「预期 / 应该 / 正确表现 / expected_behavior」或把黄金集（含期望行为）交给执行者，等于开卷考试、全过必然且无意义；② 契约一致性评测（无业务黄金集）口头拒绝类用例缺外部锚点应记「无法判定」而非通过；③ 全过 = 告警信号，无外部证据须补样本或回查泄题 | references/gotchas.md、SKILL.md、README.md、assets/sop-overview-graphic/terms-and-docs.html |
| 2026-10-10 | v1.5.7 | 评测角色体系分层：常驻角色（执行者 / 判定者 / 人工）+ 可选触发动作（存疑复核 / AI 全量复核 / 多视角，按触发条件启用、不占常驻席位）+ 干系人表（发起方 / 业务方 / 被测方 / 业务专家 / 运营）；角色分离强度对齐——多主体硬约束、单 agent 降级纪律，消除「硬约束」与单人降级声明的措辞矛盾；多视角专家改述「记录分歧、喂人工抽审」，删去一致性暗示；名字全保留（业务方 / 复核者不动） | SKILL.md、assets/sop-overview.md、assets/sop-overview-graphic/terms-and-docs.html、references/evaluation-framework.md、references/execution-flow.md、docs/maintenance.md |
| 2026-10-10 | v1.5.6 | 文档润色与结构整理：全库中文引号统一「」（直/弯引号转直角引号，代码块与版本历史行除外）；装饰性 em dash 分句改常规标点（输出串字面量「禁判——无业务黄金集」保留）；术语统一（硬纪律 → 铁律、铁律③ → 铁律 3、何时用 → 何时使用）；evaluation-framework 修复断裂引用块、收紧 §4.2 模板与列表冗余空行；判定口径、数字、机制与章节编号不变 | SKILL.md、README.md、package.json、fork-sop.md、references/evaluation-framework.md、references/execution-flow.md、references/confirmation-gate.md、references/input-check.md、references/gotchas.md、assets/sop-overview.md、assets/three-piece-sample.md、assets/score-sheet-template.md、assets/threshold-approval-template.md、assets/sop-overview-graphic/terms-and-docs.html（版本串同步） |
| 2026-10-10 | v1.5.5 | 19 子类英文标识全面中文化：子类统一用中文名（正常路径 / 负向路径 / 边界情况 / 集成 / 状态上下文 / 性能 / Token 经济性 / 可靠性 / 质量 / 故障与降级 / 提示注入 / 越狱 / 数据外泄 / PII 泄露 / 有害内容 / 幻觉 / 劫持 / 策略违规 / 技术注入），用例表 / 覆盖勾选 / 评测报告 / 维度覆盖适用表不再出现英文子类标识（字段名 id / category / subcategory 保持英文）；归因枚举中文化（skill_behavior / judge_bias / unknown → 技能行为 / 判定偏差 / 无法归因） | references/evaluation-framework.md、references/execution-flow.md、references/confirmation-gate.md、assets/three-piece-sample.md、assets/score-sheet-template.md、assets/sop-overview.md、assets/examples/crm-retail/、assets/sop-overview-graphic/、README.md、cases/crm-retail/quantified-threshold-demo.md、fork-sop.md、SKILL.md、package.json |
| 2026-10-10 | v1.5.4 | 被测版本定号：无版本标注不再卡死评测——确认门定号（被测方给号优先，否则评测暂定版本，默认 1.0.0 + 来源标注 + 快照标识），铁律 6 由\"要求先补\"改为\"未定号不产结论\"；模板增版本来源字段 | SKILL.md、references/confirmation-gate.md、references/input-check.md、references/evaluation-framework.md、references/execution-flow.md、assets/score-sheet-template.md、assets/three-piece-sample.md、assets/threshold-approval-template.md、assets/sop-overview.md、assets/sop-overview-graphic/、README.md、package.json、fork-sop.md |
| 2026-10-10 | v1.5.3 | 仓库维护：轻量可复现回归检查入口（scripts/check_regression.py：真实 PyYAML frontmatter / 三处版本同步 / md 表格列数 / CRM 逐例对账 / 安装器 5 组假 fs 边界 / 文件与章节引用存在性，+ --selftest 篡改临时副本自检；npm run check）；重复治理最小化（framework §3.5 角色表与 §4.4 确认门段改引用事实源；sop-overview 与 terms-and-docs 标注速查摘要与权威源映射）；README 仓库维护用法与检查限度；docs/maintenance.md 事实源治理 | scripts/check_regression.py、scripts/check_installer.js、package.json、README.md、docs/maintenance.md、SKILL.md、references/evaluation-framework.md、references/confirmation-gate.md、assets/examples/crm-retail/evaluation-report.md、assets/sop-overview.md、assets/sop-overview-graphic/terms-and-docs.html、fork-sop.md |
| 2026-10-09 | v1.5.2 | 独立审核修复（两轮）：过程断言独立证据与缺证口径 + 教学示例模拟事实假设声明；示例计数与差距分类按失败用例重算 + 复跑统计勘误贯通；覆盖降级统一口径（维度覆盖适用表：必测/观察/不适用 + 数值比较/阻断结果/覆盖状态三字段）；对抗响应按业务底线界定全量同步；区分资产兼容复用与运行重评；模板列数与种子示例补齐；install.js 空参数与 flag 守卫并存；gotchas 总数与版本历史对齐；演示声明限定为模拟判定教学示例 | SKILL.md、README.md、package.json、references/evaluation-framework.md、references/execution-flow.md、references/confirmation-gate.md、references/gotchas.md、assets/three-piece-sample.md、assets/sop-overview.md、assets/score-sheet-template.md、assets/threshold-approval-template.md、assets/examples/crm-retail/README.md、assets/examples/crm-retail/three-piece.md、assets/examples/crm-retail/evaluation-report.md、assets/sop-overview-graphic/terms-and-docs.html、cases/crm-retail/quantified-threshold-demo.md、cases/crm-retail/re-run-2026-09-28.md、install.js、fork-sop.md |
| 2026-10-09 | v1.5.1 | 审计修复：文档头 version 移入 metadata.version；confirmation-gate 悬空引用修正（§7.1→§八）；演示样例版本矛盾统一 v1.5；quantified-threshold-demo 术语迁移（黄金集/阻断性/无法判定/验收门槛）；README cases 归属表述统一 + 目录树补列；terms-and-docs.html 挂引用 + 「一线」残留清除；install.js --dir 缺参守卫；退役 cases/crm-retail 两个 v1.4 旧副本（evaluation-report.md / three-piece-crm.md，被 assets/examples/crm-retail/ 取代） | SKILL.md、README.md、references/confirmation-gate.md、assets/examples/crm-retail/evaluation-report.md、cases/crm-retail/quantified-threshold-demo.md、cases/crm-retail/re-run-2026-09-28.md、assets/sop-overview.md、assets/sop-overview-graphic/terms-and-docs.html、install.js、package.json、fork-sop.md |
| 2026-10-09 | v1.5 | 评测资产落盘与复用：S0 资产查找前置（复用 / 生成 / 增量三模式）+ 复用确认变体 + 资产只增不改；SKILL.md 治理拆分（资料自检 → input-check.md、确认门 → confirmation-gate.md、执行细则 → execution-flow.md、常见错误 → gotchas.md）；术语统一（金标准 → 黄金集；样本集 / 用例集 → 场景样本集；blocking → 阻断性；一线 → 发起方；门槛 → 验收门槛）；术语与业务侧对齐；喂料清单映射被测技能六要素；S6 决策衔接；对外文档术语中文化 | SKILL.md §3.0/§3.3、references/input-check.md、references/confirmation-gate.md、references/execution-flow.md、references/gotchas.md |
| 2026-10-08 | v1.4 | 归因拆分防基准污染（skill_behavior / judge_bias / unknown）+ 覆盖盲区提示 + 样本量分级措辞 + 稳定性观测可选增强 | SKILL.md §S3.5/S6/§八、evaluation-framework.md §6.2/§7.1、score-sheet-template.md |
| 2026-10-08 | v1.3 | 黄金集自增值闭环：用例字段显式化（category/subcategory/difficulty/expected_behavior）+ 专家点评要素 + 问题用例回填升级纳入回归 | SKILL.md §3.2/§8、evaluation-framework.md §4.4/§7.1 |
| 2026-10-08 | v1.2 | 黄金集分类标注形态：期望答案随场景分类分化（功能=标准输出+依据 / 边界=行为方向 / 对抗=必须拒绝+理由充分性） | SKILL.md §3.2、evaluation-framework.md §4.4/§6.3、score-sheet-template.md |
| 2026-10-08 | v1.1 | 覆盖度标准升级：场景样本集 / 黄金集统一场景分类（3 大类 19 子类，含故障与降级兜底），替代原六类对抗场景 | SKILL.md §3.2/§十二、evaluation-framework.md §6.3/§9 |
| 2026-10-08 | v1 | 初版：fork SOP（八步流程 / fork 边界 / 强合规出口 / 量化达标 / 回流） | SKILL.md §十二、threshold-approval-template.md、quantified-threshold-demo.md |
