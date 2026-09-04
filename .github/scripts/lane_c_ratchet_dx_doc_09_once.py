from __future__ import annotations

from pathlib import Path
import subprocess


OLD = Path("01_Plans/issues/issue-DX-DOC-09-backtick-path-citations-unchecked-by-link-checker.md")
NEW = Path("01_Plans/issues/done/issue-DX-DOC-09-backtick-path-citations-unchecked-by-link-checker.md")
VALIDATOR = Path("01_Plans/issues/validate_active_issue_memos.py")


def replace_references() -> None:
    old_ref = OLD.as_posix()
    new_ref = NEW.as_posix()
    completed = subprocess.run(
        ["git", "grep", "-Il", "-F", old_ref, "--", f":!{NEW.as_posix()}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode not in (0, 1):
        detail = completed.stderr.strip() or f"exit={completed.returncode}"
        raise SystemExit(f"旧パス引用の探索に失敗しました: {detail}")

    for name in [line for line in completed.stdout.splitlines() if line]:
        path = Path(name)
        body = path.read_text(encoding="utf-8")
        updated = body.replace(old_ref, new_ref)
        if updated == body:
            raise SystemExit(f"旧パス引用の置換が空振りしました: {name}")
        path.write_text(updated, encoding="utf-8")
        print(f"updated reference: {name}")


def main() -> None:
    if not OLD.exists():
        raise SystemExit(f"移動元がありません: {OLD}")
    if NEW.exists():
        raise SystemExit(f"移動先がすでに存在します: {NEW}")

    subprocess.run(["git", "mv", OLD.as_posix(), NEW.as_posix()], check=True)

    validator_text = VALIDATOR.read_text(encoding="utf-8")
    before = "LEGACY_DONE_AT_ROOT_BASELINE = 58"
    after = "LEGACY_DONE_AT_ROOT_BASELINE = 57"
    if validator_text.count(before) != 1:
        raise SystemExit("legacy Done baseline 58 の定義を一意に特定できません")
    VALIDATOR.write_text(validator_text.replace(before, after), encoding="utf-8")

    replace_references()

    moved = NEW.read_text(encoding="utf-8")
    heading = "## 配置の整理（2026-09-05）"
    if heading in moved:
        raise SystemExit("配置整理の記録がすでに存在します")

    moved += f"""

{heading}

- 本Issueは内容上すべての受入条件を満たして `Done` となっていた一方、R18以前からの経緯によりactive rootに残る58件のlegacy集合へ含まれていた。
- 既存のライフサイクル契約は、この58件を恒久的にrootへ置くことを認めるものではない。移行のたびに `LEGACY_DONE_AT_ROOT_BASELINE` を同じ変更で下げる、単調減少のラチェットとして設計されている。
- その契約に従い、本Issueを `01_Plans/issues/done/` へ移し、baselineを58から57へ縮小した。R18時点のidentity manifestは「新しいDone-at-rootを紛れ込ませない」歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
"""
    NEW.write_text(moved, encoding="utf-8")


if __name__ == "__main__":
    main()
