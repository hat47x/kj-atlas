# HIL-RS-01-A1: Architecture最小I/F契約（Critique / 再提案差分 / レビュー帰属）

- Contract ID: `HIL-RS-01-A1`
- Status: Fixed
- Owner: Architecture Owner
- Scope: `02_Architecture/`
- Upstream: `01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `00_Prompt/domain.md`
- Related: `02_Architecture/review_attribution.md`, `02_Architecture/schemas_review_attribution.md`

## 0. 目的

本契約は、`ADR-0026` D2（契約先行）に従い、A2（Frontend実装）/A3（Documentation同期）が契約参照のみで着手できる最小I/F境界を固定する。

## 1. 非目標

- Frontend実装詳細（UIコンポーネント、状態管理、イベント処理）を定義しない。
- LLM provider・推論実行制約の再設計を行わない。
- SafeMode既定ON、share/export漏えい防止契約を緩和しない。

## 2. 契約一覧（必須/任意/禁止）

### 2.0 正規I/F署名（A2/A3参照専用）

- Single Reference（SSOT）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Contract IDs: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`

#### CritiqueInputContract（固定）

- `schemaVersion`: `"1.0.0"`（固定）
- `requiredFields`（固定）:
  - `critiqueId`
  - `targetRef`
  - `critiqueType`
  - `createdAt`
  - `iteration`

#### ReviewAttributionContract（固定）

- `schemaVersion`: `"1.0.0"`（固定）
- `auditFields`（固定）:
  - `reviewState`
  - `reviewedAt`
  - `reviewerRef`
  - `auditRecordedAt`
- `overridePolicy`（固定）:
  - `allowed`: `"human_dual_control_only"`
  - `prohibited`:
    - `"ai_only_override"`
    - `"safemode_relaxation"`
    - `"share_export_leakage_relaxation"`
  - `requiredApproval`: `"SecurityOfficer+SystemOwner"`

#### DeterministicTieBreakContract（固定）

- `contractKey`: `"deterministicTieBreakOrder"`（固定）
- `schemaVersion`: `"1.0.0"`（固定）
- `order`（固定・入替禁止）:
  1. `padding_compliance`
  2. `self_intersection_avoidance`
  3. `minimum_area_delta`
  4. `minimum_vertex_count`
- `rule`（固定）:
  - 同一入力には同一順序評価を必ず適用し、同一出力を返す。
  - 順序の省略・追加・名称変更は不可（契約改訂扱い）。
  - Gate 0承認がない順序変更提案は却下する。

### 2.1 Critique入力I/F（Contract Key: `A1-CRITIQUE-IF`）

#### 必須
- `critiqueId`: critiqueイベントを一意識別する opaque string。
- `targetRef`: critique対象（card/cluster/edge/proposal）を示す参照。
- `critiqueType`: `too_close | too_far | not_the_same | feels_off | no_articulable_reason`。
- `createdAt`: ISO-8601 timestamp。
- `iteration`: 再提案世代番号（1以上の整数）。

#### 任意
- `comment`: 補足テキスト（理由任意の原則を壊さない補助情報）。
- `constraintHints`: 再提案に渡す追加制約ヒント（順序・距離・分離など）。

#### 禁止
- critique入力をもって「唯一正解」や自動確定状態へ遷移させること。
- `reviewed` 状態の自動更新。
- PII（実名/メール/外部ID生値）を critique payload に保存すること。

### 2.2 再提案差分I/F（Contract Key: `A1-REDIFF-IF`）

#### 必須
- `proposalId`: 再提案案ID。
- `basedOnIteration`: 直前案のiteration参照。
- `diffOps[]`: 可逆差分操作の配列。
- `traceKey`: critique入力から再提案までの追跡キー（`critiqueId` と連結可能）。

#### diffOps最小単位
- `opId`: 差分操作ID（案内で一意）。
- `opType`: `add | remove | move | regroup | relabel`。
- `targetRef`: 変更対象参照。
- `before` / `after`: 適用前後スナップショット（remove/add の場合は片側null可）。

#### 任意
- `rationale`: 変更理由の短文（説明可能性補助）。

#### 禁止
- 片方向差分のみを保存して逆操作不能にすること。
- traceKey未設定で critique→再提案の因果を切断すること。
- SafeModeで禁止される share/export 操作を再提案適用時に暗黙実行すること。

### 2.3 レビュー帰属I/F（Contract Key: `A1-ATTR-IF`）

#### 必須
- `reviewState`: `unreviewed | human_reviewed`。
- `reviewedAt`: `human_reviewed` 遷移時の timestamp。
- `reviewerRef`: non-empty opaque string（`review_attribution` 契約に準拠）。

#### 任意
- `reviewContext`: `internal | external | self` などの文脈ラベル。
- `ownerRef`: 表示・責務トレース用の任意参照。

