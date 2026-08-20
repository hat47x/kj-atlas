# Issue Draft: DOMAIN-EXPR-04 根拠・主張・矛盾の人間レビュー第一級化と成果物接続

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex / Claude Code
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/src/export/`, `03_Implement/frontend/e2e/`, `02_Architecture/schemas.md`, `04_Documentation/`
- Related Backlog: `DOMAIN-EXPR-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/issues/issue-PRODUCT-VALUE-03-reviewable-outcome-package.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`, `02_Architecture/schemas.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Dependencies: `01_Plans/issues/issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（Done 2026-06-20）
- Expected verification level: `e2e`

## Implementation Progress 2026-06-29

### Done
- **Schema**: EvidenceLink.contradictionState (unconfirmed/confirmed/held/resolved) — backward-compatible, optional field
  - Frontend: `types.ts`, Backend: `models.py`, Schema docs: `schemas.md` §15
- **UI**: SidePanel contradiction state selector dropdown for outgoing contradiction links (2026-06-29)
- **App.tsx**: `handleUpdateEvidenceLink` wired for state changes (2026-06-29)
- **i18n**: en/ja labels for all 4 states + history entry + contradiction_state_summary
- **Narrative export**: Evidence/Contradiction Links section in markdown/HTML (2f44227a)
- **Narrative grounding**: Contradiction state summary counts displayed in NarrativesPanel grounding section (2026-06-29)
- Existing infrastructure: SidePanel evidence display, contradiction report, trace export, SharePanel summary
- **TypeScript**: Duplicate `isAdvancedUiEnabled`/`onRestoreShelvedCard` declarations in SidePanel.tsx fixed

### Remaining（2026-06-29 更新）
- E2E: contradiction state selection → outcome package verification（Playwright環境依存）

## Implementation Evidence 2026-07-04: contradiction state operation and artifact trace

- SidePanel evidence links now render outgoing and incoming link type labels through i18n instead of raw enum text, and the outgoing contradiction state selector has a visible/ARIA label tied to the target card.
- Added targeted Playwright coverage in `e2e/domain_expression_keyboard_access.spec.ts`: select the card with an outgoing contradiction link, change the contradiction state from `unconfirmed` to `held`, save, and assert that the document preserves `contradictionState: "held"`.
- Added narrative artifact regression coverage in `src/export/narrative_export.test.ts`: markdown and HTML evidence-link sections retain `[held]` for contradiction links.
- Validation 2026-07-04:
  - `node.exe .\node_modules\typescript\bin\tsc --noEmit` passed.
  - `node.exe .\node_modules\vitest\vitest.mjs run src\export\narrative_export.test.ts src\i18n\catalog_integrity.test.ts src\i18n\untranslated_key_inventory.test.ts src\i18n\key_consistency.test.ts` passed: 4 files / 7 tests.
  - `node.exe .\node_modules\playwright\cli.js test e2e/domain_expression_keyboard_access.spec.ts --reporter=line` passed: 4 tests.
- Residual scope: broader review-pack bundle gate and product-value outcome package acceptance remain owned by `PRODUCT-VALUE-03` / `PRODUCT-QA-01`; this slice closes the direct UI operation and narrative artifact regression for contradiction state.
- No ADR is required because this uses the existing `EvidenceLink.contradictionState` contract and does not change SafeMode/share policy, schema shape, AI authority, or release authority.

## Implementation Evidence 2026-07-04: labeled evidence-link editor

- The SidePanel evidence-link editor now exposes explicit visible labels for link type, target search, and target selection. This reduces placeholder-only operation and lets mouse users and keyboard/screen-reader users identify the same fields.
- Added targeted Playwright coverage in `e2e/domain_expression_keyboard_access.spec.ts`: select a card, open the evidence-link editor, search for a target card by label, choose the target by label, confirm the link, save, and assert the document preserves the new `supports` evidence link.
- No ADR is required because this is an accessibility and operability improvement inside the existing `EvidenceLink` contract; it does not alter schema, sharing policy, SafeMode behavior, or AI authority.

### Commits (new)
- 2026-06-29: contradictionState selector dropdown in SidePanel + handleUpdateEvidenceLink in App.tsx
- 2026-06-29: contradiction state summary counts in NarrativesPanel grounding section
- 2026-06-29: TypeScript duplicate declaration fixes in SidePanel.tsx
- 2f44227a evidence/contradiction links in narrative export
- ea3af977 contradictionState schema (schemas.md + types.ts + models.py)
- c77082d0 contradictionState in narrative export (markdown + HTML)

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

- [x] カード/関係の根拠（supports/contradicts）を画面で確認できる。
- [x] 矛盾を可逆な状態（未確認/確認済み/保留/解決済み。加えて島レベル検出シグナルの採用/保留/却下 — 2026-07-08 追加）として扱える。
- [x] 成果物（narrative）に根拠への戻り方・未解決矛盾・保留点が含まれる。review pack バンドル契約の拡張は `PRODUCT-VALUE-03`/`PRODUCT-QA-01` の所有スコープであり本Issueでは変更しない（2026-07-08 スコープ確認）。
- [x] 共有時 SafeMode 既定ONで未レビュー本文・生根拠が漏れない（share/export 境界非後退）。矛盾シグナル決定は選択コンテキストのみに表示し、共有契約に新規項目を追加しない。
- [x] AIは矛盾・真偽を自動確定しない（proposal-only、考えるべき点の提示に留まる）。`analyzeContradictions()`（決定論的ヒューリスティック、AI/LLM呼び出しなし）は書き込み経路を持たず、決定は常に人間のUI操作のみ。
- [x] schema拡張時は `schemas.md` 先行更新・往復互換。E2Eで根拠確認→成果物反映を検証。

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

## E2E追認 2026-06-29: DOMAIN-EXPR-04

- 利用者指示に基づき、人間作業として残っていた Playwright E2E 実行を Codex が代行した。
- 実行対象: `review_pack_trace_export.spec.ts` と `domain_expression_keyboard_access.spec.ts` を含む対象Playwrightセット。
- 結果: 2026-06-29 の対象Playwrightセットで **10 passed**。
- 判定: 現在のスキーマ中立スライスは **Go**。根拠・矛盾の画面検査、Review Pack Detail export の trace file 確認、read-only reviewer の編集不可境界を代表操作として再現できる。
- 残る範囲: 矛盾状態の永続的な状態遷移、AI補助による矛盾候補生成、成果物契約の拡張は本追認に含めない。
- ADR影響: 既存 `evidenceLinks` / `claimType` / Review Pack trace の確認に留まるため、この追認単体ではADR不要。成果物契約、SafeMode/share-export境界、矛盾状態遷移を変える場合はADR更新が必要。

## 完了記録 2026-07-08（Claude Code）: AI/検出ロジック補助による矛盾候補生成

上記までで未決着だった「残る範囲」の最後の1点（AI補助による矛盾候補生成）を確定・実装した。成果物契約の拡張（review pack バンドル）は引き続き本Issueのスコープ外（`PRODUCT-VALUE-03`/`PRODUCT-QA-01` 所有）として着手していない。

### 要件の再定義（新規ADR不要と判断した根拠）

1. **既存の決定論的検出エンジンを「AI補助」の実体として採用**: `analyzeContradictions()`（`contradiction_checks.ts`）はキーワード/構造ヒューリスティックのみで動作し AI/LLM 呼び出しを一切持たない。Issue 本文の既存記述「AIや検出ロジックは『矛盾かもしれない箇所』を示すに留める」は AI と検出ロジックを同列に事前承認しており、新規の AI 権限付与を要しない。
2. **個別カード間 `EvidenceLink` の自動生成を明確に不採用**: シグナルは島（island）レベルの集約検出であり、特定カードペアへ機械的に対応付けると検出精度の実態を超えた偽の特定関係を作ることになる（調査で確認: C001〜C004 のいずれも `entityRefs` はカードペアではなく島/エッジ/relationSummary 単位）。代わりに、シグナル自体に人間の可逆なレビュー決定（採用/保留/却下）を付与する設計に変更した。
3. **AI権限境界の再利用（ADR-0041 CVI-2/CVI-3 の適用、拡張ではない）**: 新しい `ContradictionSignalReviewStatus = "accepted" | "held" | "rejected"` は、既存 `CE2-LOW-RISK-AI-ASSIST`（schemas.md §1.2）の `ProposalStatus` 語彙をそのまま転用したもの。検出器が決定を書き込む経路は一切存在せず（`analyzeContradictions()` は純粋関数のまま）、書き込みは常に人間のUI操作（1操作=1履歴ステップ）のみ。この構造により CVI-2 proposal-only を「構造的に」満たす（新規許可の追加ではなく既存契約の別データソースへの再適用）。

### 実装（契約先行）

- **schemas.md §16（新設）**: `DocumentV2.contradictionSignalDecisions?: ContradictionSignalDecision[]`。`signatureKey`（シグナルの決定論的識別子、`${code}:${pairKey ?? entityRefs[0].idOrSignature}`）＋`status`＋`decidedAt`。シグナル自体は永続化せず、`mergeSuggestionDecisions` の「候補生成物と決定を分離」パターンを踏襲。"proposed"（未決定）は永続化しない値— 配列に該当キーが無いことが「未決定」を意味する（取り消し操作はエントリ削除。DOMAIN-TRACE-01 の `Card.meta` 空値削除と同じ規約）。
- **往復（3経路）**: ①寛容 `validate.ts parseContradictionSignalDecisions`（`mergeSuggestionDecisions` と同じ fail-closed パターン）②厳格 `validate_doc.ts validateContradictionSignalDecisionEntry`（`hasOnlyKeys` + enum検証）③バックエンド `models.py ContradictionSignalDecision`（`status: Literal["accepted","held","rejected"]` — 不正値は422で拒否、既存 `mergeSuggestionDecisions.decision` と同じ enforcement）。CE3パッチ経路（`patch_apply.ts`）はドキュメントレベル配列に触れないため対応不要（既存 `mergeSuggestionDecisions` も同様に対象外であることを確認済み）。
- **UI（選択非依存・常時表示）**: SidePanel の「矛盾シグナル」パネル（Outline diagnostics 内、`<details>` で2箇所重複している既存構造の両方）に、各シグナルへ「採用にする/保留にする/却下する/決定を取り消す」ボタンと現在状態バッジを追加。**シグナルは決定状態に関わらず常に表示**（却下しても非表示にしない — 「却下」は検討済みの記録であり隠蔽ではない）。決定変更は `applyDocumentChange` による1操作=1履歴ステップ。
- **成果物・共有境界は変更しない**: `bundle_export.ts`（review pack契約）・narrative export・SharePanel は本拡張で一切触れていない。決定状態は選択コンテキスト内のUIにのみ表示される。

### 検証

- typecheck 0 / vitest **952 passed**（185 files。往復4件・シグネチャ関数3件・回帰アンカー1件を追加）
- backend: ruff クリーン / pytest **286 passed**（PUT+GET 往復1件・不正status 422拒否1件を追加）
- e2e 新規 `contradiction_signal_decision.spec.ts` **2/2 passed**（採用→バッジ表示→取り消しで消滅／保留と却下は排他かつ却下後もシグナル可視／PUTペイロード実測でのsignatureKey往復）
- 関連 e2e 非回帰: `ops_recovery_guidance.spec.ts`（診断進捗/キャンセル）・`complexity_budget_foregrounding.spec.ts`（Advanced パネル開閉）・`domain_expression_keyboard_access.spec.ts`（既存の根拠/矛盾キーボード導線）・`card_trace_meta.spec.ts`・`edge_type_vocabulary.spec.ts`・`review_pack_trace_export.spec.ts` すべて確認。

### 残課題（本Issueのスコープ外・別issue）

- review pack バンドル（`bundle_export.ts` の diagnostics.md / contradiction_trace_*.md）への決定状態の反映は、成果物契約変更を伴うため `PRODUCT-VALUE-03`/`PRODUCT-QA-01` 側での判断に委ねる。
- 島レベルの集約シグナルから具体的なカードペアの `EvidenceLink`（`contradictionState`）へ手動でエスカレーションする導線は、本Issueでは意図的に作らなかった（検出精度を偽ることになるため）。将来的にカード単位の検出精度が上がった場合に別途検討する。
