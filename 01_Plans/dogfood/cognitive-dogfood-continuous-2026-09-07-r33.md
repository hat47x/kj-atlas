# 継続dogfood R33 — 意味を揃えることと観測surfaceまで届けることは別に守る

- Date: 2026-09-07
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: 同じ公開設定keyのcanonical値が複数componentで一致していても、その値が運用上必要な観測surfaceまで届いていなければ、契約はどこまで未完のまま残るか。
- Canvas: `doc_kj_atlas_dogfood_r33.json`
- Observation baseline: PR #3026 / merge commit `a37dba2f9fef321937148929913ddc960c9016c1`, PR #3027 / merge commit `42f5c63b465662f6a114d77053c2d0c9d08eb4c7`
- Result class: current repositoryで実際に観測されたAPP_REVISIONの意味driftと観測surface欠落。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. #3026で見つかったcanonical意味のずれ

`KJ_ATLAS_APP_REVISION` は同じ公開keyだったが、frontend診断bundleとbackend `/version` で受理規則が一致していなかった。

frontendは `^[A-Za-z0-9._-]{1,64}$` に限定し、不正値を `unknown` へ丸めていた。一方backend Settingsは任意文字列を受理していたため、`release+1`、`feature/revision`、65文字以上などを与えると、同じ入力から `/version.revision` と診断bundle `app.revision` が別の値になり得た。

#3026はbackend/frontendに同じcanonical contractを与えた。

- 1〜64文字のASCII `A-Za-z0-9._-` のみ保持する。
- 空文字、前後空白、`+`、`/`、改行、65文字以上は `unknown` へfail-safeする。
- Python / TypeScriptで同じ入力matrixを固定する。
- JavaScriptの末尾改行に対する正規表現差も閉じる。

ここで、同じkeyを持つこと、同じdefaultを持つことに加えて、**同じ入力を同じcanonical意味へ写像すること**が必要だと分かった。

## 2. #3027で残っていた観測surfaceの穴

#3026で `/version.revision` とfrontend診断bundle `app.revision` は揃った。しかしruntime registry / configuration / Settingsコメントはrevisionをstructured logへ反映するとしていたのに、現行loggingは `requestId` と `actorRefHash` だけを出し、`appRevision` を持っていなかった。

つまりcanonical値は存在し、診断endpointにも届いていたが、運用者が実際のログ行をどのbuildへ結び付けるかという観測契約は未成立だった。

#3027ではcanonicalized `settings.app_revision` をlogging setupへ渡し、JSONの `appRevision` とhuman-readableの `[rev=…]` に反映した。これにより、設定値の意味一致とログsurfaceへの伝播が初めて一つの運用経路として閉じた。

## 3. KJ統合で立った中心構造

今回の中心は次にまとまる。

> **意味を揃えることと、その意味を必要な観測surfaceまで届けることは別の被覆である。**

R29ではkey existenceとdefault意味一致を分けた。R30では同一surface内の宣言一意性を守った。R31ではcomponent validityとdeployment realizabilityを分けた。R33ではさらに、canonical valueが正しく決まっても、それが運用者の観測面に届かなければend-to-end契約は未完だと分かった。

これは「すべての設定値をすべてのログへ出す」という意味ではない。今回のAPP_REVISIONは、どのbuildがそのログを出したかを同定するという明示済みのobservability用途を持っていたから、ログsurfaceまでの伝播が必要だった。

## 4. Finding triage

### F0 — 生の観察として保持

- 同じ `KJ_ATLAS_APP_REVISION` でもbackendとfrontendでcanonicalizationが異なり、同一入力から別値になり得た。
- #3026でcanonical value contractを統一した。
- その後もstructured logにはrevisionが存在せず、build同定という観測用途が未成立だった。
- #3027でcanonical revisionをJSON/human-readable logへ配線した。

### F1 — 既存contractへ返す

- canonicalizationはbackend/frontendの既存revision contractへ戻す。
- 観測surfaceへの伝播は既存logging contractへ戻す。
- 新しい設定基盤やobservability基盤は作らない。

### F2 — 新Issueなし

#3026/#3027で実driftと観測欠落は解消し、回帰テストも実装済みである。独立した未完作業を残していない。

### F3 — ADRなし

新しいarchitecture decisionではなく、既存公開設定とobservability用途をend-to-endに成立させた回帰防止である。

## 5. guardを広げすぎない境界

今回を理由に、全runtime parameterを自動的にログへ出す一般規則にはしない。

秘密値や個人情報、運用上不要な値まで観測surfaceへ複製すれば別の問題を作る。必要なのは、registry/documentationが明示した観測用途と、実際にその値を必要とするsurfaceとの対応である。

また、canonicalizationも「同じkeyなら全言語で同じ文字列処理を共有する」と一般化しない。今回のように同じ公開値が複数surfaceで同一identityとして扱われる場合に、入力→canonical valueの意味を一致させる。

## 6. 実証境界と次工程

R33はcurrent repositoryのAPP_REVISION運用から得た内部所見であり、formal Case 001 Arm Cの結果ではない。第三者価値実証、AI-IR named-provider evidenceにも加算しない。

この記録のために追加のpreflight、KPI、実験スキーマは作らない。formal mainlineは引き続き、既知仮説から隔離したfresh contextとfrozen KJ Atlas UIでのCase 001 Arm C実走である。
