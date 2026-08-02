# Issue: DOMAIN-VISUAL-CUE-01 島・情報集合の代表視覚手掛かり

- Type: Feature request / UX / AI / Data governance
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex / Maintainer
- Scope: `00_Prompt/representative_visual_cue_requirements.md`, `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`, `01_Plans/adr/ADR-0060-representative-visual-cue-source-boundary.md`, `02_Architecture/architecture.md`, `02_Architecture/representative_visual_cue_evaluation.md`, `02_Architecture/data_model_operations_overview.md`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/export/`, `03_Implement/frontend/src/import/`
- Related Backlog: `DOMAIN-VISUAL-CUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0060-representative-visual-cue-source-boundary.md`, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`, `00_Prompt/representative_visual_cue_requirements.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-VISUAL-CUE-01
- RequirementStatement: 島または利用者が選んだ情報集合に、内容を代表する任意の小さな視覚手掛かりを文字と併記し、意味を早く確定したり他者へ暗黙に伝えたりせず、目的のまとまりを見つけ直す負担を下げる。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=利用者が多数の島を含む文書を開いている / 操作=島を選び、手描き・基本図形・撮影写真・絵文字・プリセット・権利確認済み外部素材・生成候補から任意の手掛かりを確認して採用する / 期待結果=表札と手掛かりを併用して島を見つけ直せ、画像なしへ戻せ、一次資料と識別画像を区別でき、外部通信と権利条件を事前確認できる / 除外=自動分類、自動採用、画像だけの意味伝達、装飾目的の常設画像。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0060`

## 1) 課題 / Problem statement

島が増えると、利用者は表札を順に読んで目的のまとまりを探す必要がある。内容と関連する小さな絵文字や画像は再認識を助ける可能性があるが、装飾画像は注意を奪い、断定的な画像は曖昧さや対立を隠し得る。また、外部素材と生成画像は通信、権利、保存、共有の責任が異なる。

現状の設計は「画像生成（将来）」とだけ記載し、標準KJ法のシンボルマークや図解記号、写真KJ法、フィールド写真、簡易な手描き・汎用図形との連続性を扱っていない。また、目的、対象、各供給経路、SafeMode、権利表示、アクセシビリティ、削除を定義していない。

## 2) 提案する解決策 / Proposed solution

- 正本要件 `00_Prompt/representative_visual_cue_requirements.md` に、視覚手掛かりを表札・本文・根拠の代替ではない任意の再認識補助として定義する。
- 供給経路を A: 手描き/基本図形/利用者画像、B: Unicode絵文字/同梱プリセット、C: 権利確認済み外部素材、D: proposal-only画像生成に分離する。
- Phase 1では、紙のシンボルマークや写真ラベルから自然に移れる通信不要の作成・選択・解除・非表示を検証し、既定画面と既存操作を変えない。
- B/Cは、外部通信前確認、SafeMode、出所・ライセンス・生成来歴、共有前確認、削除を実装条件とする。
- 画像なしとの比較で再発見の時間・見誤り・主観的負担が改善または非悪化であることを確認する。
- 視覚キューの意匠は `02_Architecture/design/kj-atlas 拡張提案.dc.html` P37（代表視覚キューを視覚言語内で成立させる）の設計レビュー回答に基づく。単色slate線画（塗りなし・1.5px・currentColor=slate-500）を本文左20×20固定スロットに限定し、型/保持/確認/根拠の4チャネルと色相で競合させない。キューは想起補助であり意味・優先度・感情を担わせず、色分類やランク付けへ転用しない。供給候補はキュレート済みslate線画セット（場所・人・時間・数・問い・引用等の抽象ピクトグラム）とローカル写真（グレースケール寄りの中立枠）に限り、自由絵文字入力は廃止する。既定は「なし」でスロット非描画（初期表示の純増ゼロ）とし、LOD遠景では非表示にする。
- カードスキーマに任意フィールド `cue`（アイコンIDまたはローカル画像参照）を追加する。既存スキーマの拡張範囲内であり、本文左スロットの条件描画は `02_Architecture/design/kj-atlas プロトタイプ.dc.html` に試作済み。
- 予備操作パネルの5段階評価は反スコアリング方針に反するため製品面から全廃する。試行時間・誤答数は集計・平均・正答率・ランキングを出さない「試行ログ」（キューを選んだ／変えた、という事実の時系列記録）に読み替え、ユーザビリティ計測が必要な場合は製品タブに混ぜず明示的な調査モード（別ビルド/フラグ、被験者告知）へ分離する。

