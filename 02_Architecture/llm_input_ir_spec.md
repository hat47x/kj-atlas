# English Summary

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
This document finalizes ADR-0009 Phase B by defining deterministic KJ input normalization, non-LLM graph preprocessing, the strict LLM input IR schema, truncation behavior, fixture generation verification steps, and safety/privacy consistency checks.

# llm_input_ir_spec — LLM投入IR仕様（ADR-0009 Phase B 完了）

本仕様は `ADR-0009` の Phase B（データ/IR整備）を完了させるための正本である。  
対象は「LLMへ渡す前段データ」のみであり、モデル実装や推論品質評価ルーブリック自体は対象外とする。

> CE1 Context foundation integration note: `ContextQuery` / `ContextBundle` の契約固定（`previewConfirmed` 必須、canonical hash）は `02_Architecture/api.md` と `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` を正本とし、本書では IR 接続時の整合条件のみを規定する。

---

## 0. Scope / Non-Goals / Acceptance Criteria

### 0.1 Scope

1. KJ入力正規化の固定（`cards` / `coordinates` / `relations` / `meta`）。
2. 非LLM前処理の固定（クラスタ候補・中心性・連結成分・矛盾サブグラフ）。
3. LLM投入IR（`LLMRequest.inputs`）の JSON schema・必須/任意・サイズ上限・切り詰め規則の固定。
4. FixtureProvider回帰データを IR 仕様のみで生成可能であることの検証手順の提供。
5. safeMode / PII最小化 / 構造化テキスト限定の整合チェック項目の固定。

### 0.2 Non-Goals

1. LLM出力スキーマ（`LLMRequest.output_schema` の中身）の設計。
2. Provider transport 実装（HTTP / IPC / in-process）の選定。
3. エスカレーション有効化手順そのもの（`llm_escalation_policy.md` の領域）。
4. 画像・音声・バイナリ添付の取り扱い。

### 0.3 Acceptance Criteria

- AC-1: 本仕様の正規化入力だけで `LLMRequest.inputs` を決定論的に生成できる。
- AC-2: 非LLM前処理4種の出力形式と計算規則が曖昧語なしで定義されている。
- AC-3: サイズ上限超過時に、同一入力から同一切り詰め結果を再現できる。
- AC-4: FixtureProvider用回帰データを、LLM依存なしで生成・比較できる。
- AC-5: safeMode / PII最小化 / 構造化テキスト限定の検査が、実行チェックリストとして明文化されている。

---

## 1. 用語と識別子

- **canonical card id**: `Card.id` の正規ID。
- **relation id**: `"<type>:<fromId>:<toId>"`（文字列連結）で決定論生成。
- **negation relation**: `relations[*].type == "negation"`。
- **IR**: `LLMRequest.inputs` に格納する JSON。
- **structured text only**: JSONで表現可能な文字列・数値・配列・オブジェクトのみを許可し、バイナリを禁止する。
- **queryCanonicalHash**: canonical 化した `ContextQuery` から算出する sha256 16進小文字。
- **bundleHash**: canonical 化した `ContextBundle` から算出する sha256 16進小文字。

---

## CE1 Bridge Constraints（ContextQuery/Bundle 連携制約）

本節は Phase 1〜6 の CE1 固定契約を、IR生成境界で破らないための拘束条件を定義する。

1. `previewConfirmed != true` の `ContextQuery` から IR 生成を開始してはならない（APIは `422 preview_required` を返す前提）。
2. `queryCanonicalHash` と `bundleHash` は、IRメタデータに監査キーとして保持可能でなければならない。
3. IR生成パイプラインは、同一 canonical query に対する `bundleHash` 不一致を検知した場合に `nondeterministic_bundle` として失敗扱いにする。
4. CE2/CE4 連携では backend 未実装時も mock `ContextQuery/ContextBundle` 契約で検証を継続し、CE1完了待ちを禁止する。
5. 実行順序は `Plan -> Execute -> Verify -> Proceed` を固定し、`Proceed` は CE2/CE4 への参照専用引継ぎのみ許可する。
6. Verify 失敗時の自己修復は最大3回までとし、3回超過時は処理継続せず停止する（fail-closed）。
7. `ContextQuery/ContextBundle` は CE1 v1 最小I/F以外の未定義キーを受理してはならない（拡張は v2 契約改訂でのみ許可）。
8. 契約ID衝突（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）または safeMode 後退を検知した場合は即停止する。
9. CE2提案連携では `sourceBundleHash/status/reviewState` を必須監査キーとして扱い、proposal-only 境界（auto-apply禁止）を破ってはならない。

