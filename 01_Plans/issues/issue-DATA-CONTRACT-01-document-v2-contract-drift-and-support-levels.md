# Issue Draft: DATA-CONTRACT-01 DocumentV2契約ドリフトとサポートレベル同期

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `02_Architecture/schemas.md`, `02_Architecture/api.md`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/frontend/src/domain/types.ts`
- Related Backlog: `DATA-CONTRACT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/schemas.md`, `02_Architecture/api.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DATA-CONTRACT-01
- RequirementStatement: DocumentV2、API文書、frontend型、backend型、実装ルートの差分を棚卸しし、MVP運用サポート範囲と将来契約を一貫して説明・検証できるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=開発者がDocumentV2またはAPIを変更する / 操作=正本文書とfrontend/backend型を照合する / 期待結果=実装済み、埋め込み限定、契約のみの差分が明示され、必要なテストが分かる / 除外=全構造の個別CRUD実装。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: `ADR-0033`

## Dependency graph（Stream I）

- Upstream（先行固定）: `DATA-MODEL-OPS-01`（support level語彙・CRUD境界・参照導線）
- Parallel（並行整備）: なし
- Downstream（後続依存）: `DATA-MAINT-01`（復旧runbookで参照する契約整合チェック）
- Blocker条件: `PUT /docs/{doc_id}` create-if-absent契約の表現が `schemas.md` / `api.md` / 実装で不一致のまま


## 1) 課題 / Problem statement

- `DocumentV2` はfrontend/backend/API/設計文書の複数箇所に表現されており、フィールド追加や検証条件の同期漏れが起きやすい。
- `api.md` では `PUT /docs/{doc_id}` をMVPのCreate契約に寄せ、`POST /docs` を将来候補として残しているが、実装・テスト・関連文書の同期確認が必要である。
- frontend型には `evidenceLinks`、`claimType`、edge endpoint kind など、backend型やMVP運用表での扱いを確認すべき構造がある。
- `PatchApplyStats` などの補助型は、どこまでがMVP運用サポートで、どこからが将来契約かを明示する必要がある。
- A1契約フィールド（`critiqueInputs` / `reproposalDiffs` / `reviewAttribution` / `deterministicTieBreak`）は、UI個別編集の対象ではないが、DocumentV2内で保存・読み込み・API往復する契約境界としてfrontend/backend双方の型と検証を同期する必要がある。

## 2) 背景 / Context

- `ADR-0033` は、型が存在することと運用保守できることを分ける方針を採用した。
- `data_model_operations_overview.md` はCRUD境界を示すが、型定義のドリフト検出そのものは別Issueで扱う必要がある。
- SafeMode、share/export、review attribution は、型ドリフトが安全性ドリフトになりやすい領域である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 人間レビューと可逆性を守るには、review/evidence/patch関連型が同じ意味で扱われる必要がある。
- 安全（THREAT_MODEL / SafeMode）: 未レビュー情報や根拠リンクの扱いがfrontend/backendでずれると、共有時の抑制が壊れる。
- 企業・行政要件（enterprise_architecture）: review attributionとidentity正規化は監査・説明責任に直結する。
- 後方互換（schemas）: DocumentV1/V2の読み書き互換を壊さず、サポートレベルを明確化する必要がある。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - `schemas.md` / `api.md` のDocumentV2とCRUD記述。
  - frontend `src/domain/types.ts` とbackend `models.py` の型差分。
  - backend `routes/docs.py` のCreate/Update実装契約。
- 変更の最小単位:
  - フィールド一覧を「実装済み」「Document埋め込み限定」「契約のみ」「削除/保留候補」に分類する。
  - MVP正本を `PUT create-if-absent` に寄せたうえで、`POST /docs` を将来候補に留めるか、標準契約へ昇格するかを判断し、文書・実装・テストを同期する。
- 非目標:
  - 全フィールドの画面編集機能を一度に作ること。
  - 個別CRUD APIをMVP必須にすること。
  - AI提案の自動適用を許可すること。

## 5) 受入条件 / Acceptance criteria

