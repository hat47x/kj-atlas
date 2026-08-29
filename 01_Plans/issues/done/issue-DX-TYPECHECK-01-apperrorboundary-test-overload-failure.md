# Issue: DX-TYPECHECK-01 `tsc --noEmit`がAppErrorBoundary.test.tsで失敗する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `MVP-EXIT-01`（アドホック・モンキーテスト中に副次的に検出。canvas/UI操作の探索対象ではないため未修正）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/AppErrorBoundary.test.ts`
- Related Backlog: `DX-TYPECHECK-01`
- Related ADR/Spec: `01_Plans/issues/done/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`（G7 ビルドと回帰）
- Expected verification level: `unit`

## 課題

`npm run typecheck`（`tsc --noEmit`）が現在1件のエラーで失敗する。

```
src/ui/AppErrorBoundary.test.ts(40,9): error TS2769: No overload matches this call.
  The last overload gave the following error.
    Argument of type '{ getRecoverySnapshot: () => null; onRecover: Mock<Procedure>; }' is not assignable to parameter of type 'Attributes & AppErrorBoundaryProps'.
      Property 'children' is missing in type '{ getRecoverySnapshot: () => null; onRecover: Mock<Procedure>; }' but required in type 'AppErrorBoundaryProps'.
```

`React.createElement(AppErrorBoundary, props, child)` の3引数形式で子要素を渡しているが、TypeScriptのオーバーロード解決が `props` 単体に `children` を要求している。`AppErrorBoundary`（`UI-RESILIENCE-01`, 2026-08-12）とそのテスト（2026-08-13）は直近の変更であり、本issueを起票した時点でmain相当のツリーに存在した。

`vitest run` はこのファイルを含めて成功する（型検査を伴わないため）。`tsc --noEmit` のみが失敗する。

## 再現手順

```bash
cd 03_Implement/frontend
npx tsc --noEmit
```

## 対応方針

- 実施すること: `AppErrorBoundaryProps.children` を必須のまま保つ場合はテスト側で明示的に `children` をpropsへ渡す。または `children` をオプショナルにできるか `AppErrorBoundary` の設計次第で判断する。
- 実施しないこと: 本issueでは修正しない。直近（2026-08-12/13）の関連実装が進行中である可能性があり、対象外として起票のみ行う。

## 予算申告

- 複雑性予算（`ADR-0043`）: N/A
- 性能予算（`ADR-0046`）: N/A
- 触れるUQ次元（`ADR-0044`）: N/A

## 受入条件

- [ ] `npx tsc --noEmit` がエラー0件で完了する。
- [ ] `AppErrorBoundary.test.ts` の既存テストに退行がない。

## 検証計画

- 実行する確認: `npx tsc --noEmit`、`vitest run src/ui/AppErrorBoundary.test.ts`。
- 期待結果: 型検査・テストともに成功。

## 補足

- `MVP-EXIT-01` のアドホック・モンキーテスト（キャンバス操作、ズーム、ドラッグ等）の副産物として発見した。本issueが対象とする範囲（起動時エラー境界のテスト型定義）は今回のモンキーテストの主眼と無関係なため、調査・修正はここまでに留める。

## 対応記録（2026-08-13）

- **`AppErrorBoundaryProps.children` をオプショナル化**して解消（`b8a03df0`・SEC-AI-SAFEMODE-01 AC-4 の一環で実施済み）。`React.createElement(AppErrorBoundary, props, child)` の3引数形式が `children` を必須要求しなくなった。
- 検証: `tsc --noEmit` の `AppErrorBoundary.test.ts(40,9)` エラーは解消。残る `CanvasShell.tsx` の `WheelEvent` エラーは並行作業（QA-MONKEY-18）由来で別issue。
