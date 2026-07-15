# schemas — kj-atlas MVP スキーマ（02_Architecture）


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
> 現行契約と Stream / freeze 履歴の読み分けは `02_Architecture/contract_reading_guide.md` を参照する。
> MVPで実際に運用サポートするデータ構造、埋め込み限定の構造、契約のみの構造は `02_Architecture/data_model_operations_overview.md` を参照する。
> ADR-0033 で定義した Support/Maintenance/Contract Boundary（L1/L1.5/L2/L2.5/L3/L0）を正本とし、本書の型定義単体で運用保証を主張しない。
> `ADR-0057` は、反復的探究を独立 `InquiryJourneyV1` + 不変 `RoundSnapshotV1` DAGとして扱う設計を採択した。詳細は `02_Architecture/inquiry_journey_model.md` を参照する。実装・移行・CRUDが揃うまでは `L0: Planned` であり、現行 `DocumentV2` の型、version gate、保存契約へ履歴キーを追加しない。
本ドキュメントは、kj-atlas の **MVPで扱う永続データの最小スキーマ** を定義します。

- YAGNI方針に従い、MVPで標準運用しない型は「運用サポート済み」と扱いません
- 最小 `DocumentV1` では、出自情報（記録者・記録時間など）を保持しません
- 島（囲み）・画像・文章化・類似統合などは、型の有無と標準保守範囲を分けて管理します

ただし、本ファイルには後続フェーズのContract Freezeや型先行の記録も含まれます。型が記載されていることは、そのまま標準API/UIで個別保守できることを意味しません。

---

## 1. スコープ

MVPでは以下を成立させます。

- カード（テキスト）の配置
- 関係（線）の最小表現（任意）
- キャンバス表示のためのビュー変換（パン／ズーム）
- ドキュメントの保存・復元

### 1.0 カード内容品質とスキーマの境界

カードに記述する定性情報の品質要件は `00_Prompt/qualitative_card_quality_requirements.md` を正本とする。初期実装では、品質支援のために `Card` へ必須フィールドを追加しない。

- `Card.text` は、元の意味を保ったカード本文の正本とする。
- `claimType` は観察・主張・仮説などの位置づけを補助するが、未設定でも保存できる。
- `Card.meta.source` は外部の元記録へ戻る任意の手がかりであり、統合元カード、起票者、レビュー者を表さない。
- `holdState` と `critique` は、不明な文脈、矛盾、違和感を解消せず保持するために利用できる。
- 品質上の指摘は導出された提案であり、カード内容に関する真実の属性として保存しない。
- 分割、言い換え、補足は proposal-only とし、採用前の本文を変更しない。

提案の見送り状態、品質確認結果、確認担当者などを永続化する場合は、必須化せず、後方互換、import validation、共有範囲、SafeModeを定める内部issueまたはADRを先行する。

### 1.0.1 Stream D drift audit gate（2026-05-20）

本書の運用境界は `02_Architecture/data_model_operations_overview.md` と対で解釈する。次のいずれかを満たした場合は drift として `Stop` 判定にする。

1. `L1/L1.5/L2/L2.5/L3/L0` の語彙または意味が文書間で不一致。
2. `PUT /docs/{doc_id}` create-if-absent をMVP標準Create契約とする記述が不一致。
3. `Document.version` の非互換変更に version gate が伴わない。
4. Verify自己修復回数が3回を超えたまま継続しようとする。

### 1.1 CE0 Contract Freeze（責務境界メタ契約）

CE-0 の契約凍結として、実装型に先行して次のメタ契約を固定する。

- Input Contract Snapshot（固定）:
  - `snapshot_id = ce0-contract-freeze-2026-04-27`
  - `freeze_mode = contract-only`
  - `downstream_policy = read-only reference`

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
- No-Go canonical IDs = `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`

---


### 1.2 CE1/CE2/CE4 Contract Freeze（型先行・実装非依存）

CE-1/CE-2/CE-4 は実装着手前に次の最小I/Fを固定する（mock-first、依存切断）。

#### CE1-CONTEXT-FOUNDATION

Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`

CDC固定: Contract IDは再定義禁止、mock-first依存切断を維持し、推測による実装要件追加を禁止する。

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
  queryCanonicalHash: string; // sha256 hex (canonical query)
  bundleHash: string; // sha256 hex (canonical bundle)
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
- CE1 v1 エラー語彙は `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の3種に固定する。
- CE1 v1 は **最小I/F固定** とし、`ContextQueryV1` / `ContextBundleV1` への未定義キー追加を禁止する（拡張は v2 でのみ許可）。
- CE1 v1 は closed-world 契約とし、Contract Test/Stub API の双方で unknown key reject（`400 unknown_contract_key`）を同一意味で扱う。
- CE2/CE4 は backend 実装完了待ちを行わず、mock `ContextQuery/ContextBundle` 契約で先行検証する（mock-first）。
- CE2/CE4 への連携は read-only handoff とし、契約更新は CE1 再起票でのみ許可する。
- CE2/CE4 側で `sourceBundleHash === bundleHash` を照合できない場合は fail-closed（適用停止）とする。

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


Mock Validation Plan（implementation-decoupled）:
- Plan: `ContextQueryV1` / `ContextBundleV1` の固定fixture（A2-minimal-v1）を使用して契約検証のみ実施。
- Execute: backend未実装でも `POST /context/query` / `POST /context/bundle` の入出力語彙をmockで検証。
- Verify: deterministic hash（3/3一致）、preview gate、unknown key reject を契約テストで確認。
- Proceed: CE2/CE4へ `queryCanonicalHash` / `bundleHash` / `sourceBundleHash` をread-only handoff。

Mock適用方針（CE1 v1 固定）:
- 可能: `A2-minimal-v1` を用いた契約テスト（型/語彙/hash）
- 不可: 実DB・実LLM・worker依存を混在させる検証
- 条件付: 下流への引き渡しは read-only（契約変更は CE1 再起票時のみ）

後方互換観点（CE1 v1）:


#### CE0/CE1 downstream signature catalog（Phase 4 fixed output）

CE0/CE1 の下流実装が参照すべき固定シグネチャ一覧を次で凍結する（mock-first / 実装非依存）。

- `ContextQueryV1`（Contract ID: `CE1-CTXQ-IF`）
- `ContextBundleV1`（Contract ID: `CE1-CTXB-IF`）
- `ProposalPatchV1`（Contract IDs: `CE2-PROPOSAL-IF`, `CE2-LIFECYCLE-IF`）
- `AuditEventV1`（Contract ID: `CE4-API-CLI-AUDIT`）
- `HilRsDecisionGateV1`（Contract ID: `HIL-RS-DECISION-GATE-IF`）
- `HilRsDocSyncCheckV1`（Contract ID: `HIL-RS-DOCSYNC-IF`）

互換ルール（v1固定）:
- v1 の必須キー集合とエラー意味論（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）は変更しない。
- 拡張は v2 追加でのみ許可し、v1 の `sameQuery && sameBundle` 判定は維持する。
- Contract Freeze 中は、上記シグネチャに対する破壊的変更・改名・削除を禁止する。

HIL-RS bridge signatures（A1->A2->A3 handoff固定）:

```ts
export type HilRsDecisionGateV1 = {
  issueId: string;
  phase: "A1" | "A2" | "A3";
  approvalRecord: { approvedBy?: string; approvedAt?: string; evidence?: string };
  gateStatus: "go" | "conditional" | "no-go";
  held: string[];
};

export type HilRsDocSyncCheckV1 = {
  contractId: string;
  syncTargets: string[];
  auditDigest: string;
  syncResult: "ok" | "drift_detected";
  drift?: string[];
};
```


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
export type ProposalReviewState = "unreviewed" | "human_reviewed";

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
- `reviewState=human_reviewed` は人手操作のみ許可し、AI自動遷移を禁止。
- CE1契約との差異検知時は `held` へ遷移し、Verify自己修復は最大3回まで。
- CE1/CE2/CE4 は backend 実装待機を禁止し、mock 契約で依存切断した検証を継続する。

