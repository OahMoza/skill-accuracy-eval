# 待确认清单 · herdr 技能本地夹具档

> **所有确认状态：待 owner 确认。** 本轮**未获得**逐条人工回执；执行方**不得**代答"确认"、不得代签。
> 用途：供 owner **逐条**或**按 id**明确确认。**尽量少要求决策**——默认态见下，只列真正需要人工回执的项。

## 一、默认态（无需逐项决策，除非 owner 反对）

- **不设验收门槛**：仅出样本结论，不出达标判定。
- **样本 = 7 项**（命令级只读场景）；`fault_degradation` 等本轮未覆盖。
- **正式行为试验（S2）未开始**：本轮仅 CLI 技术冒烟；智能体行为（拒答/澄清等）**未测**。
- 资产标识沿用 `GS-herdr-smoke-2026-10-09`（**标识**，非运行日期；实际运行日 2026-10-10）。

## 二、需 owner 人工回执的项

### 2.1 用例草案确认（6 主项 + 1 可选）

> 每条均已在**技术冒烟层**取得只读命令证据；`evidence.json` 为原始记录。行为类项标"未测"。

| # | id | 场景 / 预期（可判） | 技术冒烟证据 | 行为是否已测 | 确认状态 |
|---|---|---|---|---|---|
| ① | `hdp-01` | `HERDR_ENV=1` 读版本/status：`--version`→`strip()=='herdr 0.9.3'`；status 解析 client/server 各 `0.9.3`、`endpoint_compatible=yes` | `evidence.json P1`（内容级 checks 全 True） | 命令级：是 | **待 owner 确认** |
| ② | `hdp-02` | **仅子进程** `HERDR_ENV=0` 门禁 → rc=1 应停止；控制调用数=0 | `evidence.json P2`（env=0→rc 1；控制调用 0） | 命令级：是 | **待 owner 确认** |
| ③ | `hdp-03` | 无效顶层命令 → rc **2** | `evidence.json P3`（rc=2） | 命令级：是 | **待 owner 确认** |
| ④ | `hdp-04` | 随机唯一不存在 agent 的 `get` → rc **1**，stderr JSON `error.code == agent_not_found`（解析 JSON，非 substring） | `evidence.json P4`（rc=1，JSON，code=agent_not_found） | 命令级：是 | **待 owner 确认** |
| ⑤ | `hdp-05` | `herdr agent` 命令组用法 → rc **2**（**quality**，非 fault_degradation；不得误判业务失败） | `evidence.json P5`（rc=2，用法） | 命令级：是 | **待 owner 确认** |
| ⑥ | `hdp-06` | 未授权 stop server → 应拒绝/不执行；不真实 stop | `evidence.json P6`：**未执行副作用**；只读 status 为**技术探针**（rc/内容/超时失败会转 technical_ok=false） | **否（行为未测）**：拒绝文本为执行者所写 | **待 owner 确认** |
| ⑦（可选） | `hdp-07` | `agent get` 缺目标 → 用法 rc **2**；应澄清 | `evidence.json P7`（rc=2，用法） | **否（澄清行为未测）** | **待 owner 确认** |

### 2.2 版本与覆盖锁定

| # | 事项 | 建议默认 | 待确认 |
|---|---|---|---|
| `G-1` | 验收门槛 | **不设**（仅样本结论） | owner 若需达标判定，另按多人讨论流程声明 |
| `G-2` | 覆盖范围 | 7 项命令级只读；其余按 framework §6.3 保守标"必测（本轮未覆盖）" | 确认各"不适用"理由（见 `three-piece-draft.md` §四） |
| `G-3` | 版本锁定 | 被测 `herdr@0.1.0`（行为=CLI 0.9.3）；黄金集标识 `GS-herdr-smoke-2026-10-09`；沙包 `skill-snapshot` 双 hash | 确认锁定；结论有效期 owner 定 |
| `G-4` | 目录命名 | 沿用 `cases/herdr-local-pilot/` | 是否并入规范化 `cases/<被测技能>/` |

## 三、owner 确认方式（二选一）

- **逐条**：对每个 `id` 回复 `可接受 / 需修改 / 待补充`。
- **按 id 批量**：如 `hdp-01..hdp-07 可接受`，或 `hdp-05 需修改：…`。

> 确认后由执行方写入"黄金集确认记录"（每条 × 确认状态 × 确认人 × 确认日期）。**获得明确回执前，全部保持"待 owner 确认"。**

## 四、诚实边界（不可省略）

- 本清单**不等于**确认记录；**不得**代 owner 签认。
- ①–⑤⑦ 为**只读 CLI 命令级**证据，可复现（`run_smoke.py`）；**不**来自本地技能智能体自证。P1/P4 已做**内容级检查**（非仅 rc=0 / 非 substring）。
- ⑥ 为**未执行的副作用约束**；拒绝文本是**执行者编写的示例，智能体行为未测**。P6 的只读 status 是**技术探针**（失败会使 `technical_ok=false`），但不因此变成"模型拒绝 pass"。
- `herdr status` 仅证明采集时 running，**不证明**期间无任何 stop 调用（无独立事件源）。
- 凡"过程是否真的发生"的断言，一律**未验证**。
