# Enterprise / Government Deployment Architecture


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
**English summary**  
This document defines the minimum OSS-level capabilities required for kj-atlas to be deployable in enterprise and government environments.  
The focus is integration readiness, not SaaS transformation.

---

# 基本方針

本アプリケーションは以下を維持する：

- OSSとしての軽量性
- ローカルファースト設計
- SafeMode既定ON
- 文書構造と表示状態の分離（document.json / view.json）

企業・行政運用において必要なのは「アプリの肥大化」ではなく、
**外部基盤との安全な接続点の整備**である。

---

# 1. 統合認証（SSO / IdP連携）

## 目的

- 組織内ユーザ識別
- レビュー責任所在の明確化
- アクセス制御との連動

## 方針

本アプリケーション自体は認証を実装しない。

代わりに：

- 認証はリバースプロキシまたはバックエンド層で処理
- アプリは「署名済みユーザコンテキスト」を受け取る

## 最低限必要な拡張

### 1. AuthContext抽象

- userId: string（必須）
- displayName?: string
- roles?: string[]
- groups?: string[]

これをフロントに渡すだけでよい。

対応可能なIdP例（実装は外部責務）：

- OIDC
- SAML
- LDAP（間接連携）

---

# 2. ユーザ管理

## 方針

ユーザ管理機能はアプリ内に持たない。

理由：
- 組織基盤と重複する
- セキュリティ責任が過大になる

## 必要最低限

- reviewerRef を AuthContext.userId にマッピング
- view.json に reviewerRef を保持（PII非保存）
- 表示名は揮発的に扱う（保存しない）

---

# 3. 文書管理（Document Governance）

## 目的

- 文書の所有権
- 版管理
- 承認フロー

## 最小OSS対応範囲

### A. バージョンメタデータ

view.json に保持可能：

- versionTag: string
- createdAt
- updatedAt
- ownerRef

### B. 外部ストレージ前提

文書保管は以下に委譲可能：

- 既存RDBMS
- オブジェクトストレージ
- Git管理
- DMS（Document Management System）

本アプリケーションは：
- JSON構造が安定
- スキーマ後方互換

これを保証するのみ。

---

# 4. 公開範囲とアクセス制御（重要）

企業・行政用途では「未ログイン（市民・一般職員）への公開可否」と「組織内の厳格な限定公開」が同時に求められる。
本アプリケーションはアプリ内で巨大な認可基盤を抱えず、**運用方式を複数用意して“選べる”こと**を最低ラインとする。

## 4.1 公開クラス（ドキュメント単位）

文書（Document/Pack）ごとに、次の公開クラスを持てる設計とする。

- **Public**：未ログインでも閲覧可能（広域公開）
- **Unlisted**：URLを知る者のみ（リンク共有）
- **Org**：組織内（SSO必須）
- **Restricted**：ロール/グループ単位で厳格に制御（SSO必須）

MVPでは、まず view.json（または pack manifest）に **visibility** フィールドを追加し、UIはその状態を表示する。

## 4.2 方式A：静的配信（広域公開向け）

### 背景

- 認証運用の負担を避けたい
- インフラ費用を最小化したい
- “閲覧だけ” を大量配布したい

### 方針

- 本アプリケーションの **Export（Bundle/Review Pack）** を定期連携し、
  - S3 + CloudFront
  - もしくは社内静的Webサーバ
  に配置して静的配信に載せる。

### 必要なOSS整備（最低限）

- Export を **静的サイト向け** に整形するモード
  - index.html + assets + packs
- SafeMode を強制（既定ON、解除不可を選択可能）
- “公開に必要な最小ファイル” のみ出力
- 署名/ハッシュ（将来）で改ざん検知

## 4.3 方式B：認証付き配信（限定公開向け）

### 背景

- 秘匿性が高い
- 文書ごとにロール/グループで閲覧制御が必要
- 監査・証跡が必須

### 方針

- 認証（SSO）は外部（OIDC/SAML）
- 認可（RBAC/ABAC）はAPI層で実装
- 本アプリケーションは AuthContext + isReadOnly + visibility を受け取りUI制御

### 最低限必要な拡張