### 複雑性予算

初期表示の常設要素を増やさず、島または選択集合の詳細から一段深く開く。画像なしを既定として維持し、外部素材と生成画像は高度機能でのみ提示する。

## 3) 受入条件 / Acceptance criteria

- [x] AC-1: 目的、対象、非目標、表札・本文・根拠との意味境界が要件に定義されている。
- [x] AC-2: 絵文字、同梱プリセット、外部素材、生成画像が別経路として比較されている。
- [x] AC-3: SafeMode、外部通信前確認、権利・出所、生成来歴、共有・削除の要件が定義されている。
- [x] AC-4: 代替テキスト、文字との併記、非表示、固定寸法、キーボード操作の要件が定義されている。
- [x] AC-4a: 手描きシンボル、基本図形、写真ラベル、フィールド写真、図解記号との連続性と意味の違いが定義されている。
- [x] AC-5: `ADR-0060` の供給経路、許容ライセンス、保存境界が受理されている。→ ADR-0060 Accepted（2026-07-20）。T5（emoji比較）+ T6（保存候補比較）により受理条件を充足。
- [ ] AC-6: Phase 0 fixtureで、画像なし・手描き・基本図形・撮影写真・絵文字・プリセットの再発見時間、見誤り、主観的負担を比較している。
- [x] AC-7: Phase 1のオフライン選択をマウス、キーボード、390px、スクリーンリーダー相当で検証している。
- [ ] AC-8: 外部素材を導入する場合、原典確認、クレジット、キャッシュ、削除、API停止をintegration/e2eで検証している。
- [ ] AC-9: 生成画像を導入する場合、明示送信、proposal-only、SafeMode、provider固定、来歴をintegration/e2eで検証している。
- [x] AC-10: 代表規模でレイアウト移動、メモリ、保存容量、読み込み時間が予算内である。

## 4) タスク / Tasks

- [x] T1 認知負荷、関連画像と装飾画像、画像・文字の再認記憶に関する研究を確認する。
- [x] T1a 標準KJ法のシンボルマーク・図解化、写真KJ法、フィールド写真、紙とペンを保つデジタル支援を調査する。
- [x] T2 要件正本、ドメイン語彙、AI原則、価値トレーサビリティを同期する。
- [x] T3 供給経路と未決定の保存・権利境界を `ADR-0060` として提案する。
- [x] T4a 具体・抽象・対立・機微情報・記号衝突を含み、手描き印・基本図形・写真ラベル・一次視覚資料を区別するPhase 0の機械可読fixtureと評価手順を固定する。
- [x] T4a-1 VC-S3用に人物・識別情報・実在組織名を含まない合成写真fixtureと生成・権利確認メタデータを用意し、実際の観察証拠ではないことを明示する。
- [x] T4b C0からC4の非製品プロトタイプ表示を作り、実装担当者による予備操作確認を実施する。高度な作業モード内のセッション限定UIとして実装し、マウス、キーボード、390px、ローカル画像通信をE2Eで確認した。代表利用者による効果比較はAC-6として未完了のまま残す。
- [x] T5 Unicode絵文字と固定画像セットについて、OS間表示、アクセシビリティ、ライセンス、配布容量を比較する。→ `02_Architecture/design/unicode_emoji_os_comparison.md` として完了（2026-07-20）。推奨: Unicode絵文字をPhase 1既定とし、OS間不一致が確認されたcueだけを個別SVG化する。
- [x] T6 採用参照、権利情報、画像本体、サムネイルの保存候補を比較し、ADRを受理または更新する。→ `02_Architecture/design/representative_visual_cue/storage_candidate_comparison.md` に比較完了（2026-07-20）。ADR-0060 Accepted・§8保存決定反映・`data_model_operations_overview.md` 更新済み。
- [ ] T7 Phase 1を、手描き/基本図形、利用者画像切り抜き、絵文字/プリセットの小さなPRへ分割して実装し、E2Eと実画面評価を行う。→ 小PR 1件目（契約先行の型・往復保持・SafeMode）完了（2026-07-29）。小PR 2件目（基本図形の選択UI・20×20描画・保存・Undo・390px・a11y）完了（2026-08-02）。小PR 3件目（手描き入力・scope分離IndexedDB・4KB上限・再読込・Undo期間後の削除）完了（2026-08-02、`82b173eb`）。小PR 4件目（手描きassetのreview pack明示同梱・integrity・別browser復元・旧store移行）完了（2026-08-02、`04827403`）。小PR 5件目（利用者画像の端末内切り抜き・48×48 PNG化・16KB/scope保存・原本非保持・review pack既定除外/明示移送）完了（2026-08-02、`c5ac22f0`）。小PR 6件目（300カード・30島のレイアウト・応答性・メモリ・保存容量回帰）完了（2026-08-02）。代表利用者による比較評価（AC-6）は未完了のまま残る。
- [ ] T8 実利用で不足が確認された場合だけ、外部素材と生成画像をそれぞれ別issueへ分割する。
- [x] T9 現行`Island.imageUrl`の自動外部取得とレビュー自動昇格を`SEC-VISUAL-ASSET-01`へ分離し、SafeModeで遮断する。

