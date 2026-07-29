# Issue: DOMAIN-W-ITERATION-01 W型累積KJ法の反復的探究支援

- Type: Feature request / UX / Domain model
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex / Maintainer
- Scope: `00_Prompt/w_type_iterative_inquiry_requirements.md`, `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`, `02_Architecture/inquiry_journey_model.md`, `02_Architecture/schemas.md`, `02_Architecture/data_model_operations_overview.md`, `03_Implement/frontend/src/domain/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/e2e/`
- Related Backlog: `DOMAIN-W-ITERATION-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`, `00_Prompt/w_type_iterative_inquiry_requirements.md`, `02_Architecture/inquiry_journey_model.md`, `00_Prompt/qualitative_card_quality_requirements.md`, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`, `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: DOMAIN-W-ITERATION-01
- RequirementStatement: 通常の一ラウンド利用を複雑にせず、高度な利用者がR1問題提起からR6手順化までのKJ法を反復・分岐し、中間成果、未解決点、現場への問い、カード系譜を失わず停止・再開できる探究支援を提供する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=利用者が複雑な課題について現状把握ラウンドを実施中 / 操作=中断し、追加取材を行い、同じ段階の2回目として再開し、本質追求後に新しい矛盾から現状把握へ分岐する / 期待結果=各時点のカード・配置・文章・未解決点が残り、前後差分と元情報を辿れ、AIなしでも引継ぎ・分岐できる / 除外=固定順ウィザード、進捗採点、プロジェクト管理、AI自動移行。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（`ADR-0057` Accepted）

## 1) 課題 / Problem statement

現行アプリは単一文書内のKJ法作業を支援するが、複数ラウンドを通して思考と経験を往復する探究単位を持たない。このため高度な実務では、利用者が文書複製、ファイル名、外部メモで次を管理する必要がある。

- どの段階で、何回目の検討か。
- 前のラウンドから何を持ち越したか。
- どの観察が仮説や問いを変えたか。
- 何を保留し、次に何を確かめるか。
- 後の知見から前へ戻ったとき、元の成果と新しい分岐をどう区別するか。

ファイル複製だけではカード系譜が切れ、単一文書の上書きでは思考の変化が失われる。反対に、6段階を常設すると通常利用の認知負荷が増える。

## 2) 背景 / Context

- 川喜田研究所は、狭義のKJ法一ラウンドと、その累積利用を区別している。
- 6ラウンドは、問題提起、現状把握、本質追求、構想計画、具体策、手順化という異なる姿勢を累積する。
- 累積型発想法のICT研究では、長時間を要することと、中断時の中間成果保持・円滑な再開が課題として挙げられている。
- 現行 `DocumentV1` は一つの現行スナップショットを保存し、ラウンド単位の不変成果、分岐、系譜を持たない。
- 現行UIには高度機能の段階的開示と作業モードがあるため、通常利用を変えずにプロトタイプを置く候補面は存在する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 可逆性、保留、人間判断を単一操作だけでなく長期探究へ拡張し、プロダクト価値「思考を雑にしない」を直接強化する。
- 安全（THREAT_MODEL / SafeMode）: ラウンド履歴は生データと過去の仮説を蓄積するため、部分共有、削除、AI入力の範囲を明示する必要がある。
- 企業・行政要件（enterprise_architecture）: 長期案件では説明可能性に有用だが、組織承認・担当者・期限は別境界とし、初期実装へ混ぜない。
- 後方互換（schemas）: `ADR-0057` は独立探究集約 + 不変成果DAGを採択した。`DocumentV1` へ履歴キーを追加せず、新契約は実装・移行・CRUDが揃うまで `L0: Planned` とする。

## 4) 提案する解決策 / Proposed solution

### Phase 0: 要件と操作模型

- 6ラウンド、反復、引継ぎ、分岐、再開の用語と不変条件を固定する。
- 固定fixtureを使い、永続化しない状態機械と低忠実度UIで代表シナリオを検証する。
- 通常利用時の初期表示差分0を確認する。

### Phase 1: 採択済み境界のfixture検証

