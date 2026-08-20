# Issue: DOC-NORM-03 `validate_active_issue_memos.py` が active issue の配置ミスを「ファイル欠落」と誤報告する

- Type: Bug / Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/issues/validate_active_issue_memos.py`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `discover_active_rows()` は `root.rglob("issue-*.md")` で `01_Plans/issues/` 配下を再帰的に探索し、`Status` が active（`Draft`/`Open`/`In Progress`）な memo を `ActiveMemoRow` として収集する。しかし `ActiveMemoRow.memo` には **ファイル名のみ**（`memo_path.name`）を保持し、どのサブディレクトリで見つかったかの情報を捨てる。

  続く `validate_rows()` は `memo_path = root / row.memo` で存在確認するが、この式は常に `issues/` 直下を前提にする。したがって、何らかの理由で active status の memo が `issues/done/` 配下に置かれると（本来あるべき状態ではないが、実際に一度発生した——`issue-DX-DESIGN-CHECK-02` を `done/` へ移した際、`Status: Draft` の版が誤ってコミットされた事故で再現した）、`rglob` は正しく見つけているのに、存在確認だけ `issues/` 直下を探して失敗し、**"missing memo file" という誤った診断**を出す。実際にはファイルは存在し、`done/` にある。

- 利用者または開発への影響: エラーメッセージが実態と食い違うため、原因調査が「ファイルが消えた」という誤った方向へ向かう。本来伝えるべきは「`done/` にあるのに status が active（矛盾した状態）」であり、原因も対処も異なる。

## 対応方針

- 実施すること:
  - `ActiveMemoRow.memo` を `memo_path.name` ではなく `memo_path.relative_to(root)` のような**発見時の相対パス**で保持する。
  - `validate_rows()` の存在確認は `root / row.memo` のまま使えるようにする（相対パスなので `done/xxx.md` も正しく解決される）。
  - 併せて、「`done/` 配下に active status の memo がある」こと自体を別の診断として明示できると良い（任意）——現在は単に見つけて処理するだけで、「doneディレクトリなのにactiveなのは変では」という指摘が無い。

- 実施しないこと:
  - `done/` への配置規約そのものの変更（別issueの話）。

## 受入条件

- [ ] `issues/done/` 配下に active status の memo を一時的に置いても、`validate_rows()` が正しくファイルを発見し「missing memo file」を誤報しない
- [ ] 既存の `01_Plans/issues/tests/`（存在する場合）または新規テストで、上記シナリオを mutation として固定する
- [ ] `python 01_Plans/issues/validate_active_issue_memos.py` が既存の正常な状態で変わらず通ることを確認
