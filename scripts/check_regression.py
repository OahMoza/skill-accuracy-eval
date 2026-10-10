#!/usr/bin/env python3
"""skill-accuracy-eval 仓库回归检查入口。

仓库维护工具，**不属于被测技能执行依赖**（package.json files 白名单不含 scripts/）。
依赖（维护者自备，不自动安装）：Python 3.8+、PyYAML（pip install pyyaml）、Node >= 14。

用法：
  python scripts/check_regression.py             # 检查本仓库
  python scripts/check_regression.py --selftest  # 自检：篡改临时副本，证明能捕捉关键回归
  python scripts/check_regression.py --root DIR  # 检查指定目录（自检内部使用）

检查项（任一 FAIL 退出码非零）：
  1. frontmatter 真实 YAML 解析 / schema / 关键标识符 / 三处版本同步
  2. markdown 表格列数（表头=分隔行=数据行；忽略代码围栏与转义竖线）
  3. CRM 逐例三维度重算，与报告汇总 / 量化演示 / 复跑勘误数字对账
  4. 安装器 5 组边界（Node vm 假 fs：缺参 / 空串 / 空白 / flag / 合法路径；不真实安装）
  5. 关键文件 / 章节引用存在性（真实解析引用目标，非关键词扫描）

范围：cases/herdr-local-pilot（试点工作目录）不在本检查范围，由其工作流自管。
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    print("缺依赖：PyYAML。请维护者自行安装：pip install pyyaml（本工具不自动安装依赖）")
    sys.exit(2)

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
DIMS = ("结果正确性", "规则与边界", "可靠与兜底")
SKIP_DIRS = {".git", "node_modules", "%SystemDrive%"}
SKIP_SUBPATHS = (("cases", "herdr-local-pilot"),)
FILE_REF = re.compile(r"(?:(?:references|assets|cases|docs|scripts)/)?[A-Za-z0-9_\-./]+\.md")
SEC_REF = re.compile(r"§(\d+(?:\.\d+)?|[一二三四五六七八九十]{1,3})(?![\d.])")
CHINESE = {"一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"}


def _skipped(parts):
    if any(p in SKIP_DIRS for p in parts):
        return True
    return any(parts[i:i + 2] == sub for sub in SKIP_SUBPATHS for i in range(len(parts) - 1))


def md_files(root):
    for p in sorted(Path(root).rglob("*.md")):
        if not _skipped(p.parts):
            yield p


def lines_with_fence(path):
    """逐行产出 (line, in_fence)：``` 围栏内不参与表格/引用检查。"""
    fence = False
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            yield line, True
        else:
            yield line, fence


def unescaped_pipes(line):
    return len(re.findall(r"(?<!\\)\|", line))


# ---------- 1. frontmatter / schema / 三处版本同步 ----------

def check_frontmatter(root):
    root = Path(root)
    errs = []
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
    if not m:
        return ["SKILL.md frontmatter 未找到（--- 包裹缺失）"]
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as e:
        return [f"frontmatter YAML 解析失败: {e}"]
    if not isinstance(fm, dict):
        return ["frontmatter 解析结果不是映射"]
    if "version" in fm:
        errs.append("顶层 version 字段应在 metadata 下（metadata.version）")
    name = fm.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or ""):
        errs.append(f"name 不合规: {name!r}")
    elif len(name) > 64:
        errs.append(f"name 超长: {len(name)} > 64")
    elif name != root.name:
        errs.append(f"name ({name}) 与目录名 ({root.name}) 不一致")
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc:
        errs.append("description 缺失或为空")
    else:
        if len(desc) > 1024:
            errs.append(f"description 超长: {len(desc)} > 1024 字符")
        if "\xa0" in desc:
            errs.append("description 含 NBSP（\\xa0），关键标识符可能已损坏")
    meta = fm.get("metadata")
    v_skill = str(meta.get("version")) if isinstance(meta, dict) else ""
    if not v_skill:
        errs.append("metadata.version 缺失")
    pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
    v_pkg = str(pkg.get("version", ""))
    fork = (root / "fork-sop.md").read_text(encoding="utf-8")
    row = re.search(r"\|---\|---\|---\|---\|\n\| \d{4}-\d{2}-\d{2} \| (v[\d.]+) \|", fork)
    v_fork = row.group(1).lstrip("v") if row else ""
    if len({v_skill, v_pkg, v_fork}) > 1:
        errs.append(f"三处版本不同步: SKILL.metadata={v_skill} package.json={v_pkg} fork-sop 表首行={v_fork}")
    return errs


# ---------- 2. markdown 表格列数 ----------

def check_tables(root):
    errs = []
    for path in md_files(root):
        rows = list(lines_with_fence(path))
        i = 0
        while i < len(rows):
            line, fence = rows[i]
            if fence or not line.lstrip().startswith("|") or i + 1 >= len(rows):
                i += 1
                continue
            sep_line, sep_fence = rows[i + 1]
            if sep_fence or not re.fullmatch(r"\s*\|[-: |\\]+\|\s*", sep_line):
                i += 1
                continue
            header_cols = unescaped_pipes(line) - 1
            sep_cols = unescaped_pipes(sep_line) - 1
            if header_cols != sep_cols:
                errs.append(f"{path}: 表头 {header_cols} 列 vs 分隔行 {sep_cols} 列（第 {i+1} 行）")
            j = i + 2
            while j < len(rows) and not rows[j][1] and rows[j][0].lstrip().startswith("|"):
                row_cols = unescaped_pipes(rows[j][0]) - 1
                if row_cols != header_cols:
                    errs.append(f"{path}: 数据行 {row_cols} 列 vs 表头 {header_cols} 列（第 {j+1} 行）")
                j += 1
            i = j
    return errs


# ---------- 3. CRM 逐例汇总对账 ----------

def _crm_computed(root):
    report = Path(root) / "assets/examples/crm-retail/evaluation-report.md"
    computed = {d: {"通过": 0, "不通过": 0, "无法判定": 0} for d in DIMS}
    cases = 0
    for block in re.split(r"^### crm-", report.read_text(encoding="utf-8"), flags=re.M)[1:]:
        line = next((x for x in block.splitlines() if x.startswith("| 判定 |")), None)
        if line is None:
            continue
        cases += 1
        for dim in DIMS:
            mm = re.search(dim + r"(不通过|通过|无法判定)", line)
            if mm:
                computed[dim][mm.group(1)] += 1
    return computed, cases


def check_crm(root):
    errs = []
    computed, cases = _crm_computed(root)
    if cases != 6:
        errs.append(f"逐例解析到 {cases} 例（期望 6）")
    docs = {
        "report": Path(root) / "assets/examples/crm-retail/evaluation-report.md",
        "demo": Path(root) / "cases/crm-retail/quantified-threshold-demo.md",
        "rerun": Path(root) / "cases/crm-retail/re-run-2026-09-28.md",
    }
    for dim in DIMS:
        c = computed[dim]
        pf = c["通过"] + c["不通过"]
        exp_pct = round(100 * c["通过"] / pf) if pf else None
        m = re.search(rf"^\|\s*{dim}\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)%（(\d+)/(\d+)）",
                      docs["report"].read_text(encoding="utf-8"), re.M)
        if not m:
            errs.append(f"报告 §二 未找到 {dim} 汇总行")
        else:
            p, f, ne, pct, pn, tt = m.groups()
            if (int(p), int(f), int(ne)) != (c["通过"], c["不通过"], c["无法判定"]):
                errs.append(f"报告 §二 {dim}: 文档 {p}/{f}/{ne} vs 逐例 {c['通过']}/{c['不通过']}/{c['无法判定']}")
            if int(pct) != exp_pct or int(pn) != c["通过"] or int(tt) != cases:
                errs.append(f"报告 §二 {dim}: 通过率/分母 {pct}%（{pn}/{tt}）与逐例不符")
        m = re.search(rf"^\|\s*{dim}\s*\|\s*(\d+)%（(\d+)/(\d+)）vs",
                      docs["demo"].read_text(encoding="utf-8"), re.M)
        if not m:
            errs.append(f"量化演示未找到 {dim} 数值行")
        else:
            pct, pn, tt = m.groups()
            if int(pct) != exp_pct or int(pn) != c["通过"] or int(tt) != cases:
                errs.append(f"量化演示 {dim}: {pct}%（{pn}/{tt}）与逐例不符")
        m = re.search(rf"维度通过率：.*?{dim}\s*(\d+)%（(\d+)/(\d+)）",
                      docs["rerun"].read_text(encoding="utf-8"))
        if not m:
            errs.append(f"复跑勘误行未找到 {dim} 数字")
        else:
            pct, pn, tt = m.groups()
            if int(pct) != exp_pct or int(pn) != c["通过"] or int(tt) != cases:
                errs.append(f"复跑勘误 {dim}: {pct}%（{pn}/{tt}）与逐例不符")
    return errs


# ---------- 4. 安装器 5 组边界（Node vm 假 fs） ----------

def check_installer(root):
    target = Path(root) / "install.js"
    if not target.exists():
        return [f"install.js 不存在: {target}"]
    try:
        r = subprocess.run(["node", str(SCRIPTS_DIR / "check_installer.js"), str(target)],
                           capture_output=True, text=True, encoding="utf-8", timeout=60)
    except FileNotFoundError:
        return ["未找到 node（维护依赖 Node >= 14，请自备，不自动安装）"]
    except subprocess.TimeoutExpired:
        return ["安装器校验超时（60s）"]
    print(r.stdout, end="")
    if r.returncode != 0:
        return [f"安装器 5 组边界校验失败（退出码 {r.returncode}）"]
    return []


# ---------- 5. 文件 / 章节引用存在性 ----------

def _headings(path):
    out = []
    for line, fence in lines_with_fence(path):
        if not fence:
            m = re.match(r"^#{1,6}\s+(.*)$", line)
            if m:
                out.append(m.group(1).strip())
    return out


def _resolve_bare(root, name):
    """裸文件名 → 仓库内唯一 md（优先浅层；找不到返回 None，跳过归属）。"""
    cands = [p for p in Path(root).rglob(name)
             if p.is_file() and p.suffix == ".md" and not _skipped(p.parts)]
    if not cands:
        return None
    cands.sort(key=lambda p: (len(p.parts), str(p)))
    return cands[0]


def _sec_exists(tok, headings):
    if "." in tok:
        return any(re.search(rf"\b{re.escape(tok)}\b", h) for h in headings)
    if tok.isdigit():
        return any(re.match(rf"^{tok}(\.\d+)?[.\s::、]", h) for h in headings)
    if tok in CHINESE:
        return any(h.startswith(tok + "、") for h in headings)
    return False


def check_references(root):
    root = Path(root)
    errs = []
    heading_cache = {}

    def headings_of(path):
        key = str(path)
        if key not in heading_cache:
            heading_cache[key] = _headings(path)
        return heading_cache[key]

    for path in md_files(root):
        for line, fence in lines_with_fence(path):
            if fence:
                continue
            # fork-sop 版本登记表为历史记录：旧章节引用按评审结论保留，不校验（文件引用仍查）
            is_registry_row = re.match(r"^\|\s*\d{4}-\d{2}-\d{2}", line) is not None
            mentions = [(mt.start(), mt.group(0)) for mt in FILE_REF.finditer(line)]
            # 文件引用存在性：仅检查带仓库目录前缀的引用（外部路径如 tau2-bench 的 data/... 不检查）
            for _, ref in mentions:
                if re.match(r"^(references|assets|cases|docs|scripts)/", ref) and not (root / ref).exists():
                    errs.append(f"{path.name}: 引用文件不存在 {ref}")
            if is_registry_row:
                continue
            secs = [(mt.start(), mt.group(1)) for mt in SEC_REF.finditer(line)]
            if "S 专项" in line:
                secs.append((line.find("S 专项"), "S 专项"))
            if not secs:
                continue
            for pos, tok in secs:
                target = None
                for mpos, ref in mentions:  # 位置归属：§ 之前最近的 .md 提及
                    if mpos < pos:
                        if "/" in ref:
                            target = root / ref
                        else:
                            target = _resolve_bare(root, ref)
                if target is None:
                    target = path
                if not target.exists():
                    continue  # 文件级问题已另行报告
                th = headings_of(target)
                if tok == "S 专项":
                    if not any("S 专项" in h for h in th):
                        errs.append(f"{path.name}: 目标 {target.name} 缺少 'S 专项' 章节")
                elif not _sec_exists(tok, th):
                    errs.append(f"{path.name}: 目标 {target.name} 缺少 §{tok} 章节")
    return errs


# ---------- 汇总 / 自检 ----------

CHECKS = [
    ("frontmatter / schema / 三处版本同步", check_frontmatter),
    ("markdown 表格列数", check_tables),
    ("CRM 逐例汇总对账", check_crm),
    ("安装器 5 组边界（Node 假 fs）", check_installer),
    ("文件 / 章节引用存在性", check_references),
]

COPY_ITEMS = ["SKILL.md", "README.md", "package.json", "install.js", "fork-sop.md",
              "references", "assets", "cases", "docs"]  # 复制整个 cases：仅保证 README 引用的文件存在；检查仍按 _skipped 排除 herdr-local-pilot

TAMPERS = [
    ("示例汇总数被篡改（规则与边界 3/3 → 2/4）",
     "assets/examples/crm-retail/evaluation-report.md",
     "| 规则与边界 | 3 | 3 | 0 | 50%（3/6） | 3 |",
     "| 规则与边界 | 2 | 4 | 0 | 33%（2/6） | 3 |",
     "CRM 逐例汇总对账"),
    ("模板表格列被删（10 列 → 9 列）",
     "assets/score-sheet-template.md",
     "| 结果正确性 | | | | | | | 达标 / 未达标 / 禁判 | 充足 / 覆盖不足、仅参考 | |",
     "| 结果正确性 | | | | | | | 达标 / 未达标 / 禁判 | 充足 / 覆盖不足、仅参考 |",
     "markdown 表格列数"),
    ("安装守卫被移除（flag 检查丢失）",
     "install.js",
     " || dirVal.startsWith('-')",
     "",
     "安装器 5 组边界（Node 假 fs）"),
]


def run_all(root):
    total_fail = 0
    print(f"== skill-accuracy-eval 仓库回归检查（root={root}）==")
    for name, fn in CHECKS:
        errs = fn(root)
        if errs:
            total_fail += 1
            print(f"[FAIL] {name}")
            for e in errs[:10]:
                print(f"       - {e}")
            if len(errs) > 10:
                print(f"       … 共 {len(errs)} 条")
        else:
            print(f"[PASS] {name}")
    print(f"RESULT: {'PASS' if total_fail == 0 else f'FAIL（{total_fail} 项）'}")
    return 0 if total_fail == 0 else 1


def run_selftest():
    tmp_base = Path(tempfile.mkdtemp(prefix="sae-selftest-"))
    tmp = tmp_base / "skill-accuracy-eval"  # name=目录名 检查要求副本根目录与本技能同名
    tmp.mkdir()
    caught = 0
    try:
        for item in COPY_ITEMS:
            src, dst = REPO_ROOT / item, tmp / item
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
            elif src.exists():
                shutil.copy2(src, dst)
        # 基线：未篡改副本必须全绿（否则检查器或仓库本身有回归）
        for name, fn in CHECKS:
            if fn(tmp):
                print(f"[SELFTEST-ERROR] 基线异常：{name} 在未篡改副本上已失败")
                return 1
        # 逐项篡改 → 对应检查必须失败 → 还原
        for desc, rel, old, new, check_name in TAMPERS:
            p = tmp / rel
            text = p.read_text(encoding="utf-8")
            if old not in text:
                print(f"[SELFTEST-ERROR] 篡改锚点未找到: {rel} :: {old[:50]}")
                return 1
            p.write_text(text.replace(old, new, 1), encoding="utf-8")
            fn = next(f for n, f in CHECKS if n == check_name)
            errs = fn(tmp)
            p.write_text(text, encoding="utf-8")  # 还原
            if errs:
                caught += 1
                print(f"[CAUGHT] {desc} → {check_name} 捕捉到（{len(errs)} 条）")
            else:
                print(f"[MISSED] {desc} → {check_name} 未捕捉到！")
        print(f"SELFTEST: {caught}/{len(TAMPERS)} 项篡改被捕捉（临时副本已清理，真实文件未动）")
        return 0 if caught == len(TAMPERS) else 1
    finally:
        shutil.rmtree(tmp_base, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="skill-accuracy-eval 仓库回归检查")
    ap.add_argument("--root", default=str(REPO_ROOT), help="仓库根目录（默认：脚本所在仓库）")
    ap.add_argument("--selftest", action="store_true", help="篡改临时副本自检（不改动真实文件）")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(run_selftest())
    sys.exit(run_all(Path(args.root).resolve()))


if __name__ == "__main__":
    main()
