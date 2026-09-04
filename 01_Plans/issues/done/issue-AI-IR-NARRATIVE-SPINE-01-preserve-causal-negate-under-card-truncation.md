# Issue: AI-IR-NARRATIVE-SPINE-01 文章生成の因果・対立骨格をカード切り詰めで失わない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug / AI Input Projection
- Status: Done
- Source Issue: `AI-IR-SCALE-01`, `AI-IR-PROJECTION-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/tests/test_ai_route_required_meaning_scale.py`, `03_Implement/backend/tests/test_ai_generate_narrative_ir_scale.py`
- Related ADR/Spec: `ADR-0069`, `02_Architecture/llm_input_ir_spec.md` §2.3 / §5.2.1, `AI-IR-PROJECTION-01` AC-3, `AI-IR-SCALE-01`
- Expected verification level: integration

## 課題

`generate-narrative` では、読み順（`readingOrder`）だけでなく、カード間の `causal` / `negate` を文章化の論理骨格として扱うことを `AI-IR-PROJECTION-01` AC-3で定めている。

小規模な文書ではこの契約を満たしている。しかし300カード規模では、`MAX_CARDS=200` による切り詰めによって、読み順の項目自体はDocument由来の経路から最終プロンプトに残る一方、その項目を結ぶ `causal` / `negate` の端点カードがIRから除外される場合がある。端点が除外されると、参照整合を保つため、その関係もIRから除外される。

その結果、モデルには「何がどの順序で並んでいるか」は見えても、「何が何を引き起こし、どこで見立てが対立しているか」というB型文章化の関節が届かないまま、文章生成を依頼し得る。

## 決定論的な再現条件

既存の `measure_ai_route_required_meaning.py` と `test_ai_route_required_meaning_scale.py` に `narrative-late-causal-negate` シナリオがあるため、再現器は増やさない。

代表シナリオでは次の状態を固定している。

1. `c000`〜`c299` の300カードと30島を持つ。
2. 読み順には末尾の島 `i29` も含まれる。
3. 後半カードに `c298 --causal--> c299` を置く。
4. `c299 --negate--> c000` を置く。
5. 通常の中心性による選択では `c298` / `c299` が200枚の外に出る。
6. 修正前は `i29` が最終プロンプトに残る一方、上記2関係はIRと最終プロンプトから失われる。

これは「IRにある情報をすべての経路へ渡したい」という一般論ではない。#2831で整理した経路ごとの必要意味集合に照らすと、`generate-narrative` にとって `causal` / `negate` はAC-3が明示した必須意味であり、その欠落だけを対象とする。

## 対応方針

R18で導入した入力専用の `required_card_ids` を、`generate-narrative` の契約に合わせて再利用する。

`_generate_narrative_ir()` は、`source_from_document(payload.doc)` で得たsource relationのうち、IRへ正規化可能なcard-to-card `causal` / `negate` の両端点をrequired cardとして扱う。

具体的には、次の境界を守る。

1. `type in {causal, negate}` の関係だけを文章生成の必須骨格とする。
2. `from_kind == island` または `to_kind == island` の辺はrequired cardの根拠にしない。島間辺は従来どおりDocument由来で最終プロンプトへ渡す。
3. 存在しないカードを参照する辺はrequired集合へ入れない。IR §2.3の正規化境界と一致させる。
4. required集合はカードID昇順で決定論的に作る。
5. required cardを先に確保し、残りの枠だけを既存のcentrality順で埋める。
6. `related` だけを理由にカードをrequiredへ昇格しない。
7. required cardだけで `MAX_CARDS` を超える場合は、既存の `required_card_budget_exceeded` で停止する。不完全な論理骨格を黙ってLLMへ渡さない。

## 実装状況（2026-09-03）

作業ブランチ `fix/r20-narrative-spine-preservation-20260903` で、次の実装を追加した。

- `_narrative_required_card_ids()` を追加し、正規化可能なcard-to-card `causal` / `negate` の端点だけを決定論的に抽出する。
- `_generate_narrative_ir()` がこの集合を `required_card_ids` として共有IRビルダーへ渡すようにした。
- `MAX_CARDS`、`MAX_RELATIONS`、`MAX_TEXT_CHARS` の値は変更していない。
- `suggest-layout` の未解決なscale課題には触れていない。

GitHub Actionsは現在リポジトリ側で無効化されているため、CI成功は完了条件として扱わない。ただし、実行可能な環境で回帰テストを一度通した記録は、完了時に残す。

## 受入条件

- [x] `narrative-late-causal-negate` の300カードシナリオで `c298 --causal--> c299` がIRに残る。
- [x] 同シナリオで `c299 --negate--> c000` がIRに残る。
- [x] 上記2関係が最終プロンプトの `Logical relations` と、読み順上のspine表示の双方に残る。
- [x] 読み順の末尾島がDocument由来で見えるという既存挙動を変えない。
- [x] `related` のみを持つカードは、本Issueだけを理由にrequired cardへ昇格しない。
- [x] island-to-island edgeをrequired card集合の根拠にしない。
- [x] 存在しないカードを参照するrelationをrequired card集合の根拠にしない。
- [x] requiredとなるdistinct cardが `MAX_CARDS` を超える場合は `422 / required_card_budget_exceeded` でLLM呼び出し前に停止する（共有IRビルダーの既存fail-closed経路を再利用）。
- [x] source relationの並び順に依存せず、同じDocumentから同じrequired集合を得る（`_narrative_required_card_ids()` はsorted tupleを返す決定論的実装）。
- [x] SafeMode二層、PII最小化、`MAX_CARDS` / `MAX_RELATIONS` / `MAX_TEXT_CHARS` の値を変更しない。
- [x] `suggest-layout` の未解決なscale課題を本Issueの完了として扱わない（`AI-IR-SCALE-01` に残したまま）。
- [x] 実行可能な環境で、追加したscale回帰が成功することを記録する。

## 対応記録（2026-09-04・Done）

`fix/r20-narrative-spine-preservation-20260903` の実装（`_narrative_required_card_ids()` および `_generate_narrative_ir()` への配線、`03_Implement/backend/src/kj_atlas_api/routes/ai.py:605-666`）は、その後の一連のPRを通じてすでに `main` へ統合済みだった（`git merge-base --is-ancestor` で確認、ブランチ自体はmainの祖先）。本issueのAC欄だけが未更新のまま残っていたため、実装内容をAC全項目と突き合わせて確認し、下記の回帰を実行して整合を確認した。

```
.venv\Scripts\python.exe -m pytest tests/test_ai_route_required_meaning_scale.py tests/test_ai_generate_narrative_ir_scale.py -q
9 passed in 12.43s
```

`_narrative_required_card_ids()` の実装は、causal/negateのみを対象化・island端点の除外・存在しないカード参照の除外・sorted tupleによる決定性をすべて満たしており、AC本文の境界条件と一致する。budget超過時のfail-closedは共有IRビルダー（`required_card_ids` 引数）の既存経路をそのまま再利用しており、narrative固有の別実装は追加していない。

## 完了境界

本Issueは、`MAX_CARDS` によるカード除外が原因で `generate-narrative` の `causal` / `negate` 骨格を失う経路だけを扱う。

`MAX_RELATIONS` を超えるほど多数の必須relationがある文書で、どのrelationを保持・分割するかは本Issueでは決めない。token予算、batch / hierarchical projection、relation単位の予約を含め、`AI-IR-SCALE-01` の残課題として扱う。

同様に、`suggest-layout` で全カードの相対座標、relation、島間relationをどのように保持するかも `AI-IR-SCALE-01` に残す。
