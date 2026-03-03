# Issue Memo: FB-RM-MID-02 manual assisted merge decisions

- Type: Feature
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Scope: Frontend, Backend, Docs
- Expected verification level: unit
- Related Backlog: FB-RM-MID-02, FB-P2B-02
- Related ADR/Spec: ADR-0001, ADR-0007, ADR-0019

## Context

`collectMergeCandidates` による deterministic 候補提示（FB-RM-MID-01）は完了済み。
次段として、候補に対する人間承認フロー（採用/部分採用/却下/後で）を保存し、
自動確定を禁止したまま再読込可能にする必要がある。

## Proposed solution

- `mergeSuggestionDecisions` を DocumentV2 の拡張フィールドとして追加。
- Merge Suggestions UI を4アクション（accept/partial/reject/defer）へ更新。
- クリック時は canonical merge を実行せず、decision log のみを append する。
- 最新decisionを候補一覧に表示し、再収集時に edited text と decision 状態を復元する。
- Frontend strict validator / Backend Pydantic model / roundtrip test を同期更新する。

## Acceptance criteria

- [x] 候補ごとに `採用/部分採用/却下/後で` を記録できる。
- [x] 記録した decision が document 保存・再読込で保持される。
- [x] decision 履歴（append log）と最終状態（latest）がUIで確認できる。
- [x] 自動 canonical merge が発火しない。
- [x] 既存 deterministic candidate 生成の決定論を壊さない。

## Validation plan

- `npm run test -- src/domain/merge_suggestion_decisions.test.ts`
- `npm run test -- src/domain/validate_doc.test.ts`
- `npm run test -- src/ui/MergeSuggestionsPanel.test.ts`
- `npm run typecheck`
- `pytest 03_Implement/backend/tests/test_docs_roundtrip.py -k merge_suggestion_decisions`
