# セキュリティ指針（セルフホスト最小運用）


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
このドキュメントは、**イントラネット / VPN 内でのセルフホスト運用を前提**に、
MVP で実施しやすい最小限の保護策をまとめたものです。

## 0. 文書分類（DOC-OPS-05-13）

- Classification: **Improve external**（対外向けセキュリティ基底文書として維持）
- Audience: self-host運用者 / セキュリティレビュー担当 / 監査対応担当
- Goal: 安全境界（safeMode、strict例外、監査最小化）を公開可能な粒度で共有する
- Non-goal: 実装内部の秘匿情報公開、承認フローの独自再定義

### 0.1 AUTH-OPS-03 整合メモ（Context / Decision / Consequences）

#### Context

- strict mode例外緩和は `02_Architecture/strict_mode_exception_approval_flow.md` が正本で、D1〜D4が固定済み。
- 本書はセキュリティ基底方針、`04_Documentation/security_operational_guidelines.md` は運用選択時の補助ガイドとして責務分離する。

#### Decision

- 用語を `Security Officer / System Owner / Platform Operator` に統一し、承認2者と実行責務分離を明示する。
- D1〜D4 固定値を本書の strict 例外チェックへ明示的に取り込み、`TODO化せず停止` ルールを維持する。
- `security.md -> security_operational_guidelines.md -> operations.md` の導線を保持する。

#### Consequences

- セキュリティ方針・運用判断・実行手順の文書境界が明確になり、公開文書としての再利用性が向上する。
- DOC-OPS-02 の同期観点（用語/役割/導線/固定値）を継続監査しやすくなる。

### 0.2 Stream H 直列同期（security フェーズ）

Stream H では `operations.md` 同期完了後に本書を更新する。確認順序は次のとおり。

1. 役割語彙一致（Security Officer / System Owner / Platform Operator）
2. 状態遷移一致（`DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed`、未確定は `StoppedForClarification`）
3. 固定値一致（D1=4h、D2=2h、D3=代理承認なし、D4=48h/15m/60m）
4. 相互リンク一致（`security.md -> security_operational_guidelines.md -> operations.md -> e2e_testing.md`）

不一致が残る場合は e2e フェーズへ進まずに停止する。


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

### 3.1 CE2 低リスクAI支援のフェイルセーフ

CE2（低リスクAI支援）を有効化する場合、以下を最低セキュリティ契約として固定する。

1. AI出力は proposal としてのみ保持し、直接適用経路（auto-apply）を禁止する。
2. proposal は `proposalId/diff/sourceBundleHash/status/reviewState` を必須とする。
3. `reviewState` の `unreviewed -> reviewed` 昇格は人間の明示操作のみ許可する。
4. safeMode ON時は未レビュー本文をAI入力へ混入させない。
5. CE1最小I/Fモック契約との差異を検知した場合は `status=held` で停止し、指示待ちとする。

> 停止トリガ（review自動昇格 / safeMode後退 / 直接適用経路）を検知した場合は、
> セキュリティイベントとして扱い、適用を進めないこと。

## 4. 実施しやすい最小コントロール

まずは以下の4点を推奨します。

1. **プロキシでIP許可リスト**を設定（到達元を社内セグメントやVPNに限定）
2. **プロキシでBasic認証**を有効化（簡易保護）
   - ただし原則は local/dev のみ。`DEV_BASIC_AUTH_ENABLED=true` などの明示的な環境変数がある場合に限定し、`docker-compose.local.yml` でのみ指定する。
3. **APIネットワークとDBネットワークを分離**（不要な到達経路を減らす）
4. **定期バックアップと定期パッチ**（OS / コンテナ / 依存ライブラリ）

## 5. 任意: APIキーによる簡易保護（バックエンド）

バックエンドは `KJ_ATLAS_API_KEY` を設定した場合のみ、簡易なヘッダ認証を有効化できます。

- 環境変数 `KJ_ATLAS_API_KEY` が **未設定**: 現在と同じく全APIを許可
- 環境変数 `KJ_ATLAS_API_KEY` が **設定済み**: `/healthz` 以外で `X-API-Key: <KJ_ATLAS_API_KEY>` を必須化
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


## 7.9 運用ガイドライン参照

strict / non-strict いずれの運用プロファイルでも、組織ごとの採否判断は
`04_Documentation/security_operational_guidelines.md` を参照してください。

## 8. Strict provisioning 運用（AUTH-API-02）

