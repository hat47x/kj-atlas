# Issue Draft: FB-RM-MID-01 類似度検出（deterministic heuristic）

- Type: Feature request (enhancement)
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/domain/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/App.tsx`, `01_Plans/`
- Related Backlog: `FB-RM-MID-01` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0005-phase2-qualitative-integration.md`, `01_Plans/adr/ADR-0007-future-backlog.md`
- Dependencies: `FB-RM-MID-01` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Expected verification level: `unit`
- Related Principles: `P-02` (反スコアリング), `P-04` (Human-in-the-loop), `P-05` (カード可管理性)

## 1) 課題 / Problem statement

Merge候補提示はAI依存導線が中心で、候補順序の決定論とローカル完結性が不足していた。
FB-RM-MID-01 の DoD（同一入力で候補順序安定）を満たすため、非AI heuristic の候補生成を導入する。

## 2) 提案する解決策 / Proposed solution

- `collectMergeCandidates(document)` を domain に追加し、以下の2段 heuristic で候補を生成する。
  1. normalized-text 一致（記号・空白ゆらぎ吸収）
  2. token-signature 一致（語順差の吸収）
- 候補グループとカードIDを安定ソートして deterministic を保証する。
- source card (`canonicalId`あり) / merged済み card (`mergedIntoCardId`あり) は候補生成から除外する。
- App の merge提案導線を API 呼び出しから local heuristic 呼び出しへ置換し、
  human-in-the-loop（採用確定はユーザー操作）を維持する。

## 3) 受入条件 / Acceptance criteria

- [x] 非AI heuristic の候補生成が実装される。
- [x] 同一入力で candidate group と group内 card 順が一致する。
- [x] candidate group 一覧で対象Cardを確認できる（AC-2B-1整合）。
- [x] system処理のみで `human_reviewed` へ遷移しない。
- [x] 単体テストで順序安定・境界条件・除外条件を固定する。
- [x] UI表示文言を deterministic heuristic 前提へ更新し、回帰テストを追加する。

## 4) 実装タスク分解

- [x] T1: `src/domain/merge_candidates.ts` を追加。
- [x] T2: `src/domain/merge_candidates.test.ts` を追加（決定論・除外・同率ケース）。
- [x] T3: `App.tsx` の suggest merges 経路を local heuristic へ置換。
- [x] T4: `MergeSuggestionsPanel.tsx` 文言を heuristic 前提へ更新。
- [x] T5: `MergeSuggestionsPanel.test.ts` を追加。
- [x] T6: `01_Plans` 文書へ進捗/状態を反映。

## 5) 検証計画 / Validation plan

- `npm run test -- src/domain/merge_candidates.test.ts`
- `npm run test -- src/ui/MergeSuggestionsPanel.test.ts`
- `npm run typecheck`
- `npm run test`
- `git diff --check`

## 6) Progress log

- 2026-02-28: スコープを Frontend（domain/UI/App）に固定。
- 2026-02-28: deterministic heuristic（normalized-text / token-signature）を実装。
- 2026-02-28: merge候補生成の決定論テストを追加し、同率時順序を固定。
- 2026-02-28: merge候補パネル文言を AI 前提から heuristic 前提へ更新。
- 2026-02-28: UI回帰テストを追加し、候補表示・理由表示を固定。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## Stream H realignment (2026-05-04)

### Phase 1: Read同期（依存/優先度再評価）
- 系列依存の再評価: `I18N -> MID -> RS -> SEC` を基本順とし、`FB-RM-MID-01-deterministic-similar-card-candidates` はこの順序に従って前後の成果物契約を参照する。
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
