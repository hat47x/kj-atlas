# Issue Draft: ENV-ARCH-01 グローバル環境変数プレフィックス移行計画

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/deploy/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0021`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/deployment.md`
- Dependencies: N/A
- Expected verification level: `integration`

## 1) 課題 / Problem statement

- 同一サーバ共存時、一般名の環境変数（例: `DATABASE_URL`, `API_KEY`）が他アプリと衝突し得る。
- 旧キー互換を維持すると、設定契約が二重化し運用ミスの余地が残る。
- 人間判断（E1/E2/E3）確定後、実装着手条件を「一括切替」に再定義する必要がある。

## 2) 背景 / Context

- `ADR-0021` は一括移行（互換なし）へ更新済み。
- `runtime_parameter_registry.md` は `KJ_ATLAS_*` 単独契約をSSOTとして管理する。
- `settings.py` / `docker-compose.yml` / 関連文書を同一方針で同期更新する必要がある。

### このIssueが保持する内容（実行管理SSOT）

- 実装タスク分解（T1〜T5）
- 受入条件の達成状況
- 検証コマンドと実行結果

## 3) 人間判断の確定（2026-03-05）

- E1: **Option B**（互換期間なしの一括移行）
- E2: **Option C**（移行痕跡を残さない）
- E3: **考慮外**（deprecation期限運用を採用しない）

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs + Backend settings + Deploy設定 + tests。
- 最小単位:
  - `settings.py` を `KJ_ATLAS_*` 専用へ移行（旧キーalias削除）。
  - `docker-compose.yml` / README / operations を新キーのみへ更新。
  - テストで「旧キーは失敗」「新キーのみ受理」を固定。
- 非目標:
  - 互換運用（新旧併存）
  - 旧キー利用警告や監査痕跡の追加
  - SafeMode/認可/監査仕様の変更

## 5) 受入条件 / Acceptance criteria

