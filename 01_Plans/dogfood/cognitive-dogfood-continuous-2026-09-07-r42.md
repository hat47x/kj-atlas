# 継続dogfood R42 — 検査条件と失敗時の制御効果を分ける

Date: 2026-09-07
Canvas: `doc_sui_sensemaking_dogfood_r42.json`

## 1. Trigger

R41統合後の Lane B2 public-contract監査で、PR #3087 `docs(saas): provider存在確認をwarning診断へ同期する` がmainへ入った。

対象は `saas-multitenant` の active identity provider 存在確認だった。

runtimeでは、hard preflightとDatabase初期化を通過した後に `validate_saas_providers_exist()` を実行する。しかしactive providerが0件でもstartupを拒否せず、warningを記録して起動を継続する。これはcontrol-plane / admin APIから最初のproviderを登録できるbootstrap経路を残すための意図的な挙動である。

一方、公開Profile selection criteriaは、provider存在確認を「通過すべき検査」または「1つでも欠ければfail-fastするstartup condition」と読める形になっていた。

そのため文書契約がruntimeより強くなり、実際にはwarning診断である条件をhard gateとして公開していた。

PR #3087ではruntime codeを変更せず、

- hard preflightとprovider診断を分離する
- provider存在確認はpost-DB-initのwarning診断であると明示する
- provider 0件だけではstartupを拒否しない
- provider登録までは認証requestが成立しない
- warningで継続する理由がbootstrap経路の保持である

という現在のruntime semanticsへ文書を戻し、focused contractで固定した。

## 2. KJで分けて見えたもの

### A. 「検査する」ことと「失敗時に止める」ことは別である

`validate_*`、`check_*`、`preflight`、`verify_*` のような名前や、条件を実際に評価するcode pathが存在することから、失敗時の制御効果は決まらない。

同じpredicate、たとえば、

```text
active provider count > 0
```

を評価していても、結果の扱いには複数の意味があり得る。

```text
false -> startup reject
false -> warning + startup continue
false -> feature/request path unavailable
false -> degraded mode
false -> deferred bootstrap
```

したがって、

```text
check predicate
  != enforcement policy
```

である。

### B. public contractは条件だけでなく、failure consequenceも保持する

「provider存在を検査する」とだけ書くと、利用者はその条件がstartup readinessの必須条件なのか、warningなのか、request-time capabilityだけを制約するのか判断できない。

公開する必要があるのは少なくとも、

1. 何を検査するか
2. いつ検査するか
3. 条件不成立時に何が起こるか
4. 何が引き続き可能か
5. どう回復／bootstrapするか

である。

これはすべての内部validatorを詳細文書化するという意味ではない。利用者の起動・運用判断を左右するrejection / warning / degraded capability境界だけをcurrent contractとして扱う。

### C. startup成功と機能readyは同義ではない

#3087ではactive IdPが0件でもserver startupは成功する。

しかし、providerが登録されるまではSaaS認証requestは成立しない。

したがって、

```text
process started successfully
  != identity capability ready
```

である。

ここで「startupを止めない」ことを「設定不要」「認証可能」と読み替えてはいけない。

逆に「認証requestがまだ成立しない」ことから「server startupも拒否すべき」と逆算することもできない。admin bootstrapという別経路が存在するからである。

### D. recovery / bootstrap pathはenforcement policyの一部である

provider 0件をwarningに留める理由は、単なる緩いvalidationではない。

起動後のadmin APIから最初のproviderを登録するbootstrap pathを残す設計と結びついている。

もし同じpredicateをhard fail-fastへ変更すると、外部seed等の別bootstrap経路がない限り、providerを登録するために起動が必要なのにproviderがないから起動できない、という循環を作り得る。

したがってfailure consequenceを読むときは、条件単体だけでなく、その後に残されるrepair / bootstrap pathも見る必要がある。

## 3. 中心所見

**検査predicateと、そのpredicateがfalseだったときのenforcement policyは別契約である。公開運用契約は「何を確認するか」だけでなく、「いつ確認し、不成立時に何を拒否・警告・延期し、どの回復／bootstrap経路を残すか」を必要な範囲で保持する。**

