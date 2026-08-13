# Issue: AI-REL-VOCAB-DRIFT-01 LLM投入IRとキャンバスで関係型の語彙が食い違っている

- Type: Contract Drift
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Unassigned
- Scope: `02_Architecture/llm_input_ir_spec.md`, `03_Implement/frontend/src/domain/types.ts`, `03_Implement/backend/src/kj_atlas_api/models.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`（D2）, `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3）, `02_Architecture/llm_input_ir_spec.md`
- Expected verification level: `unit`

## 課題

関係型の列挙値が、**二つの凍結された契約のあいだで食い違っている**。

| 契約 | 列挙値 | 出典 |
|---|---|---|
| キャンバス（TS） | `related` / `negate` / `causal` / `mutual` / `equivalence` | `03_Implement/frontend/src/domain/types.ts:78`（`KNOWN_EDGE_TYPES`）、`ADR-0048` D3 |
| バックエンド（Py） | 同上 ＋ `unknown` | `03_Implement/backend/src/kj_atlas_api/models.py:605`（`relationType`） |
| **LLM投入IR** | `related` / `arrow` / `negation` | `02_Architecture/llm_input_ir_spec.md` §2.3 / §4.2 |

差分の内訳:

- `arrow` はキャンバス語彙に存在しない。
- `negation` は `negate` と綴りが異なる（同義と推定されるが、仕様上の明示はない）。
- `causal` / `mutual` / `equivalence` は IR に対応する値を持たない。
- `unknown`（Python 側のみ）の IR での扱いが未定義。

IR は5値（または6値）から3値への**非可逆な正規化**を行うことになるが、**写像表が仕様に存在しない**。`llm_input_ir_spec.md` §2.3 の規則2は「`type` は列挙値のみ許可」と述べるのみで、キャンバス語彙からの変換規則を定めていない。

### 現時点の実害

**現時点で実害はない。** IR は実装されておらず（`ir_version` / `graph_summary` / `cluster_candidates` は `03_Implement` 配下に0件）、この写像を実行するコードが存在しないためである。

**IR を実装する時点で必ず決着が要る。** `causal` を `arrow` へ潰すと、AIが因果関係を受け取れなくなり、`AI-IR-PROJECTION-01` が解こうとしている問題（叙述の骨格が渡らない）が IR 経由で再発する。

### 経緯について

`ADR-0048` D3 によるキャンバス語彙の拡張が IR へ反映されなかった、というのが自然な推測だが、**本issueはその経緯を確認していない**。食い違いの事実のみが実測である。対応時に `ADR-0009` Phase B と `ADR-0048` の時系列を確認すること。

## 対応方針（実装者向け）

`ADR-0069` **D2 の採択された決定に従う**。ADR の推奨は A（IR の `relations.type` をキャンバス語彙5値へ拡張する）。

D2 が A 以外で採択された場合（3値維持＋写像表明記など）は、以下を必ず仕様へ明記すること。

- キャンバス語彙 → IR 語彙の完全な写像表（全5値＋`unknown` を網羅）
- 写像が非可逆であること、および失われる情報
- 逆方向（IR → キャンバス）の写像を行わないこと、または行う場合の規則

### D2=A 採択時のドラフト（2026-08-12・判断材料。D2 決定を拘束しない）

D2=A（IR をキャンバス語彙5値へ拡張）を採択する場合の、`llm_input_ir_spec.md` §2.3/§4.2 の変更ドラフト:

- `relations.type` の列挙値を **`related` / `negate` / `causal` / `mutual` / `equivalence`** へ統一。
- **`arrow` を廃止**: IR 独自値で、因果（causal）か方向（direction）か意図が曖昧。既存 IR データがある場合は `arrow` → `causal` への移行規則を明記（非可逆）。
- **`negation` → `negate` へ統一**: 同義の綴り違い。旧 `negation` は `negate` へ写像。
- **`unknown`（backend のみ）**: キャンバス語彙に存在しない。IR は「構造の正体」を渡す経路であり、未分類（unknown）は構造値として意味を持たないため、**IR には含めない**ことを推奨（backend の `relationType` は `unknown` を許容したまま、IR へは渡さない）。含める場合は D2 の明示的判断が必要。
- 写像が非可逆であること（`arrow` の意味確定、`unknown` の除外）と、逆方向（IR → キャンバス）は行わないことを §2.3 に明記。

このドラフトは `AI-IR-PROJECTION-01`（IR 実装）と同一 PR で適用可能。

## 受入条件

- [ ] AC-1: `llm_input_ir_spec.md` §2.3 / §4.2 の `relations.type` 列挙値が、採択された D2 の決定と一致している。
- [ ] AC-2: キャンバス語彙（`KNOWN_EDGE_TYPES` 全5値）と `unknown` のすべてについて、IR での扱いが仕様上一意に定まる。
- [ ] AC-3: 語彙の対応関係を検査するテストが存在し、いずれか一方に値が追加された場合に失敗する。`test_ts_python_contract_drift.py` の方式（生成的な集合比較）を踏襲すること。
- [ ] AC-4: D2=A を採る場合、`ir_version` の繰り上げが行われている。
- [ ] AC-5: `ADR-0048` D3 の語彙が正本であることが、両文書の相互参照で辿れる。

## 依存関係

- `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`（D2 の採択が前提）

### 連携（依存ではない）

`AI-IR-PROJECTION-01` と**同一 PR で実施してよい**。本issueを分けたのは、語彙ドリフトが IR 実装の可否とは独立に記録すべき事実だからである。IR を実装しない判断が下る場合でも、二つの凍結契約が食い違っている事実は残る。

## 検証

- `python -m pytest tests/test_ts_python_contract_drift.py -q`
- `python 01_Plans/docs_check.py`
- 手動: `grep -n "KNOWN_EDGE_TYPES" 03_Implement/frontend/src/domain/types.ts` と `llm_input_ir_spec.md` §2.3 の突き合わせ
