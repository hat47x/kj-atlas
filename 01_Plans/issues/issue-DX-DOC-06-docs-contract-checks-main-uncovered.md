# Issue: DX-DOC-06 docs_contract_checks.pyのmain()がテスト未カバー

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Testing
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/docs_contract_checks.py`
- Related ADR/Spec: `01_Plans/tests/`
- Expected verification level: `unit`

## 課題

- 現在の問題: `01_Plans/docs_contract_checks.py`の`main()`関数（CLIエントリポイント、L1030-1066）は13個の`check_*`関数を呼び出して束ねるが、この`main()`自体を直接呼び出すテストが存在しない（テストファイル内で`\bmain\b`にマッチするのは`unittest.main()`のみ）。対照的に、個々の`check_*`関数はそれぞれ2〜7件の直接テストを持つ。
- 単純な追加ではない理由: `main()`が呼び出す`check_document_contract_baseline`・`check_public_boundary`・`check_safety_routes`・`check_history_metadata`は、`schemas.md`・`api.md`・`data_model_operations_overview.md`など実リポジトリ内の固定相対パスを無条件に`(root / fixed_path).read_text(...)`で読む。既存の`check_*`単体テストはtmp_dir fixtureに必要最小限のファイルだけを用意して個別関数を直接呼ぶパターンだが、`main()`を同じ手法でテストしようとすると、13個すべてのcheckが要求するパス前提を同時に満たす完全なmulti-fileフィクスチャが必要になり、揃わない限り`FileNotFoundError`で落ちる。これは「ついでに」書けるテストではなく、フィクスチャ設計自体が相応の作業になる。
- 利用者または開発への影響: `main()`のwiring（どのcheckを呼ぶか、`findings`の集約、exit code分岐、出力フォーマット）に対する回帰保護が無い。個々の`check_*`関数自体は保護されているため、実害は「新しいcheckを追加/削除した際の呼び出し漏れ」のような配線ミスに限られる。

## 対応方針

- 実施すること: 以下のいずれかをMaintainerが選択する。
  1. 実リポジトリのルート自体をfixtureとして使う（実際の`02_Architecture/schemas.md`等を読む）end-to-endテストを`01_Plans/tests/`に追加する。
  2. 13個のcheckすべてが要求するパスを満たす最小限のsynthetic multi-fileフィクスチャを新規構築する。
  3. 費用対効果が低いと判断し、対応不要（Won't Fix）とする。
- 実施しないこと: フィクスチャ設計方針を決めずに場当たり的なテストを追加すること。

## 受入条件

- [ ] 上記3方針のいずれかが選択される。
- [ ] テストを追加する場合、`python3 -m pytest 01_Plans/tests/`が通過する。

## 検証計画

- 実行する確認: 対応後、`python3 01_Plans/docs_check.py`および該当テストスイート。
- 期待結果: 既存の13個の`check_*`単体テストに影響なく、新規テスト（追加する場合）が通過する。

## 補足

- 発見経緯: 第7ラウンドの棚卸しで、`docs_contract_checks.py`全体のテストカバレッジ構造を確認した際に発見。`main()`を直接テスト対象にできるかを検討したが、上記の固定パス依存により「機械的な追加」ではないと判断し、実装せず起票した。