`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`の strict mode では、未登録subjectを必ず拒否します。

- 拒否契約: `403` + `{"code":"identity_not_provisioned","message":"Identity not provisioned. Pre-provision via /admin/provision/users before access."}`
- 回復導線: `POST /admin/provision/users`
  - request: `{ "provider": "saml", "externalUid": "alice", "displayName": "Alice" }`
  - create時: `201` + `provisioned=true`
  - 再試行: `200` + `provisioned=false`
  - 既存identityに矛盾する `displayName/email` は `409 identity_already_provisioned_conflict`

運用上、strict緩和（`KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` への切替）は承認フローを経て記録してください。

### 8.0.0 この節の登場人物

- **Security Officer**: セキュリティ妥当性を確認する責任者。
- **System Owner**: 業務継続・提供責任を持つ責任者。
- **Platform Operator**: 設定変更と運用記録を担当する実行者。

### 8.0 strict mode とは何か（セキュリティ観点 / 初学者向け詳細）

ここでは認証の専門用語を最小限にし、strict mode を「なぜ必要か」から順に説明します。

まず結論として、strict mode は次の制御です。

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` を有効化する
- **未登録の利用者は、自動でユーザー作成せず拒否する**
- 利用を許可するには、管理者が先に登録する

---

#### 8.0.1 前提知識ミニ用語集（3つだけ）

- **認証（Authentication）**: 「あなたは誰か」を確認すること（例: SSOログイン）。
- **認可（Authorization）**: 「その人にこの操作を許すか」を決めること。
- **JIT Provisioning**: 初回アクセス時に、その場でユーザーを自動作成する方式。

strict mode は、このうち **JIT Provisioning を止める設定**です。

---

#### 8.0.2 strict mode で実際に何が起こるか

1. 利用者がSSOでログインし、認証は成功する。
2. しかしアプリ内に未登録なら、APIは `403 identity_not_provisioned` を返す。
3. 管理者が `/admin/provision/users` で事前登録する。
4. その後のアクセスで初めて利用可能になる。

重要なのは、**「ログインできた」だけでは使えない**という点です。
これにより、誤って到達した主体をその場で受け入れない設計になります。

---

#### 8.0.3 strict mode を使わない場合に起きやすい問題

1. **IdP設定ミスの受け入れ事故**
   - 例: IdPの属性マッピングが誤り、想定外の `externalUid` が到達する。
   - JIT有効時: 到達した時点で自動作成され、意図せず利用可能になる。
   - strict mode: 未登録として拒否されるため、被害が初回で止まる。

2. **なりすまし・誤同定の早期侵入**
   - 例: `provider/externalUid` の連携ミスや重複。
   - JIT有効時: 最初のアクセスでアカウント生成 → 事後調査まで露出が続く。
   - strict mode: 自動生成が起こらず、調査前のアクセス成立を防げる。

3. **障害対応中のフェイルオープン拡大**
   - 例: 夜間障害で緩和設定を急いで適用し、誰を許可したか追跡不能になる。
   - strict mode + 承認フロー: 2者承認・記録・復旧が必須となり、拡大を抑えられる。

---

#### 8.0.4 セキュリティ効果を平易に言うと

- **Attack Surface（攻撃面）縮小**
  - 「認証に通った全員」ではなく「登録済みの人だけ」を受け入れる。
- **Blast Radius（影響範囲）抑制**
  - 誤設定があっても、自動受け入れされないため被害が連鎖しにくい。
- **監査しやすい運用**
  - 「誰を、いつ、なぜ許可したか」を追える。
- **単独ミスの抑止**
  - 承認者と実行者を分離し、1人の判断ミスで恒常緩和しにくくする。

---

#### 8.0.5 実装・運用で守る最小ルール

- 本番標準プロファイルは `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`（strict）とする。
- `true` を使う場合は、次のどちらかを明確に選ぶ。
  - **例外プロファイル**: 期限付き・承認付きで一時的に利用し、終了時に `false` へ戻す。
  - **公開運用プロファイル**: 組織方針として `true` を継続利用する（後述 8.0.6）。
- どちらのプロファイルでも、監査ログにPII（subject生値、roles/groups/policyRef生値など）を残さない。

---

#### 8.0.6 公開運用プロファイル（`true` を継続利用する場合）

SNS的な多ユーザ閲覧など、
「未登録ユーザを都度受け入れる」運用を選ぶケースは現実にあり得る。
その場合、`KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` の恒常運用を**禁止しない**。
ただし、strictよりリスクが広がるため、次の補完統制を推奨ガイドラインとして明示する。

- **アクセス境界**: 認証強制（OIDC/SAML）+ 必要最小限の公開範囲設計。
- **権限分離**: 閲覧中心（read）と編集権限（write/share/export）を明確に分離。
- **観測性**: 初回作成件数・異常増加・短時間大量作成を監視し、閾値超過でアラート。
- **自動抑止**: 不審パターン時に `read_only` へフェイルセーフ、または一時的に strictへ戻せる運用手順を準備。
- **審査**: 恒常 `true` 採用時は、運用ポリシー（対象環境/対象テナント/責任者/SLA）を文書化し、定期レビューする。

---

#### 8.0.7 よくある誤解

- 誤解1: 「strict mode = 認証を強くする機能」
  - 実際: 認証の強度そのものより、**受け入れ条件（事前登録必須）**を強化する機能。

- 誤解2: 「開発効率が落ちるだけ」
  - 実際: 事前登録の手間は増えるが、誤受け入れ事故の対応コストを下げる。

- 誤解3: 「一度緩和したらそのままでも問題ない」
  - 実際: 補完統制なしの緩和常態化は管理境界を崩す。継続運用する場合は 8.0.6 の公開運用プロファイル要件を満たす。

#### 8.0.8 事前ユーザ登録の実務パターン（具体例）

strict mode では「アクセス時に自動作成しない」ため、
本アプリ外で事前登録フローを持つか、組織イベントと連携して登録する運用が必要になる。

**パターンA: 本アプリ外の承認プロセスで事前登録する**

- 想定: 情報システム部門がチケット/ワークフロー（ServiceNow/Jira/社内申請）で利用申請を受ける。
- 最低手順:
  1. 申請者の所属・利用目的・権限レベルを承認者が確認。
  2. 承認後、運用担当が `/admin/provision/users` を実行。
  3. 実行結果（`201` or `200`）をチケットへ記録してクローズ。
- メリット: 既存の社内統制（職務分離・監査証跡）をそのまま使える。

例（手動登録API呼び出し）:

```bash
curl -X POST http://localhost:8000/admin/provision/users \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: <admin-api-key>' \
  -d '{
    "provider": "saml",
    "externalUid": "a12345",
    "displayName": "Taro Example",
    "email": "taro@example.co.jp"
  }'
