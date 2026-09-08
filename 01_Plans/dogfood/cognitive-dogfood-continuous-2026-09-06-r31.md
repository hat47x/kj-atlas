# 継続dogfood R31 — componentの有効値とdeployment profileで実現可能な値を分ける

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: 公開設定値がコンポーネント単体では有効でも、実際のdeployment topologyでは実現できない場合、どの層で契約を狭めるべきか。
- Canvas: `doc_kj_atlas_dogfood_r31.json`
- Observation baseline 1: PR #3019 / merge commit `e3a9938c3a6e7a7889859620ef37fdafddc694a9`
- Observation baseline 2: PR #3021 / merge commit `16030ed3cedea717cc61aac626665ea40112a6d1`
- Result class: frontend値境界と標準Compose配送面で実際に観測された2段の契約seamを修正した運用上の陽性。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. 「slashで始まる」と「same-origin path」は同じではなかった

`KJ_ATLAS_FRONTEND_API_BASE` は公開契約上pathとして扱われていたが、PR #3019以前のmain/admin両resolverは `startsWith("/")` を主な受理条件としていた。

この判定では `//example.invalid/api` のようなnetwork-path referenceも通る。ブラウザのURL解釈ではこれは別originを指し得るため、文字列の先頭形状はpathらしく見えても、設定が意図していたsame-origin pathという意味境界を越えられた。

またmain API clientとadmin model allowlist clientが別々にresolverを持っていたため、安全境界自体も二重化していた。

PR #3019は共有 `resolveFrontendApiBase()` へ統合し、same-origin absolute pathとして解釈できる値だけを受理する契約へ戻した。

- `/api`, `/nested/api`, `/` は受理する。
- trailing slashは正規化する。
- network-path reference、backslash、query、fragment、relative path、control characterは `/api` へfail-safeする。
- `/` は内部prefixを空文字として扱い、後続pathとの結合で `//docs` 等を作らない。

ここでの所見は、**字面のpredicateが意味型を十分に表しているとは限らない**ことである。

## 2. componentで有効でも標準Composeでは実現できなかった

#3019によってfrontend component自身は複数のsame-origin absolute pathを安全に扱えるようになった。しかし配送面を追ったPR #3021では、標準Composeに別のseamが残っていた。

標準Composeはhostの `KJ_ATLAS_FRONTEND_API_BASE` をweb build argへ渡していた。一方、同梱Nginxがbackendへproxyするのは `location /api/` だけだった。

したがってhostで `/custom` を指定すると、値は#3019のcomponent contract上は有効でfrontendへも届くが、frontendは `/custom/...` へ要求する一方で標準Nginxはそこをbackendへ配送しない。**設定値はvalidでdeliveryにも成功するのに、packaged topologyでは機能しない**状態になる。

PR #3021は標準Composeのweb build argを `/api` に固定した。別pathを使う能力そのものはfrontend Dockerfileの直接build契約として残し、その場合は対応するreverse proxyも同時に構成するよう文書化した。

つまり一般componentの能力を削ったのではなく、標準deployment profileが実際に実現できるsubsetへ契約を狭めた。

## 3. KJ統合で立った中心構造

今回の中心は次にまとまる。

> **設定値の契約は、component境界での意味的validityと、deployment profile境界での実現可能性を分けて守る。**

同じ値について二つの問いがある。

1. **この値はcomponentが安全かつ意味どおりに解釈できるか。**
2. **このdeployment profileは、その値をend-to-endで実現できるか。**

#3019は1を閉じ、#3021は2を閉じた。1がgreenでも2は自動的にはgreenにならない。

この構造はR29/R30とも接続する。R29は複数層の契約値が意味まで一致すること、R30は同一surface内の宣言点を一意にすることを扱った。R31ではさらに、**値が一致して一意に配送されても、その値が受け手のtopologyで実現可能とは限らない**ことを分離する。

## 4. Finding triage

### F0 — 生の観察として保持

- PR #3019以前は `startsWith("/")` によりnetwork-path referenceをsame-origin pathとして受理し得た。
- main/adminに別resolverがあり、同じ安全境界が二重化していた。
- PR #3019で共有resolverとsemantic validationへ戻した。
- PR #3021以前の標準Composeはhost指定の有効なsame-origin pathをfrontendへ配送できたが、同梱Nginxは `/api/` 以外をbackendへproxyしなかった。
- PR #3021で標準Composeを `/api` に固定し、直接buildの一般能力とは分離した。

### F1 — 既存の局所contractへ返す

- frontend componentの値境界は共有resolverのsame-origin path contractを正とする。
- standard Composeは同梱Nginx topologyと一致する `/api` を正とする。
- custom same-origin path能力は直接frontend build + 対応reverse proxyを構成する利用形態に残す。

### F2 — 新Issueなし

観測した2段のseamは#3019/#3021で修正・回帰固定済みであり、独立した未完作業を残していない。

### F3 — ADRなし

新しい製品architectureを決めたのではなく、既存公開設定と標準deploymentの実態を一致させた契約修復である。

## 5. profile別制約を一般能力へ逆輸入しない

標準Composeが `/api` 固定だからといって、frontend component全体を `/api` だけに制限するのは過剰である。直接buildと独自reverse proxyを組み合わせれば、別のsame-origin absolute pathを正しく実現できる。

逆に、componentが `/custom` を安全に解釈できるからといって、標準Composeもその値をhost overrideで受けるべきだとは限らない。

したがってcontractはcapabilityの最小共通部分へ潰すのではなく、**component capabilityとpackaged profileのrealizable subsetを別に表現する**。

## 6. 実証境界と次工程

R31はcurrent repositoryのfrontend/deployment contract監査から得た内部所見であり、formal Case 001 Arm Cの結果ではない。第三者価値実証、AI-IR named-provider evidenceにも加算しない。

この記録を理由に新しいpreflight、KPI、実験スキーマは追加しない。新しい具体的な陽性が出なければ、formal mainlineは既知仮説から隔離したfresh contextとfrozen KJ Atlas UIでのCase 001 Arm C実走へ戻る。
