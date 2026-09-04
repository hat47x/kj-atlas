# Issue: DX-CI-STALE-ONESHOT-ASSETS-01 完了済みone-shot資産を正本から除去する

> 一回限りの適用・検証足場を恒久資産と混同しない。完了済み変更の再適用可能性を正本から取り除く。

- Type: Bug / DX / Repository Integrity
- Status: Done
- Source Issue: `DX-FRONTEND-MERGE-METHOD-DRIFT-01`
- Priority: P1
- Owner: Maintainer
- Scope: `.github/workflows/*once*.yml`, `.github/scripts/*once*.py`
- Related ADR/Spec: PR #2869, PR #2882, PR #2892
- Expected verification level: `integration`

## 課題

PR #2892で修復したfrontend正本ドリフトは、完了済み `mergeMethod` 作業の旧branch変更が後続mainへ再流入したことが主要因だった。

mainを再監査すると、完了済み作業に使った一回限りのworkflow / scriptがなお残っていた。中でも `apply_merge_method_traceability_final_once.py` は、R20の旧branchからproductファイルをcheckoutし、`App.tsx` 等へ `mergeMethod` を挿入する再適用処理そのものを保持していた。今回修復したものと同型の状態ドリフトを再び作り得る。

また、main上のworkflowには特定の旧作業branchだけを対象とする `Temporary` / `one-shot` 定義が複数残っていた。これらは恒久CIではなく、成功時に自身を削除する設計を含む実行足場である。

## 除去対象

正確な削除対象パスは本変更のGit差分を正本とする。対象は次の完了済みone-shot資産である。

### workflow

- `apply-ai-merge-ir-once.yml`
- `fix-docs-check-optional-workflows-once.yml`
- `merge-apply-e2e-once.yml`
- `reconcile-partial-with-r18-once.yml`
- `verify-ai-merge-apply-lineage-docs-once.yml`
- `verify-ai-merge-apply-lineage-once.yml`

### 専用script

- `apply_ai_merge_ir_once.py`
- `apply_merge_method_traceability_final_once.py`
- `fix_docs_check_optional_workflows_once.py`
- `reconcile_partial_with_r18_once.py`

`detect_auth_boundary.sh` のようなone-shot用途ではない補助資産は対象外とする。

## 対応方針

- product実装・現行contractは変更しない。
- 完了済みfeature branchを再適用するためだけのworkflow/scriptを正本から除去する。
- workflowディレクトリとscriptディレクトリに残るone-shot命名資産がなくなることを検証する。
- planning / docs-check / frontend typecheckを通し、削除が現行正本の実行・文書契約を壊さないことを確認する。
- workflow失敗をpushやmergeの必須条件へ変更しない。

## 受入条件

- [x] 上記10ファイルがmain候補treeから除去される。
- [x] 現行の恒久workflow/scriptを削除しない。
- [x] frontend `npm run typecheck` が成功する。
- [x] planning tests / Active memo validator / docs-check / triageが成功する。
- [x] workflow/scriptディレクトリに完了済みone-shot資産が残らない。
- [x] 一時検証workflowを最終差分へ残さない。
- [x] 内容確定後、意味を変えず自然な日本語として全文を読み直す。

## 検証結果

branch-only Run `33871984872` で、削除後の正本候補を確認した。

- frontend `npm run typecheck`: success
- planning unit tests: 130件成功、1件skip
- Active issue memo validator: 49件成功
- docs-check: success（active_memos=49 / tracked_markdown=776）
- triage: `errors: []`
- workflowディレクトリに `*once*` 名のworkflowが残っていないことを確認
- scriptディレクトリに `*once*.py` 名のscriptが残っていないことを確認
- `git -c core.whitespace=cr-at-eol diff --check`: success

## 完了境界

- 完了済みの旧workflow 6本と専用script 4本だけを除去した。
- `detect_auth_boundary.sh` はone-shot資産ではないため保持した。
- product/runtimeの実装、`mergeMethod` を含む現行contract、planning guardは変更していない。
- 恒久CIの採用方針、branch protection、pushの可否は変更していない。
- 削除した各ファイルの正確な旧パスと内容はGit履歴および本変更の差分を正本とする。
