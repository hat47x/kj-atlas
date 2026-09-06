# 継続dogfood R30 — 必要な複製でも同一層の宣言点は一意にする

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: runtime configurationの意味を複数層へ配送する必要があるとき、同一のauthority / delivery surface内に同じkeyの宣言点が複数あることをどう扱うべきか。
- Canvas: `doc_kj_atlas_dogfood_r30.json`
- Observation baseline 1: PR #3016 / merge commit `d8c72afa1cc570d5e938fe9bc4dbbc6ec5c63ed1`
- Observation baseline 2: PR #3017 / merge commit `e07aa2191c0a1a4ba7919e47bb308850b2e0a5aa`
- Result class: current repositoryで実際に観測された重複宣言2件と、それぞれを局所的な一意性contractへ戻した運用上の陽性。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. Backend settings表で起きていたこと

R29で `Profile default vs recommendation` と `Settings` のdefault意味一致を守った後、PR #3016の監査では同じruntime registry内の `Backend settings` 表に別の残差が見つかった。

- `KJ_ATLAS_APP_REVISION` が同一表内で重複し、`未設定` と `unknown` が併存していた。
- `KJ_ATLAS_LOG_LEVEL` も同一表内で重複していた。
- `KJ_ATLAS_MAX_DOCUMENT_CARDS` は上段と実装では50,000へ同期済みなのに、Backend settings表だけ10,000を残していた。

ここでは「別層に同じ意味を公開するための必要な複製」より前に、**一つの表の中で同じkeyが複数の宣言点を持っていた**。この状態では、どちらの行がその表における契約なのかが曖昧になる。

PR #3016は重複行を整理し、Backend settings表に限定してkey uniquenessと `Settings(validation_alias=...)` の静的default一致を回帰テストへ戻した。

## 2. Compose配送面でも同型が再現した

PR #3017では標準 `03_Implement/deploy/docker-compose.yml` の `api.environment` に `KJ_ATLAS_APP_REVISION` が2回記載されていた。

その時点では同値だったためruntime behaviorを直ちに変える不具合ではなかった。しかし同一serviceの同一environment listに同じ公開keyの宣言点が二つあると、将来片方だけが変更されるdrift seamになる。また、レビュー時に「どの宣言が配送契約か」を一意に追跡できない。

PR #3017は重複1行を削除し、次を現在の公開配送境界に限定して固定した。

- `api.environment` 内の `KJ_ATLAS_*` は重複しない。
- `KJ_ATLAS_APP_REVISION` はAPI runtimeへ1回、web build argsへ1回だけ配送する。
- `web.build.args` 内の `KJ_ATLAS_*` も重複しない。

ここでAPI runtimeとweb build argsの両方に同じkeyが現れること自体は問題ではない。配送先という層が異なり、それぞれに意味があるからである。問題は、**同一配送面の内部に同じ宣言が複数あること**だった。

## 3. KJ統合で立った中心構造

今回の中心は次にまとまる。

> **必要な複製は層間では許されるが、同一のauthority / delivery surface内では宣言点を一意にする。**

R28では、navigationが他正本の可変状態を複製して第二正本になることを避けた。R29では、registryのように複製が契約上必要な場合はruntime実装との意味一致を守った。R30ではさらに、その各層の内部に同一keyの宣言点が複数あると、値が今は同じでも将来の分岐点になることを扱う。

したがって三つは次のように分けられる。

1. **不要な複製を持たない** — R28。
2. **必要な層間複製は意味一致を守る** — R29。
3. **各層内部の宣言点は一意にする** — R30。

これは「すべての情報を1ファイルに集約する」という主張ではない。runtime、registry、operator docs、deployment manifestはそれぞれ異なる責務を持つ。必要なのは、層を越える意味対応と、層の内部での追跡可能な一意性である。

## 4. Finding triage

### F0 — 生の観察として保持

- PR #3016でBackend settings表内の `APP_REVISION` / `LOG_LEVEL` 重複と、同表に残る `MAX_DOCUMENT_CARDS=10000` を実際に確認した。
- `APP_REVISION` は同一表内で `未設定` と `unknown` が併存し、重複が単なる表示重複ではなく意味差も持っていた。
- PR #3017でCompose `api.environment` 内の `KJ_ATLAS_APP_REVISION` 同値重複を実際に確認した。
- Compose重複は当時のruntime behaviorを変えなかったが、片側だけが将来変更されるdrift seamだった。

### F1 — 既存の局所contractへ返す

- #3016でBackend settings表に限定したkey uniqueness + static default integrityを追加した状態を正とする。
- #3017で現在のCompose公開配送境界に限定したkey uniquenessを追加した状態を正とする。
- repository全体の任意の重複文字列を禁止する一般scannerへは広げない。

### F2 — 新Issueなし

観測した2件はすでに修正され、再発条件もそれぞれ既存contractへ固定されている。独立した未完作業は残していない。

### F3 — ADRなし

新しいconfiguration architectureではなく、既存authority / delivery surfaceの追跡可能性を回復する回帰防止である。

## 5. 一意性contractを広げすぎない境界

同じkeyがrepository内に複数回現れること自体は異常ではない。実装、registry、configuration docs、Compose、web build argsなど、異なる責務面へ同じpublic keyを配送することには意味がある。

したがって「repository内で `KJ_ATLAS_*` は1回だけ」のようなglobal uniquenessは誤りである。今回のguardが有効なのは、**一つの表、一つのservice environment、一つのbuild argsという、同じauthority / delivery surfaceの内部**に限定したからである。

R24〜R29と同様、文字列の重複だけで意味を決めず、どの境界の中で一意であるべきかを先に定義する。

## 6. 実証境界と次工程

R30はcurrent repositoryのruntime configuration contract監査から得た内部所見であり、formal Case 001 Arm Cの結果ではない。第三者価値実証、AI-IR named-provider evidenceにも加算しない。

この記録を理由に追加のpreflight、KPI、実験スキーマは作らない。新しい具体的な陽性が出なければ、formal mainlineは既知仮説から隔離したfresh contextとfrozen KJ Atlas UIでのCase 001 Arm C実走へ戻る。
