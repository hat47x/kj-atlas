# Issue: DOC-ISSUE-IDENTITY-01 完了済みIssueメモの複製がactiveとして復活できる

- Type: Bug / Process
- Status: In Progress
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

- [ ] active直下と `done/` に同じbasenameを置くfixtureでvalidatorがblocking errorを返す。
- [ ] `done/` にactive statusのmemoを置くfixtureで、`missing memo file` ではなく配置矛盾を報告する。
- [ ] `done/` に正しい `Status: Done` のmemoを1件だけ置く正常系は通る。
- [ ] 実repoから `DX-DESIGN-CHECK-02` の古いDraftコピーが除去され、Done版だけが残る。
- [ ] 実repo監査でduplicate basenameが0件、`done/` 内active statusが0件になる。
- [ ] `docs_check.py`、issue validator、triage、関連unit test、`git diff --check` が成功する。

## 非目標

- Done-at-root legacy 58件の一括移動。
- Issue IDの新しい命名体系やRequirementID必須化。
- GitHub Issuesへの移行。
- 完了済み履歴の削除。