短くすると、

```text
check predicate
  != enforcement policy

validation exists
  != hard gate
```

である。

## 4. 既存dogfoodとの関係

R42は既存Rを置き換えない。

### R36 — input acceptance predicate

R36は、利用者が与える値について、length / charset / path等のrejection-relevant predicateを公開契約へ戻した。

R42は、設定値そのものの受理ではなく、runtimeがある状態条件を検査した後の**制御効果**を扱う。

```text
R36
  is this input accepted?

R42
  when this checked condition is false, what does runtime do?
```

### R37 — configuration effect binding / scope / operating condition

R37はpublic configuration keyがどのconsumerへ結びつき、どこまで作用し、profile上required / recommended / conditionalのどれかを分けた。

R42はconfiguration keyを主語にしない。validator / diagnostic / preflight自体について、predicateとfailure consequenceを分離する。

ただし両者は、**存在しているものから制御効果を推測しない**点で接続する。

### R41 — operator probeとEvidence surface

R41はoperatorが「何を見ればclaimを証明できるか」を扱う。

R42はruntime内部のcheckが「条件不成立時に何をするか」を扱う。

```text
R41
  where should an operator observe evidence?

R42
  what consequence does the runtime attach to the checked condition?
```

### R31 — component capabilityとdeployment-profile realizability

R31はcomponent-level semantic validityとpackaged deployment profileで実現できる条件を分けた。

R42の `startup success != identity capability ready` も、process/serviceが起動可能であることと、その時点ですべてのsub-capabilityが利用可能であることを潰さない点で整合する。

## 5. 今回の設計判断

### 新しいgeneric validation registryは作らない

R42から、全 `validate_*` / `check_*` 関数へseverity metadataを付ける、全validationを共通schemaへ登録する、といった一般化には進まない。

内部validationには、

- pure input validation
- startup hard gate
- readiness dependency check
- warning diagnostic
- request-time authorization
- best-effort observability

など異なるshapeがある。

#3087はすでにfocused contractで、呼び出しphase、非throw、warning、bootstrap意図を狭く固定している。現時点ではそれで十分である。

### function名からpolicyを推論しない

文書監査では `validate_*` という名前だけを根拠にhard gateと書かない。

必要な場合はactual call siteとresult handlingを確認し、

```text
predicate
phase
false-result consequence
remaining capability
recovery path
```

を現在のruntime factへ合わせる。

ただし、すべての内部helper名をpublic contractへ露出させる必要はない。

## 6. Finding triage

- F0: PR #3087。active provider存在確認をhard startup gateのように公開していたが、実装はpost-DB-init warning診断で、provider 0件でもadmin bootstrapを残すためstartup継続だった実陽性。
- F1: #3087でprofile文書をruntimeへ同期し、focused contractで呼び出しphase・非throw・warning・bootstrap意図を固定済み。
- F2: 新Issueなし。既存public-contract conformance workstream内で閉じる。
- F3: 新ADRなし。runtime policy変更ではなく、既存policyの意味分離と公開契約同期である。

## 7. 境界

R42はwarningがfail-fastより一般に優れているとは主張しない。

security-critical predicateや不可逆な破損条件ではhard rejectionが適切な場合がある。重要なのは、実際のpolicyをfunction名や「検査」という語から推測しないことである。

また、

- startup成功なら全機能ready
- warningなら無視してよい
- requestが成立しないならstartupも失敗すべき
- bootstrap pathがあるならhard gateは禁止

とも主張しない。

それぞれのconditionについて、runtimeが現在どのeffectを持たせているかをshape-awareに確認する。

R42を恒久required checkへ単独昇格しない。今回の実陽性はfocused contractで閉じられており、generic automationの追加価値はまだ実証されていない。

## 8. 非主張

R42はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、第三者product-value validation、AI-IR named-provider evidenceを代替しない。

formal P1の現在地も変わらない。次の正式工程はfresh isolated context + frozen SUI Sensemaking UIでのCase 001 Arm C実走である。
