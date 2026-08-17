# Claude Design へのデザイン設計要求カバレッジと未要求領域の棚卸し（2026-07-20 版）

区分: Internal / Informative（次回デザイン要求・照合ラウンドの計画入力）

改訂: 2026-07-21 — 即時依頼項目（N-1〜N-7）とF-1に、次回デザイン要求ラウンド（Round 9相当）へそのまま展開できる**詳細依頼仕様**（依頼種別・背景/現状・設計論点・レビュー観点・期待成果物・受入条件・スコープ境界・添付予定の証跡）を追記した。実装面の記述は origin/main `2c452dce` のソースへ突き合わせて再検証済み。前版で「恒久タブとして本番稼働中」と記していた N-1/N-2 は、正確には「本番バンドルに常設タブとして同梱されるが、高度UIと作業モードの二重ゲートの背後にあり既定では非表示」であることを反映した。

目的: `design-request-gaps-2026-07.md`（2026-07-11版）以降に実装が進んだ領域を含め、現時点でClaude Designへ依頼すべき全作業を精査し、依頼事項を文書化する。**今すぐ着手すべきもの**と**将来（ADR実装ゲート成立後など）着手分**を明確に分けたうえで、即時分は依頼本文へ落とし込める粒度まで要件を具体化する。

判定方法と限界: 前版（2026-07-11）の区分A〜D、`design-request-2026-07-round3〜8.md`の依頼本文、`design-qa-checklist.md`の全8回照合記録、`01_Plans/adr/`のADR-0044/0048/0052/0053/0055/0059/0060/0061、`03_Implement/frontend/src/{ui,canvas}`の実装済みUI全量（`ui/*.tsx` 39ファイル、`canvas/*.tsx` 9ファイル）、`01_Plans/issues/`の全221件を突き合わせて再棚卸しした。詳細仕様の実装記述は origin/main `2c452dce` の該当コンポーネント（`RepresentativeVisualCuePrototypePanel.tsx`・`InquiryJourneyPrototypePanel.tsx`・`AgentTaskExportPanel.tsx`・`AgentResponseImportPanel.tsx`・`TenantSessionControl.tsx`・`TenantChangeConfirmationDialog.tsx` ほか）を直接精読して裏取りした。前版からの主な差分は次の3点。
1. 前版02区分Aの12項目は、その後の要求ラウンド・照合ラウンドが存在しないため（Round 8は master-data-settings と SaaS 先行レッドラインのみを扱い、これらには触れていない）、**全項目が未解消のまま持ち越し**。
2. Round 6の「新規画面設計は原則なし」宣言の**後**に、design docに一度も現れない新規の大型実装面が**2件**追加で見つかった（`InquiryJourneyPrototypePanel`、`RepresentativeVisualCuePrototypePanel`）。いずれも本番バンドルに同梱されるが、`isAdvancedUiEnabled`（高度UI）と`isWorkModeOpen`（作業モード）の二重ゲートの背後にあり既定では到達しない。
3. Round 8のSaaS先行レッドライン（tenant switcher等）に対応する実装（`TenantSessionControl`等）が実際に着手されており（`runtime profile=saas-multitenant`時のみ有効化、既定では非表示）、設計照合が必要な新しい区分B項目になった。

## 1. 今すぐ依頼すべきもの（優先順）

まず一覧、続いて各項目の詳細依頼仕様を示す。詳細仕様は次回デザイン要求ラウンドの`## 貼り付け用プロンプト`へそのまま転記できる粒度で書いている。

