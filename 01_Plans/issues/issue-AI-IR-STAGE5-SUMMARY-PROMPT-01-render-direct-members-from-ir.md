# Issue: AI-IR-STAGE5-SUMMARY-PROMPT-01 表札候補の直接メンバー本文をIRから描画する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Defect / AI Input Boundary
- Status: Open
- Source Issue: `AI-IR-PROJECTION-01` Stage 5 / `AI-IR-STAGE5-SCOPE-01`
- Source PR: #2838
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/island_summary_ir.py`, `03_Implement/backend/tests/test_ai_island_summary_ir.py`
- Expected verification level: integration

## 課題

PR #2838で `suggest-island-summary` は `LLMRequest.inputs` にLLM投入IRを持つようになり、対象島と直接隣接する意味だけをIRへ縮約した。しかし、現行providerは `LLMRequest.inputs` 自体をtransportへ送らず、実際にモデルへ送るのは `prompt` である。

現在のrouteは、最初に `_build_island_summary_prompt(payload)` を呼び、対象島の直接メンバーカード本文を `payload.doc` から描画する。その後でIR contextを構築し、IR由来の島構造・relation・evidenceをpromptへ追記している。

そのため、**構造文脈はIRから描画される一方、表札生成の中心となる直接メンバー本文はDocumentからpromptへ直接流れている**。`LLMRequest.inputs` は監査上の入力記録にはなっているが、直接メンバー本文については「IRがAI入力の実経路である」という境界をまだ満たしていない。

SafeMode、PII最小化、`required_text_truncated` 等はprovider呼出前のゲートとして機能するため、この欠陥はそれらを無効化するものではない。ただし、IRで行う本文正規化と、providerが実際に受け取る本文が一致しない状態は残る。

## 対応方針

直接メンバーの**本文**はIRから描画する。既存の仕事上の順序、task-local入力、応答契約は維持する。

- `_build_island_summary_prompt` の既存表札検査、空島検査、`critiqueTags` / `critiqueText`、明示的なisland-to-island edgeは維持する。
- 直接メンバーカードの表示順が現在の `island.cardIds` に依存している場合、その順序はtask-local情報として維持してよい。
- 各カードの本文は `ir_context.ir["cards"]` の同一IDから取得し、`payload.doc` の生本文をprovider promptへ再描画しない。
- 外部隣接カードは引き続き文脈専用とし、`groundingIds` の許可範囲を広げない。
- request / response、proposal-only、人間の最終判断権、SafeMode二層は変更しない。
- IRに存在しない直接メンバーがあれば、既存のfail-closed境界に従ってproviderを呼ばない。

## 回帰で固定すること

1. IR正規化で本文が変わる入力を使い、providerへ渡るpromptの直接メンバー本文がIR側の本文と一致する。
2. 同じ入力で、Document側の生本文がprovider promptへ残らない。
3. `LLMRequest.inputs` の直接メンバー本文とprompt上の直接メンバー本文が一致する。
4. 既存のdirect-member-only `groundingIds` 検証を維持する。
5. `critiqueTags` / `critiqueText` と明示的なisland-to-island edgeを失わない。
6. route側SafeModeとIR側SafeModeの二層を維持する。
7. 既存の表札prompt回帰とproposal-only経路を壊さない。

## 完了条件

- [ ] 直接メンバー本文をIRからprovider promptへ描画する。
- [ ] Document側の生カード本文が同じ箇所へ迂回して送られないことをintegration regressionで固定する。
- [ ] `LLMRequest.inputs` とpromptの直接メンバー本文一致を固定する。
- [ ] 既存の表札prompt / SafeMode / proposal-only回帰を実行して成功を確認する。
- [ ] `02_Architecture/api.md` に「直接メンバー本文もIRから描画する」境界を同期する。

## 非目標

- provider transport自体に `inputs` を別フィールドとして送ること。
- `critiqueText` やreading order等のtask-local入力をgeneric Document IRへ無理に移すこと。
- Stage 5の他経路を同時に変更すること。
