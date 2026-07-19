# Issue: DX-CLEANUP-04 CanvasShell.tsxとclient.tsに未参照ヘルパーが残存

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
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

## 対応方針

- 実施すること:
  1. `getFocusWorldPointForReference`について、進行中の機能（フォーカス/ズーム関連）の一部として近く呼び出し元が追加される予定か、削除してよい残骸かをMaintainerが判断する。
  2. `suggestIslandSummary`について、backend routeの`/ai/suggest-island-summary`が今後もAPIとして維持されるか（維持されるならフロントのラッパーも残す）、廃止予定か（廃止ならフロント/backend両方を削除する）を判断する。
- 実施しないこと: 両ヘルパーの削除。特に(2)はbackend側の生存中のroute契約に関わるため、フロント単体の判断で削除しない。

## 受入条件

- [ ] 2つのヘルパーそれぞれについて、維持/削除の方針が決定される。

## 検証計画

- 実行する確認: 削除する場合、`npm run typecheck`（frontend）。`suggestIslandSummary`を削除する場合は対応するbackend routeの扱いも合わせて確認する。
- 期待結果: 既存のビルドに影響がないことを確認する。

## 補足

- 発見経緯: 第8ラウンドの棚卸し（未使用export観点）で発見。
