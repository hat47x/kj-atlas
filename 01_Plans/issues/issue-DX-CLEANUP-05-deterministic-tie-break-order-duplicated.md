# Issue: DX-CLEANUP-05 DeterministicTieBreak固定順序のdriftを検出する

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/types.ts`, `03_Implement/frontend/src/domain/validate_doc.ts`, `03_Implement/backend/tests/test_deterministic_tie_break_contract_sync.py`
- Related ADR/Spec: `02_Architecture/schemas.md` §11
- Expected verification level: `unit`

## 課題

Documentの`DeterministicTieBreak.order`がfrontend型・frontend validator・backend modelで別々に記述され、片側だけ変更しても直接検出する契約テストがなかった。Polygon handoffの同じ固定順序もbackendに存在する。

## 対応

- frontendでは `DOCUMENT_DETERMINISTIC_TIE_BREAK_ORDER` を型定義の隣に置き、tuple型とstrict validatorの双方が同じ定数を参照するよう統合した。
- backend/frontendを単一言語の生成工程へ寄せる変更は行わず、言語ごとのvalidation実装は維持した。
- cross-language contract testを追加し、次の4者を期待値の再ハードコードなしで比較する。
  1. `schemas.md` §11の`deterministicTieBreakOrder`
  2. frontendの共有定数
  3. backend `DeterministicTieBreak.order` default
  4. backend `PolygonHandoffInputContract.deterministicTieBreakOrder` default
- frontend validatorがローカル定数を再導入した場合もtestで拒否する。

## Acceptance

- [x] 言語境界の定義重複は維持し、cross-language contract testでdriftを検出する方針を確定した。
- [x] frontend内の型とvalidatorの二重定義を除去した。
- [x] frontend/backend/正本の固定順序が完全一致することを確認した。

## Validation

- `vitest run src/domain/validate_doc.test.ts src/domain/validate_roundtrip_reversibility.test.ts`: 44 passed
- `tsc --noEmit`: passed
- `python -m pytest -q 03_Implement/backend/tests/test_deterministic_tie_break_contract_sync.py 03_Implement/backend/tests/test_polygon_handoff_contract_route.py`: 10 passed
- `python -m ruff check 03_Implement/backend/tests/test_deterministic_tie_break_contract_sync.py`: passed
- `python 01_Plans/docs_check.py --root .`: passed（33 active memos）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`: passed（33 active memos）