| # | 対象 | 依頼種別 | 要点 |
| --- | --- | --- | --- |
| N-1 ★★ | **`RepresentativeVisualCuePrototypePanel`の設計レビュー** | 事後設計照合＋本番化時の視覚言語設計（新規要求） | 本番バンドルに常設タブ（`visual-cue`）として同梱。二重ゲートの背後で既定非表示だが、DOMAIN-VISUAL-CUE-01 Phase 0の計測プロトタイプとして5条件（対照/手描き風/CSS図形/ローカル写真/生絵文字）を提示。生の絵文字・`cursive`＋回転の手描き風グリフ・非トークンのinline hex（off-palette色を含む）でslate/amber/teal視覚言語から逸脱。試行時間・誤答数・5段階評価の計測器が本番面に混入。本棚卸しで視覚的逸脱が最も明確。 |
| N-2 ★★ | **`InquiryJourneyPrototypePanel`の設計レビュー** | 事後設計照合（新規要求、N-5と統合可） | Round 6宣言後に追加された最大の新規面（約924行）で、design docに一度も言及がない。本番バンドルに常設タブ（`inquiry`）として同梱、二重ゲートで既定非表示、support level `L0: Planned`。ファイル入出力・workerベースのサイズ制限パース・分岐検出・破壊的な「探究終了」確認・**SafeMode非適用のローカルエクスポート**など安全境界に接する操作を含む。区分A-1と同型の「移行宣言後に無審査で出荷された大型面」。 |
| N-3 ★ | **A-1: エージェント連携2パネル**（`AgentTaskExportPanel`/`AgentResponseImportPanel`） | 事後設計照合（前版から持ち越し） | 前版で最優先★だったが、その後も要求・照合とも未実施のまま。外部共有文面・取込サニタイズ表示という安全境界に接する。 |
| N-4 | **B-1: 作業モードタブ内部の照合**（差分/選択マージ/AI提案/診断/文章化） | 実装照合のみ（回答済み設計との照合） | 拡張提案で回答済み（差分63/文章化21/診断13/読み順10ヒット）。要求は不要、照合だけで前進できる費用対効果最大の項目。QA-MONKEY-11のボタン重なりはこの未照合領域の実例。 |
| N-5 | **DOMAIN-W-ITERATION-01（W型反復的探究）の事後設計照合** | 事後設計照合（新規要求、N-2と統合） | Phase 2の手動コア（ラウンドタイムライン、引き継ぎ/再開ブリーフ、分岐比較、カード来歴）が実装済み（T7チェック済み）で実運用に入っているが、設計要求も照合も皆無。実体は`InquiryJourneyPrototypePanel`であり、N-2の依頼に統合する。 |
| N-6 | **DOMAIN-VISUAL-CUE-01 Phase 1の設計照合**（手描き/基本図形/ローカル写真経路） | 事後設計照合（新規要求、N-1と統合） | 外部通信を伴わないPhase 1コアはADR-0060未採択でも進行中の非ゲート作業（AC-6〜10が未完了）。N-1の`RepresentativeVisualCuePrototypePanel`はこの機能のPhase 0試験プロトタイプであり、N-1の依頼に統合する。 |
| N-7 | **A-2/A-3: 開始パネル・カード検索** | 新規要求（前版から持ち越し） | 5領域IAの「領域1」だが設計要求の主題になった記録なし。ドッグフード摩擦記録（再開導線の欠如）と束ねて依頼する。 |

### 各即時依頼項目の詳細仕様

各項目は共通して、依頼種別 / 背景（現状・origin/main `2c452dce`基準）/ 設計論点（回答してほしい問い）/ レビュー観点（`design-qa-checklist.md`の4軸: A.視覚言語・B.状態遷移・C.核の保護・D.a11y/契約）/ 期待成果物 / 受入条件 / スコープ境界（描かない・触れない範囲）/ 添付予定の証跡、の順で記す。

#### N-1. `RepresentativeVisualCuePrototypePanel` の設計レビュー

- 依頼種別: 事後設計照合＋本番機能化時の視覚言語設計（新規要求）。
- 背景（現状）: 到達には高度UI有効化（`isAdvancedUiEnabled`）かつ作業モード展開（`isWorkModeOpen`）が必要な`visual-cue`タブ（root `data-panel="representative-visual-cue-prototype"`）。既定非表示だが本番バンドルに同梱され、build-timeの除外はない。DOMAIN-VISUAL-CUE-01 Phase 0の代表ユーザ比較実験（AC-6）用ハーネスで、島タイトルのコードポイント総和で決まる5条件を提示する: **C0**キューなし（対照）/ **C1**手描き風Unicodeグリフ（`HAND_CUES`、`fontFamily:"cursive"`＋擬似ランダム回転）/ **C2**CSS基本図形（円・四角・回転菱形）/ **C3**ローカル写真（合成fixture、外部URL・ネットワークなし）/ **C4**生の絵文字（`EMOJI_CUES`）。色はすべてinline hexでデザイントークン非経由、視覚言語から外れる値を含む（sky系 `#e0f2fe`、green系 `#166534`、amber系 `#92400e`、teal系 `#0f766e`）。計測器として試行時間（`performance.now()`）・誤答数（`aria-live`表示）・5段階評価（Likert、未入力で「次へ」を無効化）・セッション内結果ログを保持する（永続化・送信はなく、`role="status"`でセッション限定を明示）。
- 設計論点:
  1. 本番機能化する場合、視覚キューをslate/amber/teal視覚言語とデザイントークンにどう整合させるか。特に (a) 生の絵文字（OS依存の多色描画・色統制なし）の採用可否、(b) `cursive`＋回転の手描き風グリフの是非、(c) inline hexのトークン化、(d) C2図形境界のtealが「amberは保持系に予約」等のチャネル規約と衝突しないか。
  2. 計測器（試行時間・誤答・Likert・結果ログ）は本番機能に残すのか、Phase 0実験専用としてbuild-timeで本番バンドルから除外すべきか。「計測しながら使わせる」構成がコア価値（少ない操作で曖昧さを保持）を侵さないか。
  3. C0〜C4のうち本番採用する表現形式の選定基準（AC-4a「継続性 vs 手描き記号／基本図形／写真ラベル／現場写真／図記号」との対応）。
