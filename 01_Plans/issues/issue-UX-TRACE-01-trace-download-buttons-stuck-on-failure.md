# Issue: UX-TRACE-01 トレースダウンロード失敗時にボタンが恒久的に無効化される

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/SidePanel.tsx`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `SidePanel.tsx`の`handleDownloadContradictionTrace`（L770）と`handleDownloadEvidenceTrace`（L792）は、`void computeTraceMarkdown(...).then(...)`という形でfire-and-forgetで呼び出されており、`.catch`が無い。`computeTraceMarkdown`（L710-755）は`setIsTraceRunning(true)`をL720で呼ぶが、これを`false`に戻す処理はL741（`await traceClientRef.current.computeTrace(...)`が成功した後）にしか無い。つまり`computeTrace()`がreject（例: ワーカーのクラッシュ、ネットワーク的な問題等）すると、`isTraceRunning`が`true`のまま戻らず、両方のダウンロードボタンと、同じ無効化条件を共有するコピー系ボタン（`SidePanel.tsx:3910/3913/3943/3946`）が恒久的に無効化されたままになる。
- 利用者または開発への影響: 一度トレース計算が失敗すると、ページをリロードするまでトレース関連のダウンロード/コピー機能がすべて使えなくなる。

## 対応方針

- 実施すること: `computeTrace()`が失敗した場合の復旧方法（`isTraceRunning`を`false`に戻してエラーメッセージを表示する、リトライを許可する等）をMaintainerが決定する。
- 実施しないこと: 復旧UXの実装そのもの。単に`finally`で`isTraceRunning`を戻すだけで十分か、エラー内容をユーザーに提示すべきかはUX判断が必要。

## 受入条件

- [ ] トレース計算失敗時の復旧UXが決定される。
- [ ] 実装後、失敗時にボタンが再度有効化されることを確認する。

## 検証計画

- 実行する確認: 実装後、`SidePanel`関連のunit test。
- 期待結果: `computeTrace()`が失敗してもダウンロード/コピーボタンが再度操作可能になる。

## 補足

- 発見経緯: 第10ラウンドの棚卸し（未処理Promise rejection観点）で発見。同観点で見つかったもう1件（`App.tsx`の`handleAdoptIslandSummaryProposal`まわりの同種の問題）は、探索エージェントが誤ってローカルの未pushコミット（`origin/main`にまだ反映されていない別セッションの作業）を参照しており、`origin/main`上の正確な行番号を検証フェーズで再導出できなかったため、本ラウンドでは起票を見送った。