### CE1 Contract Lock Summary（Stream B）

- 署名（識別）固定: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
- 型固定: `ContextQueryV1` / `ContextBundleV1` の v1 必須キー集合を closed-world として固定
- エラー固定: `422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle`
- mock-first 固定: `stubDatasetId=A2-minimal-v1` で検証し、実DB/実LLM/worker 依存を禁止
- Verify自己修復上限: 3回（超過時は `held` で停止）

### CE1 A2 Stub Contract Profile（検証用）

CE1 の IR 接続検証（A2）は backend 完了待ちを禁止し、次の stub contract を最小プロファイルとして固定する。

- `POST /context/query`
  - request: `ContextQueryV1`（closed-world、未定義キー禁止）
  - success: `200 { accepted: true, queryCanonicalHash }`
  - error: `422 preview_required` / `400 unknown_contract_key`
- `POST /context/bundle`
  - request: `{ query: ContextQueryV1, stubDatasetId: "A2-minimal-v1" }`
  - success: `200 ContextBundleV1 + queryCanonicalHash`
  - error: `409 nondeterministic_bundle` / `400 unknown_contract_key`



### CE1 Execution Order Lock（Stream B）

CE1 Contract 作業は次の順序を固定し、逆順・省略を禁止する。

1. Phase 1 Read
2. Phase 2 ADR CDC
3. Phase 3 Plan（AC/DoD提案合意を先に確定）
4. Phase 4 Execute（契約固定：`ContextQuery` / `ContextBundle` / `bundleHash` / `previewConfirmed`）
5. Phase 5 Verify（preview gate + 決定論 hash、自己修復は3回まで）
6. Phase 6 Proceed（参照専用 handoff）

Phase 5 Verify は最低限次の機械判定を満たすこと。

- `previewConfirmed=false -> 422 preview_required`
- 同一 canonical query を3回実行し `queryCanonicalHash` と `bundleHash` が 3/3 一致
- 未定義キーは常に `400 unknown_contract_key`

Phase 6 Proceed は CE2/CE4 への参照専用連携のみ許可し、実装変更要求を禁止する。CE2/CE4 は mock 契約で依存切断したまま進行し、CE1 完了待ちを禁止する。

A2 contract test では次を機械判定する。

1. 同一 canonical query 3回実行で `queryCanonicalHash` と `bundleHash` が 3/3 一致。
2. `previewConfirmed=false` が常に `422 preview_required`。
3. 未定義キーが常に `400 unknown_contract_key`。
4. CE2 連携キー `sourceBundleHash === bundleHash` を比較可能。

---



### Stream C CE1 Foundation Lock（2026-05-04）

- 本仕様における CE1 責務は **契約固定のみ** とし、実装詳細（handler/UI/DB/worker）を追加しない。
- `ContextQueryV1` / `ContextBundleV1` は closed-world v1 を維持し、未定義キーは常に `400 unknown_contract_key`。
- preview gate は `previewConfirmed=false -> 422 preview_required` を固定し、IR 生成を開始しない。
- hash 決定論は同一 canonical query で `queryCanonicalHash` / `bundleHash` が 3/3 一致を要件化し、不一致は `409 nondeterministic_bundle`。
- CE2/CE4 は mock-first で依存切断を維持し、CE1実装待ちを禁止する（contract handoff のみで前進）。

## 2. KJ入力正規化（固定仕様）

### 2.1 cards

入力 `cards` は以下へ正規化する。

```json
{
  "id": "string",
  "text": "string",
  "text_norm": "string",
  "char_len": 0
}
```

規則:

1. `id` は空文字禁止。
2. `text` は UTF-8 文字列。制御文字（U+0000..U+001F, U+007F）は除去する。
3. `text_norm` は次で生成する。
   - NFKC正規化
   - 連続空白を1スペースへ畳み込み
   - 前後空白を除去
4. `char_len` は `text_norm` の文字数。
5. 同一 `id` が複数ある場合は入力不正として reject する。

### 2.2 coordinates

入力座標は以下へ正規化する。

