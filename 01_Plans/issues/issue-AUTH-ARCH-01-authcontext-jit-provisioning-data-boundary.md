# Issue Draft: AUTH-ARCH-01 AuthContext/JIT Provisioning のデータ境界定義

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Auth Architecture Lead（Security/Identity）
- Scope: `02_Architecture/`, `03_Implement/backend/`, `01_Plans/adr/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0020`, `02_Architecture/schemas.md`, `02_Architecture/review_attribution.md`
- Dependencies: N/A
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

- [x] AuthContext/JIT Provisioning の属性境界（保存する/しない）が文書化されている。
- [x] reviewerRef/ownerRef と userId の対応方針が明文化されている。
- [x] PII最小化・監査要件・後方互換の観点が明示されている。
- [x] パスキー関連属性（`amr/acr/aal/auth_time`）の扱いが明文化されている。
- [x] 後続実装に必要なタスク（ADR更新 / schema更新 / migration）が分解されている。
- [x] サービス差異（AWS ALB / Cloud IAP 等）を設定テンプレートで吸収する方針が定義されている。
- [x] `users` / `user_identities` 分離モデルと、複数認証経路の例外救済手順が明文化されている。
- [x] `ALLOW_JIT_PROVISIONING=false` 時の事前プロビジョニング契約（管理者API/CLI）が明文化されている。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 現行 schema と review attribution で user identity が登場する箇所を棚卸し。
- [x] T2: AuthContext 属性の分類表（persist/transient/forbidden）を作成。
- [x] T3: reviewerRef/ownerRef との正規マッピング案を2案以上比較。
- [x] T4: ADR更新が必要な論点を切り出し、必要なら新ADRを起票。

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

- [x] `ADR-0020` の AuthContext/JIT 方針を基準文書として固定（参照先の再確認）。
- [x] `02_Architecture/review_attribution.md` と `schemas*.md` の現行差分を棚卸し済み。
- [x] 本IssueのRACIを関係者が合意済み。

### ブロッカー（Blockers）

- [x] 監査要件（`amr/acr/aal/auth_time` の保存要否）に対する Compliance の判断が未確定。
- [x] IAP別ヘッダー差異（AWS ALB / Cloud IAP）を preset で吸収する最小仕様の合意が未確定。
- [x] `ALLOW_JIT_PROVISIONING=false` 時に必要な管理者API/CLIの運用責任者が未確定。

### 完了条件（Definition of done）

- [x] 属性境界（persist/transient/forbidden）が `01_Plans` または `02_Architecture` の正本に明文化。
- [x] reviewerRef/ownerRef と AuthContext.userId の正規マッピング規則が1案に収束。
- [x] 後続Issue（AUTH-SCHEMA-01）に渡す schema 前提（制約/移行前提/非目標）を明文化。

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

## 14) 2026-03-03 決裁記録（AUTH-ARCH-01 blocker解除）

### Q1〜Q3 決裁結果

| 論点 | 選択肢A | 選択肢B | 決定 | 理由 |
|---|---|---|---|---|
| Q1: `auth_time` 保存要否 | DB永続保存（identity/profileに保持） | 認証リクエスト中のみ利用（transient）、必要時は監査イベント側に記録 | **B** | PII最小化と過剰保存回避を優先。`auth_time` は高リスク操作のステップアップ判定の入力としては利用可だが、業務データ本体へは保存しない。 |
| Q2: `aal` 保存と保持期間 | DB永続保存（固定保持期間） | transient評価のみ。保持が必要な場合は監査イベント側で短期保持（既定90日、組織ポリシーで上書き可） | **B** | 規制差異が大きく共通固定値は不適。既定は非永続とし、監査側の保持ポリシーで地域/業界要件に適合させる。 |
| Q3: strict運用責任（API/CLI） | CLI中心（運用者ローカル実行） | APIを正本、CLIはAPIラッパとして提供 | **B** | 監査証跡/冪等性/権限制御をAPI契約へ集約し、CLI差異による運用分岐を避ける。 |

### AuthContext 属性境界（最終）

- persist: `userId`, `provider`, `external_uid`, `display_name`, `email`
- transient: `amr`, `acr`, `aal`, `auth_time`, `roles`, `groups`, `trace_id`
- forbidden: password/hash/secret, WebAuthn credential id, raw policy tokens

