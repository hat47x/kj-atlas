# Issue: AI-IR-COVERAGE-01 LLM入力IRの経路漏れをCIで検知する

- Type: Test / Architecture
- Status: Done
- Source Issue: AI-IR-PROJECTION-01
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/tests/test_ai_llm_input_ir_coverage.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai_relations.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`
- Expected verification level: `unit`

## 課題

`AI-IR-PROJECTION-01` は、KJ Atlas上で人間が残した関係、根拠リンク、保留、島階層などを、AI入力へ落とさず渡すためのP1課題である。

このIssueの起票時には `routes/ai.py` のプロンプト構築経路を9件として数えていたが、その後の再実測では `routes/ai.py` 10件と `routes/ai_relations.py` 1件の計11件へ増えている。2026-08-31時点では、そのうち4件がLLM入力IRを使い、7件がStage 5の未移行経路として残っている。

この棚卸しを文書上の手作業だけに任せると、新しいAI経路が追加されたときに `LLMRequest.inputs` を持たないまま実装されても、次の再実測まで見逃し得る。既に経路数が9件から11件へ変化した事実そのものが、手作業の一覧だけでは継続的な非後退条件にならないことを示している。

## dogfoodで観察した摩擦

継続dogfood R12では、一次価値から見て `AI-IR-PROJECTION-01` をP1で進める判断が再確認された。続くR13で実装を進めるために現行コードを読み直したところ、Stage 5の残り7経路を数えるために、再び `routes/ai.py` と `routes/ai_relations.py` の `LLMRequest` 呼出しを人手で列挙する必要があった。

問題は「7件を数える手間」そのものではない。人間が構造化した意味をAIへ渡すという一次価値上の境界が、ソースコード上では新規経路の追加時に自動検査されていないことである。

## 対応

`03_Implement/backend/tests/test_ai_llm_input_ir_coverage.py` を追加し、Python ASTで2つのAIルートファイルにある全 `LLMRequest(...)` 呼出しを走査する。

検査では、現行11呼出しを次の二群へ明示的に分ける。

### IR移行済み

- `detect_contradiction`
- `suggest_card_groups`
- `generate_narrative`
- `re_layout`

これらは、すべての `LLMRequest` 呼出しが `inputs=` を持つことを必須とする。

### Stage 5の明示的な残債

- `check_narrative`
- `suggest_merges`
- `suggest_island_summary`
- `propose_opposing_viewpoint`
- `refine_card_text`
- `suggest_document_title`
- `summarize_island_relation`

これらは未移行であることを隠さず、テスト上の明示的な残債として保持する。各経路をStage 5で移行するときは、同じ変更の中で残債集合からIR移行済み集合へ移し、エンドポイント固有の統合テストも追加または確認する。

## 受入条件

- [x] `routes/ai.py` と `routes/ai_relations.py` の全 `LLMRequest` 呼出しがASTで列挙される。
- [x] `task` が文字列リテラルでない呼出しは、棚卸し不能としてテストが失敗する。
- [x] 現行11呼出しの追加・削除が、分類更新なしではテストを通過しない。
- [x] IR移行済み4タスクから `inputs=` が外れた場合にテストが失敗する。
- [x] Stage 5の7タスクは、未移行であることを明示的な集合として保持する。
- [x] Stage 5経路へ `inputs=` を追加しただけではテストを通さず、分類と固有検証の更新を要求する。
- [x] テスト自体はLLM、provider、FastAPIアプリを起動せず、ソースコードだけから決定論的に検査する。

## 非目標

- Stage 5の7経路を本IssueだけでIR化すること。
- IRに含める情報の十分性を、この静的検査だけで証明すること。
- `MAX_CARDS` やtoken予算を変更すること。代表規模での投影損失は並行するAC-10の計測系で扱う。
- `ADR-0069` の意味やStage 5の順序を変更すること。

## 検証

- `pytest tests/test_ai_llm_input_ir_coverage.py -q`
- backend CI
- 既存のdocs contract / design consistency / contract drift検査

この検査は「`inputs=` があるから意味が十分に保存される」とは判定しない。各経路が必要なIR情報を実際に使うことは、Stage 1〜4と同様にエンドポイント固有の統合テストで固定する。

## ロールバック

ASTでの検査が将来の実装形態と合わなくなった場合は、同等以上に強い経路被覆検査へ置き換える。手作業の経路数だけへ戻すことは、同じ漏れを再発させるためロールバック先としない。

## 文書品質の仕上げ

課題、対応、受入条件を固めた後、意味を変えずに全文を読み直した。識別子やコード上の語は必要な箇所だけ英語のまま残し、日本語だけでも「何を守る検査なのか」と「何を証明しないのか」が追えるように整えた。
