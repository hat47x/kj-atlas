# Issue: DOC-AI-01 生成AI向け文書の改善

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer
- Scope: `AGENTS.md`, `CLAUDE.md`, `RTK.md`, `00_Prompt/*.md`
- Related ADR/Spec: `ADR-0067-three-element-constraint-design-method.md`, `02_Architecture/dogfooding-ai-collaboration-plan.html`
- Expected verification level: `docs-check`

## 課題

- 現在の問題: 既存文書（AGENTS.md, CLAUDE.md 等）はAIエージェント向けの指示として書かれているが、自律的な設計判断に必要な判断基準・三要素牽制の視点・操作別モデルレベル・自律判断の許容範囲が明示されていない
- 利用者または開発への影響: AIが自律的に設計判断を行えないため、人間の介在が常に必要。自律開発レベル2以降への移行ができない

## 対応方針

- 実施すること:
  1. AGENTS.md に三要素牽制設計法の適用ルールを追加（いつ・どの設計判断で三者チェックを必須とするか）
  2. AGENTS.md に操作別モデルレベル表を追加（KJ操作ごとの推奨モデルと選択基準）
  3. AGENTS.md に自律判断の許容範囲をレベル分けで定義（L1: 人間判断+AI補助 → L4: AI自律）
  4. CLAUDE.md / RTK.md に三要素牽制の視点を埋め込み（設計判断時のチェックリスト）
  5. 00_Prompt/*.md に各KJ操作のAI実行手順を追加（入力・出力・判断基準・停止条件）
- 実施しないこと:
  1. 既存の「侵してはならない核」の変更
  2. AIによる自律的な安全境界の変更許可

## 予算申告

- 複雑性予算（ADR-0043 CB-1..4）: N/A（文書改善のみ、コード変更なし）
- 性能予算（ADR-0046 PB-1..5）: N/A
- 触れるUQ次元（ADR-0044）: N/A

## 受入条件

- [ ] AGENTS.md に三要素牽制の適用ルールが明記されている
- [ ] AGENTS.md に操作別モデルレベル対応表が含まれる
- [ ] AGENTS.md に自律判断の許容範囲（L1〜L4）が定義されている
- [ ] 00_Prompt/*.md のKJ操作にAI実行手順が追加されている
- [ ] 既存の核（SafeMode・proposal-only・反スコアリング・キャンバス主従）を侵していない

## 補足

- 本issueは `dogfooding-ai-collaboration-plan.html` のP1項目
- P2（モデルレベル定義）と並行して作業可能。P2の成果物をP1の文書に反映する