- DocumentACL 抽象（アプリ内実装ではなく **I/F定義**）
  - allowedRoles / allowedGroups / policyRef
- APIのガード
  - read / write / export / share の権限制御
- 監査ログ連動
  - 「誰が何を閲覧/エクスポートしたか」を外部ログ基盤に送れる導線（オプション）

### strict mode 例外運用の責務境界（AUTH-OPS-03 T1/T4）

`KJ_ATLAS_ALLOW_JIT_PROVISIONING`（旧: `ALLOW_JIT_PROVISIONING`）は、認証直後に未登録ユーザを自動作成するか否かを表す運用フラグとして扱う。

- **本番標準（strict mode）**: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`
  - 未登録ユーザは作成せず、アクセス拒否または read-only 制約を優先する。
  - SafeMode既定ON・read-only優先を崩さない。
- **例外運用**: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true`
  - 原則は障害時や移行時など、期限付きで許可する例外モードとする。
  - ただしデータ機密性/公開要件に応じて、`true` 継続運用プロファイルを選択可能（補完統制と定期審査のガイドラインを併記）。
  - 例外運用時でも share/export の抑止を含む SafeMode 制約を緩和しない。

責務境界は次のとおり固定する。

- アプリ本体（KJ Atlas）はフラグ値の受領とガード適用のみを担当し、承認ワークフロー本体は実装しない。
- 例外の発行・失効・記録は外部運用基盤（IdP/運用台帳/監査基盤）責務とする。
- 監査イベントは最小情報のみを記録し、PII最小化（氏名/メール/roles/groups生値非保存）を維持する。
- strict mode / 例外 mode いずれでも「SafeMode → read-only → AccessDecision」の優先順位は不変とする。
- 発動条件: 2者承認（Security Officer + System Owner）と復旧条件が台帳に確定した場合のみ例外を有効化する。
- 停止条件: 承認順序/TTL/代理承認など実施に必要な未確定事項が1つでも残る場合は「確認待ちで停止」とする。
- 復旧条件: 期限到来または停止条件成立時に `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` へ復帰し、復旧時刻・判定根拠を記録する。

#### strict mode 例外運用で未定義のまま保持する事項（要ユーザー確認）

以下は現時点で **未定義** とし、本ドキュメントでは推測仕様を置かない。

- 例外承認の順序（申請→承認→有効化のワークフロー詳細）
- 例外の TTL（有効期限）の既定値・上限・自動失効条件
- 代理承認（緊急時の代行承認者）の可否と条件
- 運用 SLA（承認応答時間、失効反映時間、監査反映時間）
- 例外運用の同時許可数上限・対象組織/対象文書のスコープ制約
- 例外解除後の既存セッション/トークン無効化の厳密手順
- 監査アラート閾値（例外利用回数・連続利用時間）

### FB-RM-PUB-04: AccessControlAdapter 抽象I/F（roles/groups/policyRef 外部委譲）

> 目的: `roles` / `groups` / `policyRef` を使った判定は **必ず外部アダプタへ委譲**し、アプリ本体にRBACロジックを持ち込まない。

#### インターフェース定義（実装可能仕様）

##### 1) 型契約（roles/groups/policyRef の必須/任意/null許容を明示）

```ts
type AccessAction = "read" | "write" | "export" | "share";
type Visibility = "Public" | "Unlisted" | "Org" | "Restricted";

type AuthContext = {
  actorRef?: string | null;
  roles?: string[] | null;
  groups?: string[] | null;
};

type AccessResource = {
  docId: string;
  visibility?: Visibility | null;
  policyRef?: string | null;
};

type AccessRequest = {
  action: AccessAction;
  subject: AuthContext;
  resource: AccessResource;
  safeMode: boolean;
  readOnly: boolean;
};

type AccessDecision = {
  allow: boolean;
  readOnly?: boolean;
  reason?: string;
};

interface AccessControlAdapter {
  name: string;
  authorize(request: AccessRequest): AccessDecision | Promise<AccessDecision>;
}
```

