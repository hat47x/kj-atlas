# Issue: ENV-COMPOSE-01 Compose実行時設定の配送と実効確認を一致させる

> 公開設定キーが存在することと、標準Composeの`api`コンテナへ届くことは別である。設定したつもりの安全機能が既定値のまま動く状態を防ぐ。

- Type: Bug / Security / Documentation
- Status: In Progress
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

- [x] 37個のbackend公開キーすべてに、direct / base Compose / overlay / fixedの対応とsecret区分がある。
- [ ] Compose向けと記載されたキーが`api`へ配送され、direct-onlyのキーをCompose例で案内しない。
- [ ] `KJ_ATLAS_API_KEY`と`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`が標準または明示profileで機能的に確認できる。
- [ ] local/large-scale LLM、audit、外部PDPは、必要な関連キーが一組として届くか、そのCompose profileではunsupportedと明記される。
- [ ] optional設定の未指定が空文字へ変わらず、現在の安全な既定値を維持する。
- [ ] secret値がCompose定義、Git差分、テスト出力、診断出力に現れない。
- [ ] host、Compose service、別hostのendpoint例が区別され、Compose内`localhost`の誤用がない。
- [ ] 静的契約テストがsettings公開キー、registry分類、Compose mapping、公開文書のsurface表記のdriftを検出する。
- [ ] Docker integrationがAPI key、JIT禁止、LLM stub、および外部接続test doubleの代表経路を値非表示で確認する。
- [x] SafeMode既定ON、provider=`none`、audit HTTP既定OFF、external PDP既定`noop`、share/export/import境界を変更しない。

## 実装記録（2026-07-17）: Phase 1 — 分類表の正本化とドキュメントのsurface表記修正

本Issueの「対応方針 1」（設定キーと実行面の対応表を正本化する）と「対応方針 3」（起動面ごとに例を分ける）のうち、ドキュメントのみで完結する部分を実施した。**「対応方針 2」（Composeの明示的allowlist実装）、「対応方針 4」（機能probeの自動テスト化）、静的契約テスト（AC 8）、Docker integration（AC 9）は未実施であり、後続作業として残る。**

### 実施したこと

- `02_Architecture/runtime_parameter_registry.md`の「Backend settings」表に `Delivery surface` / `Secret` / `Probe (non-secret)` の3列を追加し、37キー全てを分類した。分類は `settings.py`（`validation_alias`定義および`validate_llm_provider_guards`のfixed契約判定）と、現行の`docker-compose.yml` / `docker-compose.llm-stub.yml`の実際の配送内容を突き合わせて決定した（推測ではなく現状の実装を記述した）。
  - `direct`: 31キー（標準Compose・overlayいずれからも配送されない）。
  - `base Compose`: 2キー（`KJ_ATLAS_DATABASE_URL`, `KJ_ATLAS_LLM_PROVIDER`）。
  - `llm-stub overlay`のみ: 2キー（`KJ_ATLAS_LOCAL_LLM_BASE_URL`, `KJ_ATLAS_LOCAL_LLM_MODEL`。検証専用、本番非対応）。
  - `fixed`（validator強制）: 3キー（`KJ_ATLAS_CE4_EQUIVALENCE_MODE`, `KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT`, `KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS`）。`KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK`と`KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS`はCE4系だがvalidator未強制のため`direct`に分類した。
  - `KJ_ATLAS_API_KEY`と`KJ_ATLAS_ALLOW_JIT_PROVISIONING`には⚠️を付記し、「公開文書のexport例どおりに設定しても標準Composeでは`api`へ届かない」既知のギャップを明記した。
- `04_Documentation/configuration.md`、`04_Documentation/security.md`、`04_Documentation/local_llm_ops_guide.md`（対応方針3が明示した3ファイル）に、direct起動限定であることの注意書きを追加した。あわせて`local_llm_ops_guide.md`の`mock_local_llm.py`（direct起動向けスタブ）と`docker-compose.llm-stub.yml`（Compose overlay向けスタブ）が別の仕組みであることを明記した。
- `installation.md`、`operations.md`、`security_operational_guidelines.md`等、対応方針3が明示していない他の公開文書のlocalhost表記は本Issueでは監査していない（未着手）。

### 未実施（後続作業として残す）

- 対応方針2: 標準Composeの`api.environment`または新規overlayへの明示的キー追加（実際の配送実装）。
- 対応方針4: API key 200/401、JIT禁止、LLM stub到達性、audit/PDP test doubleの機能probeの自動テスト化。
- AC 8: `settings.py`公開キー集合 / registry分類 / Compose mapping / 公開文書surface表記のdriftを検出する静的契約テスト。
- AC 9: Docker integrationによる代表経路の機能確認（Docker/Docker Composeはこの検証環境で利用可能なことを確認済み: `docker --version` → 29.5.3、`docker compose version` → v5.1.4）。
- installation.md / operations.md 等、対応方針3の対象外だった公開文書のlocalhost表記監査。

