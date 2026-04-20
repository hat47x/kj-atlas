# E2Eテスト方針（Playwright）

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部開発者・QA
> Goal: 再現可能なE2E手順と受入条件を公開する。
> Non-goal: 内部進行メモ・個別PRの暫定判断ログの恒久公開。
> Public boundary: 内部進行管理情報は除外し、実行手順と判定基準を公開する。
> Outcome: 外部開発者が実行経路（Compose / SQLite代替）と合否判定を独力で再現できる。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Related: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/installation.md`, `04_Documentation/operations.md`, `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`

## DOC-OPS-05 統合同期メモ（2026-04-18）

- 連携 issue: `issue-doc-ops-05-06` / `issue-doc-ops-05-11` / `issue-doc-ops-05-13` / `issue-doc-ops-05-14`
- canonical 用語: `Security Officer / System Owner / Platform Operator`
- canonical 状態語彙: `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed`（未確定時 `StoppedForClarification`）
- fixed values (D1〜D4): `4h / 2h / 代理承認なし / 48h + 15m/60m`
- 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md`（`operations.md` は runbook 同値確認先）



> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
本ドキュメントは、`kj-atlas` における End-to-End テストの実施方針を定義します。  
詳細な運用ルールは `ADR-0019` を正本とし、本書では **実装チーム向けの具体手順** を扱います。

---

## 共通ワークフローとフェイルセーフ（DOC-OPS-05 共通）

本書の更新は次の固定順序で実施する。

1. Phase 1 Read
2. Phase 2 Plan（品質ゲート宣言）
3. Phase 3 Execute（局所更新）
4. Phase 4 Verify（リンク/語彙/整形）
5. Phase 5 Proceed（残課題明示）

フェイルセーフ:

- Verify 失敗時は **自己修復を最大3回まで** 実施する。
- 4回目相当は作業を停止し、`01_Plans/issues/` にブロッカーを記録してエスカレーションする。

- Stream F フェイルセーフ: テスト方針の矛盾または監査要件未達が判明した時点で更新を停止し、Proceedでは未解消項目を明示する。

## 1. 基本方針

1. `03_Implement/*` の変更では、原則として E2E確認を行う。
2. UIを伴う変更（Canvas / SidePanel / Import/Export導線 / SafeMode表示）では、
   **Playwright によるE2Eテスト追加または更新を原則必須** とする。
3. テストは「壊れにくさ」を優先し、以下を重視する。
   - 主要ユーザーフローの成功確認
   - 回帰しやすい安全境界（SafeMode / import / export / docs保存）
   - 環境差分に強い待機戦略（networkidle固定に依存しすぎない）

### 1.1 Stream F 文書横断同期チェック（Verify フェーズ）

architecture -> security -> guidelines の直列同期後、operations/e2e では docs-check と `rg` により次を固定確認する。

- 役割語彙: `Security Officer / System Owner / Platform Operator`
- 状態遷移語彙: `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed` と `StoppedForClarification`
- D1〜D4 固定値: `4h / 2h / 代理承認なし / 48h + 15m/60m`
- 相互リンク: `strict_mode_exception_approval_flow.md` / `security.md` / `security_operational_guidelines.md` / `e2e_testing.md` を参照可能

運用側の検証コマンド（docs-only変更時）:

- `python 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "Security Officer|System Owner|Platform Operator|StoppedForClarification|DraftRequest|ApprovalPending|Approved|ActiveException|RollbackPending|Closed|D1|D2|D3|D4|4h|2h|48h|15m|60m" 02_Architecture/strict_mode_exception_approval_flow.md 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/security_operational_guidelines.md 04_Documentation/e2e_testing.md`

---

## 2. kj-atlas向け推奨E2Eスコープ

### 2.1 Smoke（毎回実施）

- App起動
- APIヘルス確認
- 初期Document読込

### 2.2 Core Flow（変更影響時に必須）

- Cardの追加・移動・保存
- Islandの作成・collapse/expand
- 再読込後の状態保持

### 2.3 Security/Safety Flow（変更影響時に必須）

- SafeMode ON時の表示/制約
- readOnly + SafeMode の安全境界（編集抑止と表示ラベル）
- visibility（view/pack）の編集・再読込保持
- import（正常/異常）
- export（意図しない漏えい防止）

### 2.4 Auth Federation Flow（認証連携変更時に必須）

`ADR-0020` に従い、認証連携境界（header/JWT mapping, provider preset, logout/step-up）を変更する場合は
Level 2（Mock SP/IdP）を実施する。

- 目的: 主要IdP製品・サービスのデータ連携仕様/様式を fixture で再現し、設定互換を回帰保証する。
- 追加観点: `ALLOW_JIT_PROVISIONING=false`（事前プロビジョニング）時に、未登録IDが `403` で拒否されること。
- 最低要件:
  - provider profile fixture を1つ以上使ったE2Eを含める。
  - 差異観点（ヘッダー名、claim名、groups形式、`amr/acr` 有無）のいずれかを検証する。
- 例:
  - `e2e/auth_context_level1_smoke.spec.ts`（Frontend Playwright smoke）
  - `tests/test_auth_provider_profile_fixture.py`（Backend fixture contract）

#### Level 2 実行の標準手順（Mock SP/IdP）

`03_Implement/backend/tests/scripts/run_auth_level2.sh` を **ローカル/CI 共通の正本コマンド** とする。

- 実行コマンド
  - `cd 03_Implement/backend`
  - `tests/scripts/run_auth_level2.sh`
- 起動されるプロセス
  - backend: `uvicorn kj_atlas_api.main:app --port 18000`
  - mock_idp: `uvicorn tests.federation.mock_idp:app --port 18081`
  - mock_sp: `uvicorn tests.federation.mock_sp:app --port 18080`
