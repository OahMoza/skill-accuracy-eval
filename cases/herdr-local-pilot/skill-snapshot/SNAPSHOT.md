# 快照说明 · herdr 技能（B 修复版本记录）

> 本目录是 **B 修复版本记录**：`C:/Users/oahmo/.agents/skills/herdr` 在一次真实小任务试运行（herdr-local-pilot）时的只读快照。
> 用途：为本次技术试运行固定"被测资产版本"，供复核与回归对照。**不随 npm 包分发**（`cases/` 已在 `package.json files` 白名单之外）。
> 不虚构旧版本副本、不虚构提交历史。

## 一、快照来源与版本

| 项 | 值 |
|---|---|
| 源路径 | `C:/Users/oahmo/.agents/skills/herdr/` |
| 技能自身版本 | `metadata.version = 0.1.0`（技能包自身版本，非 herdr 二进制版本） |
| 捕获日期（UTC） | **2026-10-10**（本机 08:02 本地时间；源文件静态拷贝，见 `evidence.json` 与 `official-sources.md`） |
| 捕获方式 | 只读复制两份授权文件；未改源文件、未改 ACL |

> 说明：B 修复（F9 去 NBSP / F10 SOP 二选一 / F13 正文逐字保留）已在本次试运行**之前**完成并落盘；本快照即该修复后的版本，用作本轮"被测资产版本"。仓库 `git log` 另有 A 侧提交 `38cfc36`，与本快照无关（不由本轮产生）。

## 二、文件清单与哈希

| 文件 | 相对路径 | md5 | sha256 |
|---|---|---|---|
| SKILL.md | `SKILL.md` | `01f74c23594041a27ca1b7db0c18cbae` | `0422c3871e24ead00e5a491263e8fdff63b873dbb82966ccfe5d64bb87e21369` |
| 速查表 | `references/sop.md` | `b1a855536b84bbfd75664a02a53ef940` | `2c841a3a29aec0123735e588a827eadeec216b41f3c09a6a6ec67d7bd51aab33` |

> 校验：快照两文件与源文件 md5 逐一相等（`01f74c23…` / `b1a85553…`），证明本快照即当前 B 修复版本，无二次改动。

## 三、不收集项（合规声明）

- 不收集完整环境变量、不收集凭据/令牌、不收集 SSH 材料。
- 不关闭会话、不改权限/ACL/认证、不安装/升级/停止 server、不向任何 agent 发送输入。
