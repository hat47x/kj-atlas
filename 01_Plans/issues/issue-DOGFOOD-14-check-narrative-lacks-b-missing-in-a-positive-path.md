# Issue: DOGFOOD-14 A/B照合の b_missing_in_a（ナラティブだけにある主張）に決定的正パスがない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 179（シナリオ109・放送局/番組編成 実装時の実走行観察）。ナラティブがカードの根拠を欠く主張を含むケースを check-narrative へ送っても、モックが `{"issues":[],"counts":null}` を返し、`b_missing_in_a` 方向を報告できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ109）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §5（A/B照合は**双方向**・方向と件数で報告）, `02_Architecture/api.md`（check-narrative 契約・direction `b_missing_in_a | a_missing_in_b`）, `01_Plans/issues/issue-DOGFOOD-12-check-narrative-positive-path-hardcodes-island-i1.md`（同じく check-narrative の正パス盲点）
- Expected verification level: `e2e`

## 課題

業務フローE2E の A/B照合（check-narrative）正パスは、ナラティブ本文のマーカー「未検証の主張」で **`a_missing_in_b`（図解の島をナラティブが触れていない）方向だけ**を決定的に固定している。一方 **`b_missing_in_a`（ナラティブだけにあってカードに根拠のない主張）方向には正パスが存在しない**:

```python
if "未検証の主張" in prompt:
    ... a_missing_in_b ...
return json.dumps({"issues": []})
```

実機再現（iteration 179）:

```text
# ナラティブに「根拠のない主張」を含むケース → {"issues":[],"counts":null}（方向を報告できない）
```

### なぜ問題か

- **kj_technique.md §5 の A/B照合は双方向を要求**しているのに、E2E は `a_missing_in_b` しか正パスを固定できない。
- **`b_missing_in_a` 検出の回帰が全部 pass する**: バックエンドが常に `b_missing_in_a` を報告しない（または応答解析が方向を落とす）回帰が起きても、636チェックの業務フローE2E は検知しない。
- ナラティブに「カードにない主張」を混入させる分析者ミスは、定性的分析では典型的な品質リスク（根拠薄弱な結論）。その検出が未固定。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者はナラティブが**カードの根拠を欠く主張（b_missing_in_a）**を含まないかを検証したい。A/B照合は双方向（B型にだけある記述／A型で落ちた島）で初めて成立する | 検出は **advisory（read-only）**。ナラティブ・カードの文面は変更しない |
| **データ設計** | モックはナラティブ本文のマーカー句に基づき方向を決定的に応答する。`b_missing_in_a` は図解の参照を持たない（ナラティブ側の主張）ため reference なしの issue になる | 既存の `a_missing_in_b` マーカー（「未検証の主張」）とは別のマーカー（「根拠のない主張」）を使い、既存シナリオのナラティブに出現しない語彙を選ぶ |
| **機能設計** | `check_narrative` に `b_missing_in_a` の決定的正パス（`counts: {bMissingInA:1, aMissingInB:0}`）を追加し、シナリオ109の A/B チェックで固定する。API契約（`CheckNarrativeResponse`）は不変 | 既存の `a_missing_in_b` 正パス（シナリオ38/107/108）はマーカー分岐により非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `check_narrative` に、ナラティブ本文中のマーカー「根拠のない主張」で `b_missing_in_a`（reference なし・`counts:{bMissingInA:1, aMissingInB:0}`）を返す**決定的正パス**を追加。
  2. シナリオ109（放送局・番組編成）の A/B チェックを `b_missing_in_a` 方向で固定し、**A/B照合の双方向**を業務フローE2E で固定する。
- 実施しないこと:
  - check-narrative の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（38/107/108）の `a_missing_in_b` アサーションの変更（マーカー分岐で非後退）。

## 受入条件

- [x] 「根拠のない主張」を含むナラティブでモックが `direction:"b_missing_in_a"`・`counts:{bMissingInA:1, aMissingInB:0}` を返す（実走行で確認）。
- [x] 「未検証の主張」を含むナラティブは従来どおり `a_missing_in_b`（島参照）を返す（非後退・実走行で確認）。
- [x] シナリオ109の A/B チェックが `"direction":"b_missing_in_a"`・`bMissingInA:1` を assert し、業務フローE2E が **643/643 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 643/643（シナリオ109の BC ⑥A/B照合が b_missing_in_a 正パス）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- これで **A/B照合の双方向（b_missing_in_a / a_missing_in_b）が揃って E2E 固定**された（DOGFOOD-12 の島ID非依存化と併せて、check-narrative の検出セマンティクスが双方向で回帰から保護される）。
- モックのマーカー設計は既存の「未検証の主張」と同型。実LLM利用時はマーカーに依存せず本文から判断する。
- ドッグフーディング観察起点（2026-08-16・iteration 179）: 放送局・番組編成のナラティブ草稿に「視聴者満足度が過去最高を記録した」という根拠のない主張を含めて check-narrative を実行し、`{"issues":[],"counts":null}` が返り方向を報告できないことを再現した。
