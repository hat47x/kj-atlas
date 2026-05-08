# Minimal Context Triage for ADR / issue execution

この手順は、**計画実行前に全ADR/issueを全文再読せず**、未処理の対象だけを最小コンテキストで抽出するための運用手順である。

## 1. 目的

- コンテキストウィンドウ消費を、`Active issue` とその参照ADRに限定する。
- `Draft/Open/In Progress` の issue と、それに紐づく ADR だけを処理候補として抽出する。
- 依存未解決の `Draft` / `Open` を先に弾き、今すぐ着手できる対象だけを優先表示する。

## 2. 判定原則（機械判定）

### 2.1 issue を「未処理」とみなす条件（Active母集団）

次のいずれかに当てはまる issue memo を処理候補とする。

- `Status: Draft`
- `Status: Open`
- `Status: In Progress`

次は**処理候補から除外**する。

- `Status: Done*`
- `Status: Blocked*`
- 過去運用の `Ready*` / `Active*` は履歴として扱い、新規着手対象に混ぜない

### 2.2 ADR を「未処理」とみなす条件（Active issue逆引き）

ADR 自体の `Status` だけでなく、**紐づく issue がまだ Active か**で判定する。

- `Source Issue` が `Draft/Open/In Progress` の issue を指している ADR
- もしくは `Traceability` / `Related` で参照している issue が Active な ADR

つまり、ADR が `Accepted` でも、下流 issue が Active なら「処理中ADR」として扱う。

### 2.3 Ready/Blocked の機械判定

`triage_actionable_plans.py` は Active issue を次の規則で分類する。

- `classification=Ready`:
  - `Status ∈ {Open, In Progress}`
  - 依存 issue がすべて `Done`
- `classification=Blocked`:
  - `Status=Draft`（draft gate）
  - 依存 issue に `Done` 以外がある（blockers へ列挙）

### 2.4 依存解放順（dependency_stage）

依存解放順は `dependency_stage` で表す。値が小さいほど先に着手可能。

- `0`: 依存なし（起点）
- `1..n`: 依存を1段以上もつ
- `999`: 循環依存または解析不能（停止対象）

ソート順は **Ready優先 → dependency_stage昇順 → Priority(P0..P3) → path** の固定順とする。

### 2.5 mock適用可否（mock_applicable）

issue memo 先頭メタ（先頭180行）から `Mock適用可否` / `Mock Policy` / `Mock方針` / `Mock readiness` を読み取り、次を判定する。

- `Yes`: `yes/可/可能/applicable/enabled` を含む
- `No`: `no/不可/not applicable/disabled` を含む
- `Conditional`: 上記いずれにも明確一致しないが記述あり
- `Unknown`: メタ記載なし

`Unknown` は自動停止条件ではない。Stopper は次節 `errors` を優先する。

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
4. `## Triage errors (stopper)`

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

## 7. 停止条件（Stopper）

`triage_actionable_plans.py` は `errors` を出力し、**終了コード2で停止**する。
`errors` が1件でもある場合、推測実行は禁止。

- `missing Status metadata`
- `missing Priority metadata`

次の場合はツール出力を鵜呑みにせず停止する。

- issue の `Status` が README のライフサイクル定義と一致しない
- 依存関係が本文中に書かれていない
- `Source Issue` や `Related ADR/Spec` の表記揺れで逆引きできない
- `Ready issues` が0件なのに、実際には着手中タスクが存在する

その場合は先に memo メタデータを修正し、`validate_active_issue_memos.py` を通してから再実行する。


## 8. Stream E triage snapshot（2026-05-04）

### 8.1 Phase 1 Read（Active/Draft/Open 依存再整理）

- Active/Draft/Open: 15件（Ready 10 / Hold 5）。
- blocker 明示が必要なDraft: `CE2-low-risk-ai-assist`, `HIL-RS-02-A3-operations-documentation-sync`, `DOC-OPS-05-05/06/07`。
- 主要依存軸（再整理）:
  - `FB-P2C-01-a1-interface-contract` → `CE1-context-query-bundle-foundation` → `CE4-api-cli-audit-integration`
  - `CE0-contract-freeze` → `CE1-context-query-bundle-foundation` → `CE2-low-risk-ai-assist`
  - `HIL-RS-02-A1-governance-contract-hardening` → `HIL-RS-02-A3-operations-documentation-sync`

### 8.2 Phase 2 Priority（P0/P1/P2 再評価）

- **P0**: 変更なし。A1契約凍結系（`FB-P0-2A2B2C`, `FB-P2C-01`）は全下流の解放ゲート。
- **P1**: `CE1` は維持（理由: CE2/CE4の共通依存で、mock-first の分離実行を最も促進）。`HIL-RS-02-A3` は Draft/P1維持（理由: A1未完了のためOpen不可）。
- **P2**: DOC-OPS 3件は維持（理由: `DOC-OPS-05` gate 未確定のため先行着手不能）。

### 8.3 Phase 3 Dependency Cut（mock化可能依存）

- CE1は `ContextQueryV1/ContextBundleV1` を mock 契約として先行固定し、実装依存を切断可能。
- A3は `mock I/F preparation only` を維持し、A1完了前でも用語同期・導線同期のみ独立実行可能。
- CE2は CE1契約確定までは `proposal-only` 文書整備に限定（実装依存切断）。

### 8.4 Phase 4 Verify（整合チェック）

- 実行コマンド:
  - `python 01_Plans/triage_actionable_plans.py`
  - `python 01_Plans/triage_actionable_plans.py --format json`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 判定: `Dependency meta` 追加後も issue memo validator は通過。

### 8.5 Phase 5 Proceed（レーン投入順序）

1. `FB-P2C-01-a1-interface-contract`（P0 ゲート固定）
2. `CE1-context-query-bundle-foundation`（P1 / CE2+CE4の共通依存）
3. `CE4-api-cli-audit-integration`（P2だが CE1確定後は独立実行可）
4. `CE2-low-risk-ai-assist`（Draft→Open判定、CE1契約確認後）
5. `HIL-RS-02-A3-operations-documentation-sync`（A1完了後にOpen昇格）
6. `DOC-OPS-05-05/06/07`（DOC-OPS-05 gate確定後に順次）

停止条件: 依存の人間承認状態が未記録で推測が必要な場合は `Hold` で停止し、承認ログ入力を要求する。
