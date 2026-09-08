# Issue: DOGFOOD-33 `suggest-island-summary` を複数候補（candidates）へ拡張し、接地/凝縮を分離する

- Type: Feature / Contract change（W型探求・R5具体策/R6手順計画で検出、ADR-0077 で決定）
- Status: Done
- Source Issue: W型KJ法探求（2026-08-17〜18）の第5ラウンド（具体策）「凝縮具体策」および第6ラウンド（手順計画）Phase 1。凝縮（核融合法）の第一級化の第一歩。
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models_ai.py`（`SuggestIslandSummaryResponse`）, `routes/ai.py`（prompt/parse/propose）, `03_Implement/deploy/tools/mock_local_llm.py`, `02_Architecture/api.md`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`, 関連テスト
- Related ADR/Spec: `01_Plans/adr/ADR-0077-island-summary-condensation-multiple-candidates.md`, `00_Prompt/kj_technique.md` §3（表札検査）, `00_Prompt/ai_kj_execution_procedures.md` §3（代弁文）
- Expected verification level: `unit` + `e2e`

## 課題

現行の `POST /ai/suggest-island-summary` は単一の `summaryText` + `groundingIds` を返し、接地（代表カード≤10）と凝縮（志）が「唯一の答え」として一体に返る。W型探求の結論は「凝縮（核融合法）は単発の自動採否ではなく、複数候補・代替候補・チャット壁打ちで対話的に収束するのが最適」であり、その土台として**複数候補（`candidates`）の提示と接地/凝縮の分離**が必要。

- 現状: `SuggestIslandSummaryResponse = { summaryText, groundingIds, warnings }`（接地と凝縮が混在）。
- 目標: `SuggestIslandSummaryResponse = { candidates: [{ summaryText, groundingIds }×1〜3], warnings }` へ一本化。

## 三要素分析（ADR-0067）

ADR-0077 の Three-Element Verification を踏襲（業務: 人間が志を adopt ／データ: 候補単位で接地/凝縮を分離、接地は代表カード≤10・メンバー限定 ／機能: candidates 返却、proposal は candidates[0] を diff へ写す）。

## 対応方針

- 実施すること:
  1. `models_ai.py` に `_IslandSummaryCandidate`（`summaryText` + `groundingIds`≤10）を追加し、`SuggestIslandSummaryResponse` を `candidates: list[_IslandSummaryCandidate]`（1〜3件）+ `warnings` に変更。
  2. `routes/ai.py` の `_build_island_summary_prompt`（出力スキーマを candidates 形式へ）、`_parse_island_summary_response`（**候補ごとに**接地≤10・重複なし・メンバー限定を検証）、`propose_island_summary`（`candidates[0]` を ProposalDiff へ写す）を更新。
  3. `mock_local_llm.py` の `suggest_island_summary` を複数候補（3件）返却へ変更。候補[0]の接地は既存 E2E の `groundingIds` 部分一致を維持（メンバーID順）。
  4. `api.md` の `SuggestIslandSummaryResponse` 記述を更新。
  5. `verify_business_flow_e2e.sh` の 3d に `candidates` 複数候補の固定を追加（既存 `groundingIds` 部分一致は候補[0]に一致し続ける）。
  6. 関連テスト（`test_llm_integration.py`・`test_kj_session_e2e.py`・`test_ce2_proposal_api.py`）の直下フィールド参照を更新し、候補ごとの接地検証テストを追加。
- 実施しないこと:
  - ProposalDiff の形状変更（`after`/`groundingIds` は維持。複数候補の UI 選択は Phase 2「壁打ち」で扱う）。
  - 壁打ちチャットUI（Phase 2）、`parentIslandId` CRUD（Phase 3・DOGFOOD-32）、複層キャンバス分離（並行ADR）。
  - 接地の10件上限（品質ガード）の撤回。

## 受入条件

- [x] `suggest-island-summary` が `candidates`（1〜3件）を返し、各候補が `summaryText` + `groundingIds` を持つ。
- [x] 各候補の接地が ≤10・重複なし・対象島メンバー限定で検証される（旧形式 `summaryText` 単独は 422 で拒否）。
- [x] `propose_island_summary` が `candidates[0]` を diff へ写し、proposal-only・human_reviewed が維持される。
- [x] E2E（`verify_business_flow_e2e.sh`）で `candidates` 複数候補が固定され、既存 `groundingIds` 接地固定が壊れない。
- [x] バックエンドの unit テスト（prompt/parse/integration/kj_session）が全て通過する。

## 補足

- 本issueは凝縮（核融合法）のロードマップ Phase 1（凝縮具体策）の実装。Phase 2（壁打ち）、Phase 3（多段）は後続issue/ADR。
- モデル分業（ADR-0065）: flash が複数候補の初期生成、pro が深い凝縮・代替候補。本issueではスキーマ変更に注力し、flash/pro のルーティング適用は `resolve_model_for_task("suggest_island_summary")` の既存経路に委ねる。


## 配置の整理（2026-09-05）

- 本Issue群は、島要約の凝縮支援を単一候補から複数候補へ拡張し、違和感を踏まえた再生成、さらに採用時の critique / reproposal 履歴永続化まで段階的に完成させた機能契約成熟系列として `Done` となっていた。
- `DOGFOOD-33` が複数候補と候補単位の接地検証、`DOGFOOD-34` が違和感入力を受けた再生成と代替候補採用、`DOGFOOD-35` が採用理由・再提案差分の文書永続化を完成させたため、3件を同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は17から14へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
