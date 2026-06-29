# Issue Draft: DOMAIN-EXPR-04 根拠・主張・矛盾の人間レビュー第一級化と成果物接続

- Type: Feature request
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/src/export/`, `03_Implement/frontend/e2e/`, `02_Architecture/schemas.md`, `04_Documentation/`
- Related Backlog: `DOMAIN-EXPR-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/issues/issue-PRODUCT-VALUE-03-reviewable-outcome-package.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`, `02_Architecture/schemas.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Dependencies: `01_Plans/issues/issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（Done 2026-06-20）
- Expected verification level: `e2e`

## Implementation Progress 2026-06-27

### Done
- **Schema**: EvidenceLink.contradictionState (unconfirmed/confirmed/held/resolved) — backward-compatible, optional field
  - Frontend: `types.ts`, Backend: `models.py`, Schema docs: `schemas.md` §15
- **UI**: SidePanel contradiction state selector dropdown for outgoing contradiction links
- **App.tsx**: `handleUpdateEvidenceLink` wired for state changes
- **i18n**: en/ja labels for all 4 states + history entry
- **Narrative export**: Evidence/Contradiction Links section in markdown/HTML (2f44227a)
- Existing infrastructure: SidePanel evidence display, contradiction report, trace export, SharePanel summary

### Remaining（2026-06-29 更新）
- E2E: contradiction state selection → outcome package verification（Playwright環境依存）
- Contradiction state integration with narrative grounding summary counts

### Commits
- 2f44227a evidence/contradiction links in narrative export
- ea3af977 contradictionState schema (schemas.md + types.ts + models.py)
- 668138e3 contradiction state UI (SidePanel selector + App.tsx handler + i18n)
- c77082d0 contradictionState in narrative export (markdown + HTML)
- ea3af977 contradictionState schema (schemas.md + types.ts + models.py)
- 668138e3 contradiction state UI (SidePanel selector + App.tsx handler + i18n)

## Draft→Open 2026-06-21
DOMAIN-EXPR-01 Doneにより依存充足。ADR-0040 Phase 4（根拠・主張・矛盾を人間レビュー第一級対象＋成果物要素へ接続）。
PRODUCT-VALUE-03と連携。

> 個人OSS段階（`ADR-0039`）の軽量起票。`ADR-0040` Phase 4。`PRODUCT-VALUE-03`（成果物化）と連携。

## Dependencies

- 前段: `issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（根拠/矛盾の読取確認を起点に、人間レビューと成果物接続へ広げる）。

## 1) 課題 / Problem statement

`value_traceability.md` §2.1.1 が「根拠・主張・反対意見の追跡: ContextBundleには含まれるが、利用者が見て操作する境界が弱い」と明記。`evidenceLinks`（supports/contradicts）と `claimType`、矛盾検出は型・AI入力境界には存在するが、利用者が「根拠を確認・付与し、矛盾を確認済み/保留/解決済みとして扱い、それを成果物へ含める」第一級の導線が無い。社会的目標（説明可能・レビュー可能な成果物）の最終段が未到達。

## 2) 背景 / Context

- `ADR-0040` Phase 4。`PRODUCT-VALUE-03` の reviewable package 最小要素（確定点/保留点/未レビュー情報/根拠への戻り方）へ、根拠・主張・矛盾を接続する。
- 既存資産: `EvidenceLink`、`claimType`、contradiction checks、evidence overlay、trace export、narratives。
- `ai_cognitive_externalization_requirements.md` §9: AIは contradiction/evidence から「考えるべき点」を提示してよいが真偽を断定しない。

## 3) 提案する解決策 / Proposed solution

- Frontend:
  - 選択対象で根拠（supports/contradicts）を確認、人間レビュー対象として扱う。
  - 矛盾を「未確認 / 確認済み / 保留 / 解決済み」の状態として可逆に扱う（状態の永続化が必要なら加算スキーマ、`schemas.md` 先行）。
  - 成果物（narrative / review pack / export）へ、根拠リンクと未解決矛盾・保留点を含める。
- 非目標: AIによる真偽確定・矛盾の自動解決、証拠能力を持つ法的監査証跡、採点。

## 4) 受入条件 / Acceptance criteria

