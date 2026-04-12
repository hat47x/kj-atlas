# schemas — kj-atlas MVP スキーマ（02_Architecture）


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
本ドキュメントは、kj-atlas の **MVPで扱う永続データの最小スキーマ** を定義します。

- YAGNI方針に従い、MVPに不要な型は含めません
- 出自情報（記録者・記録時間など）は **MVPでは保持しません**
- 島（囲み）・画像・文章化・類似統合は後回しです

---

## 1. スコープ

MVPでは以下を成立させます。

- カード（テキスト）の配置
- 関係（線）の最小表現（任意）
- キャンバス表示のためのビュー変換（パン／ズーム）
- ドキュメントの保存・復元

### 1.1 CE0 Contract Freeze（責務境界メタ契約）

CE-0 の契約凍結として、実装型に先行して次のメタ契約を固定する。

- `CE0-CTX-IF`:
  - ContextQuery 必須キー: `goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode`
  - ContextBundle 必須キー: `bundleHash`（deterministic）
  - 禁止: Query Preview bypass / 非決定論 bundle
- `CE0-SAFEMODE-IF`:
  - safeMode 既定ON時は `allowUnreviewedText=false` を既定適用
  - 禁止: 未レビュー本文のAI入力混入、safeMode既定緩和
- `CE0-REVIEW-IF`:
  - review state は `unreviewed | human_reviewed`
  - `human_reviewed` への昇格は人手操作のみ
  - 禁止: AIによる review 自動昇格
- `CG-01..05`:
  - Working / ContextProjection / Consensus を分離
  - `Working -> Consensus` は `patch + approval` のみ
  - `mode=autonomous` でも proposal-only（auto-apply禁止）
  - 監査4点セット（`query/bundle/proposal/apply`）欠損は成功扱い禁止

| Contract ID | Must | Must Not |
| --- | --- | --- |
| `CE0-CTX-IF` | Query Preview を経由した ContextQuery、deterministic `bundleHash` | Query Preview bypass、非決定論 bundle |
| `CE0-SAFEMODE-IF` | safeMode既定ON、`allowUnreviewedText=false` 既定 | 未レビュー本文のAI入力混入、safeMode既定緩和 |
| `CE0-REVIEW-IF` | `human_reviewed` 昇格は人手のみ | AIによる review 自動昇格 |
| `CG-01..05` | Working/Projection/Consensus 分離、proposal-only、監査4点セット必須 | direct write、auto-apply、監査欠損成功扱い |

#### CE0 drift-stop fixed keys

- Contract ID collision = 0（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の再定義禁止）
- Vocabulary collision = 0（契約語彙は `Consensus Graph` / `WorkingGraph` / `ContextProjectionGraph` に固定）
- Verify自己修復は最大3回（4回目相当は停止）

---


### 1.2 CE1/CE2/CE4 Contract Freeze（型先行・実装非依存）

CE-1/CE-2/CE-4 は実装着手前に次の最小I/Fを固定する（mock-first、依存切断）。

#### CE1-CONTEXT-FOUNDATION

Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`

```ts
export type ContextQueryV1 = {
  queryId: string;
  goal: string;
  scope: "document" | "view" | "island";
  depth: number; // 0..5
  constraints: Record<string, unknown>;
  reviewFilter: "reviewedOnly" | "includeUnreviewed";
  safeModePolicy: "strict";
  outputMode: "summary" | "proposal" | "candidate";
  previewConfirmed: boolean;
};