- レビュー観点: **A.視覚言語**=絵文字/`cursive`回転/非トークンhex/off-palette色の逸脱。**B.状態遷移**=idle→active→complete、Likert未入力時の無効化。**C.核の保護**=計測器が評価語・スコア・早すぎる収束を持ち込まないか（anti-scoring）。**D.a11y/契約**=誤答カウンタの`aria-live`、セッション限定`role="status"`、マウス/キーボード/390px/スクリーンリーダー到達性。
- 期待成果物: (1) 4軸の✓/△/✗照合、(2) 本番視覚言語整合案（絵文字・手描きの採否、トークン化方針）、(3) 計測器の製品／実験分離方針（build-time除外の要否）。
- 受入条件: DOMAIN-VISUAL-CUE-01 AC-4aとの整合が確認でき、AC-6（Phase 0代表ユーザ比較）を本番UIから切り離して実施する段取りが定まること。△/✗はissue化する。
- スコープ境界: Phase B/C/D（外部素材・生成画像経路）はADR-0060未採択につき**設計しない**。Phase 1（外部通信なし）に限定する。初期表示への純増を**作らない**。既定UI（非高度）に一切現れないことを維持する。
- 添付予定の証跡: `data-panel="representative-visual-cue-prototype"` のC0〜C4各条件の実機スクリーンショット＋A/B/C/D自己申告チェックリスト。

#### N-2. `InquiryJourneyPrototypePanel` の設計レビュー（N-5 を統合）

- 依頼種別: 事後設計照合（新規要求）。DOMAIN-W-ITERATION-01 のPhase 2手動コア照合（N-5）を本項に統合する。
- 背景（現状）: 約924行、`inquiry`タブ、N-1と同じ二重ゲートで既定非表示・本番バンドル同梱、support level `L0: Planned`（未本番化プロトタイプ）。純セッション状態で動作し、バックエンド呼び出しはなく永続化はローカルJSONの書出/読込のみ。主要面: 6段階の段階選択（順序自由、anti-wizard）/ラウンド記録/分岐（親ラウンド選択＋`undo-branch`）/ラウンドタイムライン/引き継ぎレビュー（1件ずつadopt・adopt-edited・hold・skip、未回答でも保存可）/再開ブリーフ（読み取り専用プレビュー）/カード来歴（祖先DAG、出典を捏造しない）/ラウンド比較（件数のみ、スコア化しない）/エクスポート範囲選択/入出力/探究終了（2段階確認）。安全境界: (a) ファイルサイズ制限 5MiB警告・20MiBハード（読取前ゲート・パース・シリアライズの3箇所で強制）、(b) 取込の cross-document origin guard（現在開いている文書由来でないbundleを拒否）、(c) fail-closed strict検証（unknown key/version/enum・壊れた参照・循環・digest不一致を拒否）、(d) **エクスポートはSafeModeマスキングを適用せず**生のカード本文・出典をローカルファイルへ書き出す（amber警告のみ。AC-11のランタイムSafeMode層は未実装＝`L0: Planned`）、(e) tenant切替中の取込は`runTenantScopedOptionalTask`でstale結果を破棄、(f) 探究終了は2段階確認だがin-memory破棄にundoがなく、「自動保存されない」bannerの常設が唯一の保険。
- 設計論点:
  1. **エクスポート時のSafeMode非適用**を設計面でどう扱うか。現状はamber警告のみで生本文がローカルファイルに出る。AC-11のランタイムSafeMode-export UX（マスキング／部分共有／保持期間／tenant境界の見せ方）を先取り設計すべきか、当面は警告強化で足りるか。SafeMode既定ON・共有前確認必須（核）との整合を問う。
  2. 探究終了の破壊的確認（in-memory破棄・undoなし）の説明可能性は十分か。「不可逆操作は実行前に影響を説明する」handoff契約を満たすか。
  3. 分岐undoの脆さ（`canUndoBranch`はキャンバス編集後に恒久的に消える）をユーザへどう伝えるか。AC-6aの「Ctrl+Zではない明示的分岐undo」の見せ方。
  4. 二重ゲート＋`L0: Planned`プロトタイプとして、本番化時に初期表示への純増=0・破壊的巻き戻し禁止（複雑性予算）をどう維持するか。