理由: 対応方針2・4はComposeファイルとbackend挙動そのものを変更し、`KJ_ATLAS_API_KEY`・`KJ_ATLAS_ALLOW_JIT_PROVISIONING`という保護機構の実効性に直接影響するセキュリティ上重要な変更であるため、本ドキュメントのみの変更とは別に、専用のレビュー・Docker統合検証を伴うPRとして切り出す。

### 検証結果

- `python 01_Plans/docs_check.py` — pass（後続で再実行し記録する）。
- `git diff --check` — clean（CRLF混在ファイルへの追記はLF行のみで実施）。

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

## Sonnet級エージェント実行計画（2026-07-18）: Phase 2（配送実装・機能probe・静的契約テスト）

この節は、Phase 1（37キーの配送面分類の正本化＋公開文書の起動面注記、2026-07-17完了）に続く残作業を、**この節だけを読んだSonnet級エージェントが人間判断なしに実装からPR作成まで進められる**粒度で固定する。設計選択はここで確定済みであり、実装側で再選択しない。

### 前提事実（2026-07-18確認済み）

- API key保護は`03_Implement/backend/src/kj_atlas_api/main.py`のHTTP middleware（`require_api_key`、L45-56）。`/healthz`のみ免除、`x-api-key`ヘッダを`compare_digest`で照合、不一致は401。
- JIT provisioning拒否時のステータスは**403**（`03_Implement/backend/tests/test_auth_jit_provisioning.py`が既に固定）。
- 標準`docker-compose.yml`の`api.environment`はmap形式で`KJ_ATLAS_DATABASE_URL`と`KJ_ATLAS_LLM_PROVIDER`の2キーのみ。
- `02_Architecture/runtime_parameter_registry.md`のBackend settings表には`Delivery surface`列が存在し、`KJ_ATLAS_API_KEY`と`KJ_ATLAS_ALLOW_JIT_PROVISIONING`は「direct（base Compose 未配送）⚠️」と記載されている。
- 検証環境（WSL）でdocker 29.5.3 / compose v5.1.4が利用可能。

### 設計確定（実装側で再選択しない）

- **D-1 配送方式**: `api.environment`をmap形式からlist形式へ変換し、追加キーは**値なしpass-through**（`- KJ_ATLAS_API_KEY`）で書く。Compose仕様では、値なしentryはホスト環境に該当変数が存在する場合のみコンテナへ渡り、未設定時はコンテナ内でも未設定のままになる（空文字注入なし＝実装既定を壊さない）。**実装の最初の検証**として、変数未設定状態で`docker compose -f 03_Implement/deploy/docker-compose.yml config`を実行し、該当キーが出力に現れない（または`null`）ことを確認する。空文字（`KJ_ATLAS_API_KEY: ""`）として現れる場合はこの方式が環境のcomposeバージョンで成立しないため、**実装を停止して本節へ観測結果を追記する**。
- **D-2 base追加キー**: `KJ_ATLAS_API_KEY`と`KJ_ATLAS_ALLOW_JIT_PROVISIONING`の**2キーのみ**（AC-3が名指しする保護キー）。監査HTTP・外部PDP・large-scale LLM・local LLM接続情報はbase Composeへ追加しない（既定でunsupported、必要時は組織側overlay。AC-4は「unsupportedと明記」側で満たす）。
- **D-3 secret非固定**: Composeファイルへ値を一切書かない（pass-throughのみ）。probe scriptの出力は設定値をマスクし、pass/failと HTTP status のみを表示する。

### ステップ

1. **Compose編集** — `03_Implement/deploy/docker-compose.yml`の`api.environment`を次へ変更する:

   ```yaml
   environment:
     - KJ_ATLAS_DATABASE_URL=${KJ_ATLAS_DATABASE_URL:-postgresql+asyncpg://${KJ_ATLAS_POSTGRES_USER:-kj_atlas}:${KJ_ATLAS_POSTGRES_PASSWORD:-kj_atlas}@db:5432/${KJ_ATLAS_POSTGRES_DB:-kj_atlas}}
     - KJ_ATLAS_LLM_PROVIDER=${KJ_ATLAS_LLM_PROVIDER:-none}
     # Pass-through only when set on the host (unset stays unset in the container).
     - KJ_ATLAS_API_KEY
     - KJ_ATLAS_ALLOW_JIT_PROVISIONING
   ```

   既存のコメント（derived DB URLの説明）はlist形式へ移しても保持する。`docker-compose.llm-stub.yml`は変更しない。
