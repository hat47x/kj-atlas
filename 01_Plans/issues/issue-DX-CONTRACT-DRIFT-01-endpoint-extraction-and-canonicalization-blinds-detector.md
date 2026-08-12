# Issue: DX-CONTRACT-DRIFT-01 check_contract_drift.py が抽出漏れと形状ベース正規化で実装ルートの63%を見落としていた

- Type: Bug
- Status: Done
- Source Issue: `DX-DESIGN-CHECK-01`, `DOGFOOD-METRIC-01`
- Priority: P1
- Owner: hat47x
- Scope: `03_Implement/backend/scripts/check_contract_drift.py`, `03_Implement/backend/tests/test_contract_drift_discrimination.py`, `02_Architecture/api.md`, `02_Architecture/contract_drift_baseline.json`
- Related ADR/Spec: `ADR-0067-three-element-constraint-design-method.md`, `ADR-0049-external-flat-rate-agent-collaboration.md`
- Expected verification level: `docs-check` + `pytest`

## 課題

`dogfood-analysis-synthesis-2026-08-12.md` §5 が「`check_contract_drift.py`（prefix解決で11→2に減っており、同種の識別力低下がないか未検証）」として横展開候補に挙げていた点を検証したところ、`DX-DESIGN-CHECK-01` と**同じ欠陥クラス**が実際に存在し、しかもより severe だった。

2つの独立した欠陥が重なっていた。

1. **抽出漏れ**: `ROUTE_DECORATOR_RE` がデコレータ直後に文字列が来ることを要求していたため、`@router.post(\n    "/x", ...)` のような複数行呼び出しを一切検出できなかった。`routes/ai.py` の15個のデコレータ中14個がこの形式で、実質 `/ai/*` 系がほぼ丸ごと検出対象外だった。加えて `@router.get("", ...)`（コレクションルート）はパスキャプチャが1文字以上を要求していたため空文字列にマッチせず、これも欠落していた。
2. **形状ベース正規化**: `_CONCRETE_ID_RE`（`DX-DESIGN-CHECK-01` の `_canonicalize_endpoint` と同型のkebab/snake形状マッチ）が、fixture IDかどうかに関わらずハイフン/アンダースコアを含む全セグメントを`{param}`へ潰していた。

両者の複合効果: 生の`@router`デコレータ43個 → 抽出漏れで20個 → 形状正規化でさらに16個の一意な正規形へ収縮。この16個全てがapi.mdの何らかのエンドポイントと「一致」したため、route_docs警告は常に0件だった。

**これは仮説的リスクではなく、実害が確認できた。** 修正後、`/ai/external-tasks/register`・`/ai/external-proposals/register`・`/ai/external-proposals/audit`（ADR-0049外部エージェント協調）の3ルートがapi.md未記載であることが判明した（後述の対応方針で解消）。

### DX-DOC-08 の完了記録の再検証（2回目）

`DX-DOC-08`（api.md エンドポイントカバレッジ不整合、Status: Done）のAC-2は次の2つの測定器の「0件」を根拠にしていた。

> 全実装済みバックエンドルートがapi.mdに文書化されている — §2.12-2.14に追加。**route_docs警告0件（check_contract_drift.py）**

`check_design_consistency.py` 側の同種の無効性は `DX-DESIGN-CHECK-01` で既に指摘済みだが、`check_contract_drift.py` 側の「0件」も**同じ根本原因（測定器と測定対象が同一主体の管理下にあり、測定器を弱めることで指標を満たせる）で無効**だった。DX-DOC-08は2つの独立した測定器の両方から、同じ理由で偽の「0件」根拠を得ていたことになる。取り消しを要する話ではない（実際に139件→大幅減の作業自体は妥当）が、記録の正確化として本issueをDX-DOC-08から参照する。

### 別枠の発見（本issueの範囲外）: api.mdの記述先行（未実装）エンドポイント

調査中、逆方向のドリフトも1件見つかった。`api.md` §2.12は `POST /ai/assess-card-importance`（`AssessCardImportanceRequest`/`Response`）を文書化しているが、`models_ai.py` に該当クラスは存在せず、`routes/*.py` にも対応する `@router` デコレータが存在しない。`check_contract_drift.py` の設計（routes→api.md方向のみ）はこの逆方向（api.md→routes、文書が実装より先行/陳腐化）を検出しない。本issueはこの逆方向チェックの追加を範囲としない。フォローアップが必要。