#### CE4-API-CLI-AUDIT

```ts
export type AuditEventType = "query" | "bundle" | "proposal" | "apply";

export type AuditEventV1 = {
  eventType: AuditEventType;
  contractId?: string;
  phase?: "A1" | "A2" | "A3" | "CE0" | "CE1" | "CE2" | "CE4";
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

DOMAIN-KJ-01（ADR-0048 D3 採択）で、KJ法原典の関係記号に対応する語彙へ**追加的に**拡張した。`version: 2` を維持し、既存データの意味は変えない。

```ts
export type KnownEdgeType =
  | "related"      // 関連（無方向・既定）
  | "negate"       // 対立（無方向）。KJ法の「対立」の永続値（下記 語彙境界 参照）
  | "causal"       // 因果（有向: fromId=原因 → toId=結果）
  | "mutual"       // 相互（無方向・相互依存 ⇄）
  | "equivalence"; // 同値（無方向・「同じことを言っている」という記述）

// 未知種別の保全（ADR-0048 D3）: 取り込み時に未知の type 文字列を破棄せず、
// そのまま保持する。表示・挙動の解決は resolveKnownEdgeType() ヘルパが行い、
// 未知種別は「関連（無方向）」として扱う。型注釈上は既知5値の補完を保ちつつ
// 任意文字列を受理する（LiteralUnion 形式）。
export type EdgeType = KnownEdgeType | (string & {});

export type EdgeV1 = {
  id: string;
  fromId: string; // Card.id
  toId: string;   // Card.id
  type: "related"; // version: 1 の契約は不変
};

export type EdgeEndpointKind = "card" | "island";

export type Edge = {
  id: string;
  fromId: string;              // Card.id または Island.id（fromKind に従う）
  toId: string;
  fromKind?: EdgeEndpointKind; // 省略時 "card"
  toKind?: EdgeEndpointKind;   // 省略時 "card"
  type: EdgeType;
};
```

#### 3.3.1 方向規約

- **`causal` のみ有向**とし、`fromId`（原因）→ `toId`（結果）を意味方向とする。
- `related` / `negate` / `mutual` / `equivalence` および未知種別は**無方向**であり、描画・集約・エクスポートで端点順序に意味を持たせない。
- 集約（島間派生エッジ・abstract map の関係行）では、無方向種別はペアを正規化してよいが、**`causal` はペア正規化を行わず方向を保存**する。

#### 3.3.2 語彙境界（DOMAIN-KJ-01 T1 確定）

1. **対立 vs `negate`（Edge）vs `contradicts`（EvidenceLink）**
   - `negate` は KJ法の「対立」の**永続値**である。新たな `opposition` 値は追加しない（重複語彙の禁止）。UI 表示名は「否定」から「対立」へ改める。既存文書は無変更のまま新表示に乗る。
   - `contradicts`（EvidenceLink）は**根拠レベルの反証**（ある根拠が主張を反証する）であり、カード/島どうしの**構造上の関係**（Edge）とは独立の機構として併存する。
2. **同値（`equivalence`）vs canonical 化（`Card.canonicalId` / `sources`）**
   - `equivalence` は「2枚が同じことを言っている」という**記述**（関係の注釈）。両カードは第一級のまま残り、線の削除でいつでも取り消せる。
   - canonical 化は統合の**実行**（操作）。同値線は統合を**自動実行しない**（AI 自動グルーピングの確定禁止 = ADR-0048 D3 反パターン）。同値線は人間の統合判断への入力に留まる。
3. **未知種別の保全（往復規約）**
   - 寛容（import）・厳格（契約検証）の両モードで、未知の `type` を理由にエッジを**破棄しない**。`type` は非空文字列であれば受理する。
   - 既知5種別以外は表示・挙動上「関連（無方向）」として解決する（`resolveKnownEdgeType()`）。
   - バックエンド（Pydantic）も同じ規約（`type: 非空 str`）で受理する。export → import → save の往復で `type` 文字列は不変とする。

> 既定値: 新規に作成される関係線の既定は `related`（無方向）とし、種別の確定を強制しない（早すぎる収束の防止 = ADR-0001 P-01/P-04）。

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

### 3.5 DocumentV2 embedded support

`DocumentV2` は、MVPのスナップショット保存を保ったまま、島、文章化、根拠リンク、レビュー関連情報を含める拡張形式である。

`DocumentV2` に含まれる構造は、標準API/UIで個別CRUDできることを意味しない。標準の永続化単位は引き続き `Document` 全体であり、個別CRUDの有無は `02_Architecture/data_model_operations_overview.md` のCRUD表に従う。

```ts
export type CardClaimType = "fact" | "claim" | "hypothesis" | "unknown";
export type EdgeEndpointKind = "card" | "island";
export type A1TargetRef =
  | `card:${string}`
  | `island:${string}`
  | `cluster:${string}`
  | `edge:${string}`
  | `proposal:${string}`;

export type EvidenceLink = {
  id: string;
  type: "supports" | "contradicts";
  fromCardId: string;
  toCardId: string;
  note?: string;
  createdAt?: string; // ISO 8601
  /** DOMAIN-EXPR-04: 可逆な矛盾レビュー状態 */
  contradictionState?: "unconfirmed" | "confirmed" | "held" | "resolved";
};

export type NarrativeCheckReference = { id: string; kind: "card" | "island" };
export type NarrativeCheckIssue = {
  severity: "info" | "warn" | "error";
  message: string;
  references?: NarrativeCheckReference[];
};
export type NarrativeCheck = {
  id: string;
  createdAt: string; // ISO 8601
  kind: "consistency";
  issues: NarrativeCheckIssue[];
};

export type Narrative = {
  id: string;
  title: string;
  text: string;
  createdAt?: string; // ISO 8601
  basedOnReadingOrder?: string[];
  reviewed: boolean;
  checks?: NarrativeCheck[];
};

export type RelationSummary = {
  id: string;
  createdAt: string; // ISO 8601
  islandAId: string;
  islandBId: string;
  // KnownEdgeType（§3.3）に追随する。未知/解決不能な種別は "unknown" へ正規化して保持する。
  relationType: "related" | "negate" | "causal" | "mutual" | "equivalence" | "unknown";
  derived: boolean;
  text: string;
  reviewed: boolean;
  groundingCardIds: string[];
  groundingEdgeIds: string[];
  warnings?: string[];
  sourceSignature: string;
  history?: RelationSummaryHistoryEntry[];
};

export type RelationSummaryHistoryEntry = {
  id: string;
  createdAt: string; // ISO 8601
  changeKind: "ai" | "manual" | "rollback" | "import" | "unknown";
  fromText: string | null;
  toText: string | null;
  fromReviewed: boolean | null;
  toReviewed: boolean | null;
  warningsSnapshot?: string[];
  groundingCardIdsSnapshot?: string[];
  groundingEdgeIdsSnapshot?: string[];
  note?: string;
};

export type CritiqueInput = {
  schemaVersion: "1.0.0";
  critiqueId: string;
  targetRef: A1TargetRef;
  critiqueType: "too_close" | "too_far" | "not_the_same" | "feels_off" | "no_articulable_reason";
  createdAt: string; // ISO 8601
  iteration: number; // >= 1
  comment?: string;
  constraintHints?: string[];
};