- 独立 `InquiryJourneyV1`、不変 `RoundSnapshotV1`、親参照DAG、自己完結bundleを固定fixtureで表現する。
- 親グラフの循環、参照切れ、digest不一致、未知versionをfail-closedで拒否する純粋関数とunit testを作る。
- `RoundSnapshotV1` の意味状態、カード系譜、SafeMode派生bundle、容量を代表fixtureで検証する。

### Phase 2: 手動中核

- AIなしで、探究開始、ラウンド記録、引継ぎ、停止・再開、分岐、比較を実装する。
- 再開ブリーフは元カードへ移動できる導出表示とする。
- 現場への問いと、新規カードの応答関係を記録できる。

### Phase 3: proposal-only AI支援

- 段階別の問い、見落とした立場、引継ぎ、反証、差分の候補を追加する。
- AIなしの中核を維持し、採用前に状態を変更しない。

### 非目標

- 全利用者への6ラウンド強制。
- プロジェクト管理、担当者管理、日程最適化。
- ラウンド完了率や品質点数。
- AIによる自動移行・仮説決定。
- fixture・操作模型・通常利用非回帰の検証前にbackend永続化へ進むこと。

## 5) 受入条件 / Acceptance criteria

- [x] AC-1: 6ラウンド、反復番号、引継ぎ、分岐、再開、現場への問いが要件として定義されている。
- [x] AC-2: 固定ウィザード、進捗採点、通常画面への常設を禁止する境界が定義されている。
- [x] AC-2a: 独立探究 + 不変成果DAG + 自己完結bundleが採択され、現行 `DocumentV1` と分離されている。
- [x] AC-3: 高度機能OFFでは、初期表示とカード作成手順に変更がない。
- [x] AC-4: 既存文書から再入力なしで探究を開始できる。
- [x] AC-5: R2の1回目と2回目を別成果として保存・比較できる。
- [x] AC-6: R3からR2へ戻るとき、元成果を上書きせず分岐できる。
- [x] AC-6a: 分岐開始時のキャンバス復元と探究DAG追加を、一つの取り消し操作として整合して戻せる。
- [x] AC-7: 後続の仮説・方針・具体策から、元カード、ラウンド、出典を辿れる。
- [x] AC-8: 中断後の再開ブリーフから、問い、未解決点、次の行動、元成果へ移動できる。
- [x] AC-9: 引継ぎ確認を一件ずつ採用・修正・見送り・保留でき、未回答でも保存できる。
- [x] AC-10: `KJ_ATLAS_LLM_PROVIDER=none` で中核操作を完了できる。
- [x] AC-11: SafeMode、import strict validation、部分共有、履歴削除の境界が永続契約で定義される。→ `inquiry_journey_model.md` §4.4（SafeMode派生bundle契約）、§4.5（Import strict validation契約）、§4.6（部分共有契約）、§4.3（削除と保持）、§6 不変条件 8-10 として契約化済み（2026-07-20）。SafeMode適用結果のbundle内metadata（`InquiryExportInfoV1`）は型追加が未了のため、別途follow-upする。
- [x] AC-12: マウス・キーボード・390px・代表規模のE2Eが通る。
- [x] AC-13: 探究終了（破壊的操作）の確認は、A-1（エージェント連携）と同型の保存・破棄・取消の3択とし、SafeMode既定ONの継承と出典・文面のサニタイズを満たす。→ 2026-07-29チェックポイントで完了。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 W型問題解決モデル、6ラウンド累積KJ法、累積型発想法のICT支援課題を調査する。
- [x] T2 要件とADRを起票し、価値トレーサビリティへ接続する。
- [x] T3 代表fixtureとメモリ内状態機械を作り、段階・反復・分岐の語彙をunit testで固定する。
- [x] T4 高度機能内の低忠実度プロトタイプを作り、初期表示差分0と操作理解を確認する。
- [x] T5 広域比較を行い、`RoundSnapshotV1` の境界と採択方式を `ADR-0057` / `inquiry_journey_model.md` へ固定する。
- [x] T6 ADR受理後、型・validation・ローカル保存・import/export・roundtripを実装する。
- [x] T6a 自己完結bundleのローカルexport/import、strict validation、digest検証、roundtripを実装する。
- [x] T6b 現在文書から正式bundleを作り、画面からJSONファイルへ保存・再読込できるようにする。
- [x] T6c Phase 3のbackend永続化判断に必要な代表規模の容量・読込時間を計測する。
- [x] T7 手動中核UIとa11y/i18n/性能回帰を実装する。
- [x] T8 マウス・キーボード・390pxのE2Eとスクリーンショットを取得する。
- [ ] T9 Phase 2の実使用後に、AI支援を別issueへ分割するか判断する。
- [ ] T10 Claude Design（外部レビュー、2026-07-21 P35）の指摘を踏まえ、探究終了確認をAC-13の3択へ改修し、常設タブ化時のメニュー分類（P29確定6分類：ファイル/編集/カード/表示/作業/共有）内の配置は実機照合時に決定する（新規7分類は作らない＝CB-1）。→ 3択への改修（AC-13本体）は2026-07-29チェックポイントで完了。常設タブ化時のメニュー配置は未着手のまま残す（プロトタイプ内の高度機能タブのまま。実機照合＝Claude Design側の判断待ち）。

