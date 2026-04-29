# セキュリティ指針（セルフホスト最小運用）


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
このドキュメントは、**イントラネット / VPN 内でのセルフホスト運用を前提**に、
MVP で実施しやすい最小限の保護策をまとめたものです。

## 0. 文書分類（DOC-OPS-05-13）

- Classification: **Improve external**（対外向けセキュリティ基底文書として維持）
- Audience: self-host運用者 / セキュリティレビュー担当 / 監査対応担当
- Goal: 安全境界（safeMode、strict例外、監査最小化）を公開可能な粒度で共有する
- Non-goal: 実装内部の秘匿情報公開、承認フローの独自再定義
- Public boundary: 秘密情報・組織固有の内部統制詳細は除外し、公開可能な安全境界と運用原則のみ扱う
- Outcome: 運用者が safeMode・strict例外・監査最小要件の優先順位を誤解なく適用できる
- Related: `02_Architecture/strict_mode_exception_approval_flow.md`, `04_Documentation/security_operational_guidelines.md`, `04_Documentation/operations.md`, `01_Plans/issues/issue-doc-ops-05-13-04doc-security.md`

## DOC-OPS-05 統合同期メモ（2026-04-18）

- 連携 issue: `issue-doc-ops-05-06` / `issue-doc-ops-05-11` / `issue-doc-ops-05-13` / `issue-doc-ops-05-14`
- canonical 用語: `Security Officer / System Owner / Platform Operator`
- canonical 状態語彙: `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed`（未確定時 `StoppedForClarification`）
- fixed values (D1〜D4): `4h / 2h / 代理承認なし / 48h + 15m/60m`
- 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md`（`operations.md` は runbook 同値確認先）

### 0.1 AUTH-OPS-03 整合メモ（Context / Decision / Consequences）

#### Context

- strict mode例外緩和は `02_Architecture/strict_mode_exception_approval_flow.md` が正本で、D1〜D4が固定済み。
- 本書はセキュリティ基底方針、`04_Documentation/security_operational_guidelines.md` は運用選択時の補助ガイドとして責務分離する。

#### Decision

- 用語を `Security Officer / System Owner / Platform Operator` に統一し、承認2者と実行責務分離を明示する。
- D1〜D4 固定値を本書の strict 例外チェックへ明示的に取り込み、`TODO化せず停止` ルールを維持する。
- `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` の主導線を保持し、`operations.md` は runbook 整合確認先として並行参照する。

#### Consequences

- セキュリティ方針・運用判断・実行手順の文書境界が明確になり、公開文書としての再利用性が向上する。
- DOC-OPS-02 の同期観点（用語/役割/導線/固定値）を継続監査しやすくなる。

### 0.2 Stream F 直列同期（security フェーズ）

Stream F では `02_Architecture/strict_mode_exception_approval_flow.md` を正本として、
`security.md -> security_operational_guidelines.md -> e2e_testing.md` の順で同期する。
`operations.md` は runbook 正本として常時照合し、語彙・責務・固定値の同値性を確認する。

### 0.2.1 Stream D 実行メモ（security docs-only）

本書を Stream D 専任で更新する場合は、編集対象を `operations.md` / `security.md` / `security_operational_guidelines.md` に限定し、次を満たすまで Proceed しない。

1. 役割語彙一致（Security Officer / System Owner / Platform Operator）
2. 状態遷移一致（`DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed`、未確定は `StoppedForClarification`）
3. 固定値一致（D1=4h、D2=2h、D3=代理承認なし、D4=48h/15m/60m）
4. 相互リンク一致（`strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md`）
5. 承認未了の決定（未確定Q項目・再承認待ち）を確定事項として本文へ反映していない
6. docs-check（リンク整合 + 固定値照合 + `git diff --check`）が成功

不一致が残る場合は e2e フェーズへ進まずに停止する。D1〜D4 の不整合を検知した場合は即時停止する。

### 0.3 セキュリティ文書整合チェック（必須4観点）

security系文書の更新時は、次の4観点を **Verifyで必ず同時確認** する。

1. 用語: `Security Officer / System Owner / Platform Operator` を混在なく使用していること
2. 役割: 2者承認（Security Officer + System Owner）と実行責務分離（Platform Operator）を維持していること
3. 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` の参照導線が維持されていること
4. 固定値: D1〜D4（4h / 2h / 代理承認なし / 48h+15m/60m）が改変されていないこと


## 0.4 責務境界（security の単一責務）

