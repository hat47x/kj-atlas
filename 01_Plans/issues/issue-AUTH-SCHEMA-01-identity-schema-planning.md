# Issue Draft: AUTH-SCHEMA-01 Identity schema planning (`users` / `user_identities` / attribution)

- Type: Process
- Status: Open
- Lifecycle: Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Data Schema Lead（Backend/DB）
- Scope: `02_Architecture/`, `01_Plans/adr/`, `03_Implement/backend/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0020`, `02_Architecture/schemas.md`, `02_Architecture/schemas_review_attribution.md`, `02_Architecture/review_attribution.md`, `02_Architecture/api.md`
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

- [ ] `02_Architecture/schemas.md` に identity スキーマ方針が追加されている。
- [ ] `02_Architecture/schemas_review_attribution.md` と参照整合が取れている。
- [ ] `02_Architecture/review_attribution.md` に運用契約が同期されている。
- [ ] `02_Architecture/api.md` に strict モード時の拒否契約/管理導線が記載されている。
- [ ] `ADR-0020` との参照が相互に整合している。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 現行 schema/review attribution の identity 参照箇所を棚卸し。
- [ ] T2: identity スキーマ案（A/B）を比較し推奨案を決定。
- [ ] T3: strict モード運用 API 契約草案を作成。
- [ ] T4: architecture 文書の同一PR同期更新。

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

- [ ] AUTH-ARCH-01 で定義した属性境界（persist/transient/forbidden）がレビュー済み。
- [ ] `02_Architecture/schemas.md` / `schemas_review_attribution.md` / `api.md` の改訂対象章が確定。
- [ ] 本IssueのRACIを関係者が合意済み。

### ブロッカー（Blockers）

- [ ] AUTH-ARCH-01 の reviewerRef/ownerRef 正規マッピングが未確定。
- [ ] strict モード（`ALLOW_JIT_PROVISIONING=false`）時の運用責任境界（管理者API/CLI）が未承認。
- [ ] 既存データの互換移行ポリシー（nullable期間・段階移行）の承認が未取得。

### 完了条件（Definition of done）

- [ ] `02_Architecture/*` 4文書（schemas, schemas_review_attribution, review_attribution, api）が同一PRで同期更新。
- [ ] `ADR-0020` との参照整合と後方互換の注記が更新済み。
- [ ] 実装チーム向けに migration 前提（expand/contractの順序）が明文化。

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

## 13) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 互換性影響を伴う schema の最終固定が必要になった時点。
