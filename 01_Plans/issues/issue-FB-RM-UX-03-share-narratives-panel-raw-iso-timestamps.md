# Issue: FB-RM-UX-03 SharePanel/NarrativesPanelがcreatedAtをlocale整形せず生ISO文字列で表示

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/ui/NarrativesPanel.tsx`, `03_Implement/frontend/src/ui/SidePanel.tsx`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `SidePanel.tsx:505-512`はlocale対応の`formatTimestamp`ヘルパー（`getActiveLocale()`に応じて`ja-JP`/`en-US`で`toLocaleString`する）を定義し、Merge History（`entry.createdAt`, `SidePanel.tsx:1532`）、Island Summary History（`entry.createdAt`, `SidePanel.tsx:2709`）、Relation Summary History（`entry.createdAt`, `SidePanel.tsx:3322`）、Document作成/更新日時（`SidePanel.tsx:3571,3577`）の4箇所で一貫して使っている。しかし同じ形の`createdAt: string`（ISO-8601、`new Date().toISOString()`起源）を表示する他2箇所はこのヘルパーを使わず、生のISO文字列をそのままユーザーに表示している。
  - `SharePanel.tsx:1336`: Patch Apply Logの各エントリで`{entry.createdAt}`をそのまま`<summary>`に表示（例: `2026-07-20T09:14:03.512Z · My patch`）。
  - `NarrativesPanel.tsx:250`: narrative draftの`{t("narratives.panel.created_at", { value: entry.createdAt ... })}`が生のISO文字列を`{value}`にそのまま埋め込む（`i18n/locales/en.json:843`の文字列自体はformattingしない）。
  - `NarrativesPanel.tsx:319`: consistency checkの`{t("narratives.panel.check_summary", { createdAt: check.createdAt, ... })}`も同様に生のISO文字列（`i18n/locales/en.json:853`）。
- 利用者または開発への影響: SidePanelの各種履歴一覧はlocaleに応じた読みやすい日時表示になっている一方、Share panelのPatch Apply LogとNarratives panelのnarrative/checkタイムスタンプだけが開発者向けのISO文字列のまま一般利用者に見えており、同一アプリ内で表示形式が不統一。
- 判断が必要な理由: `formatTimestamp`は`SidePanel.tsx`内の非export local constであり、`SharePanel.tsx`/`NarrativesPanel.tsx`に単純import追加するだけでは直せない。共有utilへ切り出す小さなリファクタ（exportして両ファイルからimportする）が必要で、切り出し先のモジュール名・配置（例: 新規`domain/format_timestamp.ts`か`i18n`配下か）はMaintainerの設計判断に委ねる。

## 対応方針

- 実施すること: `SidePanel.tsx`の`formatTimestamp`を共有moduleへ切り出してexportし、`SharePanel.tsx:1336`と`NarrativesPanel.tsx:250,319`をそのformatted値を使うよう変更する。`SidePanel.tsx`側の5箇所の呼び出しはimport元を変えるだけで動作を変えない。
- 実施しないこと: `MergeSuggestionsPanel.tsx:257,368`（`new Date(x).toLocaleString()`をlocale指定なしで呼んでいる、browser既定localeに依存する別種の不整合）への対応。本Issueのスコープは「生ISO文字列 vs 整形済み」の対比であり、「整形済みだがlocale未指定」は別種の問題のため対象外。

## 受入条件

- [ ] `formatTimestamp`が共有moduleからexportされ、`SidePanel.tsx`の既存5箇所が引き続き同じ表示になる。
- [ ] `SharePanel.tsx`のPatch Apply Logタイムスタンプがlocaleに応じて整形表示される。
- [ ] `NarrativesPanel.tsx`のnarrative作成日時とconsistency checkタイムスタンプがlocaleに応じて整形表示される。
- [ ] 既存のi18n/a11y回帰テストが壊れない。

## 検証計画

- 実行する確認: `npx tsc --noEmit`、`vitest run src/ui/SharePanel.test.ts src/ui/NarrativesPanel.test.ts src/ui/SidePanel.test.ts`（存在するファイル名は実装時に確認）、`vitest run src/i18n`。
- 期待結果: 型検査・既存テストが通り、3ファイルのcreatedAt表示が同一のlocale整形ロジックを共有する。

## 補足

- 発見経緯: 第16ラウンドの「frontend日付/数値表示の不整合」観点監査で発見。探索結果は一度、探索agentが未pushのローカルHEAD（origin/mainより1 commit古い）から行番号を引用しており、verify agentがorigin/mainとの差分（`SidePanel.tsx`のformatTimestamp定義は505-512、not 503-509等）を検出して修正済み。本Issueの行番号はすべてorigin/main（かつ本ラウンドのi18nキー削除後の`en.json`行番号）に対して再検証済み。
- `MergeSuggestionsPanel.tsx:257,368`のlocale未指定`toLocaleString()`は関連するが別種の不整合として次点の監査候補に残す。