export type ReproposalDiffOp = {
  opId: string;
  opType: "add" | "remove" | "move" | "regroup" | "relabel";
  targetRef: A1TargetRef;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  rationale?: string;
};

export type ReproposalDiff = {
  schemaVersion: "1.0.0";
  proposalId: string;
  basedOnIteration: number; // >= 1
  diffOps: ReproposalDiffOp[];
  traceKey: string;
  rationale?: string;
};

export type ReviewAttribution = {
  schemaVersion: "1.0.0";
  reviewState: "unreviewed" | "human_reviewed";
  reviewedAt: string | null; // ISO 8601 when human_reviewed, null when unreviewed
  reviewerRef: string; // opaque id; email/external_uid/provider user id must not be stored here
  auditRecordedAt: string; // ISO 8601
  overridePolicy: "human_dual_control_only";
  reviewContext?: string;
  ownerRef?: string;
};

export type DeterministicTieBreak = {
  schemaVersion: "1.0.0";
  order: [
    "padding_compliance",
    "self_intersection_avoidance",
    "minimum_area_delta",
    "minimum_vertex_count",
  ];
};

export type DocumentV2 = {
  version: 2;
  id: string;
  title?: string;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
  transform: Transform;
  cards: Array<Card & { claimType?: CardClaimType }>;
  edges: Array<Edge & { fromKind?: EdgeEndpointKind; toKind?: EdgeEndpointKind }>;
  islands: Island[];
  readingOrder?: string[];
  narratives?: Narrative[];
  relationSummaries?: RelationSummary[];
  evidenceLinks?: EvidenceLink[];
  patchApplyLog?: PatchApplyLogEntry[];
  mergeSuggestionDecisions?: MergeSuggestionDecisionEntry[];
  critiqueInputs?: CritiqueInput[];
  reproposalDiffs?: ReproposalDiff[];
  reviewAttribution?: ReviewAttribution;
  deterministicTieBreak?: DeterministicTieBreak;
};
```

支援レベル:

- `claimType`、`fromKind`、`toKind`、`evidenceLinks` は `DocumentV2` スナップショット内で往復保持する。
- `edges[].type` は未知種別を含めて往復保持する（§3.3.2 の保全規約）。未知種別を理由にエッジを破棄・改変してはならない。
- `evidenceLinks` は根拠・反証のリンクであり、SafeMode/share/exportで未レビュー本文や根拠情報をどう扱うかは共有前確認のポリシーに従う。
- `patchApplyLog.stats` は evidence link の追加/削除件数（`upsertEvidenceLinks` / `deleteEvidenceLinks`）を含める。旧データで欠損する場合は0として扱う。
- `critiqueInputs`、`reproposalDiffs`、`reviewAttribution`、`deterministicTieBreak` は A1 契約の往復保持対象である。MVPでは画面上の個別編集や個別CRUDを提供せず、import/export/API保存時の型・検証・監査境界を固定する。
- `targetRef` は `card:` / `island:` / `cluster:` / `edge:` / `proposal:` の名前空間を許可する。現行UIは島を `island:` として扱い、既存A1文書の `cluster:` と互換的に残す。
- `reproposalDiffs[].diffOps[].before` と `after` はどちらも必須キーであり、追加/削除を可逆にするため片側 `null` を許可する。ただし両方 `null` は不可とする。
- `reviewAttribution.reviewedAt` は `human_reviewed` のとき ISO 8601、`unreviewed` のとき `null` とする。`reviewerRef` / `ownerRef` は不透明参照であり、生IDを含めない。
- 個別EvidenceLink API、個別Card分類API、個別Edge endpoint APIはMVP範囲外とする。

---

## 4. JSONスキーマ（サーバ検証用）

MVPでは、サーバ側で最低限の検証（型・必須フィールド）を行います。
厳密な制約（例：座標範囲や文字数）は後回し。

> 実装では Pydantic モデルで検証し、必要に応じてJSON Schema出力に対応する。

---

## 5. 将来拡張の指針（非MVP）

以下は **追加しやすい順に** 将来導入します。

1. `Card.w/h`（カードサイズ）
2. ~~`EdgeType` の拡張（negate/hypothesis 等）~~ → DOMAIN-KJ-01 で導入済み（§3.3）
3. `Island`（囲み、タイトル、所属）
4. `Asset`（画像挿入・生成結果の参照）
5. `Card.meta`（出自情報、タグ、引用元など。非主体メタの `seq`/`source` は DOMAIN-TRACE-01 で導入済み=§15。カード起票者など主体メタのUI/保存/redaction境界は引き続き `CARD-META-UI-01` で管理する）
6. `Patch`（差分同期）

---

## 6. 互換性・マイグレーション

- `Document.version` を用いてスキーマバージョンを管理する
- 破壊的変更は version を上げ、API側で移行処理を提供する

### 6.0.1 DocumentV2 mock schema version（downstream独立性）

`DocumentV2` 契約ドリフト検証では、実装進捗と独立して次の mock schema version を固定する。

- `mockSchemaVersion = "mock-2026-05-19-dv2"`
- 用途: contract test / fixture / handoff の識別子
- 非用途: runtime の `Document.version` 代替（`Document.version` は引き続き `1|2` のみ）

運用ルール:
- 下流（import/export/validator/worker）は `mockSchemaVersion` を参照して fixture 互換性を判定してよい。
- 本番永続データには `mockSchemaVersion` を書き込まない（read-only検証メタ）。
- `mockSchemaVersion` を更新する場合は `schemas.md` と `data_model_operations_overview.md` を同時更新する。

### 6.1 Document versioning / support level運用ルール（DATA-CONTRACT-01固定）

- `DocumentV2` の互換性レベルは次で固定する。
  - **Full**: `version: 2` かつ MVPで `L1/L1.5` に分類される運用対象（Document snapshot、merge decision append-read 連携）。
  - **Partial**: `version: 2` だが `L2/L2.5` の埋め込み限定/契約限定フィールド（例: `evidenceLinks` / `reviewAttribution` / `critiqueInputs`）を含む。保存・往復は保証するが個別CRUDは保証しない。
  - **Legacy**: `version: 1` または `version` 欠損の互換読込データ。読込時に `DocumentV2` へ正規化して扱う。
- 非互換変更（必須キー追加、既存キー意味変更、削除）は **version gate** で隔離する。`version: 2` の意味を壊さず、破壊的拡張は `version: 3` 以降でのみ許可する。
- `version gate` 導入前に実装が先行することを禁止し、契約文書（`schemas.md` / `data_model_operations_overview.md` / 該当issue AC）を先に同期する。

---


### 6.2 Stream D fail-safe guardrails

- 後方互換が曖昧な変更（既存キーの意味変更、必須化、削除）は `version` を上げずに導入してはならない。
- 新規フィールドは support level（L1/L1.5/L2/L2.5/L3/L0）を割り当てるまで `Contract-limited (L2.5)` とみなし、個別CRUD保証を主張しない。
- 運用責務が未確定（DecisionStatus=Pending）の項目は、スキーマに存在しても実装Go判断に使わない（fail-closed）。
## 7. 次に作るもの

- `02_Architecture/api.md`：Document（V1/V2）のCRUD I/F
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
- 運用解釈：`visibility` は公開範囲の意図を示すメタデータであり、外部サービスとの共有可否（SafeMode や export制御）を直接変更しない。

### 8.1.1 SafeMode / readOnly / visibility の評価優先順位

競合時の評価順は次で固定する（上位が優先）。

1. **SafeMode / share-export policy**（既定ON、漏えい防止）
2. **readOnly**（書込・共有・export など破壊的操作や外部サービスとの共有を抑止）
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

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true`（既定）: 未登録 `provider+external_uid` を受信したら `users` / `user_identities` を同時作成。
- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`（strict）: 未登録は `403` とし、事前プロビジョニング済みのみ許可。

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

### 11.1 Migration alignment snapshot（2026-05-20 / Stream D）

現行の物理スキーマは Alembic revision `20260314_0005` までで確定しており、本章の契約と次の対応で一致する。

- `20260211_0001_create_documents.py`:
  - `documents(id, version, updated_at, payload_json)`
- `20260303_0002_create_users_identities.py`:
  - `users(id, display_name, email, lifecycle_state, created_at, updated_at)`
  - `user_identities(id, user_id, provider, external_uid, created_at)`
  - `UNIQUE(provider, external_uid)`
- `20260313_0003_create_merge_decision_logs.py`:
  - `merge_decision_logs(id, doc_id, decision_id, group_id, snapshot_version, decided_at, payload_json)`
  - `UNIQUE(doc_id, decision_id)`
- `20260313_0004_add_merge_decision_log_indexes.py`:
  - `ix_merge_decision_logs_doc_group_id(doc_id, group_id, id)`
  - `ix_merge_decision_logs_doc_snapshot_id(doc_id, snapshot_version, id)`
- `20260314_0005_enforce_identity_lookup_uniqueness.py`:
  - `uq_user_identities_provider_lower_external_uid(lower(provider), lower(external_uid))`

互換性判定（2026-05-20時点）:

- **互換あり（backward-compatible）**
  - 読み取り経路へ影響しない index 追加。
  - `provider/external_uid` の case-insensitive uniqueness 強化（重複データがない前提）。
- **互換なし（backward-incompatible）**
  - 既存列の削除、必須化、意味変更は未実施。
  - `Document.version` の意味変更を伴う migration は未実施。
  - dry-run: `python -m kj_atlas_api.backfill_identity_refs --database-url <KJ_ATLAS_DATABASE_URL> --mapping-json mapping.json --dry-run`
  - apply: `python -m kj_atlas_api.backfill_identity_refs --database-url <KJ_ATLAS_DATABASE_URL> --mapping-json mapping.json`

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

#### CE1 v1 clarification（2026-05-03 / contract-only sync）

- `ContextQueryV1` / `ContextBundleV1` は CE1 の **closed-world最小契約** とする。
- `ContextBundleV1` の optional field は v1 では定義しない（required only）。
- 追加フィールド・列挙拡張・エラー語彙追加は **v2 契約改訂** でのみ許可する。
- エラー意味論の最小固定は `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`。
- `invalid_query_contract` のような補助バリデーション語彙を導入する場合でも、上記最小固定語彙を置換してはならない。
- フォールバックは fail-open 禁止（fail-closed 固定）。

### 1.3 CE0 handoff frozen I/F（2026-05-04 / Stream B）

CE1 への受け渡し固定I/Fを次で成果物化する（contract-only / mock-first）。

- `ContextQueryV1`
- `ContextBundleV1`
- `ProposalPatchV1`
- `AuditEventV1`

mock contract明記:
- backend未実装でも、上記4型を契約正本として stub/fixture で検証可能とする。
- 実装差し替え時も key set / enum / error semantics を v1 互換で固定する。

Deprecateルール（v1固定）:
1. v1 必須キーの削除/改名/意味変更は deprecate 不可（禁止）。
2. 拡張は v2追加のみ許可し、v1 は read-only contract として保持する。
3. `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の語彙と判定条件は不変。


