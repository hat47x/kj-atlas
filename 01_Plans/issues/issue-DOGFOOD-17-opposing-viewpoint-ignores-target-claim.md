# Issue: DOGFOOD-17 反対視点提案が対象カードの主張に応答しない（モックがscenario1の汎用文面を返す）

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 182（シナリオ112・訪問看護 実装時の実走行観察）。targetカード `v1`（訪問効率の主張）へ `propose-opposing-viewpoint` を送っても、モックが scenario 1 の「待ち時間が短い」を参照する汎用文面を返し、**反対視点が対象の主張に応答（接地）しているか**を E2E で検証できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ112）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/ai_cognitive_externalization_requirements.md` §M4（反対視点は contradiction/evidence 構造に接地）, `01_Plans/issues/done/issue-AI-OPPOSE-01-opposing-viewpoint-and-evidence-gap-proposals.md`, `02_Architecture/api.md`（proposals/opposing-viewpoint 契約）
- Expected verification level: `e2e`

## 課題

`mock_local_llm.py` の `propose_opposing_viewpoint` は、対象カードに依らず **scenario 1 用の固定文面**（「逆の状況（待ち時間が短い）でも…」）を返す:

```python
if task == "propose_opposing_viewpoint":
    return json.dumps({
        "opposingText": "（モック）この主張は、逆の状況（待ち時間が短い）でも同じ帰結が起きる可能性があり、根拠の一般性が不足しています。",
        ...
    })
```

業務フローE2E の反対視点アサーション（scenario 18/48/51/53/66 等）は `"status":"proposed"` と `"opposingText"` の**キー存在**だけを確認し、本文内容は検証しない。したがって:

- **反対視点が対象カードの主張に応答（接地）しているか**を E2E で一切検証できない。
- 訪問看護（target=訪問効率の主張）に「待ち時間」を参照する無関係な反対視点が返っても、業務フローE2E は全部 pass する。
- M4（反対視点は contradiction/evidence 構造に接地）の核心が未固定。

実機再現（iteration 182）:

```text
# target v1 = "利用者宅での処置時間が長く訪問件数をこなせない（訪問効率・件数）"
# → opposingText = "（モック）この主張は、逆の状況（待ち時間が短い）でも同じ帰結が起きる…"（無関係）
```

### なぜ問題か

- **反対視点の接地（対象主張への応答）が未検証**: 反対視点が「何に対して反対しているか」が対象カードに接地されないと、提案の根拠（evidenceGap）判断の前提が崩れる。
- **モックが scenario 1 の文脈に固定**: 業態拡大イテレーションで別業態の反対視点を固定しようとすると、無関係な文面が返る。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は対象カードの主張（例: 訪問効率）に対して**その主張に応答する反対視点・根拠不足**を確認したい。反対視点は対象カードに接地されていなければ判断材料にならない | 反対視点は **proposal-only**（status=proposed・reviewState=unreviewed・自動適用なし）のまま |
| **データ設計** | プロンプトは `Target card: {"id":..., "text":...}` を含むため、モックは**対象カード本文を抽出して opposingText へ埋め込む**ことで「対象主張への応答」を決定的に表現できる | 既存の反対視点アサーションはキー存在のみ（status/opposingText/reviewState）のため非後退 |
| **機能設計** | `propose_opposing_viewpoint` の応答を「対象カードの主張（…）は、逆の状況でも…」の形へ変更し、シナリオ112の反対視点チェックで**対象主張（訪問件数）を参照する**ことを assert する。API契約（`OpposingViewpointProposal`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオ（18/48/51/53/66 等）はキー assert のみのため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `propose_opposing_viewpoint` で、プロンプトの `Target card:` から**対象カード本文を抽出し opposingText へ埋め込む**。
  2. シナリオ112（訪問看護）に **propose-opposing-viewpoint（反対視点提案）** を操作内容へ追加し、反対視点チェックで**proposal-only（status=proposed）かつ対象主張（訪問件数）を参照**することを assert する。
- 実施しないこと:
  - propose-opposing-viewpoint の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（18/48/51/53/66 等）の反対視点アサーションの変更（キー存在 assert・非後退）。

## 受入条件

- [x] target `v1` の反対視点が「訪問件数」を含む対象主張を参照する（実走行で確認）。
- [x] 既存シナリオ相当（scenario 18 等）も `"status":"proposed"`・`"opposingText"` を返す（非後退・実走行で確認）。
- [x] シナリオ112の反対視点チェックが `"status":"proposed"` かつ「訪問件数」を assert し、業務フローE2E が **664/664 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 664/664（シナリオ112の VN ⑤反対視点が対象主張を参照）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの対象カード埋め込みは「反対視点が対象主張に応答する」ことを検証可能にする決定性表現であり、実LLMの反対視点生成品質とは独立（本issueは検証ハーネスの能力向上）。
- ドッグフーディング観察起点（2026-08-16・iteration 182）: 訪問看護（target `v1`・訪問効率の主張）へ反対視点を送り、scenario 1 の「待ち時間」を参照する無関係な文面が返ることを再現。反対視点の接地（対象主張への応答）がE2Eで検証不能であることを特定した。
