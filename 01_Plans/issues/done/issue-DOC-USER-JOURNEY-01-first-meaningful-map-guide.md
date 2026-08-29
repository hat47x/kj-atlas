# Issue: DOC-USER-JOURNEY-01 初回利用者向け「最初の意味ある配置」ガイド

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Documentation contributor
- Scope: `README.md`, `04_Documentation/getting_started.md`（新規）, `04_Documentation/public_index.md`, `04_Documentation/installation.md`, `04_Documentation/acceptance_check.md`, `04_Documentation/README.md`
- Related Backlog: `PRODUCT-VALUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `01_Plans/issues/done/issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md`, `01_Plans/issues/done/issue-UX-EMPTY-01-empty-canvas-core-loop-onboarding.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DOC-USER-JOURNEY-01
- RequirementStatement: 初回利用者が、起動方法の理解だけで止まらず、AI無効・SafeMode ON の安全な既定構成で「標準サンプルのカードを確認する、まとまりを作る、未確定を残す、保存し、共有前確認まで進む」という最初の価値到達を公開文書だけで再現できるようにする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=初回利用者がアプリを起動済み、`KJ_ATLAS_LLM_PROVIDER=none`、SafeMode ON / 操作=秘密情報を含まない標準サンプルの3カードを確認し、まとまりと保留点を作り、保存・再読込・共有前確認を行う / 期待結果=何を配置し、何をまだ決めておらず、外部共有はまだ行っていないかを説明できる / 除外=AI提案、自動分類、外部共有の実行、クラウド同期。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure

## 1) 課題 / Problem statement

公開入口は「まず試す」と案内しているが、実体は導入・設定・運用・受け入れ確認への文書索引である。起動後に何をすれば kj-atlas の価値へ到達したと言えるかを、利用者の目的に沿って案内する一本道がない。

- `04_Documentation/public_index.md` の「まず試す」は文書一覧で、作業シナリオではない。
- `04_Documentation/installation.md` は起動後の疎通確認で終わる。
- `04_Documentation/acceptance_check.md` は右クリック、削除、レスポンシブ、処理中表示まで含む QA smoke test であり、初回学習の教程ではない。
- `PRODUCT-VALUE-01` は、カード3件以上、まとまりまたは保留点1件以上、保存または共有前確認を最初の価値状態として既に定義しているが、公開教程へ翻訳されていない。

この欠落により、初回評価者、非開発者のファシリテーター、組織内導入担当者は「起動できたが、次に何をすれば成功か」を判断できない。

## 2) 背景 / Context

- `ADR-0032` の V0/V1 は、初回利用者が最初の意味ある配置へ到達することを要求する。
- `PRODUCT-VALUE-01` の E2E と固定 fixture は操作可能性を検証しているが、利用者向け説明ではない。
- `UX-EMPTY-01` はアプリ内の消えるヒントを担当し、常設チュートリアルを非目標にしている。本Issueは公開文書だけを担当し、UIを再設計しない。
- `ADR-0039` に従い、重量級KPIや新規ガバナンスを導入せず、1本の実行可能な教程に限定する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 保留・違和感・可逆性は、機能名ではなく利用者が経験できて初めて価値になる。
- 安全（THREAT_MODEL / SafeMode）: 初回教程を `provider=none`、SafeMode ON、外部共有なしで固定し、安全な習慣を最初に形成する。
- 企業・行政要件（enterprise_architecture）: 非開発者の評価・導入説明を再現可能にし、担当者個人の口頭説明へ依存しない。
- 後方互換（schemas）: 文書追加のみ。データ契約・UI・保存形式は変更しない。

## 4) 提案する解決策 / Proposed solution

`04_Documentation/getting_started.md` を新設し、次の固定題材を使う7〜10手順の一本道を作る。

標準サンプルの固定題材（秘密情報を含まない）:

1. 「ユーザー課題を集める」
2. 「観察メモをカード化する」
3. 「似ている内容を近くに置く」

到達順:

1. 安全な既定値を確認する。
2. 標準サンプルを開く。
3. 上記3カードを確認する。
4. 2カードを最初の島へまとめる。
5. 残る1カードを保留または未決として残す。
6. 必要なら配置変更を1回取り消し、可逆性を確認する。
7. 保存して再読込する。
8. 「共有と再現」を開き、共有前確認だけを行って閉じる。
9. 完了状態を読み返す。

各手順には、`目的 / 現行UIラベル / 期待する画面状態 / 取消・安全な停止方法` を必ず記載する。手順本文は QA の網羅確認にせず、利用者の価値到達に必要な操作だけに絞る。

非目標:

- アプリ内ツアー、モーダル、オンボーディングUIの追加。
- AI提案、外部LLM、外部サービスとの共有を教程の必須経路にすること。
- すべてのUI機能を説明すること。
- `acceptance_check.md` を教程へ転用すること。

## 5) 受入条件 / Acceptance criteria

