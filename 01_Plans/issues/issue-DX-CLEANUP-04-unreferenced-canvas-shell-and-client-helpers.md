# Issue: DX-CLEANUP-04 CanvasShell.tsxとclient.tsに未参照ヘルパーが残存

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/CanvasShell.tsx`, `03_Implement/frontend/src/api/client.ts`
- Related ADR/Spec: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`
- Expected verification level: `unit`

## 課題

- 現在の問題: 次の2つのexportは、リポジトリ全体で定義箇所以外に呼び出し元が無い。
  1. `getFocusWorldPointForReference`（`CanvasShell.tsx:56`）: 消費している`FocusReference`型自体は同ファイル内の他箇所（props, state）で使われているが、この関数自体を呼ぶ箇所は無い。
  2. `suggestIslandSummary`（`api/client.ts:652`）: `POST /ai/suggest-island-summary`のクライアントラッパー。backend側のroute（`routes/ai.py:553`）自体は生きているが、フロントエンドからこのラッパーを呼ぶ箇所が無い。
- 利用者または開発への影響: 実害はない。ただし(1)は大規模かつ開発中のコンポーネントファイル内にあり、周辺の型が生きているため、フォーカス/ズーム関連の未完成機能の一部である可能性がある。(2)はbackend routeが現に存在するため、削除するとフロントエンドからそのAPIを呼ぶ手段が失われる。
- 判断結果: (1) 現行CanvasShellは`focusWorldPoint`または`focusCardId`を受けて実際のfocus effect内で座標を処理しており、旧helperはこの経路へ接続されていない。(2) UIはproposal-onlyの`proposeIslandSummary`と`POST /ai/proposals/island-summary`を使用する。backendの旧route関数はproposal endpoint内部から再利用されているため維持するが、直接呼出し用frontend wrapperは置換済みである。

## 対応方針

- 実施したこと: 未参照の`getFocusWorldPointForReference`、`suggestIslandSummary`、後者専用の`SuggestIslandSummaryResult`を削除した。
- 実施しないこと: 実動中のfocus effect、proposal-only UI/API、backendの`/ai/suggest-island-summary`関数とrouteの変更。

## 受入条件

- [x] 2つのfrontend helperを置換済み残骸として削除し、backendの内部再利用routeは維持すると決定する。

## 検証計画

- 実行する確認: 削除する場合、`npm run typecheck`（frontend）。`suggestIslandSummary`を削除する場合は対応するbackend routeの扱いも合わせて確認する。
- 期待結果: 既存のビルドに影響がないことを確認する。

## Validation

- `node node_modules/vitest/vitest.mjs run src/api/client.test.ts src/ui/ux_operability_regression.test.ts`
- `node node_modules/typescript/bin/tsc --noEmit`
- `python 01_Plans/docs_check.py --root .`

## 補足

- 発見経緯: 第8ラウンドの棚卸し（未使用export観点）で発見。
