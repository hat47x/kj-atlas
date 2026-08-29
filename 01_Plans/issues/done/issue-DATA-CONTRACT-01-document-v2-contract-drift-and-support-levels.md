# Issue Draft: DATA-CONTRACT-01 DocumentV2契約ドリフトとサポートレベル同期

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1 (Stream D second)
- Owner: Codex
- Scope: `02_Architecture/schemas.md`, `02_Architecture/api.md`, `01_Plans/issues/done/issue-DATA-MODEL-OPS-01-mvp-data-model-overview-and-crud-boundary.md`, `01_Plans/issues/done/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`
- Related Backlog: `DATA-CONTRACT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `02_Architecture/data_model_operations_overview.html`, `02_Architecture/schemas.md`, `02_Architecture/api.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DATA-CONTRACT-01
- RequirementStatement: DocumentV2、API文書、frontend型、backend型、実装ルートの差分を棚卸しし、MVP運用サポート範囲と将来契約を一貫して説明・検証できるようにする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=開発者がDocumentV2またはAPIを変更する / 操作=正本文書とfrontend/backend型を照合する / 期待結果=実装済み、埋め込み限定、契約のみの差分が明示され、必要なテストが分かる / 除外=全構造の個別CRUD実装。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export

## Dependency graph（Stream I）

- Upstream（先行固定）: `DATA-MODEL-OPS-01`（support level語彙・CRUD境界・参照導線）
- Parallel（並行整備）: なし
- Downstream（後続依存）: `DATA-MAINT-01`（復旧runbookで参照する契約整合チェック）
- Blocker条件: `PUT /docs/{doc_id}` create-if-absent契約の表現が `schemas.md` / `api.md` / 実装で不一致のまま

## Stream D contract drift rule（固定判定規則）

- Drift を **Critical** と判定する条件（いずれか1つで該当）:
  1) `Document.version` または version gate 条件が `schemas.md` と `api.md` で不一致。
  2) support level 語彙（L1/L1.5/L2/L2.5/L3/L0）が DATA系3Issue と02文書で不一致。
  3) `PUT /docs/{doc_id}` create-if-absent のMVP契約位置づけが文書間で不一致。
- Drift を **Major** と判定する条件:
  - MVP保守責務（Platform operator / Security officer / Support / Developer）に衝突があるが、安全境界変更は含まない。
- Drift を **Minor** と判定する条件:
  - 用語揺れ・参照リンク欠落・重複記載のみで、契約意味論が一致している。
- 判定手順:
  - Phase 1 Readで `Status/Priority/Dependencies/Related ADR` を再抽出し、上記ルールで分類してから修正する。


## 1) 課題 / Problem statement

- `DocumentV2` はfrontend/backend/API/設計文書の複数箇所に表現されており、フィールド追加や検証条件の同期漏れが起きやすい。
- `api.md` では `PUT /docs/{doc_id}` をMVPのCreate契約に寄せ、`POST /docs` を将来候補として残しているが、実装・テスト・関連文書の同期確認が必要である。
- frontend型には `evidenceLinks`、`claimType`、edge endpoint kind など、backend型やMVP運用表での扱いを確認すべき構造がある。
- `PatchApplyStats` などの補助型は、どこまでがMVP運用サポートで、どこからが将来契約かを明示する必要がある。
- A1契約フィールド（`critiqueInputs` / `reproposalDiffs` / `reviewAttribution` / `deterministicTieBreak`）は、UI個別編集の対象ではないが、DocumentV2内で保存・読み込み・API往復する契約境界としてfrontend/backend双方の型と検証を同期する必要がある。

## 2) 背景 / Context

- `ADR-0033` は、型が存在することと運用保守できることを分ける方針を採用した。
- `02_Architecture/data_model_operations_overview.html` はCRUD境界を示すが、型定義のドリフト検出そのものは別Issueで扱う必要がある。
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
- [x] T5 `02_Architecture/data_model_operations_overview.html` と `schemas.md` のサポート記述を更新する。

進捗メモ:

