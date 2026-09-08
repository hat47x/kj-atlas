# 継続dogfood R43 — 単一keyの妥当性とcross-key relational invariantを分ける

Date: 2026-09-08
Canvas: `doc_kj_atlas_dogfood_r43.json`

## 1. Trigger

R42以後の Lane B2 public-config監査で、個々の設定値のformatやeffect scopeではなく、**複数keyの組合せそのもの**が起動可否を決める実陽性が連続してmainへ入った。

### PR #3104 — business/admin API keyの分離

`KJ_ATLAS_API_KEY` と `KJ_ATLAS_ADMIN_API_KEY` は、それぞれ単体ではcanonicalな秘密値として受理され得る。

しかし両方へ**同じ秘密値**を設定したconfigurationはSettings validationで起動時拒否される。

つまり、

```text
valid(API_KEY)
and valid(ADMIN_API_KEY)
does not imply
valid(API_KEY, ADMIN_API_KEY)
```

である。

### PR #3105 — resolver無効化時のleftover HTTP設定

Document policy binding / tenant capability resolverでは、`resolver=none` 自体は有効な値であり、endpoint / API keyもそれぞれ別の文脈では有効な値になり得る。

しかし `resolver=none` の状態でendpointまたはAPI keyが残っている組合せは、共通Settings helper `_validate_trusted_http_resolver()` が起動時に拒否する。

無効化はselectorだけを `none` へ変えれば終わるのではなく、現在のruntime contractではdependent HTTP settingsも同時に外す必要がある。

### PR #3107 — access-control integration無効化時のleftover設定

`KJ_ATLAS_ACCESS_CONTROL_ADAPTER=noop` も有効な値である。

endpoint / fixed bearerも `external_http` 選択時には有効である。

しかしadapterが `external_http` でないのにendpointまたはfixed bearerが残るconfigurationは `_validate_optional_http_integration()` により起動時拒否される。

これも単一keyのvalidationではなく、**selectorとdependent settingsのrelation**で決まる。

3件ともruntime behavior自体は変更せず、既存のfail-closed relational validationを利用者向け公開契約へ戻し、focused contractで固定した。

## 2. KJで分けて見えたもの

### A. per-key acceptanceとconfiguration-state validityは別である

単一keyのvalidationは、その値が単独で許容grammarに入るかを答える。

しかしconfigurationはkey/valueの集合であり、runtimeが要求する不変条件には複数keyの関係が含まれ得る。

```text
per-key acceptance
  != configuration-state validity
```

より形式的には、

```text
∀k: accepted(k = v)
```

だけでは、

```text
accepted(configuration = {k1=v1, k2=v2, ...})
```

を保証しない。

### B. relationには同値禁止、selector依存、presence/absence依存がある

今回観測したrelationは少なくとも次の3shapeだった。

```text
separation:
  business_key != admin_key

selector dependency:
  resolver = none -> endpoint absent and api_key absent

activation dependency:
  adapter != external_http -> endpoint absent and bearer absent
```

重要なのは、この3shapeを共通DSLへ押し込むことではない。

利用者が複数keyを一緒に変更しなければ正しい状態へ到達できない場合、そのrelationをpublic contractから落とさないことである。

### C. featureを「無効にする」ことは単一toggle操作とは限らない

#3105 / #3107では、利用者の意図はintegrationを無効にすることでも、selectorだけを `none` / `noop` へ戻すと起動拒否になる。

したがって現在のruntimeでは、

```text
disable feature
  = selector transition
  + dependent-setting cleanup
```

というstate transitionを持つ。

ただし、これは「無効機能の設定値は常に残してはいけない」という一般原則ではない。別のsystemではinactive設定をignoreして保持するpolicyもあり得る。

R43が保持するのは**現在のruntimeが採用しているrelational invariant**である。

### D. public contractは値の辞書だけでなく、必要な関係を保持する

設定表をkeyごとの独立した行として読むだけでは、#3104/#3105/#3107の失敗条件は復元できない。

利用者の変更手順や起動可否を左右するrelationについては、必要な場所で、

- 一緒に設定してはいけない組合せ
- selector変更時に同時変更が必要なdependent key
- presence / absence条件
- relation違反時のconsequence

を保持する。

これは全configurationを宣言的schemaへ移すことを意味しない。現在のfocused Settings validationとpublic docsで十分閉じられるshapeは、そのまま狭く固定する。

## 3. 中心所見

**単一keyが受理可能であることと、複数keyを組み合わせたconfiguration stateが受理可能であることは別契約である。public config contractは、利用者が正しいstateへ到達するために必要なcross-key relational invariantを、個別keyのformat/requirednessとは分けて保持する。**

