# Claude Design へのデザイン設計要求カバレッジと未要求領域の棚卸し（2026-07-20 版）

区分: Internal / Informative（次回デザイン要求・照合ラウンドの計画入力）

目的: `design-request-gaps-2026-07.md`（2026-07-11版）以降に実装が進んだ領域を含め、現時点でClaude Designへ依頼すべき全作業を精査し、依頼事項を文書化する。**今すぐ着手すべきもの**と**将来（ADR実装ゲート成立後など）着手分**を明確に分けて記載する。

判定方法と限界: 前版（2026-07-11）の区分A〜D、`design-request-2026-07-round3〜8.md`の依頼本文、`design-qa-checklist.md`の全8回照合記録、`01_Plans/adr/`のADR-0048/0052/0053/0055/0059/0061、`03_Implement/frontend/src/{ui,canvas}`の実装済みUI全量（`ui/*.tsx` 39ファイル、`canvas/*.tsx` 9ファイル）、`01_Plans/issues/`の全221件を突き合わせて再棚卸しした。前版からの主な差分は次の3点。
1. 前版02区分Aの12項目は、その後の要求ラウンド・照合ラウンドが存在しないため（Round 8は master-data-settings と SaaS 先行レッドラインのみを扱い、これらには触れていない）、**全項目が未解消のまま持ち越し**。
2. Round 6の「新規画面設計は原則なし」宣言の**後**に、design docに一度も現れない新規の大型実装面が**2件**追加で見つかった（`InquiryJourneyPrototypePanel`、`RepresentativeVisualCuePrototypePanel`）。
3. Round 8のSaaS先行レッドライン（tenant switcher等）に対応する実装（`TenantSessionControl`等）が実際に着手されており（`runtime profile=saas-multitenant`時のみ有効化、既定では非表示）、設計照合が必要な新しい区分B項目になった。

## 1. 今すぐ依頼すべきもの（優先順）

| # | 対象 | 依頼種別 | 理由 |
| --- | --- | --- | --- |
| N-1 ★★ | **`RepresentativeVisualCuePrototypePanel`の設計レビュー** | 事後設計照合（新規要求） | 設計要求・照合とも皆無のまま、恒久タブとして本番稼働中。生の絵文字・手描き風グリフをカードアイコンとして直接表示しており、アプリ全体で維持されているslate/amber/teal中心の視覚言語から明確に逸脱している。ユーザビリティ試験用の計測器（試行時間・誤答数・5段階評価の記録）が製品面に混入している状態で、視覚的な逸脱としては本棚卸しで最も明確。 |
| N-2 ★★ | **`InquiryJourneyPrototypePanel`の設計レビュー** | 事後設計照合（新規要求） | Round 6宣言後に追加された最大の新規面（925行）で、design docに一度も言及がない。恒久タブとして本番稼働中、ファイルimport/export・workerベースのサイズ制限パース・分岐検出・破壊的な「探究終了」確認など安全境界に近い操作を含む。区分A-1（エージェント連携2パネル）と同型の「移行宣言後に無審査で出荷された大型面」。 |
| N-3 ★ | **A-1: エージェント連携2パネル**（`AgentTaskExportPanel`/`AgentResponseImportPanel`） | 事後設計照合（前版から持ち越し） | 前版で最優先★だったが、その後も要求・照合とも未実施のまま。外部共有文面・取込サニタイズ表示という安全境界に接する。 |
| N-4 | **B-1: 作業モードタブ内部の照合**（差分/選択マージ/AI提案/診断/文章化） | 実装照合のみ（回答済み設計との照合） | 拡張提案で回答済み（差分63/文章化21/診断13/読み順10ヒット）。要求は不要、照合だけで前進できる費用対効果最大の項目。QA-MONKEY-11のボタン重なりはこの未照合領域の実例。 |
| N-5 | **DOMAIN-W-ITERATION-01（W型反復的探究）の事後設計照合** | 事後設計照合（新規要求、N-2と統合可） | Phase 2の手動コア（ラウンドタイムライン、引き継ぎ/再開ブリーフ、分岐比較、カード来歴）が実装済み（T7チェック済み）で実運用に入っているが、設計要求も照合も皆無。N-2の`InquiryJourneyPrototypePanel`と対象が重なるため、1件の依頼にまとめられる。 |
| N-6 | **DOMAIN-VISUAL-CUE-01 Phase 1の設計照合**（手描き/基本図形/ローカル写真経路） | 事後設計照合（新規要求） | 外部通信を伴わないPhase 1コアはADR-0060未採択でも進行中の非ゲート作業（AC-6〜10が未完了）。N-1の`RepresentativeVisualCuePrototypePanel`はこの機能の試験用プロトタイプであり、本番機能として設計する際は同じ依頼にまとめられる。 |
| N-7 | **A-2/A-3: 開始パネル・カード検索** | 新規要求（前版から持ち越し） | 5領域IAの「領域1」だが設計要求の主題になった記録なし。ドッグフード摩擦記録（再開導線の欠如）と束ねて依頼する。 |

