# Local LLM Operations Guide

> Audience: 外部運用者（閉域/企業）
> Purpose: ローカルLLM運用時の最小runbookを提供する。
> This document decides: provider切替手順、safeMode境界、最小監査確認。
> This document does not decide: 組織固有の承認フロー、秘密情報管理、内部監査ログの保管方式。
> Related: `02_Architecture/llm_provider_spec.md`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/strict_mode_exception_approval_flow.md`, `04_Documentation/operations.md`

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。

## 1. Go/No-Go gate（公開運用判定）

公開運用を開始してよいのは、次の条件をすべて満たす場合のみです。

1. SafeMode既定ONと share/export 漏えい防止を後退させない。
2. 役割語彙を `Security Officer / System Owner / Platform Operator` に統一する。
3. strict mode例外を扱う場合、D1〜D4（承認TTL=4h、最大2h、代理承認なし、48hレビュー+15m/60m）を満たす。
4. 本文に内部承認ログや秘密情報を含めない。

未充足の場合は `StoppedForClarification` として停止し、設定変更を実施しないでください。

## 2. 運用モード

- Offline: `KJ_ATLAS_LLM_PROVIDER=none`（既定、外部送信なし）
- Intranet: `KJ_ATLAS_LLM_PROVIDER=local`（社内LLMのみ）
- Enterprise: local中心 + 必要時のみ人手承認で外部経路

## 3. 最小設定（前提条件つき）

前提条件:

- APIサーバーが `http://localhost:8000` で起動している。
- ローカルLLMを使う場合、LLMエンドポイントが到達可能である。

```bash
export KJ_ATLAS_LLM_PROVIDER='none'   # default

# local利用時のみ
export KJ_ATLAS_LLM_PROVIDER='local'
export KJ_ATLAS_LOCAL_LLM_BASE_URL='http://localhost:8001'
export KJ_ATLAS_LOCAL_LLM_MODEL='local-model-name'
```

疎通確認:

```bash
curl -fsS http://localhost:8000/healthz
```

失敗時対応:

- `curl` が失敗する場合は、API起動状態とポート競合を先に確認する。
- local provider だけ失敗する場合は、`KJ_ATLAS_LOCAL_LLM_BASE_URL` 到達性を確認する。

## 4. SafeMode と漏えい防止

- `safeMode` は export/share で既定ON。
- safeMode時は未レビュー本文のAI入力混入を許可しない。
- analytics/export に生カード本文を含めない。
- AI出力は提案として扱い、確定は人手レビューで行う。

## 5. 最小監査runbook（query/bundle/proposal/apply）

監査4点セット（`query/bundle/proposal/apply`）は、成功判定の必須条件です。

1. APIで `context-query` と `context-bundle` を実行し、`equivalenceKey` と `bundleHash` を取得する。
2. CLI/GUIで同一入力を実行し、`equivalenceKey + bundleHash` が一致することを確認する。
3. `proposal-diff` 実行時に `sourceBundleHash` を記録する（`mock:<hash>` 許容）。
4. `apply --dry-run` で `dryRun=true` かつ `sideEffect=none` を確認する。
5. 監査ログで `query/bundle/proposal/apply` が揃っていることを確認する。

必須バリデーション:

- `equivalenceKey` と `bundleHash` は 64桁hex。
- `operation=apply` は `dryRun=true` を必須とし、`dryRun=false` は失敗扱い。
- `dryRun=true` で `sideEffect!=none` は失敗扱い。

## 6. エスカレーション運用

- 既定は無効（disabled by default）。
- 有効化時は明示opt-in + allowlist-only outbound + 送信前フィルタを必須とする。
- 次の条件ではローカル再試行より先に人手確認へエスカレーションする。
  - schema不一致
  - 必須セクション欠落
  - 反証・留保の欠落

## 7. Verify / 停止条件

推奨チェック:

```bash
rg -n "Audience|This document decides|This document does not decide|safeMode|equivalenceKey|bundleHash|dryRun|sideEffect|query|bundle|proposal|apply" 04_Documentation/local_llm_ops_guide.md
git diff --check
```

停止条件:

- 上流正本（`02_Architecture/*`）との矛盾を検知。
- SafeMode後退要求を検知。
- Verify自己修復が3回を超過。
