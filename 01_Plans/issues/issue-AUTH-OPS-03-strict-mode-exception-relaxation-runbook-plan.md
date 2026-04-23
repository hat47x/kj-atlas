# Issue Draft: AUTH-OPS-03 strict mode例外緩和Runbook化 実行計画

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0
- Owner: Security Officer + System Owner + Platform Operator
- Scope: `04_Documentation/operations.md`, `04_Documentation/security.md`, `02_Architecture/enterprise_architecture.md`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0020`, `02_Architecture/enterprise_architecture.md`, `THREAT_MODEL.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- strict mode（`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`）は本番標準だが、例外緩和（`true`）の運用統制を実務Runbookとして固定する手順が未整備。
- 現行文書には2者承認責任と記録責任はあるが、例外起動条件・復旧条件・承認フロー境界が不足しており、監査時に判断が分散し得る。
- 不明確な承認フローを推測で補完すると、既存ADR契約（SafeMode既定ON、PII最小化、監査最小化）と矛盾する恐れがある。

## 2) 背景 / Context

- `04_Documentation/operations.md` は strict mode 例外時に Security Officer + System Owner の2者承認と Platform Operator の記録責務を要求済み。
- `02_Architecture/enterprise_architecture.md` は監査最小情報（PII非保存）と SafeMode/read-only 優先順位を固定済み。
- `THREAT_MODEL.md` はPII最小化と漏えい防止の既定を前提としており、運用例外でもこの前提を崩せない。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 例外運用の判断軸固定により、運用者の解釈差を減らし再現性を確保する。
- 安全（THREAT_MODEL / SafeMode）: strict mode 例外は安全境界に直結し、誤運用は未登録主体の許可につながる。
- 企業・行政要件（enterprise_architecture）: 監査可能性と責任分離（承認者/実行者）が必須。
- 後方互換（schemas）: 既存API契約とSafeMode優先判定を変更せず、運用手順のみを明確化する。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（運用Runbookの実行計画を確定）。
- 最小単位:
  - 通常運用と例外運用の分離条件（トリガー/停止条件/復旧条件）を固定。
  - 2者承認必須項目（Security Officer + System Owner）と、実行記録必須項目（Platform Operator）をテンプレート化。
  - 記録項目として最低 `時刻/理由/承認者/対象環境/復旧条件` を必須化し、PII最小化制約を明記。
  - SafeMode既定ON・監査最小化契約に反しない整合チェックをRunbookチェックリスト化。
- 非目標:
  - コードでの例外バイパス実装。
  - 監査スキーマ拡張やDB保存項目の追加。
  - 承認ワークフロー製品（ITSM/ChatOps）の新規導入。

## 5) 受入条件 / Acceptance criteria

