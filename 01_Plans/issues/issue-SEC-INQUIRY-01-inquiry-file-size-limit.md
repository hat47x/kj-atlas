# Issue: SEC-INQUIRY-01 探究ファイル取込に実測由来の容量上限を設ける

- Type: Security / Performance / UX
- Status: Done
- Completion: 2026-07-18; 6・12・18ラウンドの実測から5MiB警告・20MiB拒否境界を固定し、UI preflight、domain parser、exportへ対称に適用した。
- Source Issue: N/A
- Priority: P1
- Owner: Codex / Maintainer
- Scope: `03_Implement/frontend/src/domain/inquiry_bundle_io.ts`, `03_Implement/frontend/src/worker/inquiry_bundle_client.ts`, `03_Implement/frontend/src/ui/InquiryJourneyPrototypePanel.tsx`
- Related Backlog: `DOMAIN-W-ITERATION-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`, `02_Architecture/inquiry_journey_model.md`, `01_Plans/issues/issue-PERF-INQUIRY-01-representative-inquiry-import-non-blocking.md`
- Expected verification level: `e2e`

## 1) 課題

探究ファイルのstrict validationとdigest照合はworkerへ移したが、画面は容量を確認せずに`File.text()`で全体をメモリへ読み込み、JSON文字列をworkerへ渡す。極端に大きいファイルでは、検証開始前にブラウザのメモリを圧迫し、応答停止またはタブ終了を招く可能性がある。形式が不正でも同じ負荷が発生するため、fail-closed検証だけでは入力資源の境界を守れない。

代表規模の自己完結bundleは1,460,390 bytesだった。上限はこの単一実測値をそのまま採用せず、複数反復、分岐、カード本文長、将来の共有bundleを含むfixtureを比較して決める。

## 2) 対応方針

- `File.size`を`File.text()`より前に確認し、上限超過時は内容を読み込まず理由と次の行動を表示する。
- domain parserを文字列から直接呼ぶ経路にもUTF-8 byte上限を設け、UIだけに依存しない。
- 代表規模、2倍規模、分岐を含む規模を実測し、警告閾値と拒否上限を分ける必要があるか判断する。
- ZIP取込の既存2MiB text上限を機械的に流用しない。現行代表bundleが約1.46MBであり、通常の成長余地を狭めるためである。
- 上限値を環境変数で調整可能にする場合、その名前は例外なく`KJ_ATLAS_`で始め、環境変数一覧へ追加する。

## 3) 受入条件

- [x] 代表規模と成長ケースの実測根拠から警告・拒否境界を決める。
- [x] 上限超過ファイルを`File.text()`より前に拒否し、画面が操作可能なままになる。
- [x] `parseInquiryBundleJson()`の直接利用でもUTF-8 byte上限を超える入力を拒否する。
- [x] 境界直下、境界一致、境界超過、マルチバイト文字をunit testで検証する。
- [x] 代表規模の保存・再開、worker中止、100ms設計目標を退行させない。
- [x] 利用者向けメッセージは、技術的なbyte値だけでなく、ファイルを分けるなどの次の行動を示す。

## 4) ADR判断

入力資源制限は既存の安全境界を具体化する実装課題であり、現時点では新規ADRを起票しない。外部bundle形式、保持方針、または環境ごとの互換性を変える場合だけADR要否を再評価する。

## 5) 検証計画

- `node node_modules/typescript/bin/tsc --noEmit`
- `node node_modules/vitest/vitest.mjs run src/domain/inquiry_bundle_io.test.ts src/worker/inquiry_bundle_client.test.ts`
- `node node_modules/@playwright/test/cli.js test e2e/inquiry_bundle_capacity_budget.spec.ts`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## 6) 完了記録（2026-07-18）

- 同じ300カード・30島のfixtureで、6ラウンドは1,460,390 bytes、12ラウンドは2,785,220 bytes、18ラウンドは4,110,050 bytesだった。
- 18ラウンドまで通常扱いできる余地を保ち、5MiB超を警告境界とした。警告時も読込を禁止せず、通常より時間がかかる可能性を伝える。
- 拒否上限は20MiBとした。現行6ラウンド代表値の約13.7倍であり、長期探究の成長余地を確保しつつ、異常入力による無制限のメモリ消費を防ぐ。
- UIは`File.size`を`File.text()`より前に確認する。上限超過時は内容を読み込まず、より小さいファイルを選ぶか過去ラウンドを分けて保存する次の行動を示す。
- `parseInquiryBundleJson()`はUTF-8 byte数で同じ20MiB上限を適用する。ASCIIの上限一致・超過と日本語マルチバイト超過をunit testで固定した。
- exportにも20MiB上限を適用し、「保存できるが再取込できない」成果物を生成しない。保存時も専用の次行動メッセージを表示する。
- 5MiB・20MiBは外部環境で調整する値ではなく、現行bundle契約の実測由来定数とした。新しい環境変数は追加していない。
- 入力ファイル上限は保持期間・保持件数の上限を決めるものではない。保持・削除方針は`DOMAIN-W-ITERATION-01`の未完了範囲として引き続き扱う。
