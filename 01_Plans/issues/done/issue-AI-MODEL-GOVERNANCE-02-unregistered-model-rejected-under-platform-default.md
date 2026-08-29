# Issue: AI-MODEL-GOVERNANCE-02 プラットフォーム既定（空allowlist）でも未登録・無効モデルIDを拒否する（R3の登録検証）

- Type: Bug / Security (AI-MODEL-GOVERNANCE-01 の後続)
- Status: Done
- Source Issue: ドッグフーディング iteration 109（scenario 47 実装時の観察）。`verify_business_flow_e2e.sh` で available-models / 403 強制を業務フロー化する過程で、**プラットフォーム既定（空allowlist）では未登録モデルIDが governance を通過して LLM 呼び出しに到達する**ことを実走行で確認。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`（`_assert_model_allowed`）, `03_Implement/backend/tests/test_model_governance.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（scenario 47）
- Related ADR/Spec: `01_Plans/issues/done/issue-AI-MODEL-GOVERNANCE-01-per-operation-model-selection-and-tenant-restriction.md`（R3）, `01_Plans/adr/ADR-0065-llm-model-selection-by-task-complexity.md`
- Expected verification level: `integration` + 業務フローE2E

## 課題

`_assert_model_allowed()`（R3）は**テナント許容リストのみ**を検査し、許容リストが空（プラットフォーム既定）のときは**無条件に通過**する（`tenant_allowlist_effective_model_ids` が `None` を返すため）。ドキュメント上の意味論は「空allowlist = プラットフォーム既定 = **全 active 登録済みモデル**を許可」だが、実装は「**何でも許可**」になっており、**未登録・無効モデルIDが LLM 呼び出しへ到達してしまう**。

実走行（iteration 109・モックLLM）:
```
GET /ai/available-models                    → models: ["default"]（active 登録のみ表示＝正）
POST /ai/generate-narrative {"model":"totally-bogus-model"}  → 200（モック応答） ← ギャップ
```

- 非許容モデル（許容リスト外）→ 403 `model_not_allowed`（正・scenario 47 で凍結済み）
- 未登録モデル（空許容リスト・プラットフォーム既定）→ **200 で LLM に到達**（ギャップ）

これは R3 の fail-closed 精神（「許された集合の外は呼び出さない」）と、`available-models` が「active 登録済みのみ」を返す観点との**不整合**である。管理者がタイポしたモデルIDや無効化済みモデルIDを指定した呼び出しを、呼び出し前に遮断できない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 運用者は「テナントは許されたモデル（既定=active 登録済み）だけを使う」前提で監査する。**未登録IDが静かに通る**と、意図しないプロバイダへのフォールバック・課金想定外・監査不整合のリスク。非許容（制限）と非登録（存在しない/無効）は**区別して遮断**すべき | エラーコードを分離（`model_not_allowed` vs `model_not_registered`）し、運用者が「テナント制限」と「登録ミス/無効化」を判別できる |
| **データ設計** | 真実源はモデルレジストリ（`llm_model_registry`）と provider の `lifecycle_state`。**許容リストはテナント単位の絞り込み**であり、プラットフォーム既定の実効集合は「active 登録モデル（active provider 配下）」 | 許容リストに未登録IDが入っても実効集合は空集合になる（追加の登録検証はしない） |
| **機能設計** | `_assert_model_allowed()` を「許容リスト検査」＋「**登録・活性検査**」の二段にし、後者は許容リストの有無にかかわらず常時適用（fail-closed） | 既存の「非許容→403 model_not_allowed」は不変。**未登録/無効 → 403 model_not_registered** を新設。既存呼び出し（既定モデル=登録済み）は非後退 |

## 要件

- R3 の `_assert_model_allowed()` は、テナント許容リスト検査に加えて、**解決されたモデルIDが「active 登録モデル（active provider 配下）」であること**を常時検証する。
- 許容リスト外 → 403 `model_not_allowed`（既存・非後退）。
- 未登録/無効 → 403 `model_not_registered`（新設・fail-closed）。
- 既定モデル解決（`payload.model` 無し → `resolve_model_for_task`）は登録済みであるため非後退（AI 操作は 200/503 のまま）。
- `provider=none` の縮退でも中核操作は非後退（本検証は AI 経路のみ）。

## 受入条件

- [x] 空allowlist（プラットフォーム既定）で未登録モデルIDを指定 → **403 `model_not_registered`**（LLM 呼び出し前に遮断）。→ 実装: `_assert_model_allowed()` に登録・活性検査を追加（許容リスト検査とは独立に常時適用）。
- [x] 空allowlistで登録済み active モデルID → 非403（200/503 のまま・非後退）。→ 単体テスト + scenario 47 実走行で確認。
- [x] 非許容（許容リスト外）→ 403 `model_not_allowed`（既存挙動の非後退）。→ `test_allowlist_enforced_on_ai_route` 既存テストが継続 pass。
- [x] 単体テストで 403 `model_not_registered` 境界を固定。→ `test_model_governance.py` に `test_unregistered_model_rejected_under_platform_default` を追加。
- [x] 業務フローE2E（scenario 47）で未登録モデル → 403 を凍結。→ `verify_business_flow_e2e.sh` scenario 47 に「空許容リストでの未登録モデル → 403 model_not_registered」チェックを追加し実走行 pass。

## 検証計画

- `cd 03_Implement/backend && .venv/bin/python -m pytest tests/test_model_governance.py -q`
- `bash scripts/verify_business_flow_e2e.sh 8005`（scenario 47 含む・全 checks pass）
- `python 01_Plans/docs_check.py`（planning 文書整合）

## 補足

- 本issueは AI-MODEL-GOVERNANCE-01 R3 の**意味論ギャップ**を塞ぐ後続。R4（監査）は違反イベントの structured log を既に `_assert_model_allowed` で emit しており、`model_not_registered` も同経路で記録される（要確認・同一ログ）。
- 実装は `_assert_model_allowed()` 内に閉じる（ルート・スキーマ変更なし）。provider=large-scale / external 等の既定モデルが未登録の場合のみ新規 403 が発生するが、env seed が settings と同一式で登録するため整合する。
