# Security

対象読者: kj-atlas を安全に評価・運用する管理者、セキュリティ担当者、開発者。

目的: SafeMode、外部サービスとの共有、API 保護、アクセス制御、データ取り扱いの基本境界を説明します。

範囲外: 組織固有の承認履歴、秘密情報の配布、個別インシデントの詳細記録。

公開区分: 利用者/運用者向け公開候補。SafeMode、API保護、外部サービス共有の基本境界を示し、組織固有の承認証跡や秘密設定は含めません。

データが保存される場面、外部サービスと共有される場面、利用者が共有する場面を横断して確認したい場合は、先に [data_handling.md](data_handling.md) を読んでください。


## 関連文書の使い分け

- [operations.md](operations.md): 日常運用と障害時の初動。
- [security.md](security.md)（本書）: SafeMode、share/export、外部接続の基本方針。
- [security_operational_guidelines.md](security_operational_guidelines.md): 安全設定を変える前の判断例。

設定値の詳細は、GitHub 上の [runtime_parameter_registry.md](https://github.com/hat47x/kj-atlas/blob/main/02_Architecture/runtime_parameter_registry.md) を参照してください。本書では利用時に確認する境界だけを説明します。

## 基本方針

- 既定では外部 LLM にデータを渡しません。
- SafeMode は未レビュー情報の混入、share/export の意図しない緩和、AI による自動確定を避けるための安全境界です。
- AI の出力は提案として扱い、人間の確認なしに確定状態へ昇格させません。
- 秘密情報、トークン、未公開顧客情報、生の監査ログを利用者向け文書や export に混ぜません。

## 先に知っておく用語

| 用語 | 意味 |
| --- | --- |
| SafeMode | 危険な自動処理や未レビュー情報の混入を避けるため、安全側の挙動を優先する状態です。 |
| 外部サービスとの共有 | LLM、監査ログ連携の接続先、外部アクセス制御の接続先など、アプリ外のサービスと情報を共有することです。 |
| opt-in | 危険や影響を理解したうえで、明示的に有効化することです。 |
| allowlist | 接続してよい宛先だけを列挙する一覧です。 |
| fail-safe | 障害時に、便利さより安全を優先する動きです。 |

## 既定で無効なもの

| 項目 | 既定 |
| --- | --- |
| LLM provider | `KJ_ATLAS_LLM_PROVIDER=none` |
| large-scale LLM | opt-in なしでは無効 |
| audit HTTP export | `KJ_ATLAS_AUDIT_EXPORT_ENABLED=false` |
| SafeMode 中の audit HTTP 連携 | `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE=false` |
| API key 認証 | `KJ_ATLAS_API_KEY` 未設定時は無効 |

## API key

`KJ_ATLAS_API_KEY` を設定すると、`/healthz` 以外の API は `X-API-Key` ヘッダーを要求します。

```bash
export KJ_ATLAS_API_KEY='change-me'
```

```bash
curl -H "X-API-Key: change-me" http://localhost:8080/api/docs/example
```

ブラウザで動く同梱の画面（SPA）は `X-API-Key` を送らないため、`KJ_ATLAS_API_KEY` を設定すると画面からの操作は 401 になります。API key は `curl` などプログラムからのアクセスを保護するための簡易保護です。ブラウザ配信を保護する場合は、画面に鍵を持たせるのではなく前段の認証 proxy で行います。公開ネットワークでの本格運用では、TLS、認証 proxy、アクセス制御、監査を組み合わせてください。

> 注意: 標準 Docker Compose はこのキーをホスト環境から pass-through 配送します（ホスト側で未設定の場合はコンテナ内でも未設定のままで、既定の無効状態を維持します。[runtime_parameter_registry.md](https://github.com/hat47x/kj-atlas/blob/main/02_Architecture/runtime_parameter_registry.md#backend-settings) 参照）。

## SafeMode の画面確認

share/export の前は、「共有と再現」パネルの `共有前チェック` で SafeMode、公開範囲、未レビュー情報、出力形式を確認します。SafeMode が有効な状態では、export/share コンテキストで機微テキストをマスクすること、固定マスク対象を無効化できないこと、未レビューのドラフトを含めないことが画面上に示されます。

![SafeMode と共有前の確認画面](assets/screenshots/share-export-safe-mode.png)

> 起動面の注意: 以下の `export KJ_ATLAS_*` 例は direct 起動時の設定例です。標準 Docker Compose は `KJ_ATLAS_LLM_PROVIDER` のみを `api` コンテナへ配送し、`KJ_ATLAS_LOCAL_LLM_BASE_URL` 等の接続情報キーは配送しません。配送範囲は [runtime_parameter_registry.md](https://github.com/hat47x/kj-atlas/blob/main/02_Architecture/runtime_parameter_registry.md#backend-settings)（`Delivery surface` 列）を参照してください。

## LLM provider の安全境界

### `none`

既定です。AI 機能は provider disabled として失敗します。検証やデモではこの状態を推奨します。

初回導入時は、まず `none` のまま保存・表示・受け入れ確認を行ってください。AI 接続を後から足す方が、問題の原因を分けやすくなります。

### `local`

ローカルまたは組織内の HTTP 接続先（endpoint）を使います。

```bash
export KJ_ATLAS_LLM_PROVIDER=local
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
```

接続先は `<base_url>/generate` です。local と呼んでいても、実際の宛先が外部ネットワークでないことを運用側で確認してください。

送信requestはUTF-8 JSONで1MiB以下に制限され、task、temperature、max token数を接続前に検証します。過大promptや`NaN`等の不正値は本文をerrorへ表示せず`provider_validation`で停止し、fallback設定があっても別の失敗分類へ置き換えません。

> 注意: 標準 Docker Compose は `KJ_ATLAS_LOCAL_LLM_BASE_URL` を配送しません。Compose 上で `local` provider を検証する場合は、検証専用の `docker-compose.llm-stub.yml` overlay を使ってください。また `api` コンテナ内から見た `http://localhost:8001` はホストではなく `api` コンテナ自身を指すため、Compose 環境ではこの例をそのまま転記しないでください。

### `large-scale`

large-scale は、明示 opt-in、昇格許可、allowlist がすべて必要です。

```bash
export KJ_ATLAS_LLM_PROVIDER=large-scale
export KJ_ATLAS_LLM_ESCALATION_ENABLED=true
export KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true
export KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST='llm.example.com'
```

allowlist に含まれない host との連携は失敗します。

## Audit export

audit HTTP export を使う場合:

```bash
export KJ_ATLAS_AUDIT_EXPORT_ENABLED=true
export KJ_ATLAS_AUDIT_TRANSPORT=http
export KJ_ATLAS_AUDIT_HTTP_ENDPOINT='https://audit.example.com/events'
```

注意:

- 接続先（endpoint）と API key は秘密情報として扱います。
- `KJ_ATLAS_AUDIT_TRANSPORT=http` を指定した場合、endpointは必須です。未設定ならnoopへ縮退せず、設定エラーとして起動を拒否します。
- SafeMode 中に audit HTTP 連携を許可する場合は、`KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE=true` の理由を運用記録に残してください。
- audit には必要最小限のメタ情報だけを含め、生の秘密情報を含めないでください。

## Access control

既定の adapter は `noop` です。これは外部 PDP へ問い合わせず、アプリ単体の local fail-safe だけで動きます。

現行実装で使える adapter は次です。

| adapter | 用途 |
| --- | --- |
| `noop` | 外部認可を使わない既定値 |
| `mock` | 契約・結合テスト用 |
| `external_http` | 外部 PDP へ HTTP POST で認可判定を委譲 |

外部 PDP を使う場合は、fail-safe 動作を先に決めます。

```bash
export KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http
export KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=read_only
export KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT='https://pdp.example.com/decide'
```

障害時に読み取り専用へ落とす `read_only` を推奨します。より厳格に止めたい環境では `deny` を使います。

注意:

- `external_http` を指定した場合、接続先（endpoint）は必須です。未設定なら `noop` にフォールバックせず、設定エラーとして起動を拒否します。外部PDPを使わない場合はadapterを明示的に`noop`へ戻してください。
- `Org` または `Restricted` の対象で `policyRef` がない場合、local fail-safe が働きます。`read_only` では読み取りだけを許可し、`deny` では拒否します。
- `Public` と `Unlisted` は `policyRef` 欠損による強制 fail-safe の対象外です。公開範囲を広げる前に、visibility と policyRef を確認してください。

### 外部HTTP連携は設定不備を起動時に拒否する

次の2 resolverも、access-controlと監査HTTPと同じ完全設定の原則を使います。

- `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER`
- `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER`

どちらも `none` または `external_http` だけを受理します。`external_http` を選んだのにendpointがない場合、または `none` のままendpointやAPI keyだけを残した場合は、`noop` / `none` へ静かに後退せず、設定エラーとして起動を拒否します。不明なresolver名、安全でないURL、credential・query・fragmentを含むURLもfail-closedで拒否します。

この起動時拒否は設定ミスを隠さないための安全境界です。resolverを無効化する場合は、対応するHTTP endpointとAPI keyも同時に削除してください。全キーと入力制約は `02_Architecture/runtime_parameter_registry.md` を参照してください。


## 障害診断時の共有境界

障害対応時のログ共有は、次の境界を満たす場合のみ許可します。

- 共有可: 発生日時、URL（機微部分を除去）、エラー種別、HTTP status、SafeMode 状態、再現手順。
- 共有禁止: API key、token、password、未マスク本文、個人情報、生の監査イベント。

復旧時は、先に原因を決めつけず、計画、実行、確認の順で進めます。endpoint や組織内識別子を共有する必要がある場合は、必要性を確認し、機微部分を最小化してから共有します。

承認と実行の責務は分離します。

- 判断する人: 共有範囲とマスク方針を決める。
- 実行する人: マスク済みログの作成と送付を行う。

誰が判断するか不明な場合は、ログ共有を止めて [operations.md](operations.md) の停止条件に従います。

## 保持してよい情報、避ける情報

| 区分 | 例 | 方針 |
| --- | --- | --- |
| 保持してよい | ドキュメント本文、カード、島、レビュー状態 | 通常データとして扱う |
| 最小保持 | 表示名、メールアドレス、外部 identity 参照 | 必要最小限にする |
| 一時利用 | roles, groups, policyRef, trace id | 永続化しない前提で扱う |
| 禁止 | password, token, secret, raw assertion | 保存、ログ、export に含めない |

export、share、障害調査でどの情報を削るか迷う場合は、[data_handling.md](data_handling.md) のチェックリストを使います。

## セキュリティ確認チェックリスト

- [ ] LLM provider が意図した値になっている。
- [ ] large-scale を使う場合、opt-in と allowlist が設定済み。
- [ ] API key や audit token をリポジトリに含めていない。
- [ ] SafeMode 中に外部サービスとの共有を許可していない、または許可理由を記録している。
- [ ] share/export の出力に秘密情報や内部メモが混ざっていない。
- [ ] access control 障害時の fail-safe が `read_only` など保守的な値になっている。
- [ ] `external_http` を使う場合、PDP の接続先（endpoint）を同時に設定し、設定検証を通過して起動している。
- [ ] Document policy binding / tenant capability resolverを`external_http`にする場合はendpointが設定され、`none`にする場合はHTTP endpoint・API keyが残っていない。

## 迷ったときの判断

- 外部サービスと共有する必要が説明できない場合は共有しない。
- 秘密情報が含まれる可能性がある場合は、先に入力データを減らす。
- SafeMode の緩和が必要に見える場合は、実装変更ではなく運用上の例外として扱う。
- 障害時の挙動が分からない場合は、読み取り専用または LLM disabled に倒す。

## 役割と記録の考え方

組織内の正式な役職名に関係なく、少なくとも次の責務を分けて考えます。

- 安全性を判断する人: SafeMode、外部サービスとの共有、share/export のリスクを確認する。
- 業務上の必要性を判断する人: なぜ変更や共有が必要か、利用者にどの影響があるかを確認する。
- 設定を実行する人: 設定変更、復旧、実行結果の記録を担当する。

同じ人が複数の責務を担う場合でも、記録上は「誰が判断し、誰が実行したか」を分けて残します。

## 関連文書

- [configuration.md](configuration.md)
- [data_handling.md](data_handling.md)
- [security_operational_guidelines.md](security_operational_guidelines.md)
- [operations.md](operations.md)
- [THREAT_MODEL.md](https://github.com/hat47x/kj-atlas/blob/main/THREAT_MODEL.md)