- provider profile fixture の切替
  - 既定ディレクトリ: `03_Implement/backend/tests/federation/profiles/*.json`
  - 差し替え時: `AUTH_PROVIDER_PROFILE_DIR=/path/to/profiles tests/scripts/run_auth_level2.sh`

fixture では以下の主要差異を再現する。

- ヘッダー名/subject claim 名の差異（`sub`/`oid`/`nameid`）
- claim 名差異（`email`/`upn`/`mail`, `name`/`displayName`/`cn`）
- groups 形式差異（配列 / CSV）
- `amr` / `acr` の有無

失敗時は `03_Implement/backend/.artifacts/auth-level2/` にログが残る（`backend.log`, `mock-idp.log`, `mock-sp.log`, `pytest-auth-level2.log`）。


### 2.6 CE3 Patch Workspace Flow（CE3変更時に必須）

CE3（候補比較/部分採用/rollback/preset replay）を変更するPRでは、次のE2E観点を最低限確認する。

- 候補に対する `adopt / hold / reject` が独立して操作できる。
- 候補比較UIで最低3候補を同時表示できる（`ce3-candidate-count` と selector option 件数の双方で確認）。
- 候補A/Bを連続操作した後、候補ごとの状態表示（decision matrix）が独立に保持される。
- decision matrix の候補件数表示（`ce3-candidate-count`）が収集候補数と一致する。
- `Roll back last workspace decision` で直前状態へ復帰できる。
- rollback後に「直前の候補だけ」が復旧され、先行候補の決定は維持される。
- rollback実行時に、復旧対象候補の監査遷移表示へ `(...rollback)` が追記される。
- rollback後に先行候補の監査遷移表示へ `(...rollback)` が誤付与されない。
- rollback監査遷移の時刻が、同操作で発火するUIイベント時刻と整合する（同一操作由来として追跡可能）。
- Preset保存後の replay で `scope/depth/filters` 正規化JSONが再現される（filters は trim/lowercase/重複排除後にソート）。
- Preset保存後にページ再読込しても、保存済み `Run <name>` で同一正規化JSONが再現される。
- 監査遷移数（Audit transitions）が操作回数に応じて増加する。
- Perspective切替で document永続データ差分が増えない（workspace/presetはlocal state/localStorage管理）。
- SafeMode ON でも share/export の追加露出が発生しない。

推奨コマンド（grepはプロジェクト命名に合わせる）:

- `cd 03_Implement/frontend && npm run test -- ce3_patch_workspace PatchWorkspacePanel`
- `cd 03_Implement/frontend && npm run e2e -- --grep "Patch Workspace|Preset|rollback"`

CE3 変更PRで Playwright 実行環境が未セットアップの場合は、次を事前実行する。

- `cd 03_Implement/frontend && npm exec playwright install chromium`
- `cd 03_Implement/frontend && npm exec playwright install-deps chromium`

CE3 Verify の自己修復順序（最大3回）:

1. 1回目失敗: `playwright install chromium`
2. 2回目失敗: `playwright install-deps chromium`
3. 3回目: E2E再実行（未収束なら停止して blocker 記録）

#### CE3 UI状態機械 AC/DoD（Stream F frontend）

CE3 Frontend の状態機械（`idle / decision_recorded / preset_replayed / rollback_ready / error` と候補単位の `adopt/hold/reject`）に対する最小AC/DoDを次で固定する。

- AC（受入条件）
  - `ce3-decision-state` が phase を常に可視化できる。
  - `ce3-candidate-state-*` / `ce3-candidate-audit-*` が候補ID単位で独立表示される。
  - `ce3-audit-log-size` が操作回数に応じて増減を観測できる。
  - SafeMode境界を越える導線（share/export auto）をCE3 panelに追加しない。
- DoD（完了条件）
  - panel unit（`PatchWorkspacePanel.test.ts`）で上記ACの静的可観測性を検証する。
  - domain unit（`ce3_patch_workspace.test.ts`）でrollback時の候補独立性を検証する。
  - CE3 e2e grep（Patch Workspace/Preset/rollback）を実行し、失敗時は自己修復手順を3回上限で適用する。



#### CE3 検証記録（2026-04-18 / frontend）

- 対象Issue: `01_Plans/issues/issue-CE3-patch-workspace-presets.md`
- 実行結果:
  - unit: pass（ce3 domain/ui/preset）
  - e2e 1回目: browser binary 不足で fail
  - 自己修復1: `npm --prefix 03_Implement/frontend exec playwright install chromium`
  - e2e 2回目: `libatk-1.0.so.0` 不足で fail
  - 自己修復2: `npm --prefix 03_Implement/frontend exec playwright install-deps chromium`
  - e2e 3回目: pass（`--grep "CE3 patch workspace|Patch Workspace|Preset|rollback"`）
- 判定: 自己修復2回で収束（上限3回未満）。safeMode後退・share/export露出追加なし。

### 2.5 AUTH-E2E-01 固定運用（Level 1 / Level 2）

本節は `issue-AUTH-E2E-01` の正本運用として固定する。依存実装は
`issue-AUTH-IMPL-01`（identity schema migration）と `issue-AUTH-API-02`（strict provisioning contract）。

#### AC（AUTH-E2E-01で固定する受入条件）

- **Level 1必須シナリオと実行コマンド** を固定する。
- **Level 2必須化トリガー（IdP連携境界変更時）** を固定する。
- **PR記録テンプレ（pass/fail/未実施理由）** を固定する。
- 変更分類（Smoke/Core/Safety）をPR本文へ明記する。

#### 変更分類（Smoke/Core/Safety）

- **Smoke**: 認証状態に依存せず、AuthContext前提のUI起動確認を維持する。
  - `cd 03_Implement/frontend && npx playwright test -g "auth" --reporter=line`
- **Core**: AuthContext契約（strict provisioning / allow list / JIT）を回帰確認する。
  - `cd 03_Implement/backend && pytest tests/test_auth_jit_provisioning.py -m auth_level1`