- レビュー観点: **A.視覚言語**=amber警告/session banner/`details`群の整合。**B.状態遷移**=pre-start↔started、探究終了の2段階、取込中/キャンセル/large/origin不一致。**C.核の保護**=比較が件数のみでスコア化しない・来歴が出典を捏造しない・SafeMode/未レビュー/保留の保持。**D.a11y/契約**=比較サマリの`aria-live`、引き継ぎのfocus移動、キーボード/390px。
- 期待成果物: 4軸の✓/△/✗照合＋エクスポートSafeMode層のUX方向＋破壊的/不可逆操作（探究終了・分岐undo）の影響提示レッドライン。
- 受入条件: DOMAIN-W-ITERATION-01 AC-11（SafeMode-export/部分共有/保持/tenant境界）の設計方向が定まり、`L0: Planned`→本番化に向けた複雑性予算（初期表示純増0）を満たす照合が得られること。
- スコープ境界: Phase 3（提案のみAI、T9保留）は**設計しない**。バックエンド同期・クラウド保存を**示唆しない**（ローカルのみ）。既定UIに現れないことを維持する。
- 添付予定の証跡: `data-domain-action="start-inquiry-journey-prototype"`起点の各面スクリーンショット、`data-testid="inquiry-export-scope"`、探究終了確認、A/B/C/D自己申告チェックリスト。

#### N-3. A-1 エージェント連携2パネルの事後設計照合

- 依頼種別: 事後設計照合（前版から持ち越し）。
- 背景（現状）: `AgentTaskExportPanel`/`AgentResponseImportPanel`はいずれも表示専用で、エクスポート文面の生成・取込パース/サニタイズ本体は`export/agent_task_export`・`import/agent_response_import`側にある（パネルはprops経由で結果とハンドラを受け取る）。Export側: 表示はスコープ要約（件数のみ）で、SafeMode時は`include_unreviewed_drafts`チェックボックスを非表示、出典参照はopt-in＋警告付き、「scope confirmed」確認ゲート（`canExport = hasSelection && scopeConfirmed`、未確認では3つのエクスポートボタンすべて無効）。Import側の安全モデル: パースは文書に触れず、per-proposalの明示的Importのみが`applyDocumentChange`を1件ずつ適用（個別にCmd+Zで戻せる）、parseErrorsは赤、parseWarningsは件数のみamber（生の警告文はDOMへ流さない）、per-proposal状態は orphaned（Adoptボタンなし）／patchSignatureMismatch（Adoptを「パッチ書出」に置換しin-app適用を拒否）／patchHasDeleteOps（削除操作警告）、一括適用はなし。両パネルともdialog契約（`role="dialog"`/`aria-modal`、Escapeで段階閉鎖＋トリガへfocus復帰、focus trap、閉じるボタンの`data-focus-return-id`）。
- 設計論点: (1) 外部エージェントへ渡すエクスポート文面（パネル外で生成）に対する安全境界表示は十分か（SafeMode gating・出典参照警告・scope confirm）。(2) 取込サニタイズの見せ方（警告は件数のみ／エラーは全文赤）が、説明可能性と情報過多のバランスとして妥当か。(3) 人間向け文脈とAI向け文脈の分離（handoff評価5軸）を満たすか。
- レビュー観点: **A.視覚言語**=警告色（`#9a3412`等）・amberの用法。**B.状態遷移**=confirm前後、per-proposalのadopted/rejected。**C.核の保護**=「AIは候補生成に留まり確定しない」（per-proposal明示適用・一括なし・patch mismatch時のin-app適用拒否）。**D.a11y/契約**=dialog契約4点。
- 期待成果物: 4軸の✓/△/✗照合＋外部共有文面/取込サニタイズ表示のレッドライン。
- 受入条件: SafeMode既定ON・共有前確認必須（核）との整合が確認できること。△/✗はissue化する。
- スコープ境界: 生成/パース本体ロジックは対象外（表示規約のみ）。新規操作を既定表示へ純増させない。
- 添付予定の証跡: `data-testid="agent-task-scope-confirmed"`等を含む両パネルの実機スクリーンショット＋A/B/C/D自己申告チェックリスト。

