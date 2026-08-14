# ADR-0076: 共同編集（第3反復）の並行性モデルをサーバ権威LWW＋既存CASに定める

- Status: Proposed
- Date: 2026-08-15
- Deciders: Maintainer（未採択。採択は保守者の明示判断）
- Scope: 第3反復（共同編集）の並行性モデル。`03_Implement/backend`（楽観的並行制御・revision）と将来の共同編集実装
- Related: `02_Architecture/collaboration-concurrency-comparison-2026-08-14.html`（外部比較調査）, `01_Plans/issues/issue-PGM-ITER-03-01-collaboration-concurrency-external-comparison.md`, `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`, `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`

## Context

`02_Architecture/post-mvp-business-scope-design-program.html` は3拡張軸（主体の複数化 → 成果物の複数化 → 境界の外部化）を定め、**第3反復（共同編集の並行性モデル選定）は外部比較なしに判断すべきでない**と明記した。外部比較調査（`collaboration-concurrency-comparison-2026-08-14.html`、deep-research 105エージェント・3票反証検証）が完了し、判断材料が揃った。

### 外部比較の検証済み事実（要約）

| 製品 | 並行性モデル | コンフリクトUX |
|---|---|---|
| Figma | **サーバ権威・property-level LWW**（CRDT/OTではない・OTを明示的に却下）・分数インデックス | 利用者に見えるマージUIなし |
| Confluence | 保存時LWW＋手動 Overwrite/Merge/Discard | 手動ダイアログ・履歴破損障害（CONFSERVER-32286） |
| Miro | （基盤は未確認）・単一owner・5段階ロール | — |
| Notion/Slack/Jira | 一次ソース未確認 | — |

OT vs CRDT 論争（Sun et al. はOTキャンプのadvocacy・COI）は peer-review 済みだが advocacy 色が強く、Automerge（クライアント側merge・順序非依存）は P2P/E2EE に適合。

### kj-atlas の現状との整合

kj-atlas は**サーバ権威・単一正本**のWebアプリである（backendがDocumentV1を保存・`ETag`/`If-Match` CAS で楽観的並行制御を既に実装。inquiry bundle も `revision` CAS で同型）。SafeMode の未レビュー非表示境界・tenant 境界 guard はサーバ側に集中している。

## 決定すべき論点（D1〜D3）

### D1: 並行性モデル

- **A（推奨）: サーバ権威 LWW ＋ 既存CAS拡張**。コンフリクトはサーバ側の revision で解決し、stale write は 409 で拒否（既存の document/inquiry CAS を共同編集へ拡張）。Figma 式で、クライアント CRDT の複雑性を導入しない。
- **B: クライアント側CRDT（Automerge/Yjs）**。オフライン・P2P・E2EE が必要な場合のみ。SafeMode 境界・単一正本前提と整合させる追加設計が要る。
- **C: 保存時手動merge（Confluence式）**。実装は最小だが、履歴破損リスクとKJ法の同時配置作業に合わない。

### D2: 同時編集の表現

- A を採る場合、カーソル/プレゼンス表示と、編集中の他クライアントへの変更伝播（WebSocket等）を導入するか、保存時同期に留めるか。
- 最初は**保存時同期**（既存の ETag/CAS）で十分であり、リアルタイムプレゼンスは同時利用の実測後に判断する。

### D3: ボード所有とロール

- Miro の単一owner・譲渡可・5段階ロールは、第2反復（documents所有・ADR-0073 D1=C）の帰結と整合する（文書はテナント所有・作成者は不変事実・管理権はcapability）。第3反復では**新しい所有概念を導入せず**、既存のテナント所有＋capabilityを維持する。

## 三要素牽制

| 次元 | 必要な判断 | 他次元への制約 |
|------|------------|---------------|
| **業務設計** | 複数利用者が同じ文書/探究を編集するjourney。コンフリクト時に旧操作を黙って捨てない（DATA-INQUIRY-CONCURRENCY-01 の受入と同型） | SafeMode・未レビュー非表示・tenant境界を共同編集で緩和しない |
| **データ設計** | 並行編集の合流点は server-owned revision（既存）を正本とし、クライアント側CRDT状態を永続正本にしない | payload内部の整合性をクライアントのmerge結果に委ねない |
| **機能設計** | 共同編集のAPI契約は既存の ETag/If-Match CAS を拡張し、新規並行制御を導入しない | 別クライアントの更新後に stale write を 409 で拒否する（既存契約） |

## 決定（未採択）

D1=A（サーバ権威LWW＋既存CAS拡張）を**推奨**する。理由:
1. kj-atlas は既にサーバ権威・単一正本であり、Figma と同型の構成。
2. 既存の ETag/If-Match CAS（document・inquiry bundle）を共同編集へ拡張するだけで、新規並行制御機構を導入しない。
3. SafeMode・tenant境界・未レビュー非表示はサーバ側に集中しており、クライアントCRDTを導入するとこの集中を崩す。
4. Confluence式の保存時手動merge（C）は履歴破損リスクがあり不採用。

**採択は保守者の明示判断を要する**（第3反復は 第2反復 の後に来るため、着工は第2反復の機能次元完了後が適切）。

## 採択後の実装範囲（本ADRが採択された場合）

- 第3反復: 既存 CAS を共同編集へ拡張（同時編集時の revision 管理・409 拒否）。保存時同期から開始し、リアルタイムプレゼンスは実測後に判断。
- 非目標: クライアントCRDTの導入・P2P/E2EE（要件が出た場合に別ADRで再検討）。
