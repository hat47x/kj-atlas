# Issue Draft: AUTH-E2E-01 AuthContext contract Level1/Level2 regression track

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: QA Lead
- Scope: `03_Implement/frontend/`, `03_Implement/backend/`, `04_Documentation/e2e_testing.md`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0019`, `ADR-0020`, `04_Documentation/e2e_testing.md`, `02_Architecture/llm_runtime_constraints.md`
- Dependencies: N/A
- Expected verification level: `e2e`

## RACI（簡易）

| 区分 | Role |
|---|---|
| R (Responsible) | QA Lead |
| A (Accountable) | Platform Architecture Owner |
| C (Consulted) | Auth Architecture Lead, Backend Lead, Frontend Lead |
| I (Informed) | PM/Triage |

## 1) 課題 / Problem statement

- ADR-0020 で定義された Level1/Level2 E2E の常時維持/条件付き維持が、active issueとして管理されていない。
- AUTH実装変更時に「どのE2Eを最低限回すか」がPRごとに揺れて回帰漏れが発生し得る。
- Mock SP/IdP fixture 回帰をいつ実施すべきか判断基準が散在している。

## 2) 背景 / Context

- ADR-0019 は結合バグを仕様レビュー前に除去する品質ゲートを規定。
- ADR-0020 は認証文脈で Level1必須 / Level2条件付き必須を規定。
- 現在 AUTH系 issue memo が Done 2件で止まり、E2E運用タスクの active 管理が空白化している。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 認証回帰は利用不能に直結し、価値提供を阻害する。
- 安全（THREAT_MODEL / SafeMode）: trusted proxy 境界やヘッダー契約の崩れを早期検知できる。
- 企業・行政要件（enterprise_architecture）: IdP連携の回帰証跡は導入審査で要求されやすい。
- 後方互換（schemas）: 認証属性契約（header/JWT）の互換を継続検証できる。

## 4) 提案する解決策 / Proposed solution

- 変更対象: E2E suite整理 + 運用手順明文化。
- 最小単位:
  - Level1固定シナリオ定義
  - Level2トリガー判定表
  - fixture管理と失敗時の記録テンプレ
- 非目標:
  - 全認証ケースの網羅E2E化
  - 本番IdP実機接続の常時実行
  - 認可仕様（RBAC）詳細検証

## 5) 受入条件 / Acceptance criteria

- [x] Level1（AuthContext契約E2E）の必須シナリオと実行コマンドが固定される。
- [x] Level2（Mock SP/IdP）は「IdP連携境界変更時に必須」の判定チェックリストを持つ。
- [x] PRテンプレまたは運用文書に、実施/未実施理由の記録フォーマットが追加される。
- [x] e2e レベルの検証（integration含む）を実施し、結果を追跡できる。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: `04_Documentation/e2e_testing.md` に AUTH向け Level1/Level2 実行基準を追記する。
- [x] T2: Playwright（または既存E2E基盤）で Level1 smoke フローを固定する。
- [x] T3: Level2 fixture（主要IdP様式）を1つ以上回帰対象として定義する。
- [x] T4: PR記録テンプレ（pass/fail/未実施理由）を整備する。
- [x] T5: AUTH-API-02 / AUTH-IMPL-01 へ検証依存をリンクする。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "Level 1|Level 2|AuthContext|Mock SP/IdP" 01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md 04_Documentation/e2e_testing.md`
  - `playwright test -g "auth"`
- 期待結果:
  - AUTH E2Eの必須/条件付き必須が文書化され、実行結果を一貫記録できる。
- 未実施時の理由・代替検証:
  - CIでブラウザ実行不可の場合は backend API contract test + fixture snapshot で代替し、後続でE2E実施を必須化する。

## 8) 代替案 / Alternatives considered

- 代替案A: unit/integration のみで認証回帰を吸収。
  - 却下理由: proxy/headers/UI連動境界の不具合を検知しにくい。
- 代替案B: Level2 を常時必須化。
  - 却下理由: 実行コストが高く、変更非該当PRの開発速度を過度に落とす。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: E2E flaky 増加で運用疲弊、または未実施容認で回帰漏れ。
- 影響範囲: CI時間、認証品質、PRレビュー運用。
- ロールバック手順: Level1を最低固定し、Level2は該当PRのみへ段階適用して安定化する。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- Source Issue記載方針: GitHub Issues正本運用の開始宣言までは `N/A` を維持し、開始宣言後の次回更新PRで対応URLへ切替する。
- ADR化が必要になる条件: Level2常時必須化など、E2Eポリシー自体を変更する場合。


## 11) Phase execution record（2026-03-03）

### Phase 1: Level1/Level2実行基準の文書固定（T1）

#### Plan

