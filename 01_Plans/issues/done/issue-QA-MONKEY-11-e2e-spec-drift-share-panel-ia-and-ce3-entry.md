# Issue Draft: QA-MONKEY-11 UI再編に追随できていないe2e specが2本 main 上で失敗している

- Type: Bug (test drift)
- Status: Done
- Source Issue: `QA-MONKEY-10`（修正検証中の発見）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/e2e/realistic_user_journey_expansion.spec.ts`, `03_Implement/frontend/e2e/ce3_patch_workspace.spec.ts`
- Related Backlog: `QA-MONKEY-11`
- Related ADR/Spec: `01_Plans/issues/done/issue-PRODUCT-UX-02-workspace-information-architecture.md`（推定ドリフト元）
- Expected verification level: `e2e`

## 背景

QA-MONKEY-10（ラベルカリング）の修正を検証する過程で、**main 上ですでに失敗している e2e spec** を発見した。
当初は語彙同期による文言ドリフト（status文言 `Replaced the current document` /
`現在のドキュメントを置換しました` への変更に7本のspecが未追随）も含め9本が影響を受けていたが、
文言ドリフト分7本は共有ヘルパー定数 `DOCUMENT_REPLACED_STATUS`（`e2e/helpers/i18n.ts`）の導入と
各specの置き換えで同修正内で解消済み。**残る2本はUI構造の再編に起因し、別途の追随修正が必要**なため本Issueで起票する。

## 失敗の詳細（いずれも main / バックエンド有無に関わらず再現）

### 1. `realistic_user_journey_expansion.spec.ts`（S1-S3 現実的ジャーニー）

- 失敗点: `visibilitySelect(page, "view")` → `label:has-text(/View visibility|view の公開範囲/) select` が 30s タイムアウト（spec:72）。
- 推定原因: 共有パネルが「目的を選ぶ」2段階IA（`共有用に書き出す` / `取り込む・復元する`）に再編され、
  公開範囲セレクトが目的選択後にしか表示されなくなった。specは目的選択を経ずに直接セレクトを探している。
- i18n文字列自体（`share.panel.visibility.view`）は現存するため、文言でなくフローの drift。

### 2. `ce3_patch_workspace.spec.ts`（CE3 patch workspace）

- 失敗点: `getByRole("button", { name: /Collect candidates|候補を収集/i })` が 30s タイムアウト（spec:72）。
- 推定原因: 候補収集ボタン（`merge_suggestions.collect_candidates`、i18nキーは現存）の配置が
  ワークスペースIA再編（Advanced UI ゲートまたはメニュー化）で移動し、文書置換直後のトップレベルには露出していない。
- 注意: このspecは `npm run e2e:mock` および `e2e:regression-harness` の既定パターン
  （`ce3_patch_workspace|auth_context_level1_smoke|i18n_locale_query_equivalence`）に含まれる。
  つまり**公式の回帰ハーネスが main 上で赤**になっており、他の変更の検証を静かに阻害する。P2 とした根拠。

## なぜ問題か

- 回帰ハーネスが赤のままだと「テストが落ちるのはいつものこと」という常態化を招き、
  本物の回帰（今回の QA-MONKEY-10 検証で実際に切り分けコストが発生した）の検出が遅れる。
- UI再編（共有パネルの目的ステップ、ワークスペースIA）自体は意図した設計変更であり、
  アプリ側でなく **spec 側をフローに追随させる**のが正しい修正方向。

## 受け入れ条件（案）

- [x] AC-1: `realistic_user_journey_expansion.spec.ts` が現在の共有パネルIA（目的選択ステップ経由）で完走する。
- [x] AC-2: `ce3_patch_workspace.spec.ts` が現在のワークスペースIAで「候補を収集」に到達し完走する。
- [x] AC-3: `npm run e2e:mock` が main 上で green になる。
- [x] AC-4: 今回修理したspec（本Issueの2本＋文言ドリフト7本）はUI文言・フローを `e2e/helpers/i18n.ts` の共有定数・ヘルパー経由で参照する（スイート全体への直書き禁止の徹底は継続的な規律として本Issueのスコープ外）。

## Traceability

- Derived-from: `01_Plans/issues/done/issue-QA-MONKEY-10-cascade-label-culling-hides-fresh-card-text.md`（修正検証中の発見）
- Related: `03_Implement/frontend/e2e/helpers/i18n.ts`（`DOCUMENT_REPLACED_STATUS` 追加済み）
- Related: `01_Plans/issues/done/issue-PRODUCT-UX-02-workspace-information-architecture.md`

## 対応記録（2026-07-10）

- 実際のドリフト内容は起票時の推定より深く、IA変更＋文言変更の複合だった:
  1. **公開範囲セレクトは「目的ステップの奥」ではなく Advanced UI ゲートの中**（`SharePanel.tsx` の
     `isAdvancedUiEnabled` 分岐）。目的ボタン自体は scrollIntoView のみでセクションを隠さない。
  2. **「候補を収集」は作業モードパネル（`WorkModePanel`）内の `advancedWorkModeContent`** に移動しており、
     Advanced UI 有効時のみ描画される。
  3. ce3 spec はさらに3箇所の文言/表現ドリフトを抱えていた: diff プレビュー見出し
     （→ `Review changes`/`変更内容の確認`）、トークン差分（→ `Word changes:`/`語句の変更量:`）、
     正規化クエリの表示（生JSON → `executed_query_summary` の可読サマリ。アサーションは同じ不変条件
     scope=selection / depth=2 / filters ソート済み を可読表示に対して検証する形に変更）。
- `e2e/helpers/i18n.ts` に `WORK_MODE_BUTTON` / `enableAdvancedUiIfNeeded`（aria-pressed で冪等）/
  `openAdvancedWorkMode`（共有パネルを閉じ→Advanced有効化→作業モードを開く）を追加し、両specを修理。
  realistic_user_journey の readOnly 後半にあった Advanced ボタンの素朴なクリックも、
  localStorage 永続化により**トグルOFFになる潜在バグ**だったため冪等ヘルパーへ置換。
- 検証: 対象2spec＋`e2e:mock` 相当（ce3 / auth_context_level1_smoke / i18n_locale_query_equivalence）
  計6テスト green（Docker Playwright v1.58.2）。
