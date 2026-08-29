# ADR-0021: 環境変数のグローバルプレフィックス移行方針

- Status: Accepted
- Date: 2026-03-05
- Deciders: Project Maintainers
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/deploy/`, `04_Documentation/`

## Context

同じサーバや CI 環境では、kj-atlas 以外のアプリケーション、データベース、ビルドツールも環境変数を利用する。

`DATABASE_URL`、`API_KEY`、`LLM_PROVIDER` のような一般名を公開設定として使うと、次の問題が起きやすい。

- 別アプリケーションの設定を誤って kj-atlas が読み込む。
- 運用者がどのアプリの設定値か判断しにくい。
- 公開設定、第三者コンテナ内部名、ビルドツール内部名の境界が曖昧になる。
- 古い互換キーが残り、意図しない外部連携や接続先変更につながる。

そのため、kj-atlas が利用者・運用者に公開する環境変数は、アプリケーション固有の名前空間へ統一する必要がある。

## Decision

kj-atlas の公開環境変数は、すべて例外なく `KJ_ATLAS_` で始まる名前だけを正規キーとして扱う。

### 規則

1. 利用者・運用者が設定する公開キーは `KJ_ATLAS_*` のみとする。
2. 旧キー、短縮キー、互換キーは公開設定として受け付けない。
3. 新旧キーの同時指定を許容する移行期間は設けない。
4. 旧キーを自動変換する deprecation window は設けない。
5. 新しい環境変数を追加する場合も、必ず `KJ_ATLAS_` で始める。

### 代表例

| 目的 | 正規キー |
| --- | --- |
| DB 接続先 | `KJ_ATLAS_DATABASE_URL` |
| LLM provider | `KJ_ATLAS_LLM_PROVIDER` |
| large-scale LLM 昇格許可 | `KJ_ATLAS_LLM_ESCALATION_ENABLED` |
| API key | `KJ_ATLAS_API_KEY` |
| frontend の API base path | `KJ_ATLAS_FRONTEND_API_BASE` |
| Docker Compose の web 公開 port | `KJ_ATLAS_WEB_PORT` |
| Docker Compose の PostgreSQL 入力 | `KJ_ATLAS_POSTGRES_DB`, `KJ_ATLAS_POSTGRES_USER`, `KJ_ATLAS_POSTGRES_PASSWORD` |

### Private Adapter Boundary

第三者コンテナやビルドツールが内部的に別名を要求する場合がある。

この場合でも、利用者・運用者に公開する kj-atlas の入力は `KJ_ATLAS_*` のままとする。内部名への写像は private adapter boundary として扱い、公開設定とはみなさない。

例:

- Docker Compose の PostgreSQL image へ渡す `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- frontend build tool の内部処理で使われる互換 shim

これらは利用者が直接設定する kj-atlas の公開キーではない。公開文書では、正規キーと内部写像の境界を明示する。

## Non-Goals

- 既存の安全既定値を変更しない。
- SafeMode、共有前確認、LLM opt-in、audit 連携、access control の方針をこの ADR では変更しない。
- 第三者コンテナ内部から非 `KJ_ATLAS_*` 名を完全に排除する deployment 再設計は、この ADR の範囲外とする。採用する場合は別 ADR で扱う。

## Three-Element Verification（ADR-0067 遡及適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | 同一サーバやCI環境では他アプリケーションも環境変数を利用し、`DATABASE_URL`等の一般名を公開設定にすると別アプリ設定の誤読込・所有境界の曖昧化が起きる。kj-atlasの公開環境変数をアプリ固有の名前空間に統一する | 機能: 新規環境変数も必ず`KJ_ATLAS_`で始める。データ: 設定値の所有境界を明確にし誤接続・誤送信・別アプリ設定の混入を減らす |
| **データ設計** | 公開キーは`KJ_ATLAS_*`のみ。旧キー・短縮キー・互換キーは公開設定として受け付けない。新旧キー同時指定の移行期間・旧キー自動変換のdeprecation windowは設けない | 業務: 運用者がどのアプリの設定値か判断しやすくする。機能: 古い互換キーが意図しない外部連携や接続先変更につながらないようにする |
| **機能設計** | 第三者コンテナやビルドツールが内部的に別名を要求する場合はprivate adapter boundaryとして扱い、公開入力は`KJ_ATLAS_*`のまま内部名へ写像する | 業務: 第三者コンテナ内部から非`KJ_ATLAS_*`名を完全に排除するdeployment再設計は別ADRの範囲。データ: runtime_parameter_registry.mdと公開文書で`KJ_ATLAS_*`のみを利用者向けキーとして記載 |

## Consequences

期待される効果:

- 設定値の所有境界が明確になる。
- 誤接続、誤送信、別アプリ設定の混入を減らせる。
- 公開文書、runtime registry、backend settings、Compose 入力の対応を監査しやすくなる。

制約:

- 旧キーを使っていた環境は起動時に修正が必要になる。
- 設定変更時は、実装、設計文書、公開文書、テストを同時に更新する必要がある。
- 第三者コンテナ内部名を公開設定と誤読しないよう、文書で private adapter boundary を維持する必要がある。

## Verification Expectations

この ADR を維持するため、次を継続的に確認する。

- backend settings が `KJ_ATLAS_*` の validation alias のみを公開入力として受け付ける。
- frontend build が `KJ_ATLAS_FRONTEND_API_BASE` を正規キーとして扱う。
- Docker Compose の利用者入力が `KJ_ATLAS_*` のみである。
- `04_Documentation/configuration.md` と `02_Architecture/runtime_parameter_registry.md` が同じ公開キー集合を説明している。
- 旧キー名は、拒否対象、履歴説明、private adapter boundary の説明としてのみ現れる。

## Separation of Concerns

この ADR は、長期的に維持する意思決定を記録する。

実装作業、検証ログ、Done 判定、残タスクは issue memo で管理する。

- Execution tracking: `01_Plans/issues/done/issue-ENV-ARCH-01-global-env-prefix-migration.md`
- Runtime contract tracking: `01_Plans/issues/done/issue-ENV-CONFIG-DRIFT-01-runtime-configuration-contract-alignment.md`
- Policy SSOT: `02_Architecture/runtime_parameter_registry.md`

## Traceability

- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `01_Plans/adr/ADR-0029-third-party-runtime-env-boundary.md`