### Phase 0 実装証跡（2026-07-15）

- `src/domain/inquiry_journey.ts`: `DocumentV1` へ履歴を追加せず、`InquiryJourneyV1`、`RoundSnapshotV1`、`RoundHandoffV1`、`CardLineageEdgeV1`、自己完結bundle型を独立定義した。
- `src/domain/inquiry_journey.fixture.ts`: R2現状把握、R3本質追求、追加観察後のR2・2回目という代表loopbackを固定した。観察から仮説への系譜は `derived` とし、本文編集と分離した。
- `src/domain/inquiry_journey.test.ts`: DAG循環、経路上の反復番号、複数head、出発成果、参照切れ、将来成果の逆参照、digest、系譜方向・多重度、非working成果を検証する。
- `appendRoundRecord()`: 親成果を確認し、同段階の反復番号を選択経路から導出し、過去成果を変更せず分岐先端を追加するメモリ内状態遷移を実装した。
- 検証結果: 対象16 tests passed、frontend typecheck passed、frontend全体191 files / 1050 tests passed、issue validator 6 memos / unittest 11 tests passed。
- 永続化、import parser、UIは未実装であり、support levelは引き続き `L0: Planned` とする。

### T4 低忠実度UI検証（2026-07-18）

- 高度機能の作業モードへ「探究」タブを追加した。高度機能OFFでは試作UIをDOMへ描画せず、通常の初期画面と中核操作を変更しない。
- 試作UIは現在の文書名とカード件数を起点として表示し、追加フォームなしで探究を開始できる。6段階は固定順のウィザードではなく、任意に選び直せる選択肢とした。
- 記録はセッション内だけに保持し、「保存されません」と明示する。`DocumentV1`、`InquiryJourneyV1`、API、保存形式は変更していない。
- Playwrightで、高度機能OFF時の非表示、本文だけのカード作成・保存が従来どおり完了すること、キーボードによる試作開始、R2・1回目 → R3・1回目 → R2・2回目の表示が上書きされず別項目になることを確認した。これによりT4とAC-3を完了とした。
- 試作開始と表示上の反復分離によりAC-4/5の操作模型は確認できたが、探究manifestと成果snapshotを保存・再読込・比較できないためAC-4/5は未完了のままにする。親参照を伴う分岐、永続化、比較表示、再開ブリーフはT6〜T8に残す。support levelは引き続き `L0: Planned` とする。

### T6a ローカルbundle往復（2026-07-18）