## 5) 検証計画 / Validation plan

- 要件段階: `python 01_Plans/issues/validate_active_issue_memos.py`、`python -m unittest 01_Plans.issues.tests.test_validate_active_issue_memos`、`python 01_Plans/docs_check.py`
- 実装段階: frontend unit test、Playwright E2E、Chrome実画面、代表規模性能計測、外部provider契約test。
- UX評価: `02_Architecture/representative_visual_cue_evaluation.md` と `02_Architecture/design/representative_visual_cue/phase0_scenarios.json` を用い、同じ目的の島を探す課題を文字のみ・手描き・基本図形・写真・絵文字/プリセットで比較する。時間、誤選択、意味誤認、原資料遡及、主観的負担を記録し、見栄えや利用時間だけでは採択しない。
- 予備操作証跡: `03_Implement/frontend/src/ui/RepresentativeVisualCuePrototypePanel.tsx`、`03_Implement/frontend/src/domain/representative_visual_cue_prototype.test.ts`、`03_Implement/frontend/e2e/representative_visual_cue_prototype.spec.ts`。結果はセッション内だけに保持し、文書スキーマ、外部provider、利用者評価結果を構成しない。
- Stop条件: 関連性を説明できない候補、画像だけによる意味伝達、意図しない外部通信、権利情報欠落、SafeMode回避、初期表示の複雑化のいずれかを確認した場合は実装を昇格しない。

### Phase 1 基本図形UIチェックポイント（2026-08-02）

- 高度UIで島を選択した場合だけ、一段深い詳細として4種の中立的な基本図形（円・三角形・ひし形・平行線）を表示する。既定は未設定で、通常UIの初期表示差分は0。
- 採用した図形は `Island.representativeCue` に `preset_svg` として保存し、島表札の左へ20×20の単色線画で併記する。画像だけで意味を伝えず、キャンバス上の図形は装飾扱いとして表札の読み上げを重複させない。
- 選択、代替テキスト編集、解除、Undo、PUT保存往復を実装した。空の代替テキストはUIから確定できず、最大80文字とした。readOnlyでは変更操作を無効化する。
- E2Eで Advanced UI OFF時の非表示、キーボード選択、390pxの横見切れなし、axe違反0、外部request 0、解除後Undo、保存payloadを確認した。既存の視覚手掛かり評価prototypeと旧式島画像のSafeMode遮断も含め4件成功。
- frontend全回帰は228ファイル / 1327テスト成功。typecheck、production build、docs-checkも成功。390px実画面を目視し、図形・ラベル・代替テキスト欄に横方向の見切れがないことを確認した。
- このチェックポイントは通信不要の基本図形だけを製品経路へ昇格する。外部素材、生成AI、写真、第三者SVG、手描きバイナリ保存を暗黙に有効化しない。

