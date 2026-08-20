# Issue: AI-IMPORTANCE-SCORING-01 重要度評価エンドポイントが「AIは内容を採点せず」と抵触している

- Type: Product Invariant / AI Integration
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Unassigned
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/deploy/tools/kj_canvas_demo.py`, `00_Prompt/domain.md`, `03_Implement/frontend/src/api/client.ts`
- Related ADR/Spec: `00_Prompt/domain.md`, `00_Prompt/representative_visual_cue_requirements.md`, `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`, `02_Architecture/canvas-projection-asymmetry-2026-08-09.html`（§07）, `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`
- Norms: `DOM-CORE-04`, `DOM-AI-07`, `DOM-AI-09`
- Expected verification level: `integration`

## 課題

### 宣言されている不変条件

`00_Prompt/domain.md` §3.1（`DOM-AI-07` / `DOM-CORE-04`）:

> ただし、カード本文以外の入力を一律に必須化しません。… **AIは内容を採点せず**、出典や文脈を推測せず、利用者の確認前に本文や状態を変更しません。

条件節を伴わない無条件の宣言である。

補強（ただし画像限定の非目標であり、本文ベースの評価を直接禁じてはいない）── `00_Prompt/representative_visual_cue_requirements.md` §2.2 非目標:

> （非目標）画像による自動分類、品質評価、**重要度評価**、感情判定。

### 実装

`03_Implement/backend/src/kj_atlas_api/routes/ai.py:763-770`:

```python
def _build_assess_card_importance_prompt(payload: AssessCardImportanceRequest) -> str:
    cards = "\n".join(f'  - id="{c.id}", text="{c.text}"' for c in payload.cards)
    return (
        f"Assess the importance of each KJ-method card relative to the others. "
        f"Rate each as 'high', 'medium', or 'low' with a brief rationale. "
        ...
    )
```

`POST /ai/assess-card-importance` は、カード本文を相互比較して `high` / `medium` / `low` の評定を返す。これは内容の採点そのものである。

### 拡大方向にある

2026-08-09 のコミット `2aeb23d9` が追加した `03_Implement/deploy/tools/kj_canvas_demo.py` は、このエンドポイントをデモの一工程に据えている（`:136-151`）。

```python
def phase4_importance():
    """重要度評価。"""
    demo_phase("Phase 4: 重要度評価 → 優先順位付け")
    ...
    for a in data["assessments"]:
        bar = {"high": "■■■", "medium": "■■□", "low": "■□□"}.get(a["importance"], "???")
        print(f"  {bar} {a['cardId']}: {a.get('rationale', '')[:50]}")
