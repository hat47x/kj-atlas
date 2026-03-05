# ADR-0021: 環境変数のグローバルプレフィックス移行方針

- Status: Proposed
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
3. **全ランタイムキーをプレフィックスへ段階移行**（推奨）

## Decision

**全ランタイム環境変数を `KJ_ATLAS_*` プレフィックスへ段階移行する。**

採用理由:

- 共存環境での衝突回避を設計で保証できる。
- デプロイ/監査でアプリ識別が明確になる。
- 段階移行（alias許容期間 + 最終撤去）により運用中断リスクを下げられる。

設計原則:

1. 最終正規キーは `KJ_ATLAS_*` とする。
2. 移行期間は「旧キー + 新キー」の二重受理を許容し、新キー優先で評価する。
3. 期限到来後に旧キー受理を廃止する（deprecation期限を明示）。
4. `runtime_parameter_registry.md` を正本として、移行表（旧→新）と期限を一元管理する。

非目標:

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

移行で必要な対応:

1. 実装: `settings.py` で新キー受理 + 旧キー互換受理（期限付き）。
2. デプロイ: `docker-compose.yml` / サンプル `.env` を新キーへ更新。
3. 文書: Architecture / Ops / Installation / Security の参照キー更新。
4. 検証: 単体テストで優先順位（新キー優先）と互換期限を固定。

## Traceability

- Related: `02_Architecture/runtime_parameter_registry.md`
- Related: `02_Architecture/deployment.md`
- Related: `03_Implement/backend/src/kj_atlas_api/settings.py`
- Related: `THREAT_MODEL.md`
- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`
