# English Summary

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
This document is the single source of truth for provider abstraction in kj-atlas. It standardizes provider enum, `LLM_*` configuration, `LLMRequest`/`LLMResponse` contracts, and links the LLM input IR to the dedicated Phase-B IR spec.

# llm_provider_spec — LLMプロバイダ抽象仕様（正本）

本仕様は、kj-atlas における LLM 連携の唯一の正本である。
`llm_provider.md` の内容は本仕様へ統合し、重複定義を持たない。

---

## 1. 目的と原則

- safeMode既定ONと漏えい防止を優先し、既定は `none`（LLM無効）とする。
- provider抽象はベンダロックインを避け、実装差異を吸収する。
- Provider分類は**通信プロトコルではなく信頼境界**で定義する。
  - 通信プロトコルは `transport`（in-process / ipc / http など）で別管理する。
- テスト再現性のため FixtureProvider を正式サポートする。
- 入力は構造化テキストのみ（画像・バイナリは対象外）。

---

## 2. Provider enum（確定）

正式列挙値は以下で固定する。

- `none`
- `fixture`
- `local`
- `external`

### 2.1 この分類を採用する理由

1. `local` と `external` は outbound 制御・監査・safeMode赤線化要件が異なるため、同一値へ統合しない。
2. `transport` は同一provider内で差し替え可能（例: local + ipc/local + http）であり、provider enumと役割が異なる。
3. `fixture` は決定論回帰のための特別実行形態で、`none/local/external` と同列に独立管理する必要がある。

---

## 3. 設定キー（`LLM_*` に完全統一）

互換aliasは持たない。旧 `LLM_PROVIDER` / `LOCAL_LLM_*` / `EXTERNAL_LLM_*` は非対応とする。

```text
LLM_PROVIDER=none|fixture|local|external
LLM_ESCALATION_ENABLED=false
LLM_EXTERNAL_ENABLED=false
LLM_TRANSPORT=in_process|ipc|http
LOCAL_LLM_BASE_URL=<url-or-socket>
LOCAL_LLM_MODEL=<model_id>
LLM_EXTERNAL_ENDPOINT=<allowlisted_endpoint>
LLM_EXTERNAL_MODEL=<model_id>
LLM_FIXTURE_DATASET=<fixture_dataset_path>
```

- `LLM_PROVIDER=none` を既定値とする。
- `LLM_PROVIDER=external` は `LLM_ESCALATION_ENABLED=true` かつ `LLM_EXTERNAL_ENABLED=true` を必須とする。

---

## 4. Interface 契約（`LLMRequest` を正規形に固定）

### 4.1 `LLMRequest`

```json
{
  "task": "draft_clusters|re_layout|merge_cards|narrative_probe",
  "prompt": "string",
  "inputs": {},
  "output_schema": {},
  "options": {
    "temperature": 0.2,
    "max_tokens": 2000,
    "timeout_ms": 30000,
    "seed": 42
  },
  "context": {
    "trace_id": "llm-...",
    "safe_mode": true
  }
}
```

- `inputs` は `02_Architecture/llm_input_ir_spec.md` のIR schemaに準拠する。
- `output_schema` は JSON Schema を受け取り、providerはこれを満たす構造化出力を返す。

### 4.2 `LLMResponse`

```json
{
  "output": {},
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0
  },
  "provider_meta": {
    "provider": "none|fixture|local|external",
    "provider_kind": "none|fixture|local|external",
    "model_id": "string",
    "transport": "in_process|ipc|http|none",
    "requested_at": "ISO-8601",
    "fallback_to_none": false,
    "trace_id": "llm-..."
  }
}
```

### 4.3 失敗時契約

- schema不一致は fail-fast（再整形で救済しない）。
- `external` が無効設定時は `external` へフォールバックしない。
- 失敗時も `provider_meta.trace_id` を監査ログへ残す。

---

## 5. 監査データ契約

`generate(LLMRequest) -> LLMResponse` の成否に関わらず、以下を構造化記録する。

- provider種別
- model_id
- transport
- requested_at
- fallback_to_none
- trace_id

監査ログに payload 本文・PII・秘匿トークンを保存しない。

---

## 6. Attachments 制約

- 入力データは KJ構造データ由来の構造化テキストのみ。
- バイナリ添付、画像、音声を `LLMRequest.inputs` に含めない。

---

## 7. 役割境界

- Provider層は「提案生成」だけを担当する。
- 意思決定確定APIを提供しない。
- 最終確定は人間操作でのみ実施する。

---

## 8. 参照

- 入力IR正本: `02_Architecture/llm_input_ir_spec.md`
- 実行制約: `02_Architecture/llm_runtime_constraints.md`
- 品質戦略: `02_Architecture/llm_quality_strategy.md`
- エスカレーション方針: `02_Architecture/llm_escalation_policy.md`
- 計画正本: `01_Plans/adr/ADR-0009-local-llm-integration.md`


## 9. CE1 ContextQuery/ContextBundle Contract Bridge（contract-only / mock-first）

本仕様は provider 抽象の正本であるが、CE1基盤の query/bundle 契約整合を次の通り固定する。

### 9.1 Closed-world contract（v1）

- `ContextQueryV1` / `ContextBundleV1` は v1 で closed-world とし、未定義キーを拒否する。
- 未定義キーは `400 unknown_contract_key` を返す。
- `previewConfirmed=false` は provider 呼び出し前に `422 preview_required` として失敗させる。

### 9.2 Deterministic hash gate

- `queryCanonicalHash` と `bundleHash` は監査キーとして必須扱いにする。
- 同一 canonical query で `bundleHash` が一致しない場合は `409 nondeterministic_bundle` を返し、provider実行を継続しない。

### 9.3 Mock validation profile（実装依存切断）

実LLM接続未確定でも以下を fixture で検証できる状態を DoD とする。

1. `previewConfirmed=false -> 422 preview_required`
2. 未定義キー -> `400 unknown_contract_key`
3. 同一 canonical query 3回実行で `queryCanonicalHash` / `bundleHash` が 3/3 一致
4. 3回中1回でも不一致なら `409 nondeterministic_bundle`