export type ContextBundleV1 = {
  bundleHash: string; // sha256 hex (canonical)
  selected: unknown[];
  relations: unknown[];
  evidence: unknown[];
  contradictions: unknown[];
  reviewFlags: { reviewed: number; unreviewed: number };
  truncationMeta: Record<string, unknown>;
  excludedReason: string[];
};
```

- `previewConfirmed=false` は契約違反（`422 preview_required`）。
- 同一 canonical query で `bundleHash` 不一致は fail 判定。
- CE1 v1 は **最小I/F固定** とし、`ContextQueryV1` / `ContextBundleV1` への未定義キー追加を禁止する（拡張は v2 でのみ許可）。
- CE2/CE4 は backend 実装完了待ちを行わず、mock `ContextQuery/ContextBundle` 契約で先行検証する（mock-first）。

CE1 A2 stub contract（検証専用）:

- `POST /context/query`
  - request: `ContextQueryV1`（closed-world; unknown key reject）
  - success: `200 { accepted: true, queryCanonicalHash }`
  - error: `422 preview_required`, `400 unknown_contract_key`
- `POST /context/bundle`
  - request: `{ query: ContextQueryV1, stubDatasetId: "A2-minimal-v1" }`
  - success: `200 ContextBundleV1 + queryCanonicalHash`
  - error: `409 nondeterministic_bundle`, `400 unknown_contract_key`

Contract test観点（CE1 v1）:

1. `previewConfirmed=false` は常に `422 preview_required`。
2. 同一 canonical query 3回再実行で `queryCanonicalHash` / `bundleHash` が3/3一致。
3. 未定義キーは常に `400 unknown_contract_key`。
4. CE2/CE4 連携キー `sourceBundleHash === bundleHash` を比較可能。

後方互換観点（CE1 v1）:

- v1 はエラーコード意味論（`preview_required` / `nondeterministic_bundle` / `unknown_contract_key`）を固定し、変更しない。
- 拡張時は v2 を追加し、v1 の必須キーと判定式 `sameQuery && sameBundle` を維持する。

`bundleHash` 契約（`CE1-HASH-DET-IF` / bundleHash関連節）:
1. `ContextBundle` から `generatedAt` / `traceId` / `providerLatencyMs` など非決定論フィールドを除外する。
2. 配列順序は `selected=id asc`, `relations=(type,from,to) asc`, `evidence=cardId asc`, `contradictions=(weight desc,id asc)` に正規化する。
3. オブジェクトキーは UTF-8 バイト列辞書順で整列し canonical JSON を生成する。
4. `sha256(canonical_json)` を16進小文字で出力し `bundleHash` とする。
5. `ContextQuery` も同一規則で canonical 化し、`queryCanonicalHash` を算出する。
6. Verify 判定は `sameQuery && sameBundle`（`queryCanonicalHash` 一致かつ `bundleHash` 一致）を必須とし、`sameQuery && !sameBundle` は fail-closed とする。
7. Verify自己修復は最大3回までとし、4回目相当は停止する（推測継続禁止）。

#### CE2-LOW-RISK-AI-ASSIST

Contract IDs: `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF`

```ts
export type ProposalStatus = "proposed" | "accepted" | "rejected" | "held";
export type ProposalReviewState = "unreviewed" | "reviewed";

export type ProposalPatchV1 = {
  proposalId: string;
  diff: Record<string, unknown>;
  sourceBundleHash: string;
  rationale: string;
  status: ProposalStatus;
  reviewState: ProposalReviewState;
};
```

- Auto-apply は禁止（proposal-only）。
- `reviewState=reviewed` は人手操作のみ許可し、AI自動遷移を禁止。
- CE1契約との差異検知時は `held` へ遷移し、Verify自己修復は最大3回まで。
- CE1/CE2/CE4 は backend 実装待機を禁止し、mock 契約で依存切断した検証を継続する。

#### CE4-API-CLI-AUDIT

```ts
export type AuditEventType = "query" | "bundle" | "proposal" | "apply";

