# skill-accuracy-eval

**结果导向的技能准确性评测**（临时替代品）：评测一个技能的准确性，评分只看最终结果，轨迹仅防守性参考（存疑时核验对账，只可否决、不可授分）。

- 发起方喂入业务资料（技能说明 / 业务规则 / 用户问题样例 / 禁止行为）→ 自动生成「被测版本 / 场景样本集 / 黄金集」三件套草稿 → 确认后执行评测；**已有评测资产（场景样本集 / 黄金集）时自动复用，不重复生成**（改版对比 / 回归同场景样本集，省 token 且防用例漂移）。
- 按「结果正确性 / 规则与边界 / 可靠与兜底」三维度逐条判定 `通过 / 不通过 / 无法判定`，不下放行 / 回滚裁决（那是人的决策），但必给改进建议（不通过类型 → 建议模板 + AI 润色）。
- 可事前声明分维度验收门槛（线下多人讨论 + 确认记录）→ 输出达标判定（实测 vs 验收门槛 → 达标 / 未达标 + 差距）+ 差距分类 + 改进建议；报告头锁定业务资料版本 / 黄金集版本 / 运行环境 / 结论有效期。
- 覆盖度按 **3 大类 19 子类**统一勾选（场景样本集与黄金集共用）；黄金集按分类标注形态分化（功能=标准输出 / 边界=行为方向 / 对抗=按业务底线界定违规行为+拒绝理由充分性），每条附专家点评；问题用例回填升级黄金集纳入回归（**归因拆分**防基准污染：skill_behavior 才可回填，judge_bias 先改判定口径）。
- 完全自包含：不依赖任何评测平台、执行引擎或日志系统。SKILL.md 为标准文档头格式（name + description），支持 Agent Skills 的智能体均可直接识别。

> 定位：在发起方暂不具备正式评测平台时使用；不取代正式评测实现。

## 快速开始（官方 npx skills 安装）

推荐使用 **Vercel 官方 CLI `npx skills`**安装——它支持交互式选择技能、智能体平台、全局/项目作用域、复制/软链安装方式：

```bash
# 交互式安装：选技能 → 选平台 → 选全局/项目 → 选 Symlink 或 Copy
npx skills add OahMoza/skill-accuracy-eval

# 非交互：全局安装到指定平台
npx skills add OahMoza/skill-accuracy-eval -g -a claude-code -a opencode -y

# 复制模式（不建软链）
npx skills add OahMoza/skill-accuracy-eval --copy

# 先看仓库里有哪些技能
npx skills add OahMoza/skill-accuracy-eval --list
```

**官方能力对照**（`npx skills` 已内置，无需自建安装器）：

| 需求 | 官方命令 |
|---|---|
| 选技能 | `-s, --技能 <name>`（本技能 name = `skill-accuracy-eval`） |
| 选智能体平台 | `-a, --agent <agent>`（80+ 平台：claude-code / opencode / codex / cursor / windsurf / gemini-cli / trae / qwen-code 等） |
| 全局 vs 项目 | 默认项目级；`-g, --global` 装到用户目录（如 `~/.claude/skills/`、`~/.config/opencode/skills/`） |
| 复制 vs 软链 | 交互选择；`--copy` 强制复制（默认 canonical copy + symlink，不支持时自动回退复制） |
| 私有仓库 | 直接复用本机 git 凭据 / GitHub CLI / SSH；或设 `GITHUB_TOKEN` |

其他常用：`npx skills list`（已装清单）、`npx skills update`（更新）、`npx skills remove`（卸载）、`npx skills use OahMoza/skill-accuracy-eval`（不安装直接试用）。

## 豆包安装（官方未覆盖，用兜底脚本）

`npx skills` 的平台列表不包含豆包，豆包用户用兜底脚本或手动复制：

```bash
# 复制到豆包技能根目录（Windows 示例）
npx --yes github:OahMoza/skill-accuracy-eval --dir "C:\Users\<you>\AppData\Local\Doubao\User Data\<profile>\.doubao\agent_mode\workspace\.user_skills"
```

或直接把仓库的 `SKILL.md` + `references/` + `assets/` 复制到你的技能目录。

## 目录结构

