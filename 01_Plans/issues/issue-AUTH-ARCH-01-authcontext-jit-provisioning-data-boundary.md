# Issue Draft: AUTH-ARCH-01 AuthContext/JIT Provisioning のデータ境界定義

- Type: Feature request
- Status: Open
- Lifecycle: Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Auth Architecture Lead（Security/Identity）
- Scope: `02_Architecture/`, `03_Implement/backend/`, `01_Plans/adr/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0020`, `02_Architecture/schemas.md`, `02_Architecture/review_attribution.md`
- Expected verification level: `docs-check`

## RACI（簡易）

| 区分 | Role |
|---|---|
| R (Responsible) | Auth Architecture Lead（Security/Identity） |
| A (Accountable) | Platform Architecture Owner |
| C (Consulted) | Backend Lead, Compliance/Security Officer |
| I (Informed) | PM/Triage, QA Lead |

## 1) 課題 / Problem statement

- `ADR-0020` でヘッダー認証 + JIT Provisioning 方針は固定したが、永続化するユーザー属性の最小集合が未確定。
- `header` / `jwt_header` の入力差異や、IAPごとのヘッダー名差異を設定で吸収するマッピング仕様が未確定。
- IdP がパスキー対応した場合の `amr/acr/aal/auth_time` の扱い（保存/表示/監査）が未確定。
- reviewerRef / ownerRef と AuthContext.userId の正規マッピング規則が曖昧で、後続実装で互換破壊リスクがある。
- 企業・行政運用時の PII 最小化と監査要件の境界が未整理。
- `users` / `user_identities` の分離モデルと一意制約、移行時救済手順の詳細が未確定。
- `ALLOW_JIT_PROVISIONING=false` 時の管理者API/CLI契約（事前プロビジョニング）の最小要件が未確定。

## 2) 背景 / Context

- enterprise_architecture は「認証は外部」「アプリはユーザーコンテキストを受け取る」を原則としている。
- schemas/review_attribution は reviewerRef 中心で、AuthContext 由来属性の保存戦略をまだ固定していない。
- 本Issueは Decision ではなく、後続ADR/Schema更新のための論点整理を目的とする。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 追跡可能なレビュー責任と安全運用に直結する。
- 安全（THREAT_MODEL / SafeMode）: PII過剰保存を防ぐため必須。
- 企業・行政要件（enterprise_architecture）: 監査可能性・統制説明の前提。
- 後方互換（schemas）: schema固定前に境界を決めないと migration コストが増大。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs / Schema設計（必要ならADR分離）
- 最小単位:
  1. 永続化候補属性の棚卸し（must/optional/forbidden）
  2. reviewerRef/ownerRef とのマッピング規則草案
  3. `amr/acr/aal/auth_time` の取り扱い方針（persist/transient/forbidden）
  4. `AUTH_USER_FIELD` 等のマッピング設定仕様と provider preset 方針を定義
  5. `users` / `user_identities` のスキーマ案（1:N）と migration 方針を定義
  6. `ALLOW_JIT_PROVISIONING` トグル時の拒否動作・管理者運用導線を定義
  7. 保存しない属性（non-goals）明文化
- 非目標: 本Issue内で backend 実装を完了しない。

## 5) 受入条件 / Acceptance criteria

- [ ] AuthContext/JIT Provisioning の属性境界（保存する/しない）が文書化されている。
- [ ] reviewerRef/ownerRef と userId の対応方針が明文化されている。
- [ ] PII最小化・監査要件・後方互換の観点が明示されている。
- [ ] パスキー関連属性（`amr/acr/aal/auth_time`）の扱いが明文化されている。
- [ ] 後続実装に必要なタスク（ADR更新 / schema更新 / migration）が分解されている。
- [ ] サービス差異（AWS ALB / Cloud IAP 等）を設定テンプレートで吸収する方針が定義されている。
- [ ] `users` / `user_identities` 分離モデルと、複数認証経路の例外救済手順が明文化されている。
- [ ] `ALLOW_JIT_PROVISIONING=false` 時の事前プロビジョニング契約（管理者API/CLI）が明文化されている。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 現行 schema と review attribution で user identity が登場する箇所を棚卸し。
- [ ] T2: AuthContext 属性の分類表（persist/transient/forbidden）を作成。
- [ ] T3: reviewerRef/ownerRef との正規マッピング案を2案以上比較。
- [ ] T4: ADR更新が必要な論点を切り出し、必要なら新ADRを起票。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "reviewerRef|ownerRef|AuthContext|userId" 02_Architecture/*.md 01_Plans/adr/*.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 用語と参照が整合し、issue memo の必須項目検証が通る。
- 未実施時の理由・代替検証:
  - N/A

## 8) 着手条件 / ブロッカー / 完了条件（実行用）

### 着手条件（Start conditions）

- [ ] `ADR-0020` の AuthContext/JIT 方針を基準文書として固定（参照先の再確認）。
- [ ] `02_Architecture/review_attribution.md` と `schemas*.md` の現行差分を棚卸し済み。
- [ ] 本IssueのRACIを関係者が合意済み。

### ブロッカー（Blockers）

- [ ] 監査要件（`amr/acr/aal/auth_time` の保存要否）に対する Compliance の判断が未確定。
- [ ] IAP別ヘッダー差異（AWS ALB / Cloud IAP）を preset で吸収する最小仕様の合意が未確定。
- [ ] `ALLOW_JIT_PROVISIONING=false` 時に必要な管理者API/CLIの運用責任者が未確定。

### 完了条件（Definition of done）

- [ ] 属性境界（persist/transient/forbidden）が `01_Plans` または `02_Architecture` の正本に明文化。
- [ ] reviewerRef/ownerRef と AuthContext.userId の正規マッピング規則が1案に収束。
- [ ] 後続Issue（AUTH-SCHEMA-01）に渡す schema 前提（制約/移行前提/非目標）を明文化。

## 9) 実行順序（このIssue内）

1. T1/T2で現状差分と属性分類を固定（半日）。
2. T3でマッピング案比較と推奨案確定（半日）。
3. T4でADR追記要否を判定し、必要なら起票（半日）。

## 10) 代替案 / Alternatives considered

- 代替案A: backend実装を先行し、後追いでschemaを合わせる。
  - 却下理由: 互換破壊・手戻りが大きい。
- 代替案B: reviewerRefのみを唯一IDとして固定し、AuthContext連携を見送る。
  - 却下理由: IAP連携の運用実態に合わず、追跡性が不足。

## 11) リスクとロールバック / Risks & rollback

- 失敗モード: 属性定義を過剰に固定し将来IdP連携を阻害。
- 影響範囲: schema, import/export, review attribution, API contract。
- ロールバック手順: ADRを Proposed 維持し、schema変更前に再検討する。

## 12) 未確定事項（確認質問）

- [Q1] 監査上、`auth_time` は永続保存必須か、監査イベント側のみで十分か。
- [Q2] `aal` を保存対象にする場合、規制準拠（業界/地域）ごとの保持期間は共通化できるか。
- [Q3] `ALLOW_JIT_PROVISIONING=false` の事前登録導線は、API優先かCLI優先か（運用主体をどちらに置くか）。

> 上記が未確定のままでは保存境界を確定できないため、推測では埋めず確認完了まで仕様固定を停止する。

## 13) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 永続属性と migration 方針を固定する必要が出た時点。