```json
{
  "card_id": "string",
  "x": 0.0,
  "y": 0.0,
  "radius": 0.0,
  "angle_deg": 0.0
}
```

規則:

1. `x`, `y` は有限実数（NaN / ±Inf 禁止）。
2. 座標は重心基準へ平行移動して正規化する。
   - 重心 `cx = mean(x)`, `cy = mean(y)`
   - 正規化後 `x = round(x - cx, 3)`, `y = round(y - cy, 3)`
3. `radius = round(sqrt(x^2 + y^2), 3)`。
4. `angle_deg = round(atan2(y, x) * 180 / pi, 3)`（範囲 -180.000..180.000）。
5. `card_id` は `cards.id` に存在しなければ reject。

### 2.3 relations

入力関係は以下へ正規化する。

```json
{
  "id": "string",
  "from": "string",
  "to": "string",
  "type": "related|arrow|negation"
}
```

規則:

1. `from`, `to` は `cards.id` に存在すること。
2. `type` は列挙値のみ許可。
3. 重複判定キー `(from, to, type)` が重複した場合は1件へ重複排除する。
4. 自己ループ（`from == to`）は `negation` 以外は reject。
5. 正規化後の並び順は `(type, from, to)` 昇順。

### 2.4 meta

`meta` は以下の最小フィールドへ固定する。

```json
{
  "doc_id": "string",
  "doc_version": 1,
  "safe_mode": true,
  "language": "ja|en|mixed|unknown",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

規則:

1. `safe_mode` は必須かつ `true` でなければ IR 生成を拒否する。
2. `doc_version` は正整数。
3. `language` 判定不能時は `unknown` を使用する。
4. `meta` に個人識別子（メール、電話、住所、外部ID）を含めない。

---

## 3. 非LLM前処理（固定仕様）

### 3.1 クラスタ候補（cluster_candidates）

```json
{
  "cluster_id": "cc-0001",
  "card_ids": ["c1", "c2"],
  "basis": "relation|spatial",
  "score": 0.0
}
```

計算規則:

1. relation-based 候補: `related|arrow` 辺で連結な部分集合を列挙。
2. spatial-based 候補: 座標距離の近傍グラフ（k=3）で連結な集合を列挙。
3. 同一 `card_ids` は `basis` を統合し1件にする（`relation` 優先）。
4. `score` は `round(min(1.0, density + cohesion) / 2, 4)`。

### 3.2 中心性（centrality）

```json
{
  "card_id": "c1",
  "degree": 0,
  "betweenness": 0.0,
  "rank": 1
}
```

計算規則:

1. 無向グラフとして `degree` を計算。
2. betweenness centrality を標準定義で計算し小数4桁へ丸める。
3. 並び順は `betweenness desc`, 同値時 `degree desc`, 同値時 `card_id asc`。
4. `rank` は上記順序の1始まり連番。

### 3.3 連結成分（connected_components）

```json
{
  "component_id": "cmp-001",
  "card_ids": ["c1", "c2"],
  "edge_count": 1
}
```

計算規則:

1. `related|arrow|negation` を全て無向辺として成分分解する。
2. `component_id` は card_ids の最小ID順に `cmp-001` から連番。
3. `card_ids` は昇順ソート。
4. `edge_count` は当該成分内の正規化 relation 数。

### 3.4 矛盾サブグラフ（contradiction_subgraphs）

```json
{
  "subgraph_id": "neg-001",
  "card_ids": ["c3", "c7"],
  "negation_edges": ["negation:c3:c7"],
  "summary": "string"
}
```

計算規則:

1. `negation` 辺を含む成分ごとに1サブグラフを作る。
2. `summary` はテンプレート生成のみ許可する。
   - 形式: `"<n> negation edges across <m> cards"`
3. LLM要約は禁止（前処理は純決定論）。

---

## 4. LLM投入IR JSON Schema（LLMRequest.inputs）

### 4.1 必須/任意

必須:
- `ir_version`
- `cards`
- `coordinates`
- `relations`
- `graph_summary`
- `constraints`

任意:
- `cluster_candidates`
- `truncation`

### 4.2 JSON Schema（Draft 2020-12相当）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "ir_version",
    "cards",
    "coordinates",
    "relations",
    "graph_summary",
    "constraints"
  ],
  "properties": {
    "ir_version": { "type": "string", "const": "1.0" },
    "cards": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "text", "text_norm", "char_len"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "text": { "type": "string", "minLength": 1 },
          "text_norm": { "type": "string", "minLength": 1 },
          "char_len": { "type": "integer", "minimum": 1 }
        }
      }
    },
    "coordinates": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["card_id", "x", "y", "radius", "angle_deg"],
        "properties": {
          "card_id": { "type": "string", "minLength": 1 },
          "x": { "type": "number" },
          "y": { "type": "number" },
          "radius": { "type": "number", "minimum": 0 },
          "angle_deg": { "type": "number", "minimum": -180, "maximum": 180 }
        }
      }
    },
    "relations": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "from", "to", "type"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "from": { "type": "string", "minLength": 1 },
          "to": { "type": "string", "minLength": 1 },
          "type": { "type": "string", "enum": ["related", "arrow", "negation"] }
        }
      }
    },
    "cluster_candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["cluster_id", "card_ids", "basis", "score"],
        "properties": {
          "cluster_id": { "type": "string", "minLength": 1 },
          "card_ids": { "type": "array", "minItems": 2, "items": { "type": "string" } },
          "basis": { "type": "string", "enum": ["relation", "spatial"] },
          "score": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    },
    "graph_summary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["centrality", "connected_components", "contradiction_subgraphs"],
      "properties": {
        "centrality": { "type": "array" },
        "connected_components": { "type": "array" },
        "contradiction_subgraphs": { "type": "array" }
      }
    },
    "constraints": {
      "type": "object",
      "additionalProperties": false,
      "required": ["safe_mode", "structured_text_only", "required_sections"],
      "properties": {
        "safe_mode": { "type": "boolean", "const": true },
        "structured_text_only": { "type": "boolean", "const": true },
        "required_sections": {
          "type": "array",
          "items": { "type": "string", "enum": ["overall", "clusters", "contradictions"] },
          "minItems": 3,
          "maxItems": 3,
          "uniqueItems": true
        }
      }
    },
    "truncation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["truncated", "reason_codes"],
      "properties": {
        "truncated": { "type": "boolean" },
        "reason_codes": {
          "type": "array",
          "items": { "type": "string", "enum": ["MAX_CARDS", "MAX_RELATIONS", "MAX_TEXT_CHARS"] }
        }
      }
    }
  }
}
```