- `claimType`、edge endpoint kind、`evidenceLinks`、`patchApplyLog.stats.upsertEvidenceLinks/deleteEvidenceLinks` はbackend保存モデルとroundtrip testを同期済み。
- `critiqueInputs` / `reproposalDiffs` / `reviewAttribution` / `deterministicTieBreak` はfrontend正本型、strict validator、import正規化、backend保存モデル、backend roundtrip testを同期済み。
- MVPでは上記A1契約フィールドの個別CRUD/UI編集を標準保守対象にしない。DocumentV2スナップショット内の契約のみ/限定保存として扱い、share/export/SafeModeの観点は継続確認する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "DocumentV2|evidenceLinks|PatchApplyStats|reviewAttribution|deterministicTieBreak|POST /docs|PUT /docs" 02_Architecture 03_Implement`
  - `git diff --check -- 01_Plans/issues 02_Architecture`
- 期待結果:
  - 文書、型、実装、テストが同じCreate契約とDocumentV2サポートレベルを示す。
- 未実施時の理由・代替検証:
  - Stream D は非実装スコープのため、docs-checkを正本検証とする。

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
- Phase 4 Execute: 完了（文書→型→ルート同期を更新し、PUT create-if-absent契約を再確認）
- Phase 5 Verify: 完了（`git diff --check` と `rg` による整合確認を実施）
- Phase 6 Proceed/Stop: Proceed（DB実装変更なし。Issue計画整備のみ継続可能）


## 13) Stream D fail-safe stop gates

- [x] Stop gate A（後方互換）: `schemas.md` の version gate ルール（破壊的変更は version を上げる）が明記され、`02_Architecture/data_model_operations_overview.html` と語彙一致している。
- [x] Stop gate B（support level）: `L1/L1.5/L2/L2.5/L3/L0` の定義が契約文書と運用境界文書で一致している。
- [x] Stop gate C（責務衝突）: Platform operator / Security officer / Support / Developer の責務分離が衝突なく記述されている。
- 判定: **Proceed**（3つのStop gateは現行文書上で満たされる。実装依存は凍結契約で切断済み）。

## 14) Stream D → 下流引き渡しチェックリスト

- [x] `schemas.md` の `DocumentV2` support level と version gate 定義を参照先として固定した。
- [x] `02_Architecture/data_model_operations_overview.html` の CRUD/運用責務表と語彙一致（L1/L1.5/L2/L2.5/L3/L0）を確認した。
- [x] 復旧runbook側（`DATA-MAINT-01`）で必須の契約整合チェック（`Document.version`、埋め込み往復保持、`merge_decision_logs`連携）を明記した。
- [x] 非目標（個別CRUD実装、管理UI実装）を再確認し、実装Issueへ越境しないことを固定した。

## 15) Stream D execution delta (2026-05-19)

### Context
- Stream D の担当範囲では、`DocumentV2` の「型定義が存在する」ことと「MVP運用で個別CRUDを保証する」ことの混同が再発しやすい。
- 特に `critiqueInputs` / `reproposalDiffs` / `reviewAttribution` / `deterministicTieBreak` は、A1契約として往復保持が必要だが、運用上は個別編集対象外という境界を維持する必要がある。

### Decision
- `DocumentV2` の support level を `L1/L1.5/L2/L2.5/L3/L0` で固定し、`schemas.md` と `02_Architecture/data_model_operations_overview.html` で同一語彙を必須化する。
- `PUT /docs/{doc_id}` create-if-absent をMVPの唯一の標準Create契約として維持し、`POST /docs` は将来候補（L0）扱いを継続する。
- 後方互換の判定は feature flag ではなく version gate を優先し、非互換変更は version 更新なしで導入しない。

### Consequences
- 運用責務境界（Platform operator / Security officer / Support / Developer）がドキュメント間で衝突せず、`DATA-MAINT-01` の復旧設計に引き渡し可能。
- SafeMode/share-export 領域の契約フィールドが、実装拡張前でも検証観点として残り、契約ドリフトを先に検知できる。
- Stream D の Proceed 判定を「後方互換・support level・責務分離」の3条件で機械的に再確認できる。


## 16) Stream D phase sync（2026-05-20）

### Context
- DocumentV2契約は `schemas.md` / `schemas_review_attribution.md` / `02_Architecture/data_model_operations_overview.html` の解釈差でドリフトしやすい。

### Decision
- Critical判定ルール（Section: Stream D contract drift rule）をVerifyの一次ゲートとして固定する。
- `PUT /docs/{doc_id}` create-if-absent と support level語彙一致を、毎回のRead同期で確認する。

### Consequences
- CRUD境界と契約境界を分離したまま、MVP運用責務の説明を維持できる。

## 18) Stream B phase sync（2026-05-20）

### Context
- Stream B 対象範囲で、schema/CRUD境界/運用責務の差分を再読した。

### Decision
- `DocumentV2` support level は `L1/L1.5/L2/L2.5/L3/L0` を固定し、未分類を `L2.5` として扱う。
- backward compatibility は version gate 優先で固定し、`version: 2` の非互換変更を禁止する。
- DB/API依存が未確定の統合点は read-only contract として公開し、mock-first で検証する。

### Consequences
- Plan→Execute→Verify→Proceed の判定を docs-check で再現できる。
- Self-correction は最大3回で停止条件を維持し、越境実装を防止できる。

## 19) Stream D Phase execution log（2026-05-20）

1. Read: `schemas.md` / `02_Architecture/data_model_operations_overview.html` の契約語彙と support level を再確認。
2. Context/Decision/Consequences: DocumentV2契約ドリフト判定の C/D/C を再固定。
3. CRUD境界固定: MVP標準Create契約を `PUT /docs/{doc_id}` create-if-absent に固定。
4. ドリフト監査反映: version gate と support level語彙一致を一次ゲート化。
5. 運用復旧手順整備: `DATA-MAINT-01` へ契約整合チェック観点を引き渡し。
6. Verify: docs-check（diff/rg）で整合を確認。
7. Self-correction<=3: 再試行上限3回を継続。
8. Final: 契約のみ/将来候補を運用サポートと誤読させない記述を維持。

## 20) Stream D API drift sync（2026-05-24）

### Context
- `DATA-MODEL-OPS-01` の support level 列追加後、`api.md` の冒頭と「将来拡張」節に古い記述が残っていた。
- 具体的には、認証/共有/差分同期を一括で「後回し」とする説明、`ETag`・認証・AI用endpointを非MVPとして扱う説明が、実装済みの access-control / export-audit / Context / AI / ETag 契約と矛盾していた。
- また、実装済みの `/docs/{doc_id}/context-audit` が `api.md` のDocument監査イベント節に載っておらず、CE4監査4点セットの入口を追跡しにくかった。

### Decision
- `api.md` の基本方針を「Document の標準CRUDは全体保存/取得に絞る。認証/認可、監査、Context/AI系APIは限定契約として別節で扱う」に更新する。
- 競合節を、`If-Match` 未指定時は LWW、指定時は `ETag` 一致必須という現行実装に合わせる。
- エラー設計に 403 / 409 / 422 を追加し、安全境界・競合・契約違反を区別する。
- 「将来拡張」節を、現行限定契約と非MVP/別Issue拡張に分割する。`POST /docs`、一般的なPatch API、完全な共有/管理/監査UIは引き続き非MVPまたは別Issue扱いとする。
- Document監査イベント節に `/docs/{doc_id}/context-audit` を追加し、`operation` / hash / dry-run / command / channel / schemaVersion の契約と 409/422 の失敗分類を明示する。

### Consequences
- `api.md` が `docs.py` / backend tests / `02_Architecture/data_model_operations_overview.html` の現行境界と一致し、実装済み契約を非MVPと誤読するリスクを下げる。
- `POST /docs` や個別CRUDを標準契約へ昇格する変更は、引き続き本IssueまたはADR経由で扱う。
- 追加実装は行わず、契約文書とIssue記録の同期に限定する。

### Verify
- `rg -n "後回し|将来拡張|ETag|If-Match|POST /docs|認証|監査|Context|AI" 02_Architecture/api.md 01_Plans/issues/issue-DATA-CONTRACT-01-document-v2-contract-drift-and-support-levels.md`
- `rg -n "GET /docs|PUT /docs|If-Match|ETag|export-audit|context-audit|merge-decision-logs|similar-candidate-groups" 02_Architecture/api.md 03_Implement/backend/src/kj_atlas_api/routes/docs.py 03_Implement/backend/tests/test_docs_roundtrip.py`
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check -- 01_Plans 02_Architecture`