| フィールド | 型 | 必須 | null許容 | 正規化ルール |
|---|---|---:|---:|---|
| `subject.roles` | `string[]` | 任意 | 許容 | API層で `null` を `[]` に正規化してアダプタへ渡す |
| `subject.groups` | `string[]` | 任意 | 許容 | API層で `null` を `[]` に正規化してアダプタへ渡す |
| `resource.policyRef` | `string` | 任意 | 許容 | trim後に空文字なら `null` 扱い |

補足:

- `roles/groups/policyRef` は **判定入力の運搬専用** であり、アプリ本体は意味解釈をしない。
- ヘッダ入力（`x-auth-roles`/`x-auth-groups`/`x-policy-ref`）と内部DTOの差分吸収（trim, split, null補完）は API境界の責務。

##### 2) JSON例（API → AccessControlAdapter）

```json
{
  "action": "export",
  "subject": {
    "actorRef": "user:7f2f2e26",
    "roles": ["editor", "risk-reviewer"],
    "groups": ["org:policy-team"]
  },
  "resource": {
    "docId": "doc_01JX6J6C2QW",
    "visibility": "Org",
    "policyRef": "opa://kj-atlas/org-default/v3"
  },
  "safeMode": true,
  "readOnly": false
}
```

```json
{
  "allow": false,
  "readOnly": true,
  "reason": "policy_ref_unreachable"
}
```

- 入力責務: アプリ本体は `AuthContext` / `visibility` / `policyRef` を収集して `AccessRequest` を作るだけ。
- 出力責務: `allow/readOnly/reason` を返す。ロール評価規則はアダプタ外部責務。
- 失敗時: アダプタ応答不能は運用層で扱い、アプリ本体は `reason` 付き拒否または既定fail-safeを適用する。

#### 責務境界マトリクス（アプリ内責務 / 外部責務）

| 領域 | アプリ内責務（KJ Atlas） | 外部責務（IdP/Policy Engine/Audit基盤） |
|---|---|---|
| 判定入力の組み立て | `action/subject/resource/safeMode/readOnly` を収集・正規化 | なし |
| 認可判定 | `AccessDecision` を解釈して allow/deny/readOnly を反映 | roles/groups/policyRef を評価して判定を返す |
| 拒否理由 | `reason` をUI/レスポンス/監査メタへ受け渡し | 理由コードの生成・粒度管理 |
| 監査イベント | 最小監査イベントを生成し送信（fail-open方針） | 集約・保管・相関分析・アラート |
| ポリシー配布 | `policyRef` を透過的に保持 | policyRef解決、版管理、失効、検証 |

#### 本体側の最小ガード（RBAC非実装）

- `readOnly=true` のとき `write/export/share` を拒否する。
- `safeMode` は既存の share/export 制約を維持し、AccessControlAdapter はその制約を緩和しない。
- `visibility` は公開ラベルとして扱い、詳細認可条件（roles/groups）は解釈しない。

#### フォールバック仕様（policyRef不達・無効時 fail-safe）

| 条件 | 既定挙動（`ACCESS_CONTROL_FAIL_SAFE_MODE=read_only`） | 厳格挙動（`deny`） | `reason` |
|---|---|---|---|
| `visibility in {Org, Restricted}` かつ `policyRef` 欠損/空 | `read`のみ許可、`write/export/share`拒否 | 全拒否 | `policy_ref_missing` |
| `policyRef` 解決不能（DNS/接続/timeout） | `read`のみ許可、`write/export/share`拒否 | 全拒否 | `policy_ref_unreachable` |
| `policyRef` 形式不正・署名不正・失効 | `read`のみ許可、`write/export/share`拒否 | 全拒否 | `policy_ref_invalid` |
| アダプタ内部例外/想定外レスポンス | `read`のみ許可、`write/export/share`拒否 | 全拒否 | `adapter_error` |

- `visibility` が未指定または `Public/Unlisted` のときは上表の強制fail-safeを適用しない。
- SafeMode既定ONは常に優先し、fail-safe経路でも export/share 制約を緩和しない。

#### visibility（PUB-01）との整合ルール

1. `visibility` は公開範囲ラベルであり、**単独で認可可否を確定しない**。
2. 判定優先順位は `SafeMode` → `readOnly` → `AccessDecision` → `visibilityラベル`。
3. `visibility=Public` でも SafeMode/readOnly/外部判定で拒否され得る。
4. `visibility=Org|Restricted` は policyRef連携の前提を強めるが、評価ロジック自体は外部委譲のまま維持する。
5. `view.json` / `packs/index.json` の互換既定値（Restricted/Public）は既存仕様を維持する。

