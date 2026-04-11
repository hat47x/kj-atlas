# Issue Draft: CE1 ContextQuery/ContextBundle foundation

- Type: Feature request
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Backend/Frontend Team
- Scope: `01_Plans/issues/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE1-CONTEXT-FOUNDATION`
- RequirementStatement: ContextQuery/Bundleを決定論で生成し、Query Preview必須導線を契約として固定する。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE0完了 / 操作=同一Queryを再実行 / 期待結果=bundleHash一致 / 除外=自動適用
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- Stream: `C` (CE1専任 / Contracts only / Docs-Plan only)
- DecisionQueueRef: `UNC-VSC-CE-01-02`

## 0) Phase 1 Read（I/F抽出 + mock許容）

- CE1必須I/F: `ContextQuery` / `ContextBundle` / `bundleHash` / `previewConfirmed`。
- 依存先（CE2/CE4）は CE1実装完了待ちを禁止し、`mock ContextQuery/Bundle I/F` を正規契約として先行検証する。
- 本Issueは契約固定のみを扱い、実装詳細（APIハンドラ/型生成/UI部品）は範囲外。

## 直列フェーズ固定（Stream C / Contract Freeze）

1. **Phase 1（Read）**: `ContextQuery` / `ContextBundle` / `bundleHash` / `previewConfirmed` の最小I/Fを抽出・固定する。  
2. **Phase 2（CDC）**: `previewConfirmed=false` は常に `422 preview_required` として拒否する CDC（Contract Definition Check）を固定する。  
3. **Phase 3（Plan: AC/DoD合意）**: canonical JSON + sha256 の `bundleHash` 算出手順、drift-stop 条件、AC/DoD を合意済み契約として固定する。  
4. **Phase 4（Execute: mock-first契約固定）**: CE0/CE2/CE4 完了待ちを行わず、mock `ContextQuery/ContextBundle` I/F 前提で契約同期を実行する。  
5. **Phase 5（Verify/Proceed）**: CE0/CE1/CE2 の語彙・契約ID整合を検証し、Verify の自己修復は最大3回、4回目失敗時は即停止する。

## Contract ID Freeze（CE1）

| Contract ID | Summary | Must |
| --- | --- | --- |
| `CE1-CTXQ-IF` | ContextQuery 最小I/F固定 | `queryId/goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode/previewConfirmed` |
| `CE1-CTXB-IF` | ContextBundle 最小I/F固定 | `bundleHash/selected/relations/evidence/contradictions/reviewFlags/truncationMeta/excludedReason` |
| `CE1-HASH-DET-IF` | deterministic hash 契約 | canonical JSON + sha256 + 同一query再実行一致 |
| `CE1-PREVIEW-GATE-IF` | Query Preview ゲート契約 | `previewConfirmed=false -> 422 preview_required` |

## 1) Context

- CE-1は CE-2/3/4 の前提であり、ここで Query/Bundle の最小I/Fが曖昧だと後続で互換性崩壊が起きる。
- Stream B では実装詳細ではなく、モックで依存切離し可能な契約（API/型/責務境界）を先に固定する。

## 2) Decision（ADR-0028整合）


### 2.0 Decision framing（Context / Decision / Consequences）

- Context: CE-1 は CE-2 以降の照合基盤であり、`bundleHash` の非決定論は downstream の `sourceBundleHash` 検証を破壊する。
- Decision: ContextQuery/ContextBundle の最小I/Fと canonical hash 手順を契約として固定し、実装は mock-first で backend/frontend を疎結合にする。
- Consequences: CE-2+ は `sourceBundleHash === bundleHash` を必須照合し、未一致は apply 不可（No-Go）とする。

### 2.1 API/型 契約（実装非依存）

- Query endpoint（論理名）:
  - `POST /context/query`: Query payload の構文・必須項目検証のみ。
- Bundle endpoint（論理名）:
  - `POST /context/bundle`: deterministic projection + `bundleHash` の返却。

### 2.2 ContextQuery 最小I/F

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `queryId` | string (UUID) | Yes | 監査・再実行照合キー |
| `goal` | string | Yes | 問合せ目的（空文字不可） |
| `scope` | enum(`document`\|`view`\|`island`) | Yes | 対象範囲 |
| `depth` | integer (0..5) | Yes | 探索深さ上限 |
| `constraints` | object | Yes | token/time/source 制約（数値は正） |
| `reviewFilter` | enum(`reviewedOnly`\|`includeUnreviewed`) | Yes | 既定=`reviewedOnly` |
| `safeModePolicy` | enum(`strict`) | Yes | CE-1では`strict`固定 |
| `outputMode` | enum(`summary`\|`proposal`\|`candidate`) | Yes | 出力目的 |
| `previewConfirmed` | boolean | Yes | Query Preview承認済みでなければ422 |

### 2.3 ContextBundle 最小I/F

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `bundleHash` | string (sha256 hex) | Yes | canonical serializationに基づく決定論ハッシュ |
| `selected` | array | Yes | 採択要素（ID昇順） |
| `relations` | array | Yes | 関連構造（`type,from,to` 昇順） |
| `evidence` | array | Yes | 根拠（`cardId` 昇順） |
| `contradictions` | array | Yes | 矛盾候補（`weight desc,id asc`） |
| `reviewFlags` | object | Yes | reviewed/unreviewed 内訳 |
| `truncationMeta` | object | Yes | 省略理由/上限情報 |
| `excludedReason` | array<string> | Yes | safeMode/reviewFilter による除外理由 |