## CE Contract Freeze Addendum（2026-05-04 / minimal delta）

### Context
- CE1/CE2/CE4 の並行進行で契約ドリフトを防ぐため、4型の責務境界を固定する。

### Decision
- SSOT対象を `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` に固定。
- v1では unknown key reject（closed-world）を維持し、契約の拡張は v2 でのみ扱う。
- mock-first 前提として `A1-CONTRACT-MOCK-v1` を契約検証入力に許可し、実装依存を持ち込まない。

### Consequences
- 下流は interface-only で先行でき、backend/frontend の完了待機を不要化できる。
- 契約変更要求は CDC再承認が必須となり、無断拡張を防止できる。

## Stream B Contract Annotation（Phase 2/3 alignment）

### Context
- CE系契約は実装前に type/signature を固定し、mock payload で下流連携を維持する必要がある。
- A系契約IDの一部は確定待ちがありうるため、参照は conditional を許可する。

### Decision
- v1契約は closed-world を維持し、必須キーとエラー語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を固定する。
- mock payload 例（`A2-minimal-v1`）を正規の検証入力として扱い、実装値を契約へ持ち込まない。
- conditional 参照中の契約IDは再定義せず、確定時に参照更新のみ実施する。

### Consequences
- CE2/CE4 は backend未完了でも契約テストを継続できる。
- 状態遷移（`unreviewed -> human_reviewed` の人手限定）と safeMode 境界の侵害を schema 検証で早期検出できる。
- 互換性判断は v1固定を基準に fail-closed で統一される。

### 1.3 Stream A contract freeze manifest（2026-05-07）

Contract Freeze と最小I/F合意の固定マニフェスト（read-only handoff）。

```yaml
hil_rs_a1_manifest_v1:
  freezeContractId: HIL-RS-02-A1-CONTRACT-FREEZE-v1
  schemaVersion: "1.0.0"
  overridePolicy: human_dual_control_only
  safeModeDefault: ON
  safeModeBoundary: SAFE_MODE_STRICT_ON
  contractIds:
    - A1-CRITIQUE-IF
    - A1-REDIFF-IF
    - A1-ATTR-IF
    - A1-ERROR-IF
  immutable_scope:
    - api_signature
    - major_data_types
    - compatibility_semantics
  extensible_scope:
    - v2_additive_fields_only
    - additional_audit_metadata
  decisionQueueTransition:
    - Pending->Approved
    - Pending->Rejected
  gate:
    a2a3_open_allowed: "a1Status==Done && pendingDecisionQueueCount==0"
    otherwise: Hold
```
### 1.2.1 CE1 freeze confirmation update（2026-05-07 / Stream B）

- Context contracts are frozen as v1 (`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`) and remain mock-first.
- Required `ContextQueryV1` key set is fixed to:
  - `goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode/previewConfirmed`
- Required `ContextBundleV1` key set is fixed to:
  - `queryCanonicalHash/bundleHash/selected/relations/evidence/contradictions/reviewFlags/truncationMeta/excludedReason`
- Error semantics are frozen in v1:
  - `422 preview_required`
  - `400 unknown_contract_key`
  - `409 nondeterministic_bundle`
- Verify gate is frozen as `sameQuery && sameBundle`; mismatch is fail-closed and self-repair is capped at max 3.
- Conflict-safe rule: agreement missing / dependency contradiction / collision detected => `held` and stop for instruction.

### 10.4 Stream E freeze note (2026-05-10)

- Contract freeze: `users` / `user_identities` 分離、strict時 `identity_not_provisioned`、admin provisioning 導線を AUTH 系の最小互換契約として固定。
- Compatibility rule: 判定必須キーは `status/code/provisioned` の3点を保持し、将来拡張は後方互換（追加のみ・既存キー意味変更禁止）で行う。
- Audit boundary: identity 生値（`provider/external_uid/email`）は監査最小項目へ保存しない。

## CE1 Contract Freeze Memo（2026-05-17 / Stream B）

- Contract IDs固定: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`。
- Error vocabulary固定: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`。
- `ContextQueryV1` / `ContextBundleV1` の v1 必須キー集合は closed-world（追加は v2 のみ）。
- Mock-first: `stubDatasetId=A2-minimal-v1` の契約検証のみ許可（実DB/実LLM/worker 禁止）。
- Proceed条件: CE2/CE4 は `sourceBundleHash` 参照整合を read-only で受け取る。

