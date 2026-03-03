# Issue Memo: FB-RM-MID-05 structural granularity export

- Type: Feature
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/i18n/locales/`, `01_Plans/adr/ADR-0007-future-backlog.md`, `04_Documentation/operations.md`
- Related Backlog: `FB-RM-MID-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Expected verification level: `unit`

## 1) 課題 / Problem statement

既存の bundle export は detail 相当の単一粒度のみで、
overview/detail を使い分けた再現可能な出力モードがなかった。
同一 Document から目的に応じて粒度を切り替える導線が不足していた。

## 2) 提案する解決策 / Proposed solution

- Bundle export に `exportGranularity`（`overview` / `detail`）を導入する。
- 出力物に `bundle_manifest.json` を追加し、選択粒度と生成時刻を記録する。
- `overview` 時は selected-card trace を抑止し、俯瞰用途の出力に寄せる。
- SharePanel に粒度選択 UI（radio）を追加し、bundle export 実行時に反映する。
- 非目標: backend API変更、SafeMode ポリシー変更、AI要約機能の新規導入。

## 3) 受入条件 / Acceptance criteria

- [x] overview/detail の粒度を選択して bundle export できる。
- [x] `bundle_manifest.json` に粒度情報が記録される。
- [x] `overview` では selected-card trace が出力されない。
- [x] 既存 detail export（outline/diagnostics/trace）との後方互換を維持する。
- [x] SafeMode 既定ON・share/export の漏えい防止に回帰がない。
- [x] unit test / typecheck が通過する。

## 4) 実装タスク分解 / Task breakdown

- [x] T1 `bundle_export.ts` に export granularity / manifest 追加。
- [x] T2 `buildExportBundleWithWorkers` へ同粒度ルールを反映。
- [x] T3 `SharePanel.tsx` に粒度選択 UI を追加。
- [x] T4 `App.tsx` で export granularity を context へ伝搬。
- [x] T5 `bundle_export.test.ts` / `SharePanel.test.ts` を更新。
- [x] T6 `ADR-0007` / `operations.md` / issue index を同期。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/export/bundle_export.test.ts src/ui/SharePanel.test.ts`
  - `npm run typecheck`
- 期待結果:
  - granularity/manifest/trace抑止がユニットテストで固定される。
  - TS型整合が崩れていない。

## 6) Progress log

- 2026-03-01: テスト先行で `bundle_manifest.json` と overview trace抑止の期待仕様を追加。
- 2026-03-01: `exportGranularity` を bundle export context に導入し、overview/detail 分岐を実装。
- 2026-03-01: SharePanel の bundle export UI に granularity radio を追加。
- 2026-03-01: unit test + typecheck を実行し、回帰なしを確認。
