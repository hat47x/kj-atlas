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


## 配置の整理（2026-09-05）

- 本Issueは、利用者が実画面で状態を正しく把握・操作できるためのUI operability不具合を修正し、実ブラウザを含む確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 既存のライフサイクル契約に従い、本変更では独立したUI operabilityの完了済みIssue 2件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を44から42へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