## CE1 Stream C handoff lock（2026-05-17 / interface-first）

- `ContextQueryV1` / `ContextBundleV1` の v1 必須キー集合は固定（closed-world; v2まで追加禁止）。
- Error semantics は `422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle` の3種固定。
- roundtrip contract test は `A2-minimal-v1` で実施し、同一 canonical query 3回の `queryCanonicalHash` / `bundleHash` 一致を合格条件とする。
- CE2/CE4 handoff は read-only で `sourceBundleHash === bundleHash` を比較可能であることのみを要件とし、実装依存（DB/LLM/worker）を含めない。
- Verify失敗時 self-correction は最大3回。超過時は `held` 停止を必須とする。


## 11. Stream D execution log (2026-05-19)

Phase直列実行（Read必須）で Data Contract & Model Ops を確認した。

1. Contract drift抽出: `DATA-CONTRACT-01` の観点（frontend/backend/api/schema）で `DocumentV2` 契約差分を再確認し、`version gate` 優先の fail-closed を維持。
2. Support level定義: `L1/L1.5/L2/L2.5/L3/L0` の語彙を本書の正本として再固定。新規フィールドは未分類なら `L2.5` 扱い。
3. CRUD境界更新（参照）: 個別CRUDの可否は `data_model_operations_overview.md` の表を正本とし、本書は型契約に限定。
4. Admin maintenance/recovery境界更新（参照）: 管理・復旧の実装可否は `DATA-MAINT-01` で管理し、契約変更を先行条件に据える。
5. Verify: `schemas.md` / `schemas_review_attribution.md` / `data_model_operations_overview.md` 間で support level 語彙と責務分離の矛盾がないことを確認。

## 12. Stream D reaffirmation (2026-05-19)

### Context
- `DocumentV2` には実装済み項目と契約先行項目が混在しており、型定義のみで運用CRUD保証と誤読されるリスクがある。

### Decision
- `L1/L1.5/L2/L2.5/L3/L0` を support level の唯一語彙として維持し、新規フィールドは未分類のまま導入しない。
- `PUT /docs/{doc_id}` create-if-absent をMVPの標準Create契約として維持し、`POST /docs` はversion gate導入まで契約候補（L0）に据え置く。

### Consequences
- 後方互換判定を version gate 基準で統一でき、feature flag による暫定互換運用を抑止できる。
- `data_model_operations_overview.md` / `schemas_review_attribution.md` / `issue-DATA-CONTRACT-01` と同一語彙で運用責務境界を同期できる。

## 13. Stream B contract lock sync (2026-05-20)

### Context
- `DocumentV2` の support level と backward compatibility 判定が、契約文書と運用境界文書で同時に固定されていない場合、実装側で「型=運用保証」と誤読される。

### Decision
- `DocumentV2` support level は `L1/L1.5/L2/L2.5/L3/L0` を唯一語彙として維持し、未分類フィールドは `L2.5` 扱いを継続する。
- backward compatibility は `version gate` 優先で固定し、`version: 2` の破壊的変更（必須化/意味変更/削除）は `version: 3` 以降でのみ許可する。
- CE1/CE2/CE4 連携I/Fは read-only contract（`queryCanonicalHash` / `bundleHash` / `sourceBundleHash`）として扱い、DB/API依存実装を混在させない。

### Consequences
- Stream B から下流への引き渡しは mock-first で再現可能になり、実装進捗待ちなしで契約検証を継続できる。
- CRUD保証の主張は `data_model_operations_overview.md` 側に限定され、契約文書単体の誤読リスクを抑制できる。

## 14. DOMAIN-EXPR-02 加算スキーマ拡張（2026-06-21）

ADR-0040 Phase 2: 保留 Hold + 未統合 Shelf の第一級化。加算原則に従い、全フィールドは optional。

### 14.1 Card.holdState

- 型: `"held" | "pending" | "shelved"` (optional)
- Support level: `L2.5`（未分類。実装検証後にL2以上へ昇格）
- 欠落時: 従来挙動（holdしていない通常カード）
- 意味:
  - `"held"`: 意図的に判断を保留しているカード
  - `"pending"`: 未処理/未着手のカード
  - `"shelved"`: Shelfへ退避中（本文は保持、配置からは一時的に除外）

### 14.2 ShelfEntry

- 型: `{ cardId: string; shelvedAt: string; reason?: string; }`
- 位置: `DocumentV2.shelf?: ShelfEntry[]`
- Support level: `L2.5`
- 欠落時: Shelfは空と解釈
- 不変条件: Shelf退避は可逆（cardIdのカード本文は削除されない）。Shelfからの復帰はカード削除と分離された独立操作。

### 14.3 後方互換

- 新フィールドはすべて optional。未対応クライアント・旧データは欠落を従来挙動として解釈
- `version: 2` のまま（破壊的変更なし）
- import/export/validate は未知フィールドを許容し、欠落時にデフォルト解釈する

### 14.4 参照

- ADR: `ADR-0040-domain-expression-first-class-strategy.md`
- Issue: `DOMAIN-EXPR-02-hold-and-pending-shelf`
- Frontend: `03_Implement/frontend/src/domain/types.ts` (Card.holdState, ShelfEntry, DocumentV2.shelf)

## 15. DOMAIN-TRACE-01 加算スキーマ拡張: Card.meta（通し番号・原データ遡及）（2026-07-08）

ADR-0048 D3 改訂（2026-07-03）採択分。加算原則に従い、全フィールドは optional。

### 15.1 Card.meta

- 型: `{ seq?: number; source?: string }` (optional)
- Support level: `L2.5`（契約限定。往復保持を保証し、個別CRUDは保証しない）
- 欠落時: 従来挙動（番号・出典を持たない通常カード）
- 意味:
  - `seq`: 任意の通し番号（有限数）。**自動連番を強制しない**（任意入力。一括採番機能があっても上書きは人間操作）。表示は「#N」。
  - `source`: 原データへの遡及参照（原発話・観察記録の行番号・URL 等の**自由記述**）。リンク先の自動取得・プレビュー・埋め込みは行わない。

### 15.2 語彙境界（`Card.sources` との役割分担・AC-1）

- `Card.sources`（既存）: canonical 化における**統合元カード id** の配列。意味は不変（再定義禁止）。
- `Card.meta.source`（本節）: **文書外部**の原データへの参照（自由記述）。カード id を指すためには使わない。
- 起票者・作成者・最終更新者・所有者などの**主体（provenance/accountability）メタは `Card.meta` に含めない**。これらの UI・保存・redaction 境界は `CARD-META-UI-01`（Decision Queue: `CARD-META-UI-01-DQ-01`、Pending）の確定を待つ。本節が確定するのは非主体メタ（`seq`/`source`）のみである。

### 15.3 取り込み境界（meta 内未知キーの fail-closed）

- import/validate（寛容・厳格の両モード）は `Card.meta` の **既知キー（`seq`/`source`）のみを受理**し、未知キーは破棄する。
- これは DOMAIN-KJ-01 の「未知エッジ種別の保全」（§3.3.2）と**対照的な意図的判断**である: 関係種別は語彙拡張の余地が採択済みだが、`Card.meta` の未知キーは主体メタ（起票者等）が `CARD-META-UI-01` の判断確定前に import 経由で永続化される抜け道になり得るため、fail-closed とする（同Issue AC-5「import 由来の provenance メタは非信頼データ」に整合）。
- `CARD-META-UI-01` で新キーが採択された場合は、本節の既知キー集合を追加更新してから実装する（契約先行）。

### 15.4 共有・書き出し境界（AC-4）

