# Issue Draft: AUTH-SCHEMA-01 Identity schema planning (`users` / `user_identities` / attribution)

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Data Schema Lead（Backend/DB）
- Scope: `02_Architecture/`, `01_Plans/adr/`, `03_Implement/backend/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0020`, `02_Architecture/schemas.md`, `02_Architecture/schemas_review_attribution.md`, `02_Architecture/review_attribution.md`, `02_Architecture/api.md`
- Dependencies: N/A
- Expected verification level: `docs-check`

## RACI（簡易）

| 区分 | Role |
|---|---|
| R (Responsible) | Data Schema Lead（Backend/DB） |
| A (Accountable) | Platform Architecture Owner |
| C (Consulted) | Auth Architecture Lead, Backend Lead, Compliance/Security Officer |
| I (Informed) | PM/Triage, QA Lead |

## 1) 課題 / Problem statement

- `ADR-0020` で定義した identity モデル（`users` / `user_identities`）を、アーキテクチャ正本（`02_Architecture/*`）へまだ確定反映できていない。
- `reviewerRef` / `ownerRef` と内部ユーザーID参照の整合条件が、スキーマとして未固定。
- `ALLOW_JIT_PROVISIONING=false` の厳格運用に必要な API 契約（403/管理者API/CLI）が architecture 文書へ未反映。

## 2) 背景 / Context

- 価値軸上、認証情報を保持しない前提でも認可・所有権・監査のために内部ユーザーマスタは必要。
- enterprise/government 運用では事前プロビジョニングと deprovisioning の説明可能性が要求される。
- 本Issueは schema planning の同期を目的とし、実装着手前の合意形成を行う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: レビュー責任追跡と運用継続性に直結。
- 安全（THREAT_MODEL / SafeMode）: 識別子過剰保存・誤紐付けを防ぐ設計が必要。
- 企業・行政要件（enterprise_architecture）: ガバナンス・監査説明の基盤。
- 後方互換（schemas）: 遅延すると migration 破壊コストが増える。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Architecture docs（`schemas.md`, `schemas_review_attribution.md`, `review_attribution.md`, `api.md`）
- 最小単位:
  1. `users` / `user_identities` のカラム草案・一意制約・index 方針
  2. attribution 側参照規則（`reviewerRef` / `ownerRef`）の整合方針
  3. JIT strict モード時の API 契約（403 / 管理者導線）
  4. migration 戦略（既存データ互換）
- 非目標: 本Issue内で backend 実装・DB migration 実装を完了しない。

## 5) 受入条件 / Acceptance criteria

