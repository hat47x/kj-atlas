from __future__ import annotations

from pathlib import Path
import subprocess

TARGETS = (
    "issue-DOGFOOD-15-island-relation-summary-grounding-always-empty.md",
    "issue-DOGFOOD-17-opposing-viewpoint-ignores-target-claim.md",
)
ISSUES_ROOT = Path("01_Plans/issues")
DONE_ROOT = ISSUES_ROOT / "done"
VALIDATOR = ISSUES_ROOT / "validate_active_issue_memos.py"
SCRIPT_PATH = Path(".github/scripts/lane_c_ratchet_dogfood15_17_legacy_done_once.py")


def replace_exact_reference(old: Path, new: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "grep", "-Il", "-F", old.as_posix(), "--", f":!{SCRIPT_PATH.as_posix()}", f":!{new.as_posix()}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        raise SystemExit(completed.stderr.strip() or f"git grep failed: {old}")
    updated: list[str] = []
    for name in [line for line in completed.stdout.splitlines() if line]:
        path = Path(name)
        body = path.read_text(encoding="utf-8")
        replaced = body.replace(old.as_posix(), new.as_posix())
        if replaced == body:
            raise SystemExit(f"旧パス引用の置換が空振りしました: {name}")
        path.write_text(replaced, encoding="utf-8")
        updated.append(name)
    return updated


def append_record(path: Path) -> None:
    body = path.read_text(encoding="utf-8")
    heading = "## 配置の整理（2026-09-05）"
    if heading in body:
        raise SystemExit(f"配置整理済みです: {path}")
    body += f"""

{heading}

- 本Issue群は、AI提案が対象データへ意味的に接地していることを、決定的なローカルLLMモックと業務フローE2Eで検証可能にした verification harness 改善として `Done` となっていた。
- `DOGFOOD-15` は島間関係要約の allowed groundingCardIds / groundingEdgeIds をモック応答へ反映し、関係の根拠接地をE2Eで固定した。
- `DOGFOOD-17` は反対視点提案が Target card の主張本文へ応答するようモックを接地し、proposal-only境界を維持したまま対象主張への応答をE2Eで固定した。
- いずれも実LLMの生成品質や製品API契約の変更ではなく、既存契約の意味的な検証能力を高めた完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は12から10へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
"""
    path.write_text(body, encoding="utf-8")


def main() -> None:
    validator = VALIDATOR.read_text(encoding="utf-8")
    before = "LEGACY_DONE_AT_ROOT_BASELINE = 12"
    after = "LEGACY_DONE_AT_ROOT_BASELINE = 10"
    if validator.count(before) != 1:
        raise SystemExit("legacy Done baseline 12 を一意に特定できません")

    moved: list[tuple[Path, Path]] = []
    for name in TARGETS:
        old = ISSUES_ROOT / name
        new = DONE_ROOT / name
        if not old.exists() or new.exists():
            raise SystemExit(f"移動境界が不正です: {old} -> {new}")
        if "- Status: Done" not in old.read_text(encoding="utf-8"):
            raise SystemExit(f"Status Doneではありません: {old}")
        subprocess.run(["git", "mv", old.as_posix(), new.as_posix()], check=True)
        moved.append((old, new))

    VALIDATOR.write_text(validator.replace(before, after), encoding="utf-8")
    for old, new in moved:
        refs = replace_exact_reference(old, new)
        print(f"{old.name}: updated references={len(refs)}")
        for ref in refs:
            print(f"  - {ref}")
        append_record(new)


if __name__ == "__main__":
    main()