```

**パターンB: 組織の異動イベントと連携して自動事前登録する**

- 想定: 人事異動・入社イベント（HRIS/IdM）をトリガに、連携バッチやWebhookで本APIを呼ぶ。
- 最低手順:
  1. 人事イベント（入社/異動/兼務開始）を受信。
  2. 対象ユーザの `provider/externalUid` を解決。
  3. `/admin/provision/users` を冪等で実行（重複時 `200` を許容）。
  4. 成功/失敗を運用監視へ通知し、失敗は再実行キューへ入れる。
- メリット: 初回ログイン前に登録が完了し、オンボーディング遅延を減らせる。

例（疑似コード）:

```python
for event in hr_events:
    if event.type in {"hire", "transfer", "assignment_start"}:
        payload = {
            "provider": "saml",
            "externalUid": event.employee_id,
            "displayName": event.display_name,
            "email": event.email,
        }
        resp = post("/admin/provision/users", json=payload)
        assert resp.status_code in {200, 201}
```

**どちらのパターンでも必須の注意点**

- `provider` と `externalUid` の正規化規則を固定する（前後空白・大文字小文字・文字種）。
- 失敗時（`409` など）の運用フローを先に決める（手動確認担当、SLA、再試行回数）。
- APIキー/トークンをチケット本文やログに残さない。
- 退職・権限剥奪イベント時の無効化手順（別API/別運用）を合わせて定義する。

### 8.1 strict mode例外時の安全性チェック（AUTH-OPS-03 / T3）

参照正本: `02_Architecture/strict_mode_exception_approval_flow.md` 6.8節（D1〜D4固定）、`04_Documentation/operations.md`（Runbook運用）。

- D1: Security Officer先行、承認TTL=4h
- D2: tenant単位、最大2h（超過時はstrictへ自動復帰）
- D3: 2者共同判定、代理承認なし
- D4: 変更台帳+監査ID相互参照、48hレビュー、15m一次/60m二次エスカレーション

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
- [ ] D1〜D4 固定値から逸脱する項目がある場合、**TODO化せず「確認待ちで停止」**として扱っている。

### 8.1.1 strict mode例外の時系列セキュリティ確認

運用時は `operations.md` 3.5 の時系列Runbookに追従し、セキュリティ確認を次の順で実施する。

1. Requested: 申請IDを発行し、対象tenant・理由・復旧条件を記録。
2. Approved: Security Officer → System Owner の順で承認し、TTL=4h内に完了。
3. ExceptionActive: PII非保存・SafeMode境界維持・代理承認なしを確認しながら運用。
4. RollbackPending: 最大2h到達または停止条件成立で即時復旧を開始。
5. Closed: strict復帰検証を記録し、48h以内の事後レビュー計画を確定。
6. StoppedForClarification: 1項目でも未確定があれば停止し、回答確定まで切替禁止。

監査証跡の責務分離:
- Security Officer / System Owner は承認判断と妥当性確認を担当。
- Platform Operator は承認済み内容のみを実行し、変更台帳・監査IDの相互参照を記録。

状態語彙マッピング（AUTH-OPS-03 canonical との整合）:

| Runbook語彙（operations/security） | Canonical語彙（`strict_mode_exception_approval_flow.md`） | 意味 |
|---|---|---|
| `Requested` | `DraftRequest` / `ApprovalPending` | 申請作成〜承認待ち。 |
| `ExceptionActive` | `ActiveException` | 一時緩和が適用中。 |

> 注記: 運用文書では時系列説明を優先して `Requested` / `ExceptionActive` を用いるが、承認判定と監査判定は canonical と同一に扱う。

### 8.2 監査最小化・PII最小化ルール（strict mode例外ログ）

strict mode例外ログは、以下の5項目のみを最低監査項目として保存する。

- [ ] 時刻（開始時刻/終了時刻、UTC推奨）
- [ ] 例外理由（定型カテゴリ + 短文理由）
- [ ] 承認者（Security Officer / System Owner の識別子）
- [ ] 対象環境（prod/stg/dev など）
- [ ] 復旧条件（`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ戻す判定条件）

