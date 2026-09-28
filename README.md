# skill-accuracy-eval

**结果导向的 Skill 准确性评测**（临时替代品）：评测一个 Skill（技能）的准确性，只看最终结果、不看轨迹。

- 一线喂入业务资料（技能说明 / 业务规则 / 用户问题样例 / 禁止行为）→ 自动生成「被测版本 / 用例集 / 金标准」三件套草稿 → 确认后执行评测。
- 按「结果正确性 / 规则与边界 / 可靠与兜底」三维度逐条判定 `pass / fail / not_evaluated`，只出分数 + 证据，不判生死。
- 完全自包含：不依赖任何评测平台、执行引擎或日志系统。SKILL.md 为标准 frontmatter 格式（name + description），豆包 / Claude Code / OpenCode 等支持 Agent Skills 的智能体均可直接识别。

> 定位：在一线暂不具备正式评测平台时使用；不取代正式评测实现。

## 快速开始（npx 安装，支持通用智能体）

```bash
# 交互式选择安装目标（推荐，列出各平台菜单）
npx --yes github:OahMoza/skill-accuracy-eval

# 直接指定平台（跳过菜单）
npx --yes github:OahMoza/skill-accuracy-eval --platform claude
npx --yes github:OahMoza/skill-accuracy-eval --platform opencode

# 自定义目录（优先级最高）
npx --yes github:OahMoza/skill-accuracy-eval --dir "<你的技能根目录>"

# 查看支持平台与默认目录
npx --yes github:OahMoza/skill-accuracy-eval --list
```

**平台与默认技能目录**：

| 平台 | 全局技能目录 |
|---|---|
| 豆包 | `~/.doubao/skills/` |
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Cursor | `~/.cursor/skills/` |
| Codex | `~/.agents/skills/` |
| Windsurf | `~/.windsurf/skills/` |

Windows 豆包示例：`--dir "C:\Users\<you>\AppData\Local\Doubao\User Data\<profile>\.doubao\agent_mode\workspace\.user_skills"`

> 本仓库为**公开仓库**：任何人有 GitHub 账号即可通过 npx 安装（首次运行 npx 会提示授权访问该仓库，选 Yes 即可）。

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
└── install.js                   # 安装脚本（平台可选：--platform / --dir / 交互菜单）
```

## 使用流程（摘要）

1. **S0 喂料**：把业务资料喂给 skill → 自动生成三件套草稿（不需要一线自己写）。
2. **确认门**：金标准逐条指回来源后锁定；确认不了标 `待确认`，缺资料不进入执行。
3. **S1–S6**：锁定 → 真实环境执行（只采最终结果）→ 三维度判定（fail-closed）→ 按维度汇总通过率 → 复核 → 输出评测记录 + 边界说明。

完整方法论见 `SKILL.md`；完整跑通案例见 `assets/examples/crm-retail/README.md`。

## 注意

- 评测产物（如各案例的 `cases/` 目录）保留在评测者本地，不属于本技能包。
- 结论必须带被测版本与样本边界，不扩展为整体可靠性承诺。
