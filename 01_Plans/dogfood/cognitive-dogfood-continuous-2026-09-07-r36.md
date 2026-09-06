# 継続dogfood R36 — 公開入力契約では値名だけでなく受理predicateを保持する

Date: 2026-09-07
Canvas: `doc_kj_atlas_dogfood_r36.json`

## 1. Trigger

R35統合後のmainで、Lane B2のsecurity-format監査から2件の実陽性が続いた。

- PR #3043: `KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY` は実装 `_HEX_KEY_PATTERN = ^[0-9a-f]{64}$` により **64文字・lowercase hex** だけを受理し、利用者向けconfigurationも同じ制約を記していた。一方runtime registryは「64桁16進=32バイト」とだけ書き、uppercaseも受理されるように読めた。
- PR #3044: `KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI` はtrusted HTTP endpointであるだけでなく、実装が `urlsplit(...).path == "/session/callback"` を必須とし、それ以外を起動時に拒否する。一方runtime registry / configurationは「OAuth callbackのredirect URI」とだけ記し、固定path制約を公開していなかった。

どちらもkey存在、default値、finite enum集合のdriftではない。実装が入力を受理するために評価する **predicate** の一部が、公開contractから欠落していた。

PR #3040のcurrent-state prose driftはR34で既に扱ったwiring/current-state shapeの再発であり、R36の独立triggerには数えない。#3039〜#3042のguest journey実装・closeoutも別laneの機能進行であり、continuous dogfoodの新所見とはしない。

## 2. KJで分けて見えたもの

### A. finite enumとformat predicateは同じ「値契約」ではない

R34では `LLM_PROVIDER` や `LOG_LEVEL` のような有限集合を、implementation literal setとpublic enum表のset equalityで守る形を整理した。

しかし#3043のhash keyは、列挙可能な少数の候補値から1つを選ぶ契約ではない。受理空間は多数の文字列からなり、`len == 64`、文字集合が `[0-9a-f]`、uppercase不可、という条件をすべて満たす場合だけ有効になる。

#3044のredirect URIも同様で、単にURLであることでは足りない。scheme/host等のtrusted endpoint条件に加え、pathが厳密に `/session/callback` であることが受理条件の一部である。

したがってpublic input contractには、finite setとは別に **acceptance predicate / grammar** というshapeがある。

### B. 利用者が必要なのは「何と呼ぶか」より「何が拒否されるか」

#3043では「64桁16進」という説明だけでも大意は伝わるが、実装はuppercase A-Fを拒否する。利用者が `A1...` のような64桁hexを生成すれば、文書上は妥当に見えても起動時に失敗し得る。

#3044でも「OAuth callback redirect URI」という用途名だけでは、任意のcallback pathを設定できるように読める。しかし実装は `/session/callback` 以外を拒否する。

公開configurationの責務は内部validatorを逐語的に複製することではないが、正常設定の可否を左右する **rejection-relevant constraint** は利用者から見える必要がある。

### C. predicate contractは狭い実装正本へ戻す

#3043は `_HEX_KEY_PATTERN` のstatic regexとpublic rowsの `64` / `lowercase` / `32 bytes` をfocused testで照合した。

#3044はSettings validatorが `/session/callback` 固定を保持することと、runtime registry / configurationの両方が同じpathを明示することをfocused testへ固定した。

ここでも全validatorをgeneric schemaへ変換していない。静的に安全に特定でき、利用者の設定成否を直接左右する高影響constraintだけを狭く契約化している。

### D. R35のcarrier integrityとは別層である

R35は、意味が正しくてもMarkdown delimiter衝突で値を抽出できなければsemantic comparisonへ進めない、と整理した。

R36はcarrierが正しく読めることを前提に、その中に載せる意味自体を細分する。つまり、

1. carrier integrity — 公開surfaceを欠落なく読める。
2. contract shape identification — scalar / finite set / predicate / delivery / wiring等のどの意味形かを決める。
3. semantic conformance — そのshapeに対応する実装正本と一致させる。

という順序になる。

## 3. 中心所見

**公開入力契約は、key・default・候補値名だけでは閉じない。実装が受理可否を決めるrejection-relevant predicateを、利用者が設定可能な形で保持する。**

finite enumなら集合一致でよい。一方、文字列format、長さ、case、固定path、組合せ条件のように受理空間をpredicateで切る設定では、そのpredicate自体がpublic contractの一部である。

## 4. R34〜R36の関係

- R34: current contractのshapeに応じて適切な正本照合を選ぶ。
- R35: shape-aware comparisonの前提として、contract carrierが一意にparseできることを守る。
- R36: R34のshape分類へ **acceptance predicate / grammar** を追加し、設定成否を左右するreject条件をpublic contractへ含める。

R36は「すべてのvalidatorを文書へ転写する」という主張ではない。内部実装詳細や導出可能な枝葉まで公開せず、利用者が正しい値を作るために必要な最小のrejection-relevant constraintsに限定する。

## 5. Finding triage

- F0: PR #3043/#3044で実際に観測された、実装受理predicateとpublic contractの精度差。
- F1: 既に追加された `test_security_format_contract.py` のfocused contractへ所見を戻す。
- F2: 新Issueなし。generic validator introspection / schema generatorを追加しない。
- F3: 新ADRなし。既存runtime behaviorを公開契約へ同期する責務の補足である。

## 6. 非主張

R36はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、AI-IR named-provider evidence、第三者product-value validationを代替しない。

formal P1の現在地は変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
