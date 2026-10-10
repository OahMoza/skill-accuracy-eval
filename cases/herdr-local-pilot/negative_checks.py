#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
negative_checks.py — 用替换 run() 的假返回，证明 3 类检查漏洞**会**被判失败。

- 仅使用假返回，**不运行任何真实命令**（不调 herdr、不碰真实 evidence.json）。
- 每个 case 在自有的 `TemporaryDirectory` 内写出证据，退出时自动清理。
- 用 `unittest.mock.patch.dict/patch.object` 临时改 `os.environ` / `sys.argv`，
  用例结束自动还原，不给导入调用者留下状态；装载时不写 `.pyc`（临时禁 `dont_write_bytecode` 并还原）。

用法：python negative_checks.py
预期：T1/T2/T3/T4 四个检查 PASS，退出 0。
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent


def load_module(fake_run):
    """每次装载一个干净模块，并把其 run 替换为假函数（仅假返回，不执行真实命令）。"""
    spec = importlib.util.spec_from_file_location("run_smoke", str(HERE / "run_smoke.py"))
    m = importlib.util.module_from_spec(spec)
    prev_dwb = sys.dont_write_bytecode
    sys.dont_write_bytecode = True          # 不落 __pycache__，也不给调用者留状态
    try:
        spec.loader.exec_module(m)
    finally:
        sys.dont_write_bytecode = prev_dwb

    def wrapper(argv, extra_env=None, timeout=60):
        return fake_run(list(argv), extra_env)

    m.run = wrapper
    return m


def run_case(fake_run):
    """在自有的临时目录内跑一个 case；退出即清理；不改动调用者的环境/argv。"""
    m = load_module(fake_run)
    with tempfile.TemporaryDirectory(prefix="herdr_neg_") as td:
        out = Path(td) / "evidence.json"          # 每次自有输出，退出自动清理
        with mock.patch.dict(os.environ, {"HERDR_ENV": "1"}):
            with mock.patch.object(sys, "argv", ["run_smoke.py", "--output", str(out)]):
                rc = None
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        m.main()                  # run_smoke 的 print 不污染本脚本输出
                except SystemExit as e:
                    rc = e.code
        data = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
    return m, rc, data


def mk(exit=0, stdout="", stderr="", timed_out=False):
    return {"argv": [], "env_constraints": {"HERDR_ENV": "1"}, "utc_start": "X", "utc_end": "X",
            "duration_ms": 1.0, "exit": exit, "timed_out": timed_out, "stdout": stdout,
            "stderr": stderr, "stdout_sha256": "x", "stderr_sha256": "x",
            "stdout_bytes": len(stdout), "stderr_bytes": len(stderr)}


def good_dispatch(argv, extra_env):
    """正常基线：用于验证其余探针通过、仅被注入口出错。"""
    if argv and argv[0] == "bash":      # 门禁探针
        env = extra_env or {}
        return mk(0, "") if env.get("HERDR_ENV") == "1" else mk(1, "")
    if argv[:2] == ["herdr", "--version"]:
        return mk(0, "herdr 0.9.3\n")
    if argv[:2] == ["herdr", "status"]:
        return mk(0, "client:\n  version: 0.9.3\nserver:\n  status: running\n  version: 0.9.3\n"
                     "  endpoint_compatible: yes\n")
    if argv[:2] == ["herdr", "agent"] and len(argv) == 2:
        return mk(2, "", "herdr agent commands:\n  herdr agent get <target>\n")
    if argv[:3] == ["herdr", "agent", "get"] and len(argv) == 3:
        return mk(2, "", "usage: herdr agent get <target>\n")
    if argv[:3] == ["herdr", "agent", "get"]:
        return mk(1, "", json.dumps({"error": {"code": "agent_not_found", "message": "x"}}))
    # 无效顶层 / 其他
    return mk(2, "", "unknown command\n")