---

## 5. サイズ上限と切り詰め規則（決定論）

### 5.1 上限値

- `MAX_CARDS = 200`
- `MAX_RELATIONS = 400`
- `MAX_TEXT_CHARS = 12000`（`sum(cards[*].char_len)`）

### 5.2 切り詰め順序

超過時は次を上から順に適用し、各段階で上限内か判定する。

1. `cluster_candidates` を全削除（任意フィールドのため）。
2. `centrality.rank` 低位カードからカードを除外。
3. 除外カードに接続する relation を除外。
4. なお超過する場合は `text` を `text_norm` 先頭 240 文字へ固定切り詰め。

### 5.3 記録

- 切り詰めを1回でも実施した場合、`truncation.truncated=true`。
- 該当した上限の理由コードを重複なしで `reason_codes` へ記録。

---

## 6. FixtureProvider回帰データ生成手順（IR仕様のみで再現）

1. 入力 `document.json` から `cards / coordinates / relations / meta` を抽出する。
2. 本仕様 2章の正規化規則を適用して `normalized_input.json` を生成する。
3. 本仕様 3章の前処理規則を適用して `graph_features.json` を生成する。
4. 本仕様 4章の schema に従って `llm_ir.json`（= `LLMRequest.inputs`）を生成する。
5. 本仕様 5章の上限チェックと切り詰めを適用する。
6. `llm_ir.json` を fixture key の唯一入力として FixtureProvider応答を引き当てる。
7. 回帰テストは `llm_ir.json` のハッシュ（SHA-256）一致で前段の再現性を判定する。

検証成功条件:

- 同一 `document.json` から常に同一 `llm_ir.json` が生成される。
- provider未起動（`KJ_ATLAS_LLM_PROVIDER=none`）でも回帰が成立する。

---

## 7. safeMode・PII最小化・構造化テキスト限定 整合チェック

### 7.1 safeModeチェック

- `meta.safe_mode == true` を必須化。
- `constraints.safe_mode == true` を必須化。
- どちらかが欠ける、または `false` の場合は IR 生成を失敗させる。

