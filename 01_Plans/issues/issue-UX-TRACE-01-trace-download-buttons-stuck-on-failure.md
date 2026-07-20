# Issue: UX-TRACE-01 トレースダウンロード失敗時にボタンが恒久的に無効化される

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Done
- Lifecycle: Done
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

- 実施したこと: `computeTrace()`を共通`runTraceRequest`境界の`try/catch/finally`へ通し、成功・中止・rejectの全経路で現在のcontrollerに対応するrunning／progress状態を解除する。reject時は生の例外を表示せず、既存の`onEvidenceTraceError`境界へローカライズ済みの再試行案内を渡す。新しい計算開始時は旧controllerをabortする。
- 実施しないこと: worker例外の本文・stack・内部状態をUIへ表示しない。自動再試行や結果の自動downloadは行わず、利用者が再度操作する既存境界を維持する。

## 受入条件

- [x] 失敗時は値非反射のエラーを表示し、running／progressを解除して手動再試行を許可する。
- [x] 共通境界の`finally`から`setIsTraceRunning(false)`へ戻り、ダウンロード／コピー／再試行ボタンの無効化条件が解除されることをreject単体テストと配線回帰テストで固定した。

## 検証計画

- 実行結果: SidePanel／i18n近接38件、frontend全体1,267件・219 file、frontend typecheck、docs-check、active issue validatorを実行して成功した。
- 期待結果: `computeTrace()`がrejectしても例外値を表示せず、ダウンロード／コピー／再試行ボタンが再度操作可能になる。

## 補足

- 発見経緯: 第10ラウンドの棚卸し（未処理Promise rejection観点）で発見。同観点で見つかったもう1件（`App.tsx`の`handleAdoptIslandSummaryProposal`まわりの同種の問題）は、探索エージェントが誤ってローカルの未pushコミット（`origin/main`にまだ反映されていない別セッションの作業）を参照しており、`origin/main`上の正確な行番号を検証フェーズで再導出できなかったため、本ラウンドでは起票を見送った。
- 完了判断: 未処理Promise rejectionを関数内部で吸収し、cleanupを`finally`へ集約した。download handlerだけでなく同じ計算関数を使うcopy handlerも同時に復旧するため、受入条件を満たしてDoneとする。
