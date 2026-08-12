# Issue: SEC-AI-SAFEMODE-01 SafeModeの未レビュー本文保護がAPI境界で強制されていない

- Type: Security
- Status: Draft
- Source Issue: TBD
- Priority: P0
- Owner: Unassigned
- Scope: `01_Plans/adr/ADR-0068-safemode-enforcement-at-api-boundary.md`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/frontend/src/api/client.ts`, `02_Architecture/api.md`, `THREAT_MODEL.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0068-safemode-enforcement-at-api-boundary.md`, `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`, `02_Architecture/architecture.html`, `02_Architecture/llm_escalation_policy.html`
- Expected verification level: `integration`

> **本issueは `ADR-0068` の採択を前提とする。** ADR が Proposed の間は着手しないこと。
>
> **追記（2026-08-09）: `AI-IR-PROJECTION-01` と境界が重複する。** `02_Architecture/llm_input_ir_spec.md` §7.1（`ADR-0009` Accepted の凍結仕様）が同じ SafeMode 保護を既に規定しており、`ADR-0069` はそれをサーバ側で実装する方向を提案している。**両者を並行して実装しないこと。** 詳細は `ADR-0068` の「追記（2026-08-09）」を参照。

## 課題

### 宣言されている不変条件

`02_Architecture/architecture.html` §05（CE-0 禁止事項、後退させてはならない項目）:

> safeMode既定ON時、未レビュー本文をAI入力へ含めてはならない。

`02_Architecture/llm_escalation_policy.html` §04（CE2-C2、**処理停止条件**）:

> 以下を検知した場合、処理を継続せず停止する。… 4. safeMode 保護後退（未レビュー本文混入を含む）

### 実装

**(1) safeMode パラメータが存在しない。** `models.py:941-943`:

```python
class SuggestLayoutRequest(BaseModel):
    doc: DocumentV1
    instruction: str | None = None
```

`SuggestMergesRequest`（`models.py:959-961`）、`GenerateNarrativeRequest`（`models_ai.py:52-56`）も同形。サーバは SafeMode の ON/OFF を知る手段を持たない。

**(2) 全カード本文が無条件でプロンプトへ入る。** `routes/ai.py:317-324`:

```python
for card in payload.doc.cards:
    card_lines.append(
        f'- id="{card.id}", text={json.dumps(card.text)}, x={card.x}, y={card.y}{critique_text}'
    )
```

`card.textReviewed` を見る分岐は無い。`suggest_layout`（`routes/ai.py:517-524`）は結果をそのまま `generate_with_fallback()` へ渡す。

**(3) 他に防御層が無い。** `grep -n "safe_mode\|safeMode\|unreviewed\|redact" routes/ai.py` の結果は、プロンプト内の指示文（273行）と出力側 `reviewState="unreviewed"`（611/650行）のみ。入力側のフィルタは存在しない。

### 帰結

SafeMode の未レビュー本文保護は**フロントエンドのみの強制**である。`KJ_ATLAS_LLM_PROVIDER=large-scale` 構成では、API を直接呼ぶ経路（curl / 別クライアント / 将来の MCP・エージェント連携）で**未レビュー本文が外部サービスへ送出される**。外部LLM利用時の実質的な信頼境界は API であり、そこに防御が無い。

### 影響範囲（対象エンドポイント）

`routes/ai.py` の全 LLM 呼び出しエンドポイントが対象。`DocumentV1` を受け取るものが特に該当する。

- `POST /ai/suggest-layout`
- `POST /ai/suggest-merges`
- `POST /ai/suggest-island-summary` / `POST /ai/propose-island-summary`
- `POST /ai/generate-narrative` / `POST /ai/check-narrative`
- `POST /ai/refine-card-text` / `POST /ai/suggest-card-groups` / `POST /ai/detect-contradiction` / `POST /ai/assess-card-importance`

実装前に `grep -n "@router.post" routes/ai.py` で網羅リストを再確認すること。

### 対象外（既に妥当な部分）

外部送出そのもののガードは堅く実装されており、**変更しないこと**。

- 二段 opt-in: `llm_large_scale_opt_in` + `llm_escalation_enabled`（`settings.py:473-481`）
- ホスト allowlist 突合（`settings.py:504-520`）
- trusted-HTTP エンドポイント検証（HTTPS必須・loopback例外・リダイレクト不追従）

## 対応方針

`ADR-0068` の D1 / D2 / D3 の決定に従う。ADR の推奨は D1=C（サーバ既定ON、緩和は明示要求かつ profile 許可時のみ）、D2=B（422 で拒否）、D3=A（未指定は SafeMode ON 扱い）。**採択された決定を正とする。**

実装時の注意:

- フロントエンドの SafeMode 実装は**二重防御として残す**（削除しない）。
- 拒否時のエラー応答に未レビュー本文そのものを含めないこと。`SEC-VALIDATION-LEAK-01` で確立した「入力値をエラーへ反射しない」作法（`main.py:157-167`）に従う。
- 緩和が適用された場合は監査へ記録する（`SEC-LLM-AUDIT-01` と連動）。

## 受入条件

- [ ] AC-1: SafeMode 有効時に未レビュー本文を含むリクエストが、採択された D2 の挙動（推奨: 422 拒否）で処理されることを、全対象エンドポイントについて integration テストで固定する。
- [ ] AC-2: パラメータ未指定のリクエストが安全側（SafeMode ON）に倒れることをテストで固定する。
- [ ] AC-3: 拒否・マスク時の応答に未レビュー本文が含まれないことを確認する。
- [ ] AC-4: 既存フロントエンドが改修なしで動作する（後方互換）。または必要な改修を同一 PR に含める。
- [ ] AC-5: `02_Architecture/api.md` のリクエスト契約を実装と同期する。
- [ ] AC-6: `THREAT_MODEL.md` に「API 直接呼び出しによる SafeMode 迂回」の緩和策を記載する。
- [ ] AC-7: 外部送出ガード（opt-in・allowlist・trusted-HTTP）が変更されていないことを既存テストで確認する。

## 検証

- `python -m pytest tests/ -k "ai or llm or safe" -q`
- `python -m pytest tests/ -q`（backend 全体回帰）
- frontend: `npx vitest run` および `npx tsc --noEmit -p .`
- `python 01_Plans/docs_check.py`

## 実地確認（2026-08-12、読取専用。ADR-0068 Proposed のため未実装）

本issueの主張を HEAD のコードで確認した（変更は加えていない）。

- **AI リクエストモデルに SafeMode パラメータは無い**。`SuggestLayoutRequest`（models.py:1449）/ `SuggestMergesRequest`（models.py:1467）等に `safeMode` なし。
- **プロンプトへの本文投入は無条件**。`routes/ai.py` のカード行構築（`id/text/x/y`）に `textReviewed` 分岐なし。`test_ai_prompt.py::test_build_prompt_includes_critique_constraints_and_context` は `'text="alpha"'` と `'critique="too close"'` がプロンプトに含まれることを**現在の挙動として固定**している。
- 入力側の SafeMode フィルタを assert するテストは存在しない（backend 941 tests は全て green＝保護の欠如を検知するテストが無い）。

→ 主張どおり **API 直接呼び出しで未レビュー本文が外部LLMへ送出される**。対処は ADR-0068 採択待ち（本issue冒頭の「着手しない」条件に従い未実施）。