#### 禁止
- AI処理のみで `human_reviewed` に遷移すること。
- `provider` / `external_uid` / email 等の生IDを attribution payload に保存すること。
- `reviewEvents` 欠如をエラー化して閲覧不可にすること（互換性維持）。

## 3. 横断制約（安全・可逆・並列）

### 3.1 安全制約
- SafeMode既定ONを前提とし、契約でOFFを要求しない。
- share/export漏えい防止の後退を禁止する。
- 監査情報は最小化し、PIIは既定で保存しない。

### 3.2 可逆制約
- 再提案差分は必ず `before/after` を持ち、巻き戻し可能であること。
- critique は否定・留保データとして保持し、削除による履歴欠落を既定動作にしない。

### 3.3 A2/A3並列実行境界
- A2は `03_Implement/**` のみ編集し、契約本文は参照専用。
- A3は `04_Documentation/**` のみ編集し、実装コードを変更しない。
- 共有リソース（`01_Plans/issues/README.md`, `01_Plans/project-progress-dashboard.md`）更新は統合フェーズへ分離する。

## 4. ADR更新要否判定

### Context

- `ADR-0026` D2は「A1で最小I/F契約を先に固定し、A2/A3が参照のみで着手できる状態」を要求している。
- 本書の変更範囲はA1契約の明文化に限定され、上位の価値判断・方針変更は含まない。

### Decision

- 判定: **ADR更新不要**。
- 理由:
  - 本書は `ADR-0026` D2で要求された「最小I/F契約の固定」を具体化する下位仕様であり、意思決定の追加・変更を含まない。
  - 既存 `review_attribution` 契約（opaque reviewerRef / PII最小化）を踏襲し、上位方針を変更しない。

### Consequences

- A1はArchitecture文書の更新のみで完了可能となり、A2/A3は契約待ちを発生させず着手できる。
- 今後、契約ID/安全制約/可逆要件そのものを変更する場合は、`ADR-0026` への追記または後続ADR起票を必須とする。

## 5. 契約未固定箇所チェック（A1完了判定）

- `A1-CRITIQUE-IF`: 0件（固定済み）
- `A1-REDIFF-IF`: 0件（固定済み）
- `A1-ATTR-IF`: 0件（固定済み）
- A2/A3参照先未定: 0件（本ファイルを単一参照先として固定）

### 5.2 Decision Queue解消（A1）

- `DQ-A1-01` CritiqueInputContract.requiredFields 未固定 → **Resolved**（`critiqueId | targetRef | critiqueType | createdAt | iteration` で固定）。
- `DQ-A1-02` CritiqueInputContract.schemaVersion 未固定 → **Resolved**（`1.0.0` で固定）。
- `DQ-A1-03` ReviewAttribution.auditFields 未固定 → **Resolved**（`reviewState | reviewedAt | reviewerRef | auditRecordedAt` で固定）。
- `DQ-A1-04` ReviewAttribution.overridePolicy 未固定 → **Resolved**（`human_dual_control_only` で固定）。

### 5.1 単一定義検証（Phase 1/4 記録）

