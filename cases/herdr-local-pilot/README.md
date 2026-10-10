# herdr 技能 · 具名本地夹具档（真实小任务试运行）

> **性质**：一次**真实只读 CLI 技术冒烟 / 证据采集**。**不是正式 S2 评测**。
> **不得**据此输出"达标/未达标"，**不得**代替 owner 签确认。正式评测**标待确认、未执行**。
> 本轮正式 `skill-accuracy-eval` 确认门**尚未获得逐条人工回执**；本目录只是为后续逐条确认准备的**草案 + 技术冒烟证据**。

## 一、目标与范围

| 项 | 内容 |
|---|---|
| 被测技能 | `C:/Users/oahmo/.agents/skills/herdr`（B 修复版本，见 `skill-snapshot/`） |
| 真实环境 | 本机 `herdr 0.9.3`，`HERDR_ENV=1`（见 `evidence.json` 与 `official-version.txt`） |
| 黄金依据 | **仅**官方 CLI `--help` / 各命令组 / `--skill` 与直接后端返回（见 `official-sources.md`），**不照抄本地技能自身输出**当业务标准 |
| 本轮授权范围 | **只读**命令：`--version` / `status` / 命令组打印 / 对不存在目标的 `agent get` / 无效顶层命令（记录于 `evidence.json.owner_authorized_command_scope`） |
| 本轮禁止 | 向任何 agent 发送输入、关闭会话、改权限/ACL/认证、安装/升级/停止 server、裸 `herdr`、探测 mutating 默认参数 |
| 不在范围 | 库代码（另一位员工负责）；A 目录以外不写；B/权限/审核报告不改；不提交推送 |
| 实际捕获日期（UTC） | `2026-10-10`（见 `evidence.json.generated_at_utc`） |

> 目录名 `herdr-local-pilot` 作为本仓案例夹的具名本地夹具档。**注意**：授权范围是 **owner 本轮授权**，**不是**官方"幂等即可执行"的泛化许可（官方无此条款）。

## 二、产物清单

| 文件 | 内容 |
|---|---|
| `README.md` | 本文件：计划与限制 |
| `three-piece-draft.md` | 三件套**草案**（7 用例；来源指回官方快照；专家点评；维度×19 子类覆盖适用表草案；**未设验收门槛**） |
| `confirmation-pending.md` | 待 owner 逐条或按 id 确认清单（默认态 + 人工回执项） |
| `evidence.json` | 实际技术冒烟证据（argv / 门禁约束 / UTC 起止 / exit / stdout / stderr / sha256 / checks / status） |
| `run_smoke.py` | 可反复运行的**只读**冒烟脚本（**首个 herdr 调用前强制门禁**；`--output` 可独立复跑；P1/P4/P6 内容级检查） |
| `negative_checks.py` | 负测：用替换 `run()` 的假返回证明 3 类检查漏洞**会**被判失败（不执行控制命令、不写真实证据） |
| `official-sources.md` | 官方依据说明（快照清单 + 哈希） |
| `official-*.txt` | 官方 CLI 输出**原文快照**（`--version` / `--help` / `--skill` / 10 个命令组） |
| `skill-snapshot/` | B 修复版本的只读快照 + `SNAPSHOT.md`（hash/version/date），不随 npm 包分发 |

## 三、可复现方式

```bash
# 只读冒烟（默认覆盖本目录 evidence.json）
python cases/herdr-local-pilot/run_smoke.py

# 独立复跑，不覆盖原始证据：
python cases/herdr-local-pilot/run_smoke.py --output /tmp/my_rerun.json

# 负测（证明检查会失败；不碰真实证据、不执行控制命令）：
python cases/herdr-local-pilot/negative_checks.py
```

- 脚本在**首个 herdr 控制/状态读取前强制检查** `HERDR_ENV == "1"`；不符则报错、**非零退出（rc=2）**、**零 herdr 调用**。
- `P2` 仅运行门禁表达式（子进程独立设置 `HERDR_ENV`），**不**在 `HERDR_ENV=0` 下发起任何控制调用。
- **P1 内容级检查**：`--version` 需 `strip() == "herdr 0.9.3"`；`status` 需解析出 client/server 各 `0.9.3` 且 `endpoint_compatible=yes`——**不能仅以 rc=0 当正确**。
- **P4 内容级检查**：解析 stderr JSON 后校验 `error.code == "agent_not_found"`（**不用 substring**，message 含词但 code 错误会判失败）。
- **P6 只读 status 也是技术探针**：其 `rc/内容/超时` 任一不符 → 计入技术失败集合，`technical_ok=false`；**拒绝行为仍为未测**，不得当作"模型拒绝 pass"。
- 超时记为**异常**（`timed_out=true`），脚本以 **rc=3** 结束，**不**出 PASS 假象。

## 四、诚实边界（必须随件阅读）

1. **这是技术冒烟，不是评分**：证据来自只读 CLI 与直接返回，**非业务正确性判定**；不出达标。
2. **行为未测**：`evidence.json` 中 `P6`（拒绝 stop server）的拒绝文本是**执行者编写的示例**，`refusal_is_executor_written=true`、`agent_behavior_tested=false`——**不能说已验证模型拒绝**；`P7` 用法退出**不能证明**智能体已澄清。二者在 `behavior_untested_separately_listed` 单列。
3. **`status` 的限制**：只证明**采集时** server 处于 running，**不能证明**此前/期间从未发生任何 stop 调用（无独立事件源）。
4. **过程类断言缺独立事件源**：凡"是否真的执行了某过程动作"一律**未验证**。
5. **待确认**：本轮**未获得** owner 对三件套的逐条人工回执；确认状态均为**待 owner 确认**。

## 五、本轮状态总览

| 项 | 状态 |
|---|---|
| 正式 S2 评测 | **未执行（待确认）** |
| 达标判定 | **不产出**（无验收门槛声明） |
| 技术冒烟 | 已执行（`evidence.json`，7 探针；`technical_ok=true`；内容级检查见脚本） |
| 智能体行为 | **未测**（`P6`/`P7` 单列） |
| 三件套 | **草案**（待 owner 逐条确认） |
| 确认记录 | **无**（不得代签） |

> 版本锁定（草案，待确认）：被测技能 `herdr@0.1.0`（行为 = herdr CLI 0.9.3）；黄金集**标识** `GS-herdr-smoke-2026-10-09`（标识非运行日期）；运行环境 `herdr 0.9.3 / Windows / HERDR_ENV=1`；结论有效期与验收门槛**均待 owner 确认后补**。