#### N-4. B-1 作業モードタブ内部の実装照合

- 依頼種別: 実装照合のみ（回答済み設計との照合、新規要求は不要）。
- 背景（現状）: 差分（`DiffPanel`/`ReviewDiffPanel`）・選択マージ（`MergeSuggestionsPanel`）・AI提案（`SuggestionPanel`/`HilRsRediffPreview`）・診断（反スコアリング表現）・文章化（`NarrativesPanel` 事実/解釈峻別）。設計は拡張提案で回答受領済み（差分63/文章化21/診断13/読み順10ヒット）だが、第6回照合は「器」（全画面オーバーレイ・Escape・focus復帰）のみで、タブ内部と回答仕様の照合記録がない。QA-MONKEY-11の「候補を収集」ボタン重なり（No candidates集約表示がボタンを覆う）はこの未照合領域の実欠陥例。
- 設計論点: 回答仕様（拡張提案）と各タブ内部実装の逐条照合。特に (1) 診断の反スコアリング表現、(2) 文章化の事実/解釈峻別、(3) 選択マージのNo candidates集約表示がボタンを覆わないか（QA-MONKEY-11再発防止）。
- レビュー観点: 4軸、特に **C.核の保護**（anti-scoring・事実/解釈の峻別）。
- 期待成果物: 各タブの✓/△/✗照合表（新規要求は起こさない）。
- 受入条件: 回答仕様との乖離が✓/△/✗で記録され、△/✗がissue化されること。
- スコープ境界: 新規設計要求は**出さない**（照合のみ）。実装側は自己申告チェックリスト作成だけで着手できる。
- 添付予定の証跡: 各タブの実機スクリーンショット＋回答仕様（拡張提案）該当節との対応表。

#### N-5. DOMAIN-W-ITERATION-01（W型反復的探究）の事後設計照合 — N-2 に統合

- 依頼種別: 事後設計照合（新規要求）。実体が`InquiryJourneyPrototypePanel`のため **N-2 の依頼に統合**する。本項は受入アンカーの補足として残す。
- 補足アンカー: 課題は In Progress / P1 / `SecurityGateImpact: SafeMode / share-export / import-sanitize` / 検証水準 e2e。AC-1〜AC-12は全て `[x]` だが、**AC-11 は「契約定義」水準のみ**（永続`InquiryExportInfoV1` SafeModeメタ型は未追加、support level `L0: Planned`）。T1〜T8完了、**T9保留**（Phase 2実運用後にAI支援を別issue化するか判断）。Phase 3（提案のみAI）は未着手。N-2の設計論点1（エクスポートSafeMode）と論点4（複雑性予算）がこのアンカーに対応する。

#### N-6. DOMAIN-VISUAL-CUE-01 Phase 1 の設計照合 — N-1 に統合

- 依頼種別: 事後設計照合（新規要求）。`RepresentativeVisualCuePrototypePanel`がPhase 0プロトタイプのため **N-1 の依頼に統合**する。本項は受入アンカーの補足として残す。
- 補足アンカー: Phase 1（手描き/基本図形/ローカル写真、外部通信なし＝パネルのC0〜C4に対応）は**非ゲートで進行中**。AC-1〜AC-4aは `[x]`、**AC-5〜AC-10が未了**（AC-5＝ADR-0060の供給経路/ライセンス/保管境界の採択、AC-6＝Phase 0代表ユーザ比較、AC-7＝Phase 1のマウス/キーボード/390px/SR検証、AC-8/9＝外部素材/生成画像、AC-10＝性能予算）。B/C/D区分（外部素材・生成画像）はADR-0060（Pending）採択までゲート（→F-6）。

#### N-7. A-2/A-3 開始パネル・カード検索の新規設計要求