### IAP preset 方針（Q2 blocker補完）

- 各IAPのヘッダー差異（AWS ALB / Cloud IAP）は `AUTH_PROVIDER_PROFILE` preset で吸収する。
- 実装分岐は増やさず、`AUTH_USER_FIELD` / `AUTH_EMAIL_FIELD` / `AUTH_NAME_FIELD` などのマッピング宣言のみを可変点にする。

### strict mode 運用責任（Q3 blocker補完）

- Responsible: Auth Architecture Lead（Security/Identity）
- Accountable: Platform Architecture Owner
- API責務: `POST /admin/provision/users` を正本契約として運用
- CLI責務: API呼び出しラッパ（監査責務はAPI側に集約）

### 承認記録

- 2026-03-03: Compliance/Security Officer consulted、Platform Architecture Owner 承認（A）済み。

## 13) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 永続属性と migration 方針を固定する必要が出た時点。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream E serial execution log (2026-05-01)

- Phase 1 Read同期: 本Issueを起点に AUTH-SCHEMA-01 / AUTH-API-02 / AUTH-IMPL-01 / AUTH-E2E-01 / AUTH-OPS-03 の順序依存を再確認。
- Phase 2 ADR/CDC: 既存決裁（2026-03-03）と `ADR-0020` の範囲で契約変更不要（新規CDC不要）と判定。
- Phase 3 Plan: AC/DoD の不足なしを確認し、SCHEMA確定前にIMPLへ進まないストッパーを再宣言。
- Phase 4 Execute: Stream E の固定順序 1/5（ARCH）を完了。
- Phase 5 Verify: downstream issue の前提（属性境界, `reviewerRef/ownerRef` 正規化, strict責務境界）に矛盾なし。
- Phase 6 Proceed: **Go**（SCHEMAフェーズへ進行）。

## Stream F planning alignment log (2026-05-04)

### Phase 1: Read同期（依存順固定）

- 固定順序を **ARCH → API/SCHEMA → IMPL → E2E → OPS** に再確認し、ARCH を唯一の上流契約として維持。
- 本Issueの出力を downstream Ready 判定の前提に固定（未承認論点は ARCH で停止）。

### Phase 3: Plan（AC/DoD補完）

- AC-F-1: AuthContext 属性境界（persist/transient/forbidden）を downstream で再定義しない。
- AC-F-2: `reviewerRef/ownerRef` 正規化規則は `user:<users.id>` の契約境界として保持。
- DoD-F-1: API/SCHEMA/IMPL/E2E/OPS が本Issueの境界条件を参照し、逆依存を作らない。

### Phase 4: Verify（責務分離・固定値）

- 役割分離（Security Officer / System Owner / Platform Operator）は AUTH-OPS-03 で運用責務として保持し、ARCH では設計境界のみを定義する責務分離に矛盾なし。
- strict mode 例外運用の固定値（D1〜D4）は本Issueで再定義せず、`02_Architecture/strict_mode_exception_approval_flow.md` 正本参照に限定。

### Phase 5: Proceed（契約固定）

- 判定: **Go**（ARCH 契約は承認済み・未承認決定の確定化なし）。

## Stream D execution log (2026-05-06)

### Phase 1 Read同期

- `AUTH-ARCH-01` → `AUTH-SCHEMA-01` → `AUTH-API-02` → `AUTH-IMPL-01` → `AUTH-E2E-01` の順序依存を再確認した。
- `02_Architecture/strict_mode_exception_approval_flow.md` と `02_Architecture/enterprise_architecture.md` を AUTH 系契約の正本として参照し、下流が上流を上書きしていないことを確認した。

### Phase 2 ADR/契約明文化

- 新規 ADR 追加は不要と判断（既存 `ADR-0020` と AUTH-OPS-03 の固定値 D1〜D4 で契約が閉じているため）。
- AC/DoD に不足があればドラフト化して合意する方針を継続し、今回は不足なし判定。

### Phase 3 Schema/API固定

- Schema 境界（`users` / `user_identities` / `reviewerRef` 正規化）と API 境界（strict 403 + `identity_not_provisioned` + admin provisioning）の固定状態を再確認した。
- 未承認の新規エラーコード追加や CLI 独自分岐を禁止するストッパーを維持した。

### Phase 4 実装/検証（Plan → Execute → Verify → Proceed）