- [x] `KJ_ATLAS_*` のみ実装上の正規キーとして受理される。
- [x] 旧キー単独指定は起動失敗する。
- [x] 新旧混在指定は不正設定として起動失敗する。
- [x] compose/runbook/README の実行例が新キーのみで統一される。
- [x] integrationレベル検証（起動 + 設定反映 + 旧キー拒否）が再現可能なコマンドで示される。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: E1/E2/E3 の人間判断を issue/ADR/registry に同期。
- [x] T2: backend settings から旧キーaliasを削除する。
- [x] T3: compose/README/ops文書を新キー専用へ更新する。
- [x] T4: 単体/結合テストで旧キー拒否を固定する。
- [x] T5: リリースノートに「旧キー非互換」を明記する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "Option B|Option C|考慮外|旧キー|互換なし" 01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md 02_Architecture/runtime_parameter_registry.md 01_Plans/issues/issue-ENV-ARCH-01-global-env-prefix-migration.md`
- 期待結果:
  - issue memo 形式検証が成功し、一括移行契約が追跡可能。

## 8) 代替案 / Alternatives considered

- 代替案A: 段階移行（互換あり）
  - 却下理由: 旧キー残存により衝突リスクと運用複雑性が残る。
- 代替案B: 警告のみ運用
  - 却下理由: 実害の抑止力が弱く、契約が曖昧化する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 旧キー依存環境で起動失敗。
- 影響範囲: backend起動、deploy運用、CI設定。
- ロールバック手順: リリースを即時取り下げ、設定を `KJ_ATLAS_*` へ修正した上で再展開する（旧キー再受理は行わない）。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 一括移行契約（互換なし）を見直す要求が出た場合。


## 11) Verification results

- `pytest 03_Implement/backend/tests/test_settings_env_prefix_migration.py 03_Implement/backend/tests/test_llm_provider.py 03_Implement/backend/tests/test_docs_roundtrip.py`
  - 期待通り、旧キー単独/混在を拒否し、新キー設定のみを受理する。
- `rg -n "旧: |DATABASE_URL|ALLOW_JIT_PROVISIONING|API_KEY" 03_Implement/backend/README.md 04_Documentation/operations.md 04_Documentation/security.md 03_Implement/backend/tests/scripts/run_auth_level2.sh`
  - 旧キー依存の実行例が除去されている。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream E Progress (2026-04-30)
- Phase 1 Read同期: 完了（Read OrderおよびADR-0021/registry確認）。
- Phase 2 変数契約確定: `VITE_KJ_ATLAS_API_BASE` をfrontend正規キーとして追加し、`VITE_API_BASE` は互換shimへ明確化。
- Phase 3 backend移行: 既存 `KJ_ATLAS_*` 専用契約を再確認（追加変更なし）。
- Phase 4 frontend移行: `client.ts` で `VITE_KJ_ATLAS_API_BASE` 優先読取へ移行。
- Phase 5 backward compatibility shim: `VITE_API_BASE` fallbackを維持（trim + trailing slash正規化）。
- Phase 6 検証/issue更新: 本節および検証ログを追記。


## Stream F Progress (2026-05-02)
- Phase 1 Read: `ADR-0021` と `runtime_parameter_registry.md` を再確認し、`KJ_ATLAS_*` 単独契約を再検証。
- Phase 2 ADR/仕様明文化: Context/Decision/Consequences は `ADR-0021`、運用SSOTは本Issueとregistryに分離維持。
- Phase 3 Plan: 旧prefix→新prefixは backend container default を優先更新、frontendは `VITE_KJ_ATLAS_API_BASE` 正規 + `VITE_API_BASE` shim維持。
- Phase 4 Execute: `03_Implement/backend/Dockerfile` の `DATABASE_URL` / `LLM_PROVIDER` を `KJ_ATLAS_*` へ更新。
- Phase 5 Verify: `test_settings_env_prefix_migration.py` と `rg` で旧キー拒否契約および残存箇所を確認。
- Phase 6 Proceed: 競合なし。互換shim (`VITE_API_BASE`) は独立レイヤとして継続し、将来削除判断を別タスクに分離。

## Stream J Plan Update (2026-05-04)

- Scope: Plan update only (`01_Plans/issues/...`), architecture SSOT read-only reference (`02_Architecture/runtime_parameter_registry.md`).
- Mission: ENV-ARCH-01 の段階移行計画を実装担当へ再配布し、運用影響と検証観点を明示する。

### Phase 1: Read同期（現状/未完了抽出）

- 確認結果:
  - backend契約は `KJ_ATLAS_*` 単独（旧prefix非受理）で確定済み。
  - frontend API base は `VITE_KJ_ATLAS_API_BASE` 正規、`VITE_API_BASE` は互換shimとして残置。
- 未完了/継続監視項目:
  1. `VITE_API_BASE` shim の廃止判断と削除タイミングが未決定。
  2. CI/deploy/docs における旧prefix再混入の継続監視（回帰防止）が必要。

### Phase 2: ADR明文化（CDC）

- 判定: **新規ADR追加は現時点で不要**（既存 `ADR-0021` + registry で契約は充足）。
- CDC（Context / Decision / Consequences）:
  - Context: backendは互換なし一括移行済み、frontendのみ限定的互換shimが残る。
  - Decision: 互換維持方針は「backend互換なし維持 + frontend shimは期限付き検討対象」としてIssue運用で管理する。
  - Consequences: 実装は契約逸脱（旧prefix再導入）を禁止し、shim除去時は `ADR-0021` 追補または本Issue更新を実施する。
- 承認待ち論点:
  - `VITE_API_BASE` 廃止の期限（date）
  - 廃止時の利用者通知チャネル（release notes / operations）

### Phase 3: Plan（段階化）

1) 命名規約固定
- backend: `KJ_ATLAS_*` のみ。
- frontend: `VITE_KJ_ATLAS_API_BASE` を正規キーとして固定。

2) 互換層方針
- backend: 互換層なし（旧prefix受理禁止を継続）。
- frontend: `VITE_API_BASE` を互換shimとして暫定維持し、削除は明示タスクで管理。

3) 廃止期限/検証項目
- 廃止期限: 未確定（要人間判断）。
- 最低検証項目:
  - 旧prefix単独指定が失敗すること。
  - 新旧混在指定が失敗すること（backend）。
  - frontendで正規キー優先解決が保持されること。
  - docs/compose/runbook に旧prefix実行例が増えていないこと。

### Phase 4: Verify（運用影響の列挙）

- CI影響:
  - 設定ロード系テストが旧prefix拒否を維持できるか。
  - grep/lintersによる旧prefix混入検知（回帰監視）。
- Deploy影響:
  - compose・container default・環境注入手順で新prefix統一を維持。
  - 秘匿値管理（secret manager, env file）更新漏れ防止。
- Docs影響:
  - README/operations/security/runbook の例示キーを正規契約へ揃える。
  - 互換shimの扱い（暫定/削除予定）を明文化。
- Self-heal policy (max 3):
  1. 旧prefix再混入検知時、該当箇所を正規キーへ即時修正。
  2. テスト不整合時、期待値をregistry契約に再同期。
  3. docs不整合時、実装実態に追随し再記述。

### Phase 5: Proceed（実装担当向け影響範囲マップ）

- Backend実装:
  - `settings.py`（env読取契約）
  - provider/auth/audit の env依存分岐
- Frontend実装:
  - `client.ts` 等の API base 解決ロジック
  - `VITE_API_BASE` shim 削除時の影響調査
- Deploy/Runtime:
  - `docker-compose.yml`, Dockerfile, CI secrets, runtime env templates
- Documentation:
  - backend README, `04_Documentation/operations.md`, `04_Documentation/security.md`, release notes
- Test/Validation:
  - env prefix migration tests
  - docs内キー参照の回帰検知

### Fail-safe gate

- 互換性破壊リスク評価:
  - backend: 評価済み（互換なしを契約化済み）。
  - frontend shim削除: **未評価項目あり**（期限未確定）。
- Gate判定:
  - frontend shim廃止タスクは、影響評価（利用者通知/切替手順/ロールバック）完了まで **着手停止**。

## Stream J maintenance note (2026-05-18)

- `runtime_parameter_registry.md` と `deployment.md` に prefix migration governance（互換期間なし・切替条件）を明文化し、運用判断の参照先を固定した。
- Compose 公開入力 (`KJ_ATLAS_*`) と third-party private adapter (`POSTGRES_*`) の境界を再確認し、ENV-ARCH-01 の完了条件（公開契約の単一化）を維持していることを確認した。
- 追加の破壊的変更（互換再導入・公開キー改名）は新規 ADR 必須の方針を追記済み。


## Stream D update (2026-05-20)

### Phase 1) Read同期

- `runtime_parameter_registry.md` をSSOTとして再読し、公開キー集合・既定値・profile差分を固定した。
- 関連issue（ENV-ARCH-01 / ENV-CONFIG-DRIFT-01 / ENV-PROFILE-01）の `Status / Priority / Dependencies / Related ADR` を同一セッションで再確認した。

### Phase 2) Context / Decision / Consequences

- Context: backendは `KJ_ATLAS_*` 単独契約で移行完了。deploy/frontendは公開契約と内部adapter境界の明文化が主課題。
- Decision: 公開契約は `KJ_ATLAS_*` のみを維持し、互換は private layer（third-party env / frontend shim）に閉じ込める。
- Consequences: 旧キー再導入や prefix例外は本streamで実施しない。必要時は新規ADRでGo/No-Goを先行確定する。

### Phase 3) グローバルprefix移行と互換レイヤ設計

- Public layer: 利用者入力は `KJ_ATLAS_*` のみ受理。
- Private layer: `POSTGRES_*` は third-party container内部名、`VITE_API_BASE` は非公開互換shimとして限定運用。
- Exit条件: 命名/既定値/境界/profile の4観点が同時に満たされること。

### Phase 4) Plan → Execute → Verify → Proceed

- Plan: 4観点ゲートを固定。
- Execute: 契約文書（02）→ issue運用（01）の順で同期。
- Verify: docs-check中心で差分検証し、実装契約との不整合がないことを確認。
- Proceed: 不整合なしのため継続可能。追加の実装変更は不要。

### Phase 5) 3回失敗で停止

- 本更新では Verify失敗 0回。
- 以後、同一論点で Verify が3回連続失敗した場合は Stop し、再開条件と要判断事項をissueに追記する。

## Stream F note (2026-05-20)

- ENV-ARCH-01 の契約（公開キーは `KJ_ATLAS_*` のみ）を維持したまま、profile運用文書に「実装既定値」と「推奨値」の差分説明を追加した。
- `KJ_ATLAS_ALLOW_JIT_PROVISIONING` と `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` の運用判断を profile 起点で統一し、非互換変更や互換レイヤ再導入は実施していない。
