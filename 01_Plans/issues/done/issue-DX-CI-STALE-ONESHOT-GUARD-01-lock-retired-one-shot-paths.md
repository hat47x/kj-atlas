# Issue: DX-CI-STALE-ONESHOT-GUARD-01 退役済みone-shot資産の再出現を検知する

> 一時検証そのものを禁止せず、完了済みとして退役した特定の実行資産だけを再導入不可として固定する。

- Type: Test / DX / Repository Integrity
- Status: Done
- Source Issue: `DX-CI-STALE-ONESHOT-ASSETS-01`
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/tests/test_retired_one_shot_assets.py`
- Related ADR/Spec: PR #2892, PR #2896
- Expected verification level: `unit`

## 課題

PR #2896で、完了済みfeature branch専用のone-shot workflow 6本と専用script 4本をmainから除去した。しかし、削除だけでは古いbranchを後から再マージした際に同じファイルが復活しても、既存のplanning/docs guardはその事実を直接検出しない。

一方で、`*once*` や `Temporary` という名前の資産を一般禁止すると、branch-onlyの一時検証まで妨げる。必要なのはone-shot一般の禁止ではなく、**既に役目を終えて退役した10パスだけ**の再導入防止である。

## 対応

`01_Plans/tests/test_retired_one_shot_assets.py` を追加し、PR #2896で退役した次の10パスがrepository treeへ再出現していないことを固定する。

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

テストは正確なパス集合だけを見る。したがって、将来別名・別目的で作る一時workflowや検証scriptまで禁止しない。

## 受入条件

- [x] 退役済み10パスのどれかが存在するとテストが失敗する。
- [x] 退役済み10パスが存在しなければテストが成功する。
- [x] wildcardによるone-shot一般禁止にはしない。
- [x] product/runtimeや現行意味契約を変更しない。
- [x] planning unit test suiteに通常のunittest discoveryで含まれる。
- [x] 内容確定後、意味を変えず自然な日本語として全文を読み直す。

## 完了境界

- 今回退役した10パス以外の一時検証資産には制約を追加しない。
- branch protection、required status check、push可否は変更しない。
- repository内の古いbranchそのものの削除・整理は対象外とする。
