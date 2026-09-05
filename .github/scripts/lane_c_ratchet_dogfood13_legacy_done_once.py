from __future__ import annotations

from pathlib import Path
import subprocess

TARGET = "issue-DOGFOOD-13-island-summary-grounding-capped-at-three-cards.md"
ISSUES_ROOT = Path("01_Plans/issues")
DONE_ROOT = ISSUES_ROOT / "done"
VALIDATOR = ISSUES_ROOT / "validate_active_issue_memos.py"
SCRIPT_PATH = Path(".github/scripts/lane_c_ratchet_dogfood13_legacy_done_once.py")


def replace_exact_reference(old: Path, new: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "grep", "-Il", "-F", old.as_posix(), "--", f":!{SCRIPT_PATH.as_posix()}", f":!{new.as_posix()}"],
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8",
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


def main() -> None:
    old = ISSUES_ROOT / TARGET
    new = DONE_ROOT / TARGET
    if not old.exists() or new.exists():
        raise SystemExit(f"移動境界が不正です: {old} -> {new}")
    if "- Status: Done" not in old.read_text(encoding="utf-8"):
        raise SystemExit(f"Status Doneではありません: {old}")

    validator = VALIDATOR.read_text(encoding="utf-8")
    before = "LEGACY_DONE_AT_ROOT_BASELINE = 18"
    after = "LEGACY_DONE_AT_ROOT_BASELINE = 17"
    if validator.count(before) != 1:
        raise SystemExit("legacy Done baseline 18 を一意に特定できません")

    subprocess.run(["git", "mv", old.as_posix(), new.as_posix()], check=True)
    VALIDATOR.write_text(validator.replace(before, after), encoding="utf-8")

    refs = replace_exact_reference(old, new)
    print(f"{old.name}: updated references={len(refs)}")
    for ref in refs:
        print(f"  - {ref}")

    body = new.read_text(encoding="utf-8")
    body += """

## 配置の整理（2026-09-05）

- 本Issueは、`suggest-island-summary` のモック接地が先頭3カードへ暗黙に打ち切られていた制約を除去し、4カード以上の島でも全メンバー接地をE2Eで固定できるようにした verification harness 改善として `Done` となっていた。
- 後続の `DOGFOOD-33` 以降は複数候補・壁打ち・履歴永続化という機能契約進化を扱うため、本Issueはその系列へ混ぜず、接地検証ハーネスの完了記録として単独で正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は18から17へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
"""
    new.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