### Phase 1 手描きIndexedDBチェックポイント（2026-08-02）

- 高度UIの代表視覚手掛かり内へ、20×20座標系の単色自由線入力を追加した。Pointer Eventsでマウス・ペン・タッチを同じ境界に載せ、矢印キーとSpace/Enterで描画開始・移動・停止できる代替操作、一画戻す、全消去、明示採用を備える。採用前は文書を変更しない。
- 手描き本体はversion 1の座標列としてstrict validationし、未知キー、非整数・範囲外座標、空の画、64画超・512点超、UTF-8 JSON 4KB超を拒否する。`DocumentV1`には不透明な`imageRef`と代替テキストだけを保存し、外部通信・Base64埋め込み・自動採用は行わない。
- IndexedDBレコードはlocal scopeまたは`deployment + tenantId + principalId`で分離し、別scopeの参照を解決しない。表示キャッシュもscopeと`imageRef`の両方が一致する場合だけ描画し、tenant切替時の旧scope表示を防ぐ。
- 解除・変更・島削除のUndoを成立させるため、文書履歴のpast/present/futureが参照中のassetは保持する。全履歴から参照が外れた時点で同一document/scopeの不要assetを削除し、監査情報として残さない。文書変更が拒否された場合は先行保存したassetを削除し、参照だけ／本体だけの不整合を残さない。
- 390px Chromium E2Eで、ポインターとキーボード描画、4KB/scopeレコード、採用、20×20表示、PUT保存、再読込、解除、Undo、履歴終了後のIndexedDB削除、横見切れなし、axe違反0を確認した。基本図形を含む対象2件、frontend全230ファイル / 1,342テスト、typecheck、production build、Playwright通常構成196 passed / SaaS専用3 skipped、docs-check、active issue validator、diff-checkを通過した。
- 実装は`82b173eb`。Document JSONだけを別端末へ移した場合は画像本体を復元できないため、手描きassetのbundle同梱/import復元は未完了と明記する。利用者画像、絵文字、代表利用者による効果比較もT7/AC-6〜10に残す。

### Phase 1 手描きreview pack移送チェックポイント（2026-08-02）

- 手描き本体はreview packへ既定で含めず、共有用`document.json`から`hand_drawn`参照も除去する。利用者が件数と機微情報警告を確認して一回限りの明示opt-inを行った場合だけ、参照と本体を同梱する。プリセット等の自己完結した手掛かりは既定動作を維持する。
- opt-in時は`representative_visual_cue_assets.json`を出力し、SafeMode投影後の文書IDと全`imageRef`の完全一致、重複なし、strict asset schema、400件/2MBの上限を検証する。asset欠落や参照不一致ではexportを中止し、`bundle_manifest.json`へversion/countを記録し、`integrity.json`のhash対象へ加える。
- importは整合性検証と文書・assetの完全一致検証を先に行い、現在のbrowser storage scopeへ単一IndexedDB transactionで全件復元する。復元に失敗した場合は文書を取り込まない。asset fileがない旧packやDocument JSON単体ではdanglingな手描き参照を除去し、画像本体があると誤認させない。
- IndexedDBは`scopeKey + imageRef`の複合キーを持つv2 storeへ移行し、別scopeの同一`imageRef`を衝突させない。Chromiumで旧v1 storeからの移行と、送信側とは独立したfresh browser contextへのreview pack取込・描画復元を確認した。
- frontend全233ファイル / 1,372テスト、typecheck、production build、Playwright通常構成198 passed / SaaS専用3 skipped、docs-check、active issue validator、diff-checkを通過した。実装は`04827403`。
- T7は完了扱いにしない。利用者画像、絵文字比較、代表利用者による効果比較、代表規模性能計測（AC-6〜AC-10）が残る。

### Phase 1 利用者画像切り抜きチェックポイント（2026-08-02）

