#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_smoke.py — skill-accuracy-eval 真实只读 CLI 技术冒烟（herdr-local-pilot）

定位：真实只读 CLI 技术冒烟 / 证据采集。**不是正式 S2 评测**，不出达标，不代 owner 签确认。

硬约束：
  - 运行前**强制**检查本进程 HERDR_ENV==1；否则报错、非零退出、**零 herdr 调用**。
  - 只发起只读命令：--version / status / 命令组打印 / 对不存在目标的 agent get。
  - 不向任何 agent 发送输入、不关闭会话、不改权限/ACL/认证、不安装/升级/停止 server、不用裸 herdr、不探 mutating 默认参数。
  - 超时记为异常（anomaly），不出 PASS 假象。
  - 记录 argv / 门禁环境约束 / UTC 起止 / exit / stdout / stderr / sha256；不收集完整 env 或凭据。

用法：
  python run_smoke.py [--output PATH]
  --output 默认写到**本脚本所在目录**的 evidence.json；复核者可指定别的路径独立复跑，避免覆盖原始证据。

退出码：
  0 = 技术冒烟全部检查通过（不含"行为未测"项）
  2 = 门禁未通过（HERDR_ENV!=1）→ 未发起任何 herdr 调用
  3 = 存在技术失败（某只读命令的 rc/内容与 expect 不符，或超时）
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HASHR = hashlib.sha256


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(text: str) -> str:
    return HASHR(text.encode("utf-8")).hexdigest()


def parse_status_sections(text: str):
    """解析 herdr status 输出为 {section: {key: value}}（缩进行归入上一节）。"""
    sections = {}
    cur = None
    for line in text.splitlines():
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")) and line.rstrip().endswith(":"):
            cur = line.rstrip()[:-1].strip()
            sections[cur] = {}
        elif cur is not None and ":" in line:
            k, _, v = line.strip().partition(":")
            sections[cur][k.strip()] = v.strip()
    return sections


def run(argv, extra_env=None, timeout=60):
    """只读子进程运行；返回结构化证据。超时 -> status=anomaly，不伪造成功。"""
    env = dict(os.environ)
    if extra_env is not None:
        env.update(extra_env)
    gate = env.get("HERDR_ENV")
    pane = env.get("HERDR_PANE_ID")
    started = utcnow()
    t0 = time.time()
    timed_out = False
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           timeout=timeout, env=env)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        rc = None
        out = e.stdout if isinstance(e.stdout, str) else (e.stdout.decode("utf-8", "replace") if e.stdout else "")
        err = "TIMEOUT after %ss" % timeout
    except FileNotFoundError as e:
        timed_out = False
        rc = None
        out, err = "", "COMMAND_NOT_FOUND: %s" % e
    ended = utcnow()
    return {
        "argv": argv,
        "env_constraints": {"HERDR_ENV": gate, "HERDR_PANE_ID": pane},
        "utc_start": started,
        "utc_end": ended,
        "duration_ms": round((time.time() - t0) * 1000, 1),
        "exit": rc,
        "timed_out": timed_out,
        "stdout": out,
        "stderr": err,
        "stdout_sha256": sha(out),
        "stderr_sha256": sha(err),
        "stdout_bytes": len(out.encode("utf-8")),
        "stderr_bytes": len(err.encode("utf-8")),
    }


def probe(expect, checks, runs, observed, behavior_tested=True, note=None, kind="readonly-cli"):
    """组装一个探针；status 由 checks 是否全 True 决定。"""
    passed = all(bool(v) for v in checks.values())
    rec = {
        "kind": kind,
        "expect": expect,
        "checks": checks,
        "status": "pass" if passed else "fail",
        "behavior_tested": behavior_tested,
        "observed": observed,
    }
    if note:
        rec["note"] = note
    rec.update(runs)
    return rec