### 対象読者
- Security Officer（セキュリティ妥当性の責任者）
- System Owner（業務継続責任者）
- 監査・レビュー担当

### 前提知識
- `strict_mode_exception_approval_flow.md` の承認制度と D1〜D4 固定値を理解していること
- `operations.md` が運用手順の正本であり、本書は手順書ではないこと
- `security_operational_guidelines.md` が運用判断補助であること

### 公開してよい情報
- SafeMode既定ON、share/export漏えい防止、review昇格制約などの安全境界
- strict例外運用で後退禁止とする必須制約
- 公開可能な最小コントロール（ネットワーク境界、鍵管理原則、整合チェック）

### 本書で扱わない情報（operations / guidelines へ委譲）
- 手順コマンド中心のRunbook詳細（`operations.md`）
- プロファイル選択時のケース別判断フロー（`security_operational_guidelines.md`）

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

## 7.10 同一ワークフロー（Read → C/D/C → Execute → Verify → Proceed）

`security.md` の更新は、次の同一ワークフローで固定する。

1. **Read**
   - `strict_mode_exception_approval_flow.md` / `security_operational_guidelines.md` / `operations.md` の導線を再確認する。
   - D1〜D4、役割語彙、SafeMode境界にドリフトがないことを確認する。
2. **ADR CDC**
   - Context: 本書は「セキュリティ基底方針」であり、承認フロー正本の代替ではない。
   - Decision: 4観点（用語/役割/導線/固定値）を Verify 必須項目として固定する。
   - Consequences: security系文書の横断ドリフトを公開文書だけで検知しやすくなる。
3. **Plan**
   - `strict_mode_exception_approval_flow.md` を正本として再読し、D1〜D4・役割語彙・導線を確認する。
   - SafeMode 既定ONと share/export 漏洩防止の後退表現が混入していないことを確認する。
4. **Execute**
   - 本書は「基底セキュリティ方針」に限定し、承認フロー仕様の独自再定義を行わない。
5. **Verify**
   - docs-check / diff-check で整合を確認する。
   - 不一致時は最小修正で再検証し、**自己修復は最大3回**までとする。
6. **Proceed**
   - 3回で収束しない場合は fail-safe 停止し、未解決論点を issue memo に記録する。

### 後退禁止（Fail-safe即停止）

- SafeMode 既定ONの緩和
- share/export 漏洩防止境界の緩和
- review自動昇格・auto-apply・未承認状態の確定扱い
- 承認未了の決定事項（未確定Q項目、再承認待ち差分）の本文反映

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

1. DraftRequest: 申請IDを発行し、対象tenant・理由・復旧条件を記録。
2. ApprovalPending -> Approved: Security Officer → System Owner の順で承認し、TTL=4h内に完了。
3. ActiveException: PII非保存・SafeMode境界維持・代理承認なしを確認しながら運用。
4. RollbackPending: 最大2h到達または停止条件成立で即時復旧を開始。
5. Closed: strict復帰検証を記録し、48h以内の事後レビュー計画を確定。
6. StoppedForClarification: 1項目でも未確定があれば停止し、回答確定まで切替禁止。

監査証跡の責務分離:
- Security Officer / System Owner は承認判断と妥当性確認を担当。
- Platform Operator は承認済み内容のみを実行し、変更台帳・監査IDの相互参照を記録。

状態語彙は `02_Architecture/strict_mode_exception_approval_flow.md` の canonical 語彙（`DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed` と `StoppedForClarification`）に固定する。

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


## Stream G docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **CDC**: Context / Decision / Consequences を明文化し、分類結果（Move internal / Improve external）を固定する。
3. **Plan**: AC/DoD を先に定義し、docs-only スコープ（`03_Implement/**` 非変更）を明示する。
4. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
5. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
6. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## 0.4 Phase 1-5 実行記録（2026-04-16 / DOC-OPS-05-13）

