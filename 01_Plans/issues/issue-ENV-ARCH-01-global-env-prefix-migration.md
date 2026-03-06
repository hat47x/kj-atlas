# Issue Draft: ENV-ARCH-01 グローバル環境変数プレフィックス移行計画

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/deploy/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0021`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/deployment.md`
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
