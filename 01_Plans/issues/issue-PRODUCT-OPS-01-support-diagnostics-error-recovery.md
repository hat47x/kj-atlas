# Issue Draft: PRODUCT-OPS-01 サポート・診断・復帰導線の製品化

- Type: Feature request
- Status: Open準備完了 (Ready for Open)
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/`, `03_Implement/backend/`, `04_Documentation/diagnostics.md`, `04_Documentation/operations.md`, `SUPPORT.md`
- Related Backlog: `PRODUCT-OPS-01`
- Related ADR/Spec: `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `02_Architecture/architecture.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-OPS-01
- RequirementStatement: 利用中のエラー、保存失敗、backend未接続、取り込み失敗、共有前警告に対して、利用者が次に取るべき行動と安全に共有できる診断情報を理解できる状態にする。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=保存失敗、API未接続、取り込み失敗、共有前警告のいずれかが発生する / 操作=画面のエラー表示と診断文書を確認する / 期待結果=再試行、保存、再読み込み、管理者への共有、共有してはいけない情報が分かる / 除外=24時間サポート体制やチケットシステム連携。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- 製品化後は、エラーが起きたときに利用者が自己判断で機密情報やAPIキーを共有してしまわないようにする必要がある。
- 現行の診断文書は整備されつつあるが、画面上のエラー表示、診断出力、サポート文書の関係が製品導線として固定されていない。
- backend未接続や取り込み失敗のような初期利用で起こりやすい失敗は、技術者向けメッセージだけでは一般利用者に伝わりにくい。

## 2) 背景 / Context

- `04_Documentation/diagnostics.md` は画面/API/保存の問題を切り分ける文書として改善済み。
- `SUPPORT.md` は問い合わせ窓口やサポート範囲を扱う。
- `ADR-0031` は低速環境や診断を製品化品質の一部として扱う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 問題発生時に作業を安全に中断・復帰できることは、継続利用の信頼に直結する。
- 安全（THREAT_MODEL / SafeMode）: 診断情報やサポート共有に機微情報を含めないガードが必要である。
- 企業・行政要件（enterprise_architecture）: 障害時の初動、ログの扱い、サポートへ共有する情報の範囲が必要になる。
- 後方互換（schemas）: エラー表示と診断導線の整理であり、データ契約は維持する。

## 3.1 Open化境界（Stream J）

- 本Issueは「失敗時の利用者復帰導線」と「安全な共有境界」の仕様定義を先行して Open 化する。
- 実装依存（画面実装・診断機能追加）は別PRで扱い、本Issueでは受入条件と検証手順の成立を完了条件とする。
- `PRODUCT-QA-01` からは G6 判定対象として参照されるが、相互ブロックは設定しない。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 保存失敗、API未接続、取り込み失敗、共有前警告の画面表示。
  - 診断結果のコピー/ダウンロード時のマスク方針。
  - `diagnostics.md`、`operations.md`、`SUPPORT.md` の問い合わせ前確認。
- 変更の最小単位:
  - 代表エラーごとに「何が起きたか」「次に試すこと」「共有してよい情報」を表示する。
  - 診断出力はSafeModeと同じ安全語彙で説明する。
- 非目標:
  - チケットシステム連携。
  - 自動ログ送信。
  - 高度な監視基盤の実装。

## 5) 受入条件 / Acceptance criteria

- [ ] backend未接続、保存失敗、取り込み失敗、共有前警告で、利用者向けの次アクションが表示される。
- [ ] 診断情報を共有するときに、APIキー、token、password、未加工の機微本文を含めない注意が画面または文書で分かる。
- [ ] SafeMode、share/export、import sanitizeの警告と診断文書の表現が矛盾しない。
- [ ] `SUPPORT.md` と `diagnostics.md` が、サポートへ共有する情報と共有しない情報を分けて説明している。
- [ ] 代表失敗ケースのunit/integrationまたは手動確認手順がある。

### 5.1 代表失敗ケース別の情報設計

| 失敗ケース | 利用者に伝えること | 次の操作 | 共有してよい情報 | 共有しない情報 |
| --- | --- | --- | --- | --- |
| backend未接続 | サーバーへ接続できず、一部機能が使えない | 再試行、起動状態確認、診断表示 | 時刻、画面名、エラー種別 | API key、token、内部URLの機微部分 |
| 保存失敗 | 変更が保存されていない可能性がある | 再試行、別名保存、現在の文書を保持 | エラー種別、保存先の種別 | 文書本文、ファイルパスの個人情報 |
| 取り込み失敗 | ファイル形式または検証で止まっている | 検証結果確認、別ファイル選択 | schemaVersion、検証エラー種別 | 未加工の取り込みファイル全文 |
| 共有前警告 | 共有前に確認すべき情報が残っている | マスク対象確認、共有範囲確認、キャンセル | 警告の種類、SafeMode状態 | 未マスク本文、個人名、機密メモ |
| 低速/処理中 | 処理が続いているか、再試行が必要かを判断する | 待つ、キャンセル、診断を開く | 処理名、経過時間、失敗有無 | 入力本文、認証情報 |

### 5.2 診断とサポート共有の境界

- 画面上のエラーは、原因推定よりも「今できること」を先に表示する。
- 詳細診断は折りたたみ、コピーやダウンロードの直前にマスク済みであることを明示する。
- サポートへ共有する情報は、発生日時、操作名、エラー種別、SafeMode状態、ブラウザ/環境情報の最小範囲にする。
- 共有しない情報は、API key、token、password、未加工本文、個人情報、組織内URLの機微部分として明記する。
- 自動ログ送信、診断パッケージ仕様、サポート基盤連携を固定する場合は、運用設計の変更としてADR化する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 代表失敗ケースを棚卸しする。
- [x] T2 画面上のエラー文言を利用者向けに分類する。
- [x] T3 診断出力とサポート共有時のマスク方針を確認する。
- [ ] T4 `diagnostics.md`、`operations.md`、`SUPPORT.md` を同期する。
- [ ] T5 代表失敗ケースの検証手順を追加する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "API key|token|password|未加工|機微|診断|保存失敗|取り込み失敗|backend" 03_Implement 04_Documentation SUPPORT.md`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run`
  - `git diff --check -- 03_Implement 04_Documentation SUPPORT.md`
- 期待結果:
  - 代表失敗ケースで利用者向けの復帰導線があり、診断情報の共有範囲が安全に説明される。
- 未実施時の理由・代替検証:
  - 自動失敗注入が未整備の場合は、手動手順と画面スクリーンショットで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: エラーメッセージを技術者向けのままにする。一般利用者が次の行動を判断できない。
- 代替案B: すべての診断ログを自動送信する。プライバシーと運用前提に合わないため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: エラー文言を簡略化しすぎて、開発者が原因を追えなくなる。
- 影響範囲: frontend error UI、diagnostics、support documentation。
- ロールバック手順: 利用者向け文言と詳細ログを分離し、詳細ログは開発者向け文書へ戻す。

## 10) Additional context

- ADR化が必要になる条件: 自動ログ送信、サポート基盤連携、診断パッケージ仕様を固定する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