- Phase 1 Read: 各Phase開始時に `security.md` / `security_operational_guidelines.md` / `operations.md` / `strict_mode_exception_approval_flow.md` を再Read。
- Phase 2 Plan: docs-only かつ基底セキュリティ方針に限定し、承認フロー仕様の再定義を禁止。
- Phase 3 Execute: 公開境界を維持しつつ、security系必須4観点（語彙・役割・導線・固定値）を同期。
- Phase 4 Verify（必須）:
  - 語彙: `Security Officer / System Owner / Platform Operator`
  - 役割: 2者承認（Security Officer + System Owner）と実行責務分離（Platform Operator）
  - 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md`（`operations.md` は runbook 同値確認先として並行参照）
  - 固定値: D1=4h, D2=2h, D3=代理承認なし, D4=48h+15m/60m
  - 実施コマンド: `rg` と `git diff --check`
- Phase 5 Proceed: 判定は **Ready**。Verify不一致が3回で収束しない場合は **StoppedForClarification**。

## Stream H 専任: DOC-OPS-05後半 実行記録（2026-04-16）

### Phase 1 Read

- 対象本文と関連正本（`00_Prompt/*` / `01_Plans/adr/ADR-0001` / `02_Architecture/*`）を再読し、公開境界を確認した。
- 用語・責務の整合（特に security 系は `Security Officer / System Owner / Platform Operator`）を事前確認した。

### Phase 2 Plan（AC/DoD補完）

- AC補完:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の冒頭メタを維持する。
  - 本文は docs-only で更新し、実装仕様・設定値の新規決定を持ち込まない。
  - 参照導線（関連文書・issue memo）を切断しない。
- DoD補完:
  - Read → Plan → Execute → Verify → Proceed の記録を残す。
  - Verify で `docs-check` とリンク整合を確認する。

### Phase 3 Execute

- 本文の方針を維持したまま、Stream H後半の実行責務（Phase運用・停止条件）を追記した。
- 編集範囲外（backend/frontendコード、shared統合3ファイル）は変更しない。

### Phase 4 Verify（docs-check + リンク整合）

- `rg` で必須メタ語彙・Phase見出し・停止条件語彙を確認した。
- `git diff --check` で体裁崩れがないことを確認した。
- security 系は D1〜D4 と役割語彙の整合を追加確認した。

### Phase 5 Proceed

- 判定: **Ready**
- 継続条件: 次回更新でも同一フェーズ順序と docs-only 制約を維持する。

### 停止条件（固定）

- 責務用語不整合（`Security Officer / System Owner / Platform Operator` の混在・崩れ）を検知した場合は停止。
- D1〜D4 固定値矛盾（`4h / 2h / 代理承認なし / 48h+15m/60m`）を検知した場合は停止。
- Verify の自己修復が3回を超える場合は `StoppedForClarification` として停止。

## Stream I 専任サイクル（DOC-OPS-05 security / 2026-04-18）

### Phase 1) Read

- `strict_mode_exception_approval_flow.md` / `security_operational_guidelines.md` / `operations.md` の導線を再確認し、用語・役割・固定値（D1〜D4）を再読した。
- Stream G 競合回避のため、編集対象を `operations.md` / `security.md` / `security_operational_guidelines.md` と対応issueのみに固定した。

### Phase 2) Plan（語彙・責務・導線・固定値）

- 語彙: `Security Officer / System Owner / Platform Operator` を維持。
- 責務: 2者承認（Security Officer + System Owner）と実行責務分離（Platform Operator）を維持。
- 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` を維持。
- 固定値: D1=4h, D2=2h, D3=代理承認なし, D4=48h + 15m/60m を維持。

### Phase 3) Execute

- 本書に Stream I の実行記録を追加し、docs-only スコープ外（実装コード / shared files）の編集を行わない。

### Phase 4) Verify（docs-check + 参照整合）

- docs-check: `rg` で語彙・責務・導線・固定値の一致を確認。
- 参照整合: 関連文書・対応issueで同一ワークフローと停止条件（修復3回上限）を照合。

### Phase 5) Proceed（運用注意点）

- 判定: **Ready**（Stream G 競合検出なし）。
- 運用注意点: 競合検出時は即停止、Verify失敗の自己修復は最大3回まで。3回超過時は `StoppedForClarification` として停止する。

## 12. Stream K docs-only execution log（2026-04-19 / DOC-OPS-05-13）

### Phase 1 Read

- `security.md` / `security_operational_guidelines.md` と対応issue（DOC-OPS-05-13, 05-14）を再読し、公開境界・役割語彙・D1〜D4・導線の整合を確認。

### Phase 2 ADR CDC

- Context: 本書は公開向けの基底セキュリティ方針であり、承認フロー仕様の正本ではない。
- Decision: 既存の分類（Improve external）と Fail-safe 条件を維持し、仕様値の追加変更は行わない。
- Consequences: 文書責務を維持したまま、Stream K の docs-only 証跡を追加できる。

### Phase 3 Plan

- docs-only で最小差分更新。
- Verify は docs-check（語彙/導線/固定値確認）+ `git diff --check` を必須化。

### Phase 4 Execute

- 本節を追加し、Stream K の実行証跡を明文化。
- SafeMode既定ON・share/export漏洩防止・承認責務分離に関する既存記述は変更しない。

### Phase 5 Verify

- 実施: `rg -n "Stream K docs-only execution log|Phase 1 Read|Phase 5 Verify|D1|D2|D3|D4|Security Officer|System Owner|Platform Operator" 04_Documentation/security.md`
- 実施: `git diff --check`
- 結果: 体裁崩れなし。自己修復 0/3。

### Phase 6 Proceed

- 判定: **Ready**
- 停止条件: 役割語彙・導線・固定値（D1〜D4）不一致、または自己修復3回超過を検知した場合は `StoppedForClarification` で停止。

## Stream F HIL-RS-02-A3 sync log（2026-04-19）

- Phase 1 Read: `strict_mode_exception_approval_flow.md` を正本として再読し、`security.md` / `operations.md` / `e2e_testing.md` と導線整合を確認。
- Phase 2 用語同期: `Security Officer / System Owner / Platform Operator` を維持し、2者承認+実行責務分離を再確認。
- Phase 3 D1〜D4整合: D1=4h、D2=2h、D3=代理承認なし、D4=48h+15m/60m の一致を再確認。
- Phase 4 Verify: docs-check（語彙・固定値・リンク・diff）を実施し不整合0件。
- Phase 5 Proceed: **Ready**。差分再発時は fail-safe に従い `StoppedForClarification` で停止。

## Stream G 実行記録（DOC-OPS-05文書群② / 2026-04-19）

### Phase 1 Read同期
- `strict_mode_exception_approval_flow.md` を起点に、`security.md` / `security_operational_guidelines.md` / `operations.md` の記述を再読し、用語・責務分離・固定値（D1〜D4）の一致を確認した。
- 導線 `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` を維持し、`operations.md` を runbook 同値確認先として照合した。

### Phase 2 CDC明文化（判断分岐時のみ）
- 判定: **分岐なし（CDC追加なし）**。
- 理由: 本書の分類（Improve external）と責務（基底セキュリティ方針）は既存確定事項で、代替判断を追加していない。

### Phase 3 Execute（文書更新）
- Stream G の実行証跡を追記し、既存のフェイルセーフ境界（SafeMode既定ON、share/export漏洩防止、未承認事項の確定禁止）を再確認した。
- D1〜D4 と役割語彙の固定契約を維持した。

### Phase 4 Verify（docs-check + 用語/固定値照合）
- docs-check: `rg -n "Security Officer|System Owner|Platform Operator|D1|D2|D3|D4|StoppedForClarification" 04_Documentation/security.md 04_Documentation/security_operational_guidelines.md 04_Documentation/operations.md`
- diff-check: `git diff --check`
- 判定: Pass（語彙一致、固定値一致、フォーマット異常なし）。

### Phase 5 Proceed/Stop
- 判定: **Proceed（Ready）**。
- 停止条件: Verify不一致が自己修復3回で収束しない場合は `StoppedForClarification` として停止する。

## Stream E serial cycle（2026-04-20 / DOC-OPS-05後半 docs-only）

### Phase 1 Read
- 本文先頭メタ（Classification / Audience / Goal / Non-goal / Public boundary / Outcome / Related）を再確認。

### Phase 2 Plan
- 変更は docs-only に限定し、Plan→Execute→Verify→Proceed の固定順序で進める。
- Verify失敗時の自己修復は最大3回、4回目相当は停止する。

### Phase 3 Execute
- 本文の公開境界・導線を維持し、safeMode既定ON／漏えい防止後退禁止を再確認。

### Phase 4 Verify
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Outcome|Related" 04_Documentation/security.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**。
- 次担当へ: 致命的矛盾（上位文書不整合・安全境界後退・自己修復3回超過）を検知した場合は停止してIssueへ記録する。

## 0.5 Track 4 sync addendum（2026-04-22）

- Track 4 直列順序は `05-05 → 05-11 → 05-13 → 05-14`。
- 各Phase開始時に Read同期し、用語・役割・導線・固定値（D1〜D4）を照合する。
- ADRタスクは Context / Decision / Consequences を先行記録し、DecisionStatus承認確認後に Execute する。
- Verify失敗時は自己修復を最大3回まで許可し、4回目相当は fail-safe 停止とする。

## 13. Stream M serial update log（2026-04-22 / security担当）

### Phase 1 Read
- 正本 `02_Architecture/strict_mode_exception_approval_flow.md` を再読し、AUTH系固定値 D1〜D4 と canonical 用語を確認。
- 直列同期対象 `security.md -> security_operational_guidelines.md` を確定し、同一ワークフロー（Read→Plan→Execute→Verify→Proceed）を再確認。

### Phase 2 Plan
- 用語を `Security Officer / System Owner / Platform Operator` へ固定。
- 責務分離（2者承認 + Platform Operator実行）を維持。
- 固定値 D1=4h / D2=2h / D3=代理承認なし / D4=48h+15m/60m を改変しない。
- 不一致時は `StoppedForClarification` で停止し、自己修復は最大3回まで。

### Phase 3 Execute
- 本節を追記し、security系の直列更新証跡のみを追加（docs-only）。
- SafeMode既定ON、share/export漏えい防止、承認フロー正本の再定義禁止を維持。

### Phase 4 Verify
- docs-check（語彙・責務・導線・D1〜D4）を `rg` で確認。
- `git diff --check` で体裁崩れがないことを確認。

### Phase 5 Proceed
- 判定: **Ready**。
- フェイルセーフ: D1〜D4不一致、責務分離崩れ、導線切断、または自己修復3回超過時は停止。

## 0.6 Stream L serial lane log（2026-04-26 / DOC-OPS-05-13）

### Phase 1 Read
- `issue-doc-ops-05-13-04doc-security.md` と本書、`security_operational_guidelines.md` / `operations.md` の導線を再確認。

### Phase 2 ADR/CDC
- Context: 本書は安全境界の基底方針で、運用判断補助やrunbookの代替ではない。
- Decision: `Improve external` を維持し、safeMode既定ON・share/export漏洩防止・用語3種・2者承認と実行分離・D1〜D4固定を Verify 前提へ固定。
- Consequences: 公開境界を維持しつつ、security系文書の横断ドリフトを検知しやすくなる。

### Phase 3 Plan
- Scope: docs-only 追記。
- Non-goal: 実装/設定の仕様追加、承認制度の再定義。
- AC/DoD: 4観点（用語/役割/導線/固定値）と停止条件を維持。
- Validation: `rg` / `git diff --check`。
- Stop: 自己修復3回超過、不一致未収束。

### Phase 4 Execute
- 本節を追加し、DOC-OPS-05-13直列完遂の記録を残した。

### Phase 5 Verify
- docs-check観点で不整合なし（自己修復 0/3）。

### Phase 6 Proceed
- 判定: **Ready**（次順序は security_operational_guidelines）。

## Stream F HIL-RS-02-A3 security sync log（2026-04-27）

### Phase 1 Read
- A3固定キー（`freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON`）を再読し、後退がないことを確認。
- 役割語彙を `Security Officer / System Owner / Platform Operator` で固定。

### Phase 2 Plan
- 本書の責務をセキュリティ境界（SafeMode既定ON、PII最小化、人間承認分離）に限定し、A3で契約再定義を行わない。

### Phase 3 Execute
- A3 docs-only 同期記録を追記し、`contractLinkLocked=true` / `sharedResourceFreeze=true` の freeze 条件を security 側でも再確認。

### Phase 4 Verify
- `rg -n "freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|safeModeDefault=ON|contractLinkLocked=true|sharedResourceFreeze=true|Security Officer|System Owner|Platform Operator" 04_Documentation/security.md 04_Documentation/operations.md 04_Documentation/e2e_testing.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 5 Proceed
- 判定: **Conditional（A1完了待ちでDraft維持）**。

## Stream B A3 sync log（2026-04-28）

### Phase 1 Read
- `strict_mode_exception_approval_flow.md` / `operations.md` / `e2e_testing.md` / A3 issue を再読し、4観点（用語/役割/導線/固定値）を照合。
- 判定: 語彙・責務分離・D1〜D4意味は一致。軽微な固定値表記揺れのみ確認。

### Phase 2 Plan
- security の責務境界（基底方針）を維持し、A3では契約更新・承認前確定化を行わない。
- AC/DoD不足ドラフトは issue 側に記録し、本書は整合証跡のみ追記。

### Phase 3 Execute
- 本節の docs-only 追記を実施（最小差分）。

### Phase 4 Verify
- docs-check / 相互リンク整合 / fixed-value grep を実施（自己修復 0/3）。

### Phase 5 Proceed
- 判定: **Conditional**（Approval Pending 維持）。
- 次回再開条件: A1完了 + pendingDecisionQueue解消 + 承認証跡充足。