- **Safety**: trusted proxy外からの偽装拒否、strict mode 403、監査境界を守る。
  - `cd 03_Implement/backend && pytest tests/test_auth_provider_profile_fixture.py`

#### Level 1（毎回必須）

- Frontend smoke（AuthContext前提導線）
  - `cd 03_Implement/frontend && npx playwright test -g "auth" --reporter=line`
- Backend contract（strict provisioning）
  - `cd 03_Implement/backend && pytest tests/test_auth_jit_provisioning.py -m auth_level1`

- 受入条件:
  - Playwright `-g "auth"` が pass し、AuthContext前提導線の最低動作を確認できる
  - strict mode未登録subjectが `403` かつ `identity_not_provisioned` を返す
  - `POST /admin/provision/users` 後の再試行で docs write が `200`

Playwright 実行不能環境（例: browser binary 未導入）では、以下を**代替必須**とする。

- `cd 03_Implement/backend && pytest tests/test_auth_jit_provisioning.py -m auth_level1`
- `cd 03_Implement/backend && pytest tests/test_auth_provider_profile_fixture.py::test_provider_profile_fixture_google_oidc_roundtrip`

この場合、PRには「Playwright不能理由」と「後続実施条件（例: `npx playwright install` 完了後に再実行）」を必ず記載する。

#### Level 2（条件付き必須）

以下のいずれかに該当するPRでは Level 2 を必須化する。

- `AuthContextAdapter` / provider preset / header mapping を変更
- trusted proxy境界、JWT claim mapping、step-up(amr/acr/aal)の処理を変更
- `ALLOW_JIT_PROVISIONING` 挙動または `/admin/provision/users` 契約を変更

##### AUTH-IMPL-01 / AUTH-API-02 向け Level 2 必須化判定表

| 変更チケット | 具体的な変更内容（PR差分での判定キー） | Level 2 判定 | 判定理由 |
|---|---|---|---|
| AUTH-IMPL-01 | `users` / `user_identities` migration のみ（DDL/backfill/dual-write）で、AuthContext header/JWT mapping と provisioning API 契約に変更なし | 任意（推奨） | 永続層の整合が主目的であり、IdP境界互換の破壊可能性は相対的に低い。Level 1 で strict provisioning 契約を担保する。 |
| AUTH-IMPL-01 | identity migration に伴って `AuthContextAdapter`、subject 解決順、provider 判定、trusted proxy 判定ロジックを変更 | **必須** | DB変更であっても認証境界の入力解釈に波及し、IdPプロファイル差異で破綻し得るため。 |
| AUTH-API-02 | `/admin/provision/users` の入力/出力契約、拒否コード、`ALLOW_JIT_PROVISIONING` の意味論を変更 | **必須** | strict provisioning 契約そのものの変更であり、Level 2 fixture による境界回帰確認が必要。 |
| AUTH-API-02 | header/JWT claim mapping（`sub`/`oid`/`nameid`, groups形式, `amr/acr/aal`）を変更 | **必須** | IdP差異の吸収責務に直接影響するため、Mock SP/IdPでの差異再現が必須。 |
| AUTH-API-02 | 認証無関係（ログ整形、コメント、auth外module限定） | 不要 | 認証連携境界へ影響がないため。ただしPR本文で「境界非影響」を明記する。 |

判定に迷う場合は **安全側（Level 2 実施）** を採用し、レビュー時に「境界非影響」の根拠を差分行番号つきで提示する。

最低1件の fixture を回帰対象として固定する。

- **固定fixture（最低1件）**: `tests/federation/profiles/google_oidc.json`
- 推奨追加fixture: `tests/federation/profiles/azure_oidc.json` / `tests/federation/profiles/keycloak_saml_like.json`

- `cd 03_Implement/backend && AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh`

#### Level 2 最小回帰テストパック設計（Mock SP/IdP）

IdP連携境界変更PRに対して、QA Lead が即時適用できる最小パックを以下で固定する。
本節は **設計（実行計画）** であり、実装追加時は本節を正本として追随する。

##### A. Level 2 実施トリガー（明文化）

次のいずれか1つでも該当したら Level 2 を実施する（`OR` 判定）。

1. `AuthContextAdapter` 変更
   - 例: 入力モード、subject解決順、provider判定、trusted proxy判定の変更。
2. provider preset / provider profile fixture 変更
   - 例: preset定義の追加・削除・既存キー意味変更、fixture JSON更新。
3. logout / step-up / `amr`/`acr`/`aal` 関連変更
   - 例: RP-Initiated logout経路、step-up必須条件、`amr` 正規化。
4. 認証境界のmapping変更
   - 例: header名、JWT claim名、groups形式（array/CSV）、`ALLOW_JIT_PROVISIONING` 契約。
5. 依存ライブラリ更新
   - 対象: `pysaml2` / `Authlib` / `xmlsec1`（SAML/OIDC境界に影響する更新）。

判定に迷う場合は安全側として Level 2 を実施する。

##### B. provider profile fixture 最小セット

最低セットは「主要差分1系統」を担保するため、次の2件を **必須最小** とする。

- `tests/federation/profiles/google_oidc.json`
  - ベースライン（OIDC標準寄り、既存固定fixture）。
- `tests/federation/profiles/azure_oidc.json`
  - 主要差分系統（claim/subject/groups差異）を1系統追加で担保。

任意拡張（SAML-like差分の追加確認）:

- `tests/federation/profiles/keycloak_saml_like.json`

##### C. 成否判定（Level 1整合）

Level 2 の pass 条件は、Level 1受入基準と矛盾しないよう次で統一する。

1. Level 1 の必須条件が先に pass していること。
2. Level 2 では fixture ごとに以下を満たすこと。
   - docs write/read roundtrip 成功（`put_status=200` かつ `get_status=200`）。
   - provider識別値が応答に存在する（空でない）。
