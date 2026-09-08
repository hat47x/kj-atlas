# 継続dogfood R38 — 受入不変条件とfixture / harness前提を分ける

Date: 2026-09-07
Canvas: `doc_kj_atlas_dogfood_r38.json`

## 1. Trigger

R37統合直前にmainへ入ったPR #3054のCompose-backed E2E再検証で、受入確認そのものに2種類の実陽性が観測された。

- clean PostgreSQLで `/api/healthz` はgreenだったが、既存runbookが固定document `doc_phase1_canvas` の事前seedを前提にGETしたため404になった。ADR-0019の標準Compose最小受入は固定サンプルの存在ではなく、healthと実PostgreSQL保存経路のdocument roundtripであるため、これは製品故障ではなく **受入oracleが契約外fixtureへ依存していたfalse negative** だった。
- それ以前の検証runではfrontend subtreeだけを `/tmp` へコピーしてVitestを実行し、repository-relative fixtureを失ったため失敗した。repository tree全体を保持して同じ対象を再実行するとgreenになり、これは **harnessが依存closure / repository topologyを変えたことによる偽失敗** だった。

#3054は前者に対し、毎回一意な合成 `DocumentV1` を作成してPUT→GETし、payloadとETagの一致を確認する `e2e_storage_preflight.mjs` を導入した。後者に対してはrepository tree全体を保持した検証へ戻し、無条件retryでflakyとして隠していない。

## 2. KJで分けて見えたもの

### A. 「存在しているはずのfixture」と「契約が保証する状態」は別である

固定 `doc_phase1_canvas` は開発・デモ環境では便利でも、clean PostgreSQLの標準Composeが必ず持つべき状態ではなかった。

受入testがその存在を前提にすると、製品のhealthと保存経路が正常でも404だけで失敗する。ここで観測されているのはproduct invariantの破損ではなく、test setupが暗黙に要求したseed stateの欠如である。

したがって受入oracleは、環境に偶然残るfixtureではなく **対象contractが保証する不変条件** へ戻す必要がある。

### B. 受入testは検証に必要な最小状態を自ら構成できる

#3054のpreflightは毎回一意なsynthetic `DocumentV1` を生成し、書き込みと読み出しを同一run内で行う。

これにより検証対象は「特定IDのサンプルがあるか」から、

1. endpointへ書き込める。
2. 実PostgreSQL経路へ保存される。
3. 同じdocumentを読み戻せる。
4. payloadが一致する。
5. 内容不変ならPUT/GETのETagが一致する。

というADR-0019に対応した不変条件へ移る。

self-created fixtureはseed依存を消すだけでなく、testが何を成立させてから何を観測したかを明確にする。

### C. harnessは対象コードだけでなく依存closureを再現する

frontend subtreeだけを `/tmp` へコピーすることは、表面的にはfrontend testを隔離しているように見える。しかしtestがrepository-relative fixtureを参照するなら、コピーは実行環境の意味を変える。

同じtest commandでも、fixture search path、repository-relative path、generated/shared resourceなどの依存closureが失われれば、元repositoryでの検証と同値ではない。

したがってharnessの正しさは「対象ファイルを持ってきたか」だけでなく、**testが意味上依存するclosure / topologyを保持しているか** で判断する必要がある。

### D. fixtureを禁止するのではなく、所有権と契約性を分ける

R38はshared fixtureやtemporary directoryを禁止しない。

- fixtureの存在そのものが受入contractなら、その存在確認は正しい。
- setup stepがfixtureを明示的に生成・seedし、その成功までtestが所有するなら依存してよい。
- temporary copyも、必要なdependency closureを含めて同値なenvironmentを作れるなら利用できる。

問題は、**誰も成立を保証していない状態を暗黙の前提にすること**、またはharnessの都合で依存closureを切ったのにproduct/test failureとして読むことである。

## 3. 中心所見

**受入テストは、契約が保証しない既存fixtureを暗黙前提にせず、検証する最小状態を自ら構成する。さらにharnessは、テストが依存するrepository topology / fixture closureを壊さずに対象環境を再現する。**

言い換えると、受入不変条件とfixture / harness前提を分ける。testが赤いとき、product invariantが壊れたのか、setup stateが不足したのか、harnessが意味環境を変えたのかを混同しない。

## 4. これまでの継続dogfoodとの関係

- R31はcomponent-level validityとdeployment-profile realizabilityを分けた。
- R32はplatform依存working-tree表現とcanonical Git object identityを分け、検査観測点のfalse positiveを補正した。
- R35はcarrier parseabilityとsemantic conformanceを分けた。
- R38は **acceptance invariant** と、それを観測するためのfixture/setup/harness前提を分ける。

共通しているのは、検査機構そのものが対象contractとは別の前提を持ち得るため、赤/緑をそのままproduct意味へ直結しないことである。

## 5. Finding triage

- F0: PR #3054で実際に観測された、clean DBでの固定seed 404 false negativeと、frontend-only `/tmp` copyによるrepository-relative fixture喪失の偽失敗。
- F1: 既に導入された `03_Implement/frontend/scripts/e2e_storage_preflight.mjs` と `03_Implement/frontend/docs/e2e_testing.md` の自己完結roundtrip contractへ所見を戻す。
- F2: 新Issueなし。generic fixture dependency scanner、全testのhermetic化、追加の恒久preflight frameworkを起票しない。
- F3: 新ADRなし。既存ADR-0019の標準Compose最小受入へrunbook/oracleを戻す補正である。

## 6. 境界

R38は「すべてのE2E testは完全hermeticでなければならない」という主張ではない。外部service、seeded dataset、shared fixtureを必要とするtestも、その前提がcontract/setupとして明示され、実行前に成立が確認されるなら妥当である。

またtemporary directoryやsubtree copyも禁止しない。意味上必要なrepository-relative dependencyを含むclosureを保持できる場合は有効である。

#3054で修復済みのpreflightの上に、さらに新しいpreflight/KPI/schemaを積まない。実際に観測された故障へ最小のguardを戻す。

## 7. 非主張

R38はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、AI-IR named-provider evidence、第三者product-value validationを代替しない。

formal P1の現在地は変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
