# E2E Testing

対象読者: kj-atlas の実装変更に対して Playwright E2E、回帰テスト、PR 前確認を行う開発者、QA、メンテナ。

目的: Docker Compose またはローカル起動環境で、開発者向け E2E を再現できるようにします。一般利用者向けの画面確認は [受け入れ確認](../../../04_Documentation/acceptance_check.md) を参照してください。

範囲外: 組織固有のテスト管理、非公開データを使った検証、CI 基盤の詳細設定、一般利用者向けの導入説明。

## 事前準備

標準構成を起動します。

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
curl -fsS http://localhost:8080/api/docs/doc_phase1_canvas
```

ローカル開発サーバーで確認する場合は [導入手順](../../../04_Documentation/installation.md) の「Docker を使わない最小起動」を使います。Vite の `/api` proxy は backend が起動していないと 500 を返すため、E2E 前に次の両方を確認します。frontend の port を変更した場合は `4173` を実際の port に置き換えてください。

```bash
curl -fsS http://127.0.0.1:8000/healthz
curl -fsS http://127.0.0.1:8000/docs/doc_phase1_canvas
curl -fsS http://127.0.0.1:4173/api/docs/doc_phase1_canvas
```

## 手動確認と自動テストの違い

| 種類 | 目的 | 使う場面 |
| --- | --- | --- |
| 手動 smoke test | 利用者の主要操作が実際にできるかを見る | 初回起動、画面変更、障害調査 |
| Playwright E2E | ブラウザ操作を自動で再現する | PR、リリース前、回帰確認 |
| unit/regression test | 小さなロジックやデータ変換を速く確認する | 実装変更後、原因切り分け |

一般利用者の確認では、まず [受け入れ確認](../../../04_Documentation/acceptance_check.md) の手動 smoke test だけで十分です。開発変更を含む場合は自動テストも実行します。

## 手動 smoke test

1. `http://localhost:8080` を開く。
2. 新規ドキュメントを作成する。
3. カードを追加する。
4. カードを移動する。
5. 島またはレビュー関連の表示が崩れていないことを確認する。
6. 保存し、ページを再読み込みする。
7. 変更が残っていることを確認する。
8. share/export を使う場合、[データ取り扱い](../../../04_Documentation/data_handling.md) のチェックリストに沿って、出力に秘密情報や内部メモが混ざっていないことを確認する。

表示設定や SafeMode の確認を含める場合は、`View` パネルを開きます。手動 smoke test では、視点プリセット、深さ、SafeMode、export legacy 導線が表示され、キャンバスが操作不能になっていないことを確認します。

![View パネルを開いた手動確認画面](../../../04_Documentation/assets/screenshots/view-controls-safe-mode.png)

## Playwright を実行する

frontend の依存関係を入れます。

```bash
cd 03_Implement/frontend
npm ci
```

`npm ci` は `package-lock.json` に固定された依存関係を入れるため、E2E の再現性を保ちやすい手順です。

E2E を実行します。

```bash
npm run e2e
```

画面を見ながら確認する場合:

```bash
npm run e2e:headed
```

特定の mock E2E だけ実行する場合:

```bash
npm run e2e:mock
```

## 単体・回帰テスト

E2E の前に軽量な回帰確認を行う場合:

```bash
cd 03_Implement/frontend
npm run typecheck
npm run test
npm run test:regression-guards
```

backend:

```bash
cd 03_Implement/backend
python -m pytest
```

## 確認観点

| 観点 | 期待 |
| --- | --- |
| 起動 | `/api/healthz` が成功する |
| 標準サンプル | `doc_phase1_canvas` が backend 直アクセスと frontend proxy の両方で成功する |
| 保存 | 作成・編集した内容が再読み込み後も残る |
| SafeMode | 未レビュー情報を AI が自動確定しない |
| LLM disabled | `KJ_ATLAS_LLM_PROVIDER=none` では AI 機能が disabled として扱われる |
| export | 秘密情報や共有不要な調査メモが混ざらない |
| 画面 | ヘッダー、ツールバー、主要ボタンが狭い幅でも重ならない |

