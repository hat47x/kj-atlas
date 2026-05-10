# Issue Memo: FB-RM-MID-02 manual assisted merge decisions

- Type: Feature
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Scope: Frontend, Backend, Docs
- Expected verification level: unit
- Related Backlog: FB-RM-MID-02, FB-P2B-02
- Related ADR/Spec: ADR-0001, ADR-0007, ADR-0019
- Dependencies: FB-RM-MID-02, FB-P2B-02

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

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog整理提案: FB-P2B-02 は系列メモ複数運用（4件）。再オープンではなく、次回は親統合メモ1本＋派生メモ参照化を提案。


## Stream H realignment (2026-05-04)

### Phase 1: Read同期（依存/優先度再評価）
- 系列依存の再評価: `I18N -> MID -> RS -> SEC` を基本順とし、`FB-RM-MID-02-manual-assisted-merge-decisions` はこの順序に従って前後の成果物契約を参照する。
- 優先度再評価: reversible synthesis の実装引き渡し観点で、**決定論（reproducibility）** と **監査可能性（auditability）** を同列最優先とする。

### Phase 2: Plan（A1/A2 契約）
- A1（実装契約依存点）: downstream 実装は本メモの `Acceptance criteria` と `Validation plan` を満たす I/F を維持する。
- A2（モック先行可能点）: deterministic 候補生成・監査出力フォーマット・固定フィクスチャを先行モック化して検証可能。

### Phase 3: Execute（I/F・出力・監査証跡・Proceed条件）
- 入力I/F: Document/locale/query/export context など、本メモで規定済みの入力契約を採用。
- 期待出力: 同一入力で同一順序/同一内容の出力を返す（非決定挙動を禁止）。
- 監査証跡: 実行コマンド、判定結果、失敗理由、再試行回数を issue memo に記録する。
- Proceed条件: AC/DoD が満たされ、依存系列の受入条件と矛盾しないこと。

### Phase 4: Verify（欠落検査 + 自己修復）
- 決定論要件と監査要件の欠落をチェックし、欠落時は最大3回まで自己修復を試行する。
- 3回で是正不可の場合はフェイルセーフ停止（非決定仕様混入 / 監査要件欠落 / 依存矛盾）。

### Phase 5: Proceed（実装引き渡し優先度）
- Frontend/Backend 実装への引き渡しは、`I18N-02 -> MID-01 -> MID-02 -> MID-03 -> MID-05 -> RS-02 -> SEC-02 -> I18N-03` の優先バックログ順を基準とする。

## Stream G pass (2026-05-10)

### Phase 1: Interface Read固定
- domain/worker/export の既存I/F境界（入力契約・出力順序・型）を再確認し、今回の変更は **issue memo更新のみ** に限定する。
- 決定論優先順位を P1 とし、乱数・非安定ソート・時刻依存を新規導入しない。

### Phase 2: ADR明文化（Context/Decision/Consequences）
- Context: MID/I18N/RS/SEC 系列は既に実装済みで、現在は運用上の受入境界を明文化する段階。
- Decision: 「人間の最終判断を残す」「決定論を壊さない」「監査可能な証跡を維持する」を共通規範として固定。
- Consequences: 後続streamは同一AC/DoDを参照可能になり、衝突なく局所改善できる。

### Phase 3-6: Execute/Verify要点
- Deterministic化: 既存比較キー・ソート規約の維持を前提化（仕様追加なし）。
- 監査: manual intervention は audit log/export へ残す方針を再確認。
- i18n/worker: fallback順序・worker fail-safe（fallback/cancel）を受入境界として再固定。
- 構造メトリクス: locale非依存・再現可能出力の維持を受入条件として明記。

### Phase 7: 完了判定
- 判定: ✅ Done維持（docs整合）。
- 根拠: 決定論 / 監査性 / 後方互換 / 最小E2E観点が既存AC/DoDと矛盾しない。
- Stop条件: 依存矛盾またはAC欠落が観測された場合は3回自己修復後にFail-safe停止。
