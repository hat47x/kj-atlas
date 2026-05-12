# Security

対象読者: kj-atlas を安全に評価・運用する管理者、セキュリティ担当者、開発者。

目的: SafeMode、外部送信、API 保護、アクセス制御、データ取り扱いの基本境界を説明します。

範囲外: 組織固有の承認履歴、秘密情報の配布、個別インシデントの詳細記録。

データが保存、送信、共有される場面を横断して確認したい場合は、先に [data_handling.md](data_handling.md) を読んでください。

## 基本方針

- 既定では外部 LLM へ送信しません。
- SafeMode は未レビュー情報の混入、share/export の意図しない緩和、AI による自動確定を避けるための安全境界です。
- AI の出力は提案として扱い、人間の確認なしに確定状態へ昇格させません。
- 秘密情報、トークン、未公開顧客情報、生の監査ログを利用者向け文書や export に混ぜません。

## 先に知っておく用語

| 用語 | 意味 |
| --- | --- |
| SafeMode | 危険な自動処理や未レビュー情報の混入を避けるため、安全側の挙動を優先する状態です。 |
| 外部送信 | LLM、audit endpoint、access control endpoint など、アプリ外の宛先へ情報を送ることです。 |
| opt-in | 危険や影響を理解したうえで、明示的に有効化することです。 |
| allowlist | 接続してよい宛先だけを列挙する一覧です。 |
| fail-safe | 障害時に、便利さより安全を優先する動きです。 |

## 既定で無効なもの

| 項目 | 既定 |
| --- | --- |
| LLM provider | `KJ_ATLAS_LLM_PROVIDER=none` |
| large-scale LLM | opt-in なしでは無効 |
| audit HTTP export | `KJ_ATLAS_AUDIT_EXPORT_ENABLED=false` |
| SafeMode 中の audit 外部送信 | `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE=false` |
| API key 認証 | `KJ_ATLAS_API_KEY` 未設定時は無効 |

## API key

`KJ_ATLAS_API_KEY` を設定すると、`/healthz` 以外の API は `X-API-Key` ヘッダーを要求します。

```bash
export KJ_ATLAS_API_KEY='change-me'
```

```bash
curl -H "X-API-Key: change-me" http://localhost:8080/api/docs/example
```

API key は簡易保護です。公開ネットワークでの本格運用では、TLS、認証 proxy、アクセス制御、監査を組み合わせてください。

## LLM provider の安全境界

### `none`

既定です。AI 機能は provider disabled として失敗します。検証やデモではこの状態を推奨します。

初回導入時は、まず `none` のまま保存・表示・E2E を確認してください。AI 接続を後から足す方が、問題の原因を分けやすくなります。

### `local`

ローカルまたは組織内の HTTP endpoint を使います。

```bash
export KJ_ATLAS_LLM_PROVIDER=local
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
```

送信先は `<base_url>/generate` です。local と呼んでいても、実際の宛先が外部ネットワークでないことを運用側で確認してください。

### `large-scale`

large-scale は、明示 opt-in、昇格許可、allowlist がすべて必要です。

```bash
export KJ_ATLAS_LLM_PROVIDER=large-scale
export KJ_ATLAS_LLM_ESCALATION_ENABLED=true
export KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true
export KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST='llm.example.com'
```

allowlist に含まれない host への送信は失敗します。

## Audit export

audit HTTP export を使う場合:

```bash
export KJ_ATLAS_AUDIT_EXPORT_ENABLED=true
export KJ_ATLAS_AUDIT_TRANSPORT=http
export KJ_ATLAS_AUDIT_HTTP_ENDPOINT='https://audit.example.com/events'
```

注意:

- endpoint と API key は秘密情報として扱います。
- SafeMode 中に audit 外部送信を許可する場合は、`KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE=true` の理由を運用記録に残してください。
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

- `external_http` を指定しても endpoint が未設定の場合、現行実装は `noop` にフォールバックします。外部 PDP を必須にする環境では、endpoint 未設定を運用上の設定失敗として扱ってください。
- `Org` または `Restricted` の対象で `policyRef` がない場合、local fail-safe が働きます。`read_only` では読み取りだけを許可し、`deny` では拒否します。
- `Public` と `Unlisted` は `policyRef` 欠損による強制 fail-safe の対象外です。公開範囲を広げる前に、visibility と policyRef を確認してください。

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
- [ ] SafeMode 中に外部送信を許可していない、または許可理由を記録している。
- [ ] share/export の出力に秘密情報や内部メモが混ざっていない。
- [ ] access control 障害時の fail-safe が `read_only` など保守的な値になっている。
- [ ] `external_http` を使う場合、PDP endpoint が設定され、`noop` にフォールバックしていない。

## 迷ったときの判断

- 外部へ送る必要が説明できない場合は送らない。
- 秘密情報が含まれる可能性がある場合は、先に入力データを減らす。
- SafeMode の緩和が必要に見える場合は、実装変更ではなく運用上の例外として扱う。
- 障害時の挙動が分からない場合は、読み取り専用または LLM disabled に倒す。

## 関連文書

- [configuration.md](configuration.md)
- [data_handling.md](data_handling.md)
- [security_operational_guidelines.md](security_operational_guidelines.md)
- [operations.md](operations.md)
- [THREAT_MODEL.md](../THREAT_MODEL.md)
