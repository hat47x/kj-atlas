# Issue: DOC-ISSUE-LEGACY-PATH-01 Done-at-rootの同数入替でlegacy境界をすり抜けられる

- Type: Bug / Process
- Status: Done
- Source Issue: PR #2858 再評価 / レーンC横断監査（2026-09-04）
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/issues/`, `01_Plans/issues/validate_active_issue_memos.py`
- Related ADR/Spec: `DOC-ISSUE-LIFECYCLE-01`, `DOC-ISSUE-IDENTITY-01`, `01_Plans/issues/README.md`
- Expected verification level: `unit`

## 課題

`DOC-ISSUE-LIFECYCLE-01` では、R18時点でactive直下に残っていた `Status: Done` 58件を一時baselineとし、実件数との一致を要求するexact count ratchetを導入した。58件から57件へ減らした場合は同じ変更でbaselineも57へ下げるため、一度減ったlegacy件数が古い上限まで戻ることは防げる。

しかし件数だけでは、次の変更を区別できない。

1. R18 legacyの `issue-b.md` を正しく `done/` へ移す。
2. 同じ変更で、新たに完了した `issue-c.md` をactive直下へ `Status: Done` のまま置く。
3. Done-at-root件数は58のままなので、count ratchetだけなら一致してしまう。

`DOC-ISSUE-IDENTITY-01` で導入したbasename一意性ガードも、このケースでは旧pathが消えて新pathだけが残るため検出できない。

PR #2858 はR18 commitから毎回Git履歴を再構成する案を提示していた。方向は妥当だが、最新mainではrepo固有baselineをsynthetic fixtureへ漏らさない境界が追加されており、さらにshallow cloneや履歴を持たない配布ソースでも検証を安定させたい。そのため、R18 commitから一度だけ機械生成した不変manifestを履歴境界として保存する方式へ置き換えた。

## 事前監査

一回限りworkflow run `33828753648` で、R18 commit `88aebae242d5d1a24278b3247d3544aeaa1ad386` と現在mainのDone-at-root basename集合を比較した。

- R18 baseline: 58件
- current: 58件
- currentのうちR18集合外: 0件
- R18集合のうち既に移動済み: 0件

したがって現時点では同数入替はまだ発生しておらず、新しいlegacy例外を設けずにfail-closed化できる。

## 対応方針

- R18 commitから機械生成した `legacy_done_at_root_r18.json` を不変のidentity baselineとして保持する。
- 現在active直下にある `Status: Done` のbasename集合は、常にR18 identity集合の部分集合でなければならない。
- legacyを `done/` へ移して現在集合が縮むことは許容する。identity manifestは更新しない。
- 件数ratchetは従来どおり別に維持し、移行時は `LEGACY_DONE_AT_ROOT_BASELINE` を58→57→…→0へ下げる。
- identity manifestへ新規pathを追記して検査を通す運用は禁止する。固定R18 commitからの歴史証拠として扱う。
- synthetic fixtureにはrepo固有identity baselineを暗黙適用せず、unit testではbaseline集合を明示注入できるようにする。

## 受入条件

- [x] R18 identity manifestが固定commitから機械生成され、58件・重複なし・basenameのみであることをvalidatorが検証する。
- [x] legacy 1件を減らし新規Done-at-root 1件を増やして件数を維持するfixtureで、count ratchetは通るがidentity guardが新規pathを拒否する。
- [x] R18集合の部分集合へ減る正常なlegacy移行はidentity guardを通る。
- [x] synthetic rootではrepo identityを暗黙適用せず、明示baselineで統一 `validate()` の配線をテストできる。
- [x] 実repoでR18集合外のDone-at-rootが0件である。
- [x] `docs_check.py`、issue validator、lifecycle/identity関連unit、triage、`git diff --check` が成功する。

## 実装結果

R18 commitから一回限りworkflowで `01_Plans/issues/legacy_done_at_root_r18.json` を機械生成した。manifestにはschema version、固定commit、件数、58件のbasenameだけを保存し、生成workflowは同じrunで削除した。今後legacyを移動してもこのmanifestは変更しない。

`validate_active_issue_memos.py` には次を追加した。

- `load_done_at_root_identity_manifest()`：manifestのJSON形式、schema version、固定commit、countとunique path件数の一致、重複、basename形式を検査する。
- `validate_done_memo_identity()`：現在のDone-at-root basename集合からR18集合外を抽出し、新規pathをblockingする。
- 統一 `validate()`：repo固有のidentity境界は実 `01_Plans/issues/` にだけ自動適用し、synthetic rootでは暗黙適用しない。必要なfixtureでは `enforce_done_identity=True` と `legacy_done_paths` を明示できる。

件数ratchetは変更していない。これにより「件数が増える」「一度減った件数が戻る」「件数は同じだがlegacyの顔ぶれが新規pathへ入れ替わる」をそれぞれ独立した契約で検出できる。

## 検証結果（2026-09-04）

一回限りworkflow run `33829024740` で次を確認した。

- lifecycle / issue-validator unit: 27 tests, OK
- 実issue validator: `ok: validated 52 active issue memos`
- `python 01_Plans/docs_check.py`: `docs-check passed: active_memos=52, tracked_markdown=756`
- dogfood document validation: structurally valid
- planning triage: success
- design consistency: 0 errors / 0 warnings
- identity manifest: 58 paths
- current Done-at-root: 58 paths
- R18集合外: 0 paths
- `git diff --check`: success

検証workflowは成功後に自身を削除した。恒久workflowは追加していない。

本Issue自身は新規に完了したmemoでありR18 legacyではないため、今回定めた契約に従ってactive直下へDoneとして残さず、`done/` へmoveして完了とする。

## 非目標

- legacy 58件の一括移動。
- R18 identity manifestを現在状態へ同期し続けること。
- 完了済み `DOC-ISSUE-LIFECYCLE-01` を再オープンすること。
- GitHub Actionsの恒久再導入。
