# Issue: CE1-CONTRACT-01 CE1 v1 keysetとHTTP envelopeの照合

- Type: Architecture contract / Compatibility
- Status: Done
- Source Issue: `DOC-ARCH-02`（`CI-CE1-01`〜`CI-CE1-03` の異義定義を分離）
- Priority: P1
- Owner: Maintainer / Backend and Frontend contract contributor
- Scope: `02_Architecture/schemas.md`, `02_Architecture/api.md`, `02_Architecture/architecture.html`, `03_Implement/backend/src/kj_atlas_api/models_context.py`, `03_Implement/backend/src/kj_atlas_api/routes/context.py`, `03_Implement/backend/tests/test_context_bundle_routes.py`, `03_Implement/frontend/src/domain/context/query_preview.ts`, 同test
- Related Backlog: `DOC-ARCH-02`, `CE1-CONTEXT-FOUNDATION`
- Related ADR/Spec: `00_Prompt/ai_cognitive_externalization_requirements.md`, `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`, `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`, `02_Architecture/contract_consolidation_inventory.md`
- Expected verification level: `integration`

## Requirement meta I/F

- RequirementID: CE1-CONTRACT-01
- RequirementStatement: closed-worldのCE1 v1について、論理型、HTTP request/response envelope、下流handoff keyを分離し、各required keyとversioning判断を一意にする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=CE1 ContextQuery/ContextBundleを実装または利用する / 操作=schemasから型、apiからendpointを読む / 期待結果=同一payloadが文書間でrequiredにもunknownにもならず、`schemaVersion`と`queryId`の所属を一意に判断できる / 除外=CE2/CE4の権限拡張、新しいAI機能。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode

## 1. 課題

CE1 v1はclosed-worldでありながら、現在は次の定義が同時に存在する。

| 論点 | 定義A | 定義B / 実装現況 | 危険 |
|---|---|---|---|
| `ContextQueryV1` | `02_Architecture/architecture.html`旧signatureは`scope:string[]`、depth列挙、SafeMode object | `schemas.md`、backend、frontendは`queryId`、scope列挙、depth整数、`safeModePolicy:"strict"`、`previewConfirmed` | 片方準拠payloadが他方でunknownになる |
| `ContextBundleV1.queryId` | `api.md` §2.8はresponse required | `schemas.md`、backend response、frontend mockには存在しない | v1 required keyの削除なのか文書誤記なのか未判定 |
| `schemaVersion` | backend HTTP responseは`"1.0.0"`を返す | `schemas.md`の論理`ContextBundleV1`とfrontend mockには含まれない | 論理bundle本体とtransport envelopeが混同される |
| `sourceBundleHash` | CE2/CE4 handoffでは必要 | CE1 bundle responseでは`bundleHash`から派生する | CE1 core fieldとして永続化される危険 |

SafeMode、preview gate、deterministic hashを維持したまま、既存v1を暗黙に変更せず照合する必要がある。

## 2. Scope / Non-goals

Scope:

- `ContextQueryV1`、`ContextBundleV1`、`ContextQueryValidationResponse`、`ContextBundleResponse`、CE2/CE4 handoffのkey所属を表で確定する。
- 型の正本を`schemas.md`、endpoint/status/error/envelopeの正本を`api.md`に限定する。
- backend/frontendのclosed-world validatorとfixtureを同じkey matrixへ同期する。

Non-goals:

- 新しいContract ID、AI権限、auto-apply経路の追加。
- SafeMode既定ON、`reviewedOnly`、preview gate、人手レビュー昇格の緩和。
- 根拠なくv1 required keyを追加・削除すること。

## 3. 受入条件