- **共有向け書き出し（レビューパック等）では `Card.meta` を既定で含めない**。含める場合は共有前確認の明示トグル「出典参照を含める」（**既定 OFF**）＋警告1行（出典は内部情報を含み得る旨）で opt-in する。
- 文書スナップショット自体の保存（`PUT /docs`）・バックアップ用途の文書 JSON 書き出しは redaction 対象外（既存の critique 等と同じ扱い。文書の完全な往復が目的のため）。
- SafeMode の固定マスク（未レビュー本文）とは**独立の軸**として管理する。SafeMode の ON/OFF は本トグルの既定（OFF）を変えない。

### 15.5 後方互換

- optional のため `version: 2` を維持（破壊的変更なし）。未対応クライアント・旧データは欠落を従来挙動として解釈。
- カード面（キャンバス）の通し番号バッジは**既定 OFF**（View パネルのトグルで表示）。CB-1 自己申告は issue 完了記録に記載する。

### 15.6 参照

- ADR: `ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂）
- Issue: `DOMAIN-TRACE-01-serial-number-and-source-provenance`, `CARD-META-UI-01-card-provenance-metadata-ui-boundary`（主体メタの上位境界）
- Frontend: `03_Implement/frontend/src/domain/types.ts` (Card.meta)

## 16. DOMAIN-EXPR-04 加算スキーマ拡張: 矛盾シグナルのレビュー決定（2026-07-08）

ADR-0040 Phase 4（根拠・主張・矛盾の人間レビュー第一級化）の残存スコープ。加算原則に従い、全フィールドは optional。AI権限境界は ADR-0041 CVI-2/CVI-3 の既存契約（本書 §1.2 CE2-LOW-RISK-AI-ASSIST の `ProposalStatus` 語彙）を新規許可なく再利用するため、新規ADRは不要と判断する。

### 16.1 背景・スコープ

既存の `analyzeContradictions()`（決定論的キーワード/構造ヒューリスティック。AI/LLM 呼び出しなし）は島・relationSummary 粒度の矛盾シグナル（C001〜C004）を検出済みだが、これまで「Focus」（画面遷移のみ）以外の操作導線がなく、シグナルへの人間の判断が持続化されない。本拡張は、シグナル自体に人間のレビュー決定（採用/保留/却下）を可逆に付与する。

**個別カード間の `EvidenceLink` を自動生成することはしない**: シグナルは島レベルの集約検出であり、特定のカードペアへ機械的に対応付けると検出精度を偽ることになるため。成果物（review pack）契約の拡張は本拡張のスコープ外（`PRODUCT-VALUE-03`/`PRODUCT-QA-01` が所有）。

### 16.2 ContradictionSignalDecision

```ts
export type ContradictionSignalReviewStatus = "accepted" | "held" | "rejected"; // CE2-PROPOSAL-IF の ProposalStatus 語彙を再利用（新規AI権限ではない）
export type ContradictionSignalDecision = {
  signatureKey: string; // `${signal.code}:${signal.pairKey ?? signal.entityRefs[0]?.idOrSignature ?? ""}`
  status: ContradictionSignalReviewStatus;
  decidedAt: string; // ISO 8601
};
```

- 位置: `DocumentV2.contradictionSignalDecisions?: ContradictionSignalDecision[]`
- Support level: `L2.5`（未分類。実装検証後にL2以上へ昇格）
- 欠落時、または該当 `signatureKey` が配列内に無い場合: 「未決定」（暗黙の "proposed"）として扱う。"proposed" 自体は永続化しない値であり、決定を取り消す操作は配列から該当エントリを削除する（DOMAIN-TRACE-01 の `Card.meta` 空値削除と同じ規約）。
- `signatureKey` は `analyzeContradictions()` の実行毎に再計算されるシグナル列から決定論的に導出する識別子であり、シグナル自体は永続化しない（`mergeSuggestionDecisions` が候補生成物と決定を分離する既存パターンに倣う）。

### 16.3 AI/検出ロジック権限境界（ADR-0041 CVI-2/CVI-3 の適用であり拡張ではない）

- `analyzeContradictions()` はシグナルを提示するのみで、`ContradictionSignalDecision` を書き込む経路を一切持たない。書き込みは人間のUI操作（1操作=1履歴ステップ）のみが行う。
- `status` は常に人間の最初のクリックで決まり、AIや検出ロジックが `"accepted"` を自動付与することはない（CVI-2 proposal-only）。
- 本拡張は新しい AI 権限を追加しない。既存 `CE2-LOW-RISK-AI-ASSIST`（本書 §1.2）の `ProposalStatus` 語彙を、決定論的ヒューリスティック検出器（`analyzeContradictions`）が生成する別種の候補（矛盾シグナル）に再適用するのみであり、ADR-0041 の枠内に留まる。

### 16.4 UI・可逆性

- 選択コンテキスト（SidePanel）の矛盾シグナル一覧に、各シグナルの現在状態（未決定/採用/保留/却下）と決定操作（採用にする/保留にする/却下する/決定を取り消す）を表示する。
- シグナル自体は決定状態に関わらず常に表示する（却下しても非表示にしない）。「却下」は「検討済みで対象外と判断した」ことの記録であり、シグナルの隠蔽ではない。
- 決定変更は `applyDocumentChange` による1操作=1履歴ステップ（⌘Z で取り消し可能）。

### 16.5 成果物・共有境界

- 本拡張は review pack バンドル契約（`bundle_export.ts` の `contradiction_trace_*.md` 等）を変更しない。narrative export / diagnostics.md への反映も本拡張のスコープに含めない（既存の `EvidenceLink.contradictionState` の narrative 反映で当該 AC は充足済み）。
- SafeMode / share-export の既定挙動は変更しない（決定状態は選択コンテキストのみに表示し、共有前チェック契約に新規項目を追加しない）。

### 16.6 後方互換

- 新フィールドはすべて optional。旧データ（配列欠落）は「すべて未決定」として解釈する。
- `version: 2` のまま（破壊的変更なし）。
- 寛容/厳格の両検証モードで、`signatureKey`/`status`/`decidedAt` のいずれかが不正な要素は破棄し、他の正しい要素は保全する（`mergeSuggestionDecisions` の既存パターンに倣う）。

### 16.7 参照

- ADR: `ADR-0040-domain-expression-first-class-strategy.md`（Phase 4）, `ADR-0041-core-value-invariants-single-guard.md`（CVI-2/CVI-3）
- Issue: `DOMAIN-EXPR-04-evidence-claim-contradiction-review`
- Frontend: `03_Implement/frontend/src/domain/view/contradiction_checks.ts`（シグナル生成、変更なし）, `03_Implement/frontend/src/domain/types.ts`（ContradictionSignalDecision）, `03_Implement/frontend/src/ui/SidePanel.tsx`（決定UI）

## 17. DOMAIN-KA-01 加算スキーマ拡張: KAカード種別（出来事/心の声/価値）（2026-07-08）

ADR-0048 D3 改訂（2026-07-03）採択分。加算原則に従い、全フィールドは optional。DOMAIN-TRACE-01（§15）と同じ D3改訂バッチでの条件付き採択。

### 17.1 Card.ka

```ts
export type CardKa = {
  voice?: string; // 心の声（言語化途中の一級データ。ガードレール: 嘘を書かない・話を盛らない・妄想しすぎない — UIヒント文言として反映し、機能では強制しない）
  value?: string; // 価値（KA法における本質的価値の言語化）
};
```

- 位置: `Card.ka?: CardKa`
- Support level: `L2.5`（未分類。実装検証後にL2以上へ昇格）
- 欠落時: 従来挙動（KA欄を持たない通常カード）
- `Card.text` は従来どおり**出来事の正本**として維持する（意味変更なし）。`voice`/`value` は `text` に併記しない別フィールド。
- 形状は `Card.meta`（§15.1）と同じ「関連する複数の optional フィールドを1つの入れ子オブジェクトへ束ねる」規約を踏襲する（フラットな `kaVoice`/`kaValue` ではなく `ka: { voice?, value? }`）。

### 17.2 取り込み境界

- import/validate（寛容・厳格の両モード）は `Card.ka` の既知キー（`voice`/`value`）のみを受理する。両方とも欠落・空文字列の場合は `ka` フィールド自体を省略する（`Card.meta` の空値削除規約と同じ）。
- `claimType` とは直交（統合・再定義しない）。critique・holdState 等の既存カード状態にも影響しない。

### 17.3 UI・非目標

- 選択コンテキストの基本編集群に「心の声」「価値」欄（未入力時は折りたたみ/プレースホルダ）。**カード面（キャンバス）には表示しない**（AC-4: 初期表示アンカー非回帰。UX-VISUAL-01 のメタ行チャネル予算を追加消費しない）。
- 非目標: 価値によるグルーピング画面の新設、AI による心の声/価値の自動抽出、カード面への3欄常時表示。

### 17.4 成果物境界

- レビューパック/narrative export への含め方は「本文に併記しない・任意セクション」とする。既定 OFF のオプトインで、設定時のみ KA 欄が設定されているカードを列挙する独立セクションとして追加する（`text` の本文とは混在させない）。
- SafeMode でのテキスト露出可否は `card.text` と同じ判定チャネル（`SafeModePolicy.canExposeText("card.text", ...)`）を再利用する（KA 欄は `text` と同等以上に機微な言語化途中データのため、別基準を新設しない）。

### 17.5 後方互換

- 新フィールドはすべて optional。旧データ（`ka` 欄欠落）は従来挙動として解釈する。
- `version: 2` のまま（破壊的変更なし）。

### 17.6 参照

- ADR: `ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂）
- Issue: `DOMAIN-KA-01-ka-card-fields`
- Frontend: `03_Implement/frontend/src/domain/types.ts`（Card.ka）