- Plan: docs 正本と issue memo の整合を確認対象に限定。
- Execute: AUTH 系 issue memo と architecture 正本へ直列実行ログを追記。
- Verify: 文書整合チェックを再実行し、完了条件に矛盾がないことを確認。
- Proceed: **Go**（次回は Stopper 条件に抵触しない限り同順序で継続）。

### Phase 5 Stopper

- 停止条件を再掲: (1) 未承認決定の確定化、(2) Schema 未固定での IMPL 着手、(3) strict mode 固定値 D1〜D4 の不一致。
- 失敗時の自己修復は最大3回までとし、3回超過時は `StoppedForClarification` で停止する。

## Stream E serial execution log (2026-05-10)

### Phase 1 Triage (Ready/Hold)

- 判定: `AUTH-ARCH-01=Ready(完了済みのため再実装不要)`、下流の `AUTH-SCHEMA-01` / `AUTH-API-02` / `AUTH-IMPL-01` / `AUTH-E2E-01` の前提契約を提供済み。
- Hold 条件: D1〜D4改定、役割語彙変更、または strict 例外状態遷移の改定が提案された場合のみ再Open。

### Phase 2 ADR明文化

- Context: 役割分離、2者承認、strict 例外緩和、固定値 D1〜D4 は `strict_mode_exception_approval_flow.md` の正本に収束済み。
- Decision: AUTH-ARCH-01 では上流契約の再定義を禁止し、下流は参照のみ許可。
- Consequences: 下流（Schema/API/E2E）が安全側で固定可能。

### Proceed

- 判定: **Go**（未解決依存なし）。

## Stream G hardening log (2026-05-18)

### Plan
- Stream G の担当境界（AuthN/AuthZ/Provisioning 契約）に限定し、他ストリーム領域（UX/CE/Data/Doc-Ops）へ波及しない。
- Plan → Execute → Verify → Proceed を本節で固定し、未承認の仕様追加は行わない。

### Execute
- AuthContext/JIT の契約固定点を「入力境界・出力境界・監査境界・責務分離」の4観点で再記述。
- strict provisioning（`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`）時の拒否契約を `403 + code=identity_not_provisioned` に固定し、Admin API正本・CLIラッパの責務分離を維持。
- identity schema の移行は expand → dual-write/read → backfill → contract の順序を不変条件として保持。

### Verify
- セキュリティ境界: provider/external_uid の attribution 直保存禁止、PII最小化、reviewerRef/ownerRef は opaque 参照を維持。
- 責務分離: Security Officer / System Owner / Platform Operator の語彙と2者承認原則を弱めない。
- 回帰再現性: Level1（契約単体）/Level2（統合）で同一エラー語彙と同一失敗モードを再実行可能な観点に固定。
- Self-heal 制約: 検証失敗時は最大3回まで自己修復し、超過時は `StoppedForClarification` を必須とする。

### Proceed
- Open化対象: 実装前提が確定した `AUTH-API-02` / `AUTH-IMPL-01` / `AUTH-E2E-01` を順次進行可能。
- 保留対象: 固定値 D1〜D4 改定要求、または roles/groups の永続化要求（現契約では transient）を伴う変更。
- 要承認対象: 監査保持期間変更、strict例外運用の承認フロー変更、IdP多様化に伴う一意制約拡張。



## Stream E phase execution log (2026-05-20)

- Read: AUTH系の直列依存を `AUTH-ARCH-01 -> AUTH-SCHEMA-01 -> AUTH-API-02 -> AUTH-E2E-01` で再確認。
- ADR/CDC明文化: 既存正本（`ADR-0020`, `enterprise_architecture.md`, `schemas_review_attribution.md`）に未承認決定の確定化がないことを確認。
- I/F先行定義: `reviewerRef/ownerRef = user:<users.id>` と strict時 `identity_not_provisioned` の契約境界を再固定。
- モックIdP活用: `AUTH_PROVIDER_PROFILE` + ヘッダー差替で mock IdP 回帰を維持し、アプリ本体にIdP固有分岐を追加しない方針を維持。
- 実装/文書同期: 本issueは docs契約の整合確認のみ実施（新規仕様追加なし）。
- Verify: 上流契約とのドリフトなし。
- Self-correction (<=3): 0回（修正不要）。
- 報告: 次工程へ **Go**（下流は既存契約参照のみ許可）。
