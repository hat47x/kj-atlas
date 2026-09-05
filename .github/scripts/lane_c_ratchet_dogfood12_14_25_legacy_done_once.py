from __future__ import annotations

from pathlib import Path
import subprocess


TARGETS = (
    "issue-DOGFOOD-12-check-narrative-positive-path-hardcodes-island-i1.md",
    "issue-DOGFOOD-14-check-narrative-lacks-b-missing-in-a-positive-path.md",
    "issue-DOGFOOD-25-check-narrative-multi-island-omission.md",
)
ISSUES_ROOT = Path("01_Plans/issues")
DONE_ROOT = ISSUES_ROOT / "done"
VALIDATOR = ISSUES_ROOT / "validate_active_issue_memos.py"
SCRIPT_PATH = Path(".github/scripts/lane_c_ratchet_dogfood12_14_25_legacy_done_once.py")


def replace_exact_reference(old: Path, new: Path) -> list[str]:
    completed = subprocess.run(
        [
            "git", "grep", "-Il", "-F", old.as_posix(), "--",
            f":!{SCRIPT_PATH.as_posix()}", f":!{new.as_posix()}",
        ],
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

- 本Issueは、`check-narrative` のA/B照合を島ID非依存・双方向・複数島へ段階的に拡張し、任意の図解／ナラティブで検出セマンティクスをE2E固定できるようにした verification harness 改善として `Done` となっていた。
- `DOGFOOD-12` が島ID固定を解消し、`DOGFOOD-14` が反対方向 `b_missing_in_a` の正パスを追加し、`DOGFOOD-25` が複数島の取りこぼしへ拡張したため、check-narrative の成熟系列として3件を同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は23から20へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
"""
    path.write_text(body, encoding="utf-8")


def main() -> None:
    validator = VALIDATOR.read_text(encoding="utf-8")
    before = "LEGACY_DONE_AT_ROOT_BASELINE = 23"
    after = "LEGACY_DONE_AT_ROOT_BASELINE = 20"
    if validator.count(before) != 1:
        raise SystemExit("legacy Done baseline 23 を一意に特定できません")

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