## viewport の目安

画面崩れを確認するときは、少なくとも次の幅を見ます。

| 幅 | 目的 |
| --- | --- |
| 1280px | 標準的な desktop |
| 960px | 狭めの desktop / tablet |
| 390px | mobile 相当 |

すべての細部を確認する必要はありません。主要操作が見えるか、テキストが重ならないか、保存操作ができるかを優先します。

390px では、ヘッダーが複数行に折り返され、検索、表示モード、共有と再現、保存などの主要操作が画面外へ消えないことを確認します。

![390px viewport のヘッダー確認](../../../04_Documentation/assets/screenshots/mobile-toolbar-smoke-390.png)



## QA Monkey / E2E 境界（Stream E テスト資産限定）

本節は **テスト資産のみ** を変更対象にする境界定義です。`src/ui` / `src/canvas` など本番実装コードの機能変更は含めません。

### レイヤ分離（契約テスト / スモーク / E2E）

| レイヤ | 目的 | 変更対象 | 禁止事項 |
| --- | --- | --- | --- |
| 契約テスト (unit/integration) | API・ドメイン契約の不整合を早期検知 | `03_Implement/frontend/tests/**/*` fixture / test | UI機能追加・仕様変更 |
| スモーク (manual/lightweight) | 起動・主要導線・安全境界の即時確認 | 手動手順・記録テンプレート | 合否を翻訳品質だけで確定 |
| E2E (Playwright) | 実利用シナリオと境界回帰の自動再現 | Playwright spec / mock fixture / docs | 本番データ依存・不安定な外部依存 |

### QA Monkey 群の優先境界

1. SafeMode / share-export は fail-closed を維持する。
2. `KJ_ATLAS_LLM_PROVIDER=none` でも回帰検証が継続可能である。
3. `ja/en` のユーザージャーニー等価は E2E で機械判定し、翻訳品質は人間レビューに分離する。

### 再現性・flaky対策（必須）

- mock/fixture を優先し、外部依存を固定する。
- 同一 commit で `npm run test` → `npm run e2e:mock` を同順で実行し、差分再現を確認する。
- flaky が発生した場合の自己修復は最大3回（再実行、待機調整、fixture補正）まで。4回目相当は Stop として `Pending` に保留理由と再開条件を残す。


## Draft QA issue の Open化条件（AC/DoD/証拠）

`issue-QA-*` を Draft から Open に進める前に、次を満たします。

- AC-O1: E2Eで担保する価値境界と、unit/integrationで担保する契約境界を1行ずつ記載する。
- AC-O2: `Execution: Hold` の解除条件を1行で判定可能にする。
- AC-O3: 証跡セット（コマンド、結果、失敗分類、follow-up issue）を残す。
- AC-O4: 実行経路（Compose / SQLite / 例外記録）を事前選択する。

DoD
- DoD-O1: AC-O1〜O4が issue 本文に存在する。
- DoD-O2: `python3 01_Plans/issues/validate_active_issue_memos.py` を通過する。
- DoD-O3: No-Go時の戻し先 issue と再開条件が 1:1 対応する。

## 失敗時に残す情報

- 実行したコマンド
- 対象 URL
- ブラウザと viewport
- 失敗した操作
- API status code
- `docker compose logs api --tail=200`
- 可能ならスクリーンショット

ログやスクリーンショットを共有するときは、API key、token、password、未加工の顧客情報を含めません。どこまで残すか迷う場合は [データ取り扱い](../../../04_Documentation/data_handling.md) を参照してください。

## E2E 記録

検証結果を残すときは内部の検証記録テンプレートを使います。個人情報、秘密情報、内部承認履歴は記録しません。

## 関連文書

- [導入手順](../../../04_Documentation/installation.md)
- [受け入れ確認](../../../04_Documentation/acceptance_check.md)
- [運用手順](../../../04_Documentation/operations.md)
- [診断と障害調査](../../../04_Documentation/diagnostics.md)
- [データ取り扱い](../../../04_Documentation/data_handling.md)
- [セキュリティ](../../../04_Documentation/security.md)


