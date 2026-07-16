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

- [x] AC-1: D1〜D4 の判断が記録され、`data_model_operations_overview.md` の ER図・CRUD表・サポートレベル表が同時更新される（§7 更新ルール遵守）。
- [x] AC-2: 文書一覧APIは本文（payload_json の cards/narratives 等）を一切返さない契約として `api.md` / `schemas.md` に先行固定される。→ `api.md` §2.4・`schemas.md` §3.4.1 として固定済み（2026-07-16、下記「実装記録」参照）。
- [ ] AC-3: localStorage「最近」はサーバー一覧のキャッシュとして再定義され、両者の不一致時はサーバーを正とする。
- [ ] AC-4: View/PerspectiveとQueryPresetの置き場判断が契約へ反映され、device-local QueryPresetには「この端末のみ」が利用者に見える形で明示される。
- [x] AC-5: エージェント登録の正本・認可モデルが EXT-CONN-02 の実装前提として固定される（トークンは平文保存しない）。→ `api.md` §9.5 として固定済み（2026-07-16、下記「実装記録」参照）。
- [ ] AC-6: 管理UI設計要求（Round 8）の入力パッケージ（確定した正本・権限・本文非表示原則・対象画面一覧）が `ui_design_handoff.md` の受け渡し形式で準備できる状態になる。

### AC-1 実装証跡（2026-07-16）

- `data_model_operations_overview.md` §2（物理ER図）: D1〜D3がいずれも新規物理テーブルを追加しない決定であることを説明する段落を追加した（文書一覧=既存`documents`の射影、View/Perspective・QueryPreset=既存`view.json`とdevice-local維持、エージェント登録=`EXT-CONN-02`実装まで契約先行でER図に含めない）。
- §4（CRUDサポート表）: 「文書一覧（Document index projection）」（L1）、「View/Perspective状態」（L2）、「QueryPreset（Patch workspace）」（L3）、「エージェント登録（`agent_registrations`）」（L0）の4行を新規追加し、D1〜D3の確定値をそれぞれのSupport level・CRUD手段・MVP保守責任・備考として記録した。
- §5（ステークホルダー別の運用境界）: 新規「5.2 Workspace / Admin・Audit の表示分離（DATA-MODEL-OPS-02 D4）」を追加し、Workspace文書一覧とAdmin/Audit管理面（`id`/`version`/`updatedAt`固定allowlistのみ、タイトル・本文・カード・narrative・review pack・diff非表示）の分離原則を記録した。
- §6（運用設計の不足と起票先）: `DATA-MODEL-OPS-02`自体の継続追跡行を追加した。
- 本PRはAC-1（ドキュメント記録）のみを対象とする。AC-2（api.md/schemas.md契約）、AC-3（localStorageキャッシュ再定義の実装）、AC-4（QueryPreset UI表示の実装）、AC-5（agent_registrations実装、`EXT-CONN-02`の対象）、AC-6（`ui_design_handoff.md`作成、Claude Design Round 8の入力）はいずれも実装または別文書の新規作成を伴う別スコープであり、本PRには含まない。

検証結果:
- `check_current_history_headings` / `check_relative_links` / `check_document_contract_baseline` を現行repositoryへ直接実行: いずれも0 findings。
- `python 01_Plans/issues/validate_active_issue_memos.py`: pass（25 active issue memos）。
- 本変更はMarkdownのみであり、frontend/backendのコード変更はない。

### AC-2 実装記録（2026-07-16）: 文書一覧APIの本文非返却契約を先行固定

- `api.md` §2.4「List」を、単なる「任意・後回し可」の記述から契約先行固定の節に更新した。Responseを`DocumentListItemV1[]`（新規、`schemas.md` §3.4.1）として明示し、`id`/`title`/`updatedAt`のallowlist以外（`cards`/`edges`/`islands`/`narratives`/`evidenceLinks`等）を一覧項目に含めないことを明記した。対象集合は「現認可主体がread可能な文書」に限定し、owner/ACL解決不能時はfail-closed（全文書露出へのフォールバック禁止）とする方針も明記した。
- `schemas.md` §3.4.1として`DocumentListItemV1`型を新規追加した。`DocumentV1`の部分集合ではなく独立した最小射影型とし、本文・構造フィールドは空配列であっても含めないことをコメントで明記した。この型は一覧表示専用の射影であり、`DocumentV1`への書き戻し・保存契約には関与しない。
- `data_model_operations_overview.md`のCRUD表（§4、AC-1で記録済み）は既に同じ契約（`id`/`title`/`updatedAt`のallowlist、fail-closed方針）を記述していたため、今回の契約固定と整合していることを確認した（変更なし）。
- 本スライスはMarkdownのみであり、frontend/backendのコード変更・API実装は行っていない（実装着手はAC-2の範囲外、既存の契約先行固定の方針どおり）。

検証結果:
- `python 01_Plans/docs_check.py`: pass。
- `python 01_Plans/issues/validate_active_issue_memos.py`: pass（25 active issue memos）。

### AC-5 実装記録（2026-07-16）: エージェント登録の正本・認可モデルを先行固定

- `api.md` §9.5として新規節「エージェント登録 API（契約先行固定、`DATA-MODEL-OPS-02` D3/AC-5）」を追加した。§9.3の事前プロビジョニングAPI（strict provisioning）と同じ型を踏襲し、`POST /admin/agent-registrations`（作成、token平文はこの応答でのみ返る）・`GET /admin/agent-registrations`（一覧、`token`/`tokenHash`非含有）・`DELETE /admin/agent-registrations/{id}`（失効）の3エンドポイントと`AdminCreateAgentRegistrationRequest`/`AdminCreateAgentRegistrationResponse`/`AdminAgentRegistrationSummary`型を定義した。
- D3確定事項を契約へ反映: 登録・失効はadmin限定（文書ownerによるtoken発行は不採用）、平文tokenは作成時に一度だけ表示し以後はhashのみで照合、登録は文書単位（`docId`）に束縛し登録自体を文書書込権限とみなさない（ingestごとに既存access-controlで別途許可判定）。
- `data_model_operations_overview.md`のCRUD表（§4、行167）を更新し、Create/Read/Delete列に上記3エンドポイントを反映、備考に`api.md` §9.5への参照を追加した。ER図（§2、既存記述）はEXT-CONN-02実装まで本テーブルを含めない方針を維持しており変更不要だった。
- 本スライスはMarkdownのみであり、frontend/backendのコード変更・エンドポイント実装は行っていない（実装はEXT-CONN-02のスコープ、本ACは契約先行固定のみ）。

検証結果:
- `python 01_Plans/docs_check.py`: pass。
- `python 01_Plans/issues/validate_active_issue_memos.py`: pass（25 active issue memos）。

## Traceability

- Derived-from: `01_Plans/research-2026-07-12-master-data-design-review.md`
- Related: `02_Architecture/data_model_operations_overview.md`, `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/adr/ADR-0054-external-connection-layer-staged-introduction.md`
- Related: `01_Plans/issues/issue-EXT-CONN-02-webhook-proposal-ingest.md`（D3 の利用先）