- `src/domain/inquiry_bundle_io.ts` に、元bundleを変更せずschema versionと内容由来digestを付与するexport、JSONのstrict import、自己完結参照検証を実装した。
- importは未知キー・未知version・未知enum・不正型・参照切れ・循環・digest不一致をfail-closedで拒否する。snapshot内の`DocumentV1`は既存の`validateDocumentV1Strict()`を再利用し、検証規則を二重化しない。
- digestはキー順に依存しないcanonical JSONからSHA-256を計算する。bundleを識別情報や秘匿性の代用には使わず、snapshot内容の破損検知だけに用いる。
- unit testで自己完結往復、元データ非変更、未知キー、未知enum、未知version、参照切れ、改変後digest、JSON破損、キー順の決定性を確認した。
- T6a完了時点ではローカルI/O境界だけであり、画面からの保存・読込、backend API、保持・削除、SafeMode派生bundle、容量計測は未実装だった。画面からの保存・読込は後続のT6bで実装し、その他は引き続き未完了とする。

### T6b 画面からの保存・再開（2026-07-18）

- 試作パネルの簡易配列を正式な`InquiryBundleV1`へ置き換え、現在の`DocumentV1`から追加入力なしで探究と起点snapshotを作成するようにした。
- ラウンド記録時に現在文書を新しい不変snapshotとして残し、選択経路上の同段階反復番号を導出する。同じカードIDの本文差分から`carried`/`edited`、追加・消失から`new`/`retired`系譜を自動作成し、利用者へ追加入力を求めない。
- 画面からJSONファイルを保存し、同じ起点文書を開いた状態でstrict importして再開できる。別文書を起点とするファイルは取り込まず、起点文書を開くよう案内する。自動保存ではないことを常時表示する。
- exportにもstrict shape検証を追加し、「保存できるが再取込できない」成果物を生成しない。JSONで省略される`undefined`任意項目は保存後表現からdigestを計算し、ブラウザと再取込後で一致させる。
- Playwrightで通常利用時の非表示、キーボード開始、R2→R3→R2反復、ファイル保存、終了、再取込、履歴復元、390px幅での操作表示を確認した。Chrome相当の実画面でも390px時の横スクロールがないことを確認した。
- これによりAC-4とT6/T6bを完了とする。比較表示がないためAC-5、SafeMode派生共有と保持・削除がないためAC-11、代表規模の画面操作を含む包括E2EがないためAC-12は未完了のままとする。support levelは`L0: Planned`を維持する。

### T6c 代表規模の容量・読込性能（2026-07-19）

- 300カード・30島・6ラウンドを代表規模とし、1成果、探究manifest、自己完結bundle、12/18ラウンドまでの容量増加をPlaywrightで計測した。
- 再実行時の実測は、1成果73,955 bytes、manifest 2,161 bytes、6ラウンドbundle 1,460,390 bytes、18ラウンドbundle 4,110,050 bytesだった。いずれも5 MiBの警告境界内である。
- serialize 109ms、parse 72.56ms、画面取込1,253.86ms、最大長時間タスク94msで、2.5秒のI/O上限、並列CI向け150ms退行上限、単独実行時100ms設計目標を満たした。
- `inquiry_bundle_capacity_budget.spec.ts` は計測値をartifactへ添付し、容量、I/O時間、長時間タスク、過大ファイル拒否、取込取消、履歴件数を継続検証する。これによりT6cを完了とする。

### AC-5 ラウンド比較（2026-07-18）

- 同じ段階の反復を含む任意の2ラウンドについて、それぞれの不変な出力snapshotを既存の文書差分エンジンで比較する読取専用要約を実装した。
- 比較結果はカード、島、関係要約の変化件数と読み順の変更有無だけを示す。増減や変更を品質点数、改善率、推奨として扱わない。
- 高度機能内で直近2ラウンドを既定選択し、ラベル付き選択欄から比較元・比較先を変更できる。選択変更は`aria-live`で通知し、マウスとキーボードのどちらでも同じ結果へ到達できる。
- unit testで差分集計、元snapshotの非変更、存在しないラウンドのfail-closedを確認した。Playwrightで同じR2の1回目・2回目を取り込み、既定比較とHome/Endキーによる切替を確認した。
- これによりAC-5を完了とする。詳細差分、分岐作成、引継ぎ、再開ブリーフはAC-6以降として残し、比較UIへ混在させない。

### AC-6 過去成果からの分岐（2026-07-18）

