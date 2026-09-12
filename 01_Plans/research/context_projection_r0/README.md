# Context Projection R0 — executable research slice

このdirectoryは、`actor-role-interest-context-projection-contract-2026-09-12.md`の研究仮説を、production schemaへ昇格させずに検証するための最小実行sliceである。

## 目的

- Actor / Role / Interest / Inquiry / effective Permissionを分離する。
- requester自己申告のRoleから権限を推測しない。
- server-resolved PermissionとSafeModeを使って、既存`ContextQueryV1`相当へ決定論的にcompileする。
- Human / Generative AI / SEIでProjection Formが異なっても、selectionの根拠・元情報へのtraceを失わない。
- 現行`ContextQueryV1`のtop-level keyを増やさない。

## 非目標

- production APIの追加
- `ContextQueryV1` / `ContextBundleV1`のversion変更
- Authorization実装
- ConsensusGraphの変更
- AI/SEI proposalのauto-apply
- actor profileや長期interestの推論

## ファイル

- `compile_projection_request.py`: R0 requestを既存ContextQuery形へcompileするresearch utility
- `test_compile_projection_request.py`: permission / SafeMode / role separation / determinismのsynthetic test
- `fixtures/`: human / generative AI / SEIの同一Inquiry比較fixture

## 現行契約との関係

このutilityが返すquery objectのtop-level keyは次だけに固定する。

`queryId / goal / scope / depth / constraints / reviewFilter / safeModePolicy / outputMode / previewConfirmed`

これは`02_Architecture/schemas.md`の`ContextQueryV1`と同じkey集合である。R0固有情報はproduction型へ追加せず、必要なselection hintだけをboundedな`constraints`へcompileする。

この研究で不足が判明しても、直ちにv2を作らない。まず不足をEvidenceとして記録する。
