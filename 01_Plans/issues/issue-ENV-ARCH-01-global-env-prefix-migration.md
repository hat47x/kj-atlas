# Issue Draft: ENV-ARCH-01 グローバル環境変数プレフィックス移行計画

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
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
