# Issue: ENV-COMPOSE-01 Compose実行時設定の配送と実効確認を一致させる

> 公開設定キーが存在することと、標準Composeの`api`コンテナへ届くことは別である。設定したつもりの安全機能が既定値のまま動く状態を防ぐ。

- Type: Bug / Security / Documentation
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Deployment contributor
- Scope: `03_Implement/deploy/docker-compose.yml`, `03_Implement/deploy/docker-compose.*.yml`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/deployment.md`, `04_Documentation/configuration.md`, `04_Documentation/installation.md`, `04_Documentation/operations.md`, `04_Documentation/security.md`, `04_Documentation/local_llm_ops_guide.md`, deployment/docs contract tests
- Related ADR/Spec: `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`, `01_Plans/adr/ADR-0029-third-party-runtime-env-boundary.md`, `01_Plans/issues/issue-ENV-CONFIG-DRIFT-01-runtime-configuration-contract-alignment.md`, `01_Plans/issues/issue-ENV-PROFILE-01-runtime-profile-guidance.md`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/deployment.md`
- Expected verification level: integration

## 課題

`configuration.md`はbackendが受け付ける37個の`KJ_ATLAS_*`を公開設定として列挙し、API key、local/large-scale LLM、audit HTTP、外部PDPの`export`例を示す。`operations.md`と`security.md`も標準Composeを起点に同じ設定の確認を求める。

しかし、標準`docker-compose.yml`の`api.environment`がホストから配送するbackend設定は次の2個だけである。

- `KJ_ATLAS_DATABASE_URL`
- `KJ_ATLAS_LLM_PROVIDER`

`settings.py`の37個の`validation_alias`との差分は35個ある。代表的な未配送キーと実際の影響は次のとおり。

| 未配送キー | 運用者の意図 | Compose上の実効状態 |
| --- | --- | --- |
| `KJ_ATLAS_API_KEY` | `/healthz`以外を保護する | 未設定のままでAPI key保護が有効にならない |
| `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` | 未登録identityを拒否する | 実装既定`true`のまま |
| `KJ_ATLAS_LOCAL_LLM_BASE_URL` / `MODEL` | local providerへ接続する | provider名だけ届き、接続情報は届かない |
| large-scale opt-in / allowlist / endpoint群 | 明示許可した宛先だけへ接続する | 既定の無効・未設定のまま |
| audit enable / transport / endpoint / key群 | 監査イベントを指定先へ連携する | `false` / `noop`のまま |
| access-control adapter / fail-safe / endpoint群 | 外部PDPと障害時制御を使う | `noop` / `read_only`のまま |

既定値が外部接続を無効にする点は安全側だが、API keyやJIT禁止のように「保護を有効にした」という運用者の期待に対してはfail-openになる。`docker compose config`は補間されたComposeモデルを示すだけで、文書に書かれた全設定が`api`へ配送されたことを保証しない。

さらに、Compose内の`localhost`はホストではなく`api`コンテナ自身を指す。`local_llm_ops_guide.md`等の`http://localhost:8001`例は、backend直接起動とCompose起動のどちら向けかを区別していない。

完了済み`ENV-CONFIG-DRIFT-01`はComposeの公開入力を7個、`api.environment`を2個として確認したが、backend公開キーの配送完全性や実効プローブを受入条件に含めていない。本Issueはその後続であり、完了済みIssueを再オープンしない。

## 対応方針

### 1. 設定キーと実行面の対応表を正本化する

37個のbackend公開キーを少なくとも次で分類し、`runtime_parameter_registry.md`または`deployment.md`に一度だけ置く。

- backend直接起動で利用可能
- 標準Composeで配送する
- 特定overlay/profileだけで配送する
- 利用者が変更しない固定安全契約
- secretか、通常値か
- 設定後に確認する非秘密プローブ

「公開キーだが標準Composeでは未対応」の状態を暗黙に残さない。Compose向け手順に掲載するキーは必ず配送し、配送しないキーはdirect-onlyまたはunsupportedと明記する。

### 2. Composeの配送を明示的allowlistにする

- 標準Composeでサポートすると決めたbackendキーを`api.environment`または目的別overlayへ明示的に追加する。
- ホスト環境全体や任意の`KJ_ATLAS_*`を無差別に転送しない。
- 未設定のoptional値を空文字へ変換して実装既定を壊さない。
- password、API key、bearer tokenをComposeファイル、Git、CI出力へ固定しない。秘密配送方式を非秘密設定と区別する。
- base Composeをevaluation専用とするキーは、enterprise-productionで利用可能と誤認させない。

どのCompose表現を使うかは実装時に小さく選べるが、「文書でCompose利用可能としたキーはコンテナへ届く」「未設定時は既定値を維持する」「秘密値を出力しない」を固定条件とする。

### 3. 起動面ごとに例を分ける

