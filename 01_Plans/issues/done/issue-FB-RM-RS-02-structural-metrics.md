# Issue Draft: FB-RM-RS-02 構造メトリクス（健全性指標）を diagnostics へ追加

- Type: Feature request (enhancement)
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/worker/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/domain/view/`, `04_Documentation/diagnostics.md`
- Related Backlog: `FB-RM-RS-02` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `04_Documentation/diagnostics.md`
- Dependencies: `FB-RM-RS-02` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Expected verification level: `e2e`
- Related Principles: `P-03` (レビュー追跡), `P-06` (視点制御), `P-07` (privacy-by-default)

## 1) 課題 / Problem statement

現状の Trace Analytics では「根拠リンク数」「孤立ノード数」などの**記述統計**は得られるが、
構造の健全性（偏り・分断・過密）を判断するための**評価可能なメトリクス定義**が不足している。

このため、レビュー時に以下の問題が残る。

- どこが“危険な構造”かを一貫して判定できない。
- diagnostics の警告優先度が人依存になり、再現性が低下する。
- E2E/回帰で「壊れていない」を機械的に検証しづらい。

## 2) 判断基準に基づく優先度評価

`AGENTS.md` の判断軸（価値・安全・企業/行政要件・後方互換）で評価すると、次の通り。

- 価値・判断軸（`ADR-0001`）: Human-in-the-loop のレビュー品質を定量化する基盤として有効（高）。
- 安全（`THREAT_MODEL.md` / SafeMode）: 外部送信不要でローカル計算可能。SafeModeを破らず導入可能（高）。
- 企業・行政要件（`02_Architecture/enterprise_architecture.html`）: 監査説明性（「なぜ警告したか」）を補強できる（中〜高）。
- 後方互換（`schemas.md`）: 既存schemaを破壊せず `diagnostics` 拡張で導入可能（高）。

## 3) 提案する解決策 / Proposed solution

`diagnostics` パイプラインに「構造メトリクス」レイヤを追加し、少なくとも次を定義・実装する。

1. **connectedComponentCount**: 構造分断の検知
2. **largestComponentRatio**: 主成分への集中度
3. **degreeP95**: 局所過密の検知
4. **bridgeEdgeCount**: ボトルネック依存の把握

実装要件:

- すべて決定論（入力同一 → 出力同一）で計算する。
- `diagnostics_protocol` の schemaVersion ポリシーに整合させる。
- Markdown report / UI 表示 / worker 経路で同一値を参照する。

## 4) 受入条件 / Acceptance criteria

- [x] 指標定義（意味・計算式・しきい値初期値）が `04_Documentation/diagnostics.md` に記載される。
- [x] `src/worker/*` でメトリクス計算が実装され、決定論テストで固定される。
- [x] 既存 diagnostics 出力互換を維持し、旧クライアントで致命的失敗を起こさない。
- [x] SidePanel/Report で追加指標が表示される。
- [x] E2Eまたは統合テストで「偏った構造」「分断構造」の検知シナリオが1件以上追加される（worker統合テスト追加）。

## 5) 検討した代替案 / Alternatives considered

- 代替案A: 既存 Trace Analytics のみで運用を継続
  - 欠点: 健全性評価が主観依存となり、監査説明性が弱い。
- 代替案B: LLM評価に委譲
  - 欠点: 非決定性が増し、CI回帰基準として不適。

## 6) 実装タスク分解（Issue化後にチェック運用）

- [x] metrics contract（型/命名/閾値）確定
- [x] worker計算実装 + unit test
- [x] diagnostics markdown 出力反映
- [x] SidePanel 表示反映
- [x] regression guards への追加
- [x] ドキュメント同期（diagnostics）

## 7) 実行TODO（詳細）

- [x] T1: `StructureMetrics` 型へ `connectedComponentCount/largestComponentRatio/degreeP95/bridgeEdgeCount` を追加。
- [x] T2: relation グラフ（evidence + card-card edges）を正規化し、連結成分・P95・bridge を決定論実装。
- [x] T3: `diagnostics_compute.ts` の Markdown `## Metrics` へ新規行を追加。
- [x] T4: `SidePanel.tsx` の Metrics セクションに新規指標を表示。
- [x] T5: `structural_metrics.test.ts` を拡張し、分断/偏りケースを固定。
- [x] T6: `worker_golden.test.ts` に分断・橋エッジ検知シナリオを追加。
- [x] T7: `tests/fixtures/worker/diagnostics.md` を更新し golden 差分を確定。
- [x] T8: `04_Documentation/diagnostics.md` に指標定義・計算範囲・初期しきい値を追加。

## 8) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/domain/view/structural_metrics.test.ts`
  - `npm run test -- src/worker/worker_golden.test.ts`
  - `npm run test -- src/worker/diagnostics_protocol.test.ts`
  - `npm run typecheck`
  - `npm run test`
  - `git diff --check`
- 期待結果:
  - 新規4メトリクスの値が unit + worker 経路で一致する。
  - golden diagnostics が更新後に固定される。
  - 既存 protocol validation 回帰を破壊しない。

## 9) Progress log

- 2026-02-28: タスク方針を確定し、scope を Frontend diagnostics + docs に固定。
- 2026-02-28: `computeStructureMetrics` にグラフ由来の4指標（連結成分/主成分比/P95/bridge）を追加。
- 2026-02-28: `diagnostics_compute.ts` / `SidePanel.tsx` へ新規指標表示を反映。
- 2026-02-28: `structural_metrics.test.ts` と `worker_golden.test.ts` を拡張し、分断構造・ボトルネック依存の検知を回帰固定。
- 2026-02-28: `04_Documentation/diagnostics.md` を更新し、指標定義・計算対象・初期しきい値を明文化。
- 2026-02-28: self-loop のみを持つカードが `isolatedCardCount` で非孤立扱いになる不整合を修正し、孤立判定をグラフ次数ベースへ統一。

## 10) Status が Draft のまま残る原因分析と解決

### 原因

- 本メモは実装・検証まで完了していたが、`Source Issue` が `TBD` のため
  「`Draft` 以外は不可」という Active 用ルールに該当していた。
- その結果、完了済みメモが Active 一覧に残留し、状態が進まない運用詰まりが発生した。

### 解決

- `01_Plans/issues/README.md` に `Done` 運用を正式追加。
- 本メモを `Done` へ更新し、Active 一覧から外して `Completed issue memos` セクションへ移管。
- validator は `Active issue memos` セクションのみを検証対象に限定し、運用衝突を解消。

- 2026-02-28: Active 一覧の Draft 滞留を解消するため、本メモを `Done` へ更新し README の運用ルールへ反映。

- 2026-03-01: 指摘対応として Playwright E2E `e2e/diagnostics_structural_metrics.spec.ts` を追加し、Share Panel 経由 export の diagnostics で新規指標行と決定論（同一入力2回一致）を検証した。初回でE2Eが欠けた理由は unit/worker 回帰のみで十分と誤判断したためで、`04_Documentation/e2e_testing.md` に原因分析と再発防止を追記した。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream H realignment (2026-05-04)

### Phase 1: Read同期（依存/優先度再評価）
- 系列依存の再評価: `I18N -> MID -> RS -> SEC` を基本順とし、`FB-RM-RS-02-structural-metrics` はこの順序に従って前後の成果物契約を参照する。
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

## Current-main Evidence Refresh (2026-06-06)

- Candidate: `origin/main@eca7c4979374a264a50820b14598be5eb760bde0`.
- Scope: targeted rerun of the user-facing bundle export path that verifies structural metrics are included in `diagnostics.md` and remain deterministic across repeated exports from the same document.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/diagnostics_structural_metrics.spec.ts --reporter=line` -> pass, 1 test.
- Evidence detail:
  - Imported a four-card, two-component document through the Chrome file picker flow.
  - Exported the review bundle from Share & Reproduce.
  - Confirmed `diagnostics.md` contains `connectedComponentCount=2`, `largestComponentRatio=0.75`, `bridgeEdgeCount=2`, `isolationRate=0.25`, `connectivityScore=0.6667`, and `degreeSkewRatio=2`.
  - Exported a second time and confirmed the diagnostics markdown is byte-for-byte identical.
- Decision impact: Done status remains valid. No ADR is required because the metric contract, SafeMode/share policy, and diagnostics authority did not change.