- 「次の記録の起点」で任意の過去ラウンドを選べるようにし、既定先端以外を選んだ場合は、元成果と現在の分岐を変更しないことを操作前に表示する。
- 分岐時は親IDだけを過去へ向けない。選択ラウンドの不変な出力snapshotをキャンバスへ復元し、その同じ内容を新しい分岐の最初の成果として記録する。これにより、系譜上の親と実際の編集起点を一致させる。
- キャンバス復元は既存の`applyDocumentChange()`を通すため、通常の文書変更と同じ履歴境界で扱う。探究snapshot自体は変更せず、新しいsnapshotと親参照だけを追加する。
- 反復番号の事前表示と記録時の計算を`nextRoundIteration()`へ統一し、全履歴件数ではなく選択した祖先経路上の同段階反復から算出する。
- unit testで、R2→R3の後にR2から分岐するとR3先端とR2・2回目の先端が両方残ること、元snapshotが不変であること、存在しない親を拒否することを確認した。
- 390pxのPlaywright E2Eで、キーボードによる起点・段階選択、注意表示、R2・2回目の作成、保存後bundleの2先端、親参照、復元内容を確認した。これによりAC-6を完了とする。
- 派生課題: 現行の`Ctrl+Z`は`applyDocumentChange()`によるキャンバス復元だけを戻し、試作パネル内のDAG追加は戻さない。誤った系譜は作らず、画面上の探究全体を保存せず閉じる退避はできるが、製品化時の自然な取り消しには不足する。bundle状態をAppの履歴トランザクションへ統合するか、分岐取消操作を設けるかをT7で比較し、AC-6aとして検証する。新しい永続契約の判断が必要になった場合だけADRを再起票する。

### AC-6a 分岐の一括取消（2026-07-19）

- 分岐作成後、復元したキャンバスへ別の編集を加える前に限り「この分岐を取り消す」を表示する。通常の`Ctrl+Z`へ試作bundleの状態を暗黙結合せず、分岐作成という複合操作に対応する明示的な取消とした。
- 一回の操作で、App履歴の最新キャンバス復元を破棄し、探究bundleを分岐前へ戻す。履歴のfutureも残さないため、redoでキャンバスだけが再復元される不整合を作らない。
- 390pxのPlaywright E2Eで、キーボード作成した分岐を取り消し、履歴が3件から2件へ戻ること、redoが無効であること、再保存bundleに分岐headが残らないことを確認した。ja/en翻訳カタログ整合とtypecheckも通過した。
- 永続schemaや共有境界は変更していないため、新しいADRは不要と判断し、これによりAC-6aを完了とする。

### AC-7 カード系譜と出典の確認（2026-07-19）

- 既存の`CardLineageEdgeV1`を逆向きに探索し、選択カードから`carried`、`edited`、`derived`、`split`、`merged`の元カードを再帰的に辿る読取専用projectionを実装した。複数経路で同じカードへ達した場合は`snapshotId + cardId`で重複を除く。
- 高度機能の探究パネルに、通常は閉じた「カードの由来を確認」を追加した。現在の分岐先端にあるカードを選ぶと、選択本文、元カード本文、所有ラウンドと反復番号、記録済みの`Card.meta.source`だけを表示する。出典がない場合は補完や推測をしない。
- unit testで`derived`の複数入力と、その先の`carried`祖先、存在しないカードのfail-closedを確認した。390pxのPlaywright E2Eで、キーボードによる詳細欄の展開、2世代の祖先、ラウンド、出典の表示と横切れがないことを確認した。
- 既存bundleの読取専用projectionであり永続schemaを変更しないため、新しいADRは不要と判断し、これによりAC-7を完了とする。

### AC-8 再開ブリーフ（2026-07-19）

- 現在の分岐先端にある`RoundRecordV1`と`RoundHandoffV1`から、段階と反復番号、問い、理解の変化、未解決の問い、現場確認依頼を次の行動として組み立てる読取専用projectionを実装した。記録がない項目は補完や推測をせず表示しない。
- 親ラウンドの出力snapshotを前回成果として示す。最初のラウンドでは起点snapshotを示す。ボタンをキーボードで実行すると同じパネル内の読取専用成果へフォーカスを移し、カード本文と記録済み出典を確認できる。キャンバス、通常履歴、探究DAGは変更しない。
- unit testで代表bundleの投影、入力非変更、存在しないラウンドのfail-closedを確認した。390pxのPlaywright E2Eで、キーボードによる展開と成果表示、フォーカス移動、問いから次の行動までの表示、横切れがないことを確認した。
- 既存bundleの読取専用projectionであり永続schemaや共有境界を変更しないため、新しいADRは不要と判断し、これによりAC-8を完了とする。

