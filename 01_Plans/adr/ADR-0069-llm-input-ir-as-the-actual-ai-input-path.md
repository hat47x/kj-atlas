# ADR-0069: LLM投入IRをAI入力の実経路とする（座標・関係語彙・島階層の決着を含む）

- Status: Accepted（2026-08-29、D1=B・D3=A・D4=A 仮承認。利用者からの委譲に基づく暫定決定であり、特別に重大な安全境界変更を伴わないため実行フェーズへ移行。D2は2026-08-13に別途採択済み）
- Date: 2026-08-09
- Deciders: Project Maintainers
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models_context.py`, `03_Implement/frontend/src/domain/island_edge_aggregate.ts`, `03_Implement/frontend/src/export/abstract_map_export.ts`, `02_Architecture/llm_input_ir_spec.md`

## Context

### 発端

KJ法キャンバスの人間・生成AI協働において、**座標が意味を持つのは人間側であり、AIにとって意味を持つのはカード・島のあいだの論理的関係である**。この非対称性をキャンバスの階層構造の設計へ反映すべきではないか、という問題提起があった。

調査の結果、問いの立て方が変わった。詳細な実測は `02_Architecture/canvas-projection-asymmetry-2026-08-09.html` に記録する。本ADRはそこで挙げた候補 C1 に対応する。

### 実測された現状

**(1) AIは論理構造をほとんど受け取っていない。** `routes/ai.py` の全プロンプト構築関数（9件）を走査した結果、**`edges` を渡す関数は1件も存在しない**。`evidenceLinks` / `relationSummaries` / `claimType` / `parentIslandId` / `placardCardId` も同様。ADR-0048 D3 で固定した関係語彙（`related`/`negate`/`causal`/`mutual`/`equivalence`）はAIに一度も届いていない。

具体的な帰結:

- `POST /ai/detect-contradiction`（`ai.py:746-752`）は2枚のカードの `text` のみを受け取る。`EvidenceLink.type="contradicts"` も `contradictionState`（`unconfirmed`/`confirmed`/`held`/`resolved`）も渡らないため、人間が確定・保留済みの矛盾を再提示しうる。
- `POST /ai/suggest-card-groups`（`ai.py:725-731`）は `id` と `text` の平坦なリストのみ。既存の島・階層・`holdState` を見ずに提案する。
- `POST /ai/generate-narrative` は `readingOrder` を渡すが `edges` を渡さない。叙述の骨格である因果・対立が使えない。

**(2) 座標は1件のみ、ただし生の絶対座標。** `_build_prompt`（`ai.py:317-324`、suggest-layout）のみが `x`/`y` を渡す。出力が座標である以上これ自体は妥当だが、島についても `cardIds` のカード座標から `bounds`/`anchor` を算出して渡しており（`ai.py:326-336`）、島を関係の集合ではなく矩形として提示している。

**(3) 設計済みの投影層が4つあり、AI経路はそのすべてを迂回している。**

| 投影層 | 状態 | AI入力での使用 |
|---|---|---|
| `getDerivedIslandEdges()`（`island_edge_aggregate.ts:78`） | 実装済み・呼出5箇所 | 未使用 |
| `buildAbstractMapExport()`（`abstract_map_export.ts`） | 実装済み・座標参照ゼロ・SafeMode実装済み | 未使用 |
| `ContextBundleResponse`（`models_context.py:89`、`CE0-CTX-IF`） | stub のみ（`build_bundle()` が `_STUB_DATASET` を返す） | 未接続 |
| **`LLMRequest.inputs` IR**（`llm_input_ir_spec.md` §4） | **凍結仕様・実装ゼロ** | **なし** |

`ir_version` / `graph_summary` / `cluster_candidates` は `03_Implement` 配下に1件も出現しない。

### なぜ今この判断が必要か

4層目の存在が問題の性質を変える。`llm_input_ir_spec.md` は「LLMへ渡す前段データ」の**正本**であり、`ADR-0009`（Accepted）Phase B を完了させる凍結仕様である。そこには既に、構造的観測（`graph_summary`: 中心性・連結成分・矛盾サブグラフ）、論理由来と空間由来のクラスタ区別（`cluster_candidates.basis`）、SafeMode の入力側強制（`constraints.safe_mode: const true`、§7.1 で違反時はIR生成失敗）、決定論的切り詰め、PII最小化が設計されている。

つまり本件は「新しい投影層を作るべきか」ではなく、**「凍結済みの設計が実装されないまま、別経路が出荷された」状態をどう解消するか**である。放置するほど `routes/ai.py` の直渡し経路にエンドポイントが積み上がる。実際 2026-08-09 のコミット `2aeb23d9` は、この経路を前提とした7フェーズのデモ（`kj_canvas_demo.py`）を追加している。

### 決着が必要な論点

IR は本問題提起に既に答えを出しているが、その答えは提起とは異なる。以下は**曖昧にしたまま実装へ進めない**。

**論点1: 座標。** IR は `coordinates` を必須としつつ（§4.1）、重心を原点へ平行移動し `radius`/`angle_deg` を併記する正規化を課す（§2.2）。すなわち「絶対位置は情報ではないが、相対布置は情報である」という立場を取る。これは問題提起の「原則渡さない」とも、現状の「生の絶対座標」とも異なる第三の立場である。

**論点2: 関係語彙のドリフト。** 二つの凍結契約が食い違っている。

| 契約 | 列挙値 | 出典 |
|---|---|---|
| キャンバス（TS） | `related` / `negate` / `causal` / `mutual` / `equivalence` | `types.ts:78`、ADR-0048 D3 |
| バックエンド（Py） | 同上 ＋ `unknown` | `models.py:605` |
| **LLM投入IR** | `related` / `arrow` / `negation` | `llm_input_ir_spec.md` §2.3 / §4.2 |

`arrow` はキャンバス語彙に存在せず、`negation` は `negate` と綴りが異なり、`causal`/`mutual`/`equivalence` は IR に対応値を持たない。IR は3値への非可逆な正規化を行うことになるが、**写像表は仕様に存在しない**。

**論点3: IR に島階層が存在しない。** IR のスキーマに `islands` はない。あるのは `cluster_candidates`（AIへの候補提示）であって、人間が確定させた島ではない。`parentIslandId` による入れ子も `placardCardId` による表札も表現できない。IR はカードグラフの IR であって、キャンバス階層の IR ではない。問題提起の「階層構造の設計上意識する必要がある」は、まさにここに当たる。

**論点4: 投影の実装場所。** 既存投影は TypeScript にある。サーバ側で投影するなら Python 実装が要り、TS↔Python の第2の契約ドリフト源になる（`test_ts_python_contract_drift.py` の対象）。

### ADR-0047 ゲート判定

**R-3（非機能境界の超過）に該当すると判断する。** `ADR-0009`（Accepted）の凍結仕様と出荷実装が乖離しており、`ADR-0041` の CVI 群のうち入力側の保証（CVI-2 proposal-only の前提となる入力健全性、SafeMode 保護）が、契約ではなくフロントエンド実装のみに依存している。

**R-1（実使用の摩擦）ではない。** 本件はコード監査から出ており、ドッグフードや実利用で観測された摩擦ではない。`ADR-0067` / `ADR-0068` と同じ性質である。

## Decision

**凍結仕様 `llm_input_ir_spec.md` を AI 入力の実経路とし、その適用にあたって以下 D1〜D4 を決する。**

> 以下の推奨は起票者の見解であり、**採択は保守者が行う**。実装は採択後の決定に従うこと。

### D1: 座標の扱い

| 案 | 内容 | 評価 |
|---|---|---|
| A | IR §2.2 の正規化座標を**必須のまま**維持（現仕様どおり） | 仕様変更ゼロ。ただし関係だけで足りるエンドポイントにも座標を強制し、問題提起の懸念が残る |
| **B（推奨）** | `coordinates` を**任意**へ緩和し、エンドポイントごとに要否を宣言する | `suggest-layout` は「要る」と宣言、`detect-contradiction` は宣言しない。用途に即し、かつ渡す場合は §2.2 の正規化を必ず経る |
| C | `suggest-layout` 以外では完全に除去 | 最も保守的。ただし将来「空間的まとまりの気づき」を扱う余地を閉じる |

**推奨は B。** 問題提起が拒否しているのは「AIに配置を解釈させること」であり、IR は `cluster_candidates.basis="spatial"` によって空間由来を明示ラベル付けすることで、その暗黙化を既に防いでいる。B なら「相対布置を渡すか否か」をエンドポイント単位で明示的に選べる。

**決定（2026-08-29・仮承認）**: **D1=B を採択**。`coordinates` を任意フィールドへ緩和し、`suggest-layout` は要求、他エンドポイント（`detect-contradiction`/`suggest-card-groups`/`generate-narrative`）は非要求とする。実装時にエンドポイントごとの要否表を `llm_input_ir_spec.md` へ明記する。

### D2: 関係語彙の写像

| 案 | 内容 | 評価 |
|---|---|---|
| **A（推奨）** | IR の `relations.type` をキャンバス語彙5値へ拡張する | キャンバス語彙は人間が確定させた言語化そのものであり、これを潰すと本ADRの目的（論理関係をAIへ届ける）が達成できない |
| B | 3値を維持し、写像表を仕様へ明記する（非可逆であることを含めて） | 仕様変更が小さい。ただし `causal` を `arrow` へ潰すと叙述の骨格が失われ、上記(1)の問題が IR 経由で再発する |
| C | `type`（3値）と `type_source`（原語彙）を併記する | 後方互換だが冗長で、消費側がどちらを見るべきか曖昧になる |

**推奨は A。** あわせて `unknown`（`models.py:605`）の扱いを決めること。

**決定（2026-08-13・仮承認）**: **D2=A を採択**。`llm_input_ir_spec.md` の `relations.type` をキャンバス5値 `related | negate | causal | mutual | equivalence` へ統一（`arrow`→`causal`、`negation`→`negate`）。`unknown` は IR に含めない（未分類は構造値として意味を持たない）。逆方向（IR→キャンバス）写像は行わない。

### D3: 島階層の表現

| 案 | 内容 | 評価 |
|---|---|---|
| **A（推奨）** | IR に `islands`（人間が確定させたもの）を追加し、`cluster_candidates`（AIへの候補）と**型として分ける** | CVI-2（proposal-only）/ CVI-3（人手レビュー昇格のみ）と一致する。`AbstractMapExportIsland` が既にこの形を持つ |
| B | `cluster_candidates` に `confirmed: boolean` を足す | 変更は小さいが、確定済みの島と機械が出した候補が同じ型に同居し、消費側が取り違えうる |
| C | 階層は渡さない（現状維持） | 問題提起の中心（階層構造）に答えない |

**推奨は A。** 追加する `islands` には最低限 `id` / `card_ids` / `title` / `placard_card_id` / `parent_island_id` / レビュー状態を含めること。

**決定（2026-08-29・仮承認）**: **D3=A を採択**。ただし実装は下記「前提条件」節の解消（`DOMAIN-ISLAND-MEMBERSHIP-01`）を先行させること。

### D4: 投影の実装場所

| 案 | 内容 | 評価 |
|---|---|---|
| **A（推奨）** | サーバ（Python）で IR を構築し、TS 既存実装との同値性をテストで固定する | SafeMode をサーバ側で強制できる（下記 ADR-0068 との関係を参照）。ドリフトは `test_ts_python_contract_drift.py` の拡張で管理する |
| B | フロントエンドが IR を組み立てて送る | **推奨しない。** サーバがクライアント構築の投影を信頼することになり、`SEC-AI-SAFEMODE-01` が指摘した迂回経路をそのまま残す |
| C | 投影ロジックを Python へ一本化し TS 側を削除する | 描画・export がサーバ往復を要することになり、ローカルファースト（`architecture.html`）に反する |

**推奨は A。**

**決定（2026-08-29・仮承認）**: **D4=A を採択**。サーバ側（Python）にIRビルダーを実装し、`test_ts_python_contract_drift.py` の対象へ投影ロジックを追加する。

### 仕様バージョンについて

IR スキーマは `ir_version: {"const": "1.0"}` かつ `additionalProperties: false` で固定されている。D1〜D3 のいずれを採っても**スキーマ変更を伴うため `ir_version` の繰り上げが必要**である。採択時に新版数を決めること。

### 非目標

- LLM出力スキーマ（`LLMRequest.output_schema`）の設計。IR §0.2 の非目標を引き継ぐ。
- Provider transport の選定。同上。
- `POST /ai/assess-card-importance` の採点と `DOM-AI-07`（`00_Prompt/domain.md` §7「カード品質を点数・順位・合否で評価する」の禁止。主体を問わない上位規定は `DOM-CORE-04`）の抵触。`issue-AI-IMPORTANCE-SCORING-01` で採点APIを廃止して解消済み。本ADRが将来提供する`graph_summary`は、順位や等級を持たない構造的観測（中心性・連結成分・矛盾サブグラフ）に限定する。
- IR の上限値（`MAX_CARDS=200` / `MAX_RELATIONS=400` / `MAX_TEXT_CHARS=12000`、§5.1）が現行規模に妥当かの再検討。実装時に代表規模で計測し、必要なら別途起票する。

## Three-Element Verification（ADR-0067 遡及適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | KJ法キャンバスでは座標が意味を持つのは人間側で、AIにとって意味を持つのはカード・島の論理的関係。この非対称性を踏まえ、AIは論理構造（関係語彙・島階層・holdState）を実際に受け取る必要がある | 機能: `routes/ai.py`の全プロンプト構築関数で`edges`/`evidenceLinks`/`relationSummaries`/`claimType`/`parentIslandId`を渡す。データ: 関係語彙（related/negate/causal/mutual/equivalence）をAIへ届ける |
| **データ設計** | 凍結済みの`LLMRequest.inputs` IR（llm_input_ir_spec.md §4）をAI入力の実経路とする。`graph_summary`（中心性・連結成分・矛盾サブグラフ）は順位や等級を持たない構造的観測に限定。SafeModeの入力側強制（constraints.safe_mode）とPII最小化をサーバ側契約へ | 業務: 矛盾検出が既存`evidenceLinks`を、グルーピング提案が既存の島を見る。機能: 決定論的切り詰め（MAX_CARDS=200/MAX_RELATIONS=400/MAX_TEXT_CHARS=12000）で大規模文書のAI入力を再現可能にする |
| **機能設計** | 既存の4投影層（island_edge_aggregate/abstract_map_export/ContextBundle/LLMRequest.inputs IR）のうちIRを実装してAI経路へ接続。`POST /ai/*`はIRを経由し、直渡し経路にエンドポイントを積み上げない | 業務: 採点API（assess-card-importance）は廃止済み（issue-AI-IMPORTANCE-SCORING-01）。データ: 座標はsuggest-layoutの出力に限定し、島を矩形でなく関係の集合として提示 |

## Consequences

### 期待される効果

- ADR-0048 D3 で固定した関係語彙が、はじめてAIへ届く。矛盾検出が既存の `evidenceLinks` を、グルーピング提案が既存の島を見るようになる。
- SafeMode の入力側保護が、フロントエンド実装依存からサーバ側の契約へ移る（IR §7.1）。
- PII最小化（IR §7.2）と構造化テキスト限定（§7.3）が、現在は存在しない防御として入る。
- 決定論的な切り詰め（§5）により、大規模文書でのAI入力が再現可能になる。
- `graph_summary` により、採点によらない構造的観測が可能になる。

### 想定される副作用・制約

- **TS↔Python の第2のドリフト源が生まれる**（D4=A の代償）。`test_ts_python_contract_drift.py` の対象を投影ロジックへ拡張して管理する。
- **入力トークン量が変わる**。関係・階層・`graph_summary` が増える一方、生座標が減る。差し引きは未計測であり、実装時に代表規模（カード300・島30程度）で測ること。
- **`ir_version` の繰り上げ**が必要（上述）。`llm_input_ir_spec.md` §8 のトレーサビリティと FixtureProvider 回帰データ（§6）の再生成を伴う。
- 既存の `/ai/*` 呼び出し側（フロントエンド、`kj_canvas_demo.py`）に改修が要る。

### ADR-0068 との関係（重要）

`ADR-0068`（SafeMode enforcement at API boundary、Proposed）と本ADRは**同じ境界を対象としており、独立に実装すると衝突する**。

- `ADR-0068` は `/ai/*` の各リクエストモデルへ `safeMode` を追加する方向。
- 本ADR D4=A は、IR 構築をサーバ側へ置き、IR §7.1 が `safe_mode` を強制する方向。

本ADRが採択される場合、`ADR-0068` の D1（safeMode の伝達方法）は本ADRに吸収されうる。**両者を別々のAIエージェントが並行して実装しないこと。** 採択順序を決め、後続側はその決定を前提に再検討すること。

### 移行時に必要な対応

1. `llm_input_ir_spec.md` を D1〜D3 の決定に従って改訂し、`ir_version` を繰り上げる。
2. サーバ側に IR ビルダーを実装する（D4=A の場合）。
3. `/ai/*` の各エンドポイントを IR 経由へ切り替える。段階適用の場合は論理関係が効く順（`detect-contradiction` → `suggest-card-groups` → `generate-narrative` → `suggest-layout`）を推奨する。
4. `test_ts_python_contract_drift.py` を投影ロジックへ拡張する。
5. `02_Architecture/api.md` のリクエスト契約を同期する。

### 前提条件

`02_Architecture/functional-dependency-integrity-2026-08-06.html` の **F-5「島所属の関数従属性が強制されていない」が未解消**である。カード→島の所属が一意に定まらない状態では、`islands` を含む IR の構築結果が一意にならない。本ADRの実装前に F-5 を解消するか、投影側で一意化規則（先勝ち・後勝ち・全列挙のいずれか）を明示すること。

**決定（2026-08-29）**: 書込み側のドラッグ&ドロップ経路は既に単一所属を強制済み（`island_edge_aggregate.ts` `moveCardToIsland()`）と確認したが、統合（canonicalization）経路（`canonical_ops.ts` `updateIslands()`）は跨島マージ時に重複所属を生成しうることを新たに確認した（`issue-DOMAIN-ISLAND-MEMBERSHIP-01`）。同issueが追加する助言的診断が実運用データでの発生頻度を計測するまでの**暫定の一意化規則として「先勝ち」（`getIslandsForCard()`/`islands.find()` が既に実装している、配列先頭から見て最初に一致した島を採用する）を採用する**。IRビルダー（D4=A）は、複数島に同時出現するカードについてこの規則で単一の `island_id` を選ぶこと。`issue-DOMAIN-ISLAND-MEMBERSHIP-01` のAC-1〜2が完了するまで、本ADRの `islands` 実装（D3）には着手しない。

## Traceability

- Related: `02_Architecture/canvas-projection-asymmetry-2026-08-09.html`（本ADRの根拠となる実測と分析）
- Related: `02_Architecture/llm_input_ir_spec.md`（改訂対象の正本）
- Related: `01_Plans/adr/ADR-0009-local-llm-integration.md`（Phase B の完了宣言元）
- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 で関係語彙を固定）
- Related: `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`（CVI-2 / CVI-3 / CVI-7）
- Related: `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`（再起票ゲート R-3 の判定根拠）
- Related: `01_Plans/adr/ADR-0068-safemode-enforcement-at-api-boundary.md`（**境界が重複する。上記「ADR-0068 との関係」を参照**）
- Related: `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`（本ADR採択後の実装課題）
- Related: `01_Plans/issues/issue-AI-REL-VOCAB-DRIFT-01-ir-canvas-relation-type-mismatch.md`（D2 で解決される事実の記録）
- Related: `01_Plans/issues/issue-AI-IMPORTANCE-SCORING-01-importance-rating-conflicts-with-no-scoring.md`（非目標として分離した課題）
- Related: `02_Architecture/functional-dependency-integrity-2026-08-06.html`（F-5 = 実装前提条件）
- Related: `01_Plans/issues/issue-DOMAIN-ISLAND-MEMBERSHIP-01-cross-island-cardid-duplicate-detection.md`（F-5前提条件の実装課題、Draft）

---