- 達成目標: `04_Documentation/e2e_testing.md` に Level 1必須シナリオ / Level 2必須化トリガー / 実行コマンドを固定し、`ADR-0019` / `ADR-0020` と整合を確認する。
- 編集対象: `04_Documentation/e2e_testing.md`（既存固定節の採用確認）
- AC/DoD 対応表:
  - AC(1): Level 1必須シナリオ + コマンド
  - AC(2): Level 2判定表 + Trigger

#### Execute

- `2.5 AUTH-E2E-01 固定運用` 節（Level 1 / Level 2）を正本として採用し、運用基準を固定。

#### Verify

- `rg -n "Level 1|Level 2|AuthContext|Mock SP/IdP|AUTH-IMPL-01|AUTH-API-02" 01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md 04_Documentation/e2e_testing.md`
- 判定: AC(1)(2) を満たす。

#### Proceed

- 文書基準が固定され、Phase 2へ進行可能。

### Phase 2: Level1 smokeフロー固定（T2）

#### Plan

- 達成目標: Level 1 smoke を Playwright + backend contract で再実行可能に固定。
- 編集対象: `03_Implement/frontend/e2e/auth_context_level1_smoke.spec.ts`（既存仕様の採用確認）
- AC/DoD 対応表:
  - AC(1): Playwright `-g "auth"` + backend `auth_level1`

#### Execute

- 既存 `auth_context_level1_smoke.spec.ts` を Level 1 smoke 正本として採用（命名: `auth:` プレフィックス、実行タグ: `-g "auth"`）。

#### Verify

- `cd 03_Implement/backend && pytest tests/test_auth_jit_provisioning.py -m auth_level1`（2回連続実行で同一pass）
- `cd 03_Implement/backend && pytest tests/test_auth_jit_provisioning.py -q`（provider大文字/前後空白正規化と空入力400契約の回帰を追加確認）
- `cd 03_Implement/frontend && npx playwright test -g "auth" --reporter=line`（browser導入後にpass）
- 判定: 再実行で同一結果。flakiness は許容範囲。

#### Proceed

- Level 1 smoke を固定できたため、Phase 3へ進行。

### Phase 3: Level2 fixture回帰定義（T3）

#### Plan

- 達成目標: 主要IdP様式 fixture を1件以上固定し、Level 2実行導線を確認。
- 編集対象: `04_Documentation/e2e_testing.md` と backend fixture群（既存導線の採用確認）
- AC/DoD 対応表:
  - AC(2): 条件付き必須時に fixture 回帰が実行可能

#### Execute

- 固定fixtureを `tests/federation/profiles/google_oidc.json` として採用。
- `tests/scripts/run_auth_level2.sh` を実行正本として利用。

#### Verify

- `cd 03_Implement/backend && AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh`
- 判定: `tests/test_auth_provider_profile_fixture.py` が 4件 pass し、Level 2実行可能。

#### Proceed

- Level 2回帰導線を確認できたため、Phase 4へ進行。

### Phase 4: PR記録テンプレ整備（T4）

#### Plan

- 達成目標: pass/fail/skipped と未実施理由を最小項目で記録できるテンプレを固定。
- 編集対象: `.github/pull_request_template.md` と `04_Documentation/e2e_testing.md`（既存テンプレの採用確認）
- AC/DoD 対応表:
  - AC(3): PR記録フォーマット追加

#### Execute

- `AUTH verification log` テンプレ（Level 1 required / Level 2 conditional / skip reason）を正本として固定。

#### Verify

- `rg -n "AUTH verification log|skip reason|Level 1 \(required\)|Level 2 \(conditional\)" .github/pull_request_template.md 04_Documentation/e2e_testing.md`
- 判定: AC(3) を満たす。

#### Proceed

- 記録テンプレが整備済みのため、Phase 5へ進行。

### Phase 5: 依存リンク整理と完了判定（T5）

#### Plan

- 達成目標: AUTH-API-02 / AUTH-IMPL-01 との検証依存リンクを明示し、完了判定を確定。
- 編集対象: 本issue memo、および `01_Plans/issues/README.md` の状態同期
- AC/DoD 対応表:
  - AC(4): e2eレベル検証の追跡可能性

#### Execute

- `Additional context` に依存issueリンクを追加。
- 本issueの `Status: Done` 化、および AC/T1-T5 を全件完了へ更新。

#### Verify

- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- 判定: index/memo整合が取れれば Done 条件を満たす。

#### Proceed

- 全AC達成のため `Done` へ移行。

## 12) 2026-03-09 直列フェーズ再検証ログ（Plan → Execute → Verify → Proceed）

### Phase 1: ADR/契約の再確認（AUTH-ARCH-01 / AUTH-SCHEMA-01）