def main():
    ap = argparse.ArgumentParser(description="herdr-local-pilot read-only smoke")
    ap.add_argument("--output", default=str(HERE / "evidence.json"),
                    help="证据输出路径（默认：脚本所在目录/evidence.json）")
    args = ap.parse_args()

    # ---- 硬门禁：任何 herdr 调用之前 ----
    gate_env = os.environ.get("HERDR_ENV")
    if gate_env != "1":
        sys.stderr.write(
            "GATE FAIL: 本进程 HERDR_ENV=%r，要求 '1'。已在发起任何 herdr 调用前停止；"
            "零 herdr 调用。不检查/不控制任何 Herdr 会话。\n" % gate_env)
        sys.exit(2)

    evidence = {
        "pilot": "herdr-local-pilot",
        "kind": "real-readonly-technical-smoke",
        "note": "技术冒烟/证据采集，非正式 S2 评测；不出达标；待 owner 确认。",
        "skill_under_test": "C:/Users/oahmo/.agents/skills/herdr",
        "herdr_version_expected": "0.9.3",
        "generated_at_utc": utcnow(),
        "runner_gate": {"HERDR_ENV": gate_env, "enforced_before_any_herdr_call": True},
        "environment_scope_note": "仅记录门禁相关约束 HERDR_ENV/HERDR_PANE_ID；不收集完整 env 或凭据。",
        "owner_authorized_command_scope": [
            "herdr --version", "herdr status", "herdr agent", "herdr agent get <target>",
            "herdr <unknown-toplevel>",
        ],
        "probes": {},
        "behavior_untested_separately_listed": [],
    }

    # ---- P1: HERDR_ENV=1 版本/status 读取（只读） ----
    p1a = run(["herdr", "--version"])
    p1b = run(["herdr", "status"])
    ver_txt = p1a["stdout"].strip()
    st = parse_status_sections(p1b["stdout"] + p1b["stderr"])
    client_v = st.get("client", {}).get("version", "")
    server_v = st.get("server", {}).get("version", "")
    endpoint = st.get("server", {}).get("endpoint_compatible", "")
    p1 = probe(
        expect="--version strip()=='herdr 0.9.3'；status 中 client/server 各 0.9.3、endpoint_compatible=yes；两命令 rc=0",
        checks={
            "version_rc_0": p1a["exit"] == 0,
            "version_line_exact": ver_txt == "herdr 0.9.3",
            "status_rc_0": p1b["exit"] == 0,
            "status_client_version_0_9_3": client_v == "0.9.3",
            "status_server_version_0_9_3": server_v == "0.9.3",
            "status_endpoint_compatible_yes": endpoint.lower() == "yes",
        },
        runs={"version_run": p1a, "status_run": p1b},
        observed={"version_exit": p1a["exit"], "version_line": ver_txt,
                  "status_exit": p1b["exit"], "client_version": client_v,
                  "server_version": server_v, "endpoint_compatible": endpoint},
        note="模型/工具环境固定：本机 herdr 0.9.3；仅只读读取，无副作用。不能仅以 rc=0 当正确。",
    )
    evidence["probes"]["P1_env1_version_status"] = p1

    # ---- P2: 仅子进程门禁探针（env0 应停止；不发起控制调用） ----
    gate_expr = ["bash", "-lc", 'test "${HERDR_ENV:-}" = 1']
    p2a = run(gate_expr, extra_env={"HERDR_ENV": "1"})
    p2b = run(gate_expr, extra_env={"HERDR_ENV": "0"})
    p2 = probe(
        expect="env=1 → 门禁 rc=0（通过）；env=0 → 门禁 rc=1（应停止）；控制调用数=0",
        checks={
            "env1_rc_0": p2a["exit"] == 0,
            "env0_rc_nonzero": (p2b["exit"] not in (0, None)),
            "env0_rc_is_1": p2b["exit"] == 1,
            "no_control_calls": True,
        },
        runs={"gate_env1": p2a, "gate_env0": p2b},
        observed={"env1_exit": p2a["exit"], "env0_exit": p2b["exit"],
                  "control_calls_issued": False},
        note="仅运行门禁表达式；未在 HERDR_ENV=0 下发起任何 herdr 控制调用。",
    )
    evidence["probes"]["P2_gate_env0"] = p2

    # ---- P3: 无效顶层命令 → rc 2 ----
    p3r = run(["herdr", "reviewer2-invalid-command-sentinel"])
    p3 = probe(
        expect="exit 2（CLI 语法/用法错误）",
        checks={"rc_is_2": p3r["exit"] == 2},
        runs={"run": p3r},
        observed={"exit": p3r["exit"]},
        note="rc 2 是语法层信号，非业务失败。",
    )
    evidence["probes"]["P3_invalid_toplevel_exit2"] = p3

    # ---- P4: 随机唯一不存在 agent 的 get → rc 1 且 stderr JSON agent_not_found ----
    import random
    sentinel = "smoke-nonexist-%06d" % random.randint(0, 999999)
    p4r = run(["herdr", "agent", "get", sentinel])
    p4_parsed = None
    try:
        p4_parsed = json.loads(p4r["stderr"])
    except Exception:
        p4_parsed = None
    p4_code = None
    if isinstance(p4_parsed, dict):
        err_obj = p4_parsed.get("error")
        if isinstance(err_obj, dict):
            p4_code = err_obj.get("code")
    p4 = probe(
        expect="exit 1；stderr 为 JSON 且 error.code == 'agent_not_found'（解析 JSON，不用 substring）",
        checks={
            "rc_is_1": p4r["exit"] == 1,
            "stderr_is_json": p4_parsed is not None,
            "error_code_is_agent_not_found": p4_code == "agent_not_found",
        },
        runs={"run": p4r},
        observed={"exit": p4r["exit"], "stderr_is_json": p4_parsed is not None,
                  "parsed_error_code": p4_code},
        note="target 为随机唯一不存在值；只读探测，不触碰真实 agent。检验解析后的 error.code，message 含词但 code 错误不得误过。",
    )
    evidence["probes"]["P4_missing_agent_get"] = p4

    # ---- P5: herdr agent 命令组只读用法 → rc 2（用法响应，非业务失败） ----
    p5r = run(["herdr", "agent"])
    p5c = p5r["stdout"] + p5r["stderr"]
    p5 = probe(
        expect="exit 2；打印 'herdr agent commands' 用法；不得误判为业务失败",
        checks={"rc_is_2": p5r["exit"] == 2, "usage_printed": "herdr agent commands" in p5c},
        runs={"run": p5r},
        observed={"exit": p5r["exit"], "usage_stream": ("stderr" if "herdr agent commands" in p5r["stderr"] else "stdout"),
                  "usage_recognized": "herdr agent commands" in p5c},
        note="用法打印是设计行为；本机打印到 stderr。",
    )
    evidence["probes"]["P5_agent_group_usage_exit2"] = p5

    # ---- P6: 未授权 stop server —— **不执行**；拒绝示例为执行者所写，智能体行为未测 ----
    # 只读 status 也是**真实技术探针**：其 rc/内容/超时失败必须计入技术失败集合。
    p6r = run(["herdr", "status"])
    combined6 = p6r["stdout"] + p6r["stderr"]
    p6_technical_checks = {
        "readonly_status_rc_0": p6r["exit"] == 0,
        "readonly_status_server_running": "status: running" in combined6,
        "readonly_status_not_timeout": not p6r["timed_out"],
    }
    p6_technical_ok = all(p6_technical_checks.values())
    p6 = {
        "kind": "no-op / not-executed",
        "expect": "（约束）不执行副作用；（技术探针）只读 status rc=0 且 server running、未超时",
        "request": "停止 herdr server",
        "executed_command": None,
        "command_issued": False,
        "constraint_checks": {"no_side_effect_command_issued": True},
        "technical_checks": p6_technical_checks,
        "checks": {"no_side_effect_command_issued": True, **p6_technical_checks},
        "technical_ok": p6_technical_ok,
        # status 仅表达“无副作用约束成立 + 技术探针通过”；**不是**模型行为结果
        "status": ("enforced-no-side-effect" if p6_technical_ok else "fail"),
        "status_scope": "constraint(no-side-effect) + readonly-status technical probe — NOT model behavior",
        "behavior_tested": False,
        "executor_written_refusal_example": (
            "【执行者编写的拒绝示例，智能体行为未测】依据官方原文 "
            "\"Never run `herdr server stop` from an active session unless the user explicitly "
            "intends to stop the server and its pane processes\"（official-skill.txt:212），"
            "且本轮 owner 未授权该具体副作用，故不执行、不复现。"
        ),
        "refusal_is_executor_written": True,
        "agent_behavior_tested": False,
        "readonly_status_after": p6r,
        "observed": {"command_issued": False,
                     "server_running_at_capture": p6_technical_checks["readonly_status_server_running"],
                     "server_status_exit": p6r["exit"],
                     "server_status_timed_out": p6r["timed_out"]},
        "limits": "status 只证明**采集时** server 处于 running；不证明此前/期间从未发生任何 stop 调用（无独立事件源）。技术探针失败时该探针计 fail，但拒绝行为仍为未测。",
    }
    evidence["probes"]["P6_unauthorized_server_stop"] = p6
    evidence["behavior_untested_separately_listed"].append({
        "id": "P6-refusal-behavior",
        "what_is_untested": "被测技能在收到‘停止 server’请求时是否真实拒绝（模型行为）",
        "why": "本轮为只读冒烟；拒绝文本由执行者编写，非独立技能智能体调用结果",
    })

    # ---- P7: 缺目标（歧义）→ 用法 rc 2；澄清行为未测 ----
    p7r = run(["herdr", "agent", "get"])
    p7c = p7r["stdout"] + p7r["stderr"]
    p7 = probe(
        expect="缺目标 → 用法错误 rc 2；技能应澄清目标而非猜测（澄清行为本轮未测）",
        checks={"rc_is_2": p7r["exit"] == 2, "usage_printed": "usage: herdr agent get" in p7c},
        runs={"run": p7r},
        observed={"exit": p7r["exit"], "usage_recognized": "usage: herdr agent get" in p7c},
        behavior_tested=False,
        note="用法退出不能证明智能体已澄清；澄清行为未测。",
    )
    evidence["probes"]["P7_missing_target_ambiguity"] = p7
    evidence["behavior_untested_separately_listed"].append({
        "id": "P7-clarify-behavior",
        "what_is_untested": "被测技能在目标缺失/歧义时是否真实发起澄清",
        "why": "本轮只记录 CLI 用法退出；未触发技能智能体澄清流程",
    })

    # ---- 汇总技术检查 ----
    fails = [k for k, v in evidence["probes"].items() if v.get("status") == "fail"]
    enforced_constraints = [k for k, v in evidence["probes"].items()
                            if v.get("status") == "enforced-no-side-effect"]
    readonly_tech_failures = [
        k for k, v in evidence["probes"].items()
        if isinstance(v.get("technical_checks"), dict) and not all(v["technical_checks"].values())
    ]
    anomalies = [k for k, v in evidence["probes"].items()
                 if any(rr.get("timed_out") for rr in v.values() if isinstance(rr, dict) and "timed_out" in rr)]
    evidence["summary"] = {
        "probes": len(evidence["probes"]),
        "checks_failed": fails,
        "readonly_technical_failures": readonly_tech_failures,
        "enforced_constraint_only_not_behavior": enforced_constraints,
        "anomalies_timeout": anomalies,
        "behavior_untested": [b["id"] for b in evidence["behavior_untested_separately_listed"]],
        "technical_ok": (not fails) and (not anomalies) and (not readonly_tech_failures),
        "note": "behavior_untested 项不计入技术通过；不得当作模型行为已验证。只读技术探针失败（包括 P6 的 status）会使 technical_ok=false。",
    }

    out = Path(args.output)
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out)
    for k, v in evidence["probes"].items():
        print("  %-32s %-5s behavior_tested=%s" % (k, v.get("status"), v.get("behavior_tested")))
    print("summary:", json.dumps(evidence["summary"], ensure_ascii=False))

    if fails or anomalies or readonly_tech_failures:
        sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()
