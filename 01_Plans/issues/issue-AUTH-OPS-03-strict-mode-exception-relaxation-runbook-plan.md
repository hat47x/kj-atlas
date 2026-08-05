# Issue Draft: AUTH-OPS-03 strict mode例外緩和Runbook化 実行計画

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P0
- Owner: Security Officer + System Owner + Platform Operator
- Scope: `04_Documentation/operations.md`, `04_Documentation/security.md`, `02_Architecture/enterprise_architecture.md`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0019`, `ADR-0020`, `02_Architecture/enterprise_architecture.md`, `THREAT_MODEL.md`
- Dependencies: N/A
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

## 13) Stream G CDC同期ログ（2026-04-29）

### Plan

- 目的: AUTH-OPS-03 の設計正本に CDC（Change Decision Contract）を明文化し、Plan→Execute→Verify→Proceed の運用規律を欠落なく適用できる状態にする。
- 変更範囲: `02_Architecture/strict_mode_exception_approval_flow.md` のみ（実装変更なし）。
- 受入条件:
  - CDCの Context/Decision/Consequence 定義が明記されている。
  - CDC未確定時に `ApprovalPending` へ遷移禁止が明記されている。
  - D1〜D4 と停止条件（`StoppedForClarification`）との矛盾がない。

### Execute

- `strict_mode_exception_approval_flow.md` に「1.2 CDC（Change Decision Contract）明文化」節を追加。
- CDC最小テンプレート（Context/Decision/Consequence/承認者/適用日/見直し日）を追加。
- CDC未確定時は `DraftRequest` 維持、`ApprovalPending` 遷移禁止を追記。

### Verify

- `rg -n "CDC|Change Decision Contract|ApprovalPending|StoppedForClarification|D1|D2|D3|D4" 02_Architecture/strict_mode_exception_approval_flow.md`
- 期待: CDC節と停止条件・固定値の両方が同一文書内で確認できる。

### Proceed

- 判定: CDC明文化により、AUTH設計変更の事前合意条件が設計正本で再利用可能になった。
- 次アクション: AUTH-ARCH/AUTH-SCHEMA の新規変更要求は、CDC記録作成→合意完了後にのみ実行へ進む。

## Stream E serial execution log (2026-05-01)

- Phase 1 Read同期: AUTH-ARCH〜E2E の結果を受け、運用固定値（D1〜D4）への影響有無を確認。
- Phase 2 ADR/CDC: 既存 CDC/承認フローを再利用し、新規未承認仕様の固定化は未実施。
- Phase 3 Plan: AC/DoD不足なし。2者承認・責務分離・停止条件を維持。
- Phase 4 Execute: Stream E の固定順序 5/5（OPS）を完了。
- Phase 5 Verify: docs-only 変更として契約差分なし、自己修復上限超過なし。
- Phase 6 Proceed: **Go**（Stream E 直列完了）。

## Stream F planning alignment log (2026-05-04)

### Phase 1: Read同期（依存順）

- 全AUTH Issue の依存順を **ARCH → API/SCHEMA → IMPL → E2E → OPS** で固定し、OPS を最終運用ゲートとして再確認。
- 役割分離（Security Officer / System Owner / Platform Operator）記述の存在を全Issueで点検し、欠落なしを確認。

### Phase 3: Plan（AC/DoD補完）

- AC-F-1: D1〜D4 固定値（承認順序/TTL、適用スコープ、代理承認、SLA）を運用Runbookで再定義せず正本参照で運用する。
- AC-F-2: 未承認決定の確定扱いを禁止し、`StoppedForClarification` 維持条件を明示。
- DoD-F-1: 下流実装担当が参照する「契約固定一覧」を issue 間で一貫化する。

### Phase 4: Verify（フェイルセーフ）

- 停止条件:
  1. 権限境界の矛盾
  2. 未承認決定の確定扱い
  3. 依存順破壊
- 上記3条件のいずれも検出されず、自己修復ループ不要（0/3）。

### Phase 5: Proceed（Backend着手用 契約固定一覧）

- C-1: 依存順は **ARCH → API/SCHEMA → IMPL → E2E → OPS**（逆順禁止）。
- C-2: strict拒否契約は `403 + code=identity_not_provisioned` を固定。
- C-3: 管理導線は `POST /admin/provision/users` を API 正本、CLI はラッパのみ。
- C-4: identity は `users` / `user_identities` 分離、基本制約は `UNIQUE(provider, external_uid)`。
- C-5: attribution 正規化は `reviewerRef/ownerRef = user:<users.id>`。
- C-6: 移行順序は `expand → dual-read/write → backfill → contract` 固定。
- C-7: 運用固定値 D1〜D4 は `strict_mode_exception_approval_flow` 正本に従い、実装・E2E側で再定義しない。
- 判定: **Go**（Backend実装担当が即着手可能）。


## 18) Stream E execution record (2026-05-18)

- Phase 1 Read: AUTH-ARCH-01 / AUTH-SCHEMA-01 / AUTH-API-02 / AUTH-E2E-01 と AUTH-OPS-03 正本を再読し、D1〜D4・役割語彙・停止条件を再確認。
- Phase 2 Plan: 同期順序 `02_Architecture -> 04_Documentation -> 01_Plans` を固定し、AUTH以外への越境編集を禁止。
- Phase 3 Execute: `strict_mode_exception_approval_flow.md` / `enterprise_architecture.md` 参照に合わせ、operations/security に運用チェックを追記。
- Phase 4 Verify: docs差分確認で `StoppedForClarification` 条件と D1〜D4 が全層一致することを確認。
- Phase 5 Proceed: 次回再開条件は「D1〜D4改定要求がないこと、かつ 3層同期ログが同日で揃うこと」。

## 19) Stream G execution record (2026-05-20)

- Phase 1 Read & Terminology Gate: 用語（Security Officer / System Owner / Platform Operator）、2者承認+実行責務分離、D1〜D4 固定値を再監査。
- Phase 2 Architecture: `strict_mode_exception_approval_flow.md` を起点に承認条件・停止条件・復旧条件・失効条件の整合を確認（仕様変更なし、契約維持）。
- Phase 3 Documentation: `operations.md` / `security.md` に申請→承認→実施→監査→失効の運用チェックリストを追記し、導線を正本参照へ統一。
- Phase 4 Plans: dashboard / decision-pack / 本issue の状態整合を確認し、AUTH-OPS-03 は Done 維持。
- Phase 5 Verify（4観点）: 用語・役割・導線・D1〜D4 一致、self-correction 0/3、停止条件違反0件。