### AC-9/10/12 手動引継ぎと操作回帰（2026-07-19）

- 出力snapshotのカード、島、文章、関係要約と、既存`RoundHandoffV1`の参照から、引継ぎ候補を決定論的に導出する。候補は一件だけ表示し、成果参照は採用・保留・見送り、理解の変化・未解決の問い・現場への問いはこのまま採用・修正して採用・見送りできる。未解決の問いと現場への問いは追加でき、すべてを入力必須にしない。
- 画面上の候補位置・編集中テキスト・未回答状態はview stateのままとし、永続契約を拡張しない。保存時は人が採用した値だけを既存`RoundHandoffV1`へ投影し、保留成果は`heldRefs`へ分離する。未回答候補は保存対象から除外してラウンドを`paused`のまま残し、すべて回答した場合だけ`handed_off`とする。
- 保存処理は元bundleと不変snapshotを変更せず、新しいbundleのラウンド・manifest更新時刻と引継ぎだけを更新する。存在しない成果参照は既存の自己完結bundle検証でfail-closedにし、import/exportのstrict roundtripを維持した。
- 高度機能の探究タブ内に通常は閉じた「次への引継ぎを確認」を追加した。候補決定後は次の一件へ移り、前の候補にも戻れる。未回答でも保存できることを明示し、部分保存後も再開を遮断しない。通常画面とAI提案の権限境界は変更していない。
- unit testで候補導出、採用・保留・見送り・修正、未回答の部分保存、完全回答時の状態遷移、snapshot非変更、不正参照拒否、strict JSON往復を確認した。frontend全215 files / 1,237 tests、typecheck、ja/enカタログ整合が通過した。
- 390pxのPlaywright E2Eで、キーボード採用、マウス保留、文章修正、見送り、未回答を残した保存、ダウンロード後のstrict再読込、snapshot非変更、横切れがないことを確認した。実ブラウザでもviewport 390px、文書scroll幅390px、引継ぎ欄scroll幅=client幅357pxを確認した。
- `KJ_ATLAS_LLM_PROVIDER=none`を明示し、backend/AI providerが利用できない状態で、300カード・30島・6ラウンドの代表bundle E2Eを完了した。1成果73,955 bytes、bundle 1,460,390 bytes、UI import 549.54msで既定上限内だった。既存の比較・再開・系譜・分岐取消E2Eと今回の引継ぎE2Eも同時に通過したため、AC-9、AC-10、AC-12、T7、T8を完了とする。

### AC-11 部分範囲の派生保存チェックポイント（2026-07-19）

- 選択ラウンドとその全祖先、起点snapshot、各ラウンドの入出力snapshot、対象範囲を説明する系譜だけを複製し、元bundleを変更しない自己完結projectionを実装した。派生bundleは選択ラウンドを唯一の先端として既存の`InquiryBundleV1`検証とstrict export/importを通し、内容に対応するdigestを再計算する。
- 対象ラウンドの引継ぎ・現場回答が範囲外snapshotを参照する場合や、`split`系譜の一部だけが範囲内になる場合は、参照を黙って落としたり別分岐を暗黙に追加したりせずfail-closedとする。画面では別ラウンドまたは探究全体を選ぶよう案内する。
- 高度機能の探究タブに「保存する範囲」を追加し、探究全体または任意ラウンドまでを明示して選べるようにした。部分範囲は共有物ではなくローカル保存用の派生ファイルとして扱い、SafeMode本文マスクが未適用であることと、他者へ渡す前に内容確認が必要であることを常時表示する。
- unit testで祖先・snapshot・系譜の閉包、元bundle非変更、strict往復、不正bundle、範囲外引継ぎ、境界をまたぐ分割系譜の拒否を確認した。390pxのPlaywright E2Eで部分ファイルと全体ファイルの連続保存・再読込・元探究非変更を確認し、実ブラウザでは保存範囲欄の`clientWidth=scrollWidth=357px`、文書幅390pxで横スクロールがないことを確認した。
- このチェックポイントでは永続schemaを拡張せず、共有範囲やSafeMode結果をmanifestへ記録していない。SafeMode派生bundle、保持・履歴削除の永続境界も未実装のため、AC-11は未完了のままとし、support levelは`L0: Planned`を維持する。