- [x] 例外緩和の発動条件と通常運用条件が、互いに排他的に定義されている。
- [x] 2者承認（Security Officer + System Owner）の必須承認項目が固定されている。
- [x] Platform Operator の実行記録に `時刻/理由/承認者/対象環境/復旧条件` が必須である。
- [x] Runbookが SafeMode既定ON・PII最小化・監査最小化契約に反しないことを、チェックリストで検証できる。
- [x] 不明な承認フローは推測せず、確認質問が明示され、回答前は「停止」状態である。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: strict mode例外の「通常/例外」判定基準と境界条件を定義する。
- [x] T2: 承認テンプレート（2者承認）と実行記録テンプレート（Operator記録）を作成する。
- [x] T3: PII最小化/監査最小化/SafeMode整合の事前・事後チェック項目を作成する。
- [x] T4: 不明承認フローの確認質問リストを定義し、未解決時の停止ルールを明文化する。
- [x] T5: `operations.md` と `security.md` の参照導線を同期する。
- [x] T6: `04_Documentation/security_operational_guidelines.md` を追加し、必須化ではなく運用ガイドラインとして提示する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "strict mode|例外|最小監査|SafeMode/read-only|PII" 04_Documentation/operations.md 04_Documentation/security.md 02_Architecture/enterprise_architecture.md`
- 期待結果:
  - 参照契約（strict mode責任、監査最小化、SafeMode優先）と実行計画の整合が確認できる。
- 未実施時の理由・代替検証:
  - Python実行環境欠如時は `rg` による必須フィールド検査へ切替し、未実施理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 例外緩和を都度チャット承認で運用。
  - 却下理由: 承認項目と復旧条件が欠落し、監査再現性が低い。
- 代替案B: Platform Operator 単独承認で迅速化。
  - 却下理由: 2者承認契約に反し、責任分離が崩れる。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 承認不備またはQ1〜Q10固定値逸脱のまま `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` が適用される。
- 影響範囲: 認証境界、監査整合性、運用統制。
- ロールバック手順: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ即時復旧し、未承認変更または固定値逸脱としてインシデント記録・再承認フローへ戻す。

## 10) Additional context

- D1〜D4（承認順序/TTL、適用スコープ、代理承認、SLA）は `02_Architecture/strict_mode_exception_approval_flow.md` 6.8節で固定済み。
- 本Issueの残作業は文書同期（operations/security/enterprise）と進捗同期（dashboard/decision-pack/README）に限定する。

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 2者承認の職務分掌、または監査最小項目の語彙を変更する必要が発生した場合。

## 11) Q1〜Q10 決裁同期ログ（2026-03-06）

### 11.1 決裁結果

| Question | 論点 | 決裁値 | 運用反映 | 判定 |
|---|---|---|---|---|
| Q1 | 2者承認の順序 | A（Security Officer先行） | strict_mode_exception_approval_flow 6.1 | 確定 |
| Q2 | 承認有効期限 | A（TTL=4h） | strict_mode_exception_approval_flow 6.1 | 確定 |
| Q3 | 対象環境粒度 | A（tenant単位） | strict_mode_exception_approval_flow 6.2 | 確定 |
| Q4 | 最大継続時間/自動復旧 | A（最大2h/TTL超過で自動復旧） | strict_mode_exception_approval_flow 6.2 | 確定 |
| Q5 | 復旧判定者 | A（Security Officer + System Owner共同） | strict_mode_exception_approval_flow 6.3 | 確定 |
| Q6 | 代理承認 | A（代理承認なし） | strict_mode_exception_approval_flow 6.3 | 確定 |
| Q7 | 保存先 | A（変更台帳+監査ID相互参照） | strict_mode_exception_approval_flow 6.4 | 確定 |
| Q8 | 却下時再申請 | A（新requestIdで再申請） | strict_mode_exception_approval_flow 6.4 | 確定 |
| Q9 | 事後レビュー期限 | A（48h） | strict_mode_exception_approval_flow 6.4 | 確定 |
| Q10 | 違反時SLA | A（15m一次/60m二次） | strict_mode_exception_approval_flow 6.4 | 確定 |

### 11.2 停止条件（固定後）

- Q1〜Q10 固定値を満たせない変更要求は `StoppedForClarification` として停止する。
- 2者承認情報欠損、保存先欠損、復旧条件未記載のいずれかで停止する。

### 11.3 Proceed判定

- Runbook運用境界（承認順序/TTL/代理承認/保存先/SLA）を文書で固定済み。
- 本issueは 01/02/04 の同期完了と docs-check 検証完了をもって `Done` に遷移した。


## 12) 完了同期ログ（2026-03-08）

- 同期対象（01/02/04）: `01_Plans/project-progress-dashboard.md` / `02_Architecture/enterprise_architecture.md` / `04_Documentation/operations.md` / `04_Documentation/security.md`。
- 固定値整合: D1〜D4（4h, tenant/2h, 代理承認なし, 48h+15m/60m）を全対象文書で再確認。
- 停止条件整合: 未確定事項が1件でも残る場合は `StoppedForClarification` を維持する契約を再確認。
- 検証: validator/unit test/`rg` により再現可能な形で確認。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。
