# English Summary
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
KJ_LLM_PROVIDER=none
KJ_LLM_EXTERNAL_ENABLED=false
KJ_LLM_ESCALATION_ENABLED=false
KJ_LLM_TRANSPORT=in_process
```

---

## 3. safeModeと漏えい防止

- `safeMode` は export/share で既定ON。
- safeMode時、analytics/exportに生カードテキストを含めない。
- LLM出力を保存する場合も、禁止領域では原文を残さず要約/マスク化を行う。
- MVPではPII項目（author/timeなど）は保存対象外。将来拡張時に再評価する。

---

## 4. エスカレーション運用

### 4.1 既定

- 無効（disabled by default）。
- 無効時はローカル再試行または人手確認へ遷移。

### 4.2 有効化条件

- 設定で明示opt-inする。
- allowlist-only outbound を満たす。
- 送信前フィルタ（safeMode・最小化・不要メタ除去）を有効化する。

### 4.3 代表トリガ

- schema不一致
- 重要セクション欠落/短すぎ
- 否定関係があるのに反証記述欠落
- 入力規模閾値超過
- ルーブリックスコア閾値未達

---

## 5. テストと評価運用

- 毎回実行: unit + regression（fixture中心）
- 定期実行: curated integration（強モデル、小規模セット）
- 目的: 正解一致ではなく、有用性ゲート（構造・安全・根拠性）維持

### 5.1 LFM2.5（SLM）導入目的に関する補足

- LFM2.5 の導入目的は、主に unit テストおよび E2E テストで「モデル実行経路が正しく動くか」を検証することにある。
- そのため、LFM2.5 の推論品質や処理性能は、実運用で常時利用する前提の水準に達しない可能性がある。
- 実運用上の品質が必要なケースは、ローカル前処理・人手レビュー・必要時エスカレーションを組み合わせて補完する。

---

## 6. 観測性（Observability）最小要件

### 6.1 収集する最小ログ

- 実行時刻
- provider種別
- 成否
- エスカレーション理由コード
- 評価スコア（利用時）

### 6.2 収集しない/赤線化する項目

- 生カード本文（safeMode領域）
- 個人識別につながるメタ情報
- 外部連携に不要な入力全文

---

## 7. 障害時対応

- LocalProvider障害時: FixtureProviderで回帰確認し、モデル基盤切り分けを優先。
- エスカレーション経路障害時: 外部送信を停止し、ローカルのみで運転継続。
- 安全要件違反検知時: 出力公開を停止し、safeModeルールと前処理設定を再点検。