## 2. 将来着手分（実装ゲート待ち・運用知見待ち）

| # | 対象 | ゲート条件 | 状況 |
| --- | --- | --- | --- |
| F-1 | **B-7（新規）: Tenant session制御群の設計照合**（`TenantSessionControl`/`TenantSessionBootstrapGate`/`TenantSessionRuntimeGate`/`TenantChangeConfirmationDialog`） | 実装自体は`runtime profile=saas-multitenant`時のみ有効化される形で既に着手済み（既定では非表示のため安全）。設計コンセプトは`master-data-settings-ui-ux-concept.md`（2026-07-20更新）とRound 8 R8-Eで既に文書化済み。 | **概念設計は完了、実装照合が未実施**。ADR-0059/ADR-0061のImplementation gate成立を待たずに、現在既定OFFで存在する実装を設計コンセプトと照合するレビューは今すぐ実施可能（有効化の可否とは別問題）。 |
| F-2 | **R8-C/F/G/H: Admin入口・Tenant Admin・Platform Control Plane・文書アクセス設定** | ADR-0059 Implementation gate（6項目: contract先行反映、migration/複合制約、tenant必須context伝播、DB tenant guard、越境negative matrix、effectiveCapabilities後のUI導入）+ ADR-0061 Implementation gate（5項目: tenantSessionVersion原子的解決、closed-world validation、precondition全route適用、2タブ同時操作negative matrix、cross-tab通知欠落時のserver guard） | **未充足**。対応する実装（`TenantAdmin*`/`DocumentAccessAdmin*`）はまだ存在しない。ゲート成立後に着手。 |
| F-3 | **EXT-CONN-02: 縁側レーン（外部提案カードの着地帯）** | EXT-CONN-01の運用実績 + ADR-0054 D3の採択・実装 | Draft。P32で方向性のみ確認済み、詳細レッドラインは実装ラウンドへ先送りと明記。 |
| F-4 | **EXT-CONN-03: critique constraint exportのトグル** | 段階1/2（EXT-CONN-01/02）の運用知見 | Draft。デザイン方向は既に確定済み（P32 B-3）だが実装は明示的に延期。 |
| F-5 | **EXT-CONN-04: evidence trail landing view** | 段階1/2の進行 + 実装レッドライン受領 | Draft。新規の読み取り専用画面で、まだレッドラインなし。 |
| F-6 | **DOMAIN-VISUAL-CUE-01のB/C/D区分**（外部素材・生成画像経路） | ADR-0060の採択（AC-5が未チェック） | Phase 1コア（N-6）とは独立してゲート待ち。 |
| F-7 | **A-4〜A-12（前版から持ち越し、優先度中〜低）**: 表示コントロールパネル全体・島の形状編集・根拠オーバーレイ・コンテキストメニュー・状態フィルタバー・シェルフ・横断のエラー/空/読込/保存競合の状態様式・取込検証エラーの提示 | ゲートなし。着手順は次回デザイン要求ラウンドの容量次第 | 全項目、前版から状況変化なし（要求記録なし）。 |
| F-8 | **B-2〜B-6（前版から持ち越し）**: 共有パネルの残り・読み順モード・読み取り専用モード表示・レスポンシブ/モバイル幅・⌘K/チートシート | ゲートなし。個別の照合ラウンドがまだ立っていない | 全項目、前版から状況変化なし。 |
| F-9 | **C-3/C-4/C-6（前版から持ち越し、未解決）**: ラベルカリング「…」の事後照合・要約チップと個別ブロックの二重表示解消・ドッグフード由来の低優先摩擦 | ゲートなし | 前版時点で未解決のまま、その後の解決記録なし。 |
| F-10 | **SOCIAL-DIFFUSION-01〜04（新規発見）** | Stream H（Docs first/Docs onlyで明示的にロック中） | 具体的な画面・パネル名を伴わない将来構想段階。UI設計依頼の対象にはまだ早い。 |

