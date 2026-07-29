# Issue: DOC-IA-01 「サポート診断バンドル」が通常表示に常設されている

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Documentation
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `MVP-EXIT-01`
- Priority: P2
- Owner: Maintainer
- Scope: `04_Documentation/acceptance_check.md`, `03_Implement/frontend/src/App.tsx`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- Expected verification level: `docs-check`

## 課題

- 現在の問題: `04_Documentation/acceptance_check.md` は「AIによる提案、差分確認、パッチ、診断などは『詳細』を選ぶまで表示されません」と説明している。しかしヘッダーの「サポート診断バンドル」ボタンは `isAdvancedUiEnabled` の外にあり、通常表示に常設されている（隣接する `agent_task_export` / `agent_response_import` は `isAdvancedUiEnabled` で囲われている）。右側パネルの「診断を実行」も通常表示に出ている。
- 利用者または開発への影響: 文書と画面の説明が食い違う（`PRODUCT-QA-01` G5）。「詳細を使わなくても基本作業が完結する」という導線設計の説明が、利用者から見て正確でない。ただし操作は妨げられず、安全境界にも影響しない。

## 対応方針

判断が必要なため、実装を先に変更しない。次のどちらかを選ぶ。

- **案A（文書を直す）**: サポート診断は「困ったときの基本操作」であり詳細の対象外と定義し、`acceptance_check.md` の記述を「AIによる提案、差分確認、パッチは詳細を選ぶまで表示されない」へ改める。診断が通常表示にある理由を一文で添える。
- **案B（実装を直す）**: 診断系も詳細の内側へ移し、文書の現行記述どおりにする。通常表示のヘッダーが1つ減る（`ADR-0043` 複雑性予算の観点では有利）。

実施しないこと: 案を決めずに片方だけ変更すること。

## 予算申告

- 複雑性予算（`ADR-0043` CB-1）: 案Bを選ぶ場合、初期表示のヘッダーボタンが1つ減る。
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [ ] 案Aまたは案Bを選び、理由を記録する。
- [ ] 選んだ案に従って文書または実装を変更し、両者が一致する。
- [ ] 公開画像の再撮影（`DOC-SHOT-01`）より前に決着させる。

## 検証計画

- 実行する確認: `acceptance_check.md` の記述と、通常表示（詳細OFF）のヘッダー・右側パネルの実際の表示を突き合わせる。
- 期待結果: 文書に書かれた「詳細を選ぶまで出ないもの」の一覧と、実際に隠れているものが一致する。

## 補足

- 「診断を実行」は2026-07-11撮影の公開画像にも通常表示で写っており、このずれは今回のヘッダー変更より前から存在していた可能性が高い。
- 調査記録は `03_Implement/frontend/docs/mvp_exit_human_acceptance_log_2026-07-29.md` §3 D3。