- 高度UIの代表視覚手掛かり内へ、PNG/JPEG/WebP（10MB以下・各辺8000px以下）の端末内切り抜きを追加した。横位置・縦位置・拡大はラベル付きrange操作としてキーボードでも調整でき、明示採用までは文書を変更しない。
- 選択した原本はobject URLでブラウザ内だけに読み、保持・送信しない。採用時は正方形へ切り抜き、減彩した48×48 PNGの複製だけをscope分離IndexedDBへ保存する。1件16KBを上限とし、文書には`user_image`の不透明な`imageRef`と代替テキストだけを保持する。
- 保存・import時はcanonical Base64、PNG signature、IHDR寸法・方式・先頭位置、chunk型・CRC、IDAT存在、IEND終端とブラウザ画像decodeをstrict validationする。文書参照のkindとasset kindが一致しないbundleも拒否する。表示時もscope・`imageRef`・kindがすべて一致する場合だけdata URLとして描画する。
- review packでは手描きと利用者画像を「端末内の視覚手掛かり」として同じ境界で扱い、参照と本体を既定除外する。件数と機微情報警告を確認した一回限りの明示opt-in時だけ、文書参照と完全一致するintegrity対象asset fileへ同梱する。asset fileなしのimportではdanglingな`user_image`参照を除去する。
- Chromium 390px E2Eで、画像選択、キーボード切り抜き調整、採用、48×48/16KB PNG保存、原本と保存物の不一致、外部request 0、PUT保存を確認した。基本図形・手描き・review pack移送を含む対象5件、frontend全233ファイル / 1,378テスト、typecheck、production build、docs-check、active issue validator、diff-checkを通過した。
- T7は完了扱いにしない。絵文字比較、代表利用者による効果比較、代表規模性能計測（AC-6〜AC-10）が残る。外部素材・生成画像は実利用で不足が確認された場合だけT8で別issue化する。

### Phase 1 代表規模性能チェックポイント（2026-08-02）

- ADR-0046 PB-1の代表規模（300カード・30島）へ、同梱プリセット10件、手描き10件、利用者画像切り抜き10件を割り当てる専用Playwright回帰を追加した。Portable assetはlocal scopeのIndexedDBへ格納し、通常の非同期解決・描画経路を通す。
- asset未格納時と格納後の再読込で、30島すべての境界座標・寸法が完全一致することを固定した。手掛かりの非同期解決が島配置を移動させないため、要件AC-9のレイアウト移動境界を満たす。
- 単独Chromium 3回連続実測は、初期操作可能859〜1,155ms、可視範囲の手描き・画像asset描画完了509〜645ms、検索応答86〜173ms、最大長時間タスク78〜112ms、ヒープ増分396,972〜412,240 bytes、Portable asset 20件合計5,650 bytes・手描き最大116 bytes・画像最大451 bytesだった。回帰上限は操作可能2.5秒、検索1秒、長時間タスク150ms、ヒープ増分64MiB、asset合計200KiB、手描き1件4KiB、画像1件16KiBとし、実測JSONをPlaywright attachmentへ残す。
- 既存Phase 1 E2Eがマウス、キーボード、390px、axeによるスクリーンリーダー相当、外部request 0を既に検証し、今回の代表規模でも初期表示と検索が予算内だったためAC-7とAC-10を完了とする。
- 性能予算: 代表規模での主要操作=不変（視覚手掛かり解決の前後で島境界不変、操作可能2.5秒以内） / メインスレッド100ms超の同期処理=単独3回で最大112ms、4 worker並列で137ms、退行上限150ms以内。100ms設計目標を超えた場合はartifactへ値を残し、150ms超をworker化または描画分割の判断ゲートとする。
- T7は完了扱いにしない。実装担当者の操作・性能確認を代表利用者による効果比較へ読み替えず、AC-6だけを次の実使用評価として残す。外部素材・生成画像は実利用で不足が確認された場合だけT8で別issue化する。

## 6) 依存関係 / Dependencies

- `01_Plans/adr/ADR-0060-representative-visual-cue-source-boundary.md`
- `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
- `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`
- `01_Plans/issues/issue-SEC-VISUAL-ASSET-01-legacy-island-image-safe-mode.md`

## 7) ADR判定

ADRが必要。画像の意味、供給経路、外部通信、権利、保存、共有の境界は複数モジュールと公開物へ影響し、UIだけの局所判断ではないため `ADR-0060` で提案する。ADR受理前は、要件とfixture検証を進められるが、永続スキーマや外部providerを固定しない。
