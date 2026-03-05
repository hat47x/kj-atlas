# ADR-0021: 環境変数のグローバルプレフィックス移行方針

- Status: Accepted
- Date: 2026-03-05
- Deciders: Project Maintainers
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/deploy/`, `04_Documentation/`

## Context

同一サーバ上で複数アプリが共存する運用では、`DATABASE_URL` や `API_KEY` のような一般名キーが他アプリと衝突し得る。
この衝突は次の実害を生む。

- 誤った環境値の注入（誤接続・誤送信・誤認可）
- デプロイ自動化時の変数上書き
- 運用監査時の識別困難（どのアプリの値か判別不能）

現行 `runtime_parameter_registry.md` は命名規約を整理したが、グローバル一意性（アプリ識別子プレフィックス）までは担保していない。
そのため、実装変更を伴ってでもプレフィックス移行を計画する判断が必要になった。

主要選択肢:

1. **現状維持**（プレフィックスなし）
2. **新規キーのみプレフィックス**（既存キーは据え置き）
3. **全ランタイムキーをプレフィックスへ段階移行**（採用）

## Decision

**全ランタイム環境変数を `KJ_ATLAS_*` プレフィックスへ段階移行する。**

### 判定可能な移行契約（ENV-ARCH-01の着手前提）

1. 正規キーは `KJ_ATLAS_*` とする。
2. 旧キー（プレフィックスなし）は互換aliasとして受理する。
3. **新旧同時指定時は新キー優先**とする。
4. 旧キー互換の終了期限（deprecation）は **`2026-09-30 23:59:59 UTC`** とする。
5. 移行表（旧→新）と期限管理は `runtime_parameter_registry.md` をSSOTとする。

### 実装・運用の適用範囲

- settings: `03_Implement/backend/src/kj_atlas_api/settings.py`
  - 新キー受理 + 旧キー互換受理 + 新キー優先。
- deploy: `03_Implement/deploy/docker-compose.yml`
  - 例示キーを新キーへ統一。
- docs: `02_Architecture/*`, `04_Documentation/*`, `03_Implement/backend/README.md`
  - 参照キーを新キーへ統一し、互換期限を記載。
- tests:
  - 新キー優先・旧キー互換を単体/結合テストで固定。

### 非目標

- 本ADR単体で即時に全実装を置換しない。
- プレフィックス以外の設定体系再設計（設定ファイル方式全面変更など）は扱わない。
- 既存安全契約（SafeMode優先、PII最小化、監査最小化）を変更しない。

## Consequences

期待効果:

- 環境変数衝突事故の予防。
- IaC/CI/CD の変数管理がアプリ単位で明確化。
- 運用・監査ドキュメントの可読性向上。

副作用/制約:

- 移行期間中は二重キー管理の複雑性が増える。
- 実装・ドキュメント・Compose・テストの同時更新が必要。
- 旧キー依存の外部運用スクリプトに影響が出るため、告知と移行猶予が必須。

ENV-ARCH-01着手判定チェックリスト:

- [x] `Context / Decision / Consequences` が判定可能な文で明記されている。
- [x] 旧→新キー移行表とdeprecation期限の正本が `runtime_parameter_registry.md` に存在する。
- [x] 下流で必要な契約（settings / compose / docs / tests）がTraceabilityで追跡できる。

## Traceability

- Related: `02_Architecture/runtime_parameter_registry.md`
- Related: `03_Implement/backend/src/kj_atlas_api/settings.py`
- Related: `03_Implement/deploy/docker-compose.yml`
- Related: `03_Implement/backend/tests/test_settings_env_prefix_migration.py`
- Related: `03_Implement/backend/README.md`
- Related: `04_Documentation/operations.md`
- Related: `04_Documentation/security.md`
- Related: `02_Architecture/enterprise_architecture.md`
- Related: `THREAT_MODEL.md`
- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`