2. **D-1検証** — 未設定時: `docker compose -f 03_Implement/deploy/docker-compose.yml config`の出力に`KJ_ATLAS_API_KEY`が空文字で現れないこと。設定時: `KJ_ATLAS_API_KEY=probe docker compose -f ... config`で値が渡ること。
3. **registry同期** — `02_Architecture/runtime_parameter_registry.md`のBackend settings表で、`KJ_ATLAS_API_KEY`と`KJ_ATLAS_ALLOW_JIT_PROVISIONING`の`Delivery surface`セルを`direct / base Compose`へ変更し、キー名の`⚠️`と前文の該当注記（「既知のギャップ」段落）を「base Composeがpass-through配送する（未設定時は未設定のまま）」へ更新する。あわせて前文へ「監査HTTP・外部PDP・large-scale LLMの接続系キーは標準Composeではunsupportedであり、必要な場合は組織側overlayで一組として配送する」の1文を追加する（AC-4）。
4. **公開文書同期** — `04_Documentation/configuration.md`と`04_Documentation/security.md`の「注意: 標準 Docker Compose はこのキーを `api` コンテナへ配送しません（direct 起動限定）…現状未実装」の注記（各1箇所、API keyセクション直後）を「標準 Docker Compose はこのキーをホスト環境から pass-through 配送します（ホスト側で未設定の場合はコンテナ内でも未設定のままで、既定の無効状態を維持します）」へ更新する。
5. **機能probe script新設** — `03_Implement/deploy/tools/verify_env_delivery.sh`（bash、`set -euo pipefail`）:
   - P-1 API key有効化: `KJ_ATLAS_API_KEY=probe-local-key docker compose up -d --build`後、(a) `curl -fsS http://localhost:8080/api/healthz`が200、(b) キーなし`curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/docs/example`が401、(c) `-H "X-API-Key: probe-local-key"`付きが非401（200/404いずれも可＝middleware通過の証明）。
   - P-2 JIT禁止: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`で再up後、未登録identityのauthヘッダ（`test_auth_jit_provisioning.py`と同じヘッダ組: `x-auth-provider`/`x-forwarded-user`等）付きリクエストが**403**になること。
   - P-3 既定維持: 両変数をunsetして再upし、保護対象APIが401にならない（未設定=保護無効の実装既定が維持される）こと。
   - 終了時`docker compose down`。出力はpass/failとstatus codeのみ（値・キーを表示しない）。いずれかfailで非0 exit。
6. **静的契約テスト新設** — `01_Plans/tests/test_env_delivery_contract.py`（unittest、`docs_check.py`の`_run_contract_tests`が自動発見）。repo rootは`Path(__file__).resolve().parents[2]`で取得し、実repositoryに対して次を表明する:
   - `settings.py`の`validation_alias="(KJ_ATLAS_[A-Z0-9_]+)"` regex収集集合 == registry Backend settings表の第1セルキー集合（37キー同士）。
   - registry表で`Delivery surface`セルに「base Compose」を含むキー集合 == `docker-compose.yml`の`api.environment`が配送するキー集合（list/map両形式をパース: `- KEY`、`- KEY=...`、`KEY: ...`のいずれも先頭の`KJ_ATLAS_[A-Z0-9_]+`を抽出）。
   - registry表で「llm-stub overlay」を含むキー集合 ⊆ `docker-compose.llm-stub.yml`の`api.environment`キー集合。
7. **検証ゲート**（PR前に全部pass必須）: `python3 -m unittest discover -s 01_Plans/tests -p "test_*.py"` / `python3 01_Plans/docs_check.py` / `bash 03_Implement/deploy/tools/verify_env_delivery.sh`（Docker利用可能時） / `git diff --check`。

### PR・レビュー規律

- 上記1〜6は**1 PR**にまとめる（契約テストがComposeの変更後状態を表明するため分割不可）。
- **デプロイ挙動の変更を含むため、CI green後も自動マージしない。人間レビュー保留とする**（PR #2618と同型の扱い）。PR本文に`docker compose config`のbefore/after差分（該当キーのみ）を記載する（本issueリスク節の要求）。
- Dockerを利用できない環境で実装する場合は、ステップ5の実行を省略して静的検査のみを成功扱いにし、AC-9の未実施理由とDocker-capable hostでの再開条件を本節の下へ追記する。

### AC対応

| ステップ | 閉じる受入条件 |
| --- | --- |
| 1+2 | AC-2（Compose向け記載キーの実配送）・AC-5（未設定時の既定値維持） |
| 5 | AC-3（API key/JIT禁止の機能確認）・AC-9（Docker integration、ローカル実行記録で） |
| 3 | AC-4（unsupported明記）・AC-1は Phase 1で対応済みの分類に配送実態を追随 |
| 1+3+5 | AC-6（secret値の非出現: pass-through方式とマスク出力で担保） |
| 6 | AC-8（静的契約テストによるdrift検出） |
| 全体 | AC-10（安全既定の不変: 挙動変更はキー配送のみで、既定値・SafeMode・provider境界に触れない） |

AC-7（endpoint例のnetwork namespace区別）はPhase 1（PR #2621）で対応済み。