### 2.5 Determinism 契約（機械判定可能条件）

`bundleHash` は以下の手順で算出し、差分がある場合は不一致として扱う。

1. `ContextBundle` から `generatedAt`, `traceId`, `providerLatencyMs` など非決定論フィールドを除外。
2. 配列順序を固定（`selected=id asc`, `relations=(type,from,to) asc`, `evidence=cardId asc`, `contradictions=(weight desc,id asc)`）。
3. キー順序を UTF-8 バイト列の辞書順で整列した canonical JSON を生成。
4. `sha256(canonical_json)` を16進小文字で出力し `bundleHash` とする。
5. canonicalization の入力は `ContextQuery` も同一規則（キー辞書順・列挙値正規化・数値表記正規化）を適用し、`queryCanonicalHash` を計算する。
6. 同値性判定は `queryCanonicalHash` と `bundleHash` の両方一致を必須条件とする。

判定式: `sameQuery = canonical(ContextQueryA) == canonical(ContextQueryB)` かつ `sameBundle = bundleHashA == bundleHashB`。
`sameQuery && !sameBundle` は CE-1 Fail として機械判定する。

### 2.4 責務境界（Responsibility）

- Query Preview は「送信前確認」の必須ゲートであり、バイパス経路を契約上禁止する。
- safeMode ON では未レビュー本文を既定除外とし、例外時は監査理由を必須記録する。
- CE-1時点では proposal 適用責務を持たず、生成までを担当する。

## 3) Consequences

- CE-2以降は `sourceBundleHash` をCE-1の `bundleHash` と一致照合する。
- CE-2 / CE-4 実装レーンは CE-1 完了待ちをせず、上記I/Fを前提としたモック実装を先行可能（UI/Backend分離）。
- Query Preview 未実装またはバイパス可能設計は No-Go。
- Verify 失敗の自己修復は3回まで。4回目以降は継続せず停止する。

## 4) 受入条件 / Acceptance criteria

- [ ] ContextQuery/ContextBundleの最小I/FがADR/Issue/Architectureで同一語彙で定義される。
- [ ] `bundleHash` の決定論要件（canonical化対象と順序規則）が記載される。
- [ ] safeMode ON + reviewedOnly の既定除外ルールが明記される。
- [ ] Query Preview必須導線（バイパス禁止）が明記される。
- [ ] 監査ログ必須キー `queryId`, `bundleHash`, `excludedReason` が固定される。
- [ ] CE0/CE1/CE2 の契約語彙（`proposal-only`, `safeMode`, `human_reviewed`, `sourceBundleHash`）が衝突しない。

## 4.1) DoD（Contract-only）

- [ ] Phase 1〜5 それぞれで `Plan -> Execute -> Verify -> Proceed` の記録が残る。
- [ ] Verify の自己修復は 3 回以内で終了し、4 回目は即時停止（推測継続禁止）。
- [ ] `CE1-CTXQ-IF / CE1-CTXB-IF / CE1-HASH-DET-IF / CE1-PREVIEW-GATE-IF` が CE0/CE2 文書と矛盾しない。
- [ ] mock-first 前提（依存待機禁止）が明文化され、実装手順が混入していない。

## 5) タスク分解（文書限定）

- [ ] T1: CE-1 I/F固定表を issue + architecture に同期。
- [ ] T2: deterministic bundle 要件を `02_Architecture` 側へ追記。
- [ ] T3: Query Preview 必須導線を `04_Documentation/operations.md`（CE1運用注記節）へ同期。
- [ ] T4: CE-2連携キー（`sourceBundleHash`）を明示。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "ContextQuery|ContextBundle|bundleHash|Query Preview|reviewFilter|safeModePolicy" 01_Plans/adr 01_Plans/issues 02_Architecture 04_Documentation`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 契約語彙の欠落・重複がなく、validatorが成功する。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: bundleHash定義の差異でCE-2以降の比較不能。
- ロールバック: CE0 Contract ID準拠でI/Fを再固定し、未同期文書をrevert。


## 8) AC/DoD 追加提案（Phase 3）

- Determinism DoD: 同一 canonical query を3回再実行して `bundleHash` が全一致。
- Query Preview DoD: `previewConfirmed=false` のAPI呼び出しは常に `422 preview_required`。
- safeMode除外 DoD: `safeModePolicy=strict` かつ `reviewFilter=reviewedOnly` で `excludedReason` に `unreviewed_filtered` を必須出力。
- Mock分離 DoD: frontend は mock `/context/query` `/context/bundle` で動作し、backend 実装有無で型契約が変化しない。


## 9) Phase 6 Proceed（CE3向け参照専用I/F）

- CE3は `sourceBundleHash === bundleHash` を apply 前提として強制する。
- `previewConfirmed=false` は常に拒否（`422 preview_required`）とする。
- `safeModePolicy=strict` + `reviewFilter=reviewedOnly` の除外理由を監査に残す。

フェイルセーフ（即停止）: SafeMode後退 / auto-apply許容 / 未レビュー昇格許容。

## 10) フェイルセーフ（Stream B 固定）

- Self-Correction が 3 回を超えた場合は停止し、人手判断待ちへ遷移する。
- CE0/CE1/CE2 間で Contract ID 衝突（重複定義/異義定義）を検知した場合は停止する。
- 編集許可スコープ外（実装コード、CE3/CE4 issue、dashboard、issues/README）に触れる必要が生じた場合は停止する。
