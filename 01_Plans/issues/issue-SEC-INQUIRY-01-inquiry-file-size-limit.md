# Issue: SEC-INQUIRY-01 探究ファイル取込に実測由来の容量上限を設ける

- Type: Security / Performance / UX
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
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

- [ ] 代表規模と成長ケースの実測根拠から警告・拒否境界を決める。
- [ ] 上限超過ファイルを`File.text()`より前に拒否し、画面が操作可能なままになる。
- [ ] `parseInquiryBundleJson()`の直接利用でもUTF-8 byte上限を超える入力を拒否する。
- [ ] 境界直下、境界一致、境界超過、マルチバイト文字をunit testで検証する。
- [ ] 代表規模の保存・再開、worker中止、100ms設計目標を退行させない。
- [ ] 利用者向けメッセージは、技術的なbyte値だけでなく、ファイルを分けるなどの次の行動を示す。

## 4) ADR判断

入力資源制限は既存の安全境界を具体化する実装課題であり、現時点では新規ADRを起票しない。外部bundle形式、保持方針、または環境ごとの互換性を変える場合だけADR要否を再評価する。

## 5) 検証計画

- `node node_modules/typescript/bin/tsc --noEmit`
- `node node_modules/vitest/vitest.mjs run src/domain/inquiry_bundle_io.test.ts src/worker/inquiry_bundle_client.test.ts`
- `node node_modules/@playwright/test/cli.js test e2e/inquiry_bundle_capacity_budget.spec.ts`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
