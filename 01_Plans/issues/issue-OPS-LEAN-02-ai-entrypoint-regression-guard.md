# Issue: OPS-LEAN-02 生成AI入口の肥大化回帰を防止する

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `AGENTS.md`, `00_Prompt/`, `01_Plans/tests/`, `01_Plans/lean_operations_inventory.md`, `.github/workflows/ci.yml`
- Related ADR/Spec: `ADR-0039`, `OPS-LEAN-01`
- Expected verification level: `docs-check`

## 課題

- `OPS-LEAN-01` で108行へ縮小した `AGENTS.md` が、別ブランチ統合後に304行の全件Read Orderと個別ファイル目録へ戻った。
- 新しい契約やADRを追加するたびに全タスクの必須コンテキストを増やすと、生成AIのトークン消費と判断ノイズが再び増える。

## 対応方針

- Document V1再基準化など新しい正本は維持し、関係するタスクの入口だけへ配置する。
- 補助文書に残る旧Read Order参照を、タスク別のオンデマンド読取へ統一する。
- `AGENTS.md` の規模と旧運用表現を小さな契約テストで検査する。
- 新しいADRは起票しない。Accepted済みの `ADR-0039` を守る回帰修正であり、新しい長期判断ではない。

## 受入条件

- [x] `AGENTS.md` が180行以内で、タスク別の正本選択を案内する。
- [x] Document V1契約の正本へデータ契約タスクから到達できる。
- [x] 全ADR読取、全件Project Map更新、固定Read Orderが通常手順に残らない。
- [x] 回帰テスト、issue validator、文書リンク検査が成功し、CIから実行される。

## 検証計画

- `python -m unittest 01_Plans/tests/test_agents_minimal_context.py`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python 01_Plans/docs_contract_checks.py`
- `git diff --check`

## 完了記録 2026-07-15

- 生成AI入口をタスク別の最小読取へ戻し、Document V1契約は該当タスクの入口として保持した。
- 旧Read Orderを参照していた生成AI向け補助文書5件をオンデマンド読取へ同期した。
- 行数上限と旧運用表現を検査する回帰テストを追加した。
- 標準ライブラリだけで完了する文書検査を既存Backend CIジョブへ追加し、統合後の回帰を自動検出できるようにした。
