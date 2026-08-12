# Issue Draft: DX-CLEANUP-07 `POST /ai/suggest-island-summary` routeがfrontend呼び出し元を持たない（削除検討）

- Type: Process
- Status: Done
- Source Issue: `SAAS-TENANT-SURFACE-01`（`issue-SAAS-TENANT-SURFACE-01-unclassified-frontend-caller-gap.md`の分類調査で発見）
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`
- Related ADR/Spec: `issue-DX-CLEANUP-04-unreferenced-canvas-shell-and-client-helpers.md`
- Expected verification level: `integration`

## 課題

- 現在の問題: `POST /ai/suggest-island-summary`（`routes/ai.py:565-569`のroute宣言、handler `suggest_island_summary` は`ai.py:570-585`）は`require_tenant_scoped_api_precondition`で保護されたtenant-guarded routeとして現在も公開されているが、`03_Implement/frontend/src`・`03_Implement/mcp/src`のいずれにも呼び出し元が無い。
- 発見経緯: `issue-SAAS-TENANT-SURFACE-01-unclassified-frontend-caller-gap.md`の分類調査（2026-08-06）で、tenant-guarded backend routeとfrontend `fetch()`呼び出し元を突き合わせた結果、このrouteに対応するfrontend呼び出し元が無いことを確認した。
- 過去の経緯（git履歴で確認済み）:
  1. `60111b5c7aca5a51d15c254133c625801afe8552`（2026-02-15、"Add AI island summary suggestion endpoint and UI action"）でbackend routeとframework wrapper `suggestIslandSummary`（`api/client.ts`）、およびUI action（呼び出し元）が同時に追加された。
  2. `b65d24d785f3a042f7cfb1a102f58721aff08c14`（2026-07-20、"refactor(frontend): remove replaced focus and summary helpers"）で、UIがproposal-only経路（`proposeIslandSummary` / `POST /ai/proposals/island-summary`）へ置き換わったことに伴い、frontend側の直接呼び出し用wrapper `suggestIslandSummary`とその専用型`SuggestIslandSummaryResult`が`api/client.ts`から削除された（`03_Implement/frontend/src/api/client.ts`で45行削除）。この経緯は`issue-DX-CLEANUP-04-unreferenced-canvas-shell-and-client-helpers.md`（Status: Done）に記録されている。同issueの対応方針は「UIはproposal-onlyの`proposeIslandSummary`と`POST /ai/proposals/island-summary`を使用する。backendの旧route関数はproposal endpoint内部から再利用されているため維持するが、直接呼出し用frontend wrapperは置換済みである」であり、**backendのroute自体の扱いはそのIssueのスコープ外として維持されたまま**だった。
- 現状: `suggest_island_summary`関数自体は死んでいない。`propose_island_summary`（`ai.py:593`、route `/ai/proposals/island-summary`）がPython関数として直接呼び出しており（`ai.py:594`: `summary_result = suggest_island_summary(SuggestIslandSummaryRequest(doc=payload.doc, islandId=payload.islandId))`）、これは現在frontendから実際に呼ばれている経路（`proposeIslandSummary` wrapper、`App.tsx`で使用）の内部実装である。死んでいるのは**HTTP route `POST /ai/suggest-island-summary`自体の外部公開**であり、関数の再利用ではない。

## 対応方針

- 実施すること（提案。最終判断はMaintainer）: `@router.post("/suggest-island-summary", ...)`のroute宣言（`ai.py:565-569`とそのdecorator対象である`def suggest_island_summary(...)`のHTTP公開経路）を削除するかどうかを決定する。削除する場合は次の2案のいずれかを取る。
  - 案A: `suggest_island_summary`を通常のPython関数（非route）へ変更し、`propose_island_summary`からの内部呼び出しのみを残す。
  - 案B: routeを維持しつつ、`02_Architecture/api.md`等の正本文書に「未使用だが後方互換のために維持」である旨を明記する。
- 実施しないこと: `suggest_island_summary`関数本体の削除、`propose_island_summary`・`POST /ai/proposals/island-summary`の変更、`SuggestIslandSummaryRequest`/`SuggestIslandSummaryResponse`モデルの変更。

## 受入条件

- [x] `POST /ai/suggest-island-summary`のHTTP route公開を維持するか削除するかをMaintainerが決定する。— **案B（維持）を仮承認で採択**（ドッグフーディングループの仮承認方針。否認・補正可）。関数は proposal route の内部実装＋SEC-LLM-AUDIT-01 の監査配線済みで削除しない。
- [ ] 削除する場合、`03_Implement/backend/tests/`内でこのrouteをHTTP経由で直接検証しているテスト（`propose_island_summary`経由の間接テストとは区別する）を洗い出し、削除または`propose_island_summary`経由のテストへ統合する。— 削除しないため該当なし。
- [ ] 削除する場合、このrouteのpathを直接参照している既存文書（例: `02_Architecture/ai-prompt-core-redesign-2026-07-23.md:15`）の追随更新が必要か確認する。— 削除しないため該当なし。
- [x] 維持する場合（案B）、`api.md`に維持理由を記録する。— `api.md` §446 に「後方互換・外部APIクライアント用に維持」を追記（DX-CLEANUP-07 案B）。

## 検証計画

- 実行する確認: 削除する場合、`python -m pytest -q 03_Implement/backend/tests/ -k "island_summary"`で`propose_island_summary`経由の既存契約が非回帰であることを確認する。frontend側は`suggestIslandSummary` wrapperが既に存在しないため、frontend側の追加確認は不要。
- 期待結果: `POST /ai/proposals/island-summary`の既存の挙動・契約（`ProposalEnvelope`、`SuggestIslandSummaryResponse`のgroundingIds検証等）が変化しない。

## 補足

- 発見経緯: `issue-SAAS-TENANT-SURFACE-01-unclassified-frontend-caller-gap.md`の分類調査、2026-08-06。同issueは`(a)死んだコード`（過去に呼び出し元が存在し、frontend側の実装変更で消えたもの）としてこのrouteを分類し、本issueへの切り出しを提案している。
- 本issueはbackendのroute宣言のみを対象とし、削除するかどうかの製品判断はMaintainerに委ねる（`issue-SEC-DOC-BOUND-05`等、同種の「機械的に対応しない」判断パターンに倣う）。