export type AuditEventV1 = {
  eventType: AuditEventType;
  equivalenceKey: string;
  queryId?: string;
  bundleHash?: string;
  proposalId?: string;
  sourceBundleHash?: string; // mock:<hash> 許容
  dryRun?: boolean;
  sideEffect?: "none" | "write";
  rejectReasonCode?: string;
};
```

- 同値判定は `equivalenceKey AND bundleHash` の一致を必須化。
- `dryRun=true` では `sideEffect="none"` を必須化（fail-closed）。

## 2. ID・座標系の前提

### 2.1 ID

- すべてのエンティティは `id: string` を持つ
- ID生成はクライアント（UUID v4 等）で行う
- APIは基本的にIDを透過し、衝突時のみエラー

### 2.2 座標系

- world座標は任意の連続値（浮動小数）を許容
- 画面（screen）への変換は `Transform` で表現
- 単位は px 相当を想定（厳密な意味は持たせない）

---

## 3. エンティティ定義（TypeScript）

> 実装言語はフロントが TypeScript のため、まずTS型で定義します。  
> API側（Python）は同等のPydanticモデルへ写像します。

### 3.1 Transform

```ts
export type Transform = {
  panX: number; // world を画面へ移す平行移動（x）
  panY: number; // world を画面へ移す平行移動（y）
  zoom: number; // scale（例: 1.0 = 100%）
};
```

### 3.2 Card

```ts
export type Card = {
  id: string;
  text: string;
  x: number;
  y: number;
  mergedIntoCardId?: string;
  repOf?: string[];
};
```

> 備考：MVPでは `w/h` は固定でもよい。必要になったら追加する。

### 3.3 Edge

```ts
export type EdgeType = "related"; // MVPでは1種類のみ

