# Issue Draft: DATA-MODEL-OPS-02 管理面（マスタデータ）レイヤーの境界固定とサーバー正本化の判断

- Type: Feature request / Design decision
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/research-2026-07-12-master-data-design-review.md`（maintainer 提示「マスタデータ管理UIの前にデータ設計の見直し」）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/backend/`（一覧API・エージェント登録）, `03_Implement/frontend/src/storage/`（recent/プリセットの正本格下げ）, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/schemas.md`, `02_Architecture/api.md`
- Related Backlog: `DATA-MODEL-OPS-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`, `01_Plans/issues/issue-DATA-MODEL-OPS-01-mvp-data-model-overview-and-crud-boundary.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DATA-MODEL-OPS-02
- RequirementStatement: 暗黙のまま分散している管理面データ（文書インデックス・プリセット・エージェント登録）の正本・権限・本文非表示原則を固定し、管理UI設計要求（Claude Design）の前提入力を揃える。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario: 前提=本Issueの D1〜D4 が判断済み / 操作=別端末から同一ユーザーが利用を再開する / 期待結果=自分の文書一覧（メタデータのみ）に到達でき、削除等の高権限操作は境界どおり不在または承認付きで提供される / 除外=payload本文の一覧表示、管理UIの実装そのもの（設計要求は後続）。
- GoNoGoGate（Required / Optional / N/A）: Required（公開範囲・本文非表示原則に接触）
- SecurityGateImpact: SafeMode / public-exposure / share-export
- VerificationLevel: integration
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef: D1の削除/アーカイブ/移管部分は `ADR-0035`。D3 は `ADR-0054` の Accepted 判断への同梱を推奨していたが、**2026-07-12 の受理は用語条件（庭→縁側）のみで D3（エージェント登録の正本・認可）への明示裁定を含まなかった**ため、D3 は本Issueの Open 化判断（または EXT-CONN-02 着手前の確認）に残る。それ以外（一覧API・タイトル編集・複製・D2）も本Issueの Open 化判断で確定できる。

## 背景（リサーチ結論の要約）

文書スナップショット正本（層1、ADR-0033）は意図的設計であり見直さない。問題は周辺の管理面レイヤー: **文書一覧はブラウザ localStorage（別端末から見えない・タイトル未使用・削除/リネーム/複製の導線ゼロ）**、プリセットはデバイスローカル、エージェント登録（ADR-0054 段階2の前提）は未設計。この層を固定せずに管理UIを設計要求すると localStorage 実態を追認する画面になる。詳細は `research-2026-07-12-master-data-design-review.md`。

## 判断項目（D1〜D4）

- **D1 文書インデックスのサーバー正本化**: 本文を含まないメタデータ限定の一覧API（id・タイトル・更新日時）を新設し、localStorage「最近」をキャッシュへ格下げ。タイトル編集・複製は既存 PUT の範囲で提供。削除・アーカイブ・所有者移管は ADR-0035 受理までスコープ外を維持。
- **D2 プリセットの置き場**: (a) デバイスローカル維持＋「この端末のみ」明示 / (b) DocumentV2 埋め込み / (c) サーバー別テーブル。view.json（表示再現）との整合を判断基準に含める。
- **D3 エージェント登録の正本と認可**: `agent_registrations` 相当（表示名・トークンハッシュ・有効/無効・作成者）＋ ingest ログ相関。登録・失効の権限を admin（strict provisioning 型）に置くか文書所有者に置くか。
- **D4 管理面の表示原則**: 管理導線は一般利用者の操作導線から分離。管理面では payload 本文を表示しない（DATA-MAINT-01/04 と同一原則）。

## 非目標

- DocumentV2 スナップショット正本の正規化・分解（ADR-0033 の再起票事項）。
- 語彙（claimType/edge種別/違和感タグ/holdState）のユーザー編集可能マスタ化（ADR-0048 で固定済み）。
- プロバイダ設定のDBマスタ化（環境変数契約を維持、ADR-0050）。
- 削除・アーカイブ・所有者移管・保持期限の実装（ADR-0035 の受理が先）。
- 管理UIの実装（本Issueは前提となるデータ境界の固定まで。UIは Claude Design Round 8 候補として別途要求）。

## 受け入れ条件（案）

- [ ] AC-1: D1〜D4 の判断が記録され、`data_model_operations_overview.md` の ER図・CRUD表・サポートレベル表が同時更新される（§7 更新ルール遵守）。
- [ ] AC-2: 文書一覧APIは本文（payload_json の cards/narratives 等）を一切返さない契約として `api.md` / `schemas.md` に先行固定される。
- [ ] AC-3: localStorage「最近」はサーバー一覧のキャッシュとして再定義され、両者の不一致時はサーバーを正とする。
- [ ] AC-4: プリセットの置き場判断が記録され、「この端末のみ」か「移動可能」かが利用者に見える形で明示される。
- [ ] AC-5: エージェント登録の正本・認可モデルが EXT-CONN-02 の実装前提として固定される（トークンは平文保存しない）。
- [ ] AC-6: 管理UI設計要求（Round 8）の入力パッケージ（確定した正本・権限・本文非表示原則・対象画面一覧）が `ui_design_handoff.md` の受け渡し形式で準備できる状態になる。

## Traceability

- Derived-from: `01_Plans/research-2026-07-12-master-data-design-review.md`
- Related: `02_Architecture/data_model_operations_overview.md`, `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/issues/issue-EXT-CONN-02-webhook-proposal-ingest.md`（D3 の利用先）