## 18. EXT-CONN-03 契約先行固定: agent-constraints.v1（訂正ループの輸出）＋加算スキーマ拡張（2026-07-15）

ADR-0054 段階3の契約先行固定（issue-EXT-CONN-03 AC-1 / DecisionQueueRef が要求する「constraint 契約の `schemas.md` 先行固定」）。本節は**契約の固定のみ**を行い、実装の着手可否は EXT-CONN-03 issue の段階ゲート（段階1/2 の運用知見）に従う。加算原則に従い、DocumentV2 への追加フィールドはすべて optional。

### 18.1 目的と設計判断（方式設計の要点）

TRACE（arXiv:2606.13174）の知見「記憶への保存では選好違反の57.5%が残る。訂正は次回実行の**制約**として明示的に渡す必要がある」に基づき、人間がカード・島・エージェント提案へ付けた違和感タグ・保留・却下を機械可読な制約として輸出する。

**契約形態の決定**: issue-EXT-CONN-03 が挙げた2候補 (a) `agent-task.v1` ガードレール節への追記 / (b) 独立の `agent-constraints.v1` 文書 のうち、**(b) 独立文書を正とし、(a) は (b) の埋め込みプロファイルとする**。理由:

1. 配布経路が2つある（手動レーン=タスクシート同梱、自動レーン=EXT-CONN-01 MCP サーバーの読み取りツール）。独立文書なら1つの正本形状を両経路で共有でき、ガードレール節専用形式だと MCP 経路で二重定義になる。
2. 制約の語彙はタスクパッケージと独立に進化しうる（版管理の分離）。
3. `external_agent_collaboration_spec.md` §3.3 のタスクシートには「制約」節として同一 JSON を埋め込む（同 spec 参照）。定義の重複を作らない。

**内部設計の外部化**: 本契約は HIL-RS の内部 critique 収集（`buildHilRsCritiqueInputs`: card/island の `critiqueTags`＋自由記述 → `CritiqueInput.constraintHints`）と同じ源泉・同じ5種タグ語彙（§18.3）を用いる。新しい語彙・新しいAI権限を導入しない（語彙重複禁止の既存規約に従う）。

### 18.2 AgentConstraintsV1（輸出契約・正本）

```json
{
  "schemaVersion": "agent-constraints.v1",
  "docId": "string",
  "baseDocSignature": "string (`${doc.id}:${doc.updatedAt}` — context-projection.v1 と同一形)",
  "safeMode": "boolean",
  "entries": [
    {
      "target": {
        "kind": "proposal | card | island",
        "taskId": "string (kind=proposal のみ)",
        "proposalId": "string (kind=proposal のみ)",
        "proposalKind": "string (kind=proposal のみ。agent-response.v1 の kind)",
        "cardId": "string (kind=card のみ。レビュー済みカードに限る — §18.5)",
        "islandId": "string (kind=island のみ)"
      },
      "critiqueTags": ["too_close | too_far | not_the_same | feels_off | no_articulable_reason"],
      "facts": ["held | rejected | deferred"],
      "note": "string | null (人間の自由記述。SafeMode ON では null — §18.5)",
      "noteRedacted": "boolean (SafeMode により note を秘匿した場合 true)"
    }
  ],
  "counts": {
    "withheldCardConstraints": "number (未レビューカード対象のため ID を出さず件数のみ計上した制約数)"
  },
  "constraintsHash": "string (canonical JSON 全体の sha256 hex。決定論)"
}
```

制約（契約不変条件）:

- 各 entry は `critiqueTags` と `facts` の**少なくとも一方が非空**（空の制約は生成しない）。
- **理由不要原則の保持**: `note` は任意。`no_articulable_reason` は一級のシグナルであり、理由の言語化を輸出の条件にしない（domain.md の違和感原則）。
- **反スコアリング**: `score` / `rank` / `confidence` / `priority` / `weight` 等の数値評価語彙をトップレベル・entry・target のいずれにも**含めない**（契約禁止。テストは直列化文字列への正規表現で固定する）。制約間に順序的優先度は存在せず、`entries` の並びは決定論のためのソート順（§18.6）であって重要度ではない。
- **エージェント側の遵守は受け手の責務**: kj-atlas は明示的に渡すところまで（issue 非目標）。遵守検証・自動学習・制約の自動生成は本契約のスコープ外。

### 18.3 制約の源泉（すべて文書内・人間の判断のみ）

| 源泉 | entry への写像 | 備考 |
|---|---|---|
| `Card.critiqueTags` / `Card.critique` | `target.kind="card"`＋`critiqueTags`＋`note` | §18.5 のレビュー済み条件を満たす場合のみ ID を出す |
| `Island.critiqueTags` / `Island.critique` | `target.kind="island"`＋`critiqueTags`＋`note` | 島 ID は context-projection.v1 で既に公開済みの識別子 |
| `Card.holdState === "held"` | `target.kind="card"`＋`facts:["held"]` | 同上（レビュー済み条件） |
| `mergeSuggestionDecisions`（`decision: "reject" \| "defer"`） | `target.kind="proposal"` 相当が無いため、対象カードがすべてレビュー済みの場合のみ `target.kind="card"`（複数 entry）へ展開。`facts:["rejected"]` / `["deferred"]`、`note` は決定 entry の `note` | 却下・保留の**事実**の輸出。`accept`/`partial` は制約ではない |
| `agentProposalDecisions`（§18.4。`decision: "rejected" \| "held"`） | `target.kind="proposal"`（taskId/proposalId/proposalKind）＋`facts` | エージェント既知の識別子のみで構成され、文書内部 ID を含まない |

