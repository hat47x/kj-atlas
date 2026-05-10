# Issue Memo: FB-RM-MID-03 merge decision audit export

- Type: Feature
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/domain/`, `03_Implement/frontend/src/export/`, `04_Documentation/operations.md`, `01_Plans/adr/ADR-0007-future-backlog.md`
- Related Backlog: `FB-RM-MID-03`, `FB-P2B-03..04`
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: `FB-RM-MID-03`, `FB-P2B-03..04`
- Expected verification level: `unit`

## 1) 課題 / Problem statement

`mergeSuggestionDecisions` は document に保持されるが、監査向けに独立して抽出する export がなかった。
そのため representative と source の追跡を外部監査フローへ連携しづらい。

## 2) 提案する解決策 / Proposed solution

- merge decision log から監査用途の最小JSONを生成する純粋関数を追加。
- bundle export に `merge_decision_audit.json` を同梱。
- 出力順序・カードID順を安定化して決定論を担保。
- 非目標: merge確定ロジック自体の変更、backend API仕様の変更。

## 3) 受入条件 / Acceptance criteria

- [x] bundle export に `merge_decision_audit.json` が含まれる。
- [x] 監査JSONが `decisionId/groupId/decisionType/actorType/decidedAt/representativeCardId/sourceCardIds` を含む。
- [x] 同一入力で同一監査JSONが生成される（決定論）。
- [x] MID-01/MID-02で追加した decision log の保存仕様を壊さない。

## 4) 実装タスク分解 / Task breakdown

- [x] T1 `merge_decision_audit.ts` を追加。
- [x] T2 `bundle_export.ts` に監査JSON出力を追加。
- [x] T3 `merge_decision_audit.test.ts` を追加。
- [x] T4 `bundle_export.test.ts` を拡張。
- [x] T5 `ADR-0007` / `operations.md` に反映。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/domain/merge_decision_audit.test.ts src/export/bundle_export.test.ts`
  - `npm run test -- src/domain/merge_suggestion_decisions.test.ts src/domain/validate_doc.test.ts`
  - `npm run typecheck`
- 期待結果:
  - 監査JSONの構造・順序・代表/起源追跡がユニットテストで固定される。
  - 既存decision保存・検証テストが通過する。

## 6) Progress log

- 2026-02-28: テスト先行で `merge_decision_audit` の期待仕様（代表/起源追跡・時系列順）を固定。
- 2026-02-28: bundle export に `merge_decision_audit.json` を追加。
- 2026-02-28: 関連unit testと typecheck を実行し、回帰なしを確認。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream H realignment (2026-05-04)

### Phase 1: Read同期（依存/優先度再評価）
- 系列依存の再評価: `I18N -> MID -> RS -> SEC` を基本順とし、`FB-RM-MID-03-merge-decision-audit-export` はこの順序に従って前後の成果物契約を参照する。
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