3. strict provisioning 契約を破らないこと。
   - `ALLOW_JIT_PROVISIONING=false` 時の未登録subject拒否（`403`）意味論が維持されること。
4. 失敗時は `.artifacts/auth-level2/*.log` を添付し、境界破壊か環境要因かを切り分けること。

##### D. 実行コスト最適化（常時実行 / 条件付き実行の分離）

| 区分 | 目的 | 実行コマンド | 実行タイミング |
|---|---|---|---|
| 常時実行（Level 1） | 契約の高速回帰 | `cd 03_Implement/backend && pytest tests/test_auth_jit_provisioning.py -m auth_level1` | 全PR |
| 常時実行（Level 1） | UIのAuth導線smoke | `cd 03_Implement/frontend && npx playwright test -g "auth" --reporter=line` | 全PR（不可時は代替記録必須） |
| 条件付き（Level 2最小） | Mock SP/IdP境界回帰 | `cd 03_Implement/backend && AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh` | 上記トリガー該当PR |
| 条件付き（Level 2最小） | fixture契約の高速確認 | `cd 03_Implement/backend && pytest tests/test_auth_provider_profile_fixture.py -m auth_level2` | 上記トリガー該当PR |

##### E. 不足fixture / 環境制約への対応（暫定代替 / 正式対応）

1. fixture不足（新規IdP差分が未追加）
   - 暫定代替案:
     - 既存2件（google + azure）で最も近い差分を選択し、PRに「未再現差分」を明記する。
     - 必要に応じて `tests/fixtures/provider_profile_google_oidc.json` を境界確認の補助に使う。
   - 正式対応案:
     - `tests/federation/profiles/<provider>.json` を追加し、`run_auth_level2.sh` 対象へ編入する。

2. 環境制約（`xmlsec1` 未導入 / Playwright browser 未導入）
   - 暫定代替案:
     - backend側 contract test（`auth_level1`, `auth_level2` マーカー）を先行実施し、PRで不足理由と再実行条件を宣言。
   - 正式対応案:
     - CIイメージへ `xmlsec1` を同梱、Frontend CIに `npx playwright install --with-deps chromium` を固定し再現性を恒久化。

3. mock起動不可（ポート競合/ローカル制約）
   - 暫定代替案:
     - `AUTH_LEVEL2_SP_BASE_URL` を変更して空きポートで再実行し、不可なら fixture単体契約テストまで実施。
   - 正式対応案:
     - CIのLevel 2専用ジョブでポート予約・artifact保存を標準化し、ローカル差異依存を縮小する。

#### 実施記録テンプレ（PR転記）

```md
### AUTH verification log
- classification: Smoke | Core | Safety

- Level 1 (required): pass | fail
  - command:
    - `cd 03_Implement/frontend && npx playwright test -g "auth" --reporter=line`
    - `cd 03_Implement/backend && pytest tests/test_auth_jit_provisioning.py -m auth_level1`
  - result:

- Level 2 (conditional): pass | fail | skipped
  - trigger matched: yes | no
  - trigger reason (required):
    - `AUTH-IMPL-01: <schema only | auth boundary changed>`
    - `AUTH-API-02: <contract changed | boundary unchanged | not in scope>`
  - command:
    - `cd 03_Implement/backend && AUTH_PROVIDER_PROFILE_DIR=tests/federation/profiles tests/scripts/run_auth_level2.sh`
  - fixture (required when executed): `tests/federation/profiles/google_oidc.json`
  - result:
  - skip reason (if skipped):
```

#### `playwright test -g "auth"` 実行前提（後続AUTH実装PR向け）

- Frontend依存が解決済みであること（`cd 03_Implement/frontend && npm ci`）。
- Playwright browser binary が導入済みであること（`cd 03_Implement/frontend && npx playwright install --with-deps chromium`）。
- backend/frontend の health endpoint が応答すること（本書 3.1 / 3.2 のヘルス確認）。
- 上記が満たせない場合、PRには **阻害要因・代替検証・再実行条件** を同時記載する。

---

## 3. 実行プロファイル

### 3.1 Compose優先（標準）

`web + api + db` を起動した状態で Playwright を実行する。

最小実行コマンド（PR転記対象）:

```bash
cd /path/to/kj-atlas/03_Implement/deploy
docker compose up --build -d
docker compose ps
curl -fsS http://localhost:8080/api/health
curl -fsS -X PUT http://localhost:8080/api/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8080/api/docs/<doc_id>

cd /path/to/kj-atlas/03_Implement/frontend
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
```

- `i18n_locale_query_equivalence.spec.ts` は smoke（起動/表示）+ 変更フロー（document replace）を同時確認できる最小セット。

### 3.2 Docker未導入時（代替）

`backend(SQLite) + frontend dev server` 構成で Playwright を実行する。

- backend: `:8000`
- frontend: `:4173`（`/api` proxy 経由）

最小実行コマンド（PR転記対象）:

```bash
curl -fsS http://localhost:8000/healthz
curl -fsS http://localhost:4173/api/healthz
curl -fsS -X PUT http://localhost:8000/docs/<doc_id> -H 'content-type: application/json' --data-binary @/tmp/e2e_doc.json
curl -fsS http://localhost:8000/docs/<doc_id>

cd /path/to/kj-atlas/03_Implement/frontend
npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line
```

---

## 4. テスト追加ルール（原則）

- 新機能: 1本以上のE2Eシナリオを追加
- バグ修正: 再発防止のE2Eシナリオを追加
- 文言/軽微UIのみ: screenshotベース確認でも可（ただし影響範囲をPRで明記）

命名例:

- `e2e/polygon_import_validation.spec.ts`（自己交差polygon importのフォールバック確認）
- `e2e/polygon_vertex_edit.spec.ts`（polygon頂点ドラッグ編集の保存・制約維持確認）
- `e2e/diagnostics_structural_metrics.spec.ts`（構造メトリクスがbundle diagnosticsへ反映され、連続exportで決定論を維持することを確認）