#### 監査イベント最小情報（PII非保存）

| 項目 | 必須 | 内容 | PII方針 |
|---|---:|---|---|
| `eventType` | 必須 | `view` / `export` / `access_denied` | PIIなし |
| `eventVersion` | 必須 | 監査スキーマ版（例: `1`） | PIIなし |
| `occurredAt` | 必須 | ISO-8601 UTC時刻 | PIIなし |
| `docId` | 必須 | 文書識別子 | 本文・タイトル非保存 |
| `action` | 必須 | `read|write|export|share` | PIIなし |
| `decision.allow` | 必須 | true/false | PIIなし |
| `decision.readOnly` | 任意 | true/false | PIIなし |
| `decision.reason` | 任意 | 理由コード（定義済み語彙のみ） | 自由入力禁止 |
| `visibility` | 任意 | `Public|Unlisted|Org|Restricted` | PIIなし |
| `policyRefPresent` | 必須 | boolean（値自体は保存しない） | policyRef生値非保存 |
| `adapterName` | 任意 | adapter識別子 | PIIなし |
| `traceId` | 任意 | 相関ID | actor個人情報と分離 |

- `action=read` は閲覧監査イベント（`eventType=view`）へ接続。
- `action=export` はエクスポート監査イベント（`eventType=export`）へ接続。
- `policyRef` 生値・`roles/groups` 生値・ドキュメント本文は監査に保存しない。

#### セキュリティ観点チェックリスト

- [ ] アプリ本体に role/group 評価式（`if role == ...`）を実装していない。
- [ ] `AccessControlAdapter` 未設定時でも SafeMode既定ONが維持される。
- [ ] `policyRef` の空文字/空白/不正形式を `invalid or missing` として fail-safe へ倒せる。
- [ ] deny理由はコード化された語彙のみを返し、内部例外文字列を露出しない。
- [ ] 監査イベントに PII（氏名/メール/本文/roles/groups生値）を残さない。
- [ ] 監査送信失敗時に本体機能を停止しない（fail-open）一方、失敗件数は運用監視で観測できる。
- [ ] `visibility` 追加によって readOnly/SafeMode の拒否強度が弱まらない。
- [ ] `ACCESS_CONTROL_FAIL_SAFE_MODE` の既定値が `read_only` である。

#### 受入基準（DoD）

1. `roles/groups/policyRef` の型契約（必須/任意/null許容）が API仕様と実装で一致している。
2. AccessControlAdapter を無効化/差し替えしても、アプリ本体にRBAC判定分岐が追加されない。
3. `policyRef` 欠損・不達・無効・adapter例外の4系統で、fail-safe (`read_only` or `deny`) が再現できる。
4. `visibility` と認可の整合（PUB-01）が満たされ、SafeMode/readOnly優先の判定順が崩れない。
5. 監査イベントが最小情報のみを記録し、PII非保存要件を満たす。
6. 403レスポンスと監査イベントの `reason` が同一コード語彙で照合できる。
7. ドキュメント（`enterprise_architecture.md` と `api.md`）の契約記述が同期している。

#### 実運用アダプタ最小実装計画（OIDC/SAML）

1. **接続面の最小実装**
   - `ACCESS_CONTROL_ADAPTER=external_http` を追加し、PDP（policy decision point）へ HTTP POST 委譲。
   - `auth_mode=oidc|saml` と `idp_issuer` をヘッダ運搬し、SSO運用情報を policy engine 側へ渡す。
2. **失敗時挙動の固定**
   - 4xx/不正JSON/契約違反は `policy_ref_invalid`。
   - 接続不可/timeout/5xx は `policy_ref_unreachable`。
   - いずれも `ACCESS_CONTROL_FAIL_SAFE_MODE`（既定 `read_only`）へ委譲。
3. **監査連携の固定**
   - `view/export` イベントに `decision_*`, `policyRefPresent`, `adapterName`, `traceId` を保持。
   - `roles/groups/policyRef` の生値非保存をテストで固定。
