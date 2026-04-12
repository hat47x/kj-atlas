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

---

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
- provider未起動（`LLM_PROVIDER=fixture`）でも回帰が成立する。

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
- `previewConfirmed=false` は bundle 生成前に 422 とする（Query Previewバイパス禁止）。
- `safeModePolicy=strict` + `reviewFilter=reviewedOnly` では未レビュー本文を入力IRへ含めない。
- 機械判定式: `canonical(queryA)==canonical(queryB) && hashA==hashB` が真であること。
- CE4監査では `queryId` / `queryCanonicalHash` / `bundleHash` / `excludedReason` の4キーを欠落させてはならない。