export type Edge = {
  id: string;
  fromId: string; // Card.id
  toId: string;   // Card.id
  type: EdgeType;
};
```

> 備考：否定線などは将来 `EdgeType` を拡張する。

### 3.4 Document

```ts
export type DocumentV1 = {
  version: 1;
  id: string;
  title?: string;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601

  transform: Transform;
  cards: Card[];
  edges: Edge[];
};
```

---

## 4. JSONスキーマ（サーバ検証用）

MVPでは、サーバ側で最低限の検証（型・必須フィールド）を行います。
厳密な制約（例：座標範囲や文字数）は後回し。

> 実装では Pydantic モデルで検証し、必要に応じてJSON Schema出力に対応する。

---

## 5. 将来拡張の指針（非MVP）

以下は **追加しやすい順に** 将来導入します。

1. `Card.w/h`（カードサイズ）
2. `EdgeType` の拡張（negate/hypothesis 等）
3. `Island`（囲み、タイトル、所属）
4. `Asset`（画像挿入・生成結果の参照）
5. `Card.meta`（出自情報、タグ、引用元など）
6. `Patch`（差分同期）

---

## 6. 互換性・マイグレーション

- `Document.version` を用いてスキーマバージョンを管理する
- 破壊的変更は version を上げ、API側で移行処理を提供する

---

## 7. 次に作るもの

- `02_Architecture/api.md`：DocumentV1 のCRUD I/F
- `02_Architecture/llm_provider_spec.md`：将来AI用のProvider抽象（正本）
- `02_Architecture/llm_input_ir_spec.md`：LLM入力IR仕様（正規化/前処理/schema）
- `02_Architecture/deployment.md`：Docker Compose案



## 7A. Island polygon edit constraints（FB-P2C-04）

`DocumentV2.islands[*].shape.kind === "polygon"` の場合、保存対象の `shape.points` は次を満たす。

- `points` は `Point[]`（`x: number`, `y: number`）
- 最小頂点数は 3（`points.length >= 3`）
- 自己交差禁止
- 座標は UI 編集時に小数第2位へ正規化（決定論維持）

互換読込と保存経路の扱い:

- 互換読込（import upgrade）: 不正 polygon はフォールバック（shape除去または rect解釈）を許可。
- 保存/厳格検証（strict validate / export）: 不正 polygon を reject し、document を成功扱いにしない。
- UI手動編集（vertex drag/add/remove）: 不正操作は即時拒否し、直前の確定済み polygon を保持。

## 8. Publishing / Access metadata（FB-RM-PUB-01）

公開配布（pack）および表示状態（view metadata）では、以下の visibility enum を共通契約として使う。

```ts
export type Visibility = "Public" | "Unlisted" | "Org" | "Restricted";
```

- 既定値（default）:
  - `view.json`: `visibility` 未定義時は `Restricted` を補完。
  - `packs/index.json`: `visibility` 未定義時は `Public` を補完。
- fallback は **import読込時に正規化して内部モデルへ反映** し、export時は常に enum を明示出力する。

| Artifact | Field | 欠損時 default（互換読込） | enum外値 | export時 |
| --- | --- | --- | --- | --- |
| `view.json` | `visibility` | `Restricted` を補完 | reject（strict validator） | 常に enum を明示 |
| `packs/index.json` | `packs[*].visibility` | `Public` を補完 | reject（strict validator） | 常に enum を明示 |
| `document.json` | （対象外） | 変更なし（`visibility` を持たない） | N/A | N/A |

### 8.1 view metadata（`view.json`）

```ts
export type ViewMetadataV1 = {
  version: "1";
  generatedAt: string;
  docSignature: string;
  visibility: Visibility; // 互換読込時の既定: "Restricted"
  camera: { panX: number; panY: number; zoom: number };
  viewState: { /* 既存定義 */ };
  export: { mode: "viewport" | "bounds"; bounds?: { x: number; y: number; w: number; h: number }; padding?: number };
};
```

- 互換方針：旧データで `visibility` が無い場合は `Restricted` を補完する。
- strict validator 方針：`visibility` が存在する場合は enum（`Public` / `Unlisted` / `Org` / `Restricted`）以外を拒否する。
- 安全方針：`visibility` の有無に関わらず SafeMode 既定ON・share/export 制約の既存ポリシーを維持する。
- 運用解釈：`visibility` は公開範囲の意図を示すメタデータであり、外部送信可否（SafeMode や export制御）を直接変更しない。

### 8.1.1 SafeMode / readOnly / visibility の評価優先順位

競合時の評価順は次で固定する（上位が優先）。

1. **SafeMode / share-export policy**（既定ON、漏えい防止）
2. **readOnly**（書込・共有・export など破壊/外部送信系を抑止）
3. **visibility**（公開範囲ラベル。UI表示・監査ラベル用途）

補足:
- `visibility=Public` でも SafeMode により export/share が拒否され得る。
- `visibility=Restricted` でも readOnly=false かつ SafeMode許可条件を満たす操作は、既存ポリシーに従って評価する。
- `visibility` は判定入力にはなり得るが、SafeMode/readOnly の拒否結果を上書きしてはならない。

### 8.2 public pack manifest（`packs/index.json`）

```ts
export type PublicPackManifest = {
  defaultPackId?: string;
  packs: Array<{
    id: string;
    documentPath: string;
    viewPath?: string;
    title?: string;
    enforceSafeMode?: boolean;
    readOnly?: boolean;
    visibility: Visibility; // 互換読込時の既定: "Public"
  }>;
};
```

- 互換方針：既存 manifest で `visibility` が無い場合は `Public` を補完する（公開配布の既存運用を維持）。
- strict validator 方針：`visibility` が存在する場合は enum（`Public` / `Unlisted` / `Org` / `Restricted`）以外を拒否する。
- import/export/validate は上記 enum を単一契約として扱う。
- 運用解釈：pack の `visibility` も配布上の分類情報として扱い、SafeMode 既定ONおよび漏洩防止ポリシーとは分離する。

### 8.2.1 I/F 境界（実装者向け）

- **Schema契約（本書）**
  - `Visibility` の値域、default/fallback、不正値拒否条件の単一正本。
- **Importer / Loader（Backend/Frontend 共通責務）**
  - 欠損時 default 補完（`view.json` は `Restricted`、`packs/index.json` は `Public`）。
  - 補完後の内部モデルは `visibility` 必須状態で保持する。
- **Validator（Backend/Frontend 共通責務）**
  - enum外値・型不正は互換対象にせず reject する。
  - `packs/index.json` は entry 単位で黙って救済せず、manifest 全体を失敗扱いにする。
- **Exporter（Backend/Frontend 共通責務）**
  - 互換補完で受理した旧データを含め、再出力時は必ず `visibility` を明示する。
- **Policy層（Non-Goalの明確化）**
  - `visibility` は分類メタデータであり、RBAC/認可/SafeMode 判定ロジックそのものは本タスクの対象外（FB-RM-PUB-01 のスコープ外）。

### 8.3 旧データ互換（旧→新）

- 旧 `view.json`（`visibility` 欠損）
  - 読込時: `Restricted` を補完して `ViewMetadataV1` として扱う。
  - 再export時: `visibility: "Restricted"` を明示出力する。
- 旧 `packs/index.json`（entry の `visibility` 欠損）
  - 読込時: `Public` を補完して `PublicPackManifest` として扱う。
  - 再export時: 各 entry に `visibility` を明示出力する。
- 旧データに `visibility` が存在しても enum 外値の場合は **互換読込対象にしない**（strict validator で拒否）。

#### 8.3.1 既存 document の欠損解釈（明示）

- `document.json` は FB-RM-PUB-01 の適用対象外であり、`visibility` 欠損という状態自体を扱わない。
- 互換読込で default 補完を行うのは `view.json` / `packs/index.json` のみ。
- 既存 `document.json` をそのまま読めること（非破壊）を互換要件とする。

### 8.4 失敗ケース（拒否すべき入力）

- `visibility` が文字列以外（`null`, number, object）
- `visibility` が enum 外（例: `"FriendsOnly"`, `"private"`）
- pack manifest で `packs[*].visibility` が欠損以外の不正（例: `""` や空白のみ）
- view metadata で `visibility` が空文字または大文字小文字違い（例: `"public"`）

### 8.5 Definition of Done（FB-RM-PUB-01）

1. **schema検証**
   - `view.json` / `packs/index.json` が enum 制約（`Public | Unlisted | Org | Restricted`）を満たす。
   - 不正値は import/export validator が拒否する。
2. **互換読込**
   - `visibility` 欠損の旧 `view.json` が `Restricted` として読める。
   - `visibility` 欠損の旧 `packs/index.json` が `Public` として読める。
3. **回帰観点**
   - SafeMode既定ON・share/export漏えい防止の既存テストが通る。
   - `visibility` 追加により readOnly/SafeMode の拒否挙動が緩まない。

### 8.6 importer / validator / exporter テスト観点

- importer（互換補完）:
  - `view.json` の `visibility` 欠損時は `Restricted` を補完して読込成功。
  - `packs/index.json` の `packs[*].visibility` 欠損時は `Public` を補完して読込成功。
- strict validator（不正拒否）:
  - `visibility` が enum 外または型不正（number/null/object/空文字）は失敗として拒否。
  - `packs/index.json` は entry 単位で黙って破棄せず、manifest 全体を失敗扱いにする。
- exporter（再出力明示）:
  - 互換補完で読んだ旧データは再出力時に `visibility` を必ず明示。
  - `visibility` 追加後も SafeMode/readOnly の拒否優先順は不変。

### 8.7 トレーサビリティ（FB-RM-PUB-01）

- 要求元: `01_Plans/adr/ADR-0007-future-backlog.md` の `FB-RM-PUB-01`（schema検証と既存データ互換）。
- 上位整合: `02_Architecture/architecture.md` §11（visibility enum / default補完 / SafeMode優先）。
- 本節（schemas.md）は、実装者向けの単一契約として default/fallback/strict validation/I/F境界を具体化する。


## 9. Island hierarchy compatibility contract（FB-P2A-01）

`DocumentV2.islands[*]` では、階層表現を次で扱う。

```ts
export type Island = {
  id: string;
  cardIds: string[];
  parentIslandId?: string;
};
```

- `parentIslandId` は任意（未設定時はルート島として扱う）。
- 既存データ互換のため、`parentIslandId` が欠損していても読み込みを失敗させない。
- `parentIslandId` が存在しない島を参照する場合は、import 正規化で `undefined` にフォールバックする。
- 循環参照（self-parent 含む）は import 正規化で `undefined` にフォールバックする。
- save/reload では有効な `parentIslandId` を欠落させず往復保持する。

## 10. AUTH-SCHEMA-01: Identity schema (`users` / `user_identities`)

`ADR-0020` の AUTH-ARCH-01 決定を受け、認証情報を保持しない前提で次を正本とする。

- `users`
  - `id` (UUID, immutable, PK)
  - `display_name` (nullable, 最小PII)
  - `email` (nullable, 最小PII)
  - `lifecycle_state` (`active|suspended|deprovisioned`)
  - `created_at`, `updated_at`
- `user_identities`
  - `id` (PK)
  - `user_id` (FK -> `users.id`)
  - `provider` (例: `oidc` / `saml` / `header`)
  - `external_uid` (IdP subject 等)
  - `created_at`
  - 一意制約: `UNIQUE(provider, external_uid)`

運用モード:

- `ALLOW_JIT_PROVISIONING=true`（既定）: 未登録 `provider+external_uid` を受信したら `users` / `user_identities` を同時作成。
- `ALLOW_JIT_PROVISIONING=false`（strict）: 未登録は `403` とし、事前プロビジョニング済みのみ許可。

API I/F 整合用の最小型（実装依存を避ける境界）:

```ts
export type IdentityProvisioningContract = {
  strictReject: {
    status: 403;
    code: "identity_not_provisioned";
  };
  adminProvision: {
    request: { provider: string; externalUid: string; displayName?: string; email?: string };
    success: { userId: string; reviewerRef: `user:${string}`; ownerRef: `user:${string}`; provisioned: boolean };
    conflict: { status: 409; code: "identity_already_provisioned_conflict"; message: string };
  };
};
```

- 依存実装（mock/test double含む）は `status` と `code`、および `success.provisioned` のみで分岐可能であること。
- 追加メタデータは許容（forward-compatible）だが、上記キーの意味を変更してはならない。

## 11. FB-P2B-02 Decision Log schema contract（CTR-2B-02-DECISION-LOG-V1）

Manual assisted merge の意思決定ログは、`DocumentV2` 本体とは独立した append-only ストアとして扱う。

```ts
export type MergeDecisionRecord = {
  decisionId: string;
  groupId: string;
  action: "accept" | "partial" | "reject" | "defer";
  selectedCardIds: string[];
  note: string;
  decidedBy: string;
  decidedAt: string; // ISO 8601
  snapshotVersion: string;
};
```

- `action` は4値固定（契約拡張禁止）。
- `restore(snapshotVersion)` は同一 `snapshotVersion` に紐づく記録を append 順で返す。
- `listByGroup(groupId)` は同一 `groupId` の記録を append 順で返す。
- 非自動確定を守るため、本契約は `accept` でも代表カード確定を暗黙実行しない。

移行前提（expand/contract）:

- expand:
  1) `users` / `user_identities` を追加し、`UNIQUE(provider, external_uid)` を先に適用する。
  2) 既存 attribution は互換維持しつつ、新規書込は `AuthContext.userId=users.id` 経由へ切替える。
- contract:
  3) 旧来の外部識別子直参照を段階的に廃止し、`reviewerRef` / `ownerRef` は `user:<users.id>` のみ許可する。
  4) strict 運用では未登録 subject を `403` とし、管理導線（`POST /admin/provision/users`）を必須化する。
- backfill運用: 旧 `reviewerRef` / `ownerRef`（例: `user:sso:sub:<subject>`）は mapping JSON を使って `user:<users.id>` へ変換する。
  - dry-run: `python -m kj_atlas_api.backfill_identity_refs --database-url <DATABASE_URL> --mapping-json mapping.json --dry-run`
  - apply: `python -m kj_atlas_api.backfill_identity_refs --database-url <DATABASE_URL> --mapping-json mapping.json`

属性境界（persist/transient/forbidden）:

- persist: `provider`, `external_uid`, `display_name`, `email`（最小）
- transient: `amr`, `acr`, `aal`, `auth_time`, `roles`, `groups`, `trace_id`
- forbidden: password/hash/secret, WebAuthn credential id, raw policy tokens

### 10.1 監査観点での固定ルール（実装向け決裁）

実装判断のブレをなくすため、AuthContext/identity 属性を次の3分類で固定する。

#### persist（DB永続化を許可）

- 許可: `users.display_name`, `users.email`, `user_identities.provider`, `user_identities.external_uid`
- 目的: 同一人物の再識別（`provider+external_uid`）と最低限の運用表示。
- 制約: `display_name`/`email` は nullable かつ最小利用に限定し、認可判定条件としては使用しない。

#### transient（リクエスト内/監査最小メタのみ）

- 対象: `amr`, `acr`, `aal`, `auth_time`, `roles`, `groups`, `policyRef`, `trace_id`
- DB保存: 禁止（`users` / `user_identities` / document / review attribution のいずれにも保存しない）。
- 監査出力: 直接値ではなく、後述 10.2 の「presence/level 正規化」のみ許可。

#### forbidden（受信しても保存・再出力を禁止）

- `password`/`password_hash`/`secret` 全般
- WebAuthn credential id / authenticator AAGUID 等の端末識別子
- 生の policy token / assertion / id token / access token
- `roles`/`groups`/`policyRef` の生値ログ出力

上記 forbidden は debug ログ・監査ログ・エクスポートファイルを含め **全面禁止** とする。

### 10.2 `amr/acr/aal/auth_time` の保存・表示・監査出力

- 保存（DB）: 全て禁止。
- UI表示: セッション診断表示に限定し、document/view へ埋め込まない。
- 監査出力（許可範囲）:
  - `amr`: 生値禁止。`hasStepUp`（boolean）または `amrClass`（`single_factor|multi_factor|unknown`）へ正規化。
  - `acr` / `aal`: 生値禁止。`assuranceLevel`（`low|substantial|high|unknown`）へ正規化。
  - `auth_time`: 生値禁止。`authAgeBucket`（`fresh(<=15m)|stale(>15m)|unknown`）へ正規化。
- 監査目的で詳細が必要な場合も、保存期間は短期運用ログに限定し、アプリDBへ逆流させない。

### 10.3 `roles/groups/policyRef` の永続境界

- `roles` / `groups`: 認可問い合わせ入力としてのみ利用し、アプリDBに保存しない。
- `policyRef`: リクエスト時の外部PDP参照子としてのみ扱い、生値は保存しない。
- 永続許可されるのは `policyRefPresent` のような存在フラグのみ。
- fail-safe 判定（`policy_ref_missing|policy_ref_unreachable|policy_ref_invalid`）は保存可。

この境界により、組織属性の最新性は外部IdP/PDPを正本とし、アプリ側の属性陳腐化リスクを回避する。

## 11. Polygon handoff contract keys（FB-P0-2A2B2C）

backend接続準備で利用する比較キーは次を最小契約とする。

```ts
export type PolygonHandoffInputContract = {
  gateApprovalRef: string;
  a2VerifyRef: string;
  inputHash: string; // sha256 hex(64)
  deterministicTieBreakOrder: [
    "padding_compliance",
    "self_intersection_avoidance",
    "minimum_area_delta",
    "minimum_vertex_count",
  ];
};

