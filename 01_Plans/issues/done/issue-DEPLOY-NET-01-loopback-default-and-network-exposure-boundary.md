# Issue: DEPLOY-NET-01 標準Composeをloopback既定にしネットワーク公開境界を明示する

> `http://localhost:8080`と案内することは、サービスがlocalhostだけでlistenすることを意味しない。認証なしの評価環境をLANへ暗黙公開しない。

- Type: Security / Bug / Documentation
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Deployment contributor
- Scope: `03_Implement/deploy/docker-compose.yml`, `02_Architecture/deployment.md`, `02_Architecture/runtime_parameter_registry.md`, `THREAT_MODEL.md`, `README.md`, `04_Documentation/installation.md`, `04_Documentation/configuration.md`, `04_Documentation/security.md`, `04_Documentation/operations.md`, `04_Documentation/release.md`, deployment/docs contract tests
- Related ADR/Spec: `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `01_Plans/issues/done/issue-ENV-COMPOSE-01-runtime-setting-delivery-and-effective-verification.md`, `02_Architecture/deployment.md`, `THREAT_MODEL.md`
- Expected verification level: integration

## 課題

標準Composeのweb公開は次の短縮記法である。

```yaml
ports:
  - "${KJ_ATLAS_WEB_PORT:-8080}:80"
```

host IPを省略したDockerのport公開はloopback限定ではなく、ホストの全インターフェースを対象にする。利用者は`http://localhost:8080`でアクセスできるが、同じLANやホストへ到達できる別主体からも接続可能になり得る。

現在の文書と安全モデルには次の不整合がある。

- `installation.md`とREADMEは「ローカルまたは評価環境」として標準Composeを案内し、アクセス先に`localhost`だけを示すが、bind範囲を説明しない。
- `KJ_ATLAS_API_KEY`は未設定が既定で、標準Composeへも未配送である（`ENV-COMPOSE-01`）。
- API keyを有効にしても同梱SPAは`X-API-Key`を送らないため、通常のブラウザ利用を保ったままdefault exposureを補う認証にはならない。
- `deployment.md`は`KJ_ATLAS_WEB_PORT`を「公開port」と呼ぶが、bind address、loopback、LAN公開の契約がない。
- `THREAT_MODEL.md`はimport、render、supply chain、export等を扱う一方、認証なしHTTP面の誤公開を脅威として扱わない。
- `security.md`は「公開ネットワークではTLS、認証proxy等を組み合わせる」と述べるが、標準Composeが既にどのinterfaceへ公開されるかを伝えない。

評価中に入力したカード、ドキュメント、レビュー情報は保護対象である。SafeModeはshare/exportの漏洩を抑えるが、ネットワーク経由でAPIや画面へ直接到達する主体を認証する機能ではない。`localhost`というURL表示だけでローカル限定と誤認させることは、安全既定に反する。

既存のauth、SafeMode、`ENV-COMPOSE-01`はそれぞれ認証契約、アプリ内共有境界、環境変数配送を扱う。本Issueはhost portの到達範囲を担当し、重複しない。

## 対応方針

### Phase A: 標準評価構成をloopback限定にする

- base `docker-compose.yml`のweb portをIPv4 loopbackへ明示bindする。
- 既定の利用導線を`127.0.0.1` / `localhost`からの単一ホスト評価と定義する。
- `KJ_ATLAS_WEB_PORT`はport番号だけを変え、bind範囲を拡張しない契約にする。
- README、installation、configuration、operationsで「同一ホストからだけ使う評価構成」と明記する。
- SafeModeやAPI keyをnetwork access controlの代替として説明しない。

最小実装例は次の意味を持つものとする。実際のYAML表現はCompose検証を通る等価表現でよい。

```yaml
ports:
  - "127.0.0.1:${KJ_ATLAS_WEB_PORT:-8080}:80"
```

### Phase B: 非loopback公開は別profileとして扱う

別端末、LAN、Internet、組織ネットワークから利用する必要がある場合は、base Composeのport文字列を直接書き換える手順だけを案内しない。少なくとも次を満たす明示的なdeployment profileまたは組織側構成として分離する。

- TLS終端
- SPAとAPIの双方を覆う認証proxy
- 接続元制限またはfirewall
- secret管理
- `ENV-COMPOSE-01`で確認する実効設定配送
- backup/restoreと監査
- 公開URL、owner、撤回手順の記録

Phase Bの配布profileは本Issueの必須実装にしない。新しいbind-address公開キー、同梱認証proxy、Internet公開profileを正規サポートする場合は、runtime registryを先に更新し、複数案や安全境界変更が残るならADRへ戻す。

