# Issue: PERF-INQUIRY-01 代表規模の探究ファイル読込を非ブロッキング化する

- Type: Quality / Performance / UX
- Status: Done
- Completion: 2026-07-18; strict validationとdigest照合をmodule workerへ移し、代表規模のUI読込を単独実行の最大長時間タスク93から95ms、完了1.18から1.45秒で検証した。
- Source Issue: N/A
- Priority: P1
- Owner: Codex / Maintainer
- Scope: `03_Implement/frontend/src/domain/inquiry_bundle_io.ts`, `03_Implement/frontend/src/worker/inquiry_bundle*`, `03_Implement/frontend/src/ui/InquiryJourneyPrototypePanel.tsx`, `03_Implement/frontend/e2e/inquiry_bundle_capacity_budget.spec.ts`
- Related Backlog: `DOMAIN-W-ITERATION-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`, `02_Architecture/design/inquiry_journey_model.html`
- Expected verification level: `e2e`

## 1) 課題

代表規模（1スナップショット当たり300カード・30島、6ラウンド）の自己完結探究ファイルを画面から読み込むと、厳格な形状検証、参照検証、7スナップショットのSHA-256照合、React状態反映が同じ操作に集中する。2026-07-18のChromium実測では、読込完了まで約1.03秒、最大長時間タスクは243msだった。再実行前にも294msを観測しており、`ADR-0046` PB-3の「単一の同期処理は目安100ms以下」を満たさない。

ファイルは正しく読み込めるが、利用者が操作不能に感じ、思考の連続性を損なう可能性がある。Phase 3のbackend永続化へ進む前に、ローカル集約形式の処理境界を非ブロッキングにする必要がある。

## 2) 実測根拠

- 計測日・環境: 2026-07-18、Codex Windowsホスト、Playwright Chromium、1440 x 900。
- 代表規模: 300カード、30島、299関係、起点を含む7スナップショット、6ラウンド、1,800カード系譜。
- 1成果: 73,955 bytes、探究manifest: 2,161 bytes、自己完結bundle: 1,460,390 bytes。bundleは5MiBの回帰上限以内であり、現時点で圧縮や差分形式を必須とする容量ではない。
- Node側の書き出し: 101.55から143.59ms、厳格読込: 71.13から120.38ms（単一・並列実行の参考値でありSLAではない）。
- UI読込: 1,033.26から1,246.09ms、最大長時間タスク: 243から273ms。これ以前の実行では最大294msを観測した。
- 実装前は500msを暫定回帰上限としていた。実装後は暫定値を削除し、100ms基準を直接検証する。

## 3) 対応方針

- 形状検証・参照検証・digest照合の処理内訳を計測し、workerへ移す処理とメインスレッドに残す処理を分ける。
- 読込中であることを状態表示し、二重操作を防ぐ。処理が長引く場合は中止できる境界を設ける。
- worker化後も、未知キー、未知version、参照切れ、digest不一致を拒否する現在のfail-closed契約を維持する。
- 代表規模未満の通常利用でworker起動コストが支配的にならないよう、常時worker化と容量閾値による切替を比較する。
- 外部bundle形式と`ADR-0057`の不変スナップショット方針は変更しない。既存ADRで処理の非ブロッキング化基準が確定しているため、本issueでは新規ADRを起票しない。

## 4) 受入条件

- [x] 代表規模の画面読込で、単独実行の最大長時間タスクが100ms以下になる。
- [x] 代表規模の読込完了が2.5秒以内で、処理中であることを知覚できる。
- [x] 読込中の二重実行を防ぎ、長引く処理を安全に中止できる。
- [x] strict validationとdigest照合の既存unit testが全て通る。
- [x] 300カード・30島・6ラウンドのPlaywright E2Eが、単独実行の100ms目標と並列CIの150ms退行上限を検証する。
- [x] 通常規模の開始、ラウンド記録、保存、再開、キーボード操作、390px表示を退行させない。

## 5) 検証計画

- `node node_modules/typescript/bin/tsc --noEmit`
- `node node_modules/vitest/vitest.mjs run src/domain/inquiry_bundle_io.test.ts src/domain/inquiry_journey_session.test.ts`
- `node node_modules/@playwright/test/cli.js test e2e/inquiry_bundle_capacity_budget.spec.ts e2e/complexity_budget_foregrounding.spec.ts`
- 実装前後の計測値をissueへ追記し、100ms以下になった時点で暫定500ms上限を削除する。

## 6) リスクとロールバック

- workerとの受け渡しで大きなbundleを複製すると、メモリ使用量と転送時間が増える。structured cloneの実測を含めて方式を選ぶ。
- 中止時に部分的なbundleを画面状態へ反映しない。検証完了後に一度だけ状態を置き換える。
- 非ブロッキング化がstrict validationを弱める場合は採用せず、現行同期処理と待機表示へ戻す。

## 7) 完了記録（2026-07-18）

- `InquiryBundleWorkerClient`とversion付きprotocolを追加し、JSON形状、自己完結参照、7スナップショットのdigest照合をmodule workerで実行する。
- workerは大きなbundleオブジェクトを返さず、合否と小さなエラーだけを返す。成功時は検証に使った同一JSON文字列をメイン側で一度だけ復元し、structured cloneによる長時間タスクを避ける。
- workerを利用できない環境では既存`parseInquiryBundleJson()`へfail-closedでフォールバックする。未知キー、未知version、参照切れ、digest不一致の拒否契約は変更していない。
- 画面には読込中表示と中止ボタンを追加した。中止時はworkerを終了し、遅延結果を画面状態へ反映しない。文書切替・unmount時も同じ中止境界を使う。
- ローカルファイルパスを使うPlaywright単独実測で、UI読込は1.18から1.45秒、worker検証開始後の最大長時間タスクは93から95msだった。別specとの並列実行では125msを観測したため、100msを設計目標として維持しつつ、CIはスケジューリング変動を含む150msを退行上限とする。DevTools経由の大容量Buffer注入時間はアプリ処理と分離した。