PII非保存ルール:

- [ ] subject生値（メール/外部UID/表示名）をログへ保存しない。
- [ ] `roles/groups/policyRef` の生値をログへ保存しない（必要時は件数やハッシュ化IDのみ）。
- [ ] 申請本文・添付・チャット転記など自由記述にPIIを含めない。
- [ ] 診断に必要な場合でも、PIIを含む原文は監査ログへ転記せず、別系統のアクセス制御下で管理する。

### 8.3 未確定事項の扱い（停止条件）

固定値再掲（D1〜D4）: 承認順序=Security Officer先行・承認TTL=4h、scope=tenant/最大2h、代理承認なし、変更台帳+監査ID相互参照、48hレビュー+15m/60mエスカレーション。

- 未確定事項は TODO として先送りしない（停止条件）。
- strict mode例外の実行可否に関わる未確定事項が1つでもある場合、状態を**`StoppedForClarification`（確認待ちで停止）**と明記する。
- 「確認待ちで停止」中は、回答確定まで `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` への切替を禁止する。

#### 停止条件（推測禁止）

- 承認順序・承認有効期限・代理承認・違反時SLAなどの未確定フローを決めないと運用できない場合、推測で確定せず停止する。
- 停止時は質問リストを更新し、状態を `StoppedForClarification`（確認待ちで停止）と明記したうえで、回答が得られるまで strict 例外の実行を禁止する。

## HIL-RS-02-A3 セキュリティ運用境界（仮運用 / モック証跡）

A1契約・A2仕様の文書同期として、次フェーズ運用時の最小境界を固定する。


参照契約（A1）:

- RequirementID: `HIL-RS-01-A1`
- 契約境界: Critique入力 / 再提案差分 / レビュー帰属
- Contract Keys: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`
- Freeze Flags: `contractLinkLocked=true` / `sharedResourceFreeze=true`
- 契約参照先（正本）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`

仮運用タグ（依存切断ルール）:

- `status=provisional`
- `evidenceType=mock-trace`
- `replaceOnNextSync=true`
- A2の実コード完成を待たず、A1契約I/Fと想定運用フローに基づく暫定同期として扱う。

- SafeMode既定ON、および share/export 漏えい防止の既存制約を変更しない。
- Critique→再提案の反復は候補提示として扱い、確定操作は人間操作のみで実施する。
- 単一スコア/ランキング等、単一正解を示唆する運用を追加しない。
- 可逆性を損なう一方向の自動確定フローを導入しない。