### 7.2 PII最小化チェック

以下パターンに一致する文字列を `text` / `text_norm` / `meta` で検出した場合、IR生成を失敗させる。

- メール: `/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/`
- 電話: `/\+?[0-9][0-9\- ]{8,}[0-9]/`
- URLクエリ中トークン: `/[?&](token|key|secret|password)=/i`

### 7.3 構造化テキスト限定チェック

- JSON型は `string|number|boolean|array|object|null` のみ。
- Base64疑似バイナリ（長さ1024超かつ `[A-Za-z0-9+/=]` のみ）を禁止。
- `attachments` / `binary` / `image` というキー名の出現を禁止。

---

## 8. トレーサビリティ

- Plan正本: `01_Plans/adr/ADR-0009-local-llm-integration.md` Phase B。
- Provider契約: `02_Architecture/llm_provider_spec.md`（`LLMRequest.inputs` の意味境界）。
- 実行制約: `02_Architecture/llm_runtime_constraints.md`。
- 品質ゲート: `02_Architecture/llm_quality_strategy.md`。
- エスカレーション運用: `02_Architecture/llm_escalation_policy.md`。


## 9. CE-1 ContextQuery/ContextBundle 最小I/F（Contract Freeze）

### 9.1 Context

- 本章は ADR-0028 CE-1 の「同一query同一bundleHash」を機械判定可能にするため、LLM入力IRの前段契約を固定する。
- 本章の契約は mock 実装でも同一に適用し、backend/frontend 依存を切離す。

### 9.2 Decision

`POST /context/query` と `POST /context/bundle` の論理契約を以下で固定する。

```json
{
  "ContextQuery": {
    "queryId": "uuid",
    "goal": "string",
    "scope": "document|view|island",
    "depth": "integer(0..5)",
    "constraints": {"maxTokens": "integer>0", "timeBudgetMs": "integer>0"},
    "reviewFilter": "reviewedOnly|includeUnreviewed",
    "safeModePolicy": "strict",
    "outputMode": "summary|proposal|candidate",
    "previewConfirmed": true
  }
}
```

```json
{
  "ContextBundle": {
    "bundleHash": "sha256-hex",
    "selected": [],
    "relations": [],
    "evidence": [],
    "contradictions": [],
    "reviewFlags": {"reviewed": 0, "unreviewed": 0},
    "truncationMeta": {"applied": false, "reasons": []},
    "excludedReason": []
  }
}
```

`bundleHash` 算出規則（固定）:
1. 非決定論フィールド除外（timestamp/trace/latency）。
2. 配列順序固定（selected=id asc, relations=(type,from,to) asc, evidence=cardId asc, contradictions=(weight desc,id asc)）。
3. canonical JSON 化（キー辞書順、UTF-8、空白なし）。
4. `sha256(canonical_json)` の16進小文字を採用。

### 9.3 Consequences

- CE-2+ は `sourceBundleHash` に `ContextBundle.bundleHash` を必須連携する。
- `previewConfirmed=false` は bundle 生成前に `422 preview_required` とする（Query Previewバイパス禁止）。
- 未定義キーを含む request は `400 unknown_contract_key` として reject する（CE1 v1 closed-world）。
- 同一 canonical query で `bundleHash` が不一致となる場合は `409 nondeterministic_bundle` として fail-closed する。
- `safeModePolicy=strict` + `reviewFilter=reviewedOnly` では未レビュー本文を入力IRへ含めない。
- 機械判定式: `canonical(queryA)==canonical(queryB) && hashA==hashB` が真であること。
- CE4監査では `queryId` / `queryCanonicalHash` / `bundleHash` / `excludedReason` の4キーを欠落させてはならない。

#### A2-minimal-v1 ambiguity semantics

`A2-minimal-v1` は、曖昧さを解決済みの事実へ変換しないことも検証する。固定stub内の選択項目、関係、根拠、反対意見は、次の意味情報を持つ。

- `claimType` は既存のドメイン語彙を使い、レビュー済みであっても仮説を事実として扱わない。
- `resolutionState="unresolved"` は、利用者による判断がまだ完了していないことを示す。
- `aiDisposition="constraint"` は、AI入力で結論ではなく制約として扱うことを示す。
- `autoResolve=false` は、AI、worker、APIが自動的に解決済みへ変更してはならないことを示す。
- `safeModePolicy=strict` では未レビュー本文を `selected` から除外する一方、本文を含まない根拠・反対意見・矛盾の存在は制約として保持できる。

