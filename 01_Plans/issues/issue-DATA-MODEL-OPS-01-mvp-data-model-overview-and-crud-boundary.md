# Issue Draft: DATA-MODEL-OPS-01 MVPデータモデル俯瞰とCRUD境界の継続管理

- Type: Documentation quality
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `02_Architecture/data_model_operations_overview.md`, `02_Architecture/schemas.md`, `02_Architecture/api.md`, `AGENTS.md`
- Related Backlog: `DATA-MODEL-OPS-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `02_Architecture/data_model_operations_overview.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DATA-MODEL-OPS-01
- RequirementStatement: MVPで運用サポートするデータ構造、埋め込み限定の構造、派生/契約のみの構造をER図とCRUD表で継続的に識別できるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=開発者または運用者がMVPのデータ構造を確認する / 操作=`data_model_operations_overview.md` を読む / 期待結果=物理テーブル、論理エンティティ、CRUD可否、保守責任が区別できる / 除外=個別CRUD実装、管理画面実装。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## Dependency graph（Stream I）

- Upstream（先行固定）: `ADR-0033`
- Parallel（並行整備）: なし
- Downstream（後続依存）: `DATA-CONTRACT-01`, `DATA-MAINT-01`
- Blocker条件: support level語彙（運用サポート / 埋め込み限定 / 契約のみ）が02文書間で不一致
- Contract fixture方針: `/docs/{doc_id}` の fixture（create-if-absent, DocumentV1/V2 roundtrip）を先に固定し、frontend/backendを追従させる。


## 1) 課題 / Problem statement

- `schemas.md` と `api.md` は、MVP最小契約と将来契約を同じファイル内に含むため、どのデータが通常運用で保守できるかが読み取りにくい。
- Card、Edge、Island、Narrative、ReviewAttributionなどは重要な論理構造だが、MVPでは個別CRUDを持たず、Document全体保存に含まれる。
- ER図やCRUD表がないと、運用者がデータ削除、復旧、棚卸し、監査ログ確認まで実装済みと誤解するリスクがある。

## 2) 背景 / Context

- `ADR-0033` は、MVPデータサポートを「運用サポート」「埋め込み限定」「派生/読み取り中心」「契約のみ/将来拡張」に分ける。
- `02_Architecture/data_model_operations_overview.md` は、物理ER、論理ER、CRUD表、ステークホルダー別運用境界を示す入口として追加された。
- 今後、DocumentV2、review attribution、AI連携、監査連携の実装が進むと、この表の同期が崩れやすい。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 利用者が考え途中の状態を安全に扱うには、運用側も保存範囲と保守範囲を誤解しない必要がある。
- 安全（THREAT_MODEL / SafeMode）: 共有・監査・未レビュー情報を含むデータ境界の誤読は、公開範囲の誤設定につながる。
- 企業・行政要件（enterprise_architecture）: 導入組織は、棚卸し、保管、削除、復旧、監査責任を事前に把握する必要がある。
- 後方互換（schemas）: 型追加時にCRUD表を更新することで、既存スナップショット保存方針との互換性を判断しやすくなる。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - `02_Architecture/data_model_operations_overview.md` のER図、CRUD表、ステークホルダー表。
  - `schemas.md` / `api.md` / `AGENTS.md` からの参照導線。
- 変更の最小単位:
  - 新しい永続テーブル、Document内論理エンティティ、標準APIが追加された時点で、本Issueの観点に沿ってCRUD表を更新する。
- 非目標:
  - 個別エンティティCRUDの即時実装。
  - 管理画面や削除/保管期限機能の実装。

## 5) 受入条件 / Acceptance criteria

- [x] 物理テーブルと論理データ構造が別物として説明されている。
- [x] 各データ領域について Create / Read / Update / Delete の可否が明示されている。
- [x] MVPで個別CRUDを持たない構造が、標準運用で保守可能だと読めない表現になっている。
- [x] ステークホルダー別に、標準操作でできることと不足が記載されている。
- [x] 新しい主要データ構造が追加された場合、`AGENTS.md` と関連02文書の導線が同期されている。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 MVPデータサポート境界をADR化する。
- [x] T2 物理ER、論理ER、CRUD表を含む俯瞰文書を追加する。
- [ ] T3 今後のDocumentV2/AI/監査連携の追加時に、CRUD表の同期を変更チェック項目へ組み込む。
- [ ] T4 公開文書へ転記する場合は、内部管理情報を除いた利用者向け表現に整える。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check -- 01_Plans 02_Architecture AGENTS.md`
  - `rg -n "DATA-MODEL-OPS-01|data_model_operations_overview|ADR-0033" 01_Plans 02_Architecture AGENTS.md`
- 期待結果:
  - ADR、issue、02文書、Project Mapの参照が相互に追跡できる。
- 未実施時の理由・代替検証:
  - なし。

## 8) 代替案 / Alternatives considered

- 代替案A: `schemas.md` にER/CRUD表をすべて追記する。既存ファイルがさらに長くなり、現行契約と履歴ログの読み分けが難しくなるため採用しない。
- 代替案B: 実DBテーブルだけをER図にする。Document内の論理構造と運用制約が見えなくなるため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 俯瞰表が更新されず、実装とのドリフトが再発する。
- 影響範囲: 02設計文書、API契約、公開文書、運用説明。
- ロールバック手順: 新設文書を参照から外し、`schemas.md` / `api.md` の該当節へ最小注記を戻す。

## 10) Additional context

- ADR化が必要になる条件: 新しいデータライフサイクル、削除方針、監査保持方針、所有者移管方針を固定する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。

## 11) 運用境界（含む / 含まない）

- 含む:
  - `data_model_operations_overview.md` のER/CRUD/ステークホルダー境界の継続更新。
  - `schemas.md` との用語同期（support level名称を含む）。
  - Stream G成果としての境界表メンテナンス。
- 含まない:
  - backend/frontendの機能実装。
  - public向け文書の全面改稿。

## 12) 受入条件の補完（AC gap fill）

- [x] AC-01: CRUD表の各行に `運用責務主体` が必須列として存在する。
- [x] AC-02: 各四半期で1回以上のドリフト点検（issue checklist）を定義する。
- [x] AC-03: 例外時フローへのリンク（DATA-MAINT-01）を明示する。

## Stream I Phase status

- Phase 1 Read: 完了（Read Order上流と関連ADRを確認済み）
- Phase 2 ADR/論点分離: 完了（契約ドリフト、運用保守、俯瞰境界を独立Issue化）
- Phase 3 Plan: 完了（受入条件・非目標・検証計画を明文化）
- Phase 4 Execute: 完了（Draft本文・依存関係・AC gapを更新）
- Phase 5 Verify: 完了（`git diff --check` と `rg` による整合確認を実施）
- Phase 6 Proceed/Stop: Proceed（DB実装変更なし。Issue計画整備のみ継続可能）


## 13) Stream D AC/DoD補完

- [x] AC-04: CRUD表の全行に support level（L1/L1.5/L2/L2.5/L3/L0）が明示され、`schemas.md` の定義と同一語彙である。
- [x] AC-05: 互換性判定の責務が「契約更新（Architecture）→実装追従（Implement）」の順序で記述されている。
- [x] DoD-01: 新規フィールド追加時に、`schemas.md` と `data_model_operations_overview.md` を同一コミットで更新する運用規則が明記されている。
- [x] DoD-02: 「型がある=運用可能」誤読を防ぐ注意書きが維持されている。
- 判定: **Proceed**（MVP運用境界の固定化は完了、実装依存は契約凍結で切断）。
