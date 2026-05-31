# Issue Draft: DOMAIN-EXPR-03 違和感→再提案の日常ループUI

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `02_Architecture/schemas.md`
- Related Backlog: `DOMAIN-EXPR-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `00_Prompt/domain.md`, `02_Architecture/schemas.md`
- Dependencies: `01_Plans/issues/issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`
- Expected verification level: `e2e`

> 個人OSS段階（`ADR-0039`）の軽量起票。`ADR-0040` Phase 3。

## Dependencies

- 前段: `issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（読取バッジ/絞り込みを起点に、違和感登録と再提案差分確認へ広げる）。

## 1) 課題 / Problem statement

domain.md の Critique（理由の有無を問わない否定・ツッコミ）は `critiqueInputs`（型）と `reproposalDiffs`（再提案差分）として往復保存されるが（`schemas.md`）、利用者が日常操作として「違和感を付ける→制約として再提案を見る→前案との差分を確認する」一連のループが画面上に無い。`ADR-0001` P-04（Human-in-the-loop反復）の中核が未到達。

## 2) 背景 / Context

- `ADR-0040` Phase 3。`DOMAIN-EXPR-01` の読取バッジを起点に、違和感の登録と再提案差分確認へ広げる。
- 既存資産: `CritiqueInput`（5種: too_close/too_far/not_the_same/feels_off/no_articulable_reason）、`ReproposalDiff`、HIL-RS critique payload。
- AI提案は CE2 proposal-only。再提案は候補生成であり自動確定しない。

## 3) 提案する解決策 / Proposed solution

- Frontend:
  - 選択対象に Critique を理由任意で付与（5種＋自由コメント任意）。schema既存型を使用、原則 schema変更なし。
  - Critique を制約として再提案（AI有効時は proposal-only 候補、none既定時は決定論的な再配置候補または「AIなしのため候補生成不可」を明示）。
  - 前案と再提案の差分（`reproposalDiffs`）を確認できる。
- 非目標: AIによる違和感の無視・正当化、単一正解の提示、自動採用。

## 4) 受入条件 / Acceptance criteria

- [ ] カード/島/関係に Critique を理由任意で付けられる（domain.md の5種に対応）。
- [ ] Critique 付与後、再提案候補と前案の差分が確認できる。
- [ ] AI提案は proposal-only で、採否は人間操作。違和感は消されず保持される。
- [ ] `KJ_ATLAS_LLM_PROVIDER=none` 既定でも、Critiqueの登録・保存・表示が成立する（再提案生成のAI依存部は明示的に分離）。
- [ ] schema変更がある場合は `schemas.md` 先行更新と往復互換を満たす。
- [ ] E2E で 違和感付与→再提案→差分確認 を検証する。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node ./node_modules/typescript/bin/tsc --noEmit`
  - `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run`
  - `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test --reporter=line`
  - `rg -n "critique|Critique|reproposal|Reproposal" 03_Implement/frontend/src`
- 期待結果: 違和感→再提案→差分のループが画面上で一貫し、proposal-only が保たれる。
- 未実施時の代替: ワイヤーフローと再提案差分のfixtureレビュー。

## 6) リスクとロールバック / Risks & rollback

- 失敗モード: 再提案がAI前提に偏り、none既定で導線が破綻。
- 影響範囲: 選択コンテキスト、SuggestionPanel、再提案差分表示。
- ロールバック: Critique登録のみ残し、再提案UIを無効化（保存は維持）。

## 7) Additional context

- ADR化が必要になる条件: Critique種別やreproposal契約を変更する場合（HIL-RS契約と整合が必要）。
