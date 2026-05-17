# ADR-0033: MVPデータサポート境界と保守方針

- Status: Proposed
- Date: 2026-05-15
- Deciders: Project Maintainers
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/backend/`, `03_Implement/frontend/`

## Context

kj-atlas の設計文書には、MVPで実際に利用する最小スキーマと、AI連携・レビュー帰属・監査連携・将来拡張の契約が同じ `02_Architecture` 層に存在している。

一方、現行MVPの永続化は、ドキュメント全体をJSONスナップショットとして保存し、補助的にユーザー/ID対応表とマージ判断ログを持つ構成である。Card、Edge、Island、Narrative、ReviewAttribution などは論理データとして重要だが、多くは `Document` 内の埋め込み構造であり、個別CRUDや管理画面を持たない。

この境界が曖昧なままだと、次の問題が起きる。

1. スキーマに存在する型を、標準運用で保守できるデータと誤解しやすい。
2. 利用者、レビュアー、運用者、セキュリティ担当者の責任範囲が読み取りにくい。
3. データ削除、棚卸し、復旧、所有者移管など、組織運用に必要な作業がMVP内で保証済みに見えてしまう。
4. DocumentV2やAPIの契約差分を、実装修正なしに文書だけで吸収しやすくなる。

## Decision

MVPでは、データサポート境界を次の4区分で管理する。

| 区分 | 意味 | 代表例 |
| --- | --- | --- |
| 運用サポート | 標準API/UIで通常運用できる | `Document` スナップショット、admin provisioning、merge decision log append/read |
| 埋め込み限定 | `Document` 内には保存されるが、個別CRUDは持たない | Card、Edge、Island、Narrative、ReviewAttribution |
| 派生/読み取り中心 | 保存済みデータやリクエストから生成され、保守対象ではない | SimilarCandidateGroup、ContextBundle、audit event |
| 契約のみ/将来拡張 | 型やI/Fは固定するが、MVPでは完全保守しない | CE契約、差分同期、証跡・根拠リンクの完全管理 |

`02_Architecture/data_model_operations_overview.md` を、MVPデータモデル、論理ER、CRUDサポート表、ステークホルダー別運用境界の俯瞰文書として追加する。この文書は `schemas.md` や `api.md` の詳細を置き換えず、「実際に運用できる範囲」を読むための入口とする。

採用理由は、MVPのスナップショット保存方針を維持しつつ、製品化に必要なデータ運用課題を隠さず分離できるためである。現段階で全エンティティを正規化し、個別CRUDを実装すると、UI、API、移行、監査の範囲が一気に広がり、MVPで確認したい価値よりも管理機構が先行する。

非目標:

- このADRだけで新しい永続テーブルや管理画面を追加しない。
- Card/Edge/Islandなどの個別CRUDをMVP必須にしない。
- 監査ログ閲覧、削除/保管期限、所有者移管、復旧手順を完了扱いにしない。
- 契約ドリフトを文書上の言い換えだけで解決しない。実装/API/型の不一致は内部issueで扱う。

## Consequences

- 期待される効果:
  - 初見の開発者や運用者が、MVPで保守できるデータと将来契約を区別しやすくなる。
  - ステークホルダー別に、標準操作でできることと未整備の運用課題を説明できる。
  - 製品化に必要な管理機能、復旧手順、契約同期を個別issueとして進めやすくなる。
- 想定される副作用/制約:
  - `Document` スナップショット内の構造が増えるほど、全体置換保存の競合・検証・復旧が難しくなる。
  - 個別CRUDがないため、管理者やサポートが部分修復したい場面では標準手段が不足する。
  - API文書、frontend型、backend型、実装ルートの同期を継続的に確認する必要がある。
- 移行時に必要な対応:
  - `DATA-MAINT-01` で、一覧、アーカイブ/削除、バックアップ、復旧、データ検証、ユーザー棚卸しを設計する。
  - `DATA-CONTRACT-01` で、DocumentV2とAPIの正本差分を棚卸しし、必要な実装・テストを分割する。
  - 新しい永続テーブルまたは標準CRUDを追加する場合は、本ADRの区分と `data_model_operations_overview.md` のCRUD表を更新する。

## Traceability

- Related: `02_Architecture/data_model_operations_overview.md`
- Related: `02_Architecture/schemas.md`
- Related: `02_Architecture/api.md`
- Related: `02_Architecture/enterprise_architecture.md`
- Related: `01_Plans/adr/ADR-0032-product-value-realization-model.md`
- Related: `01_Plans/issues/issue-DATA-MODEL-OPS-01-mvp-data-model-overview-and-crud-boundary.md`
- Related: `01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`
- Related: `01_Plans/issues/issue-DATA-CONTRACT-01-document-v2-contract-drift-and-support-levels.md`

---

## Authoring Checklist（人間/生成AI 共通）

- [x] 必須ヘッダ（Status/Date/Deciders/Scope）を記載した。
- [x] 必須章（Context/Decision/Consequences/Traceability）を記載した。
- [x] Decision に採用理由と非目標がある。
- [x] Traceability に関連文書を1件以上記載した。
- [x] 実装進捗は ADR ではなく Issue で管理する前提を維持した。
