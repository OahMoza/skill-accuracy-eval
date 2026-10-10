# 独立复跑与试点状态

本文件由 reviewer-b 在员工交付后独立核验，不替代正式评测报告或 owner 确认记录。

## 已完成的真实技术试运行

- 被测资料快照：`skill-snapshot/`，与本机已修复的 herdr 技能两文件逐字节相同。
- 工具环境：Herdr client/server 0.9.3，Windows，`HERDR_ENV=1`。
- 员工原始运行：`evidence.json`；审核者独立复跑：`reviewer-evidence.json`。复跑使用 `--output`，原始证据哈希未改变。
- 7 个探针的已执行命令均满足技术预期；9 份原始子进程输出的 SHA256 已独立重算吻合。
- P6 中只执行只读 status，记录采集时 server running；拒绝文字是执行者编写的示例，**拒绝行为未测**。
- P7 中实际检查 CLI 缺参响应，**智能体澄清行为未测**。
- 环境为 0 的总门禁另用拦截 `subprocess.run` 的独立验证确认：退出 2、零子进程调用、不创建输出文件。
- 故障降级、多轮、跨机、注入等覆盖尚不足，不能由本次只读 CLI 输出推导完整技能准确性。

## 独立负测

在临时目录或注入的假返回中完成，不执行副作用命令：

1. `herdr 0.9.30` 不得与 0.9.3 混同：技术脚本退出 3。
2. status 返回其他 client/server 版本：退出 3。
3. JSON 的 message 含 agent_not_found，但 error.code 不正确：退出 3。
4. 最后一次只读 status 失败：退出 3，technical_ok 为 false。

维护入口另经独立负测确认：真实 YAML 的 NBSP 标识符损坏、不存在的章节引用均被拒绝；员工提供的三项临时副本篡改自检（汇总数、模板列、安装守卫）已由 reviewer-b 重跑，3/3 捕捉。

## 可复现命令

从仓库根目录运行（需 Python、PyYAML、Node、Bash、Herdr；运行者须处于 Herdr）：

```bash
npm run check
python scripts/check_regression.py --selftest
python cases/herdr-local-pilot/run_smoke.py --output <新的证据文件路径>
npm pack --dry-run --json
```

维护检查不包含本试点目录，试点按其只读脚本与人工审阅单独复核。所有带 SHA256 的官方原文与技能快照通过 `.gitattributes` 保留原始字节，避免 Git 换行转换改变档案校验值。

## 当前确认状态

三件套为 `three-piece-draft.md`，人工回执清单为 `confirmation-pending.md`；全部仍待 owner 确认。未设验收门槛，未产生正式 S2 执行、正式三维度评分或达标结论。

owner 确认黄金集与覆盖范围后，应按锁定资料另行执行正式试评测，记录实际智能体执行环境和响应；不得把此次 CLI 技术冒烟直接改名为已完成的技能行为评测。
