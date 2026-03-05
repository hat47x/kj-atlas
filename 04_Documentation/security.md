# セキュリティ指針（セルフホスト最小運用）


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
このドキュメントは、**イントラネット / VPN 内でのセルフホスト運用を前提**に、
MVP で実施しやすい最小限の保護策をまとめたものです。

## 1. 前提と範囲

- 本プロジェクトのMVPは、**完全な認証・ユーザー管理機能（ユーザー/セッション/OAuth）を提供しません**。
- そのため、公開インターネットへ直接公開する構成は推奨しません。
- OIDC/SAML 認証統合を検証する場合は、`01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md` のテスト専用プロファイルに従ってください。
- 想定運用は以下です。
  - 社内ネットワーク内（intranet）
  - VPN 接続経由のみ

## 2. 推奨デプロイ構成

- `api` は **Nginx / Traefik などのリバースプロキシ配下**で公開する
- TLS 終端はプロキシ側で実施する（HTTPS）
- `api` と `db` は同一内部ネットワークに閉じ、DB ポートを外部公開しない

## 3. データ取り扱いの既定値

- 既定は `KJ_ATLAS_LLM_PROVIDER=none` です（外部送信なし）
- ローカルLLM / 社内LLM利用時のみ `KJ_ATLAS_LLM_PROVIDER=local` を設定します
- 外部送信が必要な場合は、組織側のポリシーに従って明示的に判断してください

## 4. 実施しやすい最小コントロール

まずは以下の4点を推奨します。

1. **プロキシでIP許可リスト**を設定（到達元を社内セグメントやVPNに限定）
2. **プロキシでBasic認証**を有効化（簡易保護）
   - ただし原則は local/dev のみ。`DEV_BASIC_AUTH_ENABLED=true` などの明示的な環境変数がある場合に限定し、`docker-compose.local.yml` でのみ指定する。
3. **APIネットワークとDBネットワークを分離**（不要な到達経路を減らす）
4. **定期バックアップと定期パッチ**（OS / コンテナ / 依存ライブラリ）

## 5. 任意: APIキーによる簡易保護（バックエンド）

バックエンドは `KJ_ATLAS_API_KEY`（旧: `API_KEY`） を設定した場合のみ、簡易なヘッダ認証を有効化できます。

- 環境変数 `KJ_ATLAS_API_KEY`（旧: `API_KEY`） が **未設定**: 現在と同じく全APIを許可
- 環境変数 `KJ_ATLAS_API_KEY`（旧: `API_KEY`） が **設定済み**: `/healthz` 以外で `X-API-Key: <KJ_ATLAS_API_KEY>` を必須化
- 不一致 / 未指定時は `401 Unauthorized`

例:

```bash
export KJ_ATLAS_API_KEY='change-me'
```

リクエスト例:

```bash
curl -H 'X-API-Key: change-me' http://localhost:8000/docs/<doc_id>
```

> 注意: これはMVP向けの簡易ガードです。強い認証基盤の代替ではありません。

## 6. ZIP import hardening（フロントエンド）

`03_Implement/frontend/src/import/zip_import.ts` では、review pack ZIP 取り込み時に以下を既定で適用します。

- パス検証: `../`、絶対パス、Windows drive path（`C:/...`）、UNC path（`\\server\share`）、NUL byte を拒否
- サイズ上限: 総展開サイズ / 1ファイル展開サイズ / テキストサイズ / PNGサイズの上限を適用
- 件数上限: アーカイブ内ファイル数に上限を適用
- 圧縮率上限: 異常な高圧縮（zip bomb疑い）を拒否
- 拡張子制限: `.json/.md/.png` のみを取り込み対象とし、それ以外は無視して警告件数へ加算

運用上、上限値を緩める場合は DoS 耐性と UX のトレードオフをレビューで明示してください。



## 7. 配信物の改ざん検知（static publish / review pack）

- `static publish` 生成物には `integrity.json`（SHA-256 digests）を同梱します。
- `--signing-key` + `--key-id` を指定した場合、`integrity.json.signature` に detached signature（`rsa-sha256`）を付与します。
- `scripts/verify_artifact_integrity.mjs` は hash / signature / key-id を検証し、失敗時は終了コード1で停止します（fail-safe）。
- review pack import は `integrity.json` が含まれている場合、import前に hash 検証を実施し、不一致時は読み込みを拒否します。

### 7.1 鍵管理（運用最小手順）

1. 署名鍵ペアは公開配布サーバと分離した安全な保管領域で管理する（private keyをリポジトリに置かない）。
2. `key-id` はローテーション単位（例: `ops-2026q1`）で採番し、配布ログに記録する。
3. CI/CDでは private key をシークレット注入し、`publish:static` 実行時のみ利用する。

