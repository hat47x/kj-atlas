# Issue: DOC-ARCH-02 現行契約の物理SSOT化と形成履歴の分離

- Type: Documentation quality / Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Architecture contributor
- Scope: `02_Architecture/architecture.md`, `02_Architecture/api.md`, `02_Architecture/schemas.md`, `02_Architecture/schemas_review_attribution.md`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/contract_reading_guide.md`, `02_Architecture/history/`（新規）, `AGENTS.md`（導線のみ）
- Related Backlog: `DOC-ARCH-01`, `DATA-CONTRACT-01`
- Related ADR/Spec: `01_Plans/issues/issue-DOC-ARCH-01-architecture-source-log-separation.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`, `02_Architecture/contract_reading_guide.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DOC-ARCH-02
- RequirementStatement: 実装者がキーワードや日付から推測せず、Contract ID・型・endpoint・運用支援レベルの現行値を物理的に一意な正本から読めるようにし、Stream/freeze/rerun等の形成履歴を現在契約から分離する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=closed-worldのCE1/DocumentV2契約を変更または実装する / 操作=architecture→api/schema→ops boundaryを読む / 期待結果=同じ型・Contract IDの異義定義に遭遇せず、現行キー・列挙・既定値・禁止事項・支援レベルを一意に特定できる / 除外=新規契約追加、runtime挙動変更、履歴削除。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export

## 1) 課題 / Problem statement

`contract_reading_guide.md` は、現行契約と履歴が同じファイルにあることを認識し、「正本」「固定」「契約」と書かれた箇所を優先するよう案内している。しかし相互に異なる定義がいずれも固定契約を名乗るため、解釈ルールだけでは一意に読めない。

既知の衝突・欠落:

| 対象 | 現在の不一致 |
|---|---|
| `ContextQueryV1` | `architecture.md` は `scope:string[]` / depth列挙 / SafeMode object、`schemas.md` は `queryId` / scope列挙 / depth数値 / `safeModePolicy:"strict"`。 |
| `ContextBundleV1` | `api.md` はresponseに `queryId` を要求する一方、`schemas.md` の型とbackend response modelには無い。`schemaVersion` の掲載位置も一致しない。 |
| `Card` / `DocumentV2` | 冒頭の合成型に `holdState`, `shelf`, `meta`, `contradictionSignalDecisions`, `ka` がなく、後段の§14〜17だけに加算定義がある。 |
| 文書構造 | `architecture.md`、`api.md`、`schemas.md`、data model overviewに日付付きfreeze、Stream実行ログ、checkpoint、reaffirmationが残り、章番号も前後する。 |

closed-world契約では、一方の「正本」に従ったpayloadが別の「正本」で `unknown_contract_key` になり得る。SafeMode契約の形まで異なるため、単なる可読性ではなく安全・実装境界の問題である。

## 2) 背景 / Context

- `DOC-ARCH-01` は value traceability と reading guide を追加してDoneになったが、物理分離を後続タスクとして明記した。
- `DATA-CONTRACT-01` は当時のDocumentV2基線を閉じたが、その後に§14〜17の加算スキーマが追加され、合成型への統合は未実施である。
- `contract_reading_guide.md` §6 は、現行契約を残し、freeze note/実行ログを `02_Architecture/history/` 相当へ分ける将来方針を既に示している。
- 本Issueは確定済み方向の実行であり、ADR-0047に従って新規ADRを作らない。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 実装者が誤った契約を選ぶと、保留・提案・レビューの意味境界が壊れる。
- 安全（THREAT_MODEL / SafeMode）: SafeMode既定、未レビュー保護、proposal-only、人手レビュー昇格を一意に読めることが必要。
- 企業・行政要件（enterprise_architecture）: 現行契約と形成履歴を監査時に分けて説明できる。
- 後方互換（schemas）: 文書整理で既存runtime契約を暗黙変更せず、差異は明示的なcontract issueへ送る。

## 4) 提案する解決策 / Proposed solution

### 4.1 責務別の物理SSOT

- `architecture.md`: コンポーネント、責務、信頼境界だけを正本化し、型シグネチャを再定義しない。
- `schemas.md`: 型、キー、列挙、既定値、version、互換規則の唯一の正本。DocumentV2は採択済みoptional fieldを含む合成型を先に読める形にする。
- `api.md`: endpoint、status/error、認証・副作用の正本。payloadはschema型名とanchorを参照し、同じ型を再定義しない。
- `data_model_operations_overview.md`: 現行の物理モデル、CRUD、support level、運用責任だけを保持する。
- `contract_reading_guide.md`: Contract ID/型/論点から唯一の正本anchorへ向かう索引。契約値を複製しない。
- `02_Architecture/history/`: Stream/freeze/rerun/checkpoint/reaffirmation等の形成履歴。各ファイルに `Informative`, 元文書, 対象期間, snapshot/日付, 現行正本への逆リンクを付ける。