4. **非目標（維持）**
   - アプリ本体へ role/group 判定ロジックを追加しない。
   - SafeMode/readOnly 優先順を変更しない。

## 4.4 方式C：ハイブリッド（現実解）

- 内部は方式B（厳格管理）
- 市民向け公開は方式A（静的配信）
- “公開版” 生成はエクスポートパイプラインで担保
  - SafeMode強制
  - 伏字/匿名化ポリシー
  - 公開クラスを Public に変換


## 4.5 strict mode例外緩和の責務境界（AUTH-OPS-03）

> 詳細な承認フロー仕様（状態遷移・Q1〜Q10の選択肢・停止/復旧条件）は `02_Architecture/strict_mode_exception_approval_flow.md` を正本とする。

### 目的

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`（旧: `ALLOW_JIT_PROVISIONING=false`）（strict）を本番既定とし、例外緩和（`true`）時の責務境界を文書で固定する。
- SafeMode既定ON / PII最小化 / 監査最小化契約を維持したまま、運用Runbookの停止条件を明示する。

### 通常/例外の排他条件

- 通常運用: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`（旧: `ALLOW_JIT_PROVISIONING=false`）。
- 例外運用: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true`（旧: `ALLOW_JIT_PROVISIONING=true`） を明示承認下で一時適用。
- 排他原則: 同一対象環境で strict/例外を同時に有効化しない（単一時点で一方のみ）。

### 責務分離（固定）

| ロール | 固定責務 | 非責務（推測禁止） |
|---|---|---|
| Security Officer | 例外緩和の安全妥当性を承認する | 実行者を兼務して承認を省略すること |
| System Owner | 業務継続上の必要性を承認する | 安全審査を単独で代替すること |
| Platform Operator | 承認済み変更の実行と記録（時刻/理由/承認者/対象環境/復旧条件） | 未承認実行、承認不備の補完 |

### 停止条件（未確定事項）

- 以下が未確定な場合、例外緩和のRunbook確定を停止する。
  - 承認順序、承認有効期限、対象環境粒度、TTL/自動復旧、復旧判定者、代理承認、保存先、再申請、事後レビュー期限、違反時SLA。
- 停止時は「要確認」ラベルで質問を維持し、推測で承認フローを決定しない。

### 復旧条件（最小）

- 例外終了時は `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`（旧: `ALLOW_JIT_PROVISIONING=false`） に復帰する。
- 復帰記録にも最小監査契約（PII非保存）を適用し、復旧条件充足を記録する。
- 復旧判定者の最終確定は未確定事項（Q5）として扱い、確定まで運用停止条件を維持する。

---

# 5. 監査・証跡

既存の：

- Merge Audit Log
- ReviewEvent

を活用。

拡張可能領域：

- 署名付きハッシュ保存（将来）
- 外部ログ基盤への送信（オプション）

---

# 6. データ保護

## 既定

- SafeMode ON
- PII保存しない

## 組織向け追加検討

- 暗号化保存（DB側責務）
- バックアップ戦略
- データ保持ポリシー

---

# 7. 推奨デプロイ構成

## 小規模

Browser → Reverse Proxy → Static Frontend + API → DB

## 中規模

Browser → SSO Gateway → API Layer → Postgres → Object Storage

## 行政用途

Browser → Internal IdP → Hardened API → RDBMS（オンプレ）


---

# 8. OSSとして整備すべき最低ライン

1. AuthContext抽象インタフェース
2. reviewerRef外部マッピング対応（`ReviewerRefResolverAdapter` により `user_id` / `sso_subject` を差し替え可能）
3. readOnlyモード対応
4. versionメタデータ構造
5. スキーマ安定性保証（後方互換）
6. データ移行ガイド

---

# 非目標

- 内蔵ユーザ管理画面
- 独自認証基盤
- SaaSマルチテナント管理

---

# 結論

企業・行政レベル運用に必要なのは、

「機能の追加」ではなく
「接続点の抽象化と責任分離」である。

本アプリケーションは、

- 認証は外部
- 保存は外部
- 統治は外部

という前提を明確にし、

“組み込まれるOSS” として成立させる。
