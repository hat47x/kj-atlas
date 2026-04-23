# Issue Draft: FB-RM-MID-01 類似度検出（deterministic heuristic）

- Type: Feature request (enhancement)
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/domain/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/App.tsx`, `01_Plans/`
- Related Backlog: `FB-RM-MID-01` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0005-phase2-qualitative-integration.md`, `01_Plans/adr/ADR-0007-future-backlog.md`
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
