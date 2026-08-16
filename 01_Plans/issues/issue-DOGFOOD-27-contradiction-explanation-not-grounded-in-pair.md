# Issue: DOGFOOD-27 矛盾検出の説明文（explanation）がカード対を参照せず、E2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 191（シナリオ121・温浴/スパ 実装時の実走行観察）。`detect-contradiction` は最も多用される操作（84回）だが、説明文（`explanation`）が**常に汎用文字列**（「2枚のカードは相反する優先事項（トレードオフ）の関係にあります」）で、**カード対を参照しているか**を E2E で検証できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ121）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md`（矛盾検出・違和感の言語化）, `02_Architecture/api.md`（detect-contradiction 契約・explanation）, `01_Plans/issues/issue-DOGFOOD-11-contradiction-detection-lacks-deterministic-positive-path.md`（正パス固定）, `01_Plans/issues/issue-DOGFOOD-21-narrative-text-not-grounded-in-reading-order.md`（テキスト接地の同型）
- Expected verification level: `e2e`

## 課題

業務フローE2E の `detect-contradiction`（矛盾検出）は**最も多用される操作（84シナリオ）**だが、全シナリオが `"hasContradiction"` キー（+ DOGFOOD-11 以降の正パス値）だけを確認し、**説明文（`explanation`）が実際のカード対を参照しているか**は検証しない。モックの説明文は常に同一の汎用文字列:

```python
if "トレードオフ" in prompt:
    return json.dumps({
        "hasContradiction": True,
        "explanation": "（モック）2枚のカードは相反する優先事項（トレードオフ）の関係にあります。",
    })
```

したがって:

- **矛盾の説明がカード対（どのカードがなぜ矛盾するか）に接地しているか**を E2E で一切検証できない。
- バックエンドが説明を無関係な/汎用的な文面に劣化させる回帰（矛盾の根拠を説明しない）が起きても、業務フローE2E は全部 pass する。
- 説明文は矛盾検出の「違和感の言語化」（kj_technique.md）であり、カード対に接地していなければ判断の根拠にならない。

実機再現（iteration 191）:

```text
# 衛生・品質 vs 快適・コスト のカード対で detect-contradiction
# → explanation="（モック）2枚のカードは相反する優先事項（トレードオフ）の関係にあります。"
#   （カード対を一切参照しない）
```

### なぜ問題か

- **矛盾説明の接地が未検証**: 説明文がカード対を参照しないと、人間が矛盾の根拠を確認できない。
- **最も多用される操作の検証深度の偏り**: 正パス（hasContradiction）は固定されたが、説明文の接地は未固定。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は「どのカードがなぜ矛盾するか」を**カード対に接地した説明**として得たい。汎用説明では判断の根拠にならない | 矛盾検出は **advisory（read-only）** のまま。カード・島は変更しない |
| **データ設計** | 矛盾検出のプロンプトは `Card A (id=..): <text>` / `Card B (id=..): <text>` を含むため、モックは**両カードの本文を説明文へ埋め込む**ことで「カード対への接地」を決定的に表現できる | 既存の `"hasContradiction"` キー/正パス assert は、説明文を変えても成立（非後退） |
| **機能設計** | `detect_contradiction` の説明文を「（モック）カードA「…」とカードB「…」は相反する優先事項（トレードオフ）…」へ変更し、シナリオ121の矛盾チェックで**両カードの本文を説明文が参照**することを assert する。API契約（`DetectContradictionResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオは `"hasContradiction"` キー assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `detect_contradiction` で、プロンプトの `Card A:` / `Card B:` から**両カードの本文を抽出して説明文へ埋め込む**。
  2. シナリオ121（温浴・スパ）の矛盾検出チェックで、**説明文が両カード（衛生・品質 / 快適・コスト）を参照**することを assert する。
- 実施しないこと:
  - detect-contradiction の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（1〜120）の矛盾検出アサーションの変更（`"hasContradiction"` キー assert・非後退）。

## 受入条件

- [x] 衛生・品質 vs 快適・コスト のカード対で、説明文が両カードの本文を参照する（実走行で確認）。
- [x] 既存シナリオ（106〜120・`hasContradiction:true` assert）は非後退。
- [x] シナリオ121の矛盾チェックが `hasContradiction:true` かつ説明文が両カードを参照することを assert し、業務フローE2E が **727/727 pass**（並行編集によるMGシナリオの干渉がない場合）。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 727/727（シナリオ121の SP ④矛盾検出が説明文でカード対を参照）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックのカード本文埋め込みは「矛盾の説明がカード対に接地する」ことを検証可能にする決定性表現であり、実LLMの矛盾説明品質とは独立（本issueは検証ハーネスの能力向上）。
- ドッグフーディング観察起点（2026-08-16・iteration 191）: 温浴・スパ（衛生・品質 vs 快適・コスト）で detect-contradiction を実行し、説明文がカード対を一切参照しないことを再現。矛盾説明の接地（カード対への言語化）がE2Eで検証不能であることを特定した。