- [x] `02_Architecture/schemas.md` に identity スキーマ方針が追加されている。
- [x] `02_Architecture/schemas_review_attribution.md` と参照整合が取れている。
- [x] `02_Architecture/review_attribution.md` に運用契約が同期されている。
- [x] `02_Architecture/api.md` に strict モード時の拒否契約/管理導線が記載されている。
- [x] `ADR-0020` との参照が相互に整合している。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 現行 schema/review attribution の identity 参照箇所を棚卸し。
- [x] T2: identity スキーマ案（A/B）を比較し推奨案を決定。
- [x] T3: strict モード運用 API 契約草案を作成。
- [x] T4: architecture 文書の同一PR同期更新。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "users|user_identities|reviewerRef|ownerRef|ALLOW_JIT_PROVISIONING|403" 02_Architecture/*.md 01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - identity 論点の参照が architecture と ADR で一致し、active issue memo 検証が通る。
- 未実施時の理由・代替検証:
  - N/A

## 8) 着手条件 / ブロッカー / 完了条件（実行用）

### 着手条件（Start conditions）

- [x] AUTH-ARCH-01 で定義した属性境界（persist/transient/forbidden）がレビュー済み。
- [x] `02_Architecture/schemas.md` / `schemas_review_attribution.md` / `api.md` の改訂対象章が確定。
- [x] 本IssueのRACIを関係者が合意済み。

### ブロッカー（Blockers）

- [x] AUTH-ARCH-01 の reviewerRef/ownerRef 正規マッピングが未確定。
- [x] strict モード（`ALLOW_JIT_PROVISIONING=false`）時の運用責任境界（管理者API/CLI）が未承認。
- [x] 既存データの互換移行ポリシー（nullable期間・段階移行）の承認が未取得。

### 完了条件（Definition of done）

- [x] `02_Architecture/*` 4文書（schemas, schemas_review_attribution, review_attribution, api）が同一PRで同期更新。
- [x] `ADR-0020` との参照整合と後方互換の注記が更新済み。
- [x] 実装チーム向けに migration 前提（expand/contractの順序）が明文化。

## 9) 実行順序（このIssue内）

1. T1で現行記述差分を抽出（半日）。
2. T2/T3でスキーマ案・strictモード契約案を確定（半日〜1日）。
3. T4で architecture 正本を同一PRで同期（半日）。

## 10) 代替案 / Alternatives considered

- 代替案A: 実装先行で architecture 文書は後追い。
  - 却下理由: 仕様逆転と互換破壊リスクが高い。
- 代替案B: `users` 単表で外部識別子を直持ち。
  - 却下理由: 複数認証経路・移行救済への拡張性が低い。

## 11) リスクとロールバック / Risks & rollback

- 失敗モード: スキーマ固定が早すぎて将来運用を阻害。
- 影響範囲: backend models, migration, review attribution, API。
- ロールバック手順: ADR/Issue を Open で維持し、実装前に再合意。

## 12) 未確定事項（確認質問）

- [Q1] `user_identities` の provider+subject 一意制約に、テナント境界（tenant_id）を含めるか。
- [Q2] deprovision 済みユーザーの attribution 参照を hard delete ではなく tombstone で保持するか。
- [Q3] strict モードでの 403 応答時、運用者向けエラーコード体系を API 仕様に含めるか。

> 上記が未確定のままでは schema の最終固定ができないため、推測で埋めず確認完了まで最終決定を停止する。

## 14) 2026-03-03 設計決定（AUTH-SCHEMA-01）

### T2: `users` / `user_identities` A/B比較

| 観点 | A案: `users` 単表（provider/external_uid を直持ち） | B案: `users` + `user_identities` 分離（1:N） | 採用 |
|---|---|---|---|
| 複数認証経路 | 弱い（後付け時に列追加/制約再設計が必要） | 強い（provider追加を行追加で吸収） | **B** |
| 運用移行（IdP切替） | 既存列更新で競合しやすい | 再紐付け/追加が明確 | **B** |
| 監査性 | userとidentityの変更履歴が混在 | identity変更を分離追跡しやすい | **B** |
| 後方互換・段階移行 | expand/contractが組みにくい | nullable期間を取りやすい | **B** |

推奨案は **B案（`users` / `user_identities` 分離）** とし、`UNIQUE(provider, external_uid)` を基本制約にする。

### Q1〜Q3 決裁結果

- Q1 (`tenant_id` を一意制約に含めるか): **現時点は含めない**。単一テナント前提を維持し、将来マルチテナント導入時は `UNIQUE(tenant_id, provider, external_uid)` への拡張ADRを起票する。
- Q2 (deprovision後の attribution 保持): **tombstone保持を採用**。`users.lifecycle_state=deprovisioned` で帰属参照は維持し hard delete しない。
- Q3 (strict 403エラーコード体系): **API仕様に含める**。最小コード `identity_not_provisioned` を正本にする。

### T3: strictモード403契約と管理者導線

- strict条件: `ALLOW_JIT_PROVISIONING=false` かつ `provider+external_uid` 未登録。
- 応答契約: `403` + `code=identity_not_provisioned` + 管理導線メッセージ。
- 管理者導線: API正本 `POST /admin/provision/users`、CLIはAPIラッパとして提供。

### T4: 同一PR同期対象4文書の更新計画（確定）

1. `02_Architecture/schemas.md`: identity logical schema /制約 / JIT strict / 属性境界
2. `02_Architecture/schemas_review_attribution.md`: reviewerRef/ownerRef 正規マッピング
3. `02_Architecture/review_attribution.md`: PII最小化とstrict拒否の運用契約
4. `02_Architecture/api.md`: strict 403契約・管理者API・CLI位置づけ

### 移行前提（expand/contract）

1. **Expand**: `users` / `user_identities` 追加（既存参照は維持）
2. **Dual-write/read**: JITまたは事前プロビジョニングで identity を並行整備
3. **Backfill**: 既存 attribution を `user:<users.id>` に正規化
4. **Contract**: 旧参照経路を段階撤去（監査ログ整合を確認後）

### 承認記録（RACI）

- A（Accountable）: Platform Architecture Owner — 2026-03-03 承認
- C（Consulted）: Auth Architecture Lead / Backend Lead / Compliance-Security Officer — 同日レビュー完了

## 13) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 互換性影響を伴う schema の最終固定が必要になった時点。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream E serial execution log (2026-05-01)

- Phase 1 Read同期: AUTH-ARCH-01 の決裁値を前提に schema 契約の依存順を確認。
- Phase 2 ADR/CDC: `users` + `user_identities` 分離、`UNIQUE(provider, external_uid)`、strict 403契約との整合に追加ADR不要。
- Phase 3 Plan: Level1/Level2 適用条件を明示（Level1常時、Level2はIdP連携境界変更時必須）し、E2E側へ受け渡し。
- Phase 4 Execute: Stream E の固定順序 2/5（SCHEMA）を完了。
- Phase 5 Verify: `schemas.md` / `schemas_review_attribution.md` / `review_attribution.md` / `api.md` 同期済み前提を再検証。
- Phase 6 Proceed: **Go**（API/IMPLフェーズへ進行）。

## Stream F planning alignment log (2026-05-04)

### Phase 1: Read同期（依存順）

- 固定順序 **ARCH → API/SCHEMA → IMPL → E2E → OPS** を再確認。
- SCHEMAは API と同層の契約固定レイヤとして扱い、IMPL Ready の前提ゲートを担う。

### Phase 3: Plan（AC/DoD補完）

- AC-F-1: `users` / `user_identities` / attribution 契約は ARCH 属性境界と矛盾しない。
- AC-F-2: mock可能境界として `identity_not_provisioned` + `status/code/provisioned` の最小分岐契約を維持。
- DoD-F-1: SCHEMA未確定で IMPL を Ready 化しない。

### Phase 4: Verify（責務分離・固定値）

- Security Officer / System Owner / Platform Operator の運用責務は OPS 正本へ委譲し、SCHEMAで再定義しない。
- strict mode 例外運用固定値（D1〜D4）との矛盾なしを確認。

### Phase 5: Proceed

- 判定: **Go**（SCHEMA契約は実装準備に十分、未承認決定の確定扱いなし）。

## Stream D execution log (2026-05-06)

### Phase 1 Read同期

- `AUTH-ARCH-01` → `AUTH-SCHEMA-01` → `AUTH-API-02` → `AUTH-IMPL-01` → `AUTH-E2E-01` の順序依存を再確認した。
- `02_Architecture/design/strict_mode_exception_approval_flow.html` と `02_Architecture/design/enterprise_architecture.html` を AUTH 系契約の正本として参照し、下流が上流を上書きしていないことを確認した。

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
- ADR/CDC明文化: 既存正本（`ADR-0020`, `02_Architecture/design/enterprise_architecture.html`, `schemas_review_attribution.md`）に未承認決定の確定化がないことを確認。
- I/F先行定義: `reviewerRef/ownerRef = user:<users.id>` と strict時 `identity_not_provisioned` の契約境界を再固定。
- モックIdP活用: `AUTH_PROVIDER_PROFILE` + ヘッダー差替で mock IdP 回帰を維持し、アプリ本体にIdP固有分岐を追加しない方針を維持。
- 実装/文書同期: 本issueは docs契約の整合確認のみ実施（新規仕様追加なし）。
- Verify: 上流契約とのドリフトなし。
- Self-correction (<=3): 0回（修正不要）。
- 報告: 次工程へ **Go**（下流は既存契約参照のみ許可）。
