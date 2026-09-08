# 継続dogfood R29 — contract keyの存在とdefault値の意味一致は別に守る

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: runtime parameter registryと実装の対応を「同じkeyが存在する」だけで確認したとき、公開default値の意味driftをどこまで見逃し得るか。
- Canvas: `doc_kj_atlas_dogfood_r29.json`
- Observation baseline: PR #3003 / merge commit `bb173e57feb19dc395f0440534c0f987d561c04b`
- Follow-up guard: PR #3014 / merge commit `8dedc1fba146f6bbc2ee1e07360293da70b71839`
- Result class: current repositoryで実際に観測されたruntime defaultのdocs driftと、その再発経路を閉じた運用上の陽性。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. 実際に起きていたずれ

`KJ_ATLAS_MAX_DOCUMENT_CARDS` の実装既定値は `50000` へ進んでいた一方、`02_Architecture/runtime_parameter_registry.md` と利用者向け `04_Documentation/configuration.md` は旧値 `10000` を公開defaultとして残していた。

PR #3003はruntime behaviorを戻さず、公開設定契約を現行実装へ同期した。設定正本とoperator-facing documentationを `50000` へ更新し、backend regressionも単なる `> 0` ではなく `== 50_000` へ固定した。

ここで重要なのは、同じ `KJ_ATLAS_MAX_DOCUMENT_CARDS` というkey自体は実装にも文書にも存在していた点である。したがって「keyが両側に存在する」だけを確認するcontract testでは、この10,000 / 50,000の意味差を検出できなかった。

## 2. #3014で閉じた検査穴

PR #3014は、runtime registryが宣言していたdefault-value gateを実際の値比較として実装した。

- registryの `Profile default vs recommendation` にある `Implementation default` を読む。
- `Settings` の静的に評価できるliteral default / `Field(default=...)` を読む。
- `50,000` と `50_000` は同じ数値として正規化する。
- `未設定` は `None` として扱い、文字列 `none` とは区別する。
- `default_factory` 等のcomputed defaultは静的gateへ無理に押し込まず対象外とする。
- documented defaultとimplementation defaultが異なる場合だけ `DC-CFG-001` を返す。

negative controlではregistry側だけを `10,000` に戻し、runtimeが `50_000` のままならfindingが1件出ることを確認した。

## 3. KJ統合で立った中心構造

今回の中心は次にまとまる。

> **契約項目が存在することと、その契約が運ぶ意味値まで一致していることは別の被覆である。**

key existenceは「対応する入口がある」ことを確かめる。しかしdefault値は利用者が実際に期待するruntime semanticsの一部であり、名前が一致していても値が違えば公開契約はずれる。

これはR16/R17で整理した「IRに項目があること」と「routeに必要な意味が保持されること」の違いにも通じる。ただし今回の対象はAI-IRではなくruntime configuration docsであり、同一Issueへ統合する話ではない。共通しているのは、**形の存在だけで意味保存を代用しない**という検査姿勢である。

またR28のnavigation/state authorityとも境界が異なる。R28ではnavigationが他正本の可変状態を複製しないことが中心だった。R29ではregistry自身が公開defaultの正本として値を持つことは妥当であり、その値をruntime実装と機械照合する。つまり「複製をやめる」のではなく、「複製が契約上必要なら意味まで照合する」側の事例である。

## 4. Finding triage

### F0 — 生の観察として保持

- runtime `Settings.max_document_cards` は50,000だったが、公開registry / configuration docsは10,000のまま残っていた。
- keyは両側に存在していたため、key-existence中心のcontractでは値driftを止められなかった。
- PR #3003で値を現行runtimeへ同期した。
- PR #3014でstatic default-value comparisonを追加し、10,000へ戻すnegative controlが検出されることを確認した。

### F1 — 既存docs contractへ返す

- 新しい設定管理機構は作らず、既存 `docs_contract_checks.py` にdefault-value comparisonを追加した状態を正とする。
- 静的に安全に読めるdefaultだけを比較し、computed/default_factoryを推測しない。
- 数値表記差は正規化し、`None` と文字列 `none` のように意味が異なる値は潰さない。

### F2 — 新Issueなし

実driftは#3003で解消し、再発gateも#3014で実装・検証済みである。独立した未完作業を残していない。

### F3 — ADRなし

新しいruntime architectureではなく、既存の公開設定契約を検査可能にした回帰防止である。

## 5. guardを広げすぎない境界

今回の成功を理由に、あらゆる設定defaultを文字列比較する一般scannerへ拡張しない。

computed default、環境依存値、factory経由の値まで静的に推測するとfalse positiveや誤った権威化が起こり得る。#3014が対象にしたのはASTで安全にliteral評価でき、registry側にも `Implementation default` として明示されている交差部分だけである。

必要意味を狭く定義し、測れる範囲だけを非退行条件へする。

## 6. 実証境界と次工程

R29はcurrent repositoryで実際に起きたconfiguration docs driftから得た内部所見であり、formal Case 001 Arm Cの結果ではない。第三者価値実証、AI-IR named-provider evidenceにも加算しない。

この記録のために追加のpreflight、KPI、実験スキーマは作らない。formal mainlineは引き続き、既知仮説から隔離したfresh contextとfrozen KJ Atlas UIでのCase 001 Arm C実走である。
