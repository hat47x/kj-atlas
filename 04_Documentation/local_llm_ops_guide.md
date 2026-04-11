# English Summary

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
This operator guide explains how to run and switch LLM providers for kj-atlas across offline, intranet, and enterprise environments, including safety defaults, escalation controls, and minimal observability.

# local_llm_ops_guide — ローカルLLM運用ガイド（04_Documentation）

本ガイドは、kj-atlas の運用者が provider を安全に切替え、コストを抑えつつ品質を維持するための実務手順をまとめる。

---

## 1. 運用モード

### 1.1 Offline（完全オフライン）

- 使用プロバイダ: LocalProvider + FixtureProvider
- 外部送信: 禁止
- 主用途: 開発、閉域PoC、高機微環境

### 1.2 Intranet（閉域ネットワーク）

- 使用プロバイダ: LocalProvider中心
- 必要に応じて社内ゲートウェイ経由エスカレーション
- 送信先: 許可済み経路のみ

### 1.3 Enterprise（企業運用）

- 使用プロバイダ: LocalProvider標準 + 任意で強モデル経路
- 監査要件: 送信理由、承認履歴、モデル選択履歴の記録
- 推奨: 常時外部送信ではなく、閾値超過時のみの補助利用

---

## 2. Provider切替手順（設定ベース）

### 2.1 YAML設定例（プレースホルダ）

```yaml
llm:
  provider: local
  local:
    engine: "<local_engine_name>"
    model: "<local_model_id>"
  fixture:
    dataset: "<fixture_dataset_path>"
  escalation:
    enabled: false
    route: "<gateway_or_disabled>"
```

### 2.2 JSON設定例（プレースホルダ）

```json
{
  "llm": {
    "provider": "fixture",
    "fixture": { "dataset": "<fixture_dataset_path>" },
    "escalation": { "enabled": false }
  }
}
```

### 2.3 環境変数例（プレースホルダ）

```text
KJ_ATLAS_LLM_PROVIDER=none
LLM_EXTERNAL_ENABLED=false
KJ_ATLAS_LLM_ESCALATION_ENABLED=false
LLM_TRANSPORT=in_process
```

---

## 3. safeModeと漏えい防止

- `safeMode` は export/share で既定ON。
- safeMode時、analytics/exportに生カードテキストを含めない。
- LLM出力を保存する場合も、禁止領域では原文を残さず要約/マスク化を行う。
- MVPではPII項目（author/timeなど）は保存対象外。将来拡張時に再評価する。

---

## 4. CE4 API/CLI 監査統合手順（query/bundle/proposal/apply）

### 4.1 運用前提（依存切離し）

- CE3完了待ちはしない。
- `sourceBundleHash` は `mock:<hash>` を許容し、監査導線と同値性導線の検証を継続する。

### 4.2 API/CLIの共通監査項目

`POST /docs/{docId}/context-audit` は次の4操作を `eventType` として記録する。

- `query`
- `bundle`
- `proposal`
- `apply`

API経由/CLI経由のどちらでも、以下の監査項目を同一キーで残す。

- `equivalenceKey`
- `bundleHash`
- `dryRun`
- `sideEffect`
- `sourceBundleHash`
- `rejectReasonCode`
- `command`
- `channel`（`api` または `cli`）

### 4.3 実施手順（最小runbook）

1. APIで `context-query` と `context-bundle` を実行し、`equivalenceKey` と `bundleHash` を取得する。
2. CLIで同一入力の `context-query` と `context-bundle` を実行し、`equivalenceKey` と `bundleHash` が一致することを確認する。
3. API/CLI両方で `proposal-diff` を実行し、`sourceBundleHash`（本番値または `mock:<hash>`）を記録する。
4. API/CLI両方で `apply --dry-run` を実行し、`dryRun=true` かつ `sideEffect=none` を確認する。
5. 監査ログで `query/bundle/proposal/apply` の4イベントが揃っていることを確認する。

### 4.4 監査欠落の検知・通知

欠落判定は「同一 `equivalenceKey` で `query/bundle/proposal/apply` が揃っているか」で行う。

- 検知条件: 上記4イベントのいずれかが欠落。
- 一次対応: 欠落した操作を再実行し、`equivalenceKey` を維持したまま再送する。
- 通知: Platform Operator が当日中に運用チャネルへ「欠落操作・equivalenceKey・再実行結果」を報告する。
- 是正: 2回連続で同一欠落が発生した場合、CLI/APIの片系実装差分を停止し、共通実行ライブラリへ集約する。
- 判定原則: ログ欠損を成功扱いしない（fail-closed）。

### 4.5 Verify → Proceed（3回自己修復上限）

- Verify で不整合を検出した場合、自己修復（再実行/設定補正/キー補完）は最大3回まで。
- 3回で解消しない場合は Proceed を停止し、論点を保留化する。

### 4.6 フェイルセーフ停止条件

以下を検知した場合、CE4運用を停止する。

1. 同値性定義の多義化
2. ログ欠損成功扱い
3. safeMode後退要求

---

## 5. エスカレーション運用

### 5.1 既定

- 無効（disabled by default）。
- 無効時はローカル再試行または人手確認へ遷移。

### 5.2 有効化条件

- 設定で明示opt-inする。
- allowlist-only outbound を満たす。
- 送信前フィルタ（safeMode・最小化・不要メタ除去）を有効化する。

### 5.3 代表トリガ

- schema不一致
- 重要セクション欠落/短すぎ
- 否定関係があるのに反証記述欠落
- 入力規模閾値超過
- ルーブリックスコア閾値未達

---

## 6. テストと評価運用

- 毎回実行: unit + regression（fixture中心）
- 定期実行: curated integration（強モデル、小規模セット）
- 目的: 正解一致ではなく、有用性ゲート（構造・安全・根拠性）維持

### 6.1 LFM2.5（SLM）導入目的に関する補足

- LFM2.5 の導入目的は、主に unit テストおよび E2E テストで「モデル実行経路が正しく動くか」を検証することにある。
- そのため、LFM2.5 の推論品質や処理性能は、実運用で常時利用する前提の水準に達しない可能性がある。
- 実運用上の品質が必要なケースは、ローカル前処理・人手レビュー・必要時エスカレーションを組み合わせて補完する。

---

## 7. 観測性（Observability）最小要件

### 7.1 収集する最小ログ

- 実行時刻
- provider種別
- 成否
- エスカレーション理由コード
- 評価スコア（利用時）
- `equivalenceKey`
- `sideEffect`

### 7.2 収集しない/赤線化する項目

- 生カード本文（safeMode領域）
- 個人識別につながるメタ情報
- 外部連携に不要な入力全文

---

## 8. 障害時対応

- LocalProvider障害時: FixtureProviderで回帰確認し、モデル基盤切り分けを優先。
- エスカレーション経路障害時: 外部送信を停止し、ローカルのみで運転継続。
- 安全要件違反検知時: 出力公開を停止し、safeModeルールと前処理設定を再点検。
