# 継続dogfood R37 — 設定の受理と実効制御・作用範囲・推奨を分ける

Date: 2026-09-07
Canvas: `doc_kj_atlas_dogfood_r37.json`

## 1. Trigger

R36統合後のmainで、Lane B2のpublic-config監査から3件の実陽性が続いた。

- PR #3048: `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS` はSettingsで `false` を読み込めたが、値をruntime behaviorへ結ぶconsumer / trigger contractが存在しない **dead toggle** だった。未確定CE4契約をどのrequestで501 stubへ分岐させるか自体が未定義なので、`false` の挙動を実装することは新しいsemanticsの発明になる。#3048は未確定trigger contractが実装されるまで `true` 固定とし、`false` を起動時fail-fastで拒否した。
- PR #3049: `KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK` には実runtime consumerがあるが、作用範囲はdocs CE4の `POST /docs/{doc_id}/context-audit` に限られる。一方公開表はCE4全体へ効くようにも読め、proposal / CE4 resolveが対象外であることを落としていた。
- PR #3050: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` はlocal-dev / evaluationでは明示的に利用できる有効値だが、Enterprise recommendationではない。runtime registryの推奨欄だけが `false または true` となり、enterprise-production / saas-multitenant profileと `TrustedSaasRuntimePolicy` の `false` 要求と矛盾していた。

これらはR36のacceptance predicateとは別である。値が構文・validator上は受理可能でも、**何を変えるのか・どこまで効くのか・どのprofileで勧められるのか** は別の意味軸としてずれ得る。

PR #3047のQA gate current-state同期はR34で扱ったcurrent-state/wiring shapeの再発であり、R37の独立triggerには数えない。

## 2. KJで分けて見えたもの

### A. accepted valueとeffective controlは同じではない

#3048では `false` がSettingsへ入ること自体は成功していた。しかし、その値を参照して未確定CE4契約の挙動を切り替えるruntime consumerがなかった。

公開toggleが存在すると、利用者は値を変えれば対応する挙動が変わると解釈する。したがって設定contractは「parser / validatorが値を受け取れる」だけでなく、**その値がどのruntime decision pointへ結びつくか** を持つ必要がある。

ただしconsumerがないからといって、その場で新しいbehaviorを発明してはならない。#3048ではCE4の未確定stub trigger自体が正本に定義されていなかったため、意味が定まるまでは `true` 固定 + `false` fail-fastが最も狭い修正だった。

### B. consumerがあっても作用範囲は別契約である

#3049はdead toggleではない。`KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK` はdocs context-audit routeで実際に参照され、`false` 時には `422 mock_source_bundle_hash_disabled` を返す。

問題は「効く / 効かない」の二値ではなく、**どのboundaryにだけ効くか** がpublic surfaceで曖昧だったことにある。proposal APIとCE4 resolveは別の契約へ従い、このtoggleの対象外だった。

したがってeffective controlにはconsumer existenceだけでなく **effect scope** がある。route、subsystem、tenant/profile、request phase等のうち、利用者の期待を変える境界は公開contractへ戻す必要がある。

### C. 設定可能であることと推奨されることも別である

#3050では `true` 自体は不正値ではない。local-dev / evaluationでは意図的に使える。

しかしEnterprise recommendationは、受理可能な値集合の説明ではなく、そのprofileで安全・標準として選ぶべき値の政策層である。同じ欄に `false または true` と書くと、capabilityとrecommendationを混同する。

よってpublic config contractでは少なくとも、

1. **acceptance** — 値が受理されるか。
2. **effect binding** — 値がruntime decisionへ接続されるか。
3. **effect scope** — どのboundaryへ作用するか。
4. **profile recommendation / policy** — どの運用文脈で何を選ぶべきか。

を必要に応じて分ける。

### D. 「公開されている設定だから可変」は成り立たない

公開keyが存在しても、現在の正本で意味が未確定なら可変にしておく必要はない。未定義behaviorへ値を流すdead controlは、設定可能性そのものが誤った約束になる。

逆に、実装済みconsumerがある設定を一律fixedへ縮めてもいけない。#3049のmock policyは実効制御として残し、その作用範囲だけを狭く明示した。#3050のJITもlocal/evaluation capabilityを残し、Enterprise recommendationだけを `false` へ戻した。

## 3. 中心所見

**公開設定契約は「値を受理できる」で終わらない。値がどのruntime decisionへ結びつき、どこまで作用し、どのprofileで推奨されるかを分けて保持する。**

特にtoggleについては、acceptedだがconsumerがない状態を「将来使う設定」として黙って残すと、利用者へ実在しない制御可能性を約束する。runtime semanticsが未定義なら、正本が決まるまでfail-fast / fixedに縮める方が、挙動を推測して配線するより安全である。

## 4. R36との関係

- R36: **acceptance predicate / grammar** — 値が入力として受理される条件を守る。
- R37: **effective control semantics** — 受理された値が実際に何へ効くかを守る。

R37の中でもさらに、consumerへのbinding、作用範囲、profile recommendationは別軸である。

したがって設定contractの確認順序は、必要に応じて次のように分けられる。

1. carrierを正しく読める。
2. 値のshape / acceptanceを正しく表せる。
3. 受理値が意図したruntime decisionへ接続される。
4. 作用範囲が公開説明と一致する。
5. profile recommendation / policyがcapabilityと混同されていない。

## 5. Finding triage

- F0: #3048のdead toggle、#3049のconsumer scope過大表現、#3050のallowed valueとEnterprise recommendation混同という実陽性。
- F1: #3048のSettings fail-fast回帰、#3049の `test_ce4_mock_policy_scope_contract.py`、#3050の `test_jit_profile_recommendation_contract.py` へ所見を戻す。
- F2: 新Issueなし。generic consumer-discovery scannerや全設定のeffect graphを追加しない。
- F3: 新ADRなし。既存CE4 / SaaS runtime contractの公開面と実効性を同期する補足である。

## 6. 境界

R37は「すべての設定keyに直接consumerが必要」という主張ではない。fixed guard、profile入力、起動時validationだけで責務が完結する設定もある。重要なのは、そのkeyが利用者へ何を制御できると約束しているかと、実装の意味が一致することである。

またrecommendationはacceptance validatorへ逆輸入しない。#3050でEnterpriseは `false` 推奨でも、local-dev / evaluationの明示 `true` capabilityは残る。

## 7. 非主張

R37はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、AI-IR named-provider evidence、第三者product-value validationを代替しない。

formal P1の現在地は変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
