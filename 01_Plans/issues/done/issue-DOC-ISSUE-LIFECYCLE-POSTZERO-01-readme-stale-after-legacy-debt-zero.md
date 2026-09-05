# Issue: DOC-ISSUE-LIFECYCLE-POSTZERO-01 legacy Done-at-root解消後もREADMEが移行中の契約を記述している

- Type: Documentation / Planning integrity
- Status: Done
- Source Issue: Lane C planning lifecycle audit（2026-09-05）
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/issues/README.md`, `01_Plans/issues/validate_active_issue_memos.py`, `01_Plans/tests/test_legacy_done_root_references.py`
- Related ADR/Spec: `01_Plans/issues/done/issue-DOC-ISSUE-LIFECYCLE-01-done-memos-remain-at-active-root.md`, PR #2950, PR #2961
- Expected verification level: docs-check

## 課題

R18で観測された58件のlegacy Done-at-rootは、PR #2950までの段階移行により0件まで解消され、validatorも `LEGACY_DONE_AT_ROOT_BASELINE = 0` へ到達した。さらにPR #2961で、R18 legacy 58件の旧rootパス再出現をtracked files全体から検出する恒久テストが追加された。

一方、`01_Plans/issues/README.md` の「Done配置のlegacy境界」は、依然として次の移行途中の状態を現在形で説明していた。

- active rootに58件が「残っている」
- 一括移動せず段階整理を続ける
- baselineは移行のたびに58→57→…→0へ下げる
- legacy集合がactive rootへ残ることを前提に、path identity guardを説明する

この記述は、現在の機械契約（baseline=0、旧root参照guardあり）と不一致であり、将来の変更者がDone-at-rootを再び許容可能な移行状態だと誤読する余地がある。

## 対応方針

- R18時点で58件存在した事実は、歴史証拠として残す。
- 現行状態を「Done-at-root 0件、移行期間終了」と明示する。
- count ratchetは完了済みであり、今後baselineを0より大きく戻して例外を作らないことを明示する。
- `legacy_done_at_root_r18.json` は許可リストではなくR18の歴史証拠であることを明示する。
- PR #2961で追加された `test_legacy_done_root_references.py` が、正本配置と旧root参照0件を固定することをREADMEへ反映する。
- runtime/API/schema、Issue status、R18 identity manifestは変更しない。

## 受入条件

- [x] READMEがR18の58件を過去形で説明する。
- [x] 現在のDone-at-rootが0件であることを明示する。
- [x] `LEGACY_DONE_AT_ROOT_BASELINE = 0` を現行契約として説明し、baseline再増加を運用として禁止する。
- [x] `legacy_done_at_root_r18.json` を歴史証拠として位置づけ、移行許可リストではないことを明示する。
- [x] `test_legacy_done_root_references.py` による旧root参照回帰guardをREADMEへ反映する。
- [ ] planning unit tests、active memo validator、docs-check、triage、stale merge reintroduction、`git diff --check` が通る。

## 検証計画

- `python -m unittest discover -s 01_Plans/issues/tests -p 'test_*.py'`
- `python -m unittest discover -s 01_Plans/tests -p 'test_*.py'`
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python 01_Plans/docs_check.py`
- `python 01_Plans/triage_actionable_plans.py --format json`
- `python 01_Plans/check_stale_merge_reintroduction.py --base-ref origin/main --head-ref HEAD --json --fail-on-strong`
- `git diff --check origin/main...HEAD`

## 補足

本Issueはlegacy Doneの追加移行ではなく、移行完了後の**運用文書をpost-zero状態へ同期する**ためのplanning integrity修正である。R18の58件という観測値とidentity manifestは削除せず、現行ルールとの時間軸だけを正す。