`configuration.md`、`security.md`、`local_llm_ops_guide.md`の例を次に分ける。

- backend直接起動
- 標準Compose
- repository同梱overlay
- 組織独自のproduction overlay / secret manager

endpoint例はnetwork namespaceを明記する。ホスト上のサービス、Compose内service、別ホストを区別し、`localhost`をそのまま転記させない。

### 4. 値を漏らさず実効状態を確認する

起動成功だけで設定反映済みとしない。代表設定を機能で確認する。

- API key設定時: `/healthz`は200、キーなしの保護対象APIは401、正しいキーでは成功。
- JIT禁止時: 未登録identityが作成されない。
- local LLM overlay: provider transportが同梱stubへ到達する。
- external接続: 実サービスへ送らず、test doubleでendpoint、timeout、fail-safeを確認する。
- audit: secret本文を出力せず、送信有無と失敗時挙動を確認する。

診断やCIには秘密値そのものを表示せず、設定済み/未設定、選択profile、接続先hostのマスク済み表現、機能probe結果だけを残す。

## 実施しないこと

- 全ホスト環境変数をコンテナへ転送すること。
- `.env`、API key、token、passwordの実値をcommitまたはCI logへ出すこと。
- API keyを同梱SPAへ埋め込むこと。
- 外部LLM、audit endpoint、PDPへCIから実通信すること。
- 設定配送の修正に便乗してSafeMode、share/export、import、AI proposal-onlyの意味を変えること。
- `ENV-CONFIG-DRIFT-01`や`ENV-PROFILE-01`へ新しい実行ログを追記すること。

## 実行順序

1. Deployment contributorが37キーの実行面・secret・probe matrixを作る。
2. Security contributorがAPI key、JIT、audit、PDPのfail-open/fail-closed期待を確認する。
3. Compose担当が明示的allowlistと必要最小のoverlayを実装する。
4. Documentation contributorが起動面別の例とnetwork namespaceを同期する。
5. QA contributorが静的集合比較と代表機能probeを追加する。

## 受入条件

- [ ] 37個のbackend公開キーすべてに、direct / base Compose / overlay / fixedの対応とsecret区分がある。
- [ ] Compose向けと記載されたキーが`api`へ配送され、direct-onlyのキーをCompose例で案内しない。
- [ ] `KJ_ATLAS_API_KEY`と`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`が標準または明示profileで機能的に確認できる。
- [ ] local/large-scale LLM、audit、外部PDPは、必要な関連キーが一組として届くか、そのCompose profileではunsupportedと明記される。
- [ ] optional設定の未指定が空文字へ変わらず、現在の安全な既定値を維持する。
- [ ] secret値がCompose定義、Git差分、テスト出力、診断出力に現れない。
- [ ] host、Compose service、別hostのendpoint例が区別され、Compose内`localhost`の誤用がない。
- [ ] 静的契約テストがsettings公開キー、registry分類、Compose mapping、公開文書のsurface表記のdriftを検出する。
- [ ] Docker integrationがAPI key、JIT禁止、LLM stub、および外部接続test doubleの代表経路を値非表示で確認する。
- [ ] SafeMode既定ON、provider=`none`、audit HTTP既定OFF、external PDP既定`noop`、share/export/import境界を変更しない。

## 検証計画

- 静的集合比較:
  - `settings.py`の`validation_alias="KJ_ATLAS_*"`集合。
  - runtime registryのbackend公開キー集合。
  - base Composeとoverlayの`api.environment`集合。
  - 公開文書の起動面annotation。
- Compose構文:
  - `docker compose -f 03_Implement/deploy/docker-compose.yml config`
  - secret値を出力・保存する検証方法は使わない。
- 機能probe:
  - API keyの200/401、JIT禁止、LLM stub、audit/PDP test double。
- repository gate:
  - `python 01_Plans/docs_check.py`
  - backend/deploymentの近接テスト。
  - `git diff --check`

Dockerを利用できない環境では静的検査だけを成功扱いにし、integration未実施理由とDocker-capable hostでの再開条件を記録する。

## リスクとロールバック

- 配送キー追加により、利用者のシェルに残った値が初めて有効になる可能性がある。変更前にeffective config差分を示し、外部接続系は明示profile/overlayへ分ける。
- 不具合時は該当overlayまたは個別mappingを戻し、文書をdirect-onlyへ戻す。安全既定を緩めて互換を取らない。
- 公開profileの意味や秘密配送方式を長期契約として変更する必要が生じた場合だけADRへ戻す。既存契約どおりに設定を届ける範囲では新規ADRを要求しない。

## 完了条件

文書で選んだ設定が選択した起動面へ実際に届き、代表的な保護・外部接続設定を秘密値なしで機能確認でき、未対応面を利用者が事前に識別できた時点でDoneとする。