## 21) Verification intake（2026-05-31）

### Context

- `DATA-MODEL-OPS-01` の完了判定は PR #2280（`codex/data-model-ops-01-closeout-20260531`）で分離した。
- 本Issueは `DATA-MODEL-OPS-01` を上流に持つため、現時点では **Openのまま** とし、#2280 がmainへ反映された後にCloseoutを行う。
- ただし、DocumentV2/API/frontend/backendの契約ドリフト検証は、現行main上で再実行済みである。

### Verification

- Backend contract/API integration:
  - Initial run without explicit `--basetemp` failed during pytest setup because `C:\Users\yhata\AppData\Local\Temp\pytest-of-hat47x` was not readable in this host session.
  - Rerun with local basetemp and cache disabled passed:
    - `03_Implement/backend/.venv/Scripts/python.exe -m pytest 03_Implement/backend/tests/test_docs_roundtrip.py 03_Implement/backend/tests/test_docs_a1_error_contract.py 03_Implement/backend/tests/test_docs_audit_integration.py 03_Implement/backend/tests/test_docs_access_control_integration.py 03_Implement/backend/tests/test_data_model_operations_contract.py -q --basetemp 03_Implement/backend/.pytest_tmp_data_contract_01 -p no:cacheprovider`
    - Result: `59 passed, 16 skipped`.