---

## 5. PR記載ルール

PR本文には最低限以下を記載する。

- 実行環境（Compose / SQLite代替）
- 実行コマンド
- 成否
- 未実施項目（あれば理由）

例:

- `npm run e2e`（Playwright）
- `npm run e2e -- e2e/polygon_import_validation.spec.ts`
- `npm run e2e -- e2e/polygon_vertex_edit.spec.ts`
- `npm run e2e -- e2e/diagnostics_structural_metrics.spec.ts`
- `npm run e2e -- e2e/pub_visibility_i18n_readonly_flow.spec.ts`
- `curl http://localhost:8000/healthz`
- `curl http://localhost:4173/api/healthz`

---

## 6. 非目標

- E2Eのみで品質を担保しない（unit/integration/typecheckは必須）
- すべてのUI差分をフルシナリオで網羅しない（重要導線優先）

## 7. 利用者向けドキュメント整合要件（必須）

E2Eはアプリケーション動作に関する利用者向けドキュメントと**完全整合**していなければなりません。

1. `04_Documentation/e2e_testing.md` をE2E手順の正本（single source of truth）とする。
2. `04_Documentation/installation.md` / `04_Documentation/operations.md` / `CONTRIBUTING.md` / `02_Architecture/coding_standards.md` にあるE2E関連記述は、本書と同じコマンド・同じ受入基準・同じ代替経路を保つ。
3. E2Eの実行方法・受入基準・対象フローを変更したPRでは、上記文書を同一PRで更新する。
4. PR本文に、更新したE2E関連文書一覧を明記する。
5. 利用者向けドキュメントとの間で不足・不整合が見つかった場合は、まず「あるべき状態（期待挙動・受入基準・コマンド）」を明文化し、正本に合わせて同期更新する。
6. どちらが正かを容易に判断できない場合は、Issueを起票して論点・候補案・影響範囲を管理し、合意後に文書を更新する。

## 8. Compose経路検証ログの記録フォーマット（PR貼り付け用）

本節は、ADR-0019 の「第三選択: 例外記録」を実務運用できる形に固定する。

```md
### E2E verification log
- Preferred path (Compose): pass | blocked
  - command:
    - `docker compose up --build -d`
    - `docker compose ps`
    - `curl -fsS http://localhost:8080/api/health`
    - `PUT /api/docs/{doc_id}` + `GET /api/docs/{doc_id}`
    - `npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line`
  - result:
  - blocker (if blocked):

- Fallback path (SQLite): pass | fail | skipped
  - command:
    - `curl -fsS http://localhost:8000/healthz`
    - `curl -fsS http://localhost:4173/api/healthz`
    - `PUT /docs/{doc_id}` + `GET /docs/{doc_id}`
    - `npx playwright test e2e/i18n_locale_query_equivalence.spec.ts --reporter=line`
  - result:

### Unverified risk delta (Compose vs SQLite)
- R-01: PostgreSQL固有差分（型/制約/接続プール）
- R-02: web(Nginx)経由差分（/api リライトルール・CORS・圧縮）
- R-03: Composeヘルス連鎖（db healthy → api 起動）
- Mitigation / next action:
```

## 9. SQLite代替経路との差分リスク（可視化）

Compose未実行時は、以下を「未確認リスク」としてPRに残す。

| Risk ID | Composeでしか確認できない境界 | SQLite代替での状態 | 推奨フォローアップ |
| --- | --- | --- | --- |
| R-01 | PostgreSQL方言・マイグレーション適用差分 | 未確認 | Composeで docs roundtrip を再実行 |
| R-02 | `web(80)` 経由 `/api` ルーティング | 未確認 | `curl http://localhost:8080/api/health` を再実行 |
| R-03 | `depends_on: service_healthy` の起動順保証 | 未確認 | `docker compose ps` と `docker compose logs api` を取得 |
| R-04 | Composeネットワーク上の接続性（web↔api↔db） | 部分確認（ローカル2プロセスのみ） | Compose経路のPlaywright smoke+変更フローを再実行 |



## 10. FB-RM-RS-02 追記（E2E未実装理由の分析と是正）

### 10.1 未実装だった理由

- FB-RM-RS-02 初回実装では、`structural_metrics.test.ts` と `worker_golden.test.ts` で計算式・決定論を固定できたため、レビュー時に「worker/unit で十分」と判断してしまった。
- 一方で実際のユーザーフロー（Share Panel から bundle export → `diagnostics.md` 取得）を通す E2E が欠けており、`04_Documentation/e2e_testing.md` の「UIを伴う変更はE2E追加」を満たしていなかった。

### 10.2 是正内容

- `e2e/diagnostics_structural_metrics.spec.ts` を追加し、以下をブラウザ経路で検証する。
  1. `document.json` 差し替え後の bundle export に新規構造メトリクス行（`isolationRate`, `connectivityScore`, `degreeSkewRatio`）が含まれる。
  2. 同一入力で 2 回 export した `diagnostics.md` が一致する（決定論）。

### 10.3 再発防止

- diagnostics の表示/出力へ新規指標を追加するPRでは、unit/workerテストに加え、export経路を通すE2Eを必須チェック項目とする。
- PR本文の「未実施項目」に E2E省略理由を記載する場合は、次回是正タスク（Issueまたは同PR内追補）を必ず紐づける。

## 11. HIL-RS-02-A3 ドキュメント同期検証（仮運用 / docs-check）

A3では、実装E2Eに加えて文書同期の再現性を次のコマンドで確認する。

仮運用タグ（依存切断ルール）:
- `status=provisional`
- `evidenceType=mock-trace`
- `replaceOnNextSync=true`