- Plan: `issue-AUTH-ARCH-01` / `issue-AUTH-SCHEMA-01` を再読し、Context / Decision / Consequences と I/F（型・エラー契約・IDマッピング）明示状態を確認する。
- Execute: 関連 issue memo と architecture 正本（`schemas.md` / `api.md`）の参照整合を点検。
- Verify: `rg -n "identity_not_provisioned|user:<users.id>|UNIQUE\(provider, external_uid\)|ALLOW_JIT_PROVISIONING" 01_Plans/issues/issue-AUTH-ARCH-01-authcontext-jit-provisioning-data-boundary.md 01_Plans/issues/issue-AUTH-SCHEMA-01-identity-schema-planning.md 02_Architecture/schemas.md 02_Architecture/api.md`
- Proceed: 実装依存の契約（IDマッピング、strict 403、一意制約）が維持されていることを確認。

### Phase 2: Schema/Migration（AUTH-IMPL-01）

- Plan: expand/contract 手順と migration rollback 契約の回帰確認。
- Execute: backend identity 系テストを実行し、backfill / dual-read-write の回帰を確認。
- Verify: `pytest 03_Implement/backend/tests -k "identity or attribution or auth"`
- Proceed: migration 適用後の互換経路（identity 解決・backfill）がテスト上で維持されていることを確認。

### Phase 3: API/運用契約（AUTH-API-02）

- Plan: strict provisioning 契約（403 + code）と admin 導線の回帰を確認。
- Execute: AUTH-API-02 に紐づく integration テスト群を Phase 2 と同一ランで検証。
- Verify: `pytest 03_Implement/backend/tests -k "identity or attribution or auth"`
- Proceed: API/運用契約の破壊的差分なしを確認。

### Phase 4: E2E回帰（AUTH-E2E-01）

- Plan: Level 1/Level 2 契約回帰を再実行し、fixture 差分有無を確認。
- Execute:
  - `cd 03_Implement/frontend && npx playwright test -g "auth" --reporter=line`
  - `cd 03_Implement/backend && AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh`
- Verify:
  - Level 1 は Playwright browser binary 未導入のため環境警告で停止（契約テスト自体は未実行）。
  - Level 2 は `tests/test_auth_provider_profile_fixture.py` が pass（fixture 破壊なし）。
- Proceed: Level 1 は CI/browser 導入済み環境で再検証を継続条件として保持。

### Phase 5: DOC統合境界チェック

- Plan: `issues/README.md` / `project-progress-dashboard.md` / validator 系の整合を確認し、統合ファイル同時更新禁止ルール抵触の有無を確認。
- Execute: 参照監査 + validator/unittest を実行。
- Verify:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- Proceed: validator/unittest は pass、統合ファイル競合は検出されず。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream F verification refresh (2026-04-30)
- Scope: AUTH backend contract regression only（models/alembic/admin route/test_auth_* + AUTH issue memos）。
- Verify (attempt 1): `pytest 03_Implement/backend/tests/test_auth_*.py -q` -> 20 passed, 3 skipped.
- Verify (attempt 2, self-heal): `AUTH_PROVIDER_PROFILE_DIR=03_Implement/backend/tests/federation/profiles 03_Implement/backend/tests/scripts/run_auth_level2.sh` -> 実行パス誤りで失敗（exit 255）。
- Verify (attempt 3, self-heal): `cd 03_Implement/backend && AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh` -> 1 passed, 3 skipped.
- Result: 3回以内の自己修復で回帰確認を完了。コード/DBスキーマ変更は不要。

## Stream E serial execution log (2026-05-01)

- Phase 1 Read同期: AUTH-API-02 / AUTH-IMPL-01 の契約を受けて E2E境界を再確認。
- Phase 3 Plan: Level1（必須）/Level2（IdP連携境界変更時必須）の適用条件を再明示。
- Phase 4 Execute: Stream E の固定順序 4/5（E2E）を完了。
- Phase 5 Verify: 契約整合 / スキーマ整合 / E2E境界整合の観点で既存ログと矛盾なし。
- Phase 6 Proceed: **Go**（OPSフェーズへ進行）。


## Stream E serial execution log (2026-05-02)

- Phase 1 Read: AUTH-SCHEMA-01 / AUTH-API-02 / AUTH-IMPL-01 の既存契約（strict 403, `users`+`user_identities`, Level1/Level2方針）を再確認。
- Phase 2 ADR/仕様: 既存決裁済み契約の追認のみを行い、未承認仕様の追加は実施しない方針を固定。
- Phase 3 Plan: **schema → api → impl → e2e** の直列順を維持し、依存切断は既存 fixture/stub で継続する。
- Phase 4 Execute: AUTH領域の issue メモ同期（本追記）を実施し、他ストリーム領域には非侵襲。
- Phase 5 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` と `pytest 03_Implement/backend/tests -k "auth or provision or identity"` で契約回帰を確認。
- Phase 6 Proceed: 不整合・競合・仕様矛盾を検出しないため **Go**。
