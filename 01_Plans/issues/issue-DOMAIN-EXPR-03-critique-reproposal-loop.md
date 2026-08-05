# Issue Draft: DOMAIN-EXPR-03 違和感→再提案の日常ループUI

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `02_Architecture/schemas.md`, `04_Documentation/acceptance_check.md`
- Related Backlog: `DOMAIN-EXPR-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `00_Prompt/domain.md`, `02_Architecture/schemas.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Dependencies: `01_Plans/issues/issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（Done 2026-06-20）
- Expected verification level: `e2e`

## Implementation Progress 2026-06-29

### Done
- SidePanel reproposal diff preview: Shows 3 most recent reproposalDiffs with ops, rationale, iteration (2f170b17)
- "Open Reproposal" action button in SidePanel (island + card critique sections) → opens advanced UI + focuses critique workflow
- `KJ_ATLAS_LLM_PROVIDER=none` explicit warning banner in critique sections (2026-06-29)
  - Detects provider-disabled errors from suggest-layout API
  - Shows amber warning: "AI-powered re-proposals are unavailable (KJ_ATLAS_LLM_PROVIDER=none). Critique notes and tags are still saved."
  - i18n: `side_panel.critique.provider_disabled` (en/ja)
- Existing infrastructure: critique note + tags editing in SidePanel, SuggestionPanel for resuggest, HilRsRediffPreview for diff details, DomainStateFilterBar hasCritique filter
- Integration test: critique→preview→apply→critique preserved (hil_rs_client_apply.integration.test.ts)

### Remaining（2026-06-29 更新）
- E2E: critique→reproposal→diff daily loop verification（Playwright環境依存）

## Implementation Evidence 2026-07-04: Review reproposal opens the work-mode surface

- Fixed a UI routing regression where the SidePanel `Review reproposal` action enabled Advanced UI but did not open the work-mode surface that owns `data-domain-workflow="critique-reproposal"`.
- `handleOpenCritiqueWorkflow` now opens Work mode before requesting focus, so the visible user action matches the documented intent: critique note -> Review reproposal -> work-mode critique workflow.
- Targeted Playwright evidence: `node.exe .\node_modules\playwright\cli.js test e2e/domain_expression_keyboard_access.spec.ts --reporter=line` passed 4 tests on 2026-07-04.
- No ADR is required. The slice restores ADR-0031/ADR-0048 surface ownership without changing schema, AI authority, SafeMode, or review authority.

### Commits (new)
- 2026-06-29: providerUnavailableMessage state + detection + explicit warning banner in SidePanel critique sections
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

- [x] カード/島/関係に Critique を理由任意で付けられる（domain.md の5種に対応）。（実装記録 2026-06-23）
- [x] Critique 付与後、再提案候補と前案の差分が確認できる。（HilRsRediffPreview + SuggestionPanel、2026-07-11 provider=local 実走行でも確認）
- [x] AI提案は proposal-only で、採否は人間操作。違和感は消されず保持される。（2026-07-11 実走行: 提案到着後も違和感メモ/タグが保持され、破棄は人間操作、自動適用なし）
- [x] `KJ_ATLAS_LLM_PROVIDER=none` 既定でも、Critiqueの登録・保存・表示が成立する（再提案生成のAI依存部は明示的に分離）。（E2E追認 2026-06-29）
- [x] schema変更がある場合は `schemas.md` 先行更新と往復互換を満たす。（schema変更なしで完了）
- [x] E2E で 違和感付与→再提案→差分確認 を検証する。（domain_expression_keyboard_access + 2026-07-11 provider=local 実走行）

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

## E2E追認 2026-06-29: DOMAIN-EXPR-03

- 利用者指示に基づき、人間作業として残っていた Playwright E2E 実行を Codex が代行した。
- 実行対象: `domain_expression_keyboard_access.spec.ts` を含む対象Playwrightセット（first value / share preflight / domain expression / review pack / complexity budget / performance budget）。
- 結果: 2026-06-29 の対象Playwrightセットで **10 passed**。
- 判定: 現在のスキーマ中立スライスは **Go**。カード選択、違和感入力、5種タグ、AI無効時の保存・表示、共有前確認への接続は代表操作として再現可能。
- 残る範囲: AI provider 有効時の再提案候補生成、前案との差分意思決定、採用・却下・保留後も元の違和感を保持する操作は後続スライスとして残す。
- ADR影響: 既存 `critique` / `critiqueTags` / proposal-only 表示の確認に留まるため、この追認単体ではADR不要。再提案権限、永続化契約、AIと人間判断の境界を変える場合はADR更新が必要。

## 実装記録（2026-06-23）: AI非依存の違和感入力

### 完了した範囲

- カードと島の違和感入力を、HIL-RS正本の5種（`too_close` / `too_far` / `not_the_same` / `feels_off` / `no_articulable_reason`）へ統一した。
- 任意メモと種別は既存の `critique` / `critiqueTags` に保存し、既存の `CritiqueInput` 変換経路で往復できる。schema変更は行っていない。
- 旧タグ（`belongs_together` / `unrelated` / `unclear_boundary`）は既存文書から削除せず、読み取り時の表示互換を維持する。新規入力候補には出さない。
- 違和感は文書に保存され、AIが無効な構成でも保持される一方、再提案候補は生成されないことを選択コンテキストに明示した。
- キーボードE2Eで5種の表示、メモ入力、種別選択、保存後のdocument反映を検証する。
- 一般利用者向けの受け入れ手順に、5種の違和感とAI無効時の挙動を同期した。
- 違和感入力欄から「再提案を確認」を実行すると、詳細表示を開き、既存のproposal-only再提案面へフォーカスする導線を追加した。

### 残る範囲（2026-06-29 更新）

- AI有効時の再提案候補生成は既存機構（hil_rs_client + rediffProvider）で対応済み。
  provider別の成功経路をリリース候補環境で確認するPlaywright証跡は未完了（環境依存）。
- 採用・却下・保留後も元の違和感を保持する操作: 統合テスト追加済み
  （hil_rs_client_apply.integration.test.ts: critique→preview→apply→critique preserved）。
- 前案と再提案の差分確認UI: HilRsRediffPreview + SuggestionPanel 実装済み。

### テスト
- 単体: hil_rs_apply.test.ts（4 tests, critique保存検証含む）✅
- 統合: hil_rs_client_apply.integration.test.ts（2 tests, 完全ループ検証）✅
- E2E: Playwright環境依存で未完了 →（2026-07-11 完了、下記）

複雑性予算: 初期表示への純増=説明1件（AI無効時の挙動を誤解させないため） / 保留・違和感操作の距離=不変 / 取り消し導線=タグ解除・メモ削除

## 完了記録（2026-07-11）: provider有効時の成功経路をリリース候補環境で実証

最後に残っていた「AI provider 有効時の再提案候補生成の成功経路をリリース候補環境で確認する
Playwright証跡」を完了し、本Issueを Done とする。

### 検証環境（本物のprovider transport を使用）

- compose 3サービス（db+api+web）＋ `docker-compose.llm-stub.yml` オーバーレイ:
  `KJ_ATLAS_LLM_PROVIDER=local` / `KJ_ATLAS_LOCAL_LLM_BASE_URL=http://llm-stub:8089`。