- Phase開始時の対象3ファイル再Read: `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `hil_rs_01_a1_minimum_interface_contract.md`。
- 検証対象: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `hil_rs_01_a1_minimum_interface_contract.md`
- 検証方法: `rg` による3ファイル横断検査（A1 issue / HIL-RS-01親issue / 本契約）
- 判定:
  - 契約ID 3件は意図した参照箇所のみで検出され、競合する別IDは未検出。
  - 参照先は `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` のみを single reference として固定。


## 6. A2/A3 handoff固定情報（Proceed）

- Contract IDs（固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `deterministicTieBreakOrder`
- Single Reference（固定）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 非目標（A2/A3共通）:
  - 単一スコア/ランキングによる自動確定を導入しない。
  - SafeMode既定ONとshare/export漏えい防止を弱めない。
  - provider/external_uid/email等の生IDをpayloadへ保存しない。
- 禁止事項（A2/A3共通）:
  - 契約本文を参照せず独自I/Fを追加すること。
  - 共有リソース（`01_Plans/issues/README.md`, `01_Plans/project-progress-dashboard.md`）をストリーム内で更新すること。
  - A2で`04_Documentation/**`、A3で`03_Implement/**`を同時に変更すること。

### 6.2 Stream B/C向け受け渡しパケット（A1契約/I-F固定）

- 受け渡し先:
  - Stream B（A2: Frontend実装）
  - Stream C（A3: Documentation同期）
- 契約ID（固定・参照専用）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
- 単一参照先（固定）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 固定値（変更禁止）:
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`
  - `DeterministicTieBreakContract.order=padding_compliance>self_intersection_avoidance>minimum_area_delta>minimum_vertex_count`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 禁止境界:
  - Stream B は `03_Implement/**` 以外を変更しない。
  - Stream C は `04_Documentation/**` 以外を変更しない。
  - 共有リソース（`01_Plans/issues/README.md`, `01_Plans/project-progress-dashboard.md`）を更新しない。
- 停止条件（B/C共通）:
  - 契約IDの複線化、または単一参照先の不一致を検出した場合。
  - SafeMode既定ON / share-export漏えい防止の後退を示唆する変更を検出した場合。
  - 未定義競合（schemaVersion・requiredFields・overridePolicy）を検出した場合。
- 変更凍結宣言:
  - A1契約本文は凍結済みとし、変更要否は統合フェーズでの人間判断にエスカレーションする。

### 6.1 A2 mock前提（fixture/stub契約）

- A2は `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` の3契約IDを fixture 名にそのまま使用し、別名aliasを禁止する。
- fixture schemaVersion 固定値:
  - critique fixture: `1.0.0`
  - review attribution fixture: `1.0.0`
- stub判定前提:
  - `reviewOverridePolicy` は `human_dual_control_only` 以外を返してはならない。
  - `reviewerRef` は opaque ID 形式を前提とし、email/provider/external_uid を返してはならない。
- A2のモック検証は「同一fixture入力→同一出力」を必須とし、未定義フィールドの自動補完を禁止する。

## 8. Contract Freeze Evidence Template（Stream A 固定）

### 8.1 Freeze Flags

- `contractLinkLocked=true`
- `sharedResourceFreeze=true`

### 8.2 Evidence Record Template

```yaml
freezeRecord:
  stream: "A"
  phase: "Phase 3 Contract Fix"
  contractLinkLocked: true
  sharedResourceFreeze: true
  singleReference:
    - "02_Architecture/hil_rs_01_a1_minimum_interface_contract.md"
  lockedContractIds:
    - "A1-CRITIQUE-IF"
    - "A1-REDIFF-IF"
    - "A1-ATTR-IF"
    - "deterministicTieBreakOrder"
  fixedValues:
    critiqueSchemaVersion: "1.0.0"
    critiqueRequiredFields:
      - critiqueId
      - targetRef
      - critiqueType
      - createdAt
      - iteration
    reviewSchemaVersion: "1.0.0"
    reviewAuditFields:
      - reviewState
      - reviewedAt
      - reviewerRef
      - auditRecordedAt
    reviewOverridePolicy: "human_dual_control_only"
    deterministicTieBreakOrder:
      - padding_compliance
      - self_intersection_avoidance
      - minimum_area_delta
      - minimum_vertex_count
  freezeDeclaration: "A2/A3開始後は本契約の本文変更を禁止し、変更は統合フェーズの人間判断でのみ実施する"

gate0ApprovalEvidence:
  approvalId: "GATE0-HIL-RS-01-A1-20260313-001"
  approvers:
    - role: "SecurityOfficer"
      approvedBy: "sec-officer-01"
      approvedAt: "2026-03-13T09:00:00Z"
    - role: "SystemOwner"
      approvedBy: "system-owner-01"
      approvedAt: "2026-03-13T09:05:00Z"
  decisionStatement: "deterministicTieBreakOrderおよびA1契約ID固定を承認し、A2/A3着手を許可する"
  impactScope:
    includes:
      - "A1-CRITIQUE-IF"
      - "A1-REDIFF-IF"
      - "A1-ATTR-IF"
      - "deterministicTieBreakOrder"
    excludes:
      - "03_Implement/** への実装変更"
      - "04_Documentation/** への運用文書変更"
  gateDecision: "approved"
  followUpAction:
    onApproved: "A2/A3へProceed（契約本文変更は禁止）"
    onRejected: "Stream Aへ差し戻し（A2/A3は停止継続）"
    onConditional: "条件充足までA2/A3を停止"
```

### 8.3 判定条件（AC/DoDチェック用）

- `contractLinkLocked=true` は、A2/A3の参照先が単一正本1件であることを示す。
- `sharedResourceFreeze=true` は、`01_Plans/issues/README.md` と `01_Plans/project-progress-dashboard.md` を統合フェーズまで更新しない宣言を示す。
- 両フラグが true でない場合、A2/A3へのProceedを禁止する。

## 7. AC/DoD自己検証（Stream A）

- [x] `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` の3契約IDが固定されている。
- [x] A2/A3の単一参照先が本ファイルで固定されている。
- [x] SafeMode既定ON・share/export漏えい防止後退禁止が明記されている。
- [x] A2/A3の禁止境界（編集スコープ分離・共有リソース更新禁止）が明記されている。


## 9. Stream A Final Lock Record（2026-03-13）

- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- 単一参照先は本ファイルのみ（`02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`）。
- 契約固定値（`schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`）は変更凍結とし、改訂要求は統合フェーズで人間承認を必須とする。
