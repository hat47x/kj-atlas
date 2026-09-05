from __future__ import annotations

from pathlib import Path
import subprocess

TARGETS = (
    "issue-QA-MONKEY-20-monkey-harness-reports-normal-ui-blocking.md",
    "issue-QA-MONKEY-22-focus-loss-check-does-not-compare-pre-action-state.md",
    "issue-QA-MONKEY-23-selection-clear-drops-keyboard-focus.md",
    "issue-QA-MONKEY-25-card-edit-escape-drops-keyboard-focus.md",
    "issue-QA-MONKEY-26-monkey-test-log-and-cli-drift.md",
    "issue-QA-MONKEY-27-card-edit-enter-drops-keyboard-focus.md",
    "issue-QA-MONKEY-28-focus-loss-check-omits-activation-keys.md",
    "issue-QA-MONKEY-29-card-delete-drops-keyboard-focus.md",
)
ISSUES_ROOT = Path("01_Plans/issues")
DONE_ROOT = ISSUES_ROOT / "done"
VALIDATOR = ISSUES_ROOT / "validate_active_issue_memos.py"
SCRIPT_PATH = Path(".github/scripts/lane_c_ratchet_qa_monkey_final_legacy_done_once.py")


def grep_exact_reference(path: Path, *, exclude: Path | None = None) -> list[str]:
    args = ["git", "grep", "-Il", "-F", path.as_posix(), "--", f":!{SCRIPT_PATH.as_posix()}"]
    if exclude is not None:
        args.append(f":!{exclude.as_posix()}")
    completed = subprocess.run(
        args,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        raise SystemExit(completed.stderr.strip() or f"git grep failed: {path}")
    return [line for line in completed.stdout.splitlines() if line]


def replace_exact_reference(old: Path, new: Path) -> list[str]:
    updated: list[str] = []
    for name in grep_exact_reference(old, exclude=new):
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

- 本Issue群は、2026-08-16のモンキーテストで見つかった誤検知・検出漏れ・キーボードfocus継続性・再現記録のdriftを、QAハーネスと既存UI挙動の境界を崩さず解消した完了系列として `Done` となっていた。
- `QA-MONKEY-20/22/28` は正常な操作遮断や操作前からのbody focusを欠陥扱いしない一方、Enter / Space / Delete / Backspaceを含む実際のfocus脱落は検出できるよう、観測契約を精密化した。
- `QA-MONKEY-23/25/27/29` は選択解除・本文編集の取消/確定・カード削除でDOM要素が消える場合にも、作業文脈へfocusを戻してキーボード操作を継続できる境界を固定した。
- `QA-MONKEY-26` は現行ハーネスに合う再現CLIと実施記録を固定し、観測結果の再現可能性を回復した。
- これらは新しい製品仕様の追加ではなく、既存のアクセシビリティ基準・QA判定・再現性を実装と検証へ反映した完了記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は8から0へ縮小する。R18 identity manifestは不変の歴史境界として維持し、今後 `Status: Done` のmemoがactive rootへ残ることを許容しない。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
"""
    path.write_text(body, encoding="utf-8")


def main() -> None:
    validator = VALIDATOR.read_text(encoding="utf-8")
    before = "LEGACY_DONE_AT_ROOT_BASELINE = 8"
    after = "LEGACY_DONE_AT_ROOT_BASELINE = 0"
    if validator.count(before) != 1:
        raise SystemExit("legacy Done baseline 8 を一意に特定できません")

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

    for old, new in moved:
        leftovers = grep_exact_reference(old, exclude=new)
        if leftovers:
            raise SystemExit(f"旧rootパス引用が残っています: {old.as_posix()} -> {', '.join(leftovers)}")


if __name__ == "__main__":
    main()