- 源泉はすべて人間の UI 操作で書かれた文書内データであり、決定論的に再導出できる（バックエンド状態・セッション状態に依存しない）。
- **v1 で源泉に含めないもの**: `contradictionSignalDecisions`（決定論的検出器のシグナルへの判断であり、エージェント行動への訂正ではない）、`shelf`（内からの退避であり訂正シグナルではない — ADR-0054 用語定義「シェルフとの対」）。将来の版で再検討する場合も加算のみとする。

### 18.4 加算スキーマ拡張: AgentProposalDecisionEntry / constraintExportOptIn

現状、エージェント提案（agent-response.v1）への却下・保留はバックエンド監査（`/context-audit`）とセッション状態にのみ記録され、文書には持続化されない。制約輸出を文書から決定論的に導出可能にするため、`mergeSuggestionDecisions` / `contradictionSignalDecisions` と同じ「決定の文書内持続化」パターンを適用する。

```ts
export type AgentProposalDecision = "adopted" | "rejected" | "held";

export type AgentProposalDecisionEntry = {
  id: string;            // `${taskId}:${proposalId}`（文書内一意・重複時は decidedAt が新しい方を採用）
  taskId: string;        // agent-task.v1 の taskId（エコーバック値）
  proposalId: string;    // agent-response.v1 応答内の proposalId
  proposalKind: string;  // agent-response.v1 の kind（自由文字列として保全）
  decision: AgentProposalDecision;
  decidedAt: string;     // ISO8601
  agent?: string;        // agent-response.v1 の agent（markdown_sanitize 済み）
};

// DocumentV2 への加算（すべて optional）:
//   agentProposalDecisions?: AgentProposalDecisionEntry[];
//   constraintExportOptIn?: boolean;   // 欠落 = false = 輸出無効（既定OFF）
```

- `adopted` も記録する（EXT-CONN-04 根拠トレイルの将来素材）。ただし**制約として輸出されるのは `rejected` / `held` のみ**（§18.3）。
- 決定の書き込みは人間の UI 操作のみ（proposal-only 維持。ADR-0041 CVI-2）。`applyDocumentChange` による 1操作=1履歴ステップで、却下も ⌘Z で取り消し可能になる（現状の「セッション限りの却下」からの改善。保全思想）。
- 取り込み境界: 寛容/厳格の両検証モードで、`id`/`taskId`/`proposalId`/`decision`/`decidedAt` のいずれかが不正な要素は破棄し、他の正しい要素は保全する（`mergeSuggestionDecisions` の既存パターン）。
- `constraintExportOptIn` の既定は **OFF**（欠落=false）。ON への切り替えは人間の明示操作（Claude Design P32 B-3「輸出は既定で含めない・明示 opt-in」）。

### 18.5 安全境界（EXT-CONN-01 の原則を弱めない）

ADR-0054「後段が前段の安全原則を弱めることはない」に従い、EXT-CONN-01 再レビューゲート（2026-07-13）の確定事項を本契約にそのまま継承する:

1. **未レビューカードの ID はいかなる形でも出さない**: `target.kind="card"` の entry は対象カードが `textReviewed === true` の場合のみ生成する。未レビューカードへの critique/hold は `counts.withheldCardConstraints` に**件数のみ**計上する（ID・タグ内訳・note のいずれも出さない。タグ内訳の集計すら相関ベクトルになりうるため v1 では件数単独とする）。
2. **proposal target は文書内部 ID を含まない**: `taskId`/`proposalId` はエージェント自身が生成・受領した識別子のエコーバックであり、新たな情報開示ではない。提案の本文・content の引用は行わない（採用後に編集・レビューされた本文の逆流を防ぐ）。
3. **SafeMode**: 自由記述（`note`）は人間著述だがカード本文を引用しうるため、`SafeModePolicy.canExposeText("card.text", "share", safeMode)` と同一チャネルで判定し、秘匿時は `note: null`＋`noteRedacted: true` とする（KA §17.4 の「別基準を新設しない」規約に従う）。タグ・facts・counts は構造情報であり SafeMode の影響を受けない。短縮ハッシュによる placeholder は用いない（EXT-CONN-01 と同じ相関ベクトル回避）。
4. **未レビュー本文の混入なし**: 本契約はカード本文フィールドを一切持たない（issue AC-4 を構造で保証）。

### 18.6 決定論・監査

- `entries` のソート順: `target.kind`（proposal → card → island）→ 各 ID の辞書順。同一 target への複数源泉（例: critique と hold）は1 entry に併合する。
- `constraintsHash` は canonical JSON（`patch_fingerprint.ts` の `canonicalizeJson`）全体の sha256 hex。同一文書・同一 SafeMode 状態からの再輸出は同一ハッシュになる（context-projection.v1 の `bundleHash` と同じ規律）。
- 監査相関: タスクシート同梱時は agent-task.v1 相関ブロックに `constraintsHash` を追加（optional・後方互換）。MCP 経由の読み取りは EXT-CONN-01 と同じ監査経路に `constraintsHash` を記録する。

### 18.7 配布（輸送を新設しない）

- **手動レーン**: `external_agent_collaboration_spec.md` §3.3 のタスクシートに任意節「制約」として同梱（同 spec §3.3a 参照）。`constraintExportOptIn` が ON の文書でのみ生成される。
- **自動レーン**: EXT-CONN-01 の MCP サーバー（`03_Implement/mcp/`）に読み取り専用ツール `get_agent_constraints` を追加する。既存 `get_context_projection` と同じサーバー・同じ投影コア共有パターン（`03_Implement/frontend/src/export/agent_constraints_export.ts` を monorepo import）であり、**新しい輸送・新しいサービスは作らない**（issue の「EXT-CONN-01 の投影に合流」の充足形）。`constraintExportOptIn` が OFF の文書に対してはエラー応答（契約 payload を返さない）。
- **用語の区別**: `ContextProjectionConstraint`（context-projection.v1 の**取得範囲**セレクタ: reviewed-only/evidence/contradiction/summary）と本契約の **constraint（訂正制約）** は別概念。取得範囲セレクタへ `"constraints"` 値を追加する案は、この語衝突を避けるため採らず、独立ツールとした。

### 18.8 後方互換

- 新フィールド（`agentProposalDecisions` / `constraintExportOptIn`）はすべて optional。旧データ（欠落）は「決定記録なし・輸出無効」として解釈する。
- `version: 2` のまま（破壊的変更なし）。
- agent-task.v1 相関ブロックへの `constraintsHash` 追加は optional であり、既存の応答エコーバック規約を変更しない。往復互換: agent-response.v1 側に constraints への応答フィールドは**設けない**（制約は一方向の入力であり、エージェントが制約に「回答」する契約を作ると遵守の自己申告に意味があるかのような誤認を生むため）。
- Support level: `L2.5`（未分類。実装検証後に L2 以上へ昇格）。

### 18.9 参照

- ADR: `ADR-0054-external-connection-layer-staged-introduction.md`（段階3）, `ADR-0049-external-flat-rate-agent-collaboration.md`（安全境界の正本）, `ADR-0041-core-value-invariants-single-guard.md`（CVI-2 proposal-only）
- Issue: `EXT-CONN-03-critique-constraint-export`
- Research: `01_Plans/research-2026-07-12-trigger-ai-external-integration.md`（追補A3: TRACE 定量根拠）
- Spec: `02_Architecture/external_agent_collaboration_spec.md`（§3.3a 制約節の埋め込みプロファイル）
- Frontend: `03_Implement/frontend/src/domain/types.ts`（CRITIQUE_TAGS / AgentProposalDecisionEntry）, `03_Implement/frontend/src/domain/hil_rs_payload.ts`（内部 critique 収集の前例）, `03_Implement/frontend/src/export/context_bundle_projection.ts`（外部読み取り面の安全境界前例）
