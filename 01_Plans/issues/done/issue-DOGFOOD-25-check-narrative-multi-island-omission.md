# Issue: DOGFOOD-25 A/B照合が読み順の最初の島だけを報告し、複数島の取りこぼしを検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 189（シナリオ119・精肉/鮮魚 実装時の実走行観察）。2島構成の文書（meat-i/fish-i）で、ナラティブが鮮度・品揃え（meat-i）に言及し魚・ロス（fish-i）に触れない場合でも、モックが**読み順の最初の島（meat-i）だけ**を `a_missing_in_b` の参照にし、**複数島の文書で「先頭以外の島」の取りこぼしを正しく検出・固定できない**ことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ119）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §5（A/B照合は双方向・件数）, `02_Architecture/api.md`（check-narrative 契約）, `01_Plans/issues/done/issue-DOGFOOD-12-check-narrative-positive-path-hardcodes-island-i1.md`（島ID非依存化）, `01_Plans/issues/done/issue-DOGFOOD-14-check-narrative-lacks-b-missing-in-a-positive-path.md`（双方向の正パス）
- Expected verification level: `e2e`

## 課題

`mock_local_llm.py` の `check_narrative` は、`a_missing_in_b`（ナラティブが図解の島に触れていない）を報告する際、**読み順の最初の島だけ**を参照する（DOGFOOD-12 で島ID非依存にはなったが「先頭島固定」のまま）:

```python
if "未検証の主張" in prompt:
    island_ids = _READING_ORDER_ISLAND_LINE.findall(prompt) or _ISLAND_LINE.findall(prompt)
    island_id = island_ids[0] if island_ids else None  # 先頭島だけ
    ...
    "references": [{"id": island_id, "kind": "island"}],
    "counts": {"bMissingInA": 0, "aMissingInB": 1},
```

したがって:

- **複数島の文書で「先頭以外の島」の取りこぼしを検出・固定できない**。ナラティブが先頭島（meat-i）の話題に言及し、別の島（fish-i）に触れない場合でも、モックは**先頭島（meat-i）を取りこぼしとして誤報告**する。
- 業務フローE2E の A/B照合シナリオ（38/107/108/115/116）は**すべて単一島**のため、この制限が顕在化していなかった。
- 複数島の文書（島形成後の典型的な図解）で A/B 正パスを固定できない。

実機再現（iteration 189）:

```text
# 2島（meat-i/fish-i）・ナラティブがfish-iに触れない
# → {"message":"ナラティブが島meat-iに触れていない（a_missing_in_b）","counts":{"aMissingInB":1}}
#   （正しくは fish-i を取りこぼしとして報告すべき）
```

### なぜ問題か

- **複数島のA/B取りこぼし検出が未固定**: 島形成後の図解は複数島が典型であり、「どの島がナラティブで落ちたか」の検出（kj_technique.md §5）が単一島に限定されている。
- **誤報告の固定**: 先頭島のみを報告するモックでは、正しい島の取りこぼしを E2E で検証できない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は複数島の図解に対し、**ナラティブがどの島に触れていないか**（各島の取りこぼし）を報告してほしい。単一島だけの報告では不十分 | A/B照合は **advisory（read-only）** のまま。ナラティブ・図解は変更しない |
| **データ設計** | モックは読み順の**全島IDを `a_missing_in_b` の参照**として報告する（ナラティブ草稿は自由文で島IDを含まないため、決定的モックは言及島を判定できない→全島を候補として報告） | 既存の単一島シナリオは `aMissingInB:1` のまま成立（非後退） |
| **機能設計** | `check_narrative` の `a_missing_in_b` で**読み順の全島を references に載せ、counts を島数**に変更する。API契約（`CheckNarrativeResponse`）は不変 | バックエンド実装・API契約は変更しない。シナリオ119（2島）で `aMissingInB:2`・fish-i を含む報告を固定 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `check_narrative` で、`a_missing_in_b` に**読み順の全島ID**を references として報告し、counts を島数にする（先頭島固定を廃止）。
  2. シナリオ119（精肉・鮮魚・2島構成 meat-i/fish-i）で、**複数島の取りこぼし（aMissingInB:2・fish-i を含む）**を A/B照合で固定する。
- 実施しないこと:
  - check-narrative の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（38/107/108/115/116・単一島）のアサーションの変更（`aMissingInB:1` のまま非後退）。

## 受入条件

- [x] 2島（meat-i/fish-i）のA/B照合が `aMissingInB:2`・references に fish-i を含む（実走行で確認）。
- [x] 単一島（i1）は従来どおり `aMissingInB:1`・references に i1（非後退・実走行で確認）。
- [x] シナリオ119のA/B照合チェックが `ナラティブが島meat-i, fish-iに触れていない` かつ `aMissingInB:2` を assert し、業務フローE2E が **713/713 pass**（並行編集によるMGシナリオの干渉がない場合）。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 713/713（シナリオ119の MF ⑥A/B照合が複数島の取りこぼし）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの全島報告は「複数島の取りこぼしを検出可能」にする決定性表現であり、実LLMのA/B照合品質とは独立（本issueは検証ハーネスの能力向上）。DOGFOOD-12（島ID非依存）・DOGFOOD-14（双方向）の延長。
- ドッグフーディング観察起点（2026-08-16・iteration 189）: 精肉・鮮魚（2島 meat-i/fish-i）で、ナラティブが鮮度・品揃えに言及し魚・ロスに触れない場合に、モックが先頭島（meat-i）を誤報告することを再現。複数島のA/B取りこぼし検出が単一島に限定されていることを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、`check-narrative` のA/B照合を島ID非依存・双方向・複数島へ段階的に拡張し、任意の図解／ナラティブで検出セマンティクスをE2E固定できるようにした verification harness 改善として `Done` となっていた。
- `DOGFOOD-12` が島ID固定を解消し、`DOGFOOD-14` が反対方向 `b_missing_in_a` の正パスを追加し、`DOGFOOD-25` が複数島の取りこぼしへ拡張したため、check-narrative の成熟系列として3件を同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は23から20へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