export type PolygonHandoffExpectedOutputContract = {
  outputPolygonHash: string; // sha256 hex(64)
  paddingViolationCount: number; // >= 0
  tieBreakOrder?: [
    "padding_compliance",
    "self_intersection_avoidance",
    "minimum_area_delta",
    "minimum_vertex_count",
  ];
  tieBreakOrderChanged?: boolean; // tieBreakOrder未送信時に必須
};
```

ロールバック判定トリガー:

- `paddingViolationCount > 0`
- `tieBreakOrder` が `deterministicTieBreakOrder` と不一致
- `tieBreakOrderChanged === true`（後方互換）

## 12. HIL-RS-01 A1 error envelope contract（A1-ERROR-IF）

A1契約違反時に backend が返すエラーは共通 envelope を用いる。

```ts
export type A1ErrorEnvelope = {
  schemaVersion: "1.0.0";
  errorEnvelope: {
    errorCode:
      | "A1_SCHEMA_VERSION_MISMATCH"
      | "A1_REQUIRED_FIELD_MISSING"
      | "A1_TRACE_KEY_MISSING"
      | "A1_OVERRIDE_POLICY_VIOLATION"
      | "A1_PII_POLICY_VIOLATION";
    message: string;
    contractId: "A1-CRITIQUE-IF" | "A1-REDIFF-IF" | "A1-ATTR-IF";
    retryable: boolean;
    occurredAt: string; // ISO 8601
  };
};
```

- `message` へ email / external_uid など生IDを含めない。
- `contractId` は違反した契約IDを必ず指す。
- A2/A3 で errorCode 列挙を拡張しない。
