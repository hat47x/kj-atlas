# 継続dogfood R34 — 文書契約のshapeに応じて実行可能な正本照合を選ぶ

Date: 2026-09-07
Canvas: `doc_kj_atlas_dogfood_r34.json`

## 1. Trigger

R33統合後のmainで、公開文書・runtime registry・ADRに残ったcurrent factのdriftが、異なるshapeで連続して実際に修正された。

- PR #3030: `configuration.md` の標準Compose配送説明が現行 `docker-compose.yml` と逆転していた。文書は `DATABASE_URL` / `LLM_PROVIDER` の2 keyだけが `api` に届くとしていたが、実装はruntime profile、DB URL、LLM provider、app revision、API key、JIT provisioning等を配送していた。さらに標準Composeでは `/api` 固定なのにhost exportで変更可能に見える例が残っていた。
- PR #3031: public enum集合に意味driftがあり、`LLM_PROVIDER` は実装が受理する `deepseek` を文書だけ欠落させ、`LOG_LEVEL` は実装が正式値としない `NOTSET` を文書だけ正式値として列挙していた。
- PR #3032: document policy binding / tenant capability resolverはtrusted SaaS runtimeへ既に構築・preflight・配線されていた一方、registry / configurationには「未配線」が残っていた。
- PR #3033: ADR-0063は `TRUSTED_PROXIES` を未実装gapとして複数箇所に残していたが、実際には同ADR起票と同一commitで `_check_trusted_proxy()` が実装され、`resolve_identity_context()`の先頭で呼ばれていた。専用回帰testも無かった。

これらは全て「文書が実装に追従していなかった」という一語では似ている。しかし、同じ検査で守れる対象ではない。

## 2. KJで分けて見えたもの

### A. 配送面はkey集合とprofile境界で照合する

#3030では、標準Composeの `api.environment` / `web.build.args` という明示的な配送面がある。ここで必要なのは説明文の単語検索ではなく、文書が公開するkey集合と実Compose定義のkey集合を比較することだった。

また `KJ_ATLAS_FRONTEND_API_BASE` はdirect frontend buildでは入力能力を持つが、standard Composeでは同梱Nginxと整合させて `/api` に固定される。R31で分けたcomponent capability / deployment-profile realizabilityが、利用者文書の配送表にも同じ境界として現れた。

### B. enum契約は集合として比較する

#3031の `deepseek` 欠落と `NOTSET` 誤列挙は、key存在やdefault値一致だけでは検出できない。public contractが有限の許容集合を宣言するなら、implementationが静的に持つ受理集合とpublic表を集合として厳密比較する必要がある。

一方、長い説明文全体をenum grammarへ変換することはしていない。厳密比較は「public表として明示された有限集合」と「静的に読めるimplementation」の交差部分に限定されている。

### C. wiring stateは構築・preflight・dataflowを追う

#3032の「未配線」は文字列だけを直しても再発し得る。current factの正本は、resolver builderがcomponent bundleへ入ること、trusted SaaS preflightがexternal componentを要求すること、document bindingがresource resolverへ渡ること、tenant capabilityがruntime stateへ届くこと、というruntimeのdataflowである。

したがってwiring stateは単一booleanやstatus語ではなく、必要な接続経路を狭く実行可能contractへ落とすのが適切だった。

### D. ADRの事実前提とdecisionは分けて訂正する

#3033では、`TRUSTED_PROXIES`未実装という事実前提は誤っていたが、ADR-0063 D2の「SaaSではheader modeを拒否しJWT検証を必須にする」というdecisionは維持された。CIDR設定ミスによる全tenant越境リスクと、暗号的証拠なしにverified claimを名乗れない点は、TRUSTED_PROXIESの実装有無から独立していたためである。

ここでは過去のADR本文をcurrent-state文書へ単純置換するのではなく、dated correctionで事実前提を訂正し、decision rationaleのどこが依存しどこが独立しているかを残した。同時に、既存 `_check_trusted_proxy()` に専用回帰testを加え、文書訂正だけで終わらせなかった。

## 3. 中心所見

**文書にcurrent contractを複製する必要があるなら、文字列の存在を守るのではなく、そのcontractのshapeに対応する実行可能な正本照合を持つ。**

今回観測したshapeは少なくとも次のように異なる。

- scalar/default → 値一致
- finite enum → 集合一致
- delivery surface → key集合 + profile境界
- wiring state → construction / preflight / dataflow
- ADR factual premise → 実装behavior + dated correction、decisionとの依存分離

これは「すべての文書をコード生成する」という話ではない。current factを利用者や設計判断のために文書へ載せる必要がある箇所だけ、その事実の種類に合う狭いconformance contractを選ぶ。

## 4. R28〜R34の境界

- R28: 不要な可変state複製はnavigationから正本へ戻す。
- R29: 必要なscalar/default複製は意味値まで合わせる。
- R30: 同一authority / delivery surface内の宣言点は一意にする。
- R31: component validityとdeployment-profile realizabilityを分ける。
- R33: canonical意味一致と必要observability surfaceへの伝播を分ける。
- R34: 文書へcurrent factを載せる必要がある場合、contract shapeごとに照合する実装正本と検査方法を選ぶ。

したがってR34はR28の反対ではない。消せる第二正本は消し、残す必要がある契約複製だけをshape-awareに実行可能化する。

## 5. Finding triage

- F0: #3030〜#3033で実際に観測されたdelivery / enum / wiring / ADR factual premiseのdrift。
- F1: 既に各PRで追加されたfocused contractと回帰testへ所見を戻す。
- F2: 新Issueなし。generic docs-schemaやrepository-wide parserを追加しない。
- F3: 新ADRなし。#3033は既存ADRの事実訂正でありdecision変更ではない。

## 6. 非主張

R34はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、AI-IR named-provider evidence、第三者product-value validationを代替しない。

formal P1の現在地は変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