### 脅威モデルと検証を同期する

`THREAT_MODEL.md`へ「誤ったネットワーク公開」を追加し、少なくとも次を扱う。

- 保護資産: document本文、レビュー情報、設定・診断情報
- 攻撃者: 同一LAN、共有ホスト、誤設定されたport forwardingから到達する未認証主体
- 入口: Nginx配信面と`/api`
- 対策: loopback既定、明示profile、認証proxy/TLS/firewall、公開前probe
- 非対策: SafeMode、URLに`localhost`を書くこと、API health成功

## 実施しないこと

- base Composeを`0.0.0.0`公開のまま注意書きだけで完了すること。
- API keyをfrontend bundle、URL、Composeファイルへ埋め込むこと。
- SafeModeを認証・認可・firewallの代替として扱うこと。
- CI runnerや開発ホストのfirewallを変更すること。
- Internet公開、TLS証明書発行、特定cloudへのdeployを本Issueで実装すること。
- LAN公開を便利にするため、認証なしoverrideを公開クイックスタートへ追加すること。

## 実行順序

1. Security contributorが現行port mapping、API認証、SPA制約を脅威モデルへ反映する。
2. Deployment contributorがbase Composeをloopback限定へ変更する。
3. Documentation contributorがlocal evaluationとnetwork deploymentを全導線で分離する。
4. QA contributorがComposeのrendered port bindingと公開文書の契約テストを追加する。
5. Maintainerが非loopback経路を正式サポートするかを別判断し、未対応なら明確に範囲外とする。

## 受入条件

- [x] base Composeのweb portがloopbackへ明示bindされ、host IP省略または`0.0.0.0`へ戻らない。→ `docker-compose.yml`の`web.ports`を`127.0.0.1:${KJ_ATLAS_WEB_PORT:-8080}:80`へ変更済み（下記「実装記録」参照）。
- [x] `KJ_ATLAS_WEB_PORT`を変更してもbind addressはloopbackのままである。→ 環境変数はport番号のみに作用し、host IP部分は固定文字列。contract testで固定。
- [x] READMEとinstallationが標準Composeを同一ホスト評価用と明記し、`localhost`表示だけを到達範囲の根拠にしない。→ 両文書に明記済み。
- [x] deployment、configuration、operationsがbase profileと非loopback deploymentの責務を区別する。→ 3文書とも該当箇所を更新済み。
- [x] security文書がSafeMode/API keyの非保証範囲と、SPAを含む前段認証の必要性を説明する。→ `security.md`のAPI key節へ追記済み。
- [x] `THREAT_MODEL.md`に未認証HTTP面の誤公開、資産、攻撃者、入口、対策が追加される。→ §7として追加済み。
- [x] contract testがhost IP省略、`0.0.0.0`、loopback以外のbase mappingを検出する。→ `01_Plans/tests/test_deploy_network_exposure_contract.py`を新規追加、修正前の設定に対する負例（fail確認）も実施済み（下記「実装記録」参照）。
- [x] Docker-capable hostでrendered Composeのweb bindingが`127.0.0.1:<port>`であることを確認する。→ `docker compose config`と実際の`docker compose up`の両方で確認済み。
- [x] 可能なintegration環境では同一ホストからhealth/UIへ到達でき、非loopback interfaceを宛先とする接続が成功しないことを確認する。→ 実機Dockerで確認済み（下記「実装記録」参照）。
- [x] 非loopback公開を提供する場合、明示profileとTLS・認証proxy・接続元制限・撤回手順が同時に定義される。→ 条件（非loopback公開を提供する）が成立しないため充足扱い。非loopback公開は現時点で提供せず、Phase Bとして明示保留（本issue「非loopback公開は現時点で提供しない」）。提供開始時に本ACを再評価する。
- [x] SafeMode、share/export、import sanitize、provider=`none`、AI proposal-onlyの既定を変更しない。→ 本変更はport bindingのみで、これらのシステムへのコード変更は無し。

## 検証計画

- 静的検査:
  - base Composeの`web.ports`にloopback host IPがある。
  - public docsにbase profileの到達範囲と非保証がある。
  - threat modelにnetwork exposure threatがある。
- Compose検査:
  - `docker compose -f 03_Implement/deploy/docker-compose.yml config`
  - `docker compose -f 03_Implement/deploy/docker-compose.yml port web 80`
  - OS依存の`ss` / `netstat`は補助証跡とし、正本コマンドに固定しない。