実装整合メモ（B handoff反映済み）:

- `HilRsWorkflowPanel` の3導線（Candidate comparison / Critique input / Diff visualization）をセキュリティ境界の操作単位として扱う。
- UI固定文言（A2実装との一致を維持）:
  - `A2-1 Candidate comparison` → `Collect and compare merge/layout candidates before any commit.`
  - `A2-2 Critique input` → `Capture critique and re-suggest iteratively while keeping human final approval.`
  - `A2-3 Diff visualization` → `Review deterministic diffs before apply/discard to keep the workflow reversible.`
- Critique / attribution payload は `provider` / `external_uid` / `email` 等のPII-like identity fieldsを許可しない。
- Critique payload は既知タグのみ型変換し、未知タグのみ・tags未指定時は `no_articulable_reason` を採用する（空コメント+空tagsは監査入力を発行しない）。
- 再提案差分は `before/after` を必須にして逆操作不能データを拒否する。

責務分離（A2挙動との整合）:

- Security Officer / System Owner は運用境界と停止条件の妥当性を承認する。
- Platform Operator は承認済み境界のみを実行し、推測で運用拡張しない。
- 人間レビュー帰属の確定は、監査最小項目とPII最小化ルールに従って記録する。

非目標（A3で追加しない事項）:

- 単一スコアでの自動ランキング
- 人間承認を省略する自動確定
- SafeMode既定ONの緩和

ロールバック条件（A3同期の停止/差し戻し）:

- Contract Keys / Freeze Flags のいずれかに不一致がある。
- `traceKey` 欠落や可逆差分欠落など、A2 handoff の必須整合に違反する。
- PII-like field拒否・人間レビュー帰属必須のいずれかを満たせない。

ロールバック手順:

1. 文書更新を停止し、逸脱箇所（契約ID/固定値/実装差分）を列挙する。
2. A1正本（`02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`）へ照合し、差分をA1差し戻しとして起票する。
3. 差分解消までA3更新を再開しない（推測補完禁止）。

### 8.2.1 異常時ロールバック実施ログ（仮運用）

- `rollbackReason`: `contract_mismatch | freeze_flag_violation | pii_violation | rediff_missing`
- `rollbackStatus`: `rollback_pending | rollback_done`
- `rollbackBy`: `Platform Operator`
- `approvalRef`: Security Officer / System Owner の承認参照ID
- `reopenCondition`: A1差し戻し解消 + docs-check再実行成功

### 8.2.2 監査証跡の必須最小項目（可逆統合フロー）

可逆統合フロー（A2-1〜A2-3）では、次の項目を監査証跡の必須最小として固定する。

- `requirementId=HIL-RS-01-A1`
- `syncScope=HIL-RS-02-A3`
- `phase=candidate_comparison | critique_input | diff_visualization`
- `decisionPending=true|false`（候補提示中は `true`）
- `traceKeyPresence=true`（欠落時はロールバック）
- `piiMinimized=true`（PII-like field 非保存）

禁止事項:
- `provider` / `external_uid` / `email` など identity fields の生値を監査ログへ保存しない。
- free-text を根拠なく二次転記しない（必要時は別系統のアクセス制御下で管理）。

上記に抵触する変更が必要な場合は、実装を停止し `ADR-0026` と上位層（00〜02）で先に合意する。

### 8.3 Stream B（FB-P2B-01 / FB-P2B-02）運用の安全境界

Similar-card 候補提示と Manual assisted merge は、次の安全境界を満たす場合のみ運用する。

- 候補提示は deterministic heuristic に限定し、AI による自動確定を禁止する。
- 最終 decision は人間が `accept` / `partial` / `reject` / `defer` を明示選択する。
- decision 記録は監査目的であり、`accept` を契機に即時自動統合しない。
- read-only モードでは候補収集・decision 記録を禁止する。

契約固定値:

- Candidate contract: `CTR-2B-01-CANDIDATE-GROUP-V1`
- Decision log contract: `CTR-2B-02-DECISION-LOG-V1`

逸脱時の扱い:

- 4値以外の decision を許容する変更
- contractVersion を未固定化する変更
- human-in-the-loop を弱める自動確定導線

上記いずれかを検知した場合、運用更新を停止し、A1契約レビュー（Stream C/D）へ差し戻す。
