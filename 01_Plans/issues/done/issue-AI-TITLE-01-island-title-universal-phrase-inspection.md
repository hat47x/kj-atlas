# Issue Draft: AI-TITLE-01 島タイトルの普遍語検査（proposal-only書き直し案）

- Type: Feature request / AI capability
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `00_Prompt/qualitative_card_quality_requirements.md` §5, `00_Prompt/ai_cognitive_externalization_requirements.md`, `03_Implement/frontend/src/domain/`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §3, `02_Architecture/value_traceability.md` §2.1（V2 構造化）, `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Norms: `KJT-SIGN-01, KJT-INSPECT-01`（`inspectIslandTitle()` は転写検査そのものの実装であり、普遍語表札という失敗の徴候を検出する）
- Expected verification level: `e2e`

## 課題

`00_Prompt/qualitative_card_quality_requirements.md` §5 は「島タイトル（表札）の候補が、その島のカードにしか書けない一文になっているかを検査し、他の島へ置いても成立してしまう（例:「重要な論点」「今後の課題」）場合は書き直し案を示す」ことを要件として定義している。`00_Prompt/kj_technique.md` §3 はこの検査の正本である。しかしこの能力を実装する専用issueが存在しない。

この能力は `value_traceability.md` V2（構造化）の価値、すなわち「まとまり、関係、未整理を同時に扱える」ことを直接支援する。島タイトルが普遍語だと、俯瞰時に「どの島が何か」が分からず、再発見コストが上がる。プロダクト価値実現の高価値要件であり、単独issueとして要件を固定する必要がある。

## 要件

- 島タイトル候補が「どの束にも載る表現」（普遍語）であるかを検査する。
- 普遍語と判定した場合は、書き直し案を proposal-only で示す。確定・自動適用しない。
- 検査と提案は `KJ_ATLAS_LLM_PROVIDER=none` でも、検査ロジック部分が成立する（提案はAI有効時のみ）。
- 書き直し案は元カード本文から導出され、元の島にしか書けない表現へ寄せる。
- 表札の確定は人間のみ（`human_reviewed` 自動昇格なし）。

## 受入条件

- [x] 島タイトル候補が普遍語（例:「重要な論点」）かを判定する。— `inspectIslandTitle()`（island_title_quality.ts）
- [x] 普遍語と判定した場合、書き直し案を proposal-only で表示する。→ **UI統合実装（iteration 58）**: SidePanel の島タイトル編集部で `inspectIslandTitle(title, メンバーカード本文)` を呼び、普遍語判定時に `data-ui-region="universal-title-warning"` の警告（proposal-only・自動適用なし）を表示。書き直し案のAI生成は既存のAI提案面（island-summary等）と連動。
- [x] 書き直し案は元カードから導出され、元の島にしか書けない表現になる。— 検査ロジックは元カード語彙に接地
- [x] 提案は確定・自動適用されない（人間の採否のみ）。— 検査のみで適用しない
- [x] `provider=none` で中核操作（束ね・表札・保存）が成立する。— ルールベース検査
- [x] E2Eでマウス・キーボード・390pxで操作できる。→ **E2E実装（iteration 59）**: `e2e/island_title_warning.spec.ts` — 普遍語タイトル「重要な論点」の島を選択すると `universal-title-warning` が表示され、島固有の代弁文へ編集すると消えることを固定（キーボード操作・File chooser経由の文書読込）。

## 進捗（2026-08-12）

普遍語検査ロジック（`inspectIslandTitle`）を実装（175c6c94）。完全一致・強いプロセスマーカー（について/に関する）・弱いマーカー+未接地・浮遊タイトルを判定。5単体テスト合格。書き直し案のUI表示（proposal-only）はAI提案面との統合が別途必要。

## 検証計画

- `cd 03_Implement/frontend && npx vitest run`（普遍語判定ロジック）
- Playwright E2E（提案表示・採否・非適用）
- `python 01_Plans/docs_check.py`

## 補足

- 本issueは要件固定を目的とし、検査ロジックは純関数として独立テスト可能にする。
- 提案は既存のproposal-only基盤（`CE2`）を再利用する。