## 対応方針

- 実施したこと:
  1. `ROUTE_DECORATOR_RE` を修正し、開始丸括弧とパス文字列の間の空白・改行を許容（複数行デコレータに対応）。パスキャプチャを`+`から`*`へ変更（空文字列＝コレクションルートに対応）。
  2. `_CONCRETE_ID_RE`と形状ベース`_canonical()`を削除。`DX-DESIGN-CHECK-01`と同じ、api.mdが宣言する`{param}`位置に対するセグメント単位の構造マッチ（`endpoint_matches_documented`）へ置き換え。
  3. `contract_drift_baseline.json`は数値上偶然一致（route_docs: 0、total: 2）だったため更新不要——ただし意味は「検出器が見分けられない」から「43/43の実ルートが構造的に一致確認済み」へ変わった。
  4. 能力カナリア `test_contract_drift_discrimination.py` を追加（`DX-DESIGN-CHECK-01`と同じAST抽出方式）。ミューテーションテストで確認: 旧`_canonical`ロジックへ戻すと97件が失敗する。
  5. 発見された3つの未文書化ルートをapi.md §2.12へ追加（ADR-0049 / `external_agent_collaboration_spec.html`の実装を参照して記述）。
- 実施しないこと:
  1. api.md→routes方向（文書先行・陳腐化）の検出追加（上記「別枠の発見」、フォローアップ課題）
  2. `/ai/assess-card-importance` の実装または api.md からの削除判断（保守者判断が必要）

## 受入条件

- [x] AC-1: `check_contract_drift.py` が複数行`@router`デコレータとコレクションルート（空パス）を抽出できる
- [x] AC-2: kebab-case形状が同じだが異なるエンドポイント（`/ai/proposals/audit` vs `/ai/external-proposals/audit` 等）を区別できる
- [x] AC-3: 能力カナリアが旧ロジックへの回帰でfailすることをミューテーションテストで実証（97/237 failed）
- [x] AC-4: 発見された実ドリフト（3ルート）をapi.mdへ追加し、`check_contract_drift.py --baseline`がPASSする

## 検証

```bash
python 03_Implement/backend/scripts/check_contract_drift.py --baseline 02_Architecture/contract_drift_baseline.json
python -m pytest 03_Implement/backend/tests/test_contract_drift_discrimination.py -v
python 01_Plans/docs_check.py
python 01_Plans/issues/validate_active_issue_memos.py
git diff --check
```

## 完了記録（2026-08-12）

`DX-DESIGN-CHECK-01`のカナリア導入から着想し、`dogfood-analysis-synthesis-2026-08-12.md` §5が横展開候補として挙げていた`check_contract_drift.py`を実測した結果、同じ欠陥クラスに加えて独立した抽出漏れ（複数行デコレータ・空パス）も発見した。修正後、43件の実バックエンドルートが1件残らず構造的に検証可能になり、3件の実ドリフトが可視化・解消された。`DOGFOOD-METRIC-01` AC-2（能力カナリアの横展開）はこれで2件目の測定器に適用済み。残る対象は `codegen_results.md` / `ai_eval_results.md` の手記録系指標（`DOGFOOD-METRIC-01`参照）。

## 補足

- 発見経緯: `対応を進めてください`（ドッグフーディング状況確認・課題対応の一環）で`dogfood-analysis-synthesis-2026-08-12.md` §5の横展開候補を検証した際に発見。
- 三要素牽制の観点: 機能設計（api.md）とデータ設計（実装ルート）の照合手段そのものが機能不全だった、`DX-DESIGN-CHECK-01`と同型の事例。

## 対応記録（2026-08-12・逆方向ドリフト）

- **別枠の発見（api.md 記述先行の未実装エンドポイント）への対応**: `POST /ai/assess-card-importance` は `AI-ROUTE-01`（MMR final_judgement タスク）の計画として api.md §2.12 に文書化されているが、`models_ai.py` の `AssessCardImportanceRequest/Response` も `routes/ai.py` の `@router` も存在しないことを再確認。
- **対応**: api.md の該当セクション先頭に「**未実装（計画）**」を明記（実装前の正本として契約を維持）。check_contract_drift.py は routes→api.md 方向のみのためこの逆方向は検出しないが、文書の誤解を防ぐ明示で対応した。
