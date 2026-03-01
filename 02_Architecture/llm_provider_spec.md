# English Summary
This document defines a provider-agnostic LLM abstraction for kj-atlas, including LocalProvider-first operation, optional strong-model provider, and deterministic FixtureProvider for regression testing.

# llm_provider_spec — LLMプロバイダ抽象仕様（02_Architecture）

本仕様は、kj-atlas における図解（KJ構造データ）→テキスト生成機能のための、**プロバイダ非依存（provider-agnostic）**なLLM連携方式を定義する。  
実装の詳細ではなく、責務境界・入出力契約・切替方針を固定することを目的とする。

---

## 1. 目的と前提

- 本プロジェクトは、コスト抑制と開発再現性の観点から **LocalProvider を第一選択** とする。
- 高性能モデル（外部/強モデル）は、常用ではなく任意の統合検証または明示的エスカレーション経路で扱う。
- テスト再現性確保のため、**FixtureProvider（録画応答）**を正式サポートする。
- 添付データは本MVPでは画像を扱わず、**構造化テキストのみ**を対象とする。

---

## 2. Provider Interface（言語非依存）

### 2.1 必須I/F

```text
generate(prompt, inputs, schema, options) -> output
```

- `prompt`: 生成方針・出力形式・制約を記述したテンプレート文字列。
- `inputs`: KJ構造データ由来のIR（JSON相当）。
- `schema`: 出力検証に用いる厳格スキーマ定義（JSON Schema相当）。
- `options`: 実行パラメータ（温度、最大トークン、タイムアウト、seed等）。
- `output`: schema準拠を期待する構造化出力（JSON相当）。

### 2.2 任意I/F（評価用）

```text
evaluate(prompt, rubric, output) -> score
```

- `rubric`: 採点観点（根拠性・矛盾反映・過剰断定抑制など）。
- `score`: 0–5の整数または小数（後段ゲート判定に利用）。

> `evaluate` は任意機能であり、未実装プロバイダでは deterministic rule checks のみで品質ゲートを通す。

### 2.3 監査データ契約（全provider共通）

`generate(...)` の成否にかかわらず、以下の監査メタを同一キーで記録できること。

```json
{
  "provider": "none|local|large-scale",
  "provider_kind": "none|local|large-scale",
  "model_id": "string",
  "transport": "none|http|...",
  "requested_at": "ISO-8601",
  "fallback_to_none": false,
  "trace_id": "llm-..."
}
```

- `trace_id` は1実行単位で一意。
- `fallback_to_none=true` は実行失敗から no-op へ退避した場合のみ。
- 監査ログに payload 本文や秘匿情報を含めない。

---

## 3. サポート対象プロバイダ

### 3.1 none（NoOpProvider / 既定）

- 用途: SafeMode前提でAI機能を明示的に無効化する。
- 挙動: 呼び出し時は「AI disabled」を返し、意思決定の自動確定を行わない。
- 位置付け: **default**。外部送信は発生しない。

### 3.2 local（LocalProvider / 標準）

- 用途: 開発・CI・本番のデフォルト推論。
- 想定実装例: LFM2.5 / llama.cpp系などのローカル実行基盤。
- 要件: オフライン/閉域環境でも動作可能であること。

### 3.3 large-scale（LargeScaleProvider / 任意）

- 用途: 高難度ケースの統合評価、定期的品質監査。
- 位置付け: **Optional**（必須依存にしない）。
- 注意: 外部通信は明示許可時のみ。

---

## 4. 設定による切替（コード外仕様）

実行時プロバイダは、**設定ファイルまたは環境変数**で切替える。実装依存のAPI呼び出しは本仕様に含めない。

### 4.1 例: YAML（プレースホルダ）

```yaml
llm:
  provider: local # local | openai | fixture
  local:
    engine: "<local_engine_name>"
    model: "<local_model_id>"
  openai:
    enabled: false
    model: "<strong_model_id>"
  fixture:
    dataset: "<fixture_dataset_path>"
```

### 4.2 例: 環境変数（プレースホルダ）

```text
KJ_LLM_PROVIDER=local
KJ_LLM_OPENAI_ENABLED=false
KJ_LLM_FIXTURE_DATASET=<fixture_dataset_path>
```

---

## 5. Attachmentsの取り扱い

- 本プロジェクトの入力は、KJカード・座標・関係・メタ情報からなる**構造化テキスト**である。
- そのため attachments は画像バイナリではなく、IR JSON（または同等のテキスト）を標準とする。
- 画像/VLM依存を前提にしないことで、ローカル・オフライン運用の移植性を維持する。

---


## 6. 入力データ前提（KJ構造データ）

LLMに渡す前段入力は、以下の構造化データを前提とする。

- card text（カード本文）
- coordinates（x, y など）
- relations（接続、矢印、否定）
- meta（MVPでは最小。将来拡張項目は別管理）

### 6.1 非LLM前処理（推奨）

LLM負荷低減と再現性向上のため、次を事前計算する。

- clustering candidates
- centrality / top nodes
- connected components
- contradiction subgraph summary

