# ADR-0068: SafeMode の未レビュー本文保護を API 境界で強制する

- Status: Proposed
- Date: 2026-08-09
- Deciders: Maintainer（本ADRは提案。採択判断は保守者が行う）
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `models.py`, `models_ai.py`, `02_Architecture/api.md`, `02_Architecture/architecture.html`, `02_Architecture/llm_escalation_policy.html`, `03_Implement/frontend/src/api/client.ts`

## Context

`02_Architecture/architecture.html` §05（CE-0 禁止事項）は、後退させてはならない不変条件としてこう定めている。

> safeMode既定ON時、未レビュー本文をAI入力へ含めてはならない。

`02_Architecture/llm_escalation_policy.html` §04（CE2-C2 実行禁止事項）は、これを**処理停止条件**として再掲している。

> 以下を検知した場合、処理を継続せず停止する。… 4. safeMode 保護後退（未レビュー本文混入を含む）

コード実読で確認した実装は、この契約を満たしていない。

### 事実1: AI エンドポイントに safeMode パラメータが存在しない

`models.py:941-943`:

```python
class SuggestLayoutRequest(BaseModel):
    doc: DocumentV1
    instruction: str | None = None
```

`SuggestMergesRequest`（`models.py:959-961`）、`GenerateNarrativeRequest`（`models_ai.py:52-56`）も同形で、**safeMode を受け取るフィールドが無い**。サーバは SafeMode が ON か OFF かを知る手段を持たない。

### 事実2: 全カード本文が無条件でプロンプトへ展開される

`routes/ai.py:317-324`:

```python
def _build_prompt(payload: SuggestLayoutRequest) -> str:
    card_lines = []
    for card in payload.doc.cards:
        critique_text = f', critique={json.dumps(card.critique)}' if card.critique else ""
        card_lines.append(
            f'- id="{card.id}", text={json.dumps(card.text)}, x={card.x}, y={card.y}{critique_text}'
        )
```

`card.textReviewed` を参照する分岐は存在しない。`suggest_layout`（`routes/ai.py:517-524`）は `_build_prompt(payload)` の結果をそのまま `generate_with_fallback()` へ渡す。`grep -n "safe_mode\|unreviewed\|redact" routes/ai.py` は、プロンプト内の指示文（273行）と出力側の `reviewState="unreviewed"` 設定（611/650行）しか返さない。

### 帰結

SafeMode の未レビュー本文保護は**フロントエンドのみの強制**である。`KJ_ATLAS_LLM_PROVIDER=large-scale` の構成では、API を直接呼ぶ経路（curl、別クライアント、将来のMCP/エージェント連携）を通じて**未レビュー本文が外部サービスへ送出される**。外部LLM利用時の実質的な信頼境界は API であり、そこに防御が無い。

なお、外部送出そのもののガード（`llm_large_scale_opt_in` + `llm_escalation_enabled` の二段 opt-in、ホスト allowlist、trusted-HTTP 検証）は `settings.py:473-520` で堅く実装されている。欠けているのは「**送出してよい構成において、何を送るか**」の側である。

## 決定すべき論点

- **D1**: SafeMode の状態を誰が宣言し、サーバはどう知るか。
- **D2**: SafeMode ON かつ未レビュー本文が含まれる場合の振る舞い。
- **D3**: 既存クライアントとの後方互換。

## 選択肢

### D1: SafeMode 状態の伝達

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **A** | リクエストに `safeMode: bool` を必須追加 | 明示的。契約が読める | クライアントが `false` を送れば無効化できる（自己申告） |
| **B** | サーバ側の設定（profile / 環境変数）を正とし、リクエストでは受け取らない | クライアントに無効化されない | 文書単位・利用者単位の切替ができない |
| **C** | サーバ既定 ON。リクエストは「緩和の明示要求」（`allowUnreviewedText: true`）のみ受け付け、緩和は profile で許可された場合だけ有効 | 既定安全。緩和が監査可能な明示操作になる。`CE0-SAFEMODE-IF` の `allowUnreviewedText=false` 既定という既存語彙と一致 | 実装がやや複雑 |

### D2: 未レビュー本文の扱い

| 案 | 内容 |
|---|---|
| **A** | 該当カード本文を除外／マスクして送信（redact して継続） |
| **B** | 422 で拒否し、処理を停止（`llm_escalation_policy` CE2-C2 の「処理を継続せず停止する」に文字通り従う） |
| **C** | provider 種別で分岐（`local` は redact、`external` は拒否） |

### D3: 後方互換

| 案 | 内容 |
|---|---|
| **A** | 新フィールドを optional にし、未指定は「SafeMode ON」として扱う（fail-safe 既定） |
| **B** | 必須化し、未指定は 422 |

## 推奨（保守者の判断を拘束しない）

**D1=C、D2=B、D3=A** を推奨する。

理由: D1=C は既存の `CE0-SAFEMODE-IF`（`allowUnreviewedText=false` 既定）の語彙をそのまま API へ持ち上げるだけで、新しい概念を増やさない。D2=B は `llm_escalation_policy` CE2-C2 が既に「停止する」と明文化しており、redact での継続はその明文と食い違う。またフロントエンドは既に SafeMode 適用済みの内容を送る想定なので、サーバが未レビュー本文を検出した時点でそれは**クライアント側の契約違反か、意図的な迂回**であり、静かに握りつぶすより拒否して顕在化させる方が安全側である。D3=A は既存フロントエンドを壊さず、かつ未指定時に危険側へ倒れない。

`allowUnreviewedText=true` を profile 側で許可する場合は、`llm_escalation_policy` の監査必須項目へ「緩和が適用された事実」を記録すること（`SEC-LLM-AUDIT-01` と連動）。

## ADR-0047 ゲート判定

- **R-1（実使用の摩擦）**: 該当しない。コード監査による発見。
- **R-3（非機能境界の超過）**: **該当すると考える。** `ADR-0041` CVI と CE-0 の安全不変条件が、API 境界では実装により担保されていないことが判明した。宣言済み不変条件と実装の乖離であり、新機能追加ではないが、境界の再確認を要する。
- **R-2 / R-4**: 該当しない。

R-3 該当の是非は保守者が確認すること。

## Non-goals

- SafeMode のフロントエンド実装は変更しない（二重防御として維持）。
- 外部送出ガード（opt-in・allowlist・trusted-HTTP）は変更しない。既に妥当。
- proposal-only / 反スコアリング / `human_reviewed` 人手昇格の各境界は変更しない。
- LLM 応答側（出力）のフィルタリングは本ADRの範囲外。

## Traceability

- Implementation: `01_Plans/issues/issue-SEC-AI-SAFEMODE-01-safemode-not-enforced-at-api-boundary.md`
- Related: `02_Architecture/architecture.html` §05（CE-0 禁止事項の出典）
- Related: `02_Architecture/llm_escalation_policy.html` §04（CE2-C2 停止条件の出典）
- Related: `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`
- Related: `01_Plans/issues/issue-SEC-LLM-AUDIT-01-llm-calls-bypass-audit-dispatcher.md`
- Related: `THREAT_MODEL.md`
