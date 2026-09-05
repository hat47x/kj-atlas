# Issue: DOGFOOD-12 A/B照合の正パスが島ID"i1"にハードコードされ、他島IDの文書は422になる

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 177（シナリオ107・データセンター運用 実装時の実走行観察）。島ID `dc-i` の文書で check-narrative の正パス（マーカー「未検証の主張」）を実行すると `422 LLM response included unknown island reference` が返り、島IDを `i1` にしたときだけ正パスが通ることを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ107）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `01_Plans/issues/done/issue-DOGFOOD-11-contradiction-detection-lacks-deterministic-positive-path.md`（同じく検証ハーネスの正パス盲点）, `02_Architecture/api.md`（check-narrative 契約）, `00_Prompt/kj_technique.md` §5（A/B照合の双方向・件数）
- Expected verification level: `e2e`

## 課題

`mock_local_llm.py` の `check_narrative` は、ナラティブ本文中のマーカー「未検証の主張」で `a_missing_in_b` を決定的に報告する（iteration 99 で導入）。しかしその応答は**島ID "i1" をハードコード**している:

```python
"message": "ナラティブが島i1に触れていない（a_missing_in_b）",
"references": [{"id": "i1", "kind": "island"}],
```

バックエンドの `_parse_narrative_check_response` は issue の references を**文書の実在島ID と照合**し、未知島なら `422 unknown island reference` を返す。したがって:

- **島ID が "i1" でない文書**（例: `dc-i`）で A/B 正パスを固定しようとすると、モックが存在しない "i1" を参照し **422** になる。
- 業務フローE2E の A/B 正パス固定は**文書の島IDが "i1" であることに暗黙依存**している（scenario 38 は島ID "i1" を使うことで回避している）。
- これはドキュメント化されていない隠れ制約であり、別の島ID を使う新しいシナリオを追加するたびに「なぜか422」という混乱を招く。

実機再現（iteration 177）:

```text
# 島dc-i + マーカー → 422 LLM response included unknown island reference
# 島i1   + マーカー → {"issues":[{"direction":"a_missing_in_b",...}],"counts":{...}}（成功）
```

### なぜ問題か

- **検証ハーネスの正パスがデータ依存（DOGFOOD-11 と同じ盲点）**: A/B 正パスが「島IDが i1 であること」に依存しており、任意の文書で検出セマンティクスを固定できない。
- **シナリオ追加の摩擦**: 業態拡大イテレーションで自然な島ID（`dc-i` 等）を使うと A/B 固定が 422 で失敗する。この制約はどこにも書かれていない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者はナラティブ草稿と図解の A/B 照合を任意の文書に対して実行したい。島IDは業態に応じ自然な命名（`dc-i` 等）を使うのが通常であり、**ID の命名に検証が依存してはならない** | A/B 正パスは **advisory（read-only）** のまま。ナラティブ・図解の確定フィールドには触れない |
| **データ設計** | モックはプロンプト中の**島ID（reading-order の island 行・島節）から実在する島を抽出**し、その島を `a_missing_in_b` の reference にする | 島が存在しない文書（reading-order に島がない）では正パスを報告しない（`issues:[]`） |
| **機能設計** | `check_narrative` の応答生成を「プロンプト内の最初の島ID」へ変更（`_READING_ORDER_ISLAND_LINE` → 島節 `_ISLAND_LINE` の順でフォールバック）。API契約（`CheckNarrativeResponse`）は不変 | 既存シナリオ38（島ID "i1"）は同じ応答を返すため非後退。backend 実装は変更しない |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `check_narrative` で、**reading-order の最初の島ID**（フォールバック: 島節の最初の島ID）を抽出して reference に使う。島がなければ `{"issues":[]}` を返す。
  2. シナリオ107（データセンター運用・島ID `dc-i`）で A/B 正パスを固定し、**島ID非依存の正パス**を業務フローE2E で検証する（`ナラティブが島dc-iに触れていない` ＋ `aMissingInB:1` を assert）。
- 実施しないこと:
  - check-narrative の**バックエンド実装・API契約の変更**。
  - 既存シナリオ38（A/B照合）の変更（島ID "i1" のままで非後退）。

## 受入条件

- [x] 島ID `dc-i` の文書で check-narrative 正パスが `a_missing_in_b`（reference に `dc-i`）を返し、422 にならない（実走行で確認）。
- [x] 島ID `i1`（scenario 38 相当）は従来どおり `i1` を reference に返す（非後退・実走行で確認）。
- [x] 島が存在しない文書では正パスを報告しない（`issues:[]`・実装で保証）。
- [x] シナリオ107の A/B チェックが `ナラティブが島dc-iに触れていない` ＋ `aMissingInB:1` を assert し、業務フローE2E が **629/629 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 629/629（シナリオ107の DC ⑤A/B照合が島ID非依存の正パス）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックのマーカー設計（「未検証の主張」）は維持し、reference の島IDだけを実在島へ動的解決する。実LLM利用時はプロンプトの島構造に従うため本制約はモック特有。
- ドッグフーディング観察起点（2026-08-16・iteration 177）: データセンター運用（島 `dc-i`）の A/B 正パス固定を試みて 422 を再現し、島IDを `i1` にすると通ることを対照確認した。


## 配置の整理（2026-09-05）

- 本Issueは、`check-narrative` のA/B照合を島ID非依存・双方向・複数島へ段階的に拡張し、任意の図解／ナラティブで検出セマンティクスをE2E固定できるようにした verification harness 改善として `Done` となっていた。
- `DOGFOOD-12` が島ID固定を解消し、`DOGFOOD-14` が反対方向 `b_missing_in_a` の正パスを追加し、`DOGFOOD-25` が複数島の取りこぼしへ拡張したため、check-narrative の成熟系列として3件を同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は23から20へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
