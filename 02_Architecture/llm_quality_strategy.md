# English Summary
This document defines a two-layer quality gate strategy: deterministic rule checks first, then optional low-cost local self-evaluation, with default-disabled (`none`) behavior and clear escalation handoff criteria.

# llm_quality_strategy — LLM品質戦略（02_Architecture）

本仕様は、図解→テキスト生成の品質保証を「正解一致」ではなく「有用性ゲート」で運用する方針を定義する。

---

## 1. 基本方針

- 生成出力は多様性を持つため、完全一致判定のみでは品質を適切に表現できない。
- そのため本プロジェクトでは、**二層評価（deterministic + optional LLM self-check）**を採用する。
- 合否は「利用可能性」「安全性」「構造整合性」を中心に判定する。
- 本戦略は `llm.provider = none`（既定無効）を前提に、opt-in時も同一ゲートを適用する。
- `none`（LLM無効）/`fixture`/`local`/`external` の各providerで、同一ゲート基準を適用する。

---

## 2. Layer A: 決定論的ルールチェック（必須）

以下をすべて機械的に検証する。

1. schema validation が成功すること。  
2. 必須セクション（例: 全体要約、島ごとの要点、矛盾/反証セクション）が存在すること。  
3. citation数・coverage閾値を満たすこと（根拠カード参照不足を防止）。  
4. length/verbosity境界（最小・最大）に収まること。  
5. safeMode要件に適合すること（禁止領域への生テキスト漏えいがないこと）。
6. `escalation.enabled=false` 時は external provider を使わないこと（fail-safe）。

---

## 3. Layer B: LocalProviderセルフチェック（任意）

低コスト評価として、LocalProviderの `evaluate`（または同等手段）を用いて 0–5 スコアを算出する。

### 3.1 ルーブリック例

- grounding（入力根拠との整合）
- missing contradictions（矛盾/否定関係の取りこぼし有無）
- over-assertion（過剰断定・根拠薄弱断定の抑制度）

### 3.2 利用方法

- Layer A 合格後に `local` 利用時のみ実行してもよい。
- スコア閾値未達はエスカレーション候補フラグとして扱う。

---

## 4. テスト体系（taxonomy）

### 4.1 Unit Tests（毎回実行）

- schema準拠検証
- post-processing（整形・正規化）安定性
- safeModeでの禁止出力検証

### 4.2 Regression Tests（毎回実行）

- FixtureProviderスナップショット（golden files）比較
- 期待フィールド、セクション、引用カバレッジの退行検出

### 4.3 Integration Tests（定期実行）

- curatedな小規模ケース群を強モデルで実行
- 夜間/定期ジョブで差分追跡
- PR必須ゲートにせず、品質監査として運用

---

## 5. 正しさ判定が難しい理由と実務対応

- KJ法の構造から導く要約は、単一正解に収束しない。
- したがって「正しいか」より「業務で利用可能か」を重視する。
- 具体的には、構造整合（schema/section/citation）と安全整合（safeMode）を最低基準とし、解釈品質は定期統合テストで補完する。