### 6.2 LLM投入IR（Intermediate Representation）

LLMが受け取るIRは厳格JSONスキーマを持つ。以下はアウトライン。

```json
{
  "version": "1",
  "cards": [
    { "id": "string", "text": "string", "x": 0.0, "y": 0.0 }
  ],
  "relations": [
    { "from": "string", "to": "string", "type": "related|arrow|negation" }
  ],
  "graph_summary": {
    "components": [],
    "top_nodes": [],
    "contradictions": []
  },
  "constraints": {
    "safe_mode": true,
    "required_sections": ["overall", "clusters", "contradictions"]
  }
}
```

### 6.3 サイズ上限と切り詰め規則

- 入力カード数・関係数・総文字数に上限を設定する。
- 上限超過時は以下の順で切り詰める。
  1. 重複/低優先メタ情報の削除
  2. 低中心性ノードの要約化
  3. クラスタ単位の代表化
- 切り詰め実行時は `truncated=true` と理由コードをIRに記録する。

---

## 7. 非機能要件


- Provider Interface は特定ベンダSDK型にロックインしない。
- 監査容易性のため、プロバイダ選択・評価結果・エスカレーション理由は構造化ログに残す（内容は最小限・秘匿情報は除去）。
- スキーマ不一致時は fail-fast し、後段で救済しない。

---

## 8. Human-in-the-loop 制約

- Provider層は「提案生成」のみを扱い、**decision確定APIは提供しない**。
- 最終確定は必ず人間操作で実施する（AI自動確定経路を実装しない）。
- SafeMode 既定ONを前提とし、外部送信の既定ON化は禁止。


## 9. FB-RM-MID-06 固定仕様（安全デフォルト + 監査一貫性）

### 9.1 I/F定義（メソッド / 戻り値 / エラー型）

```python
class LLMProvider(Protocol):
    provider_name: str  # none | local | large-scale
    provider_kind: str  # none | local | large-scale

    def generate(req: LLMRequest) -> LLMResponse: ...
```

- `LLMRequest`: `{task, prompt, temperature, max_tokens}`
- `LLMResponse`: `{raw_text, metadata}`
- `metadata`: `LLMCallMetadata`（監査用共通フィールド）

共通エラー型:

- `ProviderDisabledError`: none既定/明示無効化時の標準応答。
- `ProviderRequestError(code=provider_timeout|provider_validation|provider_unavailable)`: 通信失敗・timeout・schema不一致・allowlist違反を統一。

### 9.2 none時の標準挙動

- `LLM_PROVIDER=none` を既定値とする。
- `NoneProvider.generate` は提案を生成せず、説明可能な `ProviderDisabledError` を返す。
- APIは `code=provider_unavailable` + `disabled_reason=provider_disabled_or_none_default` を返却し、UI契約を変えない。

### 9.3 設定マトリクス（default / allowed / disallowed）

| 設定 | default | allowed | disallowed |
|---|---|---|---|
| `LLM_PROVIDER` | `none` | `none`, `local`, `large-scale` | その他文字列 |
| `LLM_LARGE_SCALE_OPT_IN` | `false` | `true`（large-scale使用時に必須） | `false` で `LLM_PROVIDER=large-scale` |
| `LLM_ESCALATION_ENABLED` | `false` | `true`（large-scale使用時に必須） | `false` で `LLM_PROVIDER=large-scale` |
| `LARGE_SCALE_LLM_ALLOWLIST` | `None` | 宛先hostnameを含むCSV | allowlist未一致 |
| `LLM_FALLBACK_TO_NONE` | `true` | `true/false` | - |

### 9.4 監査イベント最小スキーマ

```json
{
  "provider": "none|local|large-scale",
  "provider_kind": "none|local|large-scale",
  "model_id": "string",
  "transport": "none|http|mock|...",
  "requested_at": "ISO-8601",
  "trace_id": "llm-*",
  "fallback_to_none": false,
  "execution_path": "primary|<provider>->none"
}
```

- 監査キーは provider 切替時も固定し、UIや後段集計の契約を変更しない。
- payload本文・秘密情報は記録しない。

### 9.5 timeout / error / 部分失敗フォールバック

1. `provider_timeout` → HTTP 504
2. `provider_validation` → HTTP 422
3. `provider_unavailable` → HTTP 503
4. `LLM_FALLBACK_TO_NONE=true` の場合は `execution_path=<provider>->none` を付けて no-op に退避
5. 退避時も `trace_id` を維持して監査トレースを連結

### 9.6 fixtureベース回帰テスト方針（非決定性隔離）

- Unit: Providerエラー契約、allowlist、opt-inガード、fallbackメタを固定。
- Integration: API契約（status/detail schema）を provider 切替で同一確認。
- E2E: fixture応答の golden 比較を中心にし、外部強モデルは定期ジョブのみ。
- 非決定性は fixture / mock transport に閉じ込め、PR必須ゲートは決定論テストで構成する。

### 9.7 非許可機能

- Provider層は「提案のみ」。
- decision確定API（finalize/confirm）は提供しない。
