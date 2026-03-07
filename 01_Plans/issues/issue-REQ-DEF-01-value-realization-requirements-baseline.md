# Issue Draft: REQ-DEF-01 価値実現に向けた要求ベースライン定義

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Product Owner + Platform Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0010`, `ADR-0011`, `ADR-0012`, `02_Architecture/architecture.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- 価値原則（ADR-0010）と要求マッピング（ADR-0011）は存在するが、直近の実行優先度で「どの要求を先に固定するか」の合意が不足している。
- Phaseごとの計画（ADR-0012）と実装入口（03_Implement）の間で、要求の凍結範囲が曖昧なため、Issue分解時にスコープドリフトが発生しやすい。
- 人間レビュー時に「価値に対して何が未定義か」を即時判断しづらい。

## 2) 背景 / Context

- AGENTSのRead Orderは上流優先（00→01→02→03）を要求している。
- 価値実現の中核要件（保留尊重、反スコアリング、レビュー追跡、safeMode既定ON）は固定済みだが、要求定義フェーズの壁打ち成果をIssueへ転写する型が不足している。
- `01_Plans/issues/README.md` の運用では、Acceptance/Validation先行固定が必須となっている。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 価値→要求→Issue の変換ロスを減らし、価値実現速度を上げる。
- 安全（THREAT_MODEL / SafeMode）: 要求定義時点で安全境界を固定し、後工程での例外導入を抑制する。
- 企業・行政要件（enterprise_architecture）: 責務分離と監査説明可能性を要求文脈で先に整理できる。
- 後方互換（schemas）: スキーマ変更の有無を要件段階で判定し、互換リスクを先出しできる。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（要求ベースライン定義）。
- 変更の最小単位:
  - T1: 価値原則と要求ID（UX/DATA/AI）の優先固定対象を定義する。
  - T2: 要求ごとの「責任分界点（人間/AI/システム）」を明示する。
  - T3: 要求未確定項目をDecision Queueへ移送する運用ルールを固定する。
- 非目標:
  - Frontend/Backend/Schema の実装変更。
  - 新規価値原則の追加。

## 5) 受入条件 / Acceptance criteria

- [ ] 価値原則P-01〜P-07に対して、優先固定対象要求（UX/DATA/AI）が明示される。
- [ ] 各要求に責任分界点（決定者/実装者/検証者）が紐づく。
- [ ] 未確定要求をDecision Queueへ送る判定条件（いつ止めるか）が定義される。
- [ ] SafeMode既定ONと漏えい防止を弱めないことが明文化される。
- [ ] docs-check の検証コマンドと期待結果が記録される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 価値原則ごとの要求優先度（Must/Should/Could）を策定する。
- [ ] T2: 要求ごとのRACI草案を作成する。
- [ ] T3: 未確定要求の停止基準とエスカレーション条件を策定する。
- [ ] T4: 固定済み要求を具体Issueへ分割する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "REQ-DEF-01|価値実現|責任分界点|Decision Queue" 01_Plans`
- 期待結果:
  - issue memo validator が成功し、要求ベースライン定義の記述が検索可能である。
- 未実施時の理由・代替検証:
  - Python未導入時は `rg` と目視レビューで代替し、理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既存ADRだけを参照し、要求ベースライン文書を追加しない。
  - 却下理由: 実行優先度と責任分界が曖昧なまま残る。
- 代替案B: 実装Issueを先に作り、要求定義を後追いする。
  - 却下理由: 上流未確定のまま下流着手となり、手戻りが増える。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 要求の粒度が粗すぎて、具体Issueに落とせない。
- 影響範囲: `01_Plans/` と関連するArchitecture文書の参照整合。
- ロールバック手順: 追加した要求優先度の分類を撤回し、既存ADR参照のみへ戻す。

## 10) Additional context

- 要件定義フェーズの壁打ち結果を、Issue化可能な粒度で固定するための起点Issue。
- ADR化が必要になる条件（トレードオフ閾値）:
  1. 要求優先度分類をプロジェクト恒久ルールへ昇格する場合。
  2. RACI定義を全Backlog共通ルールとして適用する場合。
