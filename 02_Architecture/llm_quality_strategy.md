# English Summary

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
This document defines a two-layer quality gate strategy: deterministic rule checks first, then optional low-cost local self-evaluation, with default-disabled (`none`) behavior and clear escalation handoff criteria.

# llm_quality_strategy — LLM品質戦略（02_Architecture）

本仕様は、図解→テキスト生成の品質保証を「正解一致」ではなく「有用性ゲート」で運用する方針を定義する。

---

## 1. 基本方針

- 生成出力は多様性を持つため、完全一致判定のみでは品質を適切に表現できない。
- そのため本プロジェクトでは、**二層評価（deterministic + optional LLM self-check）**を採用する。
- 合否は「利用可能性」「安全性」「構造整合性」を中心に判定する。
- 本戦略は `LLM_PROVIDER=none`（既定無効）を前提に、opt-in時も同一ゲートを適用する。
- `none`（LLM無効）/`fixture`/`local`/`external` の各providerで、同一ゲート基準を適用する。

---

## 2. Layer A: 決定論的ルールチェック（必須）

以下をすべて機械的に検証する。

1. schema validation が成功すること。  
2. 必須セクション（例: 全体要約、島ごとの要点、矛盾/反証セクション）が存在すること。  
3. citation数・coverage閾値を満たすこと（根拠カード参照不足を防止）。  
4. length/verbosity境界（最小・最大）に収まること。  
5. safeMode要件に適合すること（禁止領域への生テキスト漏えいがないこと）。
6. `LLM_ESCALATION_ENABLED=false` 時は external provider を使わないこと（fail-safe）。

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

## 6. IR準拠条件（Phase B連携）

- Layer A の schema validation は `LLMRequest.inputs` が `02_Architecture/llm_input_ir_spec.md` に準拠することを含む。
- `structured_text_only=true` を満たさないIRは品質評価対象に進めない。


## 7. CE-1 品質ゲート（Context / Decision / Consequences）

### 7.1 Context

CE-1では生成品質以前に、ContextQuery/ContextBundle契約の再現性（determinism）を満たさない限り後続評価を開始しない。
CE0境界（safeMode後退禁止・review自動昇格禁止・Consensus direct write禁止）に抵触する差分は、品質判定対象に入れず即時 fail-closed とする。

### 7.2 Decision

Layer A（必須）へ次のCE-1ゲートを追加する。

1. Determinism gate: 同一 canonical query を3回実行し、`bundleHash` が3/3一致。
2. Query Preview gate: `previewConfirmed=true` がない request は `422 preview_required`。
3. SafeMode exclusion gate: `safeModePolicy=strict` + `reviewFilter=reviewedOnly` のとき `excludedReason` に `unreviewed_filtered` を含む。
4. Mock parity gate: mock backend と実backendで ContextQuery/ContextBundle の JSON schema が一致。

### 7.3 Consequences

- いずれか不合格なら Layer B を実行せず fail とする。
- CE-2以降の `sourceBundleHash` 検証の前提条件として、このゲート合格結果を監査ログへ残す。
- 監査ログ最小キーは `queryId`, `bundleHash`, `excludedReason`。

## 8. CE-2 proposal-only 品質ゲート（Stream D）

### 8.1 Context

CE-2 は「低リスクAI支援」のため、LLM出力を適用結果ではなく **提案差分** として扱う。  
品質判定は内容の良し悪しより先に、契約逸脱（auto-apply、review自動昇格、安全後退）を fail-closed で検出する必要がある。

### 8.2 Decision

Layer A（必須）へ次の CE-2 契約ゲートを追加する。

Contract IDs: `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF`

1. Proposal schema gate: すべての提案が `proposalId/diff/sourceBundleHash/status/reviewState` を持つ。
2. Lifecycle gate: 許可遷移は `proposed -> accepted|rejected|held` のみ（`held` から自動遷移禁止）。
3. No-auto-apply gate: `accepted` を含め、提案状態から直接適用へ進む経路を禁止する。
4. No-auto-review-promotion gate: AI/worker/API による `reviewState=human_reviewed` 自動遷移を禁止する。
5. Drift-stop gate: CE1最小I/Fとの差異検知時は `status=held` を強制し、Verify/Proceed を停止する。

### 8.3 Consequences

- 上記ゲートのいずれかが不合格なら Layer B は実行せず fail とする。
- Verify 修復は最大3回までとし、4回目相当は `status=held` で停止する。
- `Read -> ADR CDC -> Plan -> Execute -> Verify -> Proceed` の各Phase開始時に Read チェックを実施し、契約ドリフトを先に検知する。
- CE-3 への引継ぎでは CE-2 Proposal I/F の後方互換（改名・省略・型変更禁止）を必須とする。

## 9. CE-2 low-risk 運用固定（safe-side）

### 9.1 Serial Phase gate（Stream D）

CE2 は次の順序を固定し、前Phaseの証跡なしで次Phaseへ進まない。

1. Read
2. ADR CDC（必要性判定を含む）
3. Plan（AC/DoD固定）
4. Execute
5. Verify（最大3回修復）
6. Proceed（CE3引継ぎ）


### 9.1.1 Independent execution rules

- CE1 は実装完了待ちではなく **mock contract参照** で扱う。
- 実装待ちを停止理由にせず、Phase 1〜5 の契約検証を継続する。
- 停止は drift未解消・safeMode後退・auto-apply検知時のみ許可する。

### 9.2 Fail-safe first

Layer A で以下を検知した場合は **即時 fail-closed** とし、Layer B は実行しない。

- safeMode既定ONの後退
- 未レビュー本文の混入（reviewed-only既定違反）
- auto-apply経路の存在
- AIによる `reviewState=human_reviewed` 自動昇格
- CE1/CE2 契約ドリフト未解消（`status=held` 未遷移）

### 9.3 Verify/Proceed 証跡最小キー

監査可能性と再現可能性のため、CE2品質ゲート結果には次を必須記録する。

- `verifyAttempt`（1..3）
- `proposalId`
- `sourceBundleHash`
- `statusBefore` / `statusAfter`
- `reviewStateBefore` / `reviewStateAfter`
- `safeModeDefaultOnConfirmed`
- `autoApplyPathCount`
- `autoReviewPromotionCount`
- `decision`（`pass|held|stop`）

4回目相当の修復は許可せず `status=held` で停止する。