### AC-11 SafeMode派生bundleのドメイン境界チェックポイント（2026-07-19）

- `InquiryBundleV1`を外部利用向けに派生するSafeMode projectionをドメイン層へ追加した。元bundleをstrict export検証してから、探究タイトル・ラウンドテーマ・引継ぎ・現場確認、各snapshotのカード・島・文章・関係要約・批評・履歴・監査補助の自由記述を既存`SafeModePolicy`で伏字化し、画像URL、出典、主体参照、元署名を除外する。任意JSONを含む再提案差分と相関用signatureを含む矛盾判断は、内容を安全に列挙できないため集合単位で除外する。
- ID、参照、ラウンドDAG、カード系譜、時刻、採用・保留・人手レビュー状態は保持し、`human_reviewed`を派生処理が新たに設定しない。未知edge typeは表示時と同じ`related`へ安全側に正規化する。派生後に全snapshot digestを再計算し、自己完結参照とstrict import/exportを再検証する。元bundleは変更しない。
- 永続型の主要オブジェクトごとに全フィールドの扱いを型で列挙した。将来フィールドが追加された場合はSafeMode方針を明示するまでtypecheckを失敗させ、未知フィールドを含む入力も派生前のstrict validationでfail-closedにする。
- unit testで自由記述、URL、署名、主体参照、任意JSON payloadが派生物へ残らないこと、構造と人手レビュー状態の維持、元bundle非変更、digest再計算、strict roundtrip、未知フィールド拒否を確認した。
- `safeModeApplied: true`は現時点では関数結果だけに返し、永続bundleへ記録しない。共有範囲とSafeMode適用結果を受信側でも確認できる契約version、保持・履歴削除、テナント境界が未決定のため、画面に「安全な共有」として公開せず、AC-11とsupport levelは引き続き未完了の`L0: Planned`とする。

### AC-13 探究終了の3択確認（2026-07-29）

- `InquiryEndConfirmationDialog.tsx`を新設し、A-1（`TenantChangeConfirmationDialog`、SAAS-TENANT-01 F-1）と同一のalertdialogパターン（`role="alertdialog"`、取消への初期focus、Escape=取消、Tabフォーカストラップ、処理中は3操作を無効化しaria-liveで告知）で、探究終了を保存/破棄/取消の3択へ改修した。従来の2択（`role="group"`、終了/続ける）を置き換えた。
- ダイアログは動的コンテンツを一切補間しない静的文言のみで構成し、SafeMode既定ONの継承をラウンド・カード本文の露出なしという構造で満たす（テストで`t(...)`呼び出しが第二引数を取らないことを固定）。
- `handleExport()`を`Promise<boolean>`へ変更し、「保存」選択時はexportが実際に成功した場合のみ画面上の探究をクリアする。exportが失敗した場合はエラーメッセージを表示したままダイアログを開いたままにし、失敗時に黙って破棄しない。
- unit test 5件（alertdialog契約、処理中の3操作無効化とaria-live、日本語/英語の文言、フォーカス/Escapeの実装確認、動的コンテンツ非補間の確認）、E2E `inquiry_end_confirmation.spec.ts` 2件（キーボードでのフォーカス管理・Escape取消・discard、保存→ダウンロード確認後のクリア）を追加し、Chromiumで実行して確認した。既存のinquiry系E2E 4件（round comparison, handoff review, partial export, capacity budget）に回帰がないことも確認した。
- 検証: frontend typecheck pass、対象unit test 5件・既存i18nテストスイート含め全pass、Playwright新規2件・既存4件全pass。T10の3択改修部分はこれで完了。常設タブ化時のメニュー配置は別途Claude Design実機照合待ちとして残す。

