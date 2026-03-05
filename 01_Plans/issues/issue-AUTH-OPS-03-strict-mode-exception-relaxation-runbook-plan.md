# Issue Draft: AUTH-OPS-03 strict mode例外緩和Runbook化 実行計画

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0
- Owner: Security Officer + System Owner + Platform Operator
- Scope: `04_Documentation/operations.md`, `04_Documentation/security.md`, `02_Architecture/enterprise_architecture.md`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0020`, `02_Architecture/enterprise_architecture.md`, `THREAT_MODEL.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- strict mode（`ALLOW_JIT_PROVISIONING=false`）は本番標準だが、例外緩和（`true`）の運用統制を実務Runbookとして固定する手順が未整備。
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

- [ ] 例外緩和の発動条件と通常運用条件が、互いに排他的に定義されている。
- [ ] 2者承認（Security Officer + System Owner）の必須承認項目が固定されている。
- [ ] Platform Operator の実行記録に `時刻/理由/承認者/対象環境/復旧条件` が必須である。
- [ ] Runbookが SafeMode既定ON・PII最小化・監査最小化契約に反しないことを、チェックリストで検証できる。
- [ ] 不明な承認フローは推測せず、確認質問が明示され、回答前は「停止」状態である。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: strict mode例外の「通常/例外」判定基準と境界条件を定義する。
- [ ] T2: 承認テンプレート（2者承認）と実行記録テンプレート（Operator記録）を作成する。
- [ ] T3: PII最小化/監査最小化/SafeMode整合の事前・事後チェック項目を作成する。
- [ ] T4: 不明承認フローの確認質問リストを定義し、未解決時の停止ルールを明文化する。
- [ ] T5: `operations.md` と `security.md` の参照導線を同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "strict mode の例外承認責任|最小監査記録|SafeMode/read-only 優先" 04_Documentation/operations.md 02_Architecture/enterprise_architecture.md`
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

- 失敗モード: 承認不備のまま `ALLOW_JIT_PROVISIONING=true` が適用される。
- 影響範囲: 認証境界、監査整合性、運用統制。
- ロールバック手順: `ALLOW_JIT_PROVISIONING=false` へ即時復旧し、未承認変更としてインシデント記録・再承認フローへ戻す。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 2者承認の職務分掌、または監査最小項目の語彙を変更する必要が発生した場合。

## 11) 承認フロー未確定事項（確認質問リスト）

> 以下は既存文書で確定できないため、**回答が得られるまでRunbook本文の確定を停止**する。

1. 2者承認の順序は固定か（Security Officer先行/同時/順不同）？
2. 2者承認の有効期限（例: 承認後N時間以内実行）はあるか？
3. 対象環境の粒度は何か（tenant単位/cluster単位/リージョン単位）？
4. 例外緩和の最大継続時間（TTL）と自動復旧要件はあるか？
5. 復旧条件の充足判定者は誰か（Security Officer、System Owner、共同）？
6. 緊急時（夜間障害等）の代理承認者ポリシーは定義済みか？
7. 承認・実行記録の保存先はどこか（既存変更台帳、チケット、監査基盤）？
8. 承認却下時の再申請ルール（再提出要件/クールダウン）はあるか？
9. 例外終了後の事後レビュー（post-incident review）期限は固定か？
10. 違反時（未承認実行）のエスカレーション先とSLAは何か？
