# Issue: SEC-AI-SAFEMODE-01 SafeModeの未レビュー本文保護がAPI境界で強制されていない

- Type: Security
- Status: In Progress
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

- [x] AC-1: SafeMode 有効時に未レビュー本文を含むリクエストが、採択された D2 の挙動（推奨: 422 拒否）で処理されることを、全対象エンドポイントについて integration テストで固定する。— `_reject_unreviewed_text` を6ルート（suggest_layout/suggest_merges/suggest_island_summary/generate_narrative/check_narrative/propose_island_summary）へ配線。`test_ai_safemode.py` で実走行（未レビュー→422）。
- [x] AC-2: パラメータ未指定のリクエストが安全側（SafeMode ON）に倒れることをテストで固定する。— `allowUnreviewedText=None`（未指定）は fail-closed で拒否（test_ai_safemode.py の default 拒否テスト）。
- [x] AC-3: 拒否・マスク時の応答に未レビュー本文が含まれないことを確認する。— 422 応答は `unreviewed_text_not_allowed` コード＋固定メッセージのみ（本文非含有）。
- [~] AC-4: 既存フロントエンドが改修なしで動作する（後方互換）。または必要な改修を同一 PR に含める。— **frontend は現状、全文書（未レビュー含む）を送るため、未レビューカードを含む文書では AI 提案が 422 になる**。frontend 側の「未レビュー本文を除外して送る（または拒否を明示）」改修が別途必要。
- [ ] AC-5: `02_Architecture/api.md` のリクエスト契約を実装と同期する。— 未実施。
- [ ] AC-6: `THREAT_MODEL.md` に「API 直接呼び出しによる SafeMode 迂回」の緩和策を記載する。— 未実施。
- [ ] AC-7: 外部送出ガード（opt-in・allowlist・trusted-HTTP）が変更されていないことを既存テストで確認する。— 未実施（既存テスト 94 pass は確認済み）。

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

**追記（波及範囲は本文の記述より広い可能性）**: frontend の AI 提案経路も SafeMode フィルタが無い。
- `suggestLayout`（`client.ts:447`）は `JSON.stringify({ doc, instruction })` で**全文書を送信**。呼び出し元 `App.tsx` `handleSuggestLayout`（L3071）は `document` をそのまま渡し、`safeMode` による分岐・`textReviewed` フィルタ無し。
- `generateNarrative` も同形。`safeMode` の useState（App.tsx:1242、既定 true）は outline/export フラグのリセット（L8008）のみに使われ、**AI 機能をゲートしない**。
- タイトル提案の文脈（`cardTextsForSuggestion`、App.tsx:2379）は `textReviewed !== false` でフィルタするが、**`undefined`（未レビュー）は残る**ため実質保護していない。

→ つまり「未レビュー本文のAI入力保護」は backend にも frontend の提案経路にも**存在しない**。本文「フロントエンドのみの強制」は正確でなく、Web 利用者（SafeMode 既定ON）の未レビュー本文も LLM 提案時に外部へ送出され得る。SafeMode の意図的意味（共有時のみの保護か、AI入力常時禁止か）を含め、ADR-0068 の判断材料として要確認。

### 判断要約（2026-08-12・保守者決定用の一覧）

SafeMode の入力側強制を実装する経路は2つ（どちらも ADR は **Proposed** で、採択順序の判断が必要）:

| 経路 | 内容 | コスト | 備考 |
|---|---|---|---|
| **ADR-0068** | `/ai/*` リクエストモデルへ `safeMode` を追加し、未レビュー本文を拒否（D1=C・D2=B・D3=A 推奨） | 小〜中 | 現行ルートに直接適用。フロントエンドは既に SafeMode 適用済み内容を送る想定 |
| **ADR-0069** | 凍結仕様 `llm_input_ir_spec.md`（ADR-0009 Accepted）を AI 入力の実経路として実装。`constraints.safe_mode: const true` で SafeMode を IR 生成層で強制（D1=B・D2=A 推奨） | 大 | IR 全体（graph_summary/cluster_candidates/ir_version）が未実装。D2=A で関係語彙のドリフト（AI-REL-VOCAB-DRIFT-01）も同時解消 |

- 両者は同じ SafeMode 境界を対象とするため**並行実装しない**（ADR-0068 の「追記（2026-08-09）」）。
- **推奨**: 短期の SafeMode 強制は ADR-0068 を採択して `/ai/*` に適用し、ADR-0069/IR は別途（語彙ドリフト解決も含む）進める併用が現実的。ただし採択順序は保守者の判断。
