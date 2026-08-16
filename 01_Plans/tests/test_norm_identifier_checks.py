"""Verify DC-NORM-001/002/003 actually detect what they claim to.

A rule that never fires is indistinguishable from no rule. Each check below is
run against a deliberately broken input and must produce a finding, then against
the real repository and must be clean.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from docs_contract_checks import (  # noqa: E402
    check_norm_identifier_resolution,
    check_prompt_status_vocabulary,
    check_norm_identifier_uniqueness,
    check_norm_line_references,
)

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "00_Prompt"

md_paths = sorted(
    p.relative_to(ROOT)
    for p in ROOT.rglob("*.md")
    if not any(part in {".git", "node_modules", "build"} for part in p.parts)
)

failures = 0


def report(name: str, ok: bool, detail: str = "") -> None:
    global failures
    print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not ok:
        failures += 1


# --- baseline: the real repository must be clean --------------------------
uniq = check_norm_identifier_uniqueness(ROOT)
report("baseline uniqueness clean", not uniq, f"{len(uniq)} findings")

res = check_norm_identifier_resolution(ROOT, md_paths)
report(
    "baseline resolution clean",
    not res,
    "; ".join(f"{f.path}:{f.line} {f.target}" for f in res[:5]),
)

lines = check_norm_line_references(ROOT, md_paths)
report(
    "baseline line-reference clean",
    not lines,
    "; ".join(f"{f.path}:{f.line} {f.target}" for f in lines[:5]),
)

# --- mutation 1: an unresolvable reference must be caught ------------------
probe = ROOT / "01_Plans" / "_norm_probe.md"
probe.write_text("参照テスト: DOM-CORE-99 は存在しない。\n", encoding="utf-8")
try:
    found = check_norm_identifier_resolution(ROOT, md_paths + [probe.relative_to(ROOT)])
    hit = [f for f in found if f.target == "DOM-CORE-99"]
    report("mutation: unresolvable reference detected", bool(hit))
finally:
    probe.unlink()

# --- mutation 2: a line-number citation must be caught ---------------------
probe.write_text("行番号参照: `00_Prompt/domain.md:88` を見よ。\n", encoding="utf-8")
try:
    found = check_norm_line_references(ROOT, md_paths + [probe.relative_to(ROOT)])
    hit = [f for f in found if f.target == "00_Prompt/domain.md:88"]
    report("mutation: line-number citation detected", bool(hit))
finally:
    probe.unlink()

# --- mutation 3: a duplicate definition must be caught --------------------
dup = PROMPT / "_dup_probe.md"
dup.write_text("### DOM-CORE-01 重複定義\n", encoding="utf-8")
try:
    found = check_norm_identifier_uniqueness(ROOT)
    hit = [f for f in found if f.target == "DOM-CORE-01"]
    report("mutation: duplicate definition detected", bool(hit))
finally:
    dup.unlink()

# --- a valid reference must NOT be flagged --------------------------------
probe.write_text("正当な参照: DOM-CORE-02 に従う。\n", encoding="utf-8")
try:
    found = check_norm_identifier_resolution(ROOT, md_paths + [probe.relative_to(ROOT)])
    hit = [f for f in found if f.target == "DOM-CORE-02"]
    report("valid reference not flagged", not hit)
finally:
    probe.unlink()

# --- DC-NORM-004: controlled Status vocabulary ----------------------------
status = check_prompt_status_vocabulary(ROOT)
report(
    "baseline status vocabulary clean",
    not status,
    "; ".join(f"{f.path} {f.target}" for f in status[:5]),
)

bad = PROMPT / "_status_probe.md"
bad.write_text("# probe\n\n- Status: Normative（追跡情報つき）\n", encoding="utf-8")
try:
    found = check_prompt_status_vocabulary(ROOT)
    report(
        "mutation: uncontrolled Status value detected",
        any(f.path.endswith("_status_probe.md") for f in found),
    )
finally:
    bad.unlink()

bad.write_text("# probe\n\n（Status なし）\n", encoding="utf-8")
try:
    found = check_prompt_status_vocabulary(ROOT)
    report(
        "mutation: missing Status detected",
        any(f.path.endswith("_status_probe.md") for f in found),
    )
finally:
    bad.unlink()

# --- checklist items are citable and validated ----------------------------
probe.write_text("存在する: CHK-X3 / 存在しない: CHK-X9\n", encoding="utf-8")
try:
    found = check_norm_identifier_resolution(ROOT, md_paths + [probe.relative_to(ROOT)])
    bad = [f.target for f in found if f.path.endswith("_norm_probe.md")]
    report("mutation: unknown checklist item detected", "CHK-X9" in bad)
    report("valid checklist item not flagged", "CHK-X3" not in bad)
finally:
    probe.unlink()

print()
print("FAILURES:", failures)
sys.exit(1 if failures else 0)
