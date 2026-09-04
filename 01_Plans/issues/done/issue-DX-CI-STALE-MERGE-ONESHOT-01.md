# issue-DX-CI-STALE-MERGE-ONESHOT-01 — 完了済みmergeMethod検証のone-shot実行足場を残さない

- Type: Process / CI hygiene
- Status: Done
- Source Issue: N/A
- Priority: P1
- Scope: `.github/workflows/`, `.github/merge_method_traceability_once.py`, `.github/scripts/apply_merge_method_r19_once.py`
- Related ADR/Spec: `ADR-0000`
- Expected verification level: `docs-check`

## 背景

merge方式の追跡性を実装した際には、作業ブランチ上で一回だけ実装・検証・commitまで行うためのworkflowと補助scriptが複数作られました。これらは恒久CIではなく、workflow名にも `Temporary` / `one-shot` と明記され、成功時には自分自身を削除する設計でした。

mergeMethod本体はPR #2869でmainへ統合済みです。同PRの最終検証記録でも、一回限りのworkflow/scriptは成功runで削除済みとされています。一方、現在のmainには無印・v2・v3・v4・R19のworkflowと、それら専用の補助scriptが再び残っていました。

実装済みの機能を再構築するための古いworkflowが正本に残ると、通常のCIと一回限りの実行足場の区別が曖昧になります。また、実際の別ブランチ作業中にも旧workflowの失敗runが観測され、CI状況を読む際のノイズになっていました。

## 対応

mergeMethod追跡の完了済み一回限り実行足場だけを削除しました。

- `.github/workflows/merge-method-traceability-once.yml`
- `.github/workflows/merge-method-traceability-once-v2.yml`
- `.github/workflows/merge-method-traceability-once-v3.yml`
- `.github/workflows/merge-method-traceability-once-v4.yml`
- `.github/workflows/merge-method-traceability-r19-once.yml`
- `.github/merge_method_traceability_once.py`
- `.github/scripts/apply_merge_method_r19_once.py`

他の `*-once.yml` は、それぞれ別作業の履歴と実行契約を持つため、本対応では一括削除していません。対象はmergeMethod追跡の完了済み系列に限定しています。

## 確認事項

- mergeMethodのproduct実装・テスト・正本文書は変更しない。
- 恒久CIの検証条件は変更しない。
- 削除対象は、各workflow自身が成功後の削除対象としていた一回限りのファイルに限定する。
- issue lifecycle validator / docs-check に既存baseline由来の不整合がある場合は、本cleanupとは分離して扱う。

これにより、正本には現在も意味を持つCIと成果物だけを残し、一回限りの作業足場を恒久的な検証経路と誤認しない状態へ戻します。
