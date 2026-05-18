# English Summary

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
This document is the single source of truth for provider abstraction in kj-atlas. It standardizes provider enum, `KJ_ATLAS_*` configuration, `LLMRequest`/`LLMResponse` contracts, and links the LLM input IR to the dedicated Phase-B IR spec.

# llm_provider_spec — LLMプロバイダ抽象仕様（正本）

本仕様は、kj-atlas における LLM 連携の唯一の正本である。
`llm_provider.md` の内容は本仕様へ統合し、重複定義を持たない。

---


## CE1 Contract Handoff Boundary（Stream C / 2026-05-04）

- Provider層は CE1 v1 契約を入力境界として扱い、`ContextQueryV1` / `ContextBundleV1` のキー追加・再定義を行わない。
- 固定エラー語彙は provider 実装差異に依存させず、`preview_required` / `unknown_contract_key` / `nondeterministic_bundle` を共通運用語彙として保持する。
- `provider_meta.trace_id` と併せて `queryCanonicalHash` / `bundleHash` を監査相関キーとして扱えることを必須とする。
- CE2/CE4 連携は mock-first を許容し、provider 実装完了を前提条件にしない（contract-only handoff）。

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

## 3. 設定キー（`KJ_ATLAS_*` に完全統一）

互換aliasは持たない。接頭辞のない旧 LLM 設定キーは非対応とする。

```text
KJ_ATLAS_LLM_PROVIDER=none|local|local_http|large-scale|large_scale|external
KJ_ATLAS_LLM_ESCALATION_ENABLED=false
KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=false
KJ_ATLAS_LOCAL_LLM_BASE_URL=<url-or-socket>
KJ_ATLAS_LOCAL_LLM_MODEL=<model_id>
KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL=<allowlisted_endpoint>
KJ_ATLAS_LARGE_SCALE_LLM_MODEL=<model_id>
KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST=<host-list>
```

- `KJ_ATLAS_LLM_PROVIDER=none` を既定値とする。
- `KJ_ATLAS_LLM_PROVIDER=external` は `KJ_ATLAS_LLM_ESCALATION_ENABLED=true` かつ `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true` を必須とする。

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

## 10. Stream B CE0/CE1 mock-first provider alignment（2026-05-06）

- Scope: CE0/CE1 契約整合（contract-only）。
- Provider は `previewConfirmed` ゲート通過後にのみ呼び出される前提を維持する。
- CE1 v1 closed-world により未定義キーは provider 層到達前に `400 unknown_contract_key` で拒否する。
- `bundleHash` 非決定論検知時は `409 nondeterministic_bundle` を返し fail-closed とする。
- 本節は mock-first 連携を想定し、実LLM実装差分を契約語彙へ反映しない。

## CE1 mock-first contract reaffirmation（2026-05-07 / Stream B）

- Provider は CE1 v1 契約の下流であり、`ContextQueryV1` / `ContextBundleV1` のキー再定義を行わない。
- Provider 到達前ゲートを固定する：
  - `previewConfirmed=false` -> `422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - hash非決定論 -> `409 nondeterministic_bundle`
- 監査相関キーは `queryCanonicalHash` / `bundleHash` / `provider_meta.trace_id` を最小集合として保持する。
- 本再確認は contract-only であり、接続実装・リトライ戦略・モデル選定は本凍結範囲外とする。


## Stream B contract stabilization addendum（2026-05-18 / CE1-independent）

### Context
Provider 抽象の差異で CE1 契約語彙が揺れると、CE2/CE4 の監査再現性が崩れる。

### Decision
- Provider 層は CE1 契約語彙を変更しない。
- 固定語彙は `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` のみ。
- Provider 実装差異による fallback は **契約エラーを書き換えてはならない**。
- `queryCanonicalHash` / `bundleHash` / `provider_meta.trace_id` を最小監査相関キーとして固定。
- mock-first contract test は provider 種別に依存させない（fixture で同一判定）。

### Consequences
- provider 切替（none/fixture/local/external）でも CE1 I/F 契約は不変。
- CE2/CE4 は provider 実装進捗と独立して契約連携を継続できる。
