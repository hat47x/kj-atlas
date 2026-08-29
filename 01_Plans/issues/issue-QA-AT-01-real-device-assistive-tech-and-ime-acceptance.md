# Issue Draft: QA-AT-01 実機アクセシビリティ・IME・OSショートカットの受入確認

- Type: Feature request / QA
- Status: Draft
- Source Issue: `01_Plans/issues/done/issue-MVP-EXIT-01-productization-readiness.md`（残余リスク）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/`, `04_Documentation/acceptance_check.md`
- Related ADR/Spec: `02_Architecture/value_traceability.md` §2.1.1（V0〜V4 残課題「実機アクセシビリティ」）, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- Expected verification level: `e2e`（実機AT・IME・OSでの手動受入。Playwrightの機械代替では不足する残余リスクを対象とする）

## 課題

`value_traceability.md` §2.1.1 は V0〜V4 の全ループで「実機アクセシビリティ」を残課題として挙げている。`MVP-EXIT-01`（2026-07-29 ゲートレコード）はキーボード（10/10）とaccessibility tree（6/6）を機械代替で充足したが、以下の3項目を**実機ATでの残余リスク**として明記した（`03_Implement/frontend/docs/mvp_exit_human_acceptance_log_2026-07-29.md`）:

1. 実機スクリーンリーダーの読み上げ語順（NVDA / VoiceOver / JAWS）
2. IME変換中のキーボード挙動
3. OSショートカット競合（⌘K等）

これらは機械代替では検証できず、実機AT・実OS・実IMEが必要な人間確認である。`MVP-EXIT-01` は「残る人間確認」として記載するが、専用issueで要件・手順・証跡を固定しないと、出荷ゲートの完了条件として追跡できない。

## 要件

- 実機スクリーンリーダーで開始・編集・保存・共有前確認の読み上げ語順を確認する。
- IME変換中のカード本文入力・ショートカット挙動を確認する。
- OSショートカットとの競合（未レビュー状態の取り消し、カード作成等）を確認する。
- 確認結果を `04_Documentation/acceptance_check.md` の手動確認手順として固定する。

## 受入条件

- [ ] 実機スクリーンリーダー（最低1種）で主要操作の読み上げ語順を確認し、結果が記録される。
- [ ] IME変換中の主要操作が完了できる。
- [ ] OSショートカット競合がない、または代替経路が明示される。
- [ ] 確認手順が `acceptance_check.md` に固定される。
- [ ] 検出した欠陥は個別issueへ切り出される（本issueに詳細ログを積まない）。

## 検証計画

- 実機ATでの手動確認（スクリーンリーダー・IME・OS）
- `python 01_Plans/docs_check.py`

## 補足

- 本issueは `MVP-EXIT-01` の残余リスクを個別追跡する。完了条件は機械代替ではなく実機確認。
- 検出欠陥は `UI-QUALITY-A11Y-*` / `QA-MONKEY-*` パターンで個別issue化する。
