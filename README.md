# skill-accuracy-eval

**结果导向的 Skill 准确性评测**（临时替代品）：评测一个 Skill（技能）的准确性，只看最终结果、不看轨迹。

- 一线喂入业务资料（技能说明 / 业务规则 / 用户问题样例 / 禁止行为）→ 自动生成「被测版本 / 用例集 / 金标准」三件套草稿 → 确认后执行评测。
- 按「结果正确性 / 规则与边界 / 可靠与兜底」三维度逐条判定 `pass / fail / not_evaluated`，只出分数 + 证据，不判生死。
- 完全自包含：不依赖任何评测平台、执行引擎或日志系统。

> 定位：在一线暂不具备正式评测平台时使用；不取代正式评测实现。

## 快速开始（npx 安装）

```bash
npx --yes github:OahMoza/skill-accuracy-eval
```

- 默认安装到 `~/.doubao/skills/skill-accuracy-eval`。
- 指定技能根目录：

```bash
npx --yes github:OahMoza/skill-accuracy-eval --dir "<你的技能根目录>"
```

示例（Windows 豆包）：`--dir "C:\Users\<you>\AppData\Local\Doubao\User Data\<profile>\.doubao\agent_mode\workspace\.user_skills"`

> 本仓库为**私有仓库**：执行 npx 的人需要是该仓库的 collaborator（GitHub 仓库 → Settings → Collaborators 添加），且本机 git 已配置对应凭据。

## 目录结构

```
skill-accuracy-eval/
├── SKILL.md                     # 评测方法本体（S0 生成三件套 + S1–S6 执行流程 + 七条铁律）
├── references/
│   └── evaluation-framework.md  # 三维度判据 / verdict 语义 / blocking 规则 / S0 操作指南
├── assets/
│   ├── three-piece-sample.md    # 三件套种子样本（虚构示例，先看结构）
│   ├── score-sheet-template.md  # 打分表模板
│   └── examples/crm-retail/     # 完整演示样例：真实测试集（τ²-bench retail）跑通全过程
│       ├── README.md            # 使用指引（先看）
│       ├── three-piece.md       # 三件套演示版
│       └── evaluation-report.md # 评测记录演示版
├── package.json                 # npx 包入口
└── install.js                   # 安装脚本
```

## 使用流程（摘要）

1. **S0 喂料**：把业务资料喂给 skill → 自动生成三件套草稿（不需要一线自己写）。
2. **确认门**：金标准逐条指回来源后锁定；确认不了标 `待确认`，缺资料不进入执行。
3. **S1–S6**：锁定 → 真实环境执行（只采最终结果）→ 三维度判定（fail-closed）→ 按维度汇总通过率 → 复核 → 输出评测记录 + 边界说明。

完整方法论见 `SKILL.md`；完整跑通案例见 `assets/examples/crm-retail/README.md`。

## 注意

- 评测产物（如各案例的 `cases/` 目录）保留在评测者本地，不属于本技能包。
- 结论必须带被测版本与样本边界，不扩展为整体可靠性承诺。
