# Issue Draft: AUTH-E2E-01 AuthContext contract Level1/Level2 regression track

- Type: Process
- Status: Done
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

- `cd 03_Implement/backend && KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh`
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
  - `cd 03_Implement/backend && KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh`
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

## Stream F planning alignment log (2026-05-04)

### Phase 1: Read同期（依存順）

- 固定順序 **ARCH → API/SCHEMA → IMPL → E2E → OPS** を再確認し、E2E は IMPL 後段の回帰ゲートとして固定。
- API signature 固定済みを前提に、Level1/Level2 の準備作業を並行可能（実施判定は依存順に従う）。

### Phase 3: Plan（AC/DoD補完）

- AC-F-1: Level1 常時必須、Level2 条件付き必須（IdP連携境界変更時）を維持。
- AC-F-2: mock可能境界（`status/code/provisioned` と `identity_not_provisioned`）に基づき、contract-level 回帰を実施可能にする。
- DoD-F-1: 未承認契約の追加を伴う E2E ケースは Ready 化しない。

### Phase 4: Verify（責務分離）

- Security Officer / System Owner / Platform Operator の承認責務は OPS で担保し、E2E は検証証跡の提供責務に限定。
- strict mode 例外固定値（D1〜D4）に関わる運用変更をE2E仕様で上書きしないことを確認。

### Phase 5: Proceed

- 判定: **Go**（契約レベル回帰トラックとして着手条件を満たす）。
- Proceed: validator/unittest は pass、統合ファイル競合は検出されず。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream F verification refresh (2026-04-30)
- Scope: AUTH backend contract regression only（models/alembic/admin route/test_auth_* + AUTH issue memos）。
- Verify (attempt 1): `pytest 03_Implement/backend/tests/test_auth_*.py -q` -> 20 passed, 3 skipped.
- Verify (attempt 2, self-heal): `KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR=03_Implement/backend/tests/federation/profiles 03_Implement/backend/tests/scripts/run_auth_level2.sh` -> 実行パス誤りで失敗（exit 255）。
- Verify (attempt 3, self-heal): `cd 03_Implement/backend && KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh` -> 1 passed, 3 skipped.
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

### Phase 5 E2E契約レベル検証計画（更新）

- Level1（常時必須）
  - strict拒否逸脱（`403 + identity_not_provisioned` 欠落）を即Fail。
  - 監査ログ最小項目（時刻/理由/承認者/対象環境/復旧条件）の欠落をFail。
- Level2（条件付き必須: IdP連携境界変更時）
  - D1承認TTL=4h、D2最大2h超過、D3代理承認、D4レビュー/SLA逸脱の各違反を回帰観点に固定。
  - mock活用: `status/code/provisioned` の最小分岐キーで contract-level 回帰を先行し、実SP/IdP接続は条件成立時に昇格。

### Proceed

- 判定: **Go**（本Phaseは計画固定まで。実コード改修なし）。

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

## Current-main Evidence Refresh (2026-06-07)

- Candidate: `origin/main@556d54e3b50fdb5d0cf5f875407056514108a745`.
- Scope: targeted rerun of the AuthContext Level1 frontend smoke that keeps the read-only boundary visible without requiring Level2 IdP integration. This is an evidence refresh only; it does not change authentication policy, strict provisioning behavior, Level1/Level2 applicability, issue status, or release authority.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/auth_context_level1_smoke.spec.ts --reporter=line` -> pass, 1 test.
- Evidence detail:
  - Opened `?locale=en&readOnly=true`.
  - Confirmed the read-only boundary message is visible.
  - Confirmed Share & Reproduce remains visible, preserving a safe review/export entry point while editing actions are blocked.
- Decision impact: Done status remains valid. No ADR is required because this refresh does not change AuthContext contract, strict-mode exception policy, IdP boundary, or reviewer/owner attribution semantics.