```
skill-accuracy-eval/
├── SKILL.md                     # 评测方法本体（S0 资产查找 + 三件套生成 + S1–S6 流程 + 七条铁律）· 版本号见文档头
├── references/
│   ├── evaluation-framework.md  # 三维度判据 / 判定语义 / 阻断性规则 / S0 操作指南
│   ├── input-check.md           # 资料自检 9 项判据（S0 喂料后生成前必做）
│   ├── confirmation-gate.md     # 确认门细则 + 评测资产落盘与复用（v1.5）
│   ├── execution-flow.md        # S1–S6 执行细则 + 改前改后对比 + 回填升级
│   └── gotchas.md               # 常见错误 16 条（看到即纠正）
├── assets/
│   ├── three-piece-sample.md    # 三件套种子样本（虚构示例，先看结构）
│   ├── score-sheet-template.md  # 打分表模板
│   ├── threshold-approval-template.md # 验收门槛确认记录模板（多人讨论 + 签认 + 冻结声明）
│   ├── sop-overview.md          # SOP 总览速查（全流程 / 角色 / 铁律 / 覆盖度与黄金集要点）
│   ├── sop-overview-graphic/    # SOP 一屏速览图（sop-overview.png + HTML 源）+ 术语与完整资料参考页（terms-and-docs.html）
│   ├── fork-overview-graphic/   # fork 机制一屏图（fork-overview.png + HTML 源 + 方向决策记录）
│   └── examples/crm-retail/     # 流程演示样例：真实测试集（τ²-bench retail）构造的模拟判定教学示例
│       ├── README.md            # 使用指引（先看）
│       ├── three-piece.md       # 三件套演示版
│       └── evaluation-report.md # 评测记录演示版
├── fork-sop.md                  # 通用内核 → 业务专用评测技能的 fork SOP（维护文档，供智能体/评测方优化使用；不随 npx 分发）
├── docs/                        # 仓库维护说明（maintenance.md）；不随 npx 分发
├── scripts/                     # 仓库回归检查（check_regression.py + check_installer.js）；维护工具，不属于被测技能执行依赖，不随 npx 分发
├── cases/crm-retail/            # 案例（保留在仓库的演示与回归样本）
│   ├── re-run-2026-09-28.md     # 复跑验证记录（演示样例文本可复现，非真实业务复现）
│   └── quantified-threshold-demo.md # 新机制演示：验收门槛声明 + 达标判定 + 差距分类 + 建议
├── package.json                 # 兜底安装入口（npx github:...）；版本与内核版本同步
└── install.js                   # 兜底安装脚本（官方 npx skills 未覆盖的平台，如豆包）
```

> 版本同步约定：SKILL.md 文档头 `metadata.version` / `package.json` version / fork-sop.md 版本表三处保持一致，任一机制变更三处同改。

## 使用流程（摘要）

1. **S0 资产查找**：先查是否已有本被测技能的锁定评测资产——有且覆盖本次 → 复用模式（加载锁定资产，跳过喂料与生成）；无 → 生成模式（喂料 → 生成三件套草稿 → 锁定后落盘为资产）；需补用例 → 增量模式（加载既有资产，只对新增/回填用例走确认）。
2. **确认门**：黄金集逐条指回来源后锁定；确认不了标 `待确认`，缺资料不进入执行；可一并声明分维度验收门槛（多人讨论 + 确认记录）与版本字段（业务资料 / 黄金集 / 运行环境 / 有效期）。
3. **S1–S6**：锁定 → 真实环境执行（只采最终结果）→ 三维度判定（缺证从严）→ 按维度汇总通过率 + 达标判定（有验收门槛时）+ 差距分类 + 改进建议 → 复核 → 输出评测记录 + 版本锁定 + 边界说明。

完整方法论见 `SKILL.md`；模拟判定教学样例见 `assets/examples/crm-retail/README.md`。

## 仓库维护（维护者用）

- 回归检查：`npm run check`（等价 `python scripts/check_regression.py`），覆盖五项——frontmatter 真实 YAML 解析与三处版本同步、markdown 表格列数、CRM 逐例汇总与报告 / 量化演示 / 复跑勘误对账、安装器 5 组边界（Node vm 假 fs，不真实安装）、文件与章节引用存在性；任一项失败退出码非零。
- 自检：`python scripts/check_regression.py --selftest`——在临时目录副本上故意篡改示例汇总数 / 模板列 / 安装守卫，验证入口能捕捉关键回归；不改真实文件、不提交临时目录。
- 依赖（维护者自备，不自动安装）：Python 3.8+、PyYAML、Node ≥ 14。
- **检查工具仅供仓库维护，使用本 Skill 无需运行检查或安装维护依赖**：`npm run check` 仅限仓库内使用；`package.json` `files` 白名单不含 `scripts/` 与 `docs/`，检查脚本与维护说明不随技能包分发。
- 限度：文本级回归检查，不是语义审计或正式评测的替代；事实源治理与各主题权威源映射见 `docs/maintenance.md`。

## 注意

- 评测产物（`cases/` 目录）保留在仓库作演示与回归样本，不随技能包分发（package.json `files` 已排除 cases）。
- 结论必须带被测版本与样本边界，不扩展为整体可靠性承诺。