### 7.2 ローテーション

1. 新鍵ペアを発行し、新しい `key-id` を割り当てる。
2. 新鍵で再署名した配信物を生成し、`verify_artifact_integrity` で検証する。
3. 運用側の許可済み公開鍵を新 `key-id` へ切替後、旧鍵を失効する。

### 7.3 障害時対応（改ざん疑い / 鍵不一致）

- 症状: `Hash mismatch` / `Signature verification failed` / `Signing key mismatch`。
- 初動: 配布停止、当該artifact隔離、直近の正当artifactとの差分比較。
- 復旧: 正常鍵で再生成・再検証し、再配布。
- 事後: 鍵漏えい可能性がある場合は即時ローテーションし、該当 `key-id` を失効扱いにする。


## 8. Strict provisioning 運用（AUTH-API-02）

`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`（旧: `ALLOW_JIT_PROVISIONING`）の strict mode では、未登録subjectを必ず拒否します。

- 拒否契約: `403` + `{"code":"identity_not_provisioned","message":"Identity not provisioned. Pre-provision via /admin/provision/users before access."}`
- 回復導線: `POST /admin/provision/users`
  - request: `{ "provider": "saml", "externalUid": "alice", "displayName": "Alice" }`
  - create時: `201` + `provisioned=true`
  - 再試行: `200` + `provisioned=false`
  - 既存identityに矛盾する `displayName/email` は `409 identity_already_provisioned_conflict`

運用上、strict緩和（`KJ_ATLAS_ALLOW_JIT_PROVISIONING=true`（旧: `ALLOW_JIT_PROVISIONING=true`） への切替）は承認フローを経て記録してください。

### 8.1 strict mode例外時の安全性チェック（AUTH-OPS-03 / T3）

- 本節を strict mode 例外運用の**最小チェックリスト正本**として扱う。
- 以下の契約を**同時に**満たせない場合、例外適用を停止する。

#### 事前チェック（必須）

- [ ] 2者承認（Security Officer + System Owner）が確認できる。
- [ ] 必須記録5項目（時刻/理由/承認者/対象環境/復旧条件）が埋まっている。
- [ ] SafeMode既定ONを弱める設定変更（share/export制約緩和）が含まれていない。
- [ ] 監査最小化契約（下記 8.2 の最小項目のみ記録、PII非保存）を満たす記録計画になっている。

#### 事後チェック（必須）

- [ ] 復旧条件: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ復帰済み。
- [ ] 復旧時刻と復旧条件の充足を記録済み。
- [ ] 記録に `roles/groups/policyRef` 生値・subject生値・本文等のPIIが含まれていない（下記 8.2 の禁止項目準拠）。
- [ ] 未確定項目（承認順序/TTL/代理承認/エスカレーション等）が残る場合、**TODO化せず「確認待ちで停止」**として扱っている。

### 8.2 監査最小化・PII最小化ルール（strict mode例外ログ）

strict mode例外ログは、以下の5項目のみを最低監査項目として保存する。

- [ ] 時刻（開始時刻/終了時刻、UTC推奨）
- [ ] 例外理由（定型カテゴリ + 短文理由）
- [ ] 承認者（Security Officer / System Owner の識別子）
- [ ] 対象環境（prod/stg/dev など）
- [ ] 復旧条件（`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`（旧: `ALLOW_JIT_PROVISIONING=false`） へ戻す判定条件）

PII非保存ルール:

- [ ] subject生値（メール/外部UID/表示名）をログへ保存しない。
- [ ] `roles/groups/policyRef` の生値をログへ保存しない（必要時は件数やハッシュ化IDのみ）。
- [ ] 申請本文・添付・チャット転記など自由記述にPIIを含めない。
- [ ] 診断に必要な場合でも、PIIを含む原文は監査ログへ転記せず、別系統のアクセス制御下で管理する。

### 8.3 未確定事項の扱い（停止条件）

- 未確定事項は TODO として先送りしない（停止条件）。
- strict mode例外の実行可否に関わる未確定事項が1つでもある場合、状態を**「確認待ちで停止」**と明記する。
- 「確認待ちで停止」中は、回答確定まで `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` への切替を禁止する。

#### 停止条件（推測禁止）

- 承認順序・承認有効期限・代理承認・違反時SLAなどの未確定フローを決めないと運用できない場合、推測で確定せず停止する。
- 停止時は質問リストを更新し、状態を「確認待ちで停止」と明記したうえで、回答が得られるまで strict 例外の実行を禁止する。