- [ ] カード/関係の根拠（supports/contradicts）を画面で確認できる。
- [ ] 矛盾を可逆な状態（未確認/確認済み/保留/解決済み）として扱える。
- [ ] 成果物（export/narrative/review pack）に根拠への戻り方・未解決矛盾・保留点が含まれる。
- [ ] 共有時 SafeMode 既定ONで未レビュー本文・生根拠が漏れない（share/export 境界非後退）。
- [ ] AIは矛盾・真偽を自動確定しない（proposal-only、考えるべき点の提示に留まる）。
- [ ] schema拡張時は `schemas.md` 先行更新・往復互換。E2Eで根拠確認→成果物反映を検証。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node ./node_modules/typescript/bin/tsc --noEmit`
  - `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run src/export src/domain`
  - `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test --reporter=line`
  - `rg -n "evidenceLinks|contradiction|claimType|narrative" 03_Implement/frontend/src 02_Architecture/schemas.md`
- 期待結果: 根拠・矛盾が人間レビューと成果物に第一級で現れ、安全境界が保たれる。
- 未実施時の代替: 成果物要素チェックリストと export golden 比較。

## 6) リスクとロールバック / Risks & rollback

- 失敗モード: 成果物に未レビュー根拠が混入し SafeMode 境界を侵す。
- 影響範囲: export/bundle、narratives、SharePanel、schemas。
- ロールバック: 成果物への根拠包含を無効化し、表示のみへ縮退（共有安全側へ倒す）。

## Open gate sync 2026-06-04

- 現在の基準: `origin/main` は `0133c744b60e4cc5f0c48435a62c72fbb5ca9f52`。DOMAIN-EXPR-01 の evidence intake と PRODUCT-VALUE-03 の reviewable outcome package 整理を参照する。
- ステータスへの影響: このissueは引き続き `Draft`。根拠・主張・矛盾は成果物と共有境界に直結するため、UI実装より先に、保存対象・表示対象・共有対象の境界を確定する。
- Phase 1 依存ゲート: DOMAIN-EXPR-01 が読み取り専用の `claimType` / `reviewState` / `evidenceLinks` 表示基準として受け入れられてから、このissueで人間レビュー用の操作導線を広げる。
- PRODUCT-VALUE-03 ゲート: review pack / narrative / export に含める最小要素を、確定点・保留点・未レビュー情報・根拠への戻り方として確認する。成果物契約を変更する場合は、PRODUCT-VALUE-03側のissueまたはADRと同期する。
- 根拠・主張契約ゲート: 最初の実装で既存の `EvidenceLink` / `claimType` / ContextBundle `evidence` をそのまま表示するのか、新しいレビュー状態や矛盾状態を永続化するのかを決める。スキーマを増やす場合は `02_Architecture/schemas.md` を先に更新する。
- 矛盾状態ゲート: AIや検出ロジックは「矛盾かもしれない箇所」を示すに留める。未確認、確認済み、保留、解決済みなどの状態を永続化する場合は、人間が変更した事実とAIが提案した事実を分けて記録する。
- SafeMode / share-export ゲート: UI/APIの `safeMode` 既定ON、`allowUnreviewedText=false`、`KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` などの安全境界を後退させない。共有・エクスポート時は、未レビュー本文、生根拠、未確認矛盾が誤って確定情報として見えないことを先に検証する。
- ADRゲート: 既存フィールドの読み取り表示だけならADR不要。矛盾状態遷移の永続化、review pack要素の変更、AIが真偽判定を行うように見える表示、SafeMode/share-export境界の変更が必要な場合は、実装前にADRを作成または更新する。
- 推奨する次のスライス: まずスキーマ中立で、選択中カードまたは関係に紐づく `evidenceLinks` と `claimType` を表示し、成果物に「根拠へ戻るための参照」と「未レビュー/保留の明示」を含める設計メモとE2E観点を作る。矛盾状態の永続化とAI補助は後続判断に分離する。
- この同期は実装を承認しない。成果物価値、安全境界、AIの役割を1つのPRに混ぜないため、次の判断単位を切り出す更新である。

## 7) Additional context

- ADR化が必要になる条件: 矛盾状態遷移を永続化する、または成果物契約（review pack要素）を変更する場合は `PRODUCT-VALUE-03` と同期してADR化する。