- Frontend contract/regression guard:
  - PowerShell host did not expose `npm`, so the bundled Codex Node executable was used.
  - `C:/Users/yhata/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe ./node_modules/vitest/vitest.mjs run src/import/zip_import.test.ts src/import/schema_validation.test.ts src/import/document_import.test.ts src/import/view_import.test.ts src/diff/review_pack_workflow.integration.test.ts src/export/bundle_export.test.ts src/export/view_metadata.test.ts src/domain/validate_doc.test.ts src/export/canvas_svg.test.ts src/ui/ux_operability_regression.test.ts`
  - Result: `10 passed` files / `102 passed` tests.

### Decision

- `DATA-CONTRACT-01` is verified as closeout-ready, but remains **Open** until the upstream `DATA-MODEL-OPS-01` closeout in PR #2280 is merged or otherwise recreated on main.
- No ADR is required for this verification intake because no create contract, version gate, SafeMode/share-export boundary, or data normalization strategy changed.
- Next action after #2280: change `Status` to `Done`, add final Closeout, and rerun `validate_active_issue_memos.py` plus `triage_actionable_plans.py`.

## 22) Closeout（2026-06-01）

### Context

- PR #2280 (`DATA-MODEL-OPS-01` closeout) is now merged into `main`.
- The 2026-05-31 verification intake already reran the backend Document/API contract checks and frontend import/export/regression guards, and classified this issue as closeout-ready.
- Subsequent DATA-MAINT and ADR work did not change the `DocumentV2` create/update contract, version gate, support-level vocabulary, SafeMode/share-export boundary, or data normalization strategy.

### Decision

- Mark `DATA-CONTRACT-01` as `Done`.
- Treat the `DocumentV2` contract drift slice as closed for the current MVP/productization baseline.
- Keep future changes to individual CRUD, `POST /docs`, audit-viewing UI, retention management, or high-privilege lifecycle operations out of this issue. Those remain routed to `DATA-MAINT-01`, `DATA-MAINT-03`, `DATA-MAINT-04`, or a future ADR as appropriate.

### Consequences

- `DATA-MAINT-01` can continue using the fixed `DocumentV2` support-level and version-gate vocabulary as an upstream input.
- `PRODUCT-QA-01` / `MVP-EXIT-01` should treat `DocumentV2` contract drift as closed for this baseline, while still requiring separate evidence for product value, UX, Compose startup, and high-privilege lifecycle decisions.
- No runtime implementation or public documentation behavior changes in this closeout.

### Verify

- `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py`
- `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py`
- `03_Implement/backend/.venv/Scripts/python.exe -m pytest 03_Implement/backend/tests/test_data_model_operations_contract.py 03_Implement/backend/tests/test_docs_roundtrip.py 03_Implement/backend/tests/test_docs_audit_integration.py -q --basetemp 03_Implement/backend/.pytest_tmp_data_contract_01_closeout -p no:cacheprovider`
- `git diff --check -- 01_Plans/issues/issue-DATA-CONTRACT-01-document-v2-contract-drift-and-support-levels.md`
