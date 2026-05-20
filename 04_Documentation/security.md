# Security

対象読者: kj-atlas を安全に評価・運用する管理者、セキュリティ担当者、開発者。

目的: SafeMode、外部サービスとの共有、API 保護、アクセス制御、データ取り扱いの基本境界を説明します。

範囲外: 組織固有の承認履歴、秘密情報の配布、個別インシデントの詳細記録。

データが保存される場面、外部サービスと共有される場面、利用者が共有する場面を横断して確認したい場合は、先に [data_handling.md](data_handling.md) を読んでください。

## 基本方針

- 既定では外部 LLM にデータを渡しません。
- SafeMode は未レビュー情報の混入、share/export の意図しない緩和、AI による自動確定を避けるための安全境界です。
- AI の出力は提案として扱い、人間の確認なしに確定状態へ昇格させません。
- 秘密情報、トークン、未公開顧客情報、生の監査ログを利用者向け文書や export に混ぜません。

## 先に知っておく用語

| 用語 | 意味 |
| --- | --- |
| SafeMode | 危険な自動処理や未レビュー情報の混入を避けるため、安全側の挙動を優先する状態です。 |
| 外部サービスとの共有 | LLM、監査ログ連携の接続先、外部アクセス制御の接続先など、アプリ外のサービスに情報を渡すことです。 |
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

API key は簡易保護です。公開ネットワークでの本格運用では、TLS、認証 proxy、アクセス制御、監査を組み合わせてください。

## SafeMode の画面確認

share/export の前は、「共有と再現」パネルで SafeMode、visibility、reviewerRef、出力形式を確認します。SafeMode が有効な状態では、export/share コンテキストで機微テキストをマスクすること、固定マスク対象を無効化できないことが画面上に示されます。

![SafeMode と共有前の確認画面](assets/screenshots/share-export-safe-mode.png)

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

- `external_http` を指定しても接続先（endpoint）が未設定の場合、現行実装は `noop` にフォールバックします。外部 PDP を必須にする環境では、接続先の未設定を運用上の設定失敗として扱ってください。
- `Org` または `Restricted` の対象で `policyRef` がない場合、local fail-safe が働きます。`read_only` では読み取りだけを許可し、`deny` では拒否します。
- `Public` と `Unlisted` は `policyRef` 欠損による強制 fail-safe の対象外です。公開範囲を広げる前に、visibility と policyRef を確認してください。


## 障害診断時の共有境界（PRODUCT-OPS-01 関連）

障害対応時のログ共有は、次の境界を満たす場合のみ許可します。

- 共有可: 発生日時、URL（機微部分を除去）、エラー種別、HTTP status、SafeMode 状態、再現手順。
- 共有禁止: API key、token、password、未マスク本文、個人情報、生の監査イベント。
- 条件付き: endpoint や組織内識別子は、System Owner 承認後に最小化して共有。

承認と実行の責務は分離します。

- 承認（System Owner）: 共有範囲とマスク方針の決定。
- 実行（Platform Operator / First Responder）: マスク済みログの作成と送付。

役割衝突または承認責務不明がある場合、共有を停止して `04_Documentation/operations.md` の停止条件に従います。

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
- [ ] `external_http` を使う場合、PDP の接続先（endpoint）が設定され、`noop` にフォールバックしていない。

## 迷ったときの判断

- 外部サービスと共有する必要が説明できない場合は共有しない。
- 秘密情報が含まれる可能性がある場合は、先に入力データを減らす。
- SafeMode の緩和が必要に見える場合は、実装変更ではなく運用上の例外として扱う。
- 障害時の挙動が分からない場合は、読み取り専用または LLM disabled に倒す。

## 用語整合（DOC-OPS-05）

本レーンでは役割語彙を次で統一します。

- **Security Officer**: 安全境界（SafeMode、外部サービスとの共有、share/export）を評価する責務。
- **System Owner**: 変更の業務上必要性と公開境界を判断する責務。
- **Platform Operator**: 設定適用、復旧、実行ログ記録を担当する責務。

> 2者承認（Security Officer と System Owner）と実行責務分離（Platform Operator）を原則とし、同一人物が兼務する場合も記録上は分離します。

固定値 D1〜D4 は `02_Architecture/strict_mode_exception_approval_flow.md` を正本として参照し、この文書では再定義しません。

## 関連文書

- [configuration.md](configuration.md)
- [data_handling.md](data_handling.md)
- [security_operational_guidelines.md](security_operational_guidelines.md)
- [operations.md](operations.md)
- [THREAT_MODEL.md](https://github.com/hat47x/kj-atlas/blob/main/THREAT_MODEL.md)

## 運用手順（DOC-OPS-05）
1. 対象読者（Audience）と目的（Goal）を先に確認する。
2. 公開境界（Public boundary）を確認し、内部手順は公開文書へ直接書かない。
3. 実行後は関連文書の導線（Related links）と矛盾がないか確認する。

## 判断基準（DOC-OPS-05 品質ゲート）
- 可読性: 用語が定義済み語彙と一致し、読者の次アクションが明確であること。
- 検証可能性: 手順・確認コマンド・期待結果が対応していること。
- 保守性: 上流（00〜02）と矛盾せず、関連文書へ責務を分離していること。

## 失敗時対応
- 参照不整合、用語不一致、公開境界の曖昧化を検出した場合は更新を停止する。
- 自己修復は最大3回までとし、4回目相当は Hold として論点化する。
- Architecture/ADR 本体の変更が必要な場合は、この文書では確定せず提案に留める。


## AUTH-OPS-03 契約整合チェック（Stream E）

AUTH運用のセキュリティレビューでは、次を最小セットとして確認します。

- D1〜D4（承認順序/TTL、適用スコープ/継続時間、代理承認禁止、監査SLA）が `02_Architecture/strict_mode_exception_approval_flow.md` と一致。
- 承認責務（Security Officer / System Owner）と実行責務（Platform Operator）が分離されている。
- `StoppedForClarification` 中に `ActiveException` へ遷移していない。
- PII最小化（subject生値・roles/groups生値・自由記述PII非保存）を維持している。

不一致が1件でもある場合、例外緩和を新規に有効化してはならない。

### AUTH-OPS-03 セキュリティ運用チェック（申請→承認→実施→監査→失効）

1. 申請（request）  
   - requestId・対象tenant・理由・rollbackBy・監査ID相互参照が揃っていること。
2. 承認（approve）  
   - Security Officer / System Owner の2者承認が成立し、承認TTL 4hを超過していないこと（D1）。
3. 実施（execute）  
   - Platform Operator が承認済み要求のみ実施し、未承認・承認不備の補完実行をしていないこと。
4. 監査（audit）  
   - `時刻/理由/承認者/対象環境/復旧条件` の最小監査項目が記録され、PII生値が保存されていないこと。
5. 失効（expire/rollback）  
   - 最大継続2h・停止条件成立・期限到来のいずれかで strict 復帰し、復旧時刻と判定根拠を記録していること（D2〜D4）。

関連導線: `02_Architecture/strict_mode_exception_approval_flow.md`（正本）, `04_Documentation/operations.md`（実行Runbook）, `01_Plans/project-progress-dashboard.md`（進捗監査）。