## UI Operability（ADR-0030）E2E観点（計画）

実装着手前に、次の観点を E2E シナリオ化対象として固定します。

1. 開始: 初期表示で主要操作へ到達できる。
2. 選択: キーボードで選択対象へ到達し、選択結果を確認できる。
3. 表示: 文脈優先で必要情報が先に提示される。
4. 閉じる: `表示` / `共有と再現` を `Escape` で閉じられる。
5. 復帰: 閉じた後に起点フォーカスへ戻る。

### Mock-first I/F 契約（実装非依存）

- DOM 状態
  - `data-ui-region="primary-flow"` が初期表示で観測可能。
  - `data-panel="selection-context"` は選択後に可視化される。
  - `data-panel-group="advanced"` は初期 `aria-expanded="false"`。
  - 一時パネルは `data-panel="view"` / `data-panel="share-replay"` で識別可能。
- イベント契約
  - `PointerSelect|KeyboardSelect -> SelectionChanged` の同等性。
  - `SelectionChanged -> ContextPanelRequested -> ContextPanelRendered` の連鎖。
  - `Escape -> PanelDismissed(reason="escape") -> FocusReturned` の連鎖。

### 直列実装順（固定）

1. `UX-OPERABILITY-01`: 動線レビュー
2. `UX-OPERABILITY-02`: キーボード到達性
3. `UX-OPERABILITY-03`: 文脈優先パネル
4. `UX-OPERABILITY-04`: Escape 閉じる + フォーカス復帰

### フェイルセーフ

アクセシビリティ要件（フォーカス可視、読み上げ可能名、キーボード到達性）が曖昧な場合、該当 Issue は `Execution: Hold` とし、実装 PR へ進めない。

本節は計画記述であり、具体的なテスト実装は `UX-OPERABILITY-02`〜`04` の実装PRで追加する。

## Draft群 Open化向け QA Gate テンプレート（Stream E）

Draft状態の issue-QA-* を Open 判定可能にする時は、次の最小テンプレートをそのまま流用します。

### 1) Context / Decision / Consequences（QA gate）
- Context: Draft/Hold の理由を「依存・承認・実行経路」の3分類で明示する。
- Decision: `Prerequisite` / `Environment` / `Scope` の3ゲートを固定する。
- Consequences: Open可否を第三者が再判定できる状態にする。

### 2) Open化条件テンプレ
- `O-<ID>-01`: 必須依存（承認ID、上流参照）が `Pending` 欄に記録済み。
- `O-<ID>-02`: `ADR-0019` 準拠の実行経路（Compose / SQLite / 例外記録）が1つ事前選択済み。
- `O-<ID>-03`: `Execution: Hold` の解除条件が1行で判定可能。
- `O-<ID>-04`: blocker と再開条件が 1:1 対応。

### 3) Verify（実行可能性）
- docs-check: `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|Execution: Hold|Pending" <target issue>`
- metadata-check: `python3 01_Plans/issues/validate_active_issue_memos.py --files <target issue>`
- diff-check: `git diff --check -- <target issue>`

### 4) Proceed（3区分）
- Open化可能: O条件が全充足。
- 追加判断必要: O条件の一部充足（承認IDなどが未記入）。
- 保留継続: blocker未解消、または実行経路未固定。

### 5) 修復上限（失敗時）
- 自己修復は最大3回まで（再実行、記述補正、リンク補正）。
- 4回目相当は Stop とし、保留理由/再開条件を追記して終了する。


## Release Gate 連携（QA専任運用）

- E2E結果は `PRODUCT-QA-01` の Gate Record に `result/evidence/owner/due` 形式で転記します。
- Blocker または Critical を検出した場合は、E2E段で即時停止し `MVP-EXIT-01` 判定を Fail にします。
- Compose実行不可時は `ADR-0019` の代替経路（SQLiteまたはmock）を使用し、未実施理由を必ず記録します。
