# Issue Draft: REQ-DEF-02 責任分界点と契約チェックポイントの要求定義

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner + Security Officer
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0011`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`, `02_Architecture/enterprise_architecture.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- 要件定義フェーズで「誰がどこまで決めるか（責務境界）」が明示されないと、実装Issueで設計判断が再燃する。
- Architecture文書とOperations文書で責任分界の言い回しがずれると、受入判定責任が曖昧になる。
- 契約正本（schema/API/policy）と運用手順の境界が曖昧なままだと、後方互換判断が遅れる。

## 2) 背景 / Context

- AGENTS.md は上流整合（00〜02）を実装着手条件としている。
- `schemas.md` は互換性判断の単一正本であり、要件段階で変更有無を宣言する必要がある。
- `enterprise_architecture.md` は組織要件（役割分離/監査）の根拠であり、責任分界点の要求定義に必須。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Human-in-the-loop の成立には責任分界の可視化が前提。
- 安全（THREAT_MODEL / SafeMode）: 責務不明確は例外運用の拡大を招き、安全境界が緩む。
- 企業・行政要件（enterprise_architecture）: 監査説明責任を満たすため、決定権限を明文化する必要がある。
- 後方互換（schemas）: 契約変更の判定ゲートを要求定義で先に固定できる。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（責任分界点要求・契約チェックポイント定義）。
- 変更の最小単位:
  - T1: 役割別責務（Product/Architecture/Security/Implementer/Reviewer）を要求文脈で定義。
  - T2: 契約チェックポイント（Schema/API/SafeMode/Export）を要求テンプレに追加。
  - T3: 「要件確定前に実装へ進まない」停止条件を明文化。
- 非目標:
  - 認可ロジックやAPI仕様の変更。
  - CI設定や運用ツールの導入。

## 5) 受入条件 / Acceptance criteria

- [ ] 役割ごとの決定責務と承認責務が要求文書で判読可能になる。
- [ ] 契約チェックポイント（schema/API/policy/ops）が要求定義テンプレに追加される。
- [ ] 各要求に「契約変更あり/なし」の判定欄がある。
- [ ] SafeMode・漏えい防止・監査要件の境界が必須項目として保持される。
- [ ] docs-check でメタ情報と参照整合を確認できる。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 責任分界点のRACI表（要求定義向け）を作成する。
- [ ] T2: 契約チェックポイントの定義表を作成する。
- [ ] T3: 要件未確定時の停止基準（Go/No-Go）を作成する。
- [ ] T4: 後続Issueテンプレへ責任分界点項目を反映する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "REQ-DEF-02|責任分界|契約チェックポイント|Go/No-Go" 01_Plans 02_Architecture 04_Documentation`
- 期待結果:
  - issue memo validator が成功し、責任分界点の要求が文書上で追跡できる。
- 未実施時の理由・代替検証:
  - Python未導入時は `rg` による存在確認で代替し、未実施理由を残す。

## 8) 代替案 / Alternatives considered

- 代替案A: 実装担当者の裁量で責任分界を都度決める。
  - 却下理由: 監査説明責任と再現性が確保できない。
- 代替案B: Architecture更新のみを先行し、Issueテンプレ更新を行わない。
  - 却下理由: 実務の起票時に責任分界点が抜け落ちる。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 責任分界点が細かすぎて運用負荷を上げる。
- 影響範囲: 要求定義作業、レビュー会運営、文書同期作業。
- ロールバック手順: 必須項目を最小セット（決定責務/承認責務/契約変更判定）へ縮退する。

## 10) Additional context

- 実装前に責任分界点を固定することで、後工程の論点再燃を抑制する。
- ADR化が必要になる条件（トレードオフ閾値）:
  1. RACIを全フェーズ必須ルールとして固定する場合。
  2. 契約チェックポイントをCIゲートへ接続する場合。