### 4.2 競合解消規則

1. 同一内容の重複は正本1箇所へ統合し、他文書は参照へ置換する。
2. 内容が異なる場合は、Accepted ADRと既存の現行契約節を上位根拠とする。
3. backend/frontendのmodel・fixture・contract testは、文書選択を裏付ける整合証拠として使い、実装だけを理由に上位契約を暗黙変更しない。
4. 上位根拠でも一意に決まらない差異は `Conflict` として表に残し、契約値変更を扱う子Issueへ分離する。本Issue内で推測修正しない。
5. 既知の `ContextBundle.queryId`、`schemaVersion`、DocumentV2合成型は、移動前に差異表を作り、解決根拠を記録する。

非目標:

- 新しいContract ID、field、endpoint、error語彙の追加。
- Document `version: 3` またはCE v2への移行。
- runtime実装の変更。
- Stream/freeze履歴の削除や改変。
- SafeMode、proposal-only、review権限の緩和。

## 5) 受入条件 / Acceptance criteria

- [x] Contract ID・型・endpointごとに、現行の規範定義が物理的に1箇所だけ存在する。
- [x] `architecture.md` は責務、`schemas.md` は型、`api.md` はendpointという責務分離を守り、他文書はanchor参照だけを持つ。
- [x] `ContextQueryV1`, `ContextBundleV1`, `ProposalPatchV1`, `AuditEventV1` のキー・列挙・既定値・errorが一意で、現行model/fixture/contract testと整合するか、差異が専用子Issueへ明示される。
- [x] `api.md` の既知 `ContextBundle.queryId` 不一致と `schemaVersion` 掲載差異が、根拠付きで解消または子Issue化される。
- [x] `Card` / `DocumentV2` の合成型が、`holdState`, `shelf`, `meta`, `contradictionSignalDecisions`, `ka` を含む採択済みoptional fieldを一読で網羅する。
- [x] support level表と合成型に欠落・異義がない。
- [x] Stream/freeze/rerun/checkpoint等はInformative履歴へ物理移動し、現行契約として読めない。
- [x] 履歴から元文書・現行正本へ双方向に辿れる。
- [x] SafeMode、未レビュー保護、proposal-only、`human_reviewed`人手昇格、version互換の意味変更が0件である。
- [x] `AGENTS.md` と reading guide の導線が新構成に一致する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 規範節・履歴節・重複定義・既知衝突のinventoryをファイル/anchor/Contract ID単位で作る。
- [x] T2 競合解消規則に従い、各型・endpoint・運用境界の唯一の正本anchorを決める。CE1 v1の値Conflictは`CE1-CONTRACT-01`へ分離し、本Issueで推測統合しない。
- [x] T3 `schemas.md` の現行合成型を先頭側へ統合し、重複定義を参照へ変える。
- [x] T4 `architecture.md` / `api.md` / data model overviewを責務別に縮約する。
- [x] T5 `02_Architecture/history/` へ形成履歴を移し、メタと逆リンクを付ける。
- [x] T6 reading guideと`AGENTS.md`を新しい参照順へ同期する。
- [x] T7 backend/frontendの対象contract/roundtrip testsとMarkdownチェックで、意味非変更とリンク整合を検証する。
- [x] T8 自動再発防止を `DX-DOC-02` へ引き渡す。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "ContextQueryV1|ContextBundleV1|ProposalPatchV1|AuditEventV1" 02_Architecture`
  - `rg -n "holdState|shelf|meta|contradictionSignalDecisions|ka" 02_Architecture/schemas.md 02_Architecture/data_model_operations_overview.md`
  - `rg -n "^#{1,4} .*?(Stream|freeze|rerun|execution log|checkpoint|reaffirmation)" 02_Architecture/architecture.md 02_Architecture/api.md 02_Architecture/schemas.md 02_Architecture/data_model_operations_overview.md`
  - `python -m pytest 03_Implement/backend/tests/test_context_bundle_routes.py 03_Implement/backend/tests/test_data_model_operations_contract.py`
  - frontendのimport/schema validation/roundtrip対象テスト（package scriptまたは対象Vitest）
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - current領域の異義定義・履歴見出しが0件で、contract/roundtrip testsが変更前後とも同じ結果になる。
- 未実施時の理由・代替検証:
  - runtime test環境が無い場合はdocs移動を完了扱いにせず、対象test名・未実施理由・再開コマンドを記録する。

## 8) 代替案 / Alternatives considered

- reading guideだけを改善する: 固定を名乗る異義定義を解消できないため不採用。
- すべてを1つの巨大契約文書へ統合する: 責務混在と更新競合を悪化させるため不採用。
- 履歴を削除する: 形成経緯と監査証跡を失うため不採用。
- 実装を正として文書を一括追従する: 上位/下位の順序を逆転させるため不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 移動時の情報欠落、anchor切れ、履歴を現行契約へ誤昇格、契約値の暗黙変更。
- 影響範囲: CE1/CE2/CE4、DocumentV2、SafeMode、import/export、実装者の参照順。
- ロールバック手順: 責務別の小さなcommit/PRスライスで進め、問題のある移動だけ戻す。元文書の節を削除するcommitは、履歴側追加とリンク検証が同時に通るまで作らない。
- Stop条件: 上位根拠で一意に決まらない契約差異、SafeMode等の意味変更、version gate超過を検知した場合は本Issueを止め、契約Issueへ分離する。

## 10) Additional context

- 本件は `DOC-ARCH-01` が明記した後続実行であり、既存ADRの再掲ではない。
- ADR化が必要になる条件: version 3、既存Contract IDの意味変更、新しい安全・互換境界の採択が必要になった場合（ADR-0047 R-3/R-4）。

## 進捗記録 2026-07-11: inventory / history boundary slice

- `02_Architecture/contract_consolidation_inventory.md` を追加し、責務別到達先、CE1の3 Conflict、DocumentV2加算field、履歴移動H-A〜H-D、停止条件、検証コマンドを固定した。
- `02_Architecture/history/README.md` を追加し、Informativeメタ、逆リンク、batch移動、非破壊規律を明文化した。
- `contract_reading_guide.md` と `AGENTS.md` を新しいinventory/history入口へ同期した。
- 契約値、runtime、schema version、SafeModeは変更していない。`ContextQueryV1` / `ContextBundleV1` / `schemaVersion`はConflictのまま明示し、T2で上流根拠から一意に決まらなければ子Issueへ分離する。

## 進捗記録 2026-07-15: composite type / H-D history slice

- T2: 責務別SSOTを `schemas.md`（型）、`api.md`（endpoint/status/error/envelope）、data model overview（CRUD/support level）へ固定した。CE1 v1の `queryId` / `schemaVersion` / `sourceBundleHash` は値を推測せず、`CE1-CONTRACT-01`へ分離した。
- T3: `Card`へ`holdState?` / `meta?` / `ka?`、`DocumentV2`へ`shelf?` / `contradictionSignalDecisions?`を統合した。後段§14〜§17は型の再定義をやめ、§3.2/§3.5参照へ変更した。
- T5 partial (H-D): `data_model_operations_overview.md` former §1.2/§1.3/§8〜§13を`history/data-model-operations-stream-d-2026-05.md`へ移し、元文書・履歴索引・reading guideの双方向導線を追加した。
- 検証: Active issue validator 31件pass、triage active=31 / ready=14 / blocked=17 / stopper=0、validator unit 10件pass、CE1 backend contract 18件pass、CE1 frontend contract 9件pass、変更文書の相対link 17件エラー0、合成型定義の重複0、data model overviewの履歴見出し0。
- 未完了: H-A/H-B/H-C（architecture/api/schemas履歴移動）、API縮約、AGENTS最終同期、contract/roundtrip testsの全量確認。契約値、runtime、Document version、SafeMode、share/export既定は変更していない。

## 進捗記録 2026-07-15: H-A architecture history slice

- T4 partial / T5 H-A: `architecture.md`のCE0 snapshot、旧§7A.2.1型・method・event-order再掲、2026-05-04 baseline、Stream B反映メモを`history/architecture-contract-freeze-formation-2026-04-to-05.md`へ物理移動した。
- 現行側は責務・信頼境界を維持し、型を`schemas.md`、endpoint/status/errorを`api.md`、未解決CE1差異を`CE1-CONTRACT-01`へ参照する。履歴索引・inventory・元文書の双方向導線を同期した。
- 検証: 移動元39行の履歴保持、変更文書の相対link 21件、`architecture.md`の履歴風見出し0件、Active issue validator 33件、validator/triage unit 11件、CE1 backend contract 18件、CE1 frontend contract 9件がpassした。
- `main`統合後のActive集合は33件（Draft 18 / Open 8 / In Progress 7）。H-B/H-C、§7A.6/§7Bの責務別縮約、API縮約、AGENTS最終同期、contract/roundtrip tests全量確認は未完了。
- 契約値、runtime、Document version、SafeMode、未レビュー保護、proposal-only、share/export既定は変更していない。

## 進捗記録 2026-07-15: H-B API history / responsibility slice

- T4 partial / T5 H-B: `api.md`の旧Phase 1〜6、mock validation plan、Stream A log、CE0/CE1 sync/freeze/handoff、Auth freeze note、末尾addendumを`history/api-contract-formation-2026-04-to-05.md`へ物理移動した。
- 現行§2.8はendpoint/status/error/副作用に縮約し、型・キー・canonicalization・version互換を`schemas.md`、責務・信頼境界を`architecture.md`、未解決`queryId`/`schemaVersion` envelope差異を`CE1-CONTRACT-01`へ参照する。CE4 mock/stub境界は現行§2.9.5へ移設し、意味を変更していない。
- 検証: 削除対象の実質190行中188行を履歴または現行節へ原文保持し、残る2行は意味を維持した見出し名/節番号の正規化。相対link 23件、`api.md`の履歴風見出し0件、Active issue validator 33件、validator/triage unit 11件、CE1 backend contract 18件、CE1 frontend contract 9件がpassした。
- 履歴索引、reading guide、inventory、元文書の双方向導線を同期した。H-C、§7A.6/§7Bの責務別縮約、AGENTS最終同期、contract/roundtrip tests全量確認は未完了。
- 契約値、runtime、Document version、SafeMode、未レビュー保護、proposal-only、share/export既定は変更していない。

## 進捗記録 2026-07-15: H-C schema history slice

- T5 H-C: `schemas.md`の旧§1.0.1 drift gate、§11.1 migration snapshot、CE1 clarification、旧§1.3〜§13のfreeze/Stream形成記録を`history/schema-contract-formation-2026-05.md`へ物理移動した。これによりH-A〜H-Dの4batchが完了した。
- 現行側は型、validation、Document version、support level、Contract IDを維持した。現行のCE0/CE1見出しと§6.2から履歴語を除き、architecture/API/履歴文書のschema anchorを同期した。
- T6: history index、reading guide、inventory、`AGENTS.md`を最終配置へ同期した。
- T7: 移動前の実質行を現行＋履歴へ突合し、未一致20行がすべて意図的な見出し/案内文改称であることを確認した。相対link 48件エラー0、current 4文書の履歴見出し0、CE型定義は`schemas.md`各1箇所、`git diff --check` pass。最新`main`統合後にActive issue validator 35件・validator unit 11件・backend contract/roundtrip 48件・frontend contract/schema/roundtrip 76件がpassした（backendは環境依存21件skip、既知warning 1件）。
- 未完了: T4のarchitecture §7A.6/§7B責務別縮約、T8の`DX-DOC-02`引き渡し。契約値、runtime、Document version、SafeMode、未レビュー保護、proposal-only、share/export既定は変更していない。

## 完了記録 2026-07-15: responsibility SSOT / recurrence handoff closeout

- T4: `architecture.md`の重複§7A.6を除去し、§7BをCE1/CE2/CE4の責務・信頼境界と正本リンクへ縮約した。required key、列挙、error、HTTP副作用の再掲をやめ、型=`schemas.md`、HTTP=`api.md`、責務=`architecture.md`へ一意化した。
- T8: current/history分離、責務別SSOT、history必須メタ、既知CE1 Conflict、負例fixtureの検査境界を`DX-DOC-02`へ引き渡した。checker/CI実装は同Issueのスコープに残す。
- Closeout検証: current 4文書の履歴見出し0、CE主要型定義は`schemas.md`各1箇所、architecture内のrequired key/error/enum再掲0、history 4ファイルの必須メタ欠落0、変更文書の相対link 18件エラー0、validator unit 11件がpassした。issue validatorはclose直前35件、Done反映後34件をpass。直前の最新`main`統合後にはbackend contract/roundtrip 48件、frontend contract/schema/roundtrip 76件もpass済み。
- SafeMode既定ON、未レビュー保護、proposal-only、`human_reviewed`人手昇格、provider=`none`、Document version、share/export既定を変更していない。全Acceptance criteriaとT1〜T8を満たしたためDoneとする。
