# Issue Draft: DATA-CONTRACT-01 DocumentV2契約ドリフトとサポートレベル同期

- Type: Process
- Status: Draft
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
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0033`

## 1) 課題 / Problem statement

- `DocumentV2` はfrontend/backend/API/設計文書の複数箇所に表現されており、フィールド追加や検証条件の同期漏れが起きやすい。
- `api.md` では `PUT /docs/{doc_id}` をMVPのCreate契約に寄せ、`POST /docs` を将来候補として残しているが、実装・テスト・関連文書の同期確認が必要である。
- frontend型には `evidenceLinks` など、backend型やMVP運用表での扱いを確認すべき構造がある。
- `PatchApplyStats` などの補助型は、どこまでがMVP運用サポートで、どこからが将来契約かを明示する必要がある。

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

- [ ] DocumentV1/V2のフィールド差分表がfrontend/backend/API/設計文書を横断して作成されている。
- [ ] `PUT /docs/{doc_id}` がMVPのCreate契約であること、`POST /docs` が未実装時は将来候補であることが、文書・実装・テストで一致している。
- [ ] `evidenceLinks`、PatchApplyStats、ReviewAttribution、DeterministicTieBreakなどのサポートレベルが明示されている。
- [ ] SafeMode/share/exportに影響するフィールドは、漏れなくテスト観点に含まれている。
- [ ] 契約のみのフィールドは、MVPで標準運用保守可能だと読めない表現になっている。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 frontend/backend/API/設計文書のDocumentV2フィールド一覧を抽出する。
- [ ] T2 差分をサポートレベル別に分類し、削除/保留/実装同期の判断を記録する。
- [ ] T3 `PUT create-if-absent` をMVP Create契約として固定し、`POST /docs` の昇格要否を判定する。
- [ ] T4 型・バリデーション・APIテストを同期する。
- [ ] T5 `data_model_operations_overview.md` と `schemas.md` のサポート記述を更新する。

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