```

カードの序列がバーとして可視化される。**文書上の非目標が、実装とデモの両方で既成事実化しつつある。**

### なぜKJ法として問題か

KJ法は少数意見・外れた事例を掬い上げる方法である。`00_Prompt/domain.md` §3.1（`DOM-AI-09`）は明示的に「少数意見、外れた事例、矛盾、違和感をノイズとして消さない」と述べる。AIが `low` を付けたカードは、UI上どう扱われるかに関わらず、利用者の注意配分に影響する。多数派に埋もれた1枚こそがKJ法の価値である場合に、それを `low` と評定することは方法論の目的に逆行する。

## 対応方針

**本issueは決定を含まない。** 実装が明文の要求と抵触している事実を記録し、保守者の判断を仰ぐものである。

考えられる方向:

- **D-a: エンドポイントを廃止する。** `assess-card-importance` と `kj_canvas_demo.py` の Phase 4 を削除する。最も単純で、宣言との整合が確実。
- **D-b: 構造的観測へ置換する。** 採点をやめ、「このカードは3つの連結成分を橋渡ししている」「このカードは2件の矛盾サブグラフの当事者である」といった**事実の提示**へ変える。順位付けではないため反スコアリングと衝突しない。
- **D-c: `domain.md` の宣言を改める。** 採点を許容する範囲を明文化する。ただし `ADR-0041` の CVI 群および KJ法の方法論的根拠との整合を示す必要がある。

**D-b の実装基盤は既に設計されている。** `02_Architecture/llm_input_ir_spec.md` §4 の `graph_summary`（`centrality` / `connected_components` / `contradiction_subgraphs`）がそれに当たる。ただし IR は未実装であり、その実装は `ADR-0069` / `AI-IR-PROJECTION-01` の範囲である。**D-b を選ぶ場合は `ADR-0069` の後に置くこと。** D-a と D-c は独立に進められる。

D-a〜D-c の選択が設計判断として重いと判断される場合は、独立 ADR へ切り出すこと。本issueは不整合の記録として起票しており、**ADR 化の要否は保守者が判断する**。

## 受入条件

採択された方向により異なる。共通するもの:

- [x] AC-1: `DOM-AI-07`（`00_Prompt/domain.md` §3.1・§7）の宣言と、`routes/ai.py` の実装が整合している状態をテストで固定する。
- [x] AC-2: `03_Implement/deploy/tools/kj_canvas_demo.py` が採択された方向に追随している。カードを序列として可視化する表示が残っていない（D-c を除く）。
- [x] AC-3: フロントエンド（`client.ts` および呼び出し側UI）が追随している。
- [x] AC-4: `00_Prompt/representative_visual_cue_requirements.md` §2.2 の非目標一覧と矛盾しない。

D-a を採る場合:

- [x] AC-5a: `POST /ai/assess-card-importance` が存在しないこと、および関連する型（`AssessCardImportanceRequest` / `AssessCardImportanceResponse` / `_CardAssessment`）が削除されていることを確認する。

D-b を採る場合:

- [ ] AC-5b: 応答が順位・等級を含まず、構造的事実のみであることをテストで固定する。`high`/`medium`/`low` に相当する語彙が応答スキーマに存在しないこと。
- [ ] AC-6b: 同一文書に対する応答が決定論的であること（`graph_summary` は非LLM前処理であるため、LLM呼び出しを要しない）。

D-c を採る場合:

- [ ] AC-5c: `00_Prompt/domain.md` の改訂が、`ADR-0041` の CVI 群および KJ法の方法論的根拠との整合を明示している。
- [ ] AC-6c: 「少数意見、外れた事例をノイズとして消さない」（`domain.md:86`）との両立方法が記載されている。

## 依存関係

なし（D-a / D-c は独立に着手可能）。

### 連携（依存ではない）

D-b を選ぶ場合のみ、`01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md` の完了を待つ（`graph_summary` の実装がそちらに含まれるため）。`ADR-0069` はこの課題を明示的に非目標として分離している。

## 検証

- `python -m pytest tests/ -k "importance or assess" -q`
- `python -m pytest tests/ -q`（backend 全体回帰）
- frontend: `npx vitest run` および `npx tsc --noEmit -p .`
- `python 01_Plans/docs_check.py`
- 手動: `python 03_Implement/deploy/tools/kj_canvas_demo.py`（`--real` なし）が採択後の挙動と一致すること

## 完了記録（2026-08-11）

- D-aを採用し、カード内容を`high` / `medium` / `low`へ序列化するAPI、Pydantic型、prompt/parser、mock応答、統合テストを削除した。
- デモから重要度評価工程を削除し、全9タスク・6フェーズへ再構成した。
- フロントエンドには呼び出しAPI・UIが存在しないことを確認した。
- `test_ai_anti_scoring_contract.py`でroute、型、実装、デモから採点surfaceが復活しないことと、`domain.md`の明文不変条件を固定した。
- 将来の代替はADR-0069の`graph_summary`による、順位・等級を含まない構造的観測に限定する。
- 検証: backend全体 `909 passed, 33 skipped, 8 deselected`、対象回帰30件、ruff、docs-check、mock demo完走（9タスク・6フェーズ、終了後port解放）を確認した。

## 記録の正確化（2026-08-13、DOMAIN-SCORING-SURFACE-01 AC-6）

本issueの防御は**バックエンドのAI経路にしか及んでいなかった**。利用者が見る画面側（クライアント決定論計算）には、同一不変条件（`00_Prompt/domain.md`「AIは内容を採点せず」）に抵触する採点面が残存しており、`DOMAIN-SCORING-SURFACE-01`（P1）で検出・修正した。

| 経路 | 採点 | 状態 |
|---|---|---|
| AI（サーバ） | カード重要度 high/medium/low | 本issueで削除・テスト固定 |
| 画面（クライアント決定論） | 健全性 N%・接続スコア・impact等級 | **DOMAIN-SCORING-SURFACE-01（案A）で件数・種別へ転換** |

これは本issueの判断（D-a採択）の取り消しではなく、**同一不変条件の防御が経路ごとに個別実装されており、横断的に効く機構が無かった**事実の記録である（`ADR-0041`「single guard」の再検討材料）。防御がサーバ経路だけで完結していたと読める既存記録を正確化する。