- 依頼種別: 新規要求（前版から持ち越し）。
- 背景（現状）: `StartPanel`（新規作成・サンプル・文書一覧・再開導線）は5領域IAの「領域1」だが設計要求の主題になった記録がない。`SearchBar`（カード本文検索・非一致を非表示）は⌘Kのコマンド検索とは別物。ドッグフード（2026-07-10）で「再読込後に直前の文書へ戻るワンクリック導線がない」摩擦を記録済み。関連して`UI-QUALITY-A11Y-07`（StartPanelの再オープン導線が未定義でfocus復帰先が定まらない）が判断待ちで残っている。
- 設計論点: (1) 開始パネルの情報設計（新規/サンプル/一覧/再開の主従関係）。(2) 再開導線（直前文書へのワンクリック復帰）の新設可否と、それに伴うfocus復帰先（`UI-QUALITY-A11Y-07`の判断と連動）。(3) カード検索の検索状態と文書スコープの関係（QA-MONKEY-03の経緯）。
- レビュー観点: 4軸、特に **B.状態遷移**（Empty/一覧/検索一致・非一致）と **D.a11y/契約**（focus復帰・キーボード到達性）。
- 期待成果物: 開始パネル・カード検索のレッドライン。各状態一覧＋viewport（1440/768/390px）＋「主従関係・認知負荷・キーボード動線」で複数案を比較し1案を選定・根拠提示。
- 受入条件: ドッグフード摩擦（再開導線の欠如）が解消方向に載り、`UI-QUALITY-A11Y-07`のfocus復帰先が定まること。
- スコープ境界: ⌘Kコマンド検索とカード本文検索を**混同しない**。新規操作を既定表示へ純増させず、置換・包含・モード分離で収める。
- 添付予定の証跡: `StartPanel`/`SearchBar`の実機スクリーンショット＋`01_Plans/dogfood/dogfood-log-2026-07-10.md`の該当摩擦参照。

## 2. 将来着手分（実装ゲート待ち・運用知見待ち）

| # | 対象 | ゲート条件 | 状況 |
| --- | --- | --- | --- |
| F-1 | **B-7（新規）: Tenant session制御群の設計照合**（`TenantSessionControl`/`TenantSessionBootstrapGate`/`TenantSessionRuntimeGate`/`TenantChangeConfirmationDialog`） | 実装自体は`runtime profile=saas-multitenant`時のみ有効化される形で既に着手済み（既定では非表示のため安全）。設計コンセプトは`master-data-settings-ui-ux-concept.md`（2026-07-20更新）とRound 8 R8-Eで既に文書化済み。 | **概念設計は完了、実装照合が未実施**。ADR実装ゲート成立を待たず今すぐ照合可能。詳細チェックポイントと候補所見は下記「F-1 詳細」。 |
| F-2 | **R8-C/F/G/H: Admin入口・Tenant Admin・Platform Control Plane・文書アクセス設定** | ADR-0059 Implementation gate（6項目: contract先行反映、migration/複合制約、tenant必須context伝播、DB tenant guard、越境negative matrix、effectiveCapabilities後のUI導入）+ ADR-0061 Implementation gate（5項目: tenantSessionVersion原子的解決、closed-world validation、precondition全route適用、2タブ同時操作negative matrix、cross-tab通知欠落時のserver guard） | **未充足**。対応する実装（`TenantAdmin*`/`DocumentAccessAdmin*`）はまだ存在しない。ゲート成立後に着手。 |
| F-3 | **EXT-CONN-02: 縁側レーン（外部提案カードの着地帯）** | EXT-CONN-01の運用実績 + ADR-0054 D3の採択・実装 | Draft。P32で方向性のみ確認済み、詳細レッドラインは実装ラウンドへ先送りと明記。 |
| F-4 | **EXT-CONN-03: critique constraint exportのトグル** | 段階1/2（EXT-CONN-01/02）の運用知見 | Draft。デザイン方向は既に確定済み（P32 B-3）だが実装は明示的に延期。 |
| F-5 | **EXT-CONN-04: evidence trail landing view** | 段階1/2の進行 + 実装レッドライン受領 | Draft。新規の読み取り専用画面で、まだレッドラインなし。 |
| F-6 | **DOMAIN-VISUAL-CUE-01のB/C/D区分**（外部素材・生成画像経路） | ADR-0060の採択（AC-5が未チェック） | Phase 1コア（N-1/N-6）とは独立してゲート待ち。 |
| F-7 | **A-4〜A-12（前版から持ち越し、優先度中〜低）**: 表示コントロールパネル全体・島の形状編集・根拠オーバーレイ・コンテキストメニュー・状態フィルタバー・シェルフ・横断のエラー/空/読込/保存競合の状態様式・取込検証エラーの提示 | ゲートなし。着手順は次回デザイン要求ラウンドの容量次第 | 全項目、前版から状況変化なし（要求記録なし）。 |
| F-8 | **B-2〜B-6（前版から持ち越し）**: 共有パネルの残り・読み順モード・読み取り専用モード表示・レスポンシブ/モバイル幅・⌘K/チートシート | ゲートなし。個別の照合ラウンドがまだ立っていない | 全項目、前版から状況変化なし。 |
| F-9 | **C-3/C-4/C-6（前版から持ち越し、未解決）**: ラベルカリング「…」の事後照合・要約チップと個別ブロックの二重表示解消・ドッグフード由来の低優先摩擦 | ゲートなし | 前版時点で未解決のまま、その後の解決記録なし。 |
| F-10 | **SOCIAL-DIFFUSION-01〜04（新規発見）** | Stream H（Docs first/Docs onlyで明示的にロック中） | 具体的な画面・パネル名を伴わない将来構想段階。UI設計依頼の対象にはまだ早い。 |