- `03_Implement/deploy/llm-stub/server.py`: LocalProvider の HTTP 契約
  （POST /generate → `{"text": ...}`）をそのまま話す決定論スタブ。プロンプトの
  `- id="..."` 行からカードIDを抽出し、`re_layout` / `suggest_merges` に対して
  スキーマ適合の応答を返す。**provider transport・監査・応答パースの実コードパスが
  全て実行される**（スタブなのは HTTP の先の推論だけ＝「ローカル推論サーバ」の定義通り）。
- 再現スクリプト: `03_Implement/frontend/scripts/domain_expr03_provider_local_e2e.mjs`。

### 実走行結果（8ステップ全通過、2026-07-11）

1. `/api/ai/provider-status` が `{"providerKind":"local"}` を返す（none でないことをAPIで確認）。
2. 3カードのfixture文書を共有パネル経由でロード。
3. カードに違和感（Feels off＋メモ）を付与し保存。
4. 「再提案を確認」で Advanced＋critique workflow が開く。
5. 「配置を提案」→ **実providerパス（api→LocalProvider→llm-stub→パース）経由で配置案が到着**。
   スタブ由来の notes がUIに表示され、**proposal-only ヒント（自動反映されない・採否は人）も同時に表示**。
6. **提案到着後も違和感メモ・タグが完全に保持**（違和感は消されない）。
7. 破棄は人間操作で実行され、提案は消えるが**違和感は保持されたまま**。自動適用は一度も発生しない。
8. 統合候補収集も同providerを通り `/ai/suggest-merges` が **200** で応答
   （応答ペイロードに stub 候補1件を確認）。パネル内テキスト表示は即時プローブのため未確認
   （transport レベルで完全検証済み。表示確認が必要になれば再走行で追認可能）。

### スコープ注記

- `large-scale` provider の成功経路は対象外のまま: 設計上、外部エンドポイント・明示的オプトイン・
  許可リストを要求する（`_ensure_large_scale_allowlist`）。実外部接続を伴うため、
  実施する場合は人間の承認と実エンドポイントが前提（本Issueの残件ではなく運用時の受入項目）。
- compose 既定は `KJ_ATLAS_LLM_PROVIDER=none` のまま不変。オーバーレイは検証専用で、
  ユーザー向けデプロイには使用しない旨をファイル内に明記済み。
