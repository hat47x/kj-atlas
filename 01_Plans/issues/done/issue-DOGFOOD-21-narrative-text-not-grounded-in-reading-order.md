# Issue: DOGFOOD-21 ナラティブ本文が読み順の島を参照せず、E2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 186（シナリオ116・ドラッグストア 実装時の実走行観察）。読み順 `drg-i` の文書で `generate-narrative` を実行しても、モックが**本文は汎用文字列**（「読み順に沿った解釈の下書きです」）を返し、`basedOnReadingOrder` 宣言と**本文が読み順の島を参照しているか**を E2E で検証できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ116）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §4（ナラティブは読み順に沿って叙述）, `00_Prompt/ai_kj_execution_procedures.md`（B型叙述）, `02_Architecture/api.md`（generate-narrative 契約・basedOnReadingOrder）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`（84シナリオが basedOnReadingOrder のみ assert）
- Expected verification level: `e2e`

## 課題

業務フローE2E で `generate-narrative`（ナラティブ）は84シナリオが固定しているが、全シナリオが `basedOnReadingOrder` **宣言**だけを確認し、**本文が読み順の島を実際に参照しているか**は検証しない。モックは本文を常に同一の汎用文字列で返す:

```python
if task == "generate_narrative":
    order_ids = _READING_ORDER_LINE.findall(prompt)
    return json.dumps({
        "text": "（モック・未レビュー）読み順に沿った解釈の下書きです。事実の主張ではありません。",
        "basedOnReadingOrder": order_ids,
        "warnings": [],
    })
```

したがって:

- **ナラティブ本文が読み順の島（叙述の骨格）に接地しているか**を E2E で一切検証できない。
- バックエンドがナラティブを読み順と無関係な本文に劣化させる（叙述の骨格を無視する）回帰が起きても、業務フローE2E は全部 pass する。
- ナラティブは「読み順に沿った叙述」が核心（kj_technique.md §4）だが、その本文の接地が未固定。

実機再現（iteration 186）:

```text
# 読み順 drg-i の文書で generate-narrative
# → text="（モック・未レビュー）読み順に沿った解釈の下書きです。…"（drg-i を本文で参照しない）
```

### なぜ問題か

- **ナラティブの叙述の骨格（読み順）が本文で未確認**: `basedOnReadingOrder` は宣言であり、本文がその順に沿っていることは別。
- **検証深度の偏り**: 84シナリオが宣言のみ assert で、本文の接地（叙述が読み順の島に触れる）が検証されない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は**読み順（島の並び）に沿ったナラティブ**を下書きとして得たい。ナラティブは叙述の骨格（読み順）に接地していなければ事実の整合性が保てない | ナラティブは **proposal 相当（read-only の下書き・未レビュー）** のまま。自動確定しない |
| **データ設計** | ナラティブプロンプトは読み順の島行を含むため、モックは**読み順の島IDを本文へ埋め込む**ことで「読み順に接地した叙述」を決定的に表現できる | 既存の `basedOnReadingOrder` 宣言 assert は、本文に島IDを埋めても成立（非後退） |
| **機能設計** | `generate_narrative` の応答本文を「読み順（<島ID>）に沿った解釈」の形へ変更し、シナリオ116のナラティブチェックで**本文が読み順の島（drg-i）を参照**することを assert する。API契約（`GenerateNarrativeResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオは `basedOnReadingOrder` 宣言 assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `generate_narrative` で、読み順の**島IDを本文へ埋め込む**（「読み順（<島ID>）に沿った解釈」）。
  2. シナリオ116（ドラッグストア）に **ナラティブ（読み順の島を本文で参照）** を固定し、ナラティブチェックで**本文が読み順の島（drg-i）を参照**することを assert する。
- 実施しないこと:
  - generate-narrative の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（1〜115）のナラティブアサーションの変更（`basedOnReadingOrder` 宣言 assert・非後退）。

## 受入条件

- [x] 読み順 `drg-i` の文書のナラティブ本文に「drg-i」が含まれる（実走行で確認）。
- [x] 既存シナリオ相当（島 `i1`）も `basedOnReadingOrder` を返す（非後退・実走行で確認）。
- [x] シナリオ116のナラティブチェックが `basedOnReadingOrder` かつ本文の「読み順（drg-i）」を assert し、業務フローE2E が **692/692 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 692/692（シナリオ116の DG ⑤ナラティブが読み順の島を本文で参照）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの島ID埋め込みは「ナラティブ本文が読み順の島に接地する」ことを検証可能にする決定性表現であり、実LLMの叙述品質とは独立（本issueは検証ハーネスの能力向上）。
- ドッグフーディング観察起点（2026-08-16・iteration 186）: ドラッグストア（読み順 `drg-i`）で generate-narrative を実行し、本文が汎用文字列で島を参照しないことを再現。ナラティブ本文の接地（読み順の島への叙述）がE2Eで検証不能であることを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、reading order を単なるID宣言ではなく、生成本文または配置提案の構造として実際に保持・反映することをE2Eで固定した verification harness 改善として `Done` となっていた。
- `DOGFOOD-21` はナラティブ本文の読み順接地、`DOGFOOD-30` は layout 提案の島・readingOrder構造保全を固定しており、reading-order invariant の意味側と構造側をなす小さなまとまりとして同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は27から25へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