def main():
    results = []

    # ---- T1: rc=0 但内容不符（版本尾随串；status client 版本错 + endpoint no）→ 必须 fail ----
    def fake1(argv, extra_env):
        if argv[:2] == ["herdr", "--version"]:
            return mk(0, "herdr 0.9.3 (build extra)\n")          # strip() != "herdr 0.9.3"
        if argv[:2] == ["herdr", "status"]:
            return mk(0, "client:\n  version: 0.9.4\nserver:\n  status: running\n"
                         "  version: 0.9.3\n  endpoint_compatible: no\n")
        return good_dispatch(argv, extra_env)
    _, rc, data = run_case(fake1)
    p1 = data["probes"]["P1_env1_version_status"]
    ok = (rc == 3 and p1["status"] == "fail"
          and p1["checks"]["version_line_exact"] is False
          and p1["checks"]["status_client_version_0_9_3"] is False
          and p1["checks"]["status_endpoint_compatible_yes"] is False)
    results.append(("T1 rc0-but-wrong-content must fail", ok, {"rc": rc, "p1_status": p1["status"],
                                                             "checks": p1["checks"]}))

    # ---- T2: stderr 含 "agent_not_found" 子串但 error.code 不是 → 必须 fail ----
    def fake2(argv, extra_env):
        if argv[:3] == ["herdr", "agent", "get"] and len(argv) == 4:
            return mk(1, "", json.dumps(
                {"error": {"code": "agent_not_ready",
                           "message": "target mentions agent_not_found in text"}}))
        return good_dispatch(argv, extra_env)
    _, rc, data = run_case(fake2)
    p4 = data["probes"]["P4_missing_agent_get"]
    ok = (rc == 3 and p4["status"] == "fail"
          and p4["checks"]["error_code_is_agent_not_found"] is False
          and p4["observed"]["parsed_error_code"] == "agent_not_ready")
    results.append(("T2 substring-but-wrong-code must fail", ok, {"rc": rc, "p4_status": p4["status"],
                                                                  "observed": p4["observed"]}))

    # ---- T3: P6 只读 status rc!=0 → technical_ok 必须 False，行为仍未测 ----
    def fake3(argv, extra_env):
        if argv[:2] == ["herdr", "status"]:
            return mk(1, "", '{"error":{"code":"server_unavailable"}}')      # 技术探针失败
        return good_dispatch(argv, extra_env)
    _, rc, data = run_case(fake3)
    p6 = data["probes"]["P6_unauthorized_server_stop"]
    s = data["summary"]
    ok = (rc == 3 and s["technical_ok"] is False
          and "P6_unauthorized_server_stop" in s["readonly_technical_failures"]
          and p6["technical_ok"] is False
          and p6["checks"]["readonly_status_rc_0"] is False
          and p6["behavior_tested"] is False
          and p6["agent_behavior_tested"] is False
          and p6["refusal_is_executor_written"] is True)
    results.append(("T3 P6 status-failure must fail technical_ok; behavior stays untested", ok,
                    {"rc": rc, "summary": s, "p6_technical": p6["checks"],
                     "p6_status": p6["status"], "behavior_tested": p6["behavior_tested"]}))

    # ---- T4: 基线（全好）→ rc 0, technical_ok True（证明假函数本身能通过） ----
    _, rc, data = run_case(lambda a, e: good_dispatch(a, e))
    ok = (rc == 0 and data["summary"]["technical_ok"] is True)
    results.append(("T4 baseline must pass", ok, {"rc": rc, "technical_ok": data["summary"]["technical_ok"]}))

    all_ok = all(r[1] for r in results)
    for name, ok, extra in results:
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            print("   detail:", json.dumps(extra, ensure_ascii=False))
    print("\nOVERALL:", "ALL NEGATIVE CHECKS BEHAVE AS EXPECTED" if all_ok else "SOME CHECKS DID NOT FAIL AS EXPECTED")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
