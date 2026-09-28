# skill-accuracy-eval

**结果导向的 Skill 准确性评测**（临时替代品）：评测一个 Skill（技能）的准确性，只看最终结果、不看轨迹。

- 一线喂入业务资料（技能说明 / 业务规则 / 用户问题样例 / 禁止行为）→ 自动生成「被测版本 / 用例集 / 金标准」三件套草稿 → 确认后执行评测。
- 按「结果正确性 / 规则与边界 / 可靠与兜底」三维度逐条判定 `pass / fail / not_evaluated`，只出分数 + 证据，不判生死。
- 完全自包含：不依赖任何评测平台、执行引擎或日志系统。SKILL.md 为标准 frontmatter 格式（name + description），支持 Agent Skills 的智能体均可直接识别。

> 定位：在一线暂不具备正式评测平台时使用；不取代正式评测实现。

## 快速开始（官方 npx skills 安装）

推荐使用 **Vercel 官方 CLI `npx skills`** 安装——它支持交互式选择技能、智能体平台、全局/项目作用域、复制/软链安装方式：

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
| 选技能 | `-s, --skill <name>`（本技能 name = `skill-accuracy-eval`） |
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
├── package.json                 # 兜底安装入口（npx github:...）
└── install.js                   # 兜底安装脚本（官方 npx skills 未覆盖的平台，如豆包）
```

## 使用流程（摘要）

1. **S0 喂料**：把业务资料喂给 skill → 自动生成三件套草稿（不需要一线自己写）。
2. **确认门**：金标准逐条指回来源后锁定；确认不了标 `待确认`，缺资料不进入执行。
3. **S1–S6**：锁定 → 真实环境执行（只采最终结果）→ 三维度判定（fail-closed）→ 按维度汇总通过率 → 复核 → 输出评测记录 + 边界说明。

完整方法论见 `SKILL.md`；完整跑通案例见 `assets/examples/crm-retail/README.md`。

## 注意

- 评测产物（如各案例的 `cases/` 目录）保留在评测者本地，不属于本技能包。
- 结论必须带被测版本与样本边界，不扩展为整体可靠性承诺。
