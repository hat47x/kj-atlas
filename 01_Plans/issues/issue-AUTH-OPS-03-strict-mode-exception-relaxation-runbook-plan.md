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
- [ ] T6: `04_Documentation/security_operational_guidelines.md` を追加し、必須化ではなく運用ガイドラインとして提示する。

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

## 12) Phase 1 前提同期ログ（Q1〜Q10 確定/未確定）

### 12.1 文書横断Gap（現行の矛盾/不足）

- `operations.md` / `security.md` / `enterprise_architecture.md` は strict mode 例外時の2者承認責務を要求しているが、承認順序・TTL・代理承認などの運用境界は未定義。
- `operations.md` は変更台帳への記録責務を定義しているが、保存先システムの固定（チケット/監査基盤/台帳種別）は未定義。
- `enterprise_architecture.md` は PII最小化・監査最小化・SafeMode/read-only 優先を固定しているが、strict mode 例外運用の停止条件/復旧条件を分離記述していない。

### 12.2 Q1〜Q10 判定表（推測補完なし）

| Q | 内容 | 判定 | 根拠 | 停止要否 |
|---|---|---|---|---|
| Q1 | 2者承認の順序 | 未確定 | 既存文書は「2者承認必須」のみ定義し順序規約なし | 停止 |
| Q2 | 承認有効期限 | 未確定 | 承認TTLの規定なし | 停止 |
| Q3 | 対象環境粒度 | 未確定 | tenant/cluster/region 粒度の定義なし | 停止 |
| Q4 | 例外最大継続時間/自動復旧 | 未確定 | 継続時間上限・自動復旧の規定なし | 停止 |
| Q5 | 復旧条件の判定者 | 未確定 | 判定主体の固定なし | 停止 |
| Q6 | 緊急時の代理承認 | 未確定 | 代理承認ポリシー記述なし | 停止 |
| Q7 | 承認・実行記録保存先 | 一部確定（保存義務のみ） | 変更台帳記録義務はあるが保存先種別は未定義 | 停止 |
| Q8 | 却下時の再申請ルール | 未確定 | 再申請規約なし | 停止 |
| Q9 | 事後レビュー期限 | 未確定 | post-incident review 期限規定なし | 停止 |
| Q10 | 違反時のエスカレーション/SLA | 未確定 | エスカレーション先・SLA未定義 | 停止 |

### 12.3 実装可能範囲（確定情報のみ）

- 実装可能: 排他的条件（通常=`ALLOW_JIT_PROVISIONING=false`、例外=`true`）、2者承認責務、Operator記録の必須5項目、SafeMode既定ON/PII最小化/監査最小化の整合チェック。
- 実装停止: 承認順序/期限/代理承認/エスカレーション等、Q1〜Q10で未確定なワークフロー固定。

## 13) Phase 2 境界条件（T1/T4）

### 13.1 通常/例外の排他条件

- 通常運用: `ALLOW_JIT_PROVISIONING=false`（strict）。
- 例外運用: `ALLOW_JIT_PROVISIONING=true` を「期間限定の明示承認」下でのみ許可。
- 排他原則: 同一対象環境に対して strict と例外を同時成立させない（単一時点でどちらか一方のみ有効）。

### 13.2 停止条件（未確定事項による作業停止）

- Q1〜Q10の未確定項目が1つでも「実施判断に必須」の場合、例外適用作業は停止する。
- 停止時は `Status` を Draft 維持とし、質問リストに未解決ID（Q番号）を残す。
- 停止中に推測で承認フローを補完しない。

### 13.3 復旧条件（確定済み範囲）

- 復旧の最小条件: `ALLOW_JIT_PROVISIONING=false` へ戻した事実を記録し、例外記録に復旧時刻と復旧条件充足を追記。
- 復旧判定者の役割分担は未確定のため、Q5解決まで「要確認」扱いで停止する。


## 14) Phase 4 完了判定

- Task/ACは完了。ただし Q1〜Q10 の未確定事項が残るため、`Status: Draft` を維持する。
- 判定: **未確定質問により停止（推測確定なし）**。
