# Issue Draft: FB-RM-SEC-02 Worker安定化（bundle zip を off-main-thread へ移管）

- Type: Security / Process
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/worker/`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/export/*.test.ts`, `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/issues/README.md`
- Related Backlog: `FB-RM-SEC-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: `FB-RM-SEC-02`
- Expected verification level: `integration`

## 1) 課題 / Problem statement

- Bundle export の zip 圧縮はメインスレッドで実行され、ドキュメント規模次第で UI 応答を阻害する。
- 既存の diagnostics/trace/diff は worker 経路を持つが、zip 生成は off-main-thread 化されていない。

## 2) 提案する解決策 / Proposed solution

- `bundle_zip.worker.ts` + `bundle_zip_client.ts` を追加し、zip 生成を worker へ移管する。
- Worker 非利用時は既存の main-thread fallback を維持し、動作互換を保つ。
- Export フローに cancellation/progress を接続し、UI から中断可能にする。

## 3) 受入条件 / Acceptance criteria

- [x] zip 生成が worker 経路で実行可能。
- [x] worker 利用不能時に fallback で zip 生成が継続。
- [x] abort 時に cancelled として扱える。
- [x] `bundle_export.test.ts` で worker/fallback/cancel を回帰固定。
- [x] `FB-RM-SEC-02` の状態が `01_Plans` 文書に反映される。

## 4) 実装タスク分解 / Task breakdown

- [x] T1 `bundle_zip_protocol.ts` を追加。
- [x] T2 `bundle_zip.worker.ts` を追加。
- [x] T3 `bundle_zip_client.ts` を追加。
- [x] T4 `bundle_export.ts` の zip 生成経路を client 経由へ置換。
- [x] T5 `App.tsx` で zip 進捗表示/キャンセル扱いを同期。
- [x] T6 `bundle_export.test.ts` に worker/fallback/cancel テストを追加。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/export/bundle_export.test.ts`
  - `npm run test -- src/worker/diff_client.test.ts src/worker/trace_client.test.ts src/worker/diagnostics_client.test.ts`
  - `npm run typecheck`
  - `npm run test:regression-guards`
- 期待結果:
  - bundle zip 経路の worker/fallback/cancel がテストで固定される。
  - 既存 worker client 群の回帰がない。

## 6) Progress log

- 2026-02-28: `bundle_zip` worker/client/protocol を追加し zip 生成を off-main-thread 化。
- 2026-02-28: `buildBundleZipBlob` を worker client 経由に更新し、fallback/cancel を実装。
- 2026-02-28: `App.tsx` の bundle export へ zip 進捗と cancellation handling を反映。
- 2026-02-28: `bundle_export.test.ts` に worker/fallback/cancel 回帰テストを追加し、関連テストを実行して完了確認。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream H realignment (2026-05-04)

### Phase 1: Read同期（依存/優先度再評価）
- 系列依存の再評価: `I18N -> MID -> RS -> SEC` を基本順とし、`FB-RM-SEC-02-worker-stabilization` はこの順序に従って前後の成果物契約を参照する。
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