## 7) 検証計画 / Validation plan

- 要件段階:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans.issues.tests.test_validate_active_issue_memos`
  - `rg -n "DOMAIN-W-ITERATION-01|ADR-0057|WIR-" AGENTS.md 00_Prompt 01_Plans 02_Architecture`
- 実装段階:
  - `cd 03_Implement/frontend && npm run typecheck && npm test`
  - `cd 03_Implement/frontend && npx playwright test e2e/w_type_iterative_inquiry.spec.ts`
- 期待結果:
  - 採択済み設計目標と未実装の現行契約が混同されない。
  - 実装後は通常利用非回帰、停止・再開、反復、分岐、系譜、SafeModeを再現できる。
- 未実施時の理由・代替検証:
  - backend永続化前に固定fixtureとメモリ内プロトタイプで操作・複雑性を検証し、通常利用非回帰が確認できない場合はPhase 2へ進まない。

## 8) 代替案 / Alternatives considered

- 代替案A: R1からR6の固定ウィザード。
  - 不採用理由: W型の経験と思考の往復、同段階反復、前段階への差し戻しを表現できない。
- 代替案B: カードへラウンドタグだけを付ける。
  - 不採用理由: 中間成果、引継ぎ、問いの変化、分岐、再開を扱えない。
- 代替案C: 利用者が文書を手動複製する。
  - 不採用理由: 系譜と差分が切れ、長期再開時の負担が高い。
- 代替案D: 最初から組織承認と工程管理を導入する。
  - 不採用理由: KJ法の思考支援を越え、個人OSS段階の過剰ガバナンスになる。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 6段階が利用者を急かす、履歴が重くなる、同じカードの正本が分岐で曖昧になる、過去の生データが共有物へ漏れる。
- 影響範囲: domain型、validation、保存、import/export、SafeMode、作業モード、Canvas、SidePanel、性能。
- ロールバック手順: 永続化前はプロトタイプを削除し、採択済み要件・設計を `L0` のまま残す。永続化後は高度機能を無効化して現行文書表示へ戻し、独立探究成果物を読み込まなくても既存 `DocumentV1` のカード・配置が読める契約を必須とする。

## 10) Additional context

### 確定した設計判断

1. `RoundSnapshotV1` は、選択状態等を除き、意味のある空間配置を含む `DocumentV1` 成果を再現できる内容とする。
2. `DocumentV1` optional構造ではなく、独立 `InquiryJourneyV1` + 不変成果DAGを採用する。
3. 分岐後のカードは、スナップショット内の再現可能な内容、安定ID、明示的な `CardLineageEdgeV1` で表現する。
4. ラウンド単位共有は、対象が参照する祖先成果をbundle内へ同梱し、参照が閉じた状態だけを受理する。
5. 容量上限・圧縮閾値・削除UIは設計判断ではなく代表fixtureによる計測値としてPhase 1・2で決める。

### 複雑性予算（ADR-0043 自己申告）

初期表示への純増=0 / コアツールバーの操作追加=0 / 高度機能内の現在位置=1行 / 全履歴=要求時のみ / 保留操作=引継ぎ内1操作 / 破壊的巻き戻し=禁止。

### 性能予算（ADR-0046 自己申告）

通常時はラウンド履歴を読み込まず、代表規模のキャンバス操作へ追加計算を入れない。履歴比較・再開ブリーフが100msを超える場合は待機表示またはworker化の判定対象にする。

## Traceability

- Requirements: `00_Prompt/w_type_iterative_inquiry_requirements.md`
- Accepted decision: `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`
- Architecture: `02_Architecture/inquiry_journey_model.md`
- Card quality: `00_Prompt/qualitative_card_quality_requirements.md`
- Value coverage: `02_Architecture/value_traceability.md`
- Derived-from: 2026-07-15 ユーザー指摘「KJ法は6ラウンドのW型進行に見られるように、高度実務ではイテレーションで思考を深める」
