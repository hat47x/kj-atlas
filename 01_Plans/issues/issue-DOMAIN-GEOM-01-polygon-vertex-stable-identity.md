# Issue: DOMAIN-GEOM-01 島の頂点編集リストがインデックスキーで安定IDを持たない

- Type: Feature
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/canvas/PolygonEditLayer.tsx`, `03_Implement/frontend/src/domain/types.ts`, `03_Implement/frontend/src/domain/geometry/polygon_edit.ts`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `PolygonEditLayer.tsx:158`の頂点ハンドル一覧は`points.map((point, index) => ...)`で`key={index}`を使う。`Point`型（`domain/types.ts:103-106`）は`{ x: number; y: number }`のみで、安定したid相当のフィールドが存在しない。頂点削除（Alt+click）は`domain/geometry/polygon_edit.ts:83`の`points.map(roundPoint).filter((_, index) => index !== vertexIndex)`で配列途中から要素を除去するため、削除された頂点より後ろの全頂点のインデックスがシフトする。
- 利用者または開発への影響: 現状、各ハンドルの状態（ドラッグ中かどうか）は親コンポーネント（`PolygonEditLayer`）がindex経由で管理しており、ハンドル自身が保持するReact状態は無い。そのため、現時点での実害はDOMノードの再マウント（focus等の一時的な喪失）に留まり、状態の取り違えには至っていない。ただし、将来ハンドル自体がローカル状態を持つようになった場合、インデックスキーの不安定性が状態の取り違えという実害に発展するリスクがある。

## 対応方針

- 実施すること: `Point`型に合成的な安定id（例: UUID）を追加するかどうかをMaintainerが判断する。座標のみのシンプルな型に付加情報を持たせることの是非、既存のdocument/viewスキーマへの影響を検討する必要がある。
- 実施しないこと: `Point`型へのid追加。データモデルの変更判断が必要で、機械的には対応しない。

## 受入条件

- [ ] `Point`型へのid付加の要否が決定される。
- [ ] 付加する場合、既存のdocument.jsonスキーマとの互換性を確認する。

## 検証計画

- 実行する確認: 対応する場合、`npm run test`（frontend、polygon編集関連）。
- 期待結果: 頂点の追加・削除・ドラッグが従来通り機能する。

## 補足

- 発見経緯: 第12ラウンドの棚卸し（React key prop安定性観点）で発見。同じ観点で見つかった読み順リストの`SidePanel.tsx:2324`（`key={`${item.id}_${index}`}`）は、既に存在する`item.id`を使うだけの機械的な修正だったため、本ラウンドで直接対応済み（`key={item.id}`に変更）。