前提（A1/A2整合）:
- RequirementID `HIL-RS-01-A1` の契約境界（Critique入力 / 再提案差分 / レビュー帰属）を参照済みであること。
- HIL-RS-02-A3 は A2実コード完成待ちをしないモック証跡同期であることを記録していること。
- Contract Keys（`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`）が運用文書側に明記されていること。
- Freeze Flags（`contractLinkLocked=true` / `sharedResourceFreeze=true`）が運用文書側に明記されていること。
- 契約正本 `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` を参照し、Issueメモとの差分がないこと。
- A2挙動（候補比較 / 人間入力 / 差分可視）と A3文書記述の対応表が `operations.md` に記録済みであること。
- `HilRsWorkflowPanel` の3導線ラベル/説明文と、運用文書の手順文言に差分がないこと。

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
rg -n "HIL-RS-01|HIL-RS-02-A3|ADR-0026|SafeMode|可逆|Critique|レビュー帰属|仮運用|モック証跡" 04_Documentation 01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md
rg -n "A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF|contractLinkLocked|sharedResourceFreeze" 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/e2e_testing.md
cd 03_Implement/frontend && pnpm -s vitest run src/ui/HilRsWorkflowPanel.test.ts src/domain/hil_rs_contract.test.ts src/domain/hil_rs_payload.test.ts src/domain/hil_rs_rediff_stub.test.ts
```

期待値:
- issue memo validator と unit test が成功する。
- 仮運用タグ（`status=provisional`, `evidenceType=mock-trace`, `replaceOnNextSync=true`）が3文書で確認できる。
- `04_Documentation` 側に HIL-RS-01 / ADR-0026 / SafeMode / 可逆 / Critique / レビュー帰属 の同期記述が存在する。
- strict mode例外運用について、D1〜D4固定値（承認順序/TTL、tenant最大2h、代理承認なし、48hレビュー+15m/60mエスカレーション）が `operations.md` と `security.md` で一致する。
- strict mode例外の状態語彙（`DraftRequest`→`ApprovalPending`→`Approved`→`ActiveException`→`RollbackPending`→`Closed`、未確定時 `StoppedForClarification`）が運用文書間で矛盾しない。
- HIL-RS workflow 関連の vitest（UI/contract/payload）が成功し、文書化した運用制約と実装の差分がない。
- `hil_rs_payload` 系の検証（未知tags→`no_articulable_reason`、空コメント+空tagsは未発行、`iteration>=1`）が運用記述と一致する。
- A3の非目標（SafeMode後退禁止・自動確定導線禁止）が文書内で確認できる。
- docs-check失敗時の自己修復は最大3回で打ち切り、`rollback_pending` を記録してProceedへ進めない。

注記:
- `01_Plans/issues/README.md` と `01_Plans/project-progress-dashboard.md` は統合フェーズまで編集しない。

## 8. Stream B（FB-P2B-01 / FB-P2B-02）同期E2E運用

実装確定済みの Similar-card 候補提示 / Manual assisted merge について、E2E観点を以下で固定する。

### 8.1 受入条件（最低）

- 候補収集は deterministic heuristic として表示され、AI自動確定を行わない。
- 候補グループで 4値 decision（`accept` / `partial` / `reject` / `defer`）を記録できる。
- read-only モードでは `Collect candidates` と decision ボタンが disabled となる。
- 不正入力（4値外 decision、契約ID不一致）は受け入れず、既存ログを破壊しない。

### 8.2 推奨コマンド（Frontend integration）

```bash
cd 03_Implement/frontend
pnpm -s vitest run src/ui/MergeSuggestionsPanel.test.ts src/domain/merge_suggestion_decisions.test.ts src/domain/stream_b_contract_handoff.test.ts
```

### 8.3 実装契約との照合（docs-check）

```bash
rg -n "CTR-2B-01-CANDIDATE-GROUP-V1|CTR-2B-02-DECISION-LOG-V1|Deterministic heuristic only|human-in-the-loop|accept|partial|reject|defer" \
  03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx \
  03_Implement/frontend/src/domain/merge_suggestion_decisions.ts \
  03_Implement/frontend/src/domain/stream_b_contract_handoff.ts \
  04_Documentation/operations.md 04_Documentation/e2e_testing.md 04_Documentation/security.md
```

### 8.4 フェイルセーフ

- contractVersion が `CTR-2B-01-CANDIDATE-GROUP-V1` / `CTR-2B-02-DECISION-LOG-V1` と一致しない場合は停止。
- 自動マージ確定を示す導線が追加された場合は停止し、A1契約へ差し戻す。

## 8.5 Stream G（CE3 Patch Workspace / Query Presets）E2E

CE3（`issue-CE3-patch-workspace-presets.md`）の導線確認は以下で固定する。

### 8.5.1 受入観点（最低）

- 候補比較ワークスペースで `adopt / hold / reject` を候補単位に操作できる。
- 部分採用（adopt）後に `Roll back last workspace decision` 1クリックで直前状態へ復旧できる。
- Preset（name/scope/depth/filters）保存後、`Run current preset` と保存済み `Run <name>` の双方で正規化Queryが再現される。
- 実行失敗時（候補未収集など）に、失敗メッセージと復旧導線（候補再収集＋rollback）が画面上で確認できる。
- E2Eは `/docs/doc_phase1_canvas` と `/ai/suggest-merges` をPlaywright routeで固定応答化し、backend非依存で決定論を維持する。

### 8.5.2 実行コマンド（Playwright）

```bash
cd 03_Implement/frontend
npx playwright test e2e/ce3_patch_workspace.spec.ts --reporter=line
```

### 8.5.3 docs-check（UI契約の固定）

```bash
rg -n "CE3 patch workspace|Roll back last workspace decision|Run current preset|Normalized query|Recovery path" \
  03_Implement/frontend/src/ui/PatchWorkspacePanel.tsx \
  03_Implement/frontend/e2e/ce3_patch_workspace.spec.ts \
  04_Documentation/e2e_testing.md