- 機能確認:
  - loopback経由のUIと`/api/healthz`が成功する。
  - CI環境が複数interfaceを提供する場合だけ、非loopback経由が拒否されることを確認する。
- repository gate:
  - `python 01_Plans/docs_check.py`
  - deployment/docsの近接契約テスト。
  - `git diff --check`

Dockerを利用できない環境では静的検査だけを成功扱いにし、Docker-capable hostでのbinding確認を未実施として残す。

## 実装記録（2026-07-17）: Phase A 完了

- **`docker-compose.yml`**: `web.ports`を`"${KJ_ATLAS_WEB_PORT:-8080}:80"`から`"127.0.0.1:${KJ_ATLAS_WEB_PORT:-8080}:80"`へ変更した。
- **`THREAT_MODEL.md`**: §7「標準Composeのネットワーク公開境界（DEPLOY-NET-01）」を新規追加し、対象範囲一覧にも追記した。保護資産・攻撃者・入口・誤解しやすい非対策（SafeMode、`KJ_ATLAS_API_KEY`、`localhost`表示）・想定対策を記載した。
- **文書更新**: `README.md`（開発者向け起動手順の直後）、`04_Documentation/installation.md`（Compose起動手順の直後）、`04_Documentation/operations.md`（標準URL説明）、`04_Documentation/security.md`（API key節）、`02_Architecture/deployment.md`（基本方針・公開設定キー表・Registry/Deploy alignment matrix）に、標準構成がloopback限定の同一ホスト評価用であることを明記した。`04_Documentation/configuration.md`の`KJ_ATLAS_WEB_PORT`行も同様に更新した。
- **contract test**: `01_Plans/tests/test_deploy_network_exposure_contract.py`を新規追加した。`docker-compose.yml`の`web.ports`マッピングを解析し、(1) `127.0.0.1:`で始まること、(2) `0.0.0.0`を含まないこと、(3) `KJ_ATLAS_WEB_PORT`変数を含み`host_ip:port:container_port`の3要素構造を保つこと、を検証する2 test。修正前の設定（host IP省略）に対しては両testがfailすることを負例として確認済み。
- **Docker検証（実機、2026-07-17）**:
  - `docker compose config`: レンダリング結果の`web.ports`が`host_ip: 127.0.0.1`であることを確認。
  - `docker compose up --build -d`: 実際に起動し、`docker compose ps`のPORTS列が`127.0.0.1:8080->80/tcp`であることを確認。
  - `curl http://localhost:8080/api/healthz`・`curl http://127.0.0.1:8080/api/healthz`: いずれも`{"status":"ok"}`で成功。
  - ホストの非loopback IP（`hostname -I`で取得、例: `172.17.170.131`）宛の`curl http://<non-loopback-ip>:8080/api/healthz`: `Couldn't connect to server`で失敗（意図通り、到達不可を確認）。
  - `docker compose down`で後片付け済み。
- **非対象（Phase B）**: 非loopback公開のための別deployment profile（TLS終端、認証proxy、接続元制限等）は本変更に含めない。実行順序段階5「Maintainerが非loopback経路を正式サポートするかを別判断」は継続する人手判断であり、本セッションでは完了させていない。

検証結果:
- `python3 01_Plans/tests/test_deploy_network_exposure_contract.py`相当（`unittest`経由、pytest本環境未導入のため）: 2/2 pass。負例（修正前設定）: 2/2 fail（意図通り検出）。
- `python 01_Plans/docs_check.py`: pass。
- `python 01_Plans/issues/validate_active_issue_memos.py`: pass。

**残る人手判断**: 本変更はLAN上の別端末からbase Composeへ接続していた既存利用者に対する破壊的変更（互換性影響）である。実装・検証は完了しているが、この既定動作変更をMaintainerが受け入れるかどうかの最終確認は本セッションでは行っていない。Statusは`Open`のまま維持する。

## リスクとロールバック

- LAN上の別端末からbase Composeへ接続していた利用者には互換影響がある。暗黙公開を維持せず、必要性を確認してPhase Bへ移す。
- Windows、macOS、Linuxでloopback mappingのrender差があり得るため、3環境すべてを必須にせず、Composeモデルと代表Docker hostで確認する。
- 問題時は認証なし全interface公開へ戻さず、対象環境の明示overrideとfirewallで限定的に復旧する。

## 完了条件

fresh cloneの標準Composeが同一ホストだけから到達でき、利用者が公開範囲と非保証を起動前に理解でき、非loopback公開が安全要件を伴う別profileとして分離された時点でDoneとする。
