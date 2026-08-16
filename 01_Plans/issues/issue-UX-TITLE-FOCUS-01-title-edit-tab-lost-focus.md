# Issue: UX-TITLE-FOCUS-01 タイトル編集欄のTab操作でフォーカスが消失する

- Type: Accessibility / UX
- Status: Done
- Source Issue: Edgeランダム操作モンキーテスト（2026-08-16）
- Priority: P1
- Owner: Maintainer
- Scope: frontend `DocumentTitleEditor`, i18n, keyboard E2E
- Related ADR/Spec: `WCAG 2.4.3 Focus Order`, `UX-KEYBOARD-01`
- Expected verification level: `e2e`

## 課題

文書タイトルを編集状態にして入力欄からTabを押すと、inputの`onBlur`が即座に保存して入力欄と隣接する保存ボタンをunmountするため、ブラウザのフォーカスが`body`へ落ちた。またinputにlabel、`aria-label`、placeholderのいずれもなく、スクリーンリーダー上で名前のない入力欄だった。

## 対応

- タイトルinputへlocale対応の`aria-label`を付与する。
- blur保存をinput単体ではなく編集領域のfocus境界で判定し、inputから保存ボタンへのTab移動では編集UIを維持する。
- 保存ボタンで確定した後はタイトル表示ボタンへフォーカスを戻す。
- Enter/Escapeの既存フォーカス復帰を維持する。

## 受入条件

- [x] タイトル入力欄にaccessible nameがある。
- [x] inputからTabで保存ボタンへ移動しても`body`へフォーカスが落ちない。
- [x] 保存ボタン、Enter、Escape後に操作可能な要素へフォーカスがある。
- [x] Edgeモンキーテストで無名inputと当該focus消失が再現しない。