短くすると、

```text
per-key valid
  != configuration valid

valid values
  + invalid relation
  = rejected configuration
```

である。

## 4. 既存dogfoodとの関係

R43は既存Rを置き換えない。

### R36 — input acceptance predicate / grammar

R36は、1つの公開入力についてlength / charset / path / finite allowlist等のrejection-relevant predicateを扱う。

#3108のOAuth client ID / secret format、#3109のoutbound HTTP bearer formatはR36の典型的な再発である。

R43は、**各値が個別にはR36を通過していても、組合せとして拒否されるrelation**を扱う。

```text
R36
  is this value individually accepted?

R43
  is this configuration state jointly admissible?
```

### R37 — configuration effect binding / scope / operating condition

R37は、受理されたconfigurationがどのconsumerへ結びつき、どこまで作用するかを扱う。

#3101のDeepSeek thinking mode effect scopeはR37の再発である。

R43は作用面ではなく、runtimeへ入る前または起動時に**組合せ自体が許容stateか**を扱う。

### R42 — check predicateとenforcement policy

R42は、あるconditionを検査したとき、そのfalse resultへruntimeがreject / warning / degraded等のどのconsequenceを結ぶかを扱う。

R43のrelational validatorもfalse時には起動拒否されるためR42と接続するが、主語は異なる。

```text
R43
  what relation defines an admissible configuration state?

R42
  what consequence follows when a checked condition is false?
```

R43ではrelationそのものの意味と変更手順を保持し、R42ではその違反が現在fail-fastであることを必要な範囲で保持する。

### R29 — default value semantics

R29はkeyの存在、既定値、その既定値の意味を分けた。

R43はdefaultではなく複数key間のinvariantを扱う。selectorのdefaultが `none` / `noop` であっても、dependent keyとのrelationは別に確認する。

## 5. 今回の設計判断

### generic cross-key dependency graphは作らない

R43から、全Settings fieldをnodeにしたdependency graph、全組合せを列挙するschema、全validatorを自動抽出する仕組みには進まない。

今回の3件はすでに、

- Settings validation
- 利用者向けconfiguration文書
- focused contract

で狭く閉じられている。

generic化はfalse positiveや二重正本を増やす可能性があり、現時点の実陽性はそこまでを要求していない。

### deactivation手順をstate transitionとして読む

selector型の設定を監査するときは、単にenumの許容値だけを見るのではなく、

```text
active -> inactive
inactive -> active
```

の遷移でdependent settingsがどう扱われるかを確認する。

ただし「inactive時はdependent settingsを必ず拒否する」と先に決めず、actual Settings validationとruntime policyへ戻る。

### relationは利用者が踏む変更面に近い場所へ書く

relational invariantが起動可否を左右し、利用者が複数keyを協調して変更する必要がある場合、keyごとの表だけでなく無効化/切替手順などの文脈にも関係を残す。

#3105/#3107がconfiguration.mdの利用手順を補ったのはこのためである。

## 6. Finding triage

- F0: PR #3104。business/admin API keyは単体では有効でも同一秘密値の組合せが起動時拒否される実陽性。
- F0: PR #3105。resolver=`none` とleftover endpoint/API keyの組合せが起動時拒否され、無効化時に協調cleanupが必要だった実陽性。
- F0: PR #3107。access-control adapterが`external_http`でない状態とleftover endpoint/bearerの組合せが起動時拒否される実陽性。
- F1: #3104/#3105/#3107で公開文書同期とfocused contractがそれぞれmainline済み。
- F2: 新Issueなし。既存public-config conformance workstream内で個別再発防止は閉じている。
- F3: 新ADRなし。runtime policy変更ではなく、既存relational invariantの意味統合である。

## 7. 境界

R43は次を主張しない。

- すべての設定keyは他keyとのrelationを持つ。
- inactive featureのdependent settingsは常に拒否すべきである。
- cross-key validationは単一の宣言的schemaへ統合すべきである。
- accepted configurationはruntime上必ず有効に作用する。これはR37の責務である。
- relation違反は常にhard failすべきである。failure consequenceはR42へ戻る。
- 同じ値を複数credentialへ使うことは一般に禁止である。#3104の分離は対象control plane contract固有である。

R43を恒久required checkへ単独昇格しない。

今回のshapeはfocused contractで閉じられており、generic dependency checkerの運用価値やfalse-positive率は実証されていない。

## 8. 非主張

R43はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、第三者product-value validation、AI-IR named-provider evidenceを代替しない。

formal P1の現在地も変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
