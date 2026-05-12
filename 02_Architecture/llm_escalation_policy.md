# English Summary

> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
This document specifies a deterministic Local-first escalation policy: system default is `none` (LLM disabled), `local` is opt-in standard path, and `external` escalation is opt-in + disabled by default with outbound allowlist controls.

# llm_escalation_policy — Local-first + Escalation方針（02_Architecture）

本仕様は、コスト抑制と品質維持を両立するための **Local-first + Escalation** の運用ルールを定義する。

---

## 1. 運用原則

- システム既定は **`none`（LLM無効）**。
- LLM利用を有効化する場合の標準経路は **LocalProvider**。
- エスカレーションは例外処理であり、常用経路にしない。
- 外部強モデルへの送信は、明示設定がある場合のみ許可する。

---

## 2. デフォルト設定

- `KJ_ATLAS_LLM_ESCALATION_ENABLED=false`（既定: 無効）
- `KJ_ATLAS_LLM_PROVIDER=none`（既定: 無効）
- `KJ_ATLAS_LLM_PROVIDER=none|local|local_http|large-scale|large_scale|external` の列挙を前提とする。
- 明示的に `true` へ変更しない限り、外部サービスにデータを渡さない。
- 設定変更には運用責任者の承認と監査ログ記録を要する。

---

## 3. 決定論的エスカレーショントリガ

以下はいずれも**LLM不要で判定可能**であること。

1. schema validation failure  
2. 重要セクションが空、または最小長未満  
3. contradiction edge（否定関係）が存在するのに、出力に矛盾/反証セクションが欠落  
4. 閾値超過（カード数・クラスタ数・negation edge数など）  
5. ルーブリックスコアが閾値未満（Layer B利用時）

> トリガは仕様書で固定し、恣意的判定を避ける。

---

## 4. ルーティングパターン

### 4.1 無効時（既定）

- ローカル再試行（prompt圧縮・入力分割など）を行う。
- 失敗時は「要人手確認」ステータスで返却。

### 4.2 有効時（明示opt-in）

- 許可された接続先にだけデータを渡す（allowlist-only outbound）。
- 送信前にsafeMode/赤線化ポリシーを適用。
- 送信データは最小化し、不要メタデータを含めない。

### 4.3 Multi-Model Routing（責務分離）

- `intermediate` 段階（分類/要約/フォーマット変換/条件分岐）は、
  低遅延・低コスト系モデル（例: Groq 上の Llama / Qwen）を許可する。
- `final_judgement` 段階（accept/reject/merge/finalize の提案生成）は、
  高推論系モデル（例: Claude / GPT-5）へ固定する。
- `intermediate` は proposal の材料生成に限定し、最終採否の決定権を持たない。
- `final_judgement` 経路が利用不能な場合、`intermediate` へ権限昇格せず `held` へ遷移する（fail-closed）。

---

## 5. コスト制御

- 月次または環境別の外部呼び出し上限（回数/トークン）を定義する。
- 上限到達時は自動でローカル専用モードに降格する。
- 運用ダッシュボードで、ローカル成功率・エスカレーション率・失敗率を監視する。

---

## 6. セキュリティ・プライバシー整合

- safeMode ON時は、禁止対象の生カード文面を外部サービスに渡さない。
- エスカレーションログは理由コードを保持し、本文は最小化またはハッシュ化する。
- 送信経路・承認履歴・モデル識別子を監査可能にする。

---

## 6.5 CE2 低リスクAI支援 契約（Stream C / proposal-only 固定）

CE2（低リスクAI支援）では、LLM出力を「提案patch」に限定し、直接適用を禁止する。  
本節は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` の契約を architecture 観点で固定する。

### CE2-C1: Proposal I/F 必須キー（Phase 1〜6で固定）

すべての提案出力に以下を必須とする。

- `proposalId: string`
- `diff: object`
- `sourceBundleHash: string`
- `status: proposed | accepted | rejected | held`
- `reviewState: unreviewed | human_reviewed`

上記5キー（`proposalId/diff/sourceBundleHash/status/reviewState`）は CE2 Phase 1〜6 で固定し、改名・省略・型変更を禁止する。
また `reviewState` の既定値は `unreviewed` とし、`human_reviewed` は人手操作でのみ設定可能とする。

### CE2-C2: 実行禁止事項（Fail-safe）

以下を検知した場合、処理を継続せず停止する。

1. auto-apply 経路（API/UI/worker）
2. AI による review 自動昇格（`unreviewed -> human_reviewed`）
3. `human_reviewed` 自動昇格（AI/worker/API いずれの経路でも禁止）
4. safeMode 保護後退（未レビュー本文混入を含む）
5. CE1最小I/Fモック契約との差異（`sourceBundleHash` 不整合など）

停止時は `status=held` とし、手動レビュー待ちへ遷移させる。

### CE2-C3: 依存切離し（CE1 モック契約）

- CE2 は CE1 完了待ちを行わず、`ContextQuery + ContextBundle + bundleHash` をモック契約として参照する。
- 実体CE1との差異が確定した時点で drift を記録し、CE2 の適用フローを停止する。
- drift 解消後にのみ `held` から再開できる。

### CE2-C4: CDC実行シーケンス（Read → ADR CDC → Plan → Execute → Verify → Proceed）

CE2 Stream C は以下の順序を固定する。

1. **Phase 1 Read**: `proposalId/diff/sourceBundleHash/status/reviewState` を再確認。
2. **Phase 2 ADR CDC**: Context / Decision / Consequences を明文化。
3. **Phase 3 Plan**: AC/DoD不足（status遷移・drift-stop）を合意。
4. **Phase 4 Execute**: proposal-only 固定、auto-apply禁止を実施。
5. **Phase 5 Verify**: 契約逸脱を検査し、必要なら修復。
6. **Phase 6 Proceed**: CE3向け参照I/Fを引き渡し終了。

各Phase開始時に Read チェックポイントを実施し、status遷移（`proposed/accepted/rejected/held`）と proposal-only 境界を再確認する。

`Verify` は最大3回まで修復再試行を許可し、3回以内に解消しない場合は `status=held` で停止する。
`held` 中は `accepted/rejected/proposed` への自動遷移を禁止し、drift解消の手動確認が完了するまで Proceed 不可とする。

### CE2-C5: 監査必須項目（Routing）

CE2/CE4 で生成される監査イベントには、少なくとも以下を含める。

- `routingStage`: `intermediate | final_judgement`
- `provider`
- `model`
- `sourceBundleHash`
- `proposalId`（存在する場合）


## 7. 設定キー整合

- 本仕様の公開設定キーは `KJ_ATLAS_*` に統一する。
- 接頭辞のない旧 LLM 設定キーは互換aliasを提供しない。