## 3. 前版からの解決確認（区分C該当分）

| # | 論点 | 解決状況 |
| --- | --- | --- |
| C-1 | キャンバス選択ロールとメニュー内フォームの構造 | 解決済み（2026-07-13、ADR-0052 Accepted、UI-QUALITY-A11Y-03で実装） |
| C-2 | 診断バンドルの生成・プレビュー・コピー/ダウンロードUI | 判断済み（2026-07-13、ADR-0053 Accepted、PRODUCT-OPS-02で実装） |
| C-5 | 作業モードタブへのrole=tablist導入要否 | 解決済み（2026-07-15、ADR-0055 Accepted、UX-NAV-02で検証済み） |

上記3件は前版の区分Cから除外済み。区分D（メモ機能/research⇄businessモード/VUI/レンズヒント、リアルタイム共同編集）は方針変更なく維持。

## 4. 推奨する次の一手

1. **N-1/N-2（プロトタイプ2面の事後設計照合）を最優先で1件の依頼にまとめる**。両者とも「Round 6宣言後に無審査で出荷された恒久タブ」という同型の問題であり、実機スクリーンショット＋自己申告チェックリストを添えて✓/△/✗レビューを依頼する形が、A-1で確立済みの体制と整合する。特にN-1は視覚言語からの逸脱が明確なため、「本番機能として正式化する場合の視覚言語整合」を論点に含める。
2. **N-4（B-1: 作業モードタブ内部の照合）は要求不要で照合のみのため、次回照合ラウンドで独立して並行消化できる**。実装側の準備（自己申告チェックリスト作成）だけで着手可能。
3. **F-1（tenant session制御群の設計照合）はADR実装ゲートの成立を待たずに今すぐ着手できる**。有効化条件（runtime profile）とは無関係に、既存の既定OFF実装を`master-data-settings-ui-ux-concept.md`と照合するレビューは可能。ゲート成立後にF-2（Admin/Platform面）へ進む前段として位置づける。
4. **N-3/N-7（A-1、A-2/A-3）は、ドッグフード摩擦記録と束ねて次の新規デザイン要求ラウンド（Round 9相当）の主題候補として保持する**。
5. F-3〜F-6（外部連携・visual cue拡張）は、それぞれの明記されたゲート（運用実績・ADR採択）が成立するまで依頼を起こさない。

## Traceability

- Related: `02_Architecture/design/design-request-gaps-2026-07.md`（前版、2026-07-11）
- Related: `02_Architecture/design/ui_design_handoff.md`（受け渡し境界の正本）
- Related: `02_Architecture/design/design-request-2026-07-round3.md` 〜 `round8.md`
- Related: `02_Architecture/design/design-qa-checklist.md`（第1〜8回照合記録）
- Related: `02_Architecture/design/master-data-settings-ui-ux-concept.md`
- Related: `04_Documentation/ui_catalog.md`
- Related: `01_Plans/adr/ADR-0048`, `ADR-0052`, `ADR-0053`, `ADR-0055`, `ADR-0059`, `ADR-0061`
- Related issues: `issue-DOMAIN-VISUAL-CUE-01`, `issue-DOMAIN-W-ITERATION-01`, `issue-SAAS-TENANT-01`, `issue-EXT-CONN-02`, `issue-EXT-CONN-03`, `issue-EXT-CONN-04`
