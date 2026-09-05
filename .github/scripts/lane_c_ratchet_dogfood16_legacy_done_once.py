from __future__ import annotations

from pathlib import Path
import subprocess


TARGET = "issue-DOGFOOD-16-refine-card-text-meaning-preservation-unverifiable.md"
ISSUES_ROOT = Path("01_Plans/issues")
DONE_ROOT = ISSUES_ROOT / "done"
VALIDATOR = ISSUES_ROOT / "validate_active_issue_memos.py"
SCRIPT_PATH = Path(".github/scripts/lane_c_ratchet_dogfood16_legacy_done_once.py")


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


def main() -> None:
    old = ISSUES_ROOT / TARGET
    new = DONE_ROOT / TARGET
    if not old.exists():
        raise SystemExit(f"移動元がありません: {old}")
    if new.exists():
        raise SystemExit(f"移動先がすでに存在します: {new}")
    body = old.read_text(encoding="utf-8")
    if "- Status: Done" not in body:
        raise SystemExit(f"Status Doneではないため移動しません: {old}")

    validator_text = VALIDATOR.read_text(encoding="utf-8")
    before = "LEGACY_DONE_AT_ROOT_BASELINE = 34"
    after = "LEGACY_DONE_AT_ROOT_BASELINE = 33"
    if validator_text.count(before) != 1:
        raise SystemExit("legacy Done baseline 34 の定義を一意に特定できません")

    subprocess.run(["git", "mv", old.as_posix(), new.as_posix()], check=True)
    VALIDATOR.write_text(validator_text.replace(before, after), encoding="utf-8")

    refs = replace_exact_reference(old, new)
    print(f"{old.name}: updated references={len(refs)}")
    for ref in refs:
        print(f"  - {ref}")

    body = new.read_text(encoding="utf-8")
    body += """

## 配置の整理（2026-09-05）

- 本Issueは、`refine-card-text` の製品契約を変えず、モックと業務フローE2Eで入力由来の意味保持を決定的に検証できるようにし、シナリオ111を含む 657/657 pass まで確認して `Done` となっていた。
- 2026-09-05の残存39件参照グラフ監査で、他のlegacy Doneとの系列内ID参照を持たない孤立成分であり、旧rootパスの外部引用もないことを確認した。
- 既存のライフサイクル契約に従い、本変更では本Issueを `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を34から33へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
"""
    new.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
