# Issue Draft: DATA-MODEL-OPS-02 管理面（マスタデータ）レイヤーの境界固定とサーバー正本化の判断

- Type: Feature request / Design decision
- Status: Open
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
- DecisionStatus（Fixed / Pending）: Fixed（D1〜D4を2026-07-13にmaintainer代理裁可）
- DecisionQueueRef: Resolved（`ADR-0035` Accepted、D1〜D4は下記判断で固定）

## Draft→Open 2026-07-13: D1〜D4 代理裁可

- **D1 文書インデックス**: 採用。本文を含まない `GET /docs` をサーバー正本とし、返却項目は `id/title/updatedAt` のallowlistに限定する。対象集合は「現認可主体がread可能な文書」であり、認証構成でowner/ACL解決ができない場合はfail-closedとする。localStorageの「最近」は非正本キャッシュへ格下げする。タイトル変更は既存PUTの範囲で許可する。複製はcreatedAt・review/history・所有権のコピー規約が未定義のため本スライスでは保留する。削除・アーカイブ・所有者移管は `ADR-0035` のとおり解禁しない。
- **D2 プリセット**: 一括の置き場を作らず種類を分離する。表示再現に属するView/Perspective状態は既存 `view.json.viewState` を正本とし、DocumentV2へ埋め込まない。Patch workspaceのQueryPresetは当面device-localを維持し、UIで「この端末のみ」と明示する。利用実績なしにユーザー従属テーブルを新設しない。
- **D3 エージェント登録**: 採用。`agent_registrations` 相当をサーバー正本とし、登録・失効はadminのstrict provisioning型操作に限定する。平文tokenは保存せず、作成時に一度だけ表示してhash照合する。登録は文書単位に束縛し、登録自体を文書書込権限とみなさず、ingestごとに既存access-controlで別途許可判定する。文書ownerによるtoken発行は不採用とする。
- **D4 表示原則**: 採用。通常利用者のWorkspace文書一覧とAdmin/Audit管理面を分離する。Workspace一覧は認可済み文書のタイトルを表示できるが、Admin/Audit面は `id/version/updatedAt` 等の固定allowlistだけを扱い、タイトル、`payload_json`、カード、narrative、review pack、diff、未レビュー本文を表示・検索しない。

このOpen化は実装完了を意味しない。次の作業は `schemas.md` / `data_model_operations_overview.md` / `api.md` の契約先行同期であり、それが完了するまで一覧API・登録API・管理UIを実装しない。

## 背景（リサーチ結論の要約）

文書スナップショット正本（層1、ADR-0033）は意図的設計であり見直さない。問題は周辺の管理面レイヤー: **文書一覧はブラウザ localStorage（別端末から見えない・タイトル未使用・削除/リネーム/複製の導線ゼロ）**、プリセットはデバイスローカル、エージェント登録（ADR-0054 段階2の前提）は未設計。この層を固定せずに管理UIを設計要求すると localStorage 実態を追認する画面になる。詳細は `research-2026-07-12-master-data-design-review.md`。

## 判断項目（D1〜D4）

- D1〜D4 の確定値は上記「Draft→Open 2026-07-13」を正本とする。本節の選択肢比較は解決済みであり、実装側で再選択しない。

## 非目標

- DocumentV2 スナップショット正本の正規化・分解（ADR-0033 の再起票事項）。
- 語彙（claimType/edge種別/違和感タグ/holdState）のユーザー編集可能マスタ化（ADR-0048 で固定済み）。
- プロバイダ設定のDBマスタ化（環境変数契約を維持、ADR-0050）。
- 削除・アーカイブ・所有者移管・保持期限の実装（`ADR-0035` Acceptedにより標準機能外と確定）。
- 管理UIの実装（本Issueは前提となるデータ境界の固定まで。UIは Claude Design Round 8 候補として別途要求）。

## 受け入れ条件（案）

- [ ] AC-1: D1〜D4 の判断が記録され、`data_model_operations_overview.md` の ER図・CRUD表・サポートレベル表が同時更新される（§7 更新ルール遵守）。
- [ ] AC-2: 文書一覧APIは本文（payload_json の cards/narratives 等）を一切返さない契約として `api.md` / `schemas.md` に先行固定される。
- [ ] AC-3: localStorage「最近」はサーバー一覧のキャッシュとして再定義され、両者の不一致時はサーバーを正とする。
- [ ] AC-4: View/PerspectiveとQueryPresetの置き場判断が契約へ反映され、device-local QueryPresetには「この端末のみ」が利用者に見える形で明示される。
- [ ] AC-5: エージェント登録の正本・認可モデルが EXT-CONN-02 の実装前提として固定される（トークンは平文保存しない）。
- [ ] AC-6: 管理UI設計要求（Round 8）の入力パッケージ（確定した正本・権限・本文非表示原則・対象画面一覧）が `ui_design_handoff.md` の受け渡し形式で準備できる状態になる。

## Traceability

- Derived-from: `01_Plans/research-2026-07-12-master-data-design-review.md`
- Related: `02_Architecture/data_model_operations_overview.md`, `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/issues/issue-EXT-CONN-02-webhook-proposal-ingest.md`（D3 の利用先）
