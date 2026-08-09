# Issue: AI-IR-PROJECTION-01 LLM投入IRをAI入力の実経路として実装する

- Type: Architecture / AI Integration
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: Unassigned
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/backend/src/kj_atlas_api/models_context.py`, `02_Architecture/llm_input_ir_spec.md`, `02_Architecture/api.md`, `03_Implement/backend/tests/test_ts_python_contract_drift.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `02_Architecture/llm_input_ir_spec.md`, `01_Plans/adr/ADR-0009-local-llm-integration.md`, `02_Architecture/canvas-projection-asymmetry-2026-08-09.html`
- Expected verification level: `integration`

> **本issueは `ADR-0069` の採択を前提とする。** ADR が Proposed の間は着手しないこと。D1〜D4 が未決のまま実装すると、凍結仕様（`llm_input_ir_spec.md`）への非互換な改変が入る。

## 課題

`02_Architecture/llm_input_ir_spec.md` は「LLMへ渡す前段データ」の正本であり、`ADR-0009`（Accepted）Phase B を完了させる凍結仕様である。**この仕様の実装は存在しない。**

```
$ grep -rn "ir_version\|graph_summary\|cluster_candidates" --include=*.py --include=*.ts --include=*.tsx 03_Implement
（0件）
```

出荷済みの `/ai/*` は `DocumentV1` を直接プロンプト文字列へ変換している。その結果、**論理構造がAIへほとんど渡っていない**。

### 実測（`routes/ai.py` の全プロンプト構築関数9件を走査）

| 渡されていないもの | 該当 |
|---|---|
| `edges`（関係） | **全9関数** |
| `evidenceLinks` | 全9関数 |
| `relationSummaries` | 全9関数 |
| `claimType` | 全9関数 |
| `parentIslandId`（島階層） | 全9関数 |
| `placardCardId`（表札） | 全9関数 |

`ADR-0048` D3 で固定した関係語彙（`related`/`negate`/`causal`/`mutual`/`equivalence`、`types.ts:78`）は、AIに一度も届いていない。

具体的な症状:

- `POST /ai/detect-contradiction`（`ai.py:746-752`）: 矛盾を扱うAPIが、人間が既に記録した矛盾（`EvidenceLink.type="contradicts"`、`contradictionState`）を見ていない。確定・保留済みの矛盾を再提示しうる。
- `POST /ai/suggest-card-groups`（`ai.py:725-731`）: グルーピング提案が既存の島・階層・`holdState` を見ていない。人間の既決と衝突する候補を出しうる。
- `POST /ai/generate-narrative`: `readingOrder` は渡るが `edges` は渡らない。因果・対立という叙述の骨格が使えない。
- `POST /ai/suggest-layout`（`ai.py:317-336`）: 生の絶対座標 `x`/`y` と島の `bounds`/`anchor` のみ。関係を渡していないため「関係の近さを配置へ反映する」根拠を欠く。

### 使われていない投影層

座標非依存ないし座標正規化済みの投影が、既に4層設計されている。AI入力経路はそのすべてを迂回している。

| 投影層 | 状態 |
|---|---|
| `getDerivedIslandEdges()`（`island_edge_aggregate.ts:78`） | 実装済み・呼出5箇所・AI未使用 |
| `buildAbstractMapExport()`（`abstract_map_export.ts`） | 実装済み・座標参照ゼロ・SafeMode実装済み・AI未使用 |
| `ContextBundleResponse`（`models_context.py:89`） | `build_bundle()` が `_STUB_DATASET` を返す（`:263`）・未接続 |
| `LLMRequest.inputs` IR（`llm_input_ir_spec.md` §4） | 凍結仕様・実装ゼロ |

背景と分析の全文は `02_Architecture/canvas-projection-asymmetry-2026-08-09.html` を参照。

## 対応方針（実装者向け）

`ADR-0069` の D1〜D4 の**採択された決定に従う**。ADR の推奨は D1=B（`coordinates` を任意化しエンドポイントごとに要否宣言）、D2=A（IR の関係語彙をキャンバス5値へ拡張）、D3=A（`islands` を追加し `cluster_candidates` と型で分ける）、D4=A（サーバ側 Python 実装＋TS との同値テスト）。

### 実装順序（推奨）

論理関係が効く順に段階適用する。全エンドポイント一括より回帰リスクが小さい。

