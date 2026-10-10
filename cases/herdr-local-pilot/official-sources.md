# 官方依据 · herdr CLI 输出快照（黄金依据来源）

> **原则**：本试运行的黄金依据**只能**来自官方 CLI（`--help` / 各命令组 / `--skill`）与直接后端返回（命令的 stdout/stderr/exit）。
> **不照抄**本地技能 `SKILL.md` / `sop.md` 的自述作为业务标准；本地技能仅作"被测评对象"。

## 一、环境与捕获

| 项 | 值 |
|---|---|
| 二进制 | `herdr 0.9.3`（client/server 均 0.9.3，endpoint compatible） |
| 捕获时间（UTC） | **2026-10-10**（本机 08:00 本地时间；见 `evidence.json:generated_at_utc`） |
| 捕获方式 | `herdr` 官方只读命令，重定向至本目录 `official-*.txt` |
| 门禁 | `HERDR_ENV=1` |

## 二、快照文件清单与 sha256

| 文件 | 命令 | exit | sha256 |
|---|---|---|---|
| `official-version.txt` | `herdr --version` | 0 | `4140165b07f9276676a5a5d67b5c64c8f0099b7c30fa00703a3f23185cf5d60d` |
| `official-help.txt` | `herdr --help` | 0 | `0e33235a4cabd179fc16b80a8dfe42bd66f396577bb32c23303afbbb5703b20e` |
| `official-skill.txt` | `herdr --skill` | 0 | `b16ba0d9a22adbaf259d2022cd323801f8e51d530c94cb0cd23a69069292506b` |
| `official-group-agent.txt` | `herdr agent` | 2 | `35cfd2e6a557fc055b35e4aee99143faf69d98586d595a4a0fad1c3d55483644` |
| `official-group-pane.txt` | `herdr pane` | 2 | `176cd9426b7e0dfbec0399ae50ef1e51ae58a24cf5dd47e8cf10b0c891a95f03` |
| `official-group-workspace.txt` | `herdr workspace` | 2 | `439ca38afd4e903887a993ff0d9d56ef7e2ca94fd580eae04d75a8a9a403b62b` |
| `official-group-tab.txt` | `herdr tab` | 2 | `c7491e6e8a75200ec22dc8dcb8bd6386ba466ca81acd99ba7c358d57043228c0` |
| `official-group-worktree.txt` | `herdr worktree` | 2 | `dffe441073ef12c5e5a76816fe446e0b31f28edb0d628d8abe169cdcf182e271` |
| `official-group-terminal.txt` | `herdr terminal` | 2 | `00a74e5276cf0fed5540555fcfa2960fdcb1fe1f2158202cefb88976e278125b` |
| `official-group-notification.txt` | `herdr notification` | 2 | `52b71a52fc12ab989b566afa7d84c5043e43c2046a9a4a04738fab17a51d6adf` |
| `official-group-integration.txt` | `herdr integration` | 2 | `bf9ff948b624c7399acb1e9dbf90ec591a06e5a7898ef289020b1ec0218ad74b` |
| `official-group-session.txt` | `herdr session` | 2 | `805f98aa4ec37e7d4eb07c98d593398dd0e2f232eccccf5e792f6e31ceafe2cd` |
| `official-group-machine.txt` | `herdr machine` | 2 | `7eb38d3af37d530c3f05d5462824dc643626554ff1839f0357cc07b8e9d40212` |

> 命令组 exit=2 的含义（官方）：`CLI syntax errors exit with status 2`（`official-skill.txt:214`）。命令组缺子命令即打用法，属**用法响应**，非业务失败。

## 三、被多次引用的官方原文条款（摘录）

| 锚点 | 官方原文（摘录） | 支撑用例 |
|---|---|---|
| `official-skill.txt:13` | `test "${HERDR_ENV:-}" = 1` | `hdp-01`、`hdp-02` |
| `official-skill.txt:16` | "If the check fails, say that you are not running inside Herdr and stop. Do not inspect or control the focused Herdr session from outside Herdr." | `hdp-02` |
| `official-skill.txt:43` | "Do not run bare `herdr` for discovery; it launches or attaches the TUI. Do not probe a mutating nested command by omitting arguments." | 全局 `g-off-2` |
| `official-skill.txt:171` | "A timeout or stalled response does not prove the prompt was never delivered; do not blindly submit it again." | 全局 `g-off-4` |
| `official-skill.txt:212` | "Never run `herdr server stop` from an active session unless the user explicitly intends to stop the server and its pane processes." | `hdp-06` |
| `official-skill.txt:214` | "CLI server errors are JSON on stderr with exit status 1. CLI syntax errors exit with status 2." | `hdp-03`、`hdp-04`、`hdp-05` |
| `official-group-agent.txt` | `herdr agent commands:` … `herdr agent get <target>` … | `hdp-05`、`hdp-07` |

## 四、两类约束分开（避免把授权当官方条款）

- **官方原文安全条款**：见 §三 摘录（来源 `official-skill.txt`）。官方**没有**"只读/幂等命令即自动允许"的泛化许可。
- **本轮 owner 授权范围**：`--version` / `status` / 命令组打印 / 对不存在目标的 `agent get` / 无效顶层命令——这是**授权**，不是官方条款；原始 exit/stdout/stderr/sha256 作为试运行记录（`evidence.json`）。

## 五、与本地技能的关系（防止基准污染）

- 本地技能 `SKILL.md` 声称"正文逐字保留 `herdr --skill`"。经比对，**其 `# Herdr` 至「官方原文范围结束」段与 `official-skill.txt` 正文段 sha256 一致**（`0a70e8e2…`，13797 字节）——即该技能正文可作为"官方原文的忠实转写"，但**仍以本目录官方快照为唯一判据**。
- 本地技能的**中文入口/速查表**（如 `sop.md`）属其自身组织，**不**作为黄金依据。
