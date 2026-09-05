# Issue: DOGFOOD-34 島表札の壁打ち — 違和感を踏まえた代替候補の再生成

- Type: Feature / API contract change（W型探求・R5具体策/R6手順計画で検出、Phase 2）
- Status: Done
- Source Issue: W型KJ法探求（2026-08-17〜18）の第5ラウンド「壁打ち具体策」および第6ラウンド Phase 2。凝縮（核融合法）の「志」を対話的に収束する導線の第一歩（ADR-0077 の後続）。
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models_ai.py`（`SuggestIslandSummaryRequest`/`ProposeIslandSummaryRequest`）, `routes/ai.py`（prompt）, `03_Implement/deploy/tools/mock_local_llm.py`, `02_Architecture/api.md`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`, 関連テスト
- Related ADR/Spec: `01_Plans/adr/ADR-0077-island-summary-condensation-multiple-candidates.md`, `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`（DOMAIN-EXPR-03 違和感→再提案）, `02_Architecture/schemas.md`（`CritiqueInput`/`ReproposalDiff`）, `00_Prompt/kj_technique.md` §3（戻し検査）
- Expected verification level: `unit` + `e2e`

## 課題

W型探求の結論は「凝縮（核融合法）の『志』は単発の自動採否ではなく、複数候補・代替候補・チャット壁打ちで対話的に収束するのが最適」。Phase 1（ADR-0077）で複数候補（`candidates`）は返せるようになったが、**ユーザーが違和感を言語化して代替候補を再生成する導線が API に無い**。

- 現状: `suggest-island-summary` は候補を返すが、ユーザーの違和感（「この表現は強すぎる」「Aカードの意図が抜けている」等）を入力して再生成できない。
- DOMAIN-EXPR-03（違和感→再提案）はデータモデル（`CritiqueInput`/`ReproposalDiff`）が schemas.md にあるが、島表札の凝縮に特化した対話的再生成の導線が未実装。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は島の表札候補を見て違和感（志が違う・カードの意図が抜けている等）を言語化し、AIに「その違和感を踏まえた代替候補」を再生成させ、対話的に収束して**人間が adopt** する。AIは自動適用しない | 機能: 違和感をリクエストで渡し、プロンプトへ反映して代替候補を再生成する。データ: 違和感はリクエスト内の一時入力であり、文書へ自動保存しない |
| **データ設計** | 違和感は `critiqueText`（任意・一時）としてリクエストで渡す。永続化する `CritiqueInput`（schemas.md）とは別で、対話履歴の永続化は後続（st2-04）で扱う | 業務: 志の確定は人間の adopt のみ。機能: 違和感テキストは SafeMode の未レビュー本文送出の対象外（人間自身の発話） |
| **機能設計** | `SuggestIslandSummaryRequest`/`ProposeIslandSummaryRequest` に任意 `critiqueText` を追加し、`_build_island_summary_prompt` が違和感を「戻し検査」の延長として反映して代替候補を生成する。既存 proposal フロー（proposed→unreviewed→adopt）を再利用 | 業務: proposal-only・human_reviewed の緩和禁止を維持。データ: 接地（≤10・メンバー限定）の検証は候補ごとに維持（ADR-0077） |

## 対応方針

- 実施すること（本issueの最小スライス）:
  1. `SuggestIslandSummaryRequest`/`ProposeIslandSummaryRequest` に `critiqueText: str | None = Field(default=None, max_length=1000)` を追加（加算・後方互換）。
  2. `_build_island_summary_prompt` に違和感ブロックを追加（`戻し検査` の延長として、違和感を踏まえた代替候補を指示）。
  3. `propose_island_summary` が `critiqueText` を `suggest_island_summary` へ渡す。
  4. `mock_local_llm.py` が違和感を検出し、候補文に反映（E2E で固定可能に）。
  5. `api.md`・E2E・テストを更新。
- 実施しないこと（後続issue/Phase 2b）:
  - 島詳細の凝縮チャットパネルUI（フロントエンド）。本issueはバックエンドの再生成導線に注力。
  - 対話履歴の永続化（`CritiqueInput`/`reproposalDiffs` への書き込み、st2-04）。

## 受入条件

- [x] `suggest-island-summary`/`proposals/island-summary` が `critiqueText`（任意）を受け取り、違和感を踏まえた代替候補を返す。
- [x] 違和感なし（`critiqueText` 欠落）では従来挙動（後方互換）。
- [x] 接地検証（≤10・重複なし・メンバー限定）が候補ごとに維持される。
- [x] E2E で「違和感→代替候補再生成」の往復が固定される。
- [x] バックエンド unit テストが全て通過する。

## 補足

- 本issueは凝縮ロードマップ Phase 2（壁打ち）のバックエンド最小スライス。フロントのチャットパネル・対話履歴は Phase 2b として後続。
- モデル分業（ADR-0065）: 違和感に応じた深い再解釈は pro、初期候補は flash。`resolve_model_for_task("suggest_island_summary")` の既存経路に委ねる。
- 追加（2026-08-19・Phase 2b 前提）: `ProposalDiff.candidates`（全候補・1〜3件）を加算し、`propose_island_summary` が `after`/`groundingIds`（=候補[0]）に加えて全候補を返すようにした。UI が代替候補を提示できる前提（`api.md`・frontend `IslandSummaryProposal.diff.candidates` も同期）。チャットパネルUI・対話履歴は引き続き Phase 2b の残。
- 追加（2026-08-19・Phase 2b フロント最小スライス）: `SidePanel.tsx` に候補一覧表示（`diff.candidates`）＋違和感入力＋「違和感を踏まえて再生成」ボタンを追加。`client.ts` の `proposeIslandSummary` が `critiqueText` を受け取り、`App.tsx` の `handleSuggestIslandSummary(critiqueText?)` がパススルー。i18n キー（`side_panel.summary.candidates`/`critique_placeholder`/`regenerate`）を en/ja に追加。tsc typecheck・i18n 整合テスト通過。**残は「代替候補の採用（現状 adopt は候補[0]固定）」と「対話履歴の永続化（`CritiqueInput`/`reproposalDiffs`）」**。
- 追加（2026-08-21・Phase 2b 代替候補の採用）: 候補一覧を選択可能なボタンにし、選択した候補（`selectedIslandSummaryCandidateIndex`）を adopt できるようにした。`onAdoptIslandSummaryProposal(candidateIndex)` / `handleAdoptIslandSummaryProposal(candidateIndex)` に変更し、`diff.candidates?.[index]` を採用（欠落時は `diff.after`/`diff.groundingIds` へフォールバック）。tsc typecheck 通過。**「対話履歴の永続化」は DOGFOOD-35 へ切り出し**（2026-08-21 実装済み・Done）。


## 配置の整理（2026-09-05）

- 本Issue群は、島要約の凝縮支援を単一候補から複数候補へ拡張し、違和感を踏まえた再生成、さらに採用時の critique / reproposal 履歴永続化まで段階的に完成させた機能契約成熟系列として `Done` となっていた。
- `DOGFOOD-33` が複数候補と候補単位の接地検証、`DOGFOOD-34` が違和感入力を受けた再生成と代替候補採用、`DOGFOOD-35` が採用理由・再提案差分の文書永続化を完成させたため、3件を同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は17から14へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