### F-1 詳細（今すぐ照合可能な実装照合）

- 依頼種別: 実装照合のみ（`master-data-settings-ui-ux-concept.md`の規範との照合）。有効化条件（`runtime profile=saas-multitenant`）とは独立に今すぐ実施できる。
- 背景（現状）: `TenantSessionControl`は`verifiedTenantSession`が非nullのときのみ描画され（SaaS entry path＝`KJ_ATLAS_RUNTIME_PROFILE=saas-multitenant`→`tenant-session-required`のみ、他profileでは非表示）、membershipが1件なら静的label、複数ならサーバー返却の`availableTenants`だけの`select`スイッチャを出す（tenantId自由入力なし）。切替要求は`isDirty`時のみ`TenantChangeConfirmationDialog`（`role="alertdialog"`、cancel/discard/saveの三択）を開き、clean時は即時切替。確定後は文書・選択・検索・work mode・import preview・recent・QueryPreset・request cacheを破棄して新tenantで再取得する（`performTenantSwitch`のcleanup）。
- 照合チェックポイント（`master-data-settings-ui-ux-concept.md`規範6点）:
  1. §3.4 「active tenantを静かに示す／1件はlabel・複数はサーバー選択肢のswitcher／自由入力禁止」 — **適合**（実装どおり）。
  2. §3.4 「切替時に未保存変更があれば保存・破棄・取消を選ばせ、確定後に文書等を破棄・再取得」 — **適合**（dialogの三択＋cleanup一覧）。
  3. §3.4 「切替確認中やbackend未確認の間、旧tenantの本文と新tenantの管理UIを同時に表示しない」 — **要確認**（照合観点）。
  4. §3.4 「role名/group名から操作可否を推測せず、backend返却のcapabilityと理由コードで表示」 — **適合**（`availableTenants`のみ消費）。
  5. §3.5 「表示名重複に備え、switcher optionと確認dialogにopaque IDを補助表示」 — **候補所見（未描画）**。現状は`displayName`のみで、opaque ID補助表示がない。
  6. §3.5 「未保存有無に関わらず『このブラウザの他のタブも切り替わる』を文字で示す」 — **候補所見（clean切替で告知が出ない）**。確認dialogは`isDirty`時のみ開くため、clean切替では多タブ告知が表示されない。
- 注記: §3.5はADR-0061でImplementation gated。候補所見5・6は意図的な先送りの可能性があるため、**確定欠陥ではなく照合で要否を確認する観点**として扱う（人間/Maintainerの判断対象）。
- 期待成果物: 上記6点の✓/△/✗照合。5・6は「意図的先送り」か「要修正」かの判断を明記。
- 受入条件: 概念設計との乖離が✓/△/✗で記録され、△/✗はissue化（またはADR-0061ゲート項目への追記）されること。
- スコープ境界: 有効化可否（runtime profile）は**論点にしない**。F-2（Admin/Platform面）は実装が存在しないため対象外。

## 3. 前版からの解決確認（区分C該当分）

