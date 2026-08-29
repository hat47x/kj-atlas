# Issue: BUDGET-OPS-01 複雑性・性能予算の自己申告運用の定着

> 個人OSS段階（`ADR-0039`）の軽量起票。`ADR-0043` / `ADR-0046` の運用定着。docs/テンプレのみ。

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: TBD
- Scope: `01_Plans/issues/TEMPLATE.md`, `.github/pull_request_template.md`, `01_Plans/issues/done/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- Related Backlog: `BUDGET-OPS-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

`ADR-0043`（複雑性予算 CB-1..4）と `ADR-0046`（性能予算 PB-1..5）は「UI/性能影響 issue は予算1行を自己申告し、悪化時は `PRODUCT-QA-01` で確認」と定めたが、その**申告様式が TEMPLATE / PR テンプレ / 価値ゲートに組み込まれておらず、運用として定着していない**。定義はあるが守られる仕組みが無い。

## 2) 背景 / Context

- `ADR-0043` CB-1..4（認知負荷）、`ADR-0046` PB-1..5（計算負荷）、`ADR-0044` UQ（触れる品質次元の明記）。
- これらは「自己申告＋悪化時ゲート確認」という軽量運用で機能する設計（`ADR-0039` 準拠、強制機構は最小）。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 予算が「申告される仕組み」になって初めて、機能増加局面で根幹価値（思考を雑にしない／待たされない）が守られる。
- 安全: 安全境界は直接変えないため P3（基盤ADR完了後の運用整備）。
- 後方互換: テンプレ・docsのみ、コード変更なし。

## 4) 提案する解決策 / Proposed solution

- 変更対象（テンプレ・docs のみ）:
  - `01_Plans/issues/TEMPLATE.md` に、UI/性能影響 issue 向けの**任意1行ブロック**を追加：
    - `複雑性予算:` 初期表示への純増 / 保留操作の距離 / 取り消し導線（`ADR-0043` CB）
    - `性能予算:` 代表規模での主要操作 / 100ms超同期処理の worker 化（`ADR-0046` PB）
    - `触れるUQ次元:` UQ-1..6（`ADR-0044`）
  - `.github/pull_request_template.md` に同趣旨の任意チェック行を追加。
  - `PRODUCT-QA-01` の Go/No-Go に「予算申告で『悪化』を含む変更はゲート確認」を1項目追記。
- 最小単位: TEMPLATE への任意ブロック追加が中核。PR テンプレ／QA ゲートは追従。
- 非目標: 全 issue への必須化（軽量運用を維持、UI/性能影響時のみ）、自動 lint による強制。

## 5) 受入条件 / Acceptance criteria

- [x] `TEMPLATE.md` に複雑性/性能/UQ の予算申告1行ブロック（任意）が追加される。
- [x] `pull_request_template.md` に対応する任意チェックが追加される。
- [x] `PRODUCT-QA-01` に「予算『悪化』時のゲート確認」が1項目入る。
- [x] 申告は UI/性能影響 issue で任意、それ以外では不要（軽量運用、`ADR-0039`）。
- [x] 既存の必須メタ・validator を壊さない（docs-check 緑）。

### 実装証跡（2026-07-16）

- `TEMPLATE.md`: 「受入条件」の直前に「予算申告（UI・性能影響がある場合のみ、任意）」を新設し、複雑性予算（`ADR-0043` CB-1..4）・性能予算（`ADR-0046` PB-1..5）・触れるUQ次元（`ADR-0044`）の3行をプレースホルダ形式（`<... または N/A>`）で追加した。
- `.github/pull_request_template.md`: 既存の「複雑性予算（UI変更時）」節を「複雑性・性能予算 / UQ次元（UI・性能影響時）」へ拡張し、既存の複雑性予算3項目をそのまま維持しつつ、性能予算2項目と触れるUQ次元1項目を追加した。既存項目の文言・順序は変更していない。
- `issue-PRODUCT-QA-01-release-readiness-quality-gates.md`: 「判定方法」の箇条書きへ7番目の項目として「予算自己申告が『悪化』を含む場合は対応するゲート（主にG2主要操作、G4画面耐性）の確認対象に含める」を追加した。既存のゲート表・Value Gate表・重大度定義は変更していない。
- 検証結果: `rg -n "複雑性予算|性能予算|触れるUQ" 01_Plans/issues/TEMPLATE.md .github/pull_request_template.md` で両ファイルに3語すべて存在することを確認した。`python 01_Plans/issues/validate_active_issue_memos.py`・`python -m unittest 01_Plans.issues.tests.test_validate_active_issue_memos`はいずれもpass（Markdownのみの変更でvalidatorロジックへの影響なし）。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "複雑性予算|性能予算|触れるUQ" 01_Plans/issues/TEMPLATE.md .github/pull_request_template.md`
- 期待結果: 予算申告様式が3箇所に存在し、validator/unittest が緑。
- 未実施時の代替: テンプレ差分レビューで様式の存在を確認。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: 申告が形骸化。→「悪化」時のみ `PRODUCT-QA-01` 確認に接続して最小の強制力を持たせる。
- 影響範囲: テンプレ・docsのみ。ロールバック=追加ブロックの除去。

## 8) Additional context

- `CORE-VALUE-GUARD-01`（CVI）が「不変条件」を、本issueが「予算（漸増の歯止め）」を、それぞれ運用に乗せる関係。両者で機能増加下の根幹価値を守る。
