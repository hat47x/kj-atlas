# Issue: DOC-ISSUE-IDENTITY-01 完了済みIssueメモの複製がactiveとして復活できる

- Type: Bug / Process
- Status: Done
- Source Issue: レーンC再triage（2026-09-04）
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/issues/`, `01_Plans/issues/validate_active_issue_memos.py`
- Related ADR/Spec: `01_Plans/issues/README.md`, `DOC-NORM-03`, `DOC-ISSUE-LIFECYCLE-01`
- Expected verification level: `unit`

## 課題

レーンCでactive計画メモを再triageしたところ、`DX-DESIGN-CHECK-02` が `Status: Draft` のP1としてactive直下に存在した。しかし履歴と `done/` を確認すると、このIssueは2026-08-18に受入条件を全件再検証して `Status: Done` として完了済みであり、同じbasenameの完成版が `01_Plans/issues/done/` に存在していた。

一回限り監査 run `33828257506` で `01_Plans/issues/` 全体を走査した結果、次を確認した。

- duplicate basename: 1件
- 対象: `issue-DX-DESIGN-CHECK-02-citation-shape-and-planned-endpoints-fail-ci.md`
- 配置: active直下のDraft版と `done/` のDone版
- `done/` 配下のactive status: 0件

つまり既存legacyではなく、単発の配置・同一性破損である。

`DOC-NORM-03` は、`done/` にactive statusのmemoが置かれた場合にもファイルを「missing」と誤診断しないよう、発見時の相対パスを保持するところまで修正した。ただし「done配下にactive statusがあること自体をエラーにする」は任意項目として残していた。また現行validatorはactive `RequirementID` の重複は検査するが、同じissue memo basenameがactive/done/archiveへ複数存在することは検査しない。

その結果、完了済みIssueの古いDraftコピーがactive直下へ戻ってもdocs-checkが通り、triage上ではP1の未完了作業として再び現れる。実装済み作業の重複着手や、古い計画記述を正本と誤認する原因になる。

## 対応方針

- `01_Plans/issues/` 配下の `issue-*.md` はbasenameを一意とし、root / `done/` / `archive/` の複数箇所に同じmemoを共存させない。
- `done/` 配下のmemoが `Draft / Open / In Progress` なら配置矛盾としてblocking errorにする。
- `DOC-NORM-03` の「発見時の相対パスを保持し、missingと誤診断しない」契約は維持する。配置矛盾は追加診断として報告する。
- 現存する `DX-DESIGN-CHECK-02` のactive直下Draftコピーを削除し、`done/` のDone版だけを残す。
- R18由来のDone-at-root 58件は本Issueの対象外とし、baselineやlegacy配置を動かさない。

## 受入条件

- [x] active直下と `done/` に同じbasenameを置くfixtureでvalidatorがblocking errorを返す。
- [x] `done/` にactive statusのmemoを置くfixtureで、`missing memo file` ではなく配置矛盾を報告する。
- [x] `done/` に正しい `Status: Done` のmemoを1件だけ置く正常系は通る。
- [x] 実repoから `DX-DESIGN-CHECK-02` の古いDraftコピーが除去され、Done版だけが残る。
- [x] 実repo監査でduplicate basenameが0件、`done/` 内active statusが0件になる。
- [x] `docs_check.py`、issue validator、triage、関連unit test、`git diff --check` が成功する。

## 実装結果

`validate_active_issue_memos.py` に `validate_memo_identity_and_placement()` を追加した。

- `root.rglob("issue-*.md")` で見つかるmemoをbasename単位で束ね、同じbasenameが複数配置に存在すればblocking errorを返す。
- `done/` 直下のmemoが `Draft / Open / In Progress` なら、`active Status ... is not allowed under done/` と配置矛盾を明示する。
- `DOC-NORM-03` が導入した発見時相対パスの保持は変更していない。そのため `done/` にactive memoを置くmutationでも `missing memo file` という旧誤診断は再発しない。
- `README.md` に、状態遷移に伴う配置変更はcopyではなくmoveであり、同じbasenameをroot / `done/` / `archive/` 等へ共存させないことを明記した。
- 完了済み `DX-DESIGN-CHECK-02` の古いactive直下Draftコピーを削除し、既存の `done/` Done版だけを残した。

## 検証結果（2026-09-04）

一回限りworkflow run `33828460564` で次を確認した。

- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` → 17 tests, OK
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → `ok: validated 52 active issue memos`
- `python 01_Plans/docs_check.py` → `docs-check passed: active_memos=52, tracked_markdown=755`
- `python 01_Plans/dogfood/validate_dogfood_docs.py` → structurally valid
- `python 01_Plans/triage_actionable_plans.py --format json` → success
- `python 03_Implement/backend/scripts/check_design_consistency.py` → 0 errors, 0 warnings
- 実repo再監査 → `duplicate_basenames=0`, `active_in_done=0`
- `git diff --check` → success

検証用workflowは成功後に自身を削除した。恒久workflowは追加していない。

本Issue自身も今回定めたmove契約へ従い、`Status: Done` として `done/` へ移す。R18のlegacy Done 58件には含まれないため、`LEGACY_DONE_AT_ROOT_BASELINE` の変更は不要である。

## 非目標

- Done-at-root legacy 58件の一括移動。
- Issue IDの新しい命名体系やRequirementID必須化。
- GitHub Issuesへの移行。
- 完了済み履歴の削除。
