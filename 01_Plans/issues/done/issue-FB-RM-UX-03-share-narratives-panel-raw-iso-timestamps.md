# Issue: FB-RM-UX-03 SharePanel/NarrativesPanelがcreatedAtをlocale整形せず生ISO文字列で表示

- Type: Bug
- Status: Done
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

- [x] `formatTimestamp`が共有moduleからexportされ、`SidePanel.tsx`の既存5箇所が引き続き同じ表示になる。
- [x] `SharePanel.tsx`のPatch Apply Logタイムスタンプがlocaleに応じて整形表示される。
- [x] `NarrativesPanel.tsx`のnarrative作成日時とconsistency checkタイムスタンプがlocaleに応じて整形表示される。
- [x] 既存のi18n/a11y回帰テストが壊れない。

## 検証計画

- 実行する確認: `npx tsc --noEmit`、`vitest run src/ui/SharePanel.test.ts src/ui/NarrativesPanel.test.ts src/ui/SidePanel.test.ts`（存在するファイル名は実装時に確認）、`vitest run src/i18n`。
- 期待結果: 型検査・既存テストが通り、3ファイルのcreatedAt表示が同一のlocale整形ロジックを共有する。

## 補足

- 発見経緯: 第16ラウンドの「frontend日付/数値表示の不整合」観点監査で発見。探索結果は一度、探索agentが未pushのローカルHEAD（origin/mainより1 commit古い）から行番号を引用しており、verify agentがorigin/mainとの差分（`SidePanel.tsx`のformatTimestamp定義は505-512、not 503-509等）を検出して修正済み。本Issueの行番号はすべてorigin/main（かつ本ラウンドのi18nキー削除後の`en.json`行番号）に対して再検証済み。
- `MergeSuggestionsPanel.tsx:257,368`のlocale未指定`toLocaleString()`は関連するが別種の不整合として次点の監査候補に残す。

## 実装記録（2026-08-06）

- 「判断が必要な理由」で保留していた唯一の論点（切り出し先のモジュール名・配置）を、既存の`domain/`直下フラット配置＋同名`.test.ts`併置という規約（`ai_provider_error.ts`+`.test.ts`等、多数の先例）に従って`domain/format_timestamp.ts`として決定した。ADRや契約変更を伴わない、可逆的な命名判断のため単独で実施した。
- `SidePanel.tsx`: ローカル`formatTimestamp`を削除し、`domain/format_timestamp`からimport（既存5箇所は呼び出し変更なし）。使用箇所が無くなった`getActiveLocale`のimportも削除。
- `SharePanel.tsx`: importを追加し、Patch Apply Logの`<summary>`表示を`{entry.createdAt}` → `{formatTimestamp(entry.createdAt)}`に変更。
- `NarrativesPanel.tsx`: importを追加し、2箇所を変更。
  - narrative作成日時: `entry.createdAt`は`optional`（`?? t("narratives.panel.generated_at_export_time")`という別文字列へのfallbackを持つ）ため、`entry.createdAt ? formatTimestamp(entry.createdAt) : t(...)`という条件分岐にした（fallback文字列自体をformatTimestampに渡す誤りを避けるため）。
  - consistency checkタイムスタンプ: `check.createdAt`は`NarrativeCheck`型で必須`string`のため、単純に`formatTimestamp(check.createdAt)`でラップした。
- 新規テスト`domain/format_timestamp.test.ts`（3件）: 整形後の値が入力と異なること、ja/en間で出力が異なること（locale依存性の確認）、不正な日付文字列は元の文字列をそのまま返すこと（fallback分岐）を検証。ブラウザ/Node ICU実装差に脆弱な厳密文字列一致は避けた。

検証結果:
- `npx tsc --noEmit`: エラー無し。
- 対象テスト: `format_timestamp.test.ts`（3件）・`SharePanel.test.ts`（15件）・`NarrativesPanel.accessibility.test.ts`（3件）全てpass。`SidePanel.tsx`には既存の専用テストファイルが無い（新設もしていない。本Issueのスコープは既存関数の切り出しのみ）。
- frontend全体: 233ファイル中231ファイルpass（1383/1384テストpass）。失敗した2ファイルは`external_agent_workflow_doc.test.ts`と`representative_visual_cue_prototype.test.ts`で、いずれも本変更と無関係な既知の環境依存gap（WSL nativeテスト用ディレクトリがリポジトリ全体の構造を持たないための相対パス解決失敗。`DX-CI-TEST-01`として既に別issueで追跡済み）。
- `npm run build`: 成功（既存のchunk-size警告のみ、新規警告無し）。
- 実ブラウザでの目視確認は未実施。変更が小さく（既存の純関数の切り出しと3箇所の呼び出し更新のみ）、型検査・単体テスト・本番buildの組み合わせで十分な確証が得られると判断したため。
