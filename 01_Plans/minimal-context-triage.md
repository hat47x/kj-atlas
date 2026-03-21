# Minimal Context Triage for ADR / issue execution

この手順は、**計画実行前に全ADR/issueを全文再読せず**、未処理の対象だけを最小コンテキストで抽出するための運用手順である。

## 1. 目的

- コンテキストウィンドウ消費を、`Active issue` とその参照ADRに限定する。
- `Draft/Open/In Progress` の issue と、それに紐づく ADR だけを処理候補として抽出する。
- 依存未解決の `Draft` / `Open` を先に弾き、今すぐ着手できる対象だけを優先表示する。

## 2. 判定原則

### 2.1 issue を「未処理」とみなす条件

次のいずれかに当てはまる issue memo を処理候補とする。

- `Status: Draft`
- `Status: Open`
- `Status: In Progress`

次は**処理候補から除外**する。

- `Status: Done*`
- `Status: Blocked*`
- 過去運用の `Ready*` / `Active*` は履歴として扱い、新規着手対象に混ぜない

### 2.2 ADR を「未処理」とみなす条件

ADR 自体の `Status` だけでなく、**紐づく issue がまだ Active か**で判定する。

- `Source Issue` が `Draft/Open/In Progress` の issue を指している ADR
- もしくは `Traceability` / `Related` で参照している issue が Active な ADR

つまり、ADR が `Accepted` でも、下流 issue が Active なら「処理中ADR」として扱う。

## 3. 最小読取フロー

### Step 1. まず一覧だけで絞る

最初に次のコマンドだけを実行する。

```bash
python 01_Plans/triage_actionable_plans.py
```

この出力で確認するのは次の3点だけ。

1. `## Ready issues`
2. `## Parked or blocked issues`
3. `## ADRs linked to active work`

### Step 2. Ready issue だけ読む

`Ready issues` に出た memo だけを開く。

- まず先頭メタ (`Status / Priority / Owner / Scope / Related ADR/Spec`) を読む
- 次に `受入条件` / `検証方法` / `依存関係` だけ読む
- 実装や文書変更に入る前に、関連 ADR を**その issue が参照するものだけ**読む

### Step 3. blocked を後回しにする

`Parked or blocked issues` に出たものは、次のどちらかに分類する。

- `blockers=...` がある: 依存先が Done になるまで保留
- `draft gate`: 依存はないが、まだ Open 化条件を満たしていないため保留

### Step 4. ADR は issue から逆引きする

ADR を先に全件読むのではなく、`ADRs linked to active work` に出たものだけ読む。

読む順序は次で固定する。

1. `Source Issue` に直結する ADR
2. Ready issue が `Related ADR/Spec` で参照する ADR
3. 依存解消に必要な上位 ADR

## 4. JSON 出力を使う場面

複数候補を自動整形したい場合だけ JSON を使う。

```bash
python 01_Plans/triage_actionable_plans.py --format json
```

用途例:

- 自分用の着手順メモ作成
- PR本文の「着手対象」「保留対象」整理
- 次の自動化ツールへの受け渡し

## 5. 推奨運用

1. `triage_actionable_plans.py` を実行する。
2. `ready=true` の issue だけを処理対象にする。
3. その issue が参照する ADR だけを読む。
4. 実作業後は既存の整合検査を実行する。

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
python -m unittest 01_Plans/tests/test_triage_actionable_plans.py
```

## 6. なぜ Python ツール化したか

このリポジトリでは issue / ADR が増えており、`rg` だけでも毎回全文に近い再確認が発生しやすい。
そのため、**先頭メタデータと依存行だけを読む薄いスキャナ** を Python で用意し、次を自動化した。

- Active issue の抽出
- 依存未解決 issue の切り分け
- Active issue に紐づく ADR の逆引き
- Ready / Parked の二値化

これにより、計画実行前の人間/AIの読取対象を「全件」から「Ready issue + 関連ADR」に圧縮できる。

## 7. 停止条件

次の場合はツール出力を鵜呑みにせず停止する。

- issue の `Status` が README のライフサイクル定義と一致しない
- 依存関係が本文中に書かれていない
- `Source Issue` や `Related ADR/Spec` の表記揺れで逆引きできない
- `Ready issues` が0件なのに、実際には着手中タスクが存在する

その場合は先に memo メタデータを修正し、`validate_active_issue_memos.py` を通してから再実行する。
