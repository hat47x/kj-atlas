# Issue: DOGFOOD-10 並行イテレーション（cron loop）のシナリオ追記が verify_all.sh の E2E 実走行と競合して誤検知する

- Type: Process / Bug
- Status: Done
- Source Issue: ドッグフーディングループ（`/loop` 10分間隔）の並行ファイアと CI ハーネスの実走行が競合して再現（2026-08-16、2回観測）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/verify_all.sh`（check 10）, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`, ループ運用（`/loop` のファイア間隔・single-flight化）
- Related ADR/Spec: `01_Plans/dogfood/README.md`（検証経路の追加規約）, `01_Plans/dogfood/DOGFOODING_MANIFEST.md`（検証ハーネス）, `issue-DOGFOOD-09`（同じ verify_all.sh の前提まわり）
- Expected verification level: `docs-check`

## 課題

`verify_all.sh` check 10 は、自己完結E2E（`verify_business_flow_e2e.sh` など）を**共有作業ツリー上のファイルを直接実行**する。一方、ドッグフーディングの `/loop`（10分間隔の cron ファイア）がシナリオ拡大イテレーションとして**同一ファイルへシナリオを追記**する。両者が並行すると、実行中の bash が読み込み中のスクリプトをファイアが書き換え、E2E が**コードの欠陥ではなく環境競合で誤検知**する。

実地で2回再現した（2026-08-16）:

```text
# 再現1（シナリオ66追記と競合）: verify_all.sh check 10 の business-flow が 365/16
# 再現2（シナリオ67追記と競合）: verify_all.sh check 10 の business-flow が 3件失敗
    FAIL: AG ③矛盾検出
    FAIL: AG ④ナラティブ
    FAIL: AG 読戻し (200) (expected 200, got 000)   # backend 到達不能
```

いずれも**同じシナリオ群をツリーが安定しているときに単独実行した場合は pass**（375/375・381/381）。つまりコード回帰ではなく、ハーネス実行中にファイルが書き換えられる競合起因。

### なぜ問題か

- **CI/検証結果の信頼性を損なう**: 開発者が `verify_all.sh` を実行したタイミングとファイアの追記が重なると、関係のない FAIL を目撃する。実欠陥との切り分けに時間を奪う。
- **DOGFOOD-06（検証は異常系も assert する）の精神と矛盾**: 検証ハーネス自身が「実行中に入力が変わらない」前提を assert していない。
- **再現条件が時間依存**: ファイア間隔（10分）とハーネス実行時間（数分）が同程度のため、偶然の競合が頻発しうる。

## 三要素分析（ADR-0067）

- **機能設計（検証機能）**: check 10 は「ファイルを読んで実行する」方式で、実行開始後にファイルが変わることを想定していない。検証の入力（E2Eスクリプト）の不変性を確保する機構がない。
- **データ設計**: シナリオ定義（`verify_business_flow_e2e.sh`）は「検証入力」であると同時に「イテレーションの成果物」でもあり、並行書き込みが発生しうる共有リソース。実行時スナップショット（temp copy）か、書き込み側の serialization が必要。
- **業務設計**: ループの運用目標（段階的カバー拡大）と CI の運用目標（決定性の高い検証）が、同一共有ファイルへの並行アクセスで衝突する。どちらか一方を譲る必要がある。

## 対応方針（候補）

- **案A（入力のスナップショット化・最小）**: `verify_all.sh` check 10 が各E2Eスクリプトを temp へコピーしてから実行する（`bash "$(mktemp)"` 相当）。追記が進行中のファイルを実行しなくなる。検証は「追記完了時点」のスナップショットを検証する。
- **案B（書き込み側の serialization）**: ループファイアを single-flight 化する（前回ファイアが未完了なら skip、または interval を 20m/30m へ延長して競合窓を縮小）。
- **案C（検出＋再試行）**: check 10 実行前に `verify_business_flow_e2e.sh` の mtime を記録し、実行後に変化していたら「環境競合」として SKIP/再試行を報告する（`DOGFOOD-09` の migration 前提チェックと同じ発想）。

採否は案A（検証側の自己防衛）を最優先候補とし、案Bはループ運用のパラメータ調整として併用を検討する。

## 対応（2026-08-16）: 案A（実行時スナップショット化）を採択

`verify_all.sh` check 10 を、各E2Eスクリプトを**同じディレクトリの一時スナップショット**（`.e2e_snapshot_$$_<basename>`）へコピーしてから実行する方式へ変更した（`run_e2e_snapshot` ヘルパー）。同一ディレクトリに置くことで、各スクリプトの `BASH_SOURCE` 由来パス（`SCRIPT_DIR` / `ROOT_DIR` / `examples/admin_lifecycle.py`）が単独実行と同一に解決される。実行後はスナップショットを削除する。

- 対象: `verify_business_flow_e2e.sh`・`verify_admin_ops_flow_e2e.sh`・`verify_kj_multi_round.sh`（check 10 の3本）
- 検証: `verify_all.sh` フル実走行で **All checks passed**（business-flow・admin・kj multi-round・MCP CE-4 audit の4本すべて PASS）。admin E2E はスナップショット経由でも `examples/admin_lifecycle.py` のパス解決が正しく 12/12。
- 補足: 並行ファイアのポート重複（8005-8007）による競合は、ファイアが REPL アイドル時のみ起動する運用（案B）に依存するため、本Issueでは案Aのみ採択。競合が再発する場合は案B（interval延長・single-flight）を適用する。

## Traceability

- `01_Plans/dogfood/DOGFOODING_MANIFEST.md` §2.2 — check 10 の配線対象（本課題の競合対象）
- `03_Implement/backend/verify_all.sh` — check 10（E2Eスクリプト直接実行）
- `01_Plans/dogfood/README.md` — イテレーション履歴（シナリオ62〜67 を並行ファイアが追加）


## 配置の整理（2026-09-05）

- 本Issue群は、並行開発・並行ドッグフーディングによって検証入力や期待値が実行中／変更後の実装とずれ、実回帰ではない失敗を生む verification drift を解消した完了系列として `Done` となっていた。
- `DOGFOOD-10` は E2E スクリプトを実行時スナップショットへコピーしてから走らせることで、`/loop` の並行追記と共有作業ツリー実行のraceを遮断した。
- `DOGFOOD-24` は model governance の allowlist 強化後に古いE2E期待値・テストfixtureが残ったdriftを、登録済み活性モデルを用いるシナリオとprovider設定fixtureへ追随させて解消した。
- いずれも並行編集そのものを禁止するのではなく、検証ハーネスと期待値を現在の実装契約へ整合させることで、検証結果の信頼性を回復した記録である。
- `LEGACY_DONE_AT_ROOT_BASELINE` は10から8へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