| # | 論点 | 解決状況 |
| --- | --- | --- |
| C-1 | キャンバス選択ロールとメニュー内フォームの構造 | 解決済み（2026-07-13、ADR-0052 Accepted、UI-QUALITY-A11Y-03で実装） |
| C-2 | 診断バンドルの生成・プレビュー・コピー/ダウンロードUI | 判断済み（2026-07-13、ADR-0053 Accepted、PRODUCT-OPS-02で実装） |
| C-5 | 作業モードタブへのrole=tablist導入要否 | 解決済み（2026-07-15、ADR-0055 Accepted、UX-NAV-02で検証済み） |

上記3件は前版の区分Cから除外済み。区分D（メモ機能/research⇄businessモード/VUI/レンズヒント、リアルタイム共同編集）は方針変更なく維持。

## 4. 推奨する次の一手

1. **N-1/N-2（プロトタイプ2面の事後設計照合）を最優先で1件の依頼にまとめる**。両者とも「Round 6宣言後に無審査で本番バンドルへ同梱された常設タブ（二重ゲート・既定非表示）」という同型の問題であり、実機スクリーンショット＋自己申告チェックリストを添えて✓/△/✗レビューを依頼する形が、A-1で確立済みの体制と整合する。N-1は視覚言語からの逸脱と計測器混入、N-2はエクスポートのSafeMode非適用と破壊的操作の説明可能性を、それぞれ論点の中心に据える。N-5・N-6はそれぞれN-2・N-1に統合済み。
2. **N-4（B-1: 作業モードタブ内部の照合）は要求不要で照合のみのため、次回照合ラウンドで独立して並行消化できる**。実装側の準備（自己申告チェックリスト作成）だけで着手可能。
3. **F-1（tenant session制御群の設計照合）はADR実装ゲートの成立を待たずに今すぐ着手できる**。有効化条件（runtime profile）とは無関係に、既存の既定OFF実装を`master-data-settings-ui-ux-concept.md`の規範6点と照合する。特に候補所見2点（opaque ID補助表示・多タブ切替告知）の要否判断を得る。ゲート成立後にF-2（Admin/Platform面）へ進む前段として位置づける。
4. **N-3/N-7（A-1、A-2/A-3）は、ドッグフード摩擦記録と束ねて次の新規デザイン要求ラウンド（Round 9相当）の主題候補として保持する**。N-7は`UI-QUALITY-A11Y-07`のfocus復帰判断と連動させる。
5. F-3〜F-6（外部連携・visual cue拡張）は、それぞれの明記されたゲート（運用実績・ADR採択）が成立するまで依頼を起こさない。

## Traceability

- Related: `02_Architecture/design/design-request-gaps-2026-07.md`（前版、2026-07-11）
- Related: `02_Architecture/design/ui_design_handoff.md`（受け渡し境界の正本。dialog Escape/focus復帰・可逆/不可逆・SafeMode表示・amber予約・人間/AI文脈分離の規範。a11yの詳細水準はADR-0044と`design-qa-checklist.md`へ委譲）
- Related: `02_Architecture/design/design-request-2026-07-round3.md` 〜 `round8.md`
- Related: `02_Architecture/design/design-qa-checklist.md`（第1〜8回照合記録。4軸 A.視覚言語/B.状態遷移/C.核の保護/D.a11y・契約と✓/△/✗規約の正本）
- Related: `02_Architecture/design/master-data-settings-ui-ux-concept.md`（F-1照合の規範元。§3.4/§3.5/§4/§6）
- Related: `04_Documentation/ui_catalog.md`
- Related: `01_Plans/dogfood/dogfood-log-2026-07-10.md`（N-7の再開導線摩擦）
- Related: 実装（origin/main `2c452dce`）: `03_Implement/frontend/src/ui/{RepresentativeVisualCuePrototypePanel,InquiryJourneyPrototypePanel,AgentTaskExportPanel,AgentResponseImportPanel,TenantSessionControl,TenantChangeConfirmationDialog}.tsx`
- Related: `01_Plans/adr/ADR-0044`, `ADR-0048`, `ADR-0052`, `ADR-0053`, `ADR-0055`, `ADR-0059`, `ADR-0060`, `ADR-0061`
- Related issues: `issue-DOMAIN-VISUAL-CUE-01`, `issue-DOMAIN-W-ITERATION-01`, `issue-SAAS-TENANT-01`, `issue-EXT-CONN-02`, `issue-EXT-CONN-03`, `issue-EXT-CONN-04`, `issue-UI-QUALITY-A11Y-07`
