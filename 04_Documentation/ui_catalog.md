# 現行UIカタログ / Current UI Catalog

対象読者: kj-atlas の画面構成を一覧で把握したい利用者・運用者・評価担当者、および UI/UX の見直し（再設計）を検討する担当者。

目的:

1. **利用者向け**: 現在の画面に「どのUI要素があり、何のためにあるか」を、現行スクリーンショット付きで一望できるようにする。操作手順は [受け入れ確認](acceptance_check.md) を参照。
2. **設計見直し向け**: 外部のデザイン支援（例: Claude Design）へ現行デザインを渡して根本的な UI/UX 見直しを行う際の入力（全UI要素の現行画像）と、守るべき制約（設計思想・複雑性予算・確定済みの課題・非目標）を1か所に揃える。後半の「[設計見直しの前提と受け渡しブリーフ](#設計見直しの前提と受け渡しブリーフ)」を参照。

> 画面は機能追加に伴い変化します。本書の画像は下記「撮影条件」で再生成できます。差異を見つけたら画像を再生成し、必要なら本文も更新してください。

## 撮影条件

- サンプル文書: `doc_phase1_canvas`（決定論的フィクスチャ。秘密情報・API key・顧客データを含まない）
- UI locale: `ja` / LLM provider: `KJ_ATLAS_LLM_PROVIDER=none`（AI 無効・既定構成）
- 既定ビューポート: 1440×900（レスポンシブ節は 390 / 768 / 960px）
- 再生成スクリプト（リポジトリ正本）:
  - `03_Implement/frontend/scripts/capture_release_screenshots.mjs`（入口・全体・選択・共有・モバイル）
  - `03_Implement/frontend/scripts/capture_product_value_screenshots.mjs`（価値状態）
  - `03_Implement/frontend/scripts/capture_ui_catalog.mjs`（本書の UI 要素カタログ）
- ローカルに Playwright ブラウザ依存が無い場合は Playwright 公式 Docker イメージ内で実行します（手順は [assets/screenshots/README.md](assets/screenshots/README.md)）。

---

## 1. 起動 / 文書入口（ADR-0031 領域1）

起動直後に表示される「作業を開始」パネル。新規作成・サンプル・最近の文書・document.json / レビューパック取り込み・SafeMode 状態を扱う入口です。

![起動直後の作業開始パネル](assets/screenshots/start-document-entry.png)

## 2. 全体レイアウト

ヘッダー（主要ツールバー）・キャンバス作業面・右側の選択コンテキストの3分割が基本レイアウトです。

![起動後の標準画面（ヘッダー・キャンバス・右側パネル）](assets/screenshots/app-canvas-overview.png)

## 3. ヘッダー / 主要ツールバー

左から: `ファイル` / `編集` メニュー、`新規カード`、`島を作成`、`削除`、`保存`、`詳細`（AI・高度機能の表示トグル）、表示モード（`探索` / `レビュー` / `要約`、Cmd/Ctrl+1/2/3）、検索、`表示`、`共有と再現`、SafeMode 状態。`data-ui-core-action`（作成・島・削除・保存の4主要操作）と `data-ui-complexity-tier`（core / advanced）で前景／段階開示の境界が機械判定できます。

![ヘッダーと主要ツールバー](assets/screenshots/ui-header-toolbar.png)

## 4. キャンバス: カードとドメイン表現バッジ

カードには claimType（`事実`=緑 / `主張`=青 / `仮説`=紫 / `unknown`）、保留状態（`保留` / `未決` / `棚上げ`）、違和感（タグ数または点）、未レビュー（点）のバッジが表示されます。島は領域として囲み、見出しと折りたたみ操作を持ちます。

![カードのドメイン表現バッジと島](assets/screenshots/ui-card-domain-badges.png)

## 5. カード操作

背景の右クリックで「ここに新規カード」、カードの右クリックで `カードを編集` / `関係線でつなぐ` / `島を作成` / `削除` のコンテキストメニュー。カードのダブルクリックで本文をインライン編集（Enter または外側クリックで確定、Esc で取消、Shift+Enter で改行）。

![カード右クリックのコンテキストメニュー](assets/screenshots/ui-card-context-menu.png)

![カードのインライン編集](assets/screenshots/ui-card-inline-edit.png)

## 6. 選択コンテキスト（ADR-0031 領域3）

カードや島を選択すると、右側パネル先頭に「現在の選択」（対象・レビュー状態・根拠・矛盾）が表示されます。判断保留（通常/保留/未決/棚上げ）と違和感もこの文脈で確認・編集します。

![カード選択時の選択コンテキスト](assets/screenshots/selection-context-card.png)

![選択コンテキストの保留状態・違和感](assets/screenshots/ui-selection-context-holdstate.png)

![島選択時の選択コンテキスト](assets/screenshots/ui-selection-context-island.png)

## 7. 作業モード面（ADR-0031 領域4・「詳細」ON）

`詳細` を ON にしたうえで `作業モード` を開くと、レビュー差分・ナラティブ・マージ候補・パッチ・AI 提案などの高度機能が、選択コンテキスト（領域3）とは別の `data-ui-region="work-mode"` に表示されます。これにより、カードや島を選択した直後の右側パネルには、選択対象の確認と基本編集・レビューだけが残ります。

![「詳細」ON 時に展開される作業モード群](assets/screenshots/ui-advanced-work-mode-panels.png)

## 8. 表示（View）コントロール

`表示` パネルでは、表示モード・視点プリセット（俯瞰/中間/詳細）・フォーカス・深さ・SafeMode を扱います。

![表示コントロール](assets/screenshots/ui-view-controls.png)

## 9. 共有前確認 / 書き出し（ADR-0031 領域5）

`共有と再現` は「何を誰と共有するか」を起点にした確認フローです。共有前チェックで SafeMode・公開範囲・未レビュー情報・出力形式・レビューパック粒度を確認してから書き出します。

![共有と再現パネルの共有前確認](assets/screenshots/ui-share-preflight.png)

![共有・書き出し前の SafeMode チェック](assets/screenshots/share-export-safe-mode.png)

## 10. 読み取り専用モード

`?readOnly=1` 等で読み取り専用にすると、編集操作が無効化され、その旨が明示されます。

![読み取り専用モード](assets/screenshots/ui-read-only-mode.png)

## 11. 価値状態の例（Product Value フィクスチャ）

代表的な利用価値の状態。最初のまとまり作成、曖昧さの保持、レビューパックのトレース・読み取り専用レビューなど。

| | |
| --- | --- |
| ![最初の島](assets/screenshots/product-value-first-island.png) | ![最初の島の共有前確認](assets/screenshots/product-value-first-island-share-preflight.png) |
| ![曖昧さの状態](assets/screenshots/product-value-ambiguity-state.png) | ![曖昧さの共有前確認](assets/screenshots/product-value-ambiguity-share-preflight.png) |
| ![レビューパックのトレース](assets/screenshots/product-value-review-pack-trace.png) | ![レビューパックの読み取り専用](assets/screenshots/product-value-review-pack-readonly.png) |

## 12. レスポンシブ / 表示幅

主要操作が画面外へ消えないこと、テキストが重ならないことを各幅で確認します。

| 幅 | 画像 |
| --- | --- |
| 390px（mobile） | ![390px のヘッダーと主要操作](assets/screenshots/mobile-toolbar-smoke-390.png) |
| 768px（tablet 相当） | ![768px レイアウト](assets/screenshots/ui-responsive-768.png) |
| 960px（狭め desktop） | ![960px レイアウト](assets/screenshots/ui-responsive-960.png) |

## 13. 診断レポート

診断実行後に表示される品質レポート（参考。最新UIと差がある場合は再生成してください）。

![診断の品質レポート](assets/screenshots/diagnostics-quality-report.png)

---

## 設計見直しの前提と受け渡しブリーフ

外部のデザイン支援（Claude Design など）へ現行デザインを渡して**根本的な UI/UX 見直し**を行うことは有効ですが、**「白紙からの全面刷新」として渡すのは不適切**です。kj-atlas の課題の多くは見た目ではなく情報設計（IA）・構造にあり、また独自性の強い設計思想を持つため、無制約の刷新は価値を損ないます。次の前提・制約を**必ず同梱**し、「これらのレールの中で対象を絞って改善する」依頼として渡してください。

### A. コア価値と設計思想（侵してはならない核）

- **コア価値**: 「少ない操作で曖昧さを保持できること」。機能の多さではない（`01_Plans/adr/ADR-0001`, `00_Prompt/domain.md`, `ADR-0043`）。
- **3つの中核概念**: 保留（意味を確定しない健全な状態）／違和感（言語化前でも一級データ）／可逆性（配置・分類・構造はやり直せる）。
- **キャンバス主・チャット従**: AI は常に候補生成役で、確定はしない。チャットUIを主役にしない。
- **反スコアリング**: 単一正解・ランキング・採点で結論を誘導しない。
- **provider=none で完結**: AI 無効でも「書く・並べる・束ねる・つなぐ・保留する」が成立する。
- **SafeMode 既定ON**・共有前確認必須・出力安全境界。

### B. 5つの判断軸（出力評価ルーブリック）

1. これは人間の思考を雑にしないか／2. AI に早すぎる収束を与えないか／3. 保留・対立・未レビューを保持できるか／4. 差分・監査・レビューに載るか／5. 人間向け文脈と AI 向け文脈を混同していないか。いずれかに強く反する案は採用しない。

### C. 情報設計と複雑性予算（守る枠組み）

- **5領域 IA（`ADR-0031`）**: 開始/入口・キャンバス・選択コンテキスト・作業モード面・共有前確認。
- **複雑性予算（`ADR-0043`）**: CB-1 既定の静けさ／CB-2 保留の容易さ最優先／CB-3 純増禁止（置換・包含・モード分離で追加）／CB-4 可逆の明示。
- **段階開示・キーボード/focus 契約（`ADR-0030`, `UX-OPERABILITY-01..05`）**: Escape 閉鎖＋トリガへの focus 復帰、`data-panel` / `data-ui-region` / `data-focus-return-id` 等の契約を回帰させない。

### D. 確定済みの主要課題（再設計で優先的に解くべき対象）

- **`UX-NAV-01`（完了）**: 作業モード面（領域4）に独立領域を与え、Narrative / HIL / 差分を選択コンテキスト（領域3）の外へ移設した。`作業モード` は既定OFFのオーバーレイとして開き、Escape で閉じるとトリガへフォーカスが戻る。
- **CB-3 違反（中）**: ドメイン状態フィルタの二重化、Guided Flow の常設リーク等、既定表示への純増（`UX-COMPLEXITY-01` の監査対象）。
- **モード語彙の衝突**: 表示モードの「レビュー」と作業モードの「レビュー」が同語で別概念。
- **provider=none の第一級化**: AI 無効時の状態を「劣化フォールバック」でなく明示的な第一級モードとして提示する。

### E. 非目標（やらないこと）

- document/view/pack スキーマの変更、レガシー import/export の削除、`ADR-0030/0031/0043` の再決定、反スコアリング/キャンバス主従/SafeMode 既定ON の方針転換。

### F. 受け渡しに含める入力

- 本書の全 UI 要素スクリーンショット（§1〜§13）。
- 上記 A〜E（思想・判断軸・IA/複雑性予算・確定課題・非目標）。
- 関連正本: `01_Plans/adr/ADR-0001/0030/0031/0043`、`00_Prompt/domain.md`、`01_Plans/issues/issue-UX-NAV-01-*`、`issue-UX-COMPLEXITY-01-*`。

## 関連文書

- [受け入れ確認（操作手順）](acceptance_check.md)
- [導入手順](installation.md)
- [データ取り扱い](data_handling.md)
- スクリーンショット再生成: [assets/screenshots/README.md](assets/screenshots/README.md)
