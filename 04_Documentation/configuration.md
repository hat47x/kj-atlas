# 設定（OSS / イントラ・自前ホスト向け）

> DOC-OPS-05 Classification: **Improve external**
> Audience: 外部運用者・管理者
> Goal: 公開設定ガイドとして最小安全設定と確認手順を提供する。
> Public boundary: 内部の意思決定メモは含めず、実行可能手順と正本参照のみ公開する。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。
> Non-goal: 組織固有の内部承認メモや未公開ネットワーク情報の共有。
> Outcome: 外部運用者が最小安全設定と確認手順を再現できる。
> Related: `02_Architecture/runtime_parameter_registry.md`, `04_Documentation/security.md`, `01_Plans/issues/issue-doc-ops-05-03-04doc-configuration.md`



> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
このドキュメントは、最小運用に必要な設定のみを記載します。

## 1. 基本方針（デフォルトは外部送信なし）

- `KJ_ATLAS_LLM_PROVIDER=none` が既定です。
- 既定のままでは外部LLMへのデータ送信は行いません。
- ローカル/社内LLMを使う場合のみ `KJ_ATLAS_LLM_PROVIDER=local` を明示設定します。

## 2. 主要環境変数

### `KJ_ATLAS_DATABASE_URL`

保存先DBを指定します。

- SQLite 例: `sqlite:///./kj_atlas.db`
- PostgreSQL 例: `postgresql+asyncpg://<user>:<password>@<host>:5432/<db>`

### `KJ_ATLAS_LLM_PROVIDER`

LLM連携方式を指定します。

- `none`（既定）
- `local`
- `external`（将来向け・現状未実装）



### `KJ_ATLAS_AUDIT_EXPORT_ENABLED` / `KJ_ATLAS_AUDIT_TRANSPORT`

閲覧/エクスポート監査イベントの外部送信を制御します。

- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=false`（既定）: 監査外部送信を完全無効化（no-op）
- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` + `KJ_ATLAS_AUDIT_TRANSPORT=noop`: 送信処理は有効だが外部送信はしない（疎通試験向け）
- `KJ_ATLAS_AUDIT_EXPORT_ENABLED=true` + `KJ_ATLAS_AUDIT_TRANSPORT=http`: `KJ_ATLAS_AUDIT_HTTP_ENDPOINT` へ POST 送信

補助設定:

- `KJ_ATLAS_AUDIT_HTTP_ENDPOINT`（`KJ_ATLAS_AUDIT_TRANSPORT=http` 時に必須）
- `KJ_ATLAS_AUDIT_HTTP_API_KEY`（任意、Bearer トークン）
- `KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS`（既定 2.0）
- `KJ_ATLAS_AUDIT_QUEUE_SIZE`（既定 100、失敗時メモリキュー上限）
- `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE`（既定 `false`。SafeMode時送信を許可する場合のみ `true`）

### `KJ_ATLAS_API_KEY`（任意）

簡易なAPI保護キーです。

- 未設定: 認証なし（既定動作）
- 設定時: `/healthz` 以外のAPIで `X-API-Key: <KJ_ATLAS_API_KEY>` を必須化

> 本機能はMVP向けの簡易ガードです。完全な認証/認可の代替ではありません。

## 3. `local` 設定（ローカル/社内LLM）

`KJ_ATLAS_LLM_PROVIDER=local` のときは以下を設定します。

- `KJ_ATLAS_LOCAL_LLM_BASE_URL`（必須）
  - 例: `http://localhost:8001`
- `KJ_ATLAS_LOCAL_LLM_MODEL`（任意）
  - 例: `local-model-name`

バックエンドは `KJ_ATLAS_LOCAL_LLM_BASE_URL + /generate` へ HTTP POST します。

## 4. Docker Composeでの設定例

`03_Implement/deploy/docker-compose.yml` では環境変数上書きが可能です。

### 既定（外部送信なし）

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_DATABASE_URL='postgresql+asyncpg://kj_atlas:kj_atlas@db:5432/kj_atlas'
export KJ_ATLAS_LLM_PROVIDER='none'
docker compose up -d
```

### ローカル/社内LLMを利用

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_LLM_PROVIDER='local'
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
docker compose up -d
```


### APIキーを有効化（任意）

```bash
cd /path/to/kj-atlas/03_Implement/deploy
export KJ_ATLAS_API_KEY='change-me'
docker compose up -d
```

## 5. データ搬送（JSON Export / Import）

フロントエンドで JSON Export / Import を利用できます。

- Export: 現在ドキュメントを JSON 保存
- Import: JSON を読み込み、バリデーション後に反映

イントラ運用時の持ち出し可否や保管場所は、組織ルールで管理してください。

## セキュリティ設定

最小運用の保護策（リバースプロキシ/TLS、IP制限、Basic認証、KJ_ATLAS_API_KEY など）は
[security.md](./security.md) を参照してください。


## 6. フロントエンドi18n辞書契約（FB-RM-I18N-02）

翻訳辞書は `03_Implement/frontend/src/i18n/locales/*.json` を正本とします。

- フォーマット: `{"<message.key>": "<localized string>"}` の JSON object
- 値型: すべて string（`validateLocaleMessages` で検証）
- 解決順序: `requested locale -> default locale (ja) -> key literal`

この順序により、要求locale側でキー欠損があっても既定言語（ja）へ復元され、
ja側にも存在しないキーのみ最終的に key 文字列を返します。