- [x] DocumentV1/V2のフィールド差分表がfrontend/backend/API/設計文書を横断して作成されている。
- [x] `PUT /docs/{doc_id}` がMVPのCreate契約であること、`POST /docs` が未実装時は将来候補であることが、文書・実装・テストで一致している。
- [x] `evidenceLinks`、PatchApplyStats、ReviewAttribution、DeterministicTieBreakなどのサポートレベルが明示されている。
- [x] SafeMode/share/exportに影響するフィールドは、漏れなくテスト観点に含まれている。
- [x] 契約のみのフィールドは、MVPで標準運用保守可能だと読めない表現になっている。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 frontend/backend/API/設計文書のDocumentV2フィールド一覧を抽出する。
- [x] T2 差分をサポートレベル別に分類し、削除/保留/実装同期の判断を記録する。
- [x] T3 `PUT create-if-absent` をMVP Create契約として固定し、`POST /docs` の昇格要否を判定する。
- [x] T4 型・バリデーション・APIテストを同期する。
- [x] T5 `data_model_operations_overview.md` と `schemas.md` のサポート記述を更新する。

進捗メモ:

- `claimType`、edge endpoint kind、`evidenceLinks`、`patchApplyLog.stats.upsertEvidenceLinks/deleteEvidenceLinks` はbackend保存モデルとroundtrip testを同期済み。
- `critiqueInputs` / `reproposalDiffs` / `reviewAttribution` / `deterministicTieBreak` はfrontend正本型、strict validator、import正規化、backend保存モデル、backend roundtrip testを同期済み。
- MVPでは上記A1契約フィールドの個別CRUD/UI編集を標準保守対象にしない。DocumentV2スナップショット内の契約のみ/限定保存として扱い、share/export/SafeModeの観点は継続確認する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "DocumentV2|evidenceLinks|PatchApplyStats|reviewAttribution|deterministicTieBreak|POST /docs|PUT /docs" 02_Architecture 03_Implement`
  - `cd 03_Implement/backend && python -m pytest`
  - `cd 03_Implement/frontend && npm test -- --run`
  - `git diff --check -- 02_Architecture 03_Implement`
- 期待結果:
  - 文書、型、実装、テストが同じCreate契約とDocumentV2サポートレベルを示す。
- 未実施時の理由・代替検証:
  - 実装同期前は差分表とdocs-checkで代替し、テスト未実施理由をPRに残す。

## 8) 代替案 / Alternatives considered

- 代替案A: frontend/backendの型差分を許容し続ける。共有・レビュー・監査の安全境界に影響するため採用しない。
- 代替案B: 全フィールドを即時実装済みにする。MVP範囲を超え、管理・移行・UIが肥大化するため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 型同期の過程で既存DocumentV1/V2の読み込み互換を壊す。
- 影響範囲: backend validation、frontend import/export、share/review pack、E2E。
- ロールバック手順: 新規フィールドの必須化を戻し、既存DocumentV1/V2をoptional扱いに戻す。

## 10) Additional context

- ADR化が必要になる条件: Create契約を変更して外部互換に影響する場合、またはDocumentV2を正規化テーブルへ移行する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。

## 11) 運用境界（含む / 含まない）

- 含む:
  - DocumentV2契約の差分棚卸し（frontend/backend/api/schema）。
  - Support levelの明示（運用サポート / 埋め込み限定 / 契約のみ）。
  - `PUT /docs/{doc_id}` create-if-absent契約の検証観点固定。
- 含まない:
  - 個別エンティティCRUD実装。
  - 管理者向け復旧UIの実装。
  - HIL/CEワークフロー仕様の新規拡張。

## 12) 受入条件の補完（AC gap fill）

- [x] AC-01: 差分棚卸し表に「差分の理由」と「同期先責務（frontend/backend/api/docs）」が必須列としてある。
- [x] AC-02: SafeMode/share-export影響フィールドは、`support level` と `test level` の両軸で分類される。
- [x] AC-03: 未解決項目には `DecisionQueueRef` と期限（yyyy-mm-dd）を付与する。

## Stream I Phase status

- Phase 1 Read: 完了（Read Order上流と関連ADRを確認済み）
- Phase 2 ADR/論点分離: 完了（契約ドリフト、運用保守、俯瞰境界を独立Issue化）
- Phase 3 Plan: 完了（受入条件・非目標・検証計画を明文化）
- Phase 4 Execute: 完了（Draft本文・依存関係・AC gapを更新）
- Phase 5 Verify: 完了（`git diff --check` と `rg` による整合確認を実施）
- Phase 6 Proceed/Stop: Proceed（DB実装変更なし。Issue計画整備のみ継続可能）