- [x] logical type、HTTP request、HTTP response、handoff metadataの4層key matrixがあり、各keyの所属とrequired/optionalが一意である。
- [x] `ContextQueryV1`のkey・列挙・rangeが`schemas.md`、backend、frontendで一致する。
- [x] `ContextBundleV1.queryId`が、採択済みv1 required keyか過去文書の誤記かを上流記録とcontract testから根拠付きで判定する。
- [x] `schemaVersion`がbundle hash対象の論理fieldかHTTP envelope metadataかを明示し、canonical hash入力を変えない。
- [x] `sourceBundleHash`をCE1 core responseへ混入させず、CE2/CE4のread-only handoffとして位置づける。
- [x] `api.md`はpayload型を再定義せずschema anchorを参照し、endpoint/status/error/envelopeだけを規定する。
- [x] `previewConfirmed=false -> 422 preview_required`、unknown key拒否、同一queryのhash一致、SafeMode strictが回帰しない。
- [x] v1 required key削除・意味変更が必要なら作業を停止し、ADR-0047 R-4に従ってversioning判断を起票する。

## 4. 実装タスク

- [x] T1 現行文書、backend model/route/test、frontend type/testからkey matrixを抽出する。
- [x] T2 `queryId`、`schemaVersion`、`sourceBundleHash`の所属を契約形成記録まで遡って判定する。
- [x] T3 `schemas.md`へ唯一の論理型、`api.md`へ唯一のtransport契約を反映する。
- [x] T4 `02_Architecture/architecture.html`の旧type signatureを責務参照へ縮約し、形成記録はhistoryへ移す。
- [x] T5 backend/frontend contract testを同じmatrixでgreenにする。
- [x] T6 `DOC-ARCH-02`のConflict inventoryをResolvedまたはADR-requiredへ更新する。

## 5. 検証計画

```powershell
python -m pytest 03_Implement/backend/tests/test_context_bundle_routes.py
cd 03_Implement/frontend
npm test -- --run src/domain/context/query_preview.test.ts
```

追加確認:

- `rg -n "ContextQueryV1|ContextBundleV1|schemaVersion|queryId|sourceBundleHash" 02_Architecture 03_Implement/backend/src/kj_atlas_api/models_context.py 03_Implement/frontend/src/domain/context`
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `git diff --check`

## 6. Stop条件

- v1 required keyの削除、意味変更、enum再解釈が必要になる。
- SafeMode、preview gate、proposal-only、review昇格境界に変更が必要になる。
- 文書と実装のどちらを正とするか、上位記録から一意に決められない。

Stop時は推測で統合せず、ADR-0047 R-4の破壊的契約変更としてversioning判断へ送る。

## 進捗記録 2026-07-15: layer matrix / cross-runtime hash

- 形成順、現行SSOT、backend/frontend実装を照合し、`queryId`はlogical query専用、`schemaVersion="1.0.0"`はHTTP response metadata、`sourceBundleHash`は下流が`bundleHash`から派生するread-only handoff値と判定した。
- 旧API形成記録のbundle response `queryId`は、後発のschema型にも稼働中responseにも存在しないtype再掲上の誤帰属であり、Informative historyとして保持する。現行v1 fieldの追加・削除は行わない。
- `schemas.md`へlogical/transport/handoff matrix、`api.md`へendpointとresponse型参照、`02_Architecture/architecture.html`へ解決済みmatrix導線を反映し、Conflict inventory `CI-CE1-01..03`をResolvedへ更新した。
- frontend logical bundle validatorへunknown-key拒否を追加し、`queryId` / `schemaVersion` / `sourceBundleHash`の混入をfail-closed化した。frontendの`queryCanonicalHash`をbackendと同じ全object key辞書順canonical JSON + SHA-256 lowercase hexへ同期し、共通fixture hashを両runtimeのtestで固定した。

## 完了記録 2026-07-15

- backend `test_context_bundle_routes.py`: 20件pass。query/bundle HTTP responseのexact key、transport metadata、`queryId` / `sourceBundleHash`非混入、cross-runtime SHA-256 fixtureを含む。
- frontend `query_preview.test.ts`: 11件pass。query/bundle closed-world、SafeMode/preview gate、logical bundleへのtransport/handoff key混入拒否、backend同値hashを含む。`tsc --noEmit`もpass。
- Active issue validatorはclose直前34件、Done反映後33件をpass。validator unit 11件、変更文書の相対link 22件、stale unresolved参照0、`git diff --check`もpassした。
- v1 payload、backend response、SafeMode、proposal-only、review昇格、share/export、provider=`none`を変更していない。全Acceptance criteriaとT1〜T6を満たしたためDoneとする。
