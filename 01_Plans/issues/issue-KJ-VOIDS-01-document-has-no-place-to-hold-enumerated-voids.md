# Issue: KJ-VOIDS-01 文書に空白（voids）を保持する場所が無い

- Type: Product Invariant / Data
- Status: In Progress
- Source Issue: `01_Plans/direction-review-2026-08-13.md` 優先3-1
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/types.ts`, `void_detection.ts`, `validate.ts`, `inquiry_bundle_safe_mode.ts`, `App.tsx`, `03_Implement/backend/src/kj_atlas_api/models.py`, `02_Architecture/schemas.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md`（§4 空白の列挙・§6 失敗の徴候）, `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`
- Expected verification level: `integration`

## 課題

方法論の正本は空白の列挙を「この技法の最大の産物のひとつ」とし、空白ゼロを失敗の徴候としている。

> `00_Prompt/kj_technique.md:159-167`
> **空白を見つける（この技法の最大の産物のひとつ）**
> 配置すると、「ここに本来あるべき束が無い」という空白が見える。
> 空白を必ず言語化して列挙する。「見当たらなかった」で済ませない。
> **空白がゼロ件なら、それは材料が完全なのではなく、探索が足りない。**
> 空白は次の情報収集の指示になる。

しかし `DocumentV1` には空白を保持できる場所が無い（`kj_technique.md:196` の「空白の指摘がゼロ件」を評価できない）。方向性レビュー優先3-1の「業務✓✓ / データ✗ / 機能✗」の典型。

## 対応方針

- 実施すること（D-a）:
  1. **データモデル**: `DocumentV1.voids?: VoidEntry[]` を追加（optional・後方互換）。`VoidEntry { id, kind, title, detail, cardIds?, islandIds?, resolved?, createdAt }`。`kind` は `unintegrated_card` / `orphaned_island` / `unspoken_island` / `unexplained_relation` / `unreviewed_content`。
  2. **決定論的検出（provider=none可）**: `detectVoidCandidates(doc)` を新設 — 構造ルールで空白候補を列挙（カード非統合・孤立島・表札なし・接続理由なし・未レビュー）。
  3. **ゼロ空白の注意喚起**: 検出が0件でも材料がある場合は「空白がゼロ件 — 探索が足りない」警告を返す（§4/§6）。
  4. **UI**: outline診断パネルに「空白を検出」ボタンを追加し、検出結果を `DocumentV1.voids` へ保存。
  5. **SafeMode**: `title`/`detail` は本文引用の可能性があるため redact、構造値（kind/cardIds/islandIds/resolved）は preserve。
  6. **契約同期**: schemas.md・Pydantic・drift test（VoidEntry を TYPE_MAP へ）・validate.ts。
- 実施しないこと:
  1. 空白の AI 生成（非決定論）。検出は決定論的ルールのみ。AI による空白提案は将来の別issue。
  2. `RoundHandoffV1.unresolvedQuestions` との統合（本issueでは文書レベルへの供給源の追加のみ。inquiry bundle への供給は別issue）。

## 受入条件

- [x] AC-1: `DocumentV1.voids?: VoidEntry[]` が TS/Python/schemas で同期し、drift test で固定される。
- [x] AC-2: `detectVoidCandidates` が決定論的（provider=none可）に空白候補を列挙する。
- [x] AC-3: ゼロ空白でも材料がある場合、警告（探索が足りない）を返す。
- [x] AC-4: SafeMode 投影が void の title/detail を redact し、構造値を preserve する。
- [x] AC-5: frontend 検証が voids をラウンドトリップで保持する。

## 検証

- `cd 03_Implement/frontend && npm run test -- src/domain/void_detection.test.ts src/domain/validate.test.ts src/domain/inquiry_bundle_safe_mode.test.ts && npm run typecheck`
- `python -m pytest tests/test_ts_python_contract_drift.py -q`
- `python 01_Plans/docs_check.py`

## 対応記録（2026-08-14）

D-a を実装した。

- `DocumentV1.voids?: VoidEntry[]` を frontend `types.ts` / backend `models.py` / `schemas.md` に追加。drift test の TYPE_MAP へ `VoidEntry` を追加。
- `domain/void_detection.ts` を新設 — 5種の構造ルールで決定論的に空白候補を列挙し、ゼロ空白時に警告（§4/§6）を返す。
- `validate.ts` に `parseVoids`（id/kind/title/detail/refs/resolved/createdAt を検証）。
- `inquiry_bundle_safe_mode.ts` に `VOID_FIELDS`（title/detail: redact・構造値: preserve）と `sanitizeVoidEntry` を追加。
- UI: SidePanel 診断パネルに「空白を検出」ボタン、App.tsx に `handleDetectVoids`（検出→`DocumentV1.voids` 保存→ゼロ空白警告表示）を追加。
- テスト: `void_detection.test.ts`（4件）・`validate.test.ts`（voids ラウンドトリップ）・`safe_mode.test.ts`（redact/preserve）。全 AC 完了。frontend 1446 tests・backend 61 tests 通過。