これらは `ContextBundleV1` のトップレベルキーを増やすものではなく、固定stubの意味論を検証するための値である。永続データの状態語彙やレビュー権限を変更する場合は、別issue/ADRで扱う。

---

## Stream A CE0/HIL Contract Snapshot Linkage (2026-04-16)

### Context
- CE0/HIL 契約凍結（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF`）は IR 生成境界で後退させてはならない。

### Decision
- 本仕様の CE1 Bridge Constraints は、`CE0-HIL-CONTRACT-SNAPSHOT-2026-04-16-v1` を参照し、次を固定する。
  - `previewConfirmed=true` 必須
  - deterministic `queryCanonicalHash` / `bundleHash`
  - safeMode後退禁止
  - proposal-only 境界（direct write / auto-apply 禁止）

### Consequences
- Verifyで契約ドリフトを検知した場合は IR生成を停止し、Self-Correction は最大3回。
- 下流は snapshot 参照のみ可とし、契約更新は CE0/A1 issue 側でのみ実施する。

### Snapshot Metadata
- Snapshot ID: `CE0-HIL-CONTRACT-SNAPSHOT-2026-04-16-v1`
- Version: `1.0.0`
- Hash (sha256): `851849b770825eb4844d46c77bae34bbefb4aec1ae9bd004e7dc4d50b875a698`

## Stream B Contract Vocabulary Sync Note（2026-04-17）

本書で扱う CE0/CE1/CE2 契約語彙は次で固定する。

- CE0: `safeMode` 後退禁止 / Consensus direct write 禁止 / auto-apply 禁止
- CE1: `ContextQuery` / `ContextBundle` / `queryCanonicalHash` / `bundleHash` / `previewConfirmed`
- CE2: `proposal-only` / `proposalId` / `diff` / `sourceBundleHash` / `status` / `reviewState` / `held`

上記語彙の意味変更・列挙値変更・安全境界変更は本書単独で行わず、Issue 契約（CE0/CE1/CE2）で CDC 承認後に同期する。


## CE1 contract freeze sync note（2026-05-06 / Stream B）

- `ContextQueryV1` / `ContextBundleV1` の required key と意味論は v1 凍結を維持する。
- IR 生成前提ゲートとして `previewConfirmed=true` を必須化し、違反は `422 preview_required` とする。
- unknown key は `400 unknown_contract_key`、hash非決定論は `409 nondeterministic_bundle` の fail-closed を維持する。
- 同一 canonical query 3回実行で `queryCanonicalHash` / `bundleHash` が 3/3 一致する検証を mock-first 基準とする。

## CE1 contract-freeze note（2026-05-07 / Stream B）

- 本仕様は CE1 `ContextQueryV1` / `ContextBundleV1` を **contract-only / mock-first** 境界として参照する。
- IR 生成は Query Preview 完了後のみ許可し、`previewConfirmed=false` は `422 preview_required` で停止する。
- v1 は closed-world とし、未定義キーは `400 unknown_contract_key` とする。
- 同一 canonical query に対して `queryCanonicalHash` / `bundleHash` が一致しない場合は `409 nondeterministic_bundle` で fail-closed とする。
- 本節は実装方式を拘束せず、契約語彙と検証条件のみを固定する。

## CE0 Contract Matrix Freeze（CTX / SAFEMODE / REVIEW）

本節は CE0 契約行列を IR 仕様上で凍結する。実装進捗に依存せず、後退不能の契約境界として扱う。

| Contract ID | Domain | Frozen rule | Regression check |
| --- | --- | --- | --- |
| `CE0-CTX-IF` | CTX | `ContextQuery/ContextBundle` は preview gate (`previewConfirmed=true`) を満たした場合のみ IR 生成を許可する。 | `previewConfirmed=false` は常に `422 preview_required`。 |
| `CE0-SAFEMODE-IF` | SAFEMODE | safeMode 既定 `ON`（`meta.safe_mode=true`）を必須とし、`reviewFilter=reviewedOnly` を既定境界として保持する。 | safeMode OFF 入力、unreviewed 混入、既定値緩和は fail-closed。 |
| `CE0-REVIEW-IF` | REVIEW | `reviewState` は `unreviewed | human_reviewed` のみ。AI による自動昇格を禁止。 | `unreviewed -> human_reviewed` が人手以外経路で発生したら fail。 |

### Core Graph write boundary（CE0-CG-WRITE-IF）

- `ConsensusGraph` への direct write は禁止。
- AI/worker/API は proposal を生成しても、適用は `patch + approval` のみ許可。
- quality gate 実行中に direct write path を1件でも検知した場合、検証を即時停止する。

### Freeze invariants

1. Contract ID の追加・改名・削除は禁止（重複定義 0 を維持）。
2. safeMode 既定ON・unreviewed 保護・Core Graph direct write 禁止の3点は同時成立が必須。
3. 本節で扱う契約は CE1 以降の実装進捗に依存せず、read-only 参照で運用する。

## Stream B Bridge Freeze Note（2026-05-17）

- IR 接続時も CE1 v1 closed-world を維持し、未定義キー受理を禁止する。
- 失敗語彙は `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の3種固定。
- A2 では `stubDatasetId=A2-minimal-v1` を唯一の検証データセットとし、実DB/実LLM/worker 経路を無効化する。
- Verify は `queryCanonicalHash` / `bundleHash` の 3/3 一致を必須とし、自己修復上限は3回。
- Proceed は CE2/CE4 への read-only handoff のみ許可。

