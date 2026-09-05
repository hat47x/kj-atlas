from __future__ import annotations

from pathlib import Path
import subprocess


TARGETS = (
    "issue-QA-MONKEY-21-context-menu-keyboard-focus-and-name.md",
    "issue-QA-MONKEY-24-focused-collapsed-island-expand-update-loop.md",
    "issue-QA-MONKEY-30-start-sample-drops-keyboard-focus.md",
    "issue-QA-MONKEY-31-minimap-toggle-drops-keyboard-focus.md",
    "issue-QA-MONKEY-32-title-candidate-keyboard-and-adoption-clarity.md",
)
ISSUES_ROOT = Path("01_Plans/issues")
DONE_ROOT = ISSUES_ROOT / "done"
VALIDATOR = ISSUES_ROOT / "validate_active_issue_memos.py"
SCRIPT_PATH = Path(".github/scripts/lane_c_ratchet_qa_isolated_legacy_done_once.py")


def replace_exact_reference(old: Path, new: Path) -> list[str]:
    old_ref = old.as_posix()
    new_ref = new.as_posix()
    completed = subprocess.run(
        [
            "git",
            "grep",
            "-Il",
            "-F",
            old_ref,
            "--",
            f":!{SCRIPT_PATH.as_posix()}",
            f":!{new.as_posix()}",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        detail = completed.stderr.strip() or f"exit={completed.returncode}"
        raise SystemExit(f"旧パス引用の探索に失敗しました: {old_ref}: {detail}")

    updated_paths: list[str] = []
    for name in [line for line in completed.stdout.splitlines() if line]:
        path = Path(name)
        body = path.read_text(encoding="utf-8")
        updated = body.replace(old_ref, new_ref)
        if updated == body:
            raise SystemExit(f"旧パス引用の置換が空振りしました: {name}")
        path.write_text(updated, encoding="utf-8")
        updated_paths.append(name)
    return updated_paths


def append_placement_record(path: Path) -> None:
    body = path.read_text(encoding="utf-8")
    heading = "## 配置の整理（2026-09-05）"
    if heading in body:
        raise SystemExit(f"配置整理の記録がすでに存在します: {path}")

    body += f"""

{heading}

- 本Issueは、モンキーテストで見つかった直接のUI／キーボード操作不具合を修正し、個別の回帰確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 2026-09-05の残存39件参照グラフ監査で、本Issueは他のlegacy Doneとの系列内ID参照を持たない孤立成分であり、旧rootパスの外部引用もないことを確認した。
- 既存のライフサイクル契約に従い、本変更ではこの条件を満たすQA-MONKEY完了Issue 5件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を39から34へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
"""
    path.write_text(body, encoding="utf-8")


def main() -> None:
    validator_text = VALIDATOR.read_text(encoding="utf-8")
    before = "LEGACY_DONE_AT_ROOT_BASELINE = 39"
    after = "LEGACY_DONE_AT_ROOT_BASELINE = 34"
    if validator_text.count(before) != 1:
        raise SystemExit("legacy Done baseline 39 の定義を一意に特定できません")

    moved: list[tuple[Path, Path]] = []
    for name in TARGETS:
        old = ISSUES_ROOT / name
        new = DONE_ROOT / name
        if not old.exists():
            raise SystemExit(f"移動元がありません: {old}")
        if new.exists():
            raise SystemExit(f"移動先がすでに存在します: {new}")
        body = old.read_text(encoding="utf-8")
        if "- Status: Done" not in body:
            raise SystemExit(f"Status Doneではないため移動しません: {old}")
        subprocess.run(["git", "mv", old.as_posix(), new.as_posix()], check=True)
        moved.append((old, new))

    VALIDATOR.write_text(validator_text.replace(before, after), encoding="utf-8")

    for old, new in moved:
        refs = replace_exact_reference(old, new)
        print(f"{old.name}: updated references={len(refs)}")
        for ref in refs:
            print(f"  - {ref}")
        append_placement_record(new)


if __name__ == "__main__":
    main()
