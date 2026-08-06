# Issue Draft: SAAS-TENANT-SURFACE-01 frontend呼び出しを持たないtenant-guarded backend routeが9件

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/routes/context.py`
- Related ADR/Spec: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Expected verification level: `docs-check`

## 課題

SAAS-TENANT-01の2件の監査（2026-08-06、backend全routeの網羅性監査とfrontend全fetch呼び出し箇所の監査）を突き合わせた結果、以下9件のtenant-guarded backend routeに対応するfrontend呼び出しが `03_Implement/frontend/src` 内に一切見つからなかった。

- `POST /docs/{doc_id}/context-audit`
- `merge-decision-logs` 系 3 route
- `similar-candidate-groups`
- `polygon-handoff/verify-contract`
- `POST /ai/suggest-island-summary`
- `/context/*` 4 route

いずれもbackend側の認可境界（`_authorize_request`／`require_tenant_scoped_api_precondition`）は正しく適用されており、セキュリティ上の穴ではない。

## 論点（人的判断が必要な理由）

未分類のAPI面である可能性が複数あり、コードだけでは判別できない。

(a) 死んだコード（過去に使われていたが、frontend側の実装変更で呼び出し元が消えた）。
(b) 外部消費者向け（MCP、将来のAgent連携等、frontend以外からの呼び出しを想定した契約）。
(c) 未実装のfrontend機能（backend契約は先行して用意されているが、対応するUIがまだない）。

判断によって対応が変わる: (a)なら削除候補としてDX-CLEANUP系issueへ、(b)ならcontractとして`api.md`に「外部消費者向け」と明記、(c)なら実装待ちのバックログとして扱う。

## 影響

低リスク（認可は正しく機能している）。ただし、使われていない、あるいは意図が不明なAPI面は、将来の変更時にテスト漏れや意図しない振る舞いを生みやすく、SAAS-TENANT-01のようなセキュリティ監査のたびに「本当に全部把握できているか」の確認コストを生む。

## Acceptance

- [x] 9 routeそれぞれについて、(a)/(b)/(c)のいずれかに分類する。→ 実際に現在のコードを突き合わせた結果、対象は9件ではなく11件だった（下記「実装記録」参照）。11件全てを分類済み。
- [x] (a)と判定したものは別issueとして削除を検討する。→ `issue-DX-CLEANUP-07-ai-suggest-island-summary-route-no-frontend-caller.md`（Draft）を新規作成。
- [x] (b)と判定したものは`api.md`へ「外部消費者向け」である旨を明記する。→ `02_Architecture/api.md` §2.5（`POST /docs/{doc_id}/context-audit`）に消費者境界の注記を追加。

## Validation

- 分類結果を本issueまたは`api.md`へ記録する。→ 下記「実装記録（2026-08-06）」節、および`api.md`の該当箇所に記録済み。
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python 01_Plans/docs_check.py`

## 実装記録（2026-08-06）

### 手法

課題文の「9件」という数字と、routeのグルーピング（`merge-decision-logs系3route`／`/context/*`4route）を鵜呑みにせず、次の手順で現在のコードから独立に再導出した。

1. `03_Implement/backend/src/kj_atlas_api/routes/{docs,ai,context}.py`の全`@router.`宣言を洗い出し、`_authorize_request`（docs.py）または`require_tenant_scoped_api_precondition`（ai.py個別route依存 / context.py router全体依存）でtenant-guardされているものだけを対象にした。`GET /ai/provider-status`はどちらのゲートも掛かっていないため対象外。
2. `03_Implement/frontend/src/api/client.ts`（784行、全文読み込み済み）の全export関数を洗い出し、各routeに対応するwrapperが存在するか、存在する場合はそのwrapperの呼び出し元が`client.ts`/`client.test.ts`以外（実際には主に`App.tsx`）に存在するかを`Grep`で確認した（未使用wrapperもgapとして扱う方針に従った）。
3. gapと判定したroute（wrapperが無い、またはwrapperがあっても呼び出し元が無いもの）について、`git log --oneline -S'<対象文字列>' -- 03_Implement/frontend/src`で「frontendでそのroute文字列が過去に増減した commit」の有無を確認し、(a)の可能性を機械的に判定した（0件なら(a)ではない）。
4. 残りについて、`03_Implement/mcp/src`内の参照、`01_Plans/issues/`・`02_Architecture/`内の関連ADR/issue/spec、および frontend側のコードコメント・関連domainモジュールを調査し、(b)/(c)の判断根拠を集めた。

### 再集計結果: 対象は9件ではなく11件

tenant-guarded routeは合計20件（docs.py 9件 + ai.py 7件 + context.py 4件）。このうち9件は実際に`client.ts`のwrapper経由で`App.tsx`等から呼ばれていることを確認した（`getDocument`/`putDocument`/`postExportAudit`/`suggestLayout`/`suggestMerges`/`proposeIslandSummary`/`recordProposalDecision`/`generateNarrative`/`checkNarrative`）。残る11件がfrontend呼び出し元を持たないgapであり、これが今回の対象である。

なお、課題文自身の箇条書き（context-audit 1 + merge-decision-logs系3 + similar-candidate-groups 1 + polygon-handoff 1 + suggest-island-summary 1 + /context/* 4）を素直に数えると合計11であり、見出しの「9件」はこの列挙とすでに矛盾している。今回の11件という結果は、この列挙を修正して裏付けたものであり、新たに発見した追加routeはない。

### 分類結果（11件）

| # | Route | 分類 | 根拠 |
| --- | --- | --- | --- |
| 1 | `POST /docs/{doc_id}/context-audit` | **(b)** 外部消費者向け（最有力。ただし未結線） | `channel: "api"｜"cli"｜"gui"`契約。read-only MCPサーバーが外部消費者の候補として名指しされたが未結線（`03_Implement/mcp/src/audit_log.ts:4-14`のコメント、`03_Implement/mcp/README.md`「Non-goals」節、`issue-EXT-CONN-01-readonly-mcp-server.md` AC-3「CE-4のバックエンド`POST /docs/{id}/context-audit`への実結線は今回未実施」）。`issue-EXT-AGENT-02-agent-response-import.md`のスコープ判断4も別の外部連携機能（エージェント応答取込）でこのrouteの採用を検討し、`command`許可リストがclosed-worldであることを理由に不採用と判定。git履歴では`03_Implement/frontend/src`で"context-audit"という文字列に触れたcommitは`971c118e`（2026-07-09、EXT-AGENT-02実装）の1件のみで、中身はwrapper追加ではなく上記スコープ判断を記すコード内コメント追加のみ（(a)ではない）。**不確実性**: `channel`に`"gui"`も含まれるため、CE1の実文書対応が実装された場合にfrontend自身がこのrouteの呼び出し元になる余地は残る。現時点で「frontendを呼び出し元にする」という具体的な計画を記す open issueは無く、「MCP/外部Agentを呼び出し元にする」という具体的な計画（EXT-CONN-01・EXT-AGENT-02が実際に検討し記録した）の方が根拠が強いため(b)を最有力とした。 |
| 2 | `POST /docs/{doc_id}/merge-decision-logs` | **(c)** 未実装のfrontend機能 | git履歴: `03_Implement/frontend/src`で"merge-decision-logs"という文字列に触れたcommitは0件（一度もfrontendから参照されたことがない）。frontendは統合判断を別の仕組み（`DocumentV1.mergeSuggestionDecisions[]`、`PUT /docs/{doc_id}`経由でDocument本体に埋め込み保存、`App.tsx:828,851,872,3096,3192-3193`・`domain/merge_suggestion_decisions.ts`・`domain/merge_decision_audit.ts`で使用）で永続化しており、この2つの仕組みは意図的に別物として扱われている（`02_Architecture/data_model_operations_overview.html:392`「embedded限定…append-onlyの`merge_decision_logs`と混同しない」、`02_Architecture/functional-dependency-integrity-2026-08-06.html` F-6節が本日時点でこの構造的ギャップ＝`merge_decision_logs`テーブルは正本化できる器を持つが現状は`mergeSuggestionDecisions[]`側が状態でありlogは未使用、と分析）。 |
| 3 | `GET /docs/{doc_id}/merge-decision-logs/by-group/{group_id}` | **(c)** 同上 | 上記と同一根拠。 |
| 4 | `GET /docs/{doc_id}/merge-decision-logs/restore/{snapshot_version}` | **(c)** 同上 | 上記と同一根拠。 |
| 5 | `GET /docs/{doc_id}/similar-candidate-groups` | **(c)** 未実装のfrontend機能 | git履歴: "similar-candidate-groups"文字列に触れたfrontend commitは0件。MCP参照も0件。frontendの実際のマージ候補提示UI（`MergeSuggestionsPanel`）はLLMベースの`POST /ai/suggest-merges`（`suggestMerges` wrapper、呼び出し確認済み）で駆動されており、非LLMのheuristic版であるこのrouteとは別経路。両者は`STREAM_B_CONTRACTS.candidateGroup`（`CTR-2B-01-CANDIDATE-GROUP-V1`、`domain/stream_b_contract.ts`）という同一contract IDで応答形状を約束しているが、実際に配線されたのはLLM版のみ。`issue-DX-DOC-05-undocumented-response-model-endpoints.md`（Done）はこのrouteの`response_model`文書化のみを扱い、呼び出し元の存在は主張していない。 |
| 6 | `POST /docs/{doc_id}/polygon-handoff/verify-contract` | **(c)** 未実装のfrontend機能 | git履歴: "polygon-handoff"文字列に触れたfrontend commitは0件。MCP参照も0件。`02_Architecture/api.md` §2.10自身が「Polygon auto-fit の**backend接続準備**として」と明記しており、まだ接続されていない前提の契約であることを文書自身が認めている。frontend側は同等の検証ロジックをHTTP経由ではなくローカルstub（`domain/p2c_polygon_stub_client.ts`の`runP2CMockValidation`、`domain/p2c_polygon_handoff.ts`）として独自に持っており、`issue-DX-CLEANUP-05-deterministic-tie-break-order-duplicated.md`（Done）はtie-break順序定数をfrontend/backend双方に意図的に複製しcross-language contract testで同期を保証する対応を取った（HTTP呼び出しへの統合ではない）。 |
| 7 | `POST /ai/suggest-island-summary` | **(a)** 死んだコード | `60111b5c7aca5a51d15c254133c625801afe8552`（2026-02-15 08:45:02 +0900、"Add AI island summary suggestion endpoint and UI action"）でbackend route・frontend wrapper・UI actionが同時追加された。`b65d24d785f3a042f7cfb1a102f58721aff08c14`（2026-07-20 00:21:59 +0900、"refactor(frontend): remove replaced focus and summary helpers"）でUIがproposal-only経路（`proposeIslandSummary`/`POST /ai/proposals/island-summary`）へ置き換わり、frontend wrapper `suggestIslandSummary`と型`SuggestIslandSummaryResult`が`client.ts`から削除された（`issue-DX-CLEANUP-04-unreferenced-canvas-shell-and-client-helpers.md`、Done、に記録済み）。backendのhandler関数自体は`propose_island_summary`（`ai.py:593-594`）からのPython内部呼び出しで生きているが、HTTP route自体の外部公開に対する呼び出し元は無い。→ `issue-DX-CLEANUP-07-ai-suggest-island-summary-route-no-frontend-caller.md`（Draft）を新規作成し、route公開自体の削除検討をMaintainerに委ねた。 |
| 8 | `POST /context/query` | **(c)** 未実装のfrontend機能 | git履歴: "/context/query"文字列に触れたfrontend commitは0件。`issue-CE1-context-query-bundle-foundation.md`（Done、closure 2026-06-20）がCE1を"mock-first, contract-only interface until a separate implementation slice explicitly expands the provider/runtime behavior"として明示的に凍結。`issue-EXT-AGENT-01-agent-task-package-export.md`（Done）が実装前調査で「`ContextQueryPreviewPanel`/`/context/query`・`/context/bundle`を実際に呼び出すフロントエンド呼び出し元も皆無（本Issueが最初の呼び出し元になる想定だった）」と明記した上で、実際には呼ばずローカル計算で代替する判断を採用（`frontend/src/export/agent_task_export.ts:6-18`、`frontend/src/ui/AgentTaskExportPanel.tsx:5-12`のコードコメントに同じ判断根拠が記録されている）。MCP参照も0件。 |
| 9 | `POST /context/bundle` | **(c)** 同上 | 上記と同一根拠。 |
| 10 | `POST /context/bundles:resolve` | **(c)** 同上 | git履歴: "bundles:resolve"文字列に触れたfrontend commitは0件。CE1のクローズ記録が`/context/query`・`/context/bundle`・`/context/bundles:resolve`の3つをまとめて「Backend route contract present」として扱っており（CE1系4routeの一部）、上記と同じmock-first判断の対象。 |
| 11 | `POST /context/v1/bundles:resolve` | **(c)** 同上 | `bundles:resolve`のv1 alias。同一根拠。 |

分類の内訳: (a) 1件、(b) 1件、(c) 9件。

### 対応した処置

- (a)の1件: `issue-DX-CLEANUP-07-ai-suggest-island-summary-route-no-frontend-caller.md`をDraftで新規作成し、route公開自体の削除検討を切り出した（本issueへの参照を含む）。
- (b)の1件: `02_Architecture/api.md` §2.5の`POST /docs/{doc_id}/context-audit`に、外部消費者向けである旨と未結線の既知ギャップを注記した。
- (c)の9件: 本節に分類と根拠を記録済み。追加対応は不要（バックログとして現状のまま）。

### 未解決の不確実性

- `POST /docs/{doc_id}/context-audit`の(b)判定は、実際に呼び出す外部消費者が現時点で1つも存在しない（MCPは意図的に未結線）という点で、厳密な「外部消費者向けに実際に使われている」ではなく「外部消費者向けに設計されており、結線は先送りされている」という状態である。`channel: "gui"`の余地も残るため、将来frontendが呼び出し元になる可能性を完全には排除できない。
- 上記の理由により、本issueのStatusは`Draft`のまま維持する（Acceptanceの3項目自体は充足したと判断するが、判定に残る不確実性を踏まえ、Doneへの遷移はMaintainerの確認を待つ）。
