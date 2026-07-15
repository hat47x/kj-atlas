# Issue: OPS-LEAN-01 小規模OSS向けに過度な運用を削減する

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `AGENTS.md`, `00_Prompt/`, `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related ADR/Spec: `ADR-0039`, `01_Plans/lean_operations_inventory.md`
- Expected verification level: `docs-check`

## 課題

- 個人OSS・プレリリース向けの軽量化を `ADR-0039` で決定済みだが、全件Read Order、多重台帳同期、rerunログ、仮想多役割、重量級issueテンプレートが残っている。
- 主要な運用入口だけで約372KBあり、生成AIが無関係な履歴を読むと、コンテキスト消費と判断ノイズが増える。

## 対応方針

- `lean_operations_inventory.md` のP0から順に削減する。
- 現行判断はActive issue memoとGit履歴へ集約し、履歴は削除せず通常読取から外す。
- 安全不変条件、リスクに応じたテスト、公開文書と内部文書の分離は維持する。
- 非目標: 製品の安全機能削除、テスト一律削減、過去の意思決定記録の改変。

## 受入条件

- [x] AGENTSの必須読取をタスク別の最小読取へ変更する。
- [x] issueテンプレートを最小メタ、課題、方針、AC、検証へ縮小する。
- [x] 削減対象、維持対象、実行順、再導入条件を一覧化する。
- [x] issues READMEをActive索引中心へ縮小し、反復同期ログはGit履歴から参照する形へ変更する。
- [x] dashboardとdecision-packを現行正本から外し、Git履歴を参照する短い案内へ置き換える。
- [x] AI引き継ぎと仮想会議をオンデマンドの最小補足へ縮小し、仮想役職をsolo開発の通常手順から外す。2者承認は組織がJIT provisioning例外を使う場合だけのプロファイルとする。
- [x] Active一覧の手動表と件数同期を廃止し、memoメタデータからtriage表示・validator検証する。
- [x] docs-checkとリンク検査が成功する。

## 検証計画

- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg` でAGENTSの旧必須Read Order、Project Map個別列挙、固定同期ルールが残っていないことを確認する。
- 文書リンクとMarkdown差分を確認する。

## 補足

- 新ADRは起票しない。削減判断はAccepted済みの `ADR-0039` の実行であり、新しい長期判断を追加しないため。
- 大量の履歴移動はレビュー可能な単位へ分け、現在のP0軽量化とは別コミットにする。

## 進捗記録 2026-07-15: AI入口と契約テストの分離

- backendのデータモデル契約テストが、AGENTSに `data_model_operations_overview.md` の個別列挙を要求し、タスク別最小読取への変更をCIで拒否していた。
- データモデル設計文書間の参照検査は維持し、AI入口だけを対象外にした。AGENTSは `02_Architecture/` のタスク別入口を示し、個別ファイル目録を持たない。
- `test_data_model_operations_contract.py` の対象testとbackend非PostgreSQL test全体で回帰を確認する。

## 完了記録 2026-07-15

- `validate_active_issue_memos.py --root 01_Plans/issues` でActive memo 31件を検証し、validator・triage・データモデル契約の対象15テストが成功した。
- OPS-LEAN実装コミットで変更したMarkdown 21文書について相対リンク23件を検査し、欠落0件を確認した。
- `AGENTS.md` に旧必須`Read Order`、全件`Project Map`、固定同期ルールの見出しが復活していないことと、`git diff --check`成功を確認した。
- 全受入条件を満たしたためDoneとする。リポジトリ全体の既存リンク品質は`DX-DOC-02`の文書契約CIで別管理し、本Issueの軽量化範囲へ混在させない。