```


### 11.1 未確定事項とA1差し戻し条件（Proceed）

未確定事項（仮運用中）:
- A2実コード由来の最終監査イベント形式（`mock-trace` からの置換点）
- 差分レビュー画面の最終UI文言が `HilRsWorkflowPanel` 固定値から変更される可能性

A1差し戻し対象（検知時に停止）:
- Contract Keys / Freeze Flags の不一致
- `A1-ERROR-IF` 固定コード外の追加
- `traceKey` 必須条件の欠落
- PII-like field拒否または人間レビュー帰属必須の破れ

### 11.1.1 A3 docs-check の時系列実行手順

A3の検証は以下の固定順序で実施する（Read → CDC → Plan → Execute → Verify/Proceed）。

1. Read: `operations.md` / `security.md` / `e2e_testing.md` のD1〜D4固定値と状態語彙を棚卸し。
2. CDC: Context/Decision/Consequences を A3 issue に固定し、依存切断（A1/A2はRead-only参照）を確認。
3. Plan: AC/DoD不足ドラフトを合意し、`operations -> security -> e2e` の直列同期計画を確定。
4. Execute: 文書差分を反映（運用直列順 `operations -> security -> e2e`、ロールバック条件・2者承認・監査最小項目）。
5. Verify-1: `python 01_Plans/issues/validate_active_issue_memos.py` を実行。
6. Verify-2: `rg -n "DraftRequest|ApprovalPending|Approved|ActiveException|StoppedForClarification|RollbackPending|Closed|Security Officer|System Owner|Platform Operator"` で用語一致を検証。
7. Verify-3: `rg -n "承認TTL=4h|最大2h|代理承認なし|48h|15m|60m"` で固定値一致を検証。
8. Verify-4: `rg -n "HIL-RS-02 A3|Read|CDC|Plan|Execute|Verify/Proceed|Stream G" 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md` で issue 証跡を検証。
9. Verify/Proceed: 全検証成功時のみ `provisional_reapplied` として継続。

自己修復ルール（上限3回）:
- docs-check失敗時は、原因を1点ずつ修正して再実行する。
- 3回失敗した場合は `rollback_pending` を記録し、A3同期を停止する。

### 11.2 ロールバック検証（A3運用）

docs-checkで次のいずれかを検知した場合、A3同期は失敗として扱う。

- Contract Keys / Freeze Flags の欠落または表記不一致
- `traceKey` 必須条件の欠落
- PII-like field 拒否制約との矛盾

失敗時の標準処理:
1. `status=rollback_pending` を記録する。
2. 直前の `status=provisional` との差分を切り戻す。
3. 是正後に docs-check を再実行し、成功時のみ `provisional_reapplied` へ更新する。


## Stream F docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **CDC**: Context / Decision / Consequences を明文化し、分類結果（Move internal / Improve external）を固定する。
3. **Plan**: AC/DoD を先に定義し、docs-only スコープ（`03_Implement/**` 非変更）を明示する。
4. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
5. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
6. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## Phase 1-5 execution record (2026-04-16, DOC-OPS-05-06/07/08/09/10 scope)

### Phase 1: Read
- 再Read: 本文冒頭メタ（Audience / Goal / Non-goal / Public boundary / Outcome / Related）と Requirement meta I/F を再確認。
- スコープ確認: 本タスクは「当該Issue本文 + 当該Scope文書」のみを編集対象とする。

### Phase 2: Plan
- 再Read: 関連ADR（特に ADR-0019）と `01_Plans/documentation_quality.md` の参照導線を再確認。
- 計画: Read → Plan → Execute → Verify → Proceed を単一サイクルで実施し、記録を追記する。
- フェイルセーフ: Verify 失敗時の自己修復は最大3回まで、4回目相当は停止。

### Phase 3: Execute
- 再Read: 直前差分と本文の禁止事項（SafeMode後退、公開境界逸脱）を再確認してから編集。
- 実施内容: 本セクションを追記し、Phase運用・再Read・修復上限ルールを明文化。

### Phase 4: Verify
- 再Read: 追記後の本文を再読し、語彙ドリフト・参照不整合・体裁崩れの有無を確認。
- 実施: `git diff --check` と対象ファイルの目視確認を実施。
- 修復回数: 0回（3回超過なし）。

### Phase 5: Proceed
- 再Read: Verify結果とスコープ逸脱の有無を再確認。
- 判定: **Ready**（docs-only、許可範囲内、停止条件なし）。
- 継続条件: 後続差分でも同じ5Phase + 再Read + 修復上限3回を維持する。

## DOC-OPS-05 Stream G 前半フェーズ実行記録（2026-04-16）

- Classification確認: **Improve external**（再判定なし）
- フェイルセーフ固定: 用語ドリフト検知・固定値不一致検知・自己修復3回超過で停止（Hold）

### Phase 1: Read（対象ファイル再読）
- 本ファイルを再読し、Scope / Audience / Goal / Public boundary / Related の整合を確認。

### Phase 2: Plan（対象ファイル再読）
- 本ファイルを再読したうえで、docs-only の変更範囲と受入条件を固定。

### Phase 3: Execute（対象ファイル再読）
- 本ファイルを再読したうえで、分類方針（Move internal / Improve external）を維持して更新。

### Phase 4: Verify（docs-check、対象ファイル再読）
- 本ファイルを再読したうえで docs-check を実施。
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/e2e_testing.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。

#### CE3 検証記録（2026-04-19 / frontend）

- 対象Issue: `01_Plans/issues/issue-CE3-patch-workspace-presets.md`
- 実行結果:
  - unit: pass（`src/domain/ce3_patch_workspace.test.ts` / `src/ui/PatchWorkspacePanel.test.ts` / `src/domain/view/presets.test.ts`）
  - lint: pass（`npm --prefix 03_Implement/frontend run lint`）
  - e2e 1回目: browser binary 不足で fail
  - 自己修復1: `npm --prefix 03_Implement/frontend exec playwright install chromium`
  - e2e 2回目: `libatk-1.0.so.0` 不足で fail
  - 自己修復2: `npm --prefix 03_Implement/frontend exec playwright install-deps chromium`
  - e2e 3回目: pass（`--grep "CE3 patch workspace|Patch Workspace|Preset|rollback"`）
- 判定: 自己修復2回で収束（上限3回未満）。SafeMode後退・share/export露出追加なし。

#### CE3 検証記録（2026-04-19 / frontend / Stream F rerun）

- 対象Issue: `01_Plans/issues/issue-CE3-patch-workspace-presets.md`
- 実行結果:
  - unit: pass（`src/domain/ce3_patch_workspace.test.ts` / `src/ui/PatchWorkspacePanel.test.ts` / `src/domain/view/presets.test.ts`）
  - e2e 1回目: browser binary 不足で fail
  - 自己修復1: `npm --prefix 03_Implement/frontend exec playwright install chromium`
  - e2e 2回目: `libatk-1.0.so.0` 不足で fail
  - 自己修復2: `npm --prefix 03_Implement/frontend exec playwright install-deps chromium`
  - e2e 3回目: pass（`--grep "CE3 patch workspace|Patch Workspace|Preset|rollback"`）
- 判定: 自己修復2回で収束（上限3回未満）。SafeMode後退・share/export露出追加なし。
## Stream I mid-1 execution record（2026-04-19, DOC-OPS-05-06）

### Phase 1 Read（対象再読）
- 本文と対応Issue（DOC-OPS-05-06）を再読し、公開runbookの範囲を再確認。

### Phase 2 ADR CDC（対象再読）
- Context: E2E手順は公開運用正本として維持し、内部ログ文書との差分境界を明確化する必要がある。
- Decision: Classification **Improve external** を維持し、実行手順・受入条件・導線を優先して整備する。
- Consequences: 本書は公開向け手順に集中し、内部監査ログの詳細は verification log 側へ分離する。

### Phase 3 Plan（対象再読）
- AC: Audience/Goal/Public boundary/Outcome/Related と Go/No-Go を追跡可能にする。
- DoD: Read→ADR CDC→Plan→Execute→Verify→Proceed を記録する。

### Phase 4 Execute（対象再読）
- 本節を追記し、6Phase運用を固定。

### Phase 5 Verify（対象再読）
- `rg -n "Stream I mid-1|Phase 1 Read|Phase 2 ADR CDC|Phase 6 Proceed" 04_Documentation/e2e_testing.md`
- `git diff --check`

### Phase 6 Proceed（対象再読）
- 判定: **Ready**（公開runbookとしての整合を維持）。


## Stream H serial cycle（2026-04-19 / DOC-OPS-05-06）

### Phase 1 Read（参照整合）
- 対象Issueと本文を照合し、Classification=Improve external と公開境界（Audience / Goal / Non-goal / Outcome / Related）の整合を確認。
- 重複・矛盾は既存本文へ統合し、新規仕様追加は行わない。

### Phase 2 Plan（AC/DoDドラフト）
- AC: 公開境界メタの維持、Issue分類との一致、docs-onlyスコープ維持。
- DoD: Read→Plan→Execute→Verify→Proceed を記録し、検証コマンドを再現可能に残す。

### Phase 3 Execute（本文更新）
- 本節を追記し、Stream H の担当範囲であることを明示。
- 編集範囲は本ファイルのみとし、他ストリーム対象ファイルは非変更。

### Phase 4 Verify（docs-check + 参照リンク）
- `rg -n "Audience|Goal|Non-goal|Outcome|Related|Go/No-Go|Stream H serial cycle" 04_Documentation/e2e_testing.md`
- `git diff --check`
- 参照リンクは `Related` に記載された正本/Issue導線が有効であることを目視確認。

### Phase 5 Proceed/Stop
- 判定: **Ready**
- 停止条件: Verify自己修復が3回を超過、または未定義競合（要件キー未定義/契約衝突）を検知した場合は **Stop** とし、`01_Plans/issues/` に保留論点を記録する。


## Stream F HIL-RS-02-A3 docs-check sync log（2026-04-19）

- Phase 1 Read: `strict_mode_exception_approval_flow.md` / `operations.md` / `security.md` / `security_operational_guidelines.md` / 本書を再読。
- Phase 2 用語同期: `Security Officer / System Owner / Platform Operator` と状態語彙（`DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed` + `StoppedForClarification`）を確認。
- Phase 3 D1〜D4整合: `4h / 2h / 代理承認なし / 48h + 15m/60m` の固定値一致を確認。
- Phase 4 Verify: issue memo validator、語彙/固定値 `rg`、`git diff --check` で docs-check pass。
- Phase 5 Proceed: **Ready**。統合ストリームには「不整合再発時は3回修復上限、超過時停止」を引き継ぐ。

## Stream E serial cycle（2026-04-20 / DOC-OPS-05後半 docs-only）

### Phase 1 Read
- 本文先頭メタ（Classification / Audience / Goal / Non-goal / Public boundary / Outcome / Related）を再確認。

### Phase 2 Plan
- 変更は docs-only に限定し、Plan→Execute→Verify→Proceed の固定順序で進める。
- Verify失敗時の自己修復は最大3回、4回目相当は停止する。

### Phase 3 Execute
- 本文の公開境界・導線を維持し、safeMode既定ON／漏えい防止後退禁止を再確認。

### Phase 4 Verify
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Outcome|Related" 04_Documentation/e2e_testing.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**。
- 次担当へ: 致命的矛盾（上位文書不整合・安全境界後退・自己修復3回超過）を検知した場合は停止してIssueへ記録する。
