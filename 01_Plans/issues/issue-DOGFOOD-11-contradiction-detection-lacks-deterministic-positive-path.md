# Issue: DOGFOOD-11 業務フローE2Eが矛盾検出の正パスを固定できない（モックに決定的正パスなし）

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 176（シナリオ106・警察/公安 実装時の実走行観察）。防犯強化 vs 監視不安のトレードオフ対を detect-contradiction へ送ってもモックは常に `hasContradiction:false` を返し、「矛盾を表面化する」シナリオ主張を E2E が検証できないことに気づいた。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ106）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `01_Plans/issues/issue-DOGFOOD-06-verification-paths-abnormal-case-coverage.md`（検証は正常系も異常系も assert する）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`（シナリオ1〜106・622 checks）
- Norms: `KJT-SIGN-05`（`hasContradiction:false` 固定のモックは、対立が検出できないまま「調和的にまとまった」ことにされる失敗様態そのものを検証不能にしていた）
- Expected verification level: `e2e`

## 課題

業務フローE2E は**決定性モックLLM（`mock_local_llm.py`）**を応答源として標準業務フローを固定する。check-narrative（A/B照合）はナラティブ本文中のマーカー「未検証の主張」で決定的に `a_missing_in_b` と `counts` を報告し、**不整合検出の正パスを E2E で固定**できる（scenario 38・A/B照合の方向＋件数）。一方 **detect-contradiction は常に `hasContradiction:false` を返し、正パス（矛盾あり）が存在しない**。

その結果:

- シナリオ1〜106の各「矛盾検出で表面化」チェックは `"hasContradiction"` **キーの存在**だけを検証し、**矛盾が実際に検出されること**を一切検証しない。
- 仮にバックエンドが常に `hasContradiction:false` を返す回帰（LLMが矛盾を検出しない・応答解析が false 固定）が起きても、業務フローE2Eは **622/622 で全部 pass する**。
- check-narrative と detect-contradiction のモックに**非対称**があり、A/B検出は固定できても矛盾検出は固定できない。

### なぜ問題か

- **DOGFOOD-06 の精神（検証は正常系も異常系も assert）と矛盾**: 矛盾検出の**正常系（矛盾あり）**が assert されていない。
- **シナリオの主張と検証の乖離**: 各シナリオ定義は「〜のトレードオフを矛盾検出で表面化」と述べるが、E2Eはその表面化の可否を検証できない。検証ハーネスの検出能力に盲点がある。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は「対立する2枚のカード」（トレードオフ・相克）を矛盾検出で表面化し、判断の根拠にしたい。矛盾検出は KJ 分析の中核操作であり、**「検出されること」を回帰から守る**必要がある | 正パスは **proposal 相当（read-only の報告）**のまま。自動適用・確定への昇格はしない（既存の proposal-only / SafeMode を緩和しない） |
| **データ設計** | 入力は `textReviewed=true` の確定カード本文、出力は `hasContradiction` と `explanation`。モックは入力プロンプト中のマーカー句に基づき決定的に応答する | マーカー語は**既存シナリオのカード文面に出現しない語彙（「トレードオフ」）**を選ぶ。既存の `hasContradiction:false` アサーション（QM・MK）はマーカー不在のため不変 |
| **機能設計** | `mock_local_llm.py` の `detect_contradiction` に check-narrative と同型のマーカー正パスを追加し、シナリオ106の矛盾検出チェックを `"hasContradiction":true` で固定する | API契約（`DetectContradictionResponse`）は不変。プロンプト内容のみ変わるため既存シナリオは非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `detect_contradiction` に、プロンプト中の「トレードオフ」マーカーで `hasContradiction:true` を返す**決定的正パス**を追加（check-narrative の「未検証の主張」と同型）。
  2. シナリオ106（警察・公安）の矛盾検出チェックを `"hasContradiction":true` で固定し、**「矛盾が実際に検出される」**ことを業務フローE2E で固定する。カード p1 の文面にトレードオフ句を追記（注意事項「防犯強化と住民の安心・プライバシーのトレードオフ」と整合）。
- 実施しないこと:
  - detect-contradiction の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（1〜105）の矛盾検出アサーションの変更（schema のみのままでよい。モックのマーカーが既存文面に出現しないことを確認済み）。

## 受入条件

- [x] モックが「トレードオフ」を含むカード対で `hasContradiction:true` を返す（実走行で確認）。
- [x] マーカーを含まないカード対（既存シナリオ相当）は `hasContradiction:false` のまま（非後退。QM・MK の false アサーションを維持）。
- [x] シナリオ106の矛盾検出チェックが `"hasContradiction":true` を assert し、業務フローE2E が **622/622 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 622/622（シナリオ106の PL ③矛盾検出が正パス）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックのマーカーは check-narrative（「未検証の主張」）の決定性パターンを踏襲した設計。実LLM利用時はマーカーに依存せず本文から判断する（本issueは検証ハーネスの能力向上であり、実LLMの品質を変えない）。
- ドッグフーディング観察起点（2026-08-16・iteration 176）: シナリオ106（警察・公安）実装時の実走行で、防犯強化 vs 監視不安の対立対を送っても `hasContradiction:false` が返り、注意事項が述べる「トレードオフを矛盾検出で表面化」を E2E が検証できないことに気づいた。
