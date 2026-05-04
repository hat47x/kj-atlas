# Issue Draft: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/tests`, `04_Documentation/e2e_testing.md`
- Related Backlog: `QA-E2E-USE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-E2E-USE-01
- RequirementStatement: 現在のE2E検証を、実運用に近いユーザージャーニー（作成→編集→レビュー→安全共有）で再現できるシナリオ群へ拡張し、回帰検知力を向上させる。
- PriorityClass: Must
- AcceptanceScenario:
  - 前提: seedデータまたはfixtureから起動し、safeMode既定ONの状態でテスト開始できる。
  - 操作: カード作成/配置、差分確認、review attribution更新、share/export判定を1フローで実行する。
  - 期待結果: 主要導線が安定して完走し、安全境界（safeMode・share/export制御）に回帰がない。
  - 除外: SSO本番連携、外部LLMプロバイダ実通信、長時間負荷試験。
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export / import-sanitize
- VerificationLevel: e2e
- DecisionStatus: Pending
- DecisionQueueRef: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`

## 1) 課題 / Problem statement

- 現行E2Eがスモーク中心で、実務に近い複合操作（作業継続・再編集・安全共有）を十分に検証できていない。
- UI/ドメインの境界変更時に、個別機能は通るが利用者フロー全体で破綻するリスクが残る。
- safeModeやreview attributionのような統治系要件の回帰が、単発シナリオでは検知しづらい。

## 2) 背景 / Context

- E2E方針の正本は `ADR-0019` と `04_Documentation/e2e_testing.md`。
- 既存IssueでもE2E境界（I18N/認証/UI同等性）は扱われているが、日常利用の縦断シナリオを統合した回帰セットは未整備。
- 仕様上、safeMode既定ONとshare/export漏えい防止は最優先であり、実利用シナリオで常時検証すべき。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 利用者価値（安心して反復編集できる）と品質価値（回帰早期検知）に直結。
- 安全（THREAT_MODEL / SafeMode）: 共有経路の誤開放を事前に検知するゲートとして有効。
- 企業・行政要件（enterprise_architecture）: 監査可能な再現フローを準備することで導入時の説明責任を補強。
- 後方互換（schemas）: UI/ワーカー/エクスポート境界の破壊的変更を早期発見し、互換維持に寄与。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Frontend tests + E2E運用ドキュメント（必要最小限）。
- 変更の最小単位:
  1. 実利用ジャーニー候補を3〜5本に定義（通常編集/レビュー重視/安全共有重視）。
  2. 既存Playwright基盤へ段階導入（まず1本を安定化、次に並列追加）。
  3. flaky要因を切り分け、fixture・待機戦略・assert粒度を標準化。
- 非目標:
  - 全機能の網羅テスト化
  - パフォーマンス/負荷試験
  - 本Issue内での認証基盤刷新

## 5) 受入条件 / Acceptance criteria

- [ ] 実利用を想定した主要ジャーニー定義（前提/操作/期待結果/除外）が3本以上文書化される。
- [ ] 少なくとも1本は「作成→再配置→レビュー反映→安全共有判定」を通しで自動実行できる。
- [ ] safeMode既定ONとshare/export制御に関する回帰アサーションが含まれる。
- [ ] CIで再実行可能なコマンドと失敗時の切り分け手順が明示される。
- [ ] 必要な検証（unit/integration/e2e/docs-check）が `Expected verification level` と一致する。
- [ ] `GoNoGoGate` の要否（Required/Optional/N/A）が明示され、Required時は判定基準が本文に記載される。
- [ ] セキュリティ境界に影響するIssueでは `SecurityGateImpact` を明示し、レビューゲート項目を記載する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 現行E2Eシナリオ棚卸しと、実利用ジャーニー候補のマッピング。
- [ ] T2: 優先1シナリオ（縦断フロー）をPlaywrightで実装しCI実行へ統合。
- [ ] T3: safeMode/share-export回帰アサーションを共通ヘルパ化。
- [ ] T4: `04_Documentation/e2e_testing.md` に運用手順・失敗時の診断手順を追記。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test:e2e`
  - `npm run test:e2e -- --grep "realistic journey"`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 主要ジャーニーが再現可能で、safeMode/share-exportの境界違反を検知できる。
- 未実施時の理由・代替検証:
  - CI環境差異で不安定な場合は、対象シナリオを単独実行しtraceを添付して要因分離する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既存スモークのみを増量する（実利用再現性が不足するため不採用）。
- 代替案B: 手動回帰チェックリスト中心で運用する（継続負荷と漏れリスクが高いため限定採用）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: シナリオが重くなりCI時間増大、flaky増加。
- 影響範囲: Frontend E2Eパイプライン、リリース判定時間。
- ロールバック手順: 追加シナリオをfeature flag的に分離し、安定化までnightly専用ジョブへ退避。

## 10) Additional context

- 関連Issue/PR/議論ログ: `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`, `01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
- ADR化が必要になる条件（トレードオフ閾値）: CI所要時間が許容閾値を継続超過し、検証レベル設計の方針変更が必要になった場合。