i18n表示差分を追加する場合は、UIコンポーネントの生文字列を直接変更せず、
`src/i18n/locales/ja.json` と `src/i18n/locales/en.json` に同一キーを追加して
`t("...")` 経由で参照してください（例: `search_bar.*`）。

## Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されている。
2. 既定の安全設定（`KJ_ATLAS_LLM_PROVIDER=none`、監査外部送信OFF既定）が明記されている。
3. 追加/改名パラメータの正本が `02_Architecture/runtime_parameter_registry.md` であることを明記している。

いずれか未充足の場合は「No-Go」として公開更新を停止します。

## DOC-OPS-05 実行記録（Phase 1〜5）

### Phase 1 Read

- Latest Read: 2026-04-13
- Audience / Goal / Public boundary / Related を確認し、公開境界を再確認。

### Phase 2 Plan

- Latest Read: 2026-04-13
- 本文は docs-only の範囲で更新し、仕様正本（00〜02）を上書きしない方針を固定。

### Phase 3 Execute

- Latest Read: 2026-04-13
- DOC-OPS-05 classification に沿って本文の公開メタと導線を整備。

### Phase 4 Verify

- Latest Read: 2026-04-13
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/configuration.md`
- `git diff --check`

### Phase 5 Proceed

- Latest Read: 2026-04-13
- 状態: **Ready**
- 次アクション: 公開運用者向けの前提条件と確認手順を維持し、内部判断メモは 01_Plans 側へ分離する。


## Stream F docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **Plan**: AC/DoD を先に定義する。不足時はドラフトを提示し、合意後に実行へ進む。
3. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
4. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
5. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 参照仕様未確定、または競合検知時は作業を停止する。
- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## DOC-OPS-05 追加実行記録（2026-04-16 / Target 05-01..05）

### Phase 1 Read（再Read）
- 本書と関連Issueを再Readし、公開境界とdocs-onlyスコープを確認。

### Phase 2 Plan（再Read）
- 5Phase（Read→Plan→Execute→Verify→Proceed）で進行し、対象外文書へは非接触とする。

### Phase 3 Execute（再Read）
- 本書の既存分類・公開境界メタを維持しつつ、05-01..05セットの実行記録を追記。

### Phase 4 Verify（再Read）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/configuration.md 01_Plans/documentation_quality.md`
- `git diff --check`
- 修復は最大3回まで。3回超過は停止（Hold）。

### Phase 5 Proceed（再Read）
- 判定: **Ready**
- 次アクション: 同一セット内Issue本文とScope本文の整合を維持して進行。

## DOC-OPS-05 Stream G 前半フェーズ実行記録（2026-04-16）

- Classification確認: **Improve external**（再判定なし）
- フェイルセーフ固定: 用語ドリフト検知・固定値不一致検知・自己修復3回超過で停止（Hold）

### Phase 1: Read（対象ファイル再読）
- 本ファイルを再読し、Scope / Audience / Goal / Public boundary / Related の整合を確認。

### Phase 2: Plan（対象ファイル再読）
- 本ファイルを再読したうえで、docs-only の変更範囲と受入条件を固定。

### Phase 3: Execute（対象ファイル再読）
- 本ファイルを再読したうえで、分類方針（Move internal / Improve external）を維持して更新。

### Phase 4: Verify（docs-check、対象ファイル再読）
- 本ファイルを再読したうえで docs-check を実施。
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/configuration.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。

## Stream H docs群1 serial cycle (2026-04-18)

### Phase 1 Read
- 対象ファイルを再読し、`Audience / Goal / Non-goal / Public boundary / Outcome / Related` の整合を確認した。
- Scopeを docs-only に固定し、編集禁止対象（`security.md` / `security_operational_guidelines.md` / shared files）へ非接触であることを確認した。

### Phase 2 Plan
- 1Phase1責務で進行し、変更は「実行記録の同期」と「公開境界の維持」に限定する。
- AC/DoD不足があれば先に補完提案し、未合意の新規仕様決定は持ち込まない。

### Phase 3 Execute（1ファイル直列）
- Classification: **Improve external**
- 04_Documentation/configuration.md は外部運用者向け設定導線を維持し、公開境界メタの整合のみ更新する。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/configuration.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。

## DOC-OPS-05 Stream J2 execution record (2026-04-18)

### Phase 1: Read
- Target issue scope and this document were re-read to confirm Audience / Goal / Public boundary.
- Classification remains **Improve external** and no Stream H-owned file edits are required.

### Phase 2: ADR CDC
- CDC update is **not required** because the existing placement policy is within current DOC-OPS-05 decisions.

### Phase 3: Plan
- AC/DoD補足: 分類根拠（Audience/Goal/公開境界）・次アクション・検証一致（docs-check）を1セットで記録する。
- 次アクション固定: 公開設定手順の改善範囲を維持し、内部判断ログは持ち込まない。

### Phase 4: Execute
- docs-onlyで本ファイルのみを更新し、実装仕様変更は行わない。

### Phase 5: Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|DOC-OPS-05 Stream J2" 04_Documentation/configuration.md`
- `git diff --check`
- Self-correction policy: max 3 attempts, then stop and reassign if unresolved.

### Phase 6: Proceed
- 判定: **Ready**
- 根拠: 分類根拠・次アクション・検証一致を同一文書内で追跡可能。