1. `detect-contradiction` — `evidenceLinks` / `contradictionState` を渡す効果が最も直接的
2. `suggest-card-groups` — 既存の島・階層・`holdState` を渡す
3. `generate-narrative` — `edges`（`causal`/`negate`）を渡す
4. `suggest-layout` — 座標を渡す唯一の例外として契約へ明記し、あわせて `edges` を渡す
5. 残りのエンドポイント

### 注意事項

- **`ir_version` を繰り上げること。** 現スキーマは `ir_version: {"const": "1.0"}` かつ `additionalProperties: false`。D1〜D3 のいずれもスキーマ変更を伴う。
- **`llm_input_ir_spec.md` §6 の FixtureProvider 回帰データを再生成すること。** IR 仕様のみから決定論的に生成できること（AC-1 / AC-4）が仕様の受入条件である。
- **フロントエンドの既存 SafeMode 実装を削除しないこと。** 二重防御として残す。
- **既存の外部送出ガードを変更しないこと** — 二段 opt-in（`settings.py:473-481`）、ホスト allowlist（`:504-520`）、trusted-HTTP エンドポイント検証。これらは妥当であり本issueの対象外。

### 前提条件（着手前に解消または回避すること）

`02_Architecture/functional-dependency-integrity-2026-08-06.html` の **F-5「島所属の関数従属性が強制されていない」が未解消**である。カード→島の所属が一意に定まらない状態では、`islands` を含む IR の構築結果が一意にならない。F-5 を解消するか、投影側で一意化規則（先勝ち／後勝ち／全列挙）を明示すること。後者を選ぶ場合は決定を仕様へ記載する。

## 受入条件

- [ ] AC-1: `detect-contradiction` が `evidenceLinks` と `contradictionState` を受け取り、`confirmed` / `held` の矛盾を再提示しないことを integration テストで固定する。
- [ ] AC-2: `suggest-card-groups` が既存の島・`parentIslandId`・`holdState` を受け取り、`holdState` が保留中のカードを新規グループへ含めないことをテストで固定する。
- [ ] AC-3: `generate-narrative` が `edges` を受け取り、`causal` / `negate` が入力に含まれることをテストで固定する。
- [ ] AC-4: 全対象エンドポイントで、IR が `constraints.safe_mode == true` を満たさない場合に IR 生成が失敗すること（仕様 §7.1）をテストで固定する。
- [ ] AC-5: PII最小化チェック（§7.2）と構造化テキスト限定チェック（§7.3）が入力側で機能することをテストで固定する。
- [ ] AC-6: 上限超過時の切り詰めが決定論的であること（同一入力→同一出力、§5）をテストで固定する。
- [ ] AC-7: `test_ts_python_contract_drift.py` を投影ロジックへ拡張し、TS 実装（`buildAbstractMapExport` / `getDerivedIslandEdges`）と Python 実装の同値性を検査する。
- [ ] AC-8: `ir_version` が繰り上がり、`llm_input_ir_spec.md` が採択された D1〜D3 と一致している。
- [ ] AC-9: `02_Architecture/api.md` のリクエスト契約が実装と同期している。
- [ ] AC-10: 代表規模（カード300・島30程度）で入力トークン量を計測し、変化を記録する。上限値（`MAX_CARDS=200` 等、§5.1）が現行規模に合わない場合は別issueへ切り出す。
- [ ] AC-11: 既存フロントエンドが動作する（後方互換）。または必要な改修を同一 PR に含める。`03_Implement/deploy/tools/kj_canvas_demo.py` も追随させる。

## 依存関係

- `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`（採択が前提）
- `01_Plans/issues/issue-AI-REL-VOCAB-DRIFT-01-ir-canvas-relation-type-mismatch.md`（D2 の決定で同時に解消される。本issueと同一PRで実施してよい）

### 連携（依存ではない）

`SEC-AI-SAFEMODE-01` / `ADR-0068` は**同じ境界を対象としており、独立に実装すると衝突する**。`ADR-0068` は `/ai/*` の各リクエストモデルへ `safeMode` を追加する方向、本issueは IR §7.1 でサーバ側強制する方向である。**両者を並行実装しないこと。** 採択順序を保守者に確認してから着手すること。

## 検証

- `python -m pytest tests/ -k "ai or llm or ir" -q`
- `python -m pytest tests/ -q`（backend 全体回帰）
- frontend: `npx vitest run` および `npx tsc --noEmit -p .`
- `python 01_Plans/docs_check.py`
