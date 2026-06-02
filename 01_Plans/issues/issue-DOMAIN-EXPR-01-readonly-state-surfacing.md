# Issue Draft: DOMAIN-EXPR-01 既存ドメイン状態の読取UI第一級化

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/e2e/`
- Related Backlog: `DOMAIN-EXPR-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `00_Prompt/domain.md`, `02_Architecture/schemas.md`
- Dependencies: N/A
- Expected verification level: `e2e`

> 個人OSS段階（`ADR-0039`）の軽量起票。重量級の RACI/KPI セクションは省略。`ADR-0040` Phase 1。

## 1) 課題 / Problem statement

`schemas.md` は `claimType` / `critiqueInputs` / `evidenceLinks` / `reviewAttribution` を往復保存するが、line 432 のとおり画面上の個別UIを提供していない。利用者は domain.md 中核概念（違和感・根拠・矛盾・レビュー状態）が文書に存在しても、画面上で確認・発見できない。frontend に Hold/Pending系の表示も無い。

## 2) 背景 / Context

- `ADR-0040` Phase 1 は「schema変更なしで、既存往復状態を読取UIとして第一級化する」最小・低リスク段階。
- `PRODUCT-VALUE-02` Representation boundary table が、違和感/根拠/矛盾/レビュー境界は「現行構造で扱える」と確認済み（不足は日常導線）。
- `PRODUCT-UX-02`（Done）で選択コンテキストパネルは既に存在し、そこへ状態を露出できる。

## 3) 提案する解決策 / Proposed solution

- 変更対象（Frontend のみ、schema変更なし）:
  - カード/島の選択コンテキストに、`claimType`（fact/hypothesis/unknown等）、`reviewState`（unreviewed/human_reviewed）、関連する `critiqueInputs`・`evidenceLinks` 件数を状態バッジとして表示。
  - キャンバス/一覧で「未レビュー」「根拠なし」「違和感あり」を絞り込めるフィルタ。
- 最小単位: まず表示とフィルタ（読取専用）。登録・編集は `DOMAIN-EXPR-02/03` で扱う。
- 非目標: schema拡張、Hold/Shelfの新設、AIによる状態変更、正解判定・採点。

## 4) 受入条件 / Acceptance criteria

- [ ] カード/島選択時に claimType と reviewState がバッジ等で確認できる。
- [ ] 「未レビュー」「根拠なし」「違和感あり」で対象を絞り込める。
- [ ] schema（DocumentV2）に変更がない（往復保存フィールドの読取のみ）。
- [ ] AI/worker/API が `human_reviewed` を自動昇格しない（CE0-REVIEW-IF 非後退）。
- [ ] `KJ_ATLAS_LLM_PROVIDER=none` 既定でも表示・絞り込みが成立する。
- [ ] E2E で状態表示と絞り込みを検証する。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node ./node_modules/typescript/bin/tsc --noEmit`
  - `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run`
  - `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test --reporter=line`
  - `rg -n "claimType|reviewState|critiqueInputs|evidenceLinks" 03_Implement/frontend/src`
- 期待結果: 既存往復状態が選択コンテキストと絞り込みで一貫して確認でき、schema差分が無い。
- 未実施時の代替: 実装前はワイヤーフローと選択コンテキストのレビューで代替。

## 6) リスクとロールバック / Risks & rollback

- 失敗モード: バッジ過多で選択コンテキストが煩雑化。
- 影響範囲: SidePanel、CardView/IslandView、フィルタ状態。
- ロールバック: バッジ/フィルタをコンポーネント単位で無効化（schema非依存のため安全）。

## 7) Additional context

- ADR化が必要になる条件: 表示のために永続状態を追加する必要が出た場合（その時点で `DOMAIN-EXPR-02` または新schema issueへ送る）。
