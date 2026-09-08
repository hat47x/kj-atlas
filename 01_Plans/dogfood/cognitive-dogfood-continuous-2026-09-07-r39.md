# 継続dogfood R39 — test oracleのsemantic surfaceを偶発的一意性から分ける

Date: 2026-09-07
Canvas: `doc_kj_atlas_dogfood_r39.json`

## 1. Trigger

R38統合後、PR #3063で `QA-PUB-01-I18N-03` の公開互換 / I18N flow parity / readOnly + SafeMode の3軸を、標準Docker Composeで配信されたcurrent-main frontendへChromiumを直接接続して再実走した。

初回product-path run `34068672554` では、clean Compose health、実PostgreSQLのsynthetic DocumentV1 roundtrip、typecheckはpassした一方、Playwrightは14件中12件pass・2件failとなった。

2件とも製品欠落ではなかった。期待する公開パックerror本文は既存の専用surface `data-testid="status-message"` に正しく表示されていたが、Compose本番配信では別の正当なmodel/runtime `role="status"` も同時に存在していた。そのため非限定の `getByRole("status")` がstrict modeで2要素へ一致し、assertionだけが失敗した。

#3063は製品側の別statusを消さず、`.first()` でDOM順へ逃げず、該当2箇所だけを `getByTestId("status-message")` へ限定した。最終Compose run `34068886877` では targeted 4 specsが14/14 passとなり、製品実装変更はなかった。

## 2. KJで分けて見えたもの

### A. 画面上の「一意だった要素」とassertionが意味上観測したいsurfaceは別である

`role="status"` はアクセシビリティ上正当な意味を持つ。しかし一つの画面にstatusが常に一個だけ存在する、という契約までは意味しない。

Vite系の以前の実行ではたまたま一意だったため、非限定locatorでもtestは通っていた。標準Composeで別の正当なstatus surfaceが同時に存在したことで、その暗黙前提が露見した。

したがってtest oracleは、現在のDOMでたまたま一個見つかる要素ではなく、**そのassertionが検証対象としているsemantic surface** へ結びつく必要がある。

### B. broad semantic locatorが悪いのではなく、assertionの意味境界とlocatorのscopeを揃える

R39は `getByRole()` より `data-testid` を常に優先する主張ではない。

- 「この画面にはstatusが一つだけである」こと自体が契約なら、role-basedな一意性assertionは妥当である。
- 利用者操作のアクセシブルな意味を検証するtestなら、role/nameを使う方が適切な場合も多い。
- 今回は「公開パックerror surfaceに特定文言が出る」ことを検証しており、別のmodel/runtime statusの存在は契約違反ではない。

よってlocatorの抽象度は、testのassertionが所有する意味境界へ合わせる。一般roleの存在を検証するtestと、特定subsystemのstatus messageを検証するtestを同じoracleにしない。

### C. `.first()` はambiguityを消してもsemantic ownershipを与えない

strict locator ambiguityに対して `.first()` を付ければtestは形式上通り得る。しかしDOM順は、公開パックerrorとmodel/runtime statusのどちらがassertion対象かを説明しない。

DOM挿入順やrender順が変われば別surfaceを読む可能性があり、greenが正しい意味を観測した証拠にならない。

したがってambiguity修正では、単に候補数を1にするのではなく **なぜその一要素がassertion対象なのかをlocator自体で表す** 必要がある。

### D. productをtestに合わせて狭めない

#3063では別の `role="status"` も正当な製品surfaceだった。testを通すためにそのstatusを削除・role変更すれば、製品の有効な観測surfaceをtest oracleの都合で壊すことになる。

test failureをtriageするときは、

1. 期待内容が対象surfaceに存在するか。
2. 同時に存在する他surfaceも製品契約上正当か。
3. locatorがassertionのsemantic ownershipより広くないか。

を分けて見る。期待内容が存在し、他surfaceも正当なら、test oracle側のscopeを疑う。

## 3. 中心所見

**test oracleは、画面上でたまたま一意だった一般surfaceではなく、assertionが検証対象として所有するsemantic surfaceを観測する。観測対象の一意性はDOMの偶然ではなく、意味境界から定義する。**

つまり、testがgreenであるために「候補が一つである」ことを求めるのではなく、「このassertionが読むべき対象を一意に指定できる」ことを求める。

## 4. R38および既存所見との関係

- R33: productのcanonical意味が、明示された必要観測surfaceまで届くかを分けた。
- R38: acceptance invariantと、それを成立・実行するfixture / setup / harness前提を分けた。
- R39: environmentと期待結果が正しくても、**test oracleがどのsemantic surfaceを読むか** がずれるとfalse failureになることを分ける。

受入評価を大きく見ると、

1. 検証対象contractを決める。
2. 必要な状態・environmentを正しく構成する。
3. productを同等なharnessで実行する。
4. assertionが所有するsemantic surfaceから結果を読む。
5. その結果をcontract invariantと比較する。

という層があり、R38とR39は4の前後を分離する。

## 5. Finding triage

- F0: PR #3063の初回Compose実走で観測された、期待内容が正しく存在するのに非限定 `getByRole("status")` が2個の正当なstatusへ一致して失敗した2件のtest false failure。
- F1: 既に修正された `03_Implement/frontend/e2e/public_pack_visibility_compat.spec.ts` の2 assertionを、既存専用 `status-message` surfaceへ限定する最小修正へ所見を戻す。
- F2: 新Issueなし。repository-wide locator linter、test-id必須化、UI surface schemaを追加しない。
- F3: 新ADRなし。既存QA境界の再実走から得たtest oracle補正である。

## 6. 境界

R39はrole-based locatorを禁止しない。accessible role/nameがassertion対象そのものであり、その一意性がproduct contractなら引き続き適切である。

また `data-testid` の全面導入も主張しない。今回のように既存の専用surfaceがあり、一般roleよりassertion ownershipを正確に表す場合にだけ利用する。

strict-mode failureを避ける目的だけで `.first()` / `.last()` に逃げない。DOM順がcontractでない限り、それはambiguityを隠すだけである。

#3063でtest-only修正と同一Compose経路の再実走がgreenになっているため、さらにgeneric locator guardや新しい恒久E2E frameworkを積まない。

## 7. 非主張

R39はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、AI-IR named-provider evidence、第三者product-value validationを代替しない。

formal P1の現在地は変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
