# Herdr 速查表（SOP 精简版）

> 依据：`herdr --skill`（v0.9.3）官方语义浓缩。与 SKILL.md 正文冲突时**以正文为准**；herdr 升级后须同步修订本文件。

## 门禁

```bash
test "${HERDR_ENV:-}" = 1   # 非 1 → 停止，不控制外部会话
```

## 安全红线（违反即停）

- 不运行裸 `herdr`（启动/附着 TUI）；不 kill 主进程；
- 不关闭自己未创建的 workspace/tab/pane；`workspace close --group` 慎用；
- 不替用户做 SSH 认证（`machine reconnect` 需用户终端操作）；
- 不擅自安装/升级/停止 server；`--trust-repository` 需用户先核实仓库；
- 后台工作一律 `--no-focus`。

## 状态语义

| 状态 | 含义 | 动作 |
|---|---|---|
| idle / done | 就绪 | 可 prompt |
| working | 工作中 | `--wait` |
| blocked | approval/提问 UI | 查看 → 问用户，不代答 |
| unknown | 无法分类 | 不代表完成，`read` 确认 |

## 命令速查

**A 自查**：`herdr --help`；`herdr agent` 等命令组打印用法；`herdr status` 查版本差异。

**B 布局**：
```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus   # 方向按需改 down
```
新 pane ID 取 `.result.pane.pane_id`；缺省兄弟 pane/当前 tab/当前 cwd。

**C 编码 agent**：
```bash
herdr agent start <name> --kind <kind> --pane <pane-id> [-- <args>]
herdr agent prompt <name> "..." --wait --timeout 120000
herdr agent read <name> --source recent-unwrapped --lines 120
herdr agent send-keys <name> esc       # 发送 Esc（二选一）
herdr agent send-keys <name> ctrl+c    # 发送 Ctrl+C（二选一）
```
`prompt --wait`：5s 无 working/blocked → `agent_prompt_stalled`；timeout 不证明未送达，不盲目重发。
`send-keys` 的 `esc` 与 `ctrl+c` 为**二选一**，各发一条，不要用 `|` 连接（Bash 会当管道解析）。

**D pane 普通命令**：
```bash
herdr pane run <pane-id> "cmd"
herdr pane wait-output <pane-id> --match "text" --timeout 120000
herdr pane read <pane-id> --source recent-unwrapped --lines 120
```
读源：`visible` / `recent` / `recent-unwrapped`（首选）/ `detection`；样式证据用 `--format ansi`。

**E 远程机器**（已保存 profile）：所有命令加 `herdr --machine <label-or-id>` 前缀；`machine status --json` 诊断；转发不启动远端 server，连接失败 ≠ 未应用，先查远端状态。

## 失败矩阵

| 现象 | 处理 |
|---|---|
| `agent_not_ready` | 启动被阻塞：`agent read`，等 idle |
| `agent_blocked` | 看 UI，问用户 |
| `agent_prompt_stalled` | `agent get` + `read` 诊断，不重发 |
| `timeout` | 不证明未送达，不盲目重试 |
| 退出码 1 | server 错误（stderr JSON） |
| 退出码 2 | 语法错误，`--help` 核对 |
| 版本差异 | `herdr status` 后决定，不擅自升级/停服 |

## 校验

执行前：门禁、目标唯一、`--no-focus`；执行中：ID 取 JSON、不依赖其他客户端焦点；执行后：结果可追溯、不擅自关会话。
