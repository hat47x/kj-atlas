# Issue Draft: DOMAIN-EXPR-03 違和感→再提案の日常ループUI

- Type: Feature request
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `02_Architecture/schemas.md`, `04_Documentation/acceptance_check.md`
- Related Backlog: `DOMAIN-EXPR-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `00_Prompt/domain.md`, `02_Architecture/schemas.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Dependencies: `01_Plans/issues/issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（Done 2026-06-20）
- Expected verification level: `e2e`

## Implementation Progress 2026-06-23

### Done
- SidePanel reproposal diff preview: Shows 3 most recent reproposalDiffs with ops, rationale, iteration (2f170b17)
- Existing infrastructure: critique note + tags editing in SidePanel, SuggestionPanel for resuggest, HilRsRediffPreview for diff details, DomainStateFilterBar hasCritique filter

### Remaining
- "Suggest re-proposal" action button from SidePanel critique context → SuggestionPanel
- `KJ_ATLAS_LLM_PROVIDER=none` explicit "no AI candidates" messaging in re-proposal context
- E2E: critique→reproposal→diff daily loop verification

### Commits
- 2f170b17 reproposal diff preview section in SidePanel

## Draft→Open 2026-06-21
DOMAIN-EXPR-01 Doneにより依存充足。ADR-0040 Phase 3（違和感→再提案の日常ループUI）。
既存のcritiqueInputs/reproposalDiffsを日常導線へ接続。

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

## Open gate sync 2026-06-04

- 現在の基準: `origin/main` は `0133c744b60e4cc5f0c48435a62c72fbb5ca9f52`。DOMAIN-EXPR-01 の mainline evidence intake 後の状態を起点にする。DOMAIN-EXPR-02 は別issueとして管理されており、このissueの批評・再提案UI作業を承認するものではない。
- ステータスへの影響: このissueは引き続き `Draft`。スキーマ中立の最初のスライスは計画できるが、批評から再提案までの完全なループを実装するには、受け入れ済みの契約が不足している。
- Phase 1 依存ゲート: DOMAIN-EXPR-01 が「読み取り専用状態の表示」の基準として受け入れられてから、批評入力と再提案確認を日常操作へ組み込む。
- Critique 契約ゲート: 最初の実装で既存の `critique` / `critiqueTags` を使うのか、`critiqueInputs` を導入するのか、または互換レイヤーで扱うのかを決める。分類やpayload契約を変える場合は、先に `02_Architecture/schemas.md` を更新する。
- 再提案の生成元ゲート: `KJ_ATLAS_LLM_PROVIDER=none` とAI支援時のふるまいを分けて定義する。AIなしでも批評の登録・表示は成立させる。AI支援による再提案はproposal-onlyとし、自動適用しない。
- 差分・意思決定UIゲート: どの変更前後フィールドを表示するか、利用者が候補を承認・却下する手順、承認・却下・保留後も元の批評をどう見せるかを決める。
- ADRゲート: 既存フィールドを見せるだけのスキーマ中立UIスライスではADR不要。批評分類、再提案の権限、スキーマ互換性、AI提案と人間判断の境界を変える場合は、実装前にADRの作成または更新を行う。
- 推奨する次のスライス: まずAIなし・スキーマ中立のUIフローを文書化し、テストする。カードまたはクラスタを選択し、既存の批評種別と任意メモを付与し、文脈内に表示する。`KJ_ATLAS_LLM_PROVIDER=none` では「AIによる再提案は生成されない」状態を明示する。AI生成の再提案候補は、上記契約が受け入れられるまで延期する。
- この同期は実装を承認しない。スキーマ、AI権限、操作設計を1つのPRに混ぜずに済むよう、次の計画判断を絞り込むための更新である。

## 7) Additional context

- ADR化が必要になる条件: Critique種別やreproposal契約を変更する場合（HIL-RS契約と整合が必要）。

## 実装記録（2026-06-23）: AI非依存の違和感入力

### 完了した範囲

- カードと島の違和感入力を、HIL-RS正本の5種（`too_close` / `too_far` / `not_the_same` / `feels_off` / `no_articulable_reason`）へ統一した。
- 任意メモと種別は既存の `critique` / `critiqueTags` に保存し、既存の `CritiqueInput` 変換経路で往復できる。schema変更は行っていない。
- 旧タグ（`belongs_together` / `unrelated` / `unclear_boundary`）は既存文書から削除せず、読み取り時の表示互換を維持する。新規入力候補には出さない。
- 違和感は文書に保存され、AIが無効な構成でも保持される一方、再提案候補は生成されないことを選択コンテキストに明示した。
- キーボードE2Eで5種の表示、メモ入力、種別選択、保存後のdocument反映を検証する。
- 一般利用者向けの受け入れ手順に、5種の違和感とAI無効時の挙動を同期した。
- 違和感入力欄から「再提案を確認」を実行すると、詳細表示を開き、既存のproposal-only再提案面へフォーカスする導線を追加した。

### 残る範囲

- AI有効時の再提案候補生成自体は既存機構を利用する。provider別の成功経路をリリース候補環境で確認する証跡は未完了。
- 前案と再提案の差分確認、採用・却下・保留後も元の違和感を保持する操作。
- 上記は再提案権限と差分意思決定UIを含むため、本Issueの後続スライスとして分離する。

複雑性予算: 初期表示への純増=説明1件（AI無効時の挙動を誤解させないため） / 保留・違和感操作の距離=不変 / 取り消し導線=タグ解除・メモ削除