## CE1 Stream C sync note（2026-05-17 / I/F-first mock-first）

- Phase開始ごとに `issue-CE1-context-query-bundle-foundation.md` / `schemas.md` / 本書を再Readし、contract drift を禁止する。
- `ContextQueryV1` / `ContextBundleV1` は v1 closed-world のまま固定し、未定義キーを受理しない（`400 unknown_contract_key`）。
- roundtrip 検証は `stubDatasetId=A2-minimal-v1` 固定で行い、同一 canonical query 3回で `queryCanonicalHash` と `bundleHash` の 3/3一致を必須とする。
- `previewConfirmed=false` は IR 生成開始前に必ず `422 preview_required` として fail-closed する。
- CE2/CE4 への引き渡しは read-only（`sourceBundleHash === bundleHash` 検証可能な最小鍵のみ）とし、CE1側での実装依存追加を禁止する。


## Stream B contract lock addendum（2026-05-18 / CE1-independent）

### Context
CE2/CE4 の進行を CE1 実装完了待ちにしないため、IR境界で ContextQuery/ContextBundle 契約の不変条件を固定する。

### Decision
1. **Schema/versioning 固定**
   - `ContextQueryV1` / `ContextBundleV1` は closed-world。
   - v1 では未知キー拒否（`400 unknown_contract_key`）。
   - 契約変更は v2 改訂のみ許可。
2. **Truncation 境界固定**
   - truncation は IR payload（`LLMRequest.inputs`）内でのみ許可。
   - Query/Bundle canonicalization 結果（`queryCanonicalHash` / `bundleHash`）を変化させる truncation を禁止。
3. **Fallback 固定（fail-closed）**
   - `previewConfirmed!=true` は `422 preview_required` で即失敗。
   - canonical query 同値で hash 不一致は `409 nondeterministic_bundle`。
4. **Mock/contract test 固定**
   - `stubDatasetId=A2-minimal-v1` を CE1 検証の唯一プロファイルとして固定。

### Consequences
- IR実装は CE1 契約に依存しつつも backend 実装非依存で検証可能。
- 下流は hash 監査キーを不変前提で再利用できる。
- 契約衝突時は実装継続せず `held` 停止が必須となる。


## Stream B CE1 contract freeze addendum（2026-05-20 / Context-Decision-Consequences）

### Context
CE1 v1 の query/bundle 契約が揺れると、IR生成境界でCE2/CE4の監査再現性が崩れる。

### Decision
- `ContextQueryV1` / `ContextBundleV1` は closed-world v1 として維持する。
- 固定エラー語彙を `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の3種に限定する。
- Verifyは `Plan -> Execute -> Verify -> Proceed` の直列順序を固定し、Verify失敗の自己修復は最大3回までとする。

### Consequences
- IR仕様は provider差分や実装進捗と独立して contract-first で検証可能。
- 競合（契約ID衝突・語彙衝突）検知時は fail-closed で停止できる。