- [x] `getting_started.md` が Audience / Goal / Non-goal / Outcome を明示し、QG-1〜QG-6を満たす。
- [x] `provider=none`、SafeMode ON、秘密情報を含まない固定題材で開始する。
- [x] 7〜10手順以内で、カード3件、まとまり1件、保留または未決1件、保存・再読込、共有前確認へ到達する。
- [x] 各手順に目的、現行UIラベル、期待状態、取消または安全な停止方法がある。
- [x] 完了時に「配置した内容」「未確定の内容」「外部共有していないこと」を利用者が確認できる。
- [x] 保存失敗時は、現行実装で確認済みの退避方法または `diagnostics.md` / `SUPPORT.md` への安全な導線がある。
- [x] `README.md`、`public_index.md` の「まず試す」、`installation.md` の起動後導線から教程へ到達できる。
- [x] `acceptance_check.md` は smoke test、教程は学習経路であることを相互リンク付きで明記する。
- [x] SafeMode、未レビュー、share/export の説明が `data_handling.md` と矛盾しない。
- [x] UI実装、schema、SafeMode既定値を変更していない。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 現行UIラベルと固定題材の操作可否を、既存 first-meaningful-map E2E と画面で照合する。
- [x] T2 `getting_started.md` を上記固定構造で作成する。
- [x] T3 必要最小限の既存スクリーンショットを再利用し、代替テキストを付ける。新規撮影が必要なら秘密情報を含まない fixture を使う。
- [x] T4 `README.md` / `public_index.md` / `installation.md` / `acceptance_check.md` / `04_Documentation/README.md` の導線と公開対象表を同期する。
- [x] T5 手順未読のレビュー担当者が文面だけで再現し、迷った箇所を修正する。
- [x] T6 公開品質・リンク・用語・安全境界を検証する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "getting_started|最初の意味ある配置|SafeMode|provider=none|保存|共有前" README.md 04_Documentation`
  - `rg -n "Audience|Goal|Non-goal|Outcome|Related" 04_Documentation/getting_started.md`
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 目視確認:
  - 現行 `main` で手順を最初から最後まで1回実行する。
  - 外部共有、AI呼び出し、秘密情報入力が発生しないことを確認する。
- 期待結果:
  - すべての入口から教程へ到達でき、教程単体で価値到達と安全な停止が再現できる。
- 未実施時の理由・代替検証:
  - ブラウザ確認不能時は既存 first-meaningful-map E2E と UI catalog を照合し、未実施理由と再開条件を記録する。公開 Go には実機1回を必須とする。

## 8) 代替案 / Alternatives considered

- `acceptance_check.md` へ追記する: 学習とQAの責務がさらに混ざるため不採用。
- `public_index.md` だけに全手順を書く: 入口が長大化し、目的別索引としての役割を失うため不採用。
- アプリ内ツアーを実装する: docs-onlyで解ける欠落にUI複雑性を追加するため本Issueでは不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: UIラベル変更で教程が陳腐化する、または教程が機能カタログ化する。
- 影響範囲: 初回利用者の理解、安全な共有習慣、公開文書の保守コスト。
- ロールバック手順: 新規教程への入口を一時的に外し、公開前状態へ戻す。誤った手順を残したまま公開しない。
- 再発防止: `DX-DOC-02` の文書品質ゲートでリンク・公開境界・鮮度メタを検査する。

## 10) Additional context

- 本件は新しい価値要件ではなく、`PRODUCT-VALUE-01` の確定済み価値状態を公開教程へ翻訳する実行Issueである。
- ADR化が必要になる条件: 「最初の意味ある配置」の定義変更、LLM必須化、SafeMode既定変更、外部共有の自動実行を求める場合。

## 実装記録 2026-07-11

- `04_Documentation/getting_started.md` を追加し、現行UI/E2Eで固定された9手順、安全な停止、保存失敗時の退避、教程とsmoke testの境界を記載した。
- README、公開入口、導入、受け入れ確認、04管理indexを同期した。
- 相対リンク/画像、公開境界、Markdown体裁を機械確認し、入口・SafeMode画像を目視確認した。
- 2026-07-15、手順未読の利用者としてSQLite代替構成（`KJ_ATLAS_LLM_PROVIDER=none`、SafeMode ON）を起動し、標準サンプルから島作成、未決設定、保存、再読込、共有前チェックまで実機dry-runした。外部共有、書き出し、AI呼び出し、秘密情報入力は行っていない。
- dry-runで、島作成後は島が主対象として残るためカードの`保留状態`へ直行できないことと、再読込後に`サンプルを開く`を選び直すと組み込みサンプルの初期状態へ戻ることを確認した。手順5へEscによる選択解除を追加し、手順8を「読込完了を待って開始パネルを閉じる」経路へ修正した。
- 標準サンプルの固定題材とIssue内の提案文言を同期し、T5を完了したためDoneとする。
