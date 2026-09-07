# 認知dogfood ナビゲーション索引

- Status: Maintainer/operator navigation only
- Date: 2026-09-06
- Scope: cognitive dogfood / product-value validation workstream
- Arm input: **No** — この文書をCase 001〜003のA/B/C/Dへ渡さない。

## 1. この索引の役割

認知dogfoodに関する文書が増えたため、「意思決定の正本」「実行条件」「回顧監査」「実験入力」「実行結果」を混同しないための導線を示す。

この文書自体は新しい判断を定義しない。文書間に矛盾がある場合は、次の優先順位で正本へ戻る。

1. 長期的な判断: ADR。
2. 実行課題と受入条件: Issueメモ。
3. ケースの問いと比較条件: ケース契約、事前登録、凍結記録。
4. 各実行の事実: 生の成果物、実行記録、KJ Atlas InquiryJourney。
5. 本索引: 導線のみを示す。

## 2. 現在地

- P0: **完了**。
  - Case 001〜003の問い、製品スナップショット、スキルスナップショット、A〜Dそれぞれに適用する条件、必須出力を凍結済み。
  - 起動条件の同等性、製品資料manifestとblob、製品資料一式の再生成、スキル正本のblob一致を検証済み。
  - freeze Run #29でCase 001〜003のA〜D、計12件の独立したActions artifactを生成済み。2026-09-06の再確認時点では12件とも`expired=false`で、2026-09-13 06:17Z前後まで保持される。
  - 2026-09-02のcommit `066544c62d6639d3d46c28fefe5ce20f57373a21` で常設GitHub Actions workflow群はmainから意図的に削除済みであり、現在mainから同じartifactを常設workflowで再生成できる、という意味ではない。
  - 成果物の境界は、全条件に同一ケースの製品証拠、B/Dだけにスキル、C/Dだけに空の開始文書、各成果物には自条件の `launch.md` だけを含める。
- P1: **Case 001 Arm C 実行可能 / 生の実行記録は未取得**。
  - 実行順は C → D → B → A。
  - Run #29の`cognitive-dogfood-case-001-arm-c`（artifact id `9727586537`、digest `sha256:c5964b6d1654c8e19b7961aca893f4a1fb98d5db896573c6819f57dc805a23f5`）を2026-09-06に実ZIPで再確認した。
  - Arm C artifactには専用`launch.md`、frozen product bundle 20資料、空の`starter.json`だけが入り、skill subtreeはない。`launch.md`もfrozen product commit、外部Web検索禁止、cultural-substrate-weaving不使用を維持するため、既存artifactからfresh-context実走を開始できる。
  - 現在の設計者チャットは既知仮説を含むため、比較条件として使わない。
  - R10で、現在不足している主なものは比較設計・ハーネス・製品スキーマではなく、比較設計の既知情報から隔離された新規コンテキストと、C/Dでの実際のUI操作だと再確認した。
  - 生の実行記録を得る前に、新しい事前検証、KPI、実験スキーマを増やして実行の代替にしない。
- P2以降: 未開始。
- 第三者価値実証: **手順一式は準備済み / 検証セッションは未実施**。
  - `VALUE-REALNESS-01` はP0かつOpenのまま。
  - 実行計画、参加者向け説明、開始前チェックリスト、セッション記録、公開境界、事前分析計画、検証スクリプトは準備済み。
  - 準備時には専用workflowも存在したが、認知dogfoodと同様に2026-09-02のActions停止で現行mainから削除されている。手順一式の準備済み状態と、現在の常設workflow有無を混同しない。
  - 現在残る主要な外部入力は、第三者協力者または同等の外部評価機会と、その文脈で扱える資料である。
  - 手順一式が準備済みであることを、価値実証の完了とはみなさない。

## 3. 最初に読む文書

### 全体の順序

- `cognitive-dogfood-execution-plan.md`
  - P0〜P6の順序と終了条件。
- `cognitive-dogfood-case-portfolio-preregistration.md`
  - Case 001〜003を結果を見る前に選んだ理由と横断評価。
- `cognitive-dogfood-case-portfolio-freeze.md`
  - 実行入力の凍結状態、実行前補正、凍結時のCI検証記録、現在のartifact実行導線。

### 評価方法

- `../issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md`
  - A〜Dの4条件とM1〜M9。
- `cognitive-dogfood-run-record-template.md`
  - 各実行の共通記録。
- `cognitive-dogfood-blind-review-protocol.md`
- `cognitive-dogfood-blind-review-template.md`
  - BR1、BR2、条件開示の順序。

### KJ Atlasの操作

- `cognitive-dogfood-cd-ui-runbook.md`
  - C/Dで共通して用いるUI操作の正本。
- `../issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md`
  - InquiryJourney Phase 2の手動中核とT9。

## 4. Case 000 — 回顧監査であり対照実験ではない

- `cognitive-dogfood-case-000-r1-r5-audit.md`
  - R1〜R5を探索的なCase 0として監査。
- `cognitive-dogfood-case-000-outcome-trace.md`
  - 代表論点が後続Issue、ADR、実装へどう変換されたかを追跡。
- `doc_kj_atlas_dogfood_r1.json` 〜 `doc_kj_atlas_dogfood_r5.json`
  - 元資料。Case 001の各比較条件に答えとして渡さない。

Case 000から認知的優位性の因果関係を主張しない。比較対照、AI提案の採否記録、独立した新規コンテキストという条件を持たないためである。

### 継続dogfood — 日常開発の自己分析

Case 001〜003の統制比較とは別に、既知の設計判断を含む日常開発の自己分析を継続dogfoodとして扱う。これらも比較条件への入力にはしない。

- `cognitive-dogfood-continuous-2026-09-02.md`
  - R7。外部AIが長期的な共同思考へ参加するときの接続・受け渡し上の摩擦を分析した、最初の継続dogfood記録。
- `doc_kj_atlas_dogfood_r7.json`
  - R7のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-02-r2.md`
  - R8。最初の10分と一次利用仕事のずれを分析し、公開用パック、導入手順、同期テストへ戻した記録。
- `doc_kj_atlas_dogfood_r8.json`
  - R8のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-02-r3.md`
  - R9。第三者価値実証が何を待っているのかを分析し、手順準備済みと外部セッション未実施を分離した記録。
- `doc_kj_atlas_dogfood_r9.json`
  - R9のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-02-r4.md`
  - R10。認知比較実験が何を待っているのかを分析し、実験準備済みと有効な生の実行記録が未取得であることを分離した記録。
- `doc_kj_atlas_dogfood_r10.json`
  - R10のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-03.md`
  - R11。一次利用仕事が未完課題の優先順位を実際に分けられるかを検証した記録。
- `cognitive-dogfood-continuous-2026-09-03-r5.md`
  - R11。公開ROADMAPと実装・価値検証の正本を照合し、完了済み機能を実装済み基盤へ戻して、現在の焦点を認知比較評価と第三者価値実証へ合わせた記録。
- `doc_kj_atlas_dogfood_r11.json`
  - R11のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-03-r6.md`
  - R12。一次利用仕事から未完課題を見直し、人間が残した意味をAI入力で落とさない `AI-IR-PROJECTION-01` をP1で継続する優先順位判断へ戻した記録。
- `doc_kj_atlas_dogfood_r12.json`
  - R12のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-03-r7.md`
  - R13。LLM入力IRの経路棚卸しが手作業へ戻っていたことを分析し、IR移行済み経路とStage 5残債をCI上の明示的な被覆契約へ変えた記録。
- `doc_kj_atlas_dogfood_r13.json`
  - R13のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-03-r8.md`
  - R14。継続dogfoodの記録と索引に時間差が生じていたことを分析し、存在する記録へ戻る導線をdocs contractで守るようにした記録。
- `doc_kj_atlas_dogfood_r14.json`
  - R14のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-03-r9.md`
  - R15。route別の最終prompt計測からevidenceの `20→0` をrenderer欠落と判定した記録。この判定はR16で仕様へ戻って補正したが、測定値と判断経路を追跡するため記録自体は残す。
- `doc_kj_atlas_dogfood_r15.json`
  - R15のKJキャンバス。R16で反証された推論を含む履歴資料として残す。
- `cognitive-dogfood-continuous-2026-09-03-r10.md`
  - R16。R15の測定値は保持したまま、「IRにある全情報を全routeへ描画する」という暗黙前提を撤回し、coverageをrouteごとの必要意味集合で判定するよう補正した記録。
- `doc_kj_atlas_dogfood_r16.json`
  - R16のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-03-r11.md`
  - R17。route固有の必要意味を正本から対応づけ、`detect-contradiction` のfocus pairに対するhuman adjudicationが300枚切り詰めで消え得ること、narrative/groups/layoutに未測定の必要意味軸が残ることを分離した記録。
- `doc_kj_atlas_dogfood_r17.json`
  - R17のKJキャンバス。
- `cognitive-dogfood-continuous-2026-09-04.md`
  - R18。意味保存型mergeの実装済み利用経路を横断照合し、backendのremote提案契約とfrontendの決定論fallback契約が混線して正常なprovider応答を拒否し得ることを発見・修正した記録。
- `doc_kj_atlas_dogfood_r18.json`
  - R18のKJキャンバス。既存testが誤った契約前提を非退行条件として固定し得ること、Done-at-rootの計画legacy差、merge方式の追跡性を別の残差として保持する。
- `cognitive-dogfood-continuous-2026-09-04-r19.md`
  - R19。promptが04ステップ型／核融合法型を選ばせながら方式をreview契約で失っていたことを分析し、`near_duplicate | kernel_fusion` をproposal・decisionの独立した意味属性として確定した記録。
- `doc_kj_atlas_dogfood_r19.json`
  - R19のKJキャンバス。AI理由・人間理由・方式を分離し、新規記録は厳格、旧記録は推測しない境界を保持する。
- `cognitive-dogfood-continuous-2026-09-04-r20.md`
  - R20。R19の契約をbackend provider、frontend decoder、決定論fallback、UI、人間の採否、Document decisionへ通し、欠落・未知値・後方互換の回帰契約を追加した記録。
- `doc_kj_atlas_dogfood_r20.json`
  - R20のKJキャンバス。方式の意味が利用経路のどこでも落ちないことと、formal Case・第三者価値実証・scale課題を別境界として残すことを示す。
- `cognitive-dogfood-continuous-2026-09-04-r21.md`
  - R21。8月27日のformal product snapshotと9月4日のcurrent mainを混同せず、元比較の内的妥当性と現在mainへの移送妥当性を二段階へ分離した記録。C/D runtimeも既存freeze契約どおり固定product commitを使うことをoperator手順へ戻す。
- `doc_kj_atlas_dogfood_r21.json`
  - R21のKJキャンバス。commit距離と意味ドリフトを分け、元portfolioを書き換えず後段のcurrent-state replicationで現在性を確かめる構造を保持する。
- `cognitive-dogfood-continuous-2026-09-04-r22.md`
  - R22。古いbranch一般を禁止せず、merge-baseからcurrent mainとbranchの状態反転候補をmerge前に絞る診断へ変換した記録。既知path guard、path-level診断、typecheck/test・人間reviewの役割を分離する。
- `doc_kj_atlas_dogfood_r22.json`
  - R22のKJキャンバス。workflow・Issue lifecycle・frontend sourceで再現したstale state再流入を束ね、commit距離ではなく状態の向きが逆転する場所を見る構造を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r23.md`
  - R23。R22のpre-merge stale-state診断が#2902/#2961/#2971の異種PRで再利用されたことを確認し、運用上の生存と実事故の検出実績を分離した記録。後続runはすべてstrong=0のため、required check化を先回りしない。
- `doc_kj_atlas_dogfood_r23.json`
  - R23のKJキャンバス。作成→再利用→検出の三段階を分け、positive hitまたはfalse positiveの実例が得られるまでoptional診断として使い続ける境界を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r24.md`
  - R24。PR #2994で露呈したplanning unittest baseline failureを追い、同じ旧Issue root pathでもcurrent参照とfrozen product commit上のhistorical coordinateでは意味が異なることを分離した記録。manifestを書き換えず、構造化された凍結座標だけをguardで狭く認識する。
- `doc_kj_atlas_dogfood_r24.json`
  - R24のKJキャンバス。文字列一致だけのguardとsnapshot identityの衝突を整理し、blanket exemptionではなく固定manifest・commit・path+blobShaから意味を判別する構造を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r25.md`
  - R25。PR #3001でCase 002 frozen manifestのAI-ROUTE pathがcurrent done/へ実際に追随した再発を分析し、historical-coordinate例外の認識とfrozen manifest自身のimmutabilityを別契約として分離した記録。
- `doc_kj_atlas_dogfood_r25.json`
  - R25のKJキャンバス。R24のlive-reference guard、履歴不要のmanifest blob identity guard、既存full-history path/blob validatorを三層に分け、current lifecycleとsnapshot identityを同時に守る構造を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r26.md`
  - R26。R25のfull planning runが、success済みone-shot workflowの退役漏れをstale current referenceとして実際に検出した記録。run成功とexecution assetのretirementを別の完了条件として分離する。
- `doc_kj_atlas_dogfood_r26.json`
  - R26のKJキャンバス。実証済み退役対象だけをexact pathで閉じ、temporary one-shot一般を一括禁止せず、R22 stale-merge diagnosticのrequired化とも原因クラスを分ける。
- `cognitive-dogfood-continuous-2026-09-06-r27.md`
  - R27。R26のfull planning runが、実参照の消滅後もhistorical exception allow-listに5件が残っていたことを逆向きの陽性として検出した記録。例外を追加時だけでなく不要時にも縮退させる。
- `doc_kj_atlas_dogfood_r27.json`
  - R27のKJキャンバス。`observed == expected`の対称性により、未承認参照の増加とstale exception残存の両方をfailさせ、ENV-ARCHの実在1件だけを残す構造を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r28.md`
  - R28。PR #3011で、Architecture索引が正本上Done済みのQA-E2E-SAAS-01をDraftと表示し続けた実docs driftを分析し、navigationが別正本の可変lifecycle/decision stateを複製して第二正本にならない境界へ戻した記録。
- `doc_kj_atlas_dogfood_r28.json`
  - R28のKJキャンバス。索引はtopic・ID・関係・正本への導線を持てる一方、current state authorityは各正本へ戻し、一例だけで状態語一般を禁止するguardへ飛躍しない構造を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r29.md`
  - R29。PR #3003で実装default 50,000に対して公開registry/configurationが10,000のまま残った実driftと、#3014でkey existenceからdefault値の意味一致へcontractを引き上げた経路を分析した記録。
- `doc_kj_atlas_dogfood_r29.json`
  - R29のKJキャンバス。契約項目の存在と意味値一致を分け、静的に安全に読めるdefaultだけを照合し、R28の「複製をやめる」境界とは別に「必要な複製は意味まで守る」構造を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r30.md`
  - R30。PR #3016/#3017で、Backend settings表とCompose配送面に同じpublic keyの重複宣言が実在したことを分析し、必要な層間複製と同一authority/delivery surface内の宣言一意性を分離した記録。
- `doc_kj_atlas_dogfood_r30.json`
  - R30のKJキャンバス。R28の不要な複製を持たない、R29の必要な複製は意味一致を守る、R30の各層内部では宣言点を一意にする、という三段の境界を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r31.md`
  - R31。PR #3019/#3021で、same-origin pathというcomponent意味境界と、標準Compose/Nginx topologyで実現できる値集合が別契約だったことを分析した記録。
- `doc_kj_atlas_dogfood_r31.json`
  - R31のKJキャンバス。component-level semantic validityとdeployment-profile realizabilityを二段に分け、packaged profileの制約をcomponent一般能力へ逆輸入しない構造を保持する。
- `cognitive-dogfood-continuous-2026-09-06-r32.md`
  - R32。PR #3022でWindows CRLF working treeがfrozen manifest破損に見えたfalse positiveを分析し、immutabilityの観測点をraw bytesからGit clean filter後のcanonical blob identityへ戻した記録。
- `doc_kj_atlas_dogfood_r32.json`
  - R32のKJキャンバス。LF/CRLFというplatform表現差は同一Git objectへ正規化しつつ、historical pathのsemantic rewriteは別identityとして拒否し、R25のfrozen-input責務を維持する構造を保持する。
- `cognitive-dogfood-continuous-2026-09-07-r33.md`
  - R33。PR #3026/#3027で、APP_REVISIONのcanonical意味driftと、canonical値がstructured logへ届かない観測surface欠落を分析し、意味一致と必要surfaceへの伝播を別coverageとして分離した記録。
- `doc_kj_atlas_dogfood_r33.json`
  - R33のKJキャンバス。同じkeyの存在・default一致・canonical意味一致・必要観測surfaceへの伝播を段階的に分け、APP_REVISIONの明示済みbuild同定用途だけを閉じて全設定値のlog出力へ一般化しない構造を保持する。
- `cognitive-dogfood-continuous-2026-09-07-r34.md`
  - R34。PR #3030〜#3033で、Compose配送集合・public enum集合・resolver wiring状態・ADR実装前提という異なるshapeのcurrent contractがそれぞれ実装とずれた実陽性を分析し、文書契約のshapeごとに実行可能な正本照合を選ぶ構造へ統合した記録。
- `doc_kj_atlas_dogfood_r34.json`
  - R34のKJキャンバス。scalar/default、finite enum、delivery surface、wiring state、ADR factual premiseを一種類の文字列guardで扱わず、消せる第二正本は消し、残す必要があるcurrent factだけをshape-awareなconformanceへ戻す構造を保持する。
- `cognitive-dogfood-continuous-2026-09-07-r35.md`
  - R35。PR #3036で、DeepSeek thinking enumの意味集合は正しいままraw pipeがMarkdown table delimiterと衝突し、enum監査でcellが切断された実陽性を分析し、carrier integrityをsemantic conformanceの前段として分離した記録。
- `doc_kj_atlas_dogfood_r35.json`
  - R35のKJキャンバス。machine-checkedなcurrent-contract surfaceだけを対象に、表現を一意にparseできること→shape-awareな意味照合の順で守り、全Markdownをgeneric grammar化しない構造を保持する。
- `cognitive-dogfood-continuous-2026-09-07-r36.md`
  - R36。PR #3043/#3044で、session hash keyのlowercase/length/charsetとOAuth redirect URIの固定callback pathという、実装の受理predicateがpublic contractから欠けた実陽性を分析し、finite enumとは別のacceptance predicate / grammar shapeとして分離した記録。
- `doc_kj_atlas_dogfood_r36.json`
  - R36のKJキャンバス。carrier integrityを前提に、finite setとrejection-relevant predicateを分け、利用者がvalid inputを構成するために必要な最小制約だけをfocused contractへ戻す構造を保持する。
- `cognitive-dogfood-continuous-2026-09-07-r37.md`
  - R37。PR #3048〜#3050/#3052で、acceptedだがconsumerのないdead toggle、実効consumerの作用範囲過大表現、allowed valueとprofile上のrequired / recommended / conditionalの混同という実陽性を分析し、acceptanceの先にeffect binding / scope / operating conditionを分離した記録。
- `doc_kj_atlas_dogfood_r37.json`
  - R37のKJキャンバス。未定義behaviorを発明せずfail-fastへ縮める境界、consumer存在と作用範囲、設定可能性とprofile運用条件を分け、公開keyが約束する制御可能性・必須性とruntime正本を一致させる構造を保持する。
- `cognitive-dogfood-continuous-2026-09-07-r38.md`
  - R38。PR #3054で、clean DBの固定seed依存による受入false negativeと、frontend subtreeだけをtemporary copyしてrepository-relative fixtureを失ったharness偽失敗を分析し、acceptance invariantとfixture / setup / harness前提を分離した記録。
- `doc_kj_atlas_dogfood_r38.json`
  - R38のKJキャンバス。testが必要な最小状態を自ら構成してcontract上の不変条件を観測し、harnessは意味上必要なdependency closure / repository topologyを保持する一方、shared fixtureやtemporary directory自体は一律禁止しない構造を保持する。
- `cognitive-dogfood-continuous-2026-09-07-r39.md`
  - R39。PR #3063で、期待内容が正しく存在するのに非限定status locatorが別の正当なstatus surfaceまで拾って失敗したtest defectを分析し、DOM上の偶発的一意性とassertionが所有するsemantic surfaceを分離した記録。
- `doc_kj_atlas_dogfood_r39.json`
  - R39のKJキャンバス。role/testidの一般優先を決めず、locator scopeをassertionの意味境界へ合わせ、.first()やproduct surface削除でambiguityを隠さない構造を保持する。
- `cognitive-dogfood-continuous-2026-09-07-r40.md`
  - R40。PR #3072で、すでにmainへ適用済みのcloseout branchを再mergeし、PR diffは残るのに直前main→merge commitのchanged filesが0だった実陽性を分析し、merge-base差分とcurrent mainへのnet tree effectを分離した記録。
- `doc_kj_atlas_dogfood_r40.json`
  - R40のKJキャンバス。R22 strong inversionを維持したまま、prospective merge treeがbase treeと同一になるalready-applied deltaをreview signalとして分け、required checkへはまだ昇格しない構造を保持する。
- `ai-ir-required-semantic-coverage-map-2026-09-03.md`
  - R17で作成した、移行済み4 routeの必要意味・scale測定状況・未測定軸の対応表。

継続dogfoodで得た内部所見を、Case 001〜003の比較結果や第三者価値実証の代替証拠として扱わない。

## 5. Case 001 — 存在目的と一次利用仕事

### 問い・入力の正本

- `cognitive-dogfood-case-001-product-purpose.md`
- `cognitive-dogfood-case-001-round1-source-manifest.json`
- `cognitive-dogfood-case-001-skill-manifest.json`
- `cognitive-dogfood-case-001-contamination-exclusions.md`

### 起動用入力

- A: `cognitive-dogfood-case-001-launch-ordinary.md`
- B: `cognitive-dogfood-case-001-launch-skill.md`
- C: `cognitive-dogfood-case-001-launch-atlas.md`
- D: `cognitive-dogfood-case-001-launch-atlas-skill.md`

### C/Dの開始文書

- `doc_cognitive_case_001_starter.json`
  - `cards`、`islands`、`evidenceLinks`、`readingOrder`、`narratives` は空のまま開始する。

### Round 2

- `cognitive-dogfood-case-001-round2-external-manifest.md`
  - Round 1の結果を見る前に、外部比較資料を事前登録済み。

## 6. Case 002 / 003 — Case 001の結果に依存して選ばない

### Case 002: AI提案と人間判断の境界

- `cognitive-dogfood-case-002-ai-human-boundary.md`
- `cognitive-dogfood-case-002-round1-source-manifest.json`
- `doc_cognitive_case_002_starter.json`
- `cognitive-dogfood-case-002-launch-*.md`
- 生成済みActions artifact: `cognitive-dogfood-case-002-arm-a` 〜 `arm-d`

### Case 003: ローカル実行・自己ホストと共同作業の境界

- `cognitive-dogfood-case-003-local-collaboration-boundary.md`
- `cognitive-dogfood-case-003-round1-source-manifest.json`
- `doc_cognitive_case_003_starter.json`
- `cognitive-dogfood-case-003-launch-*.md`
- 生成済みActions artifact: `cognitive-dogfood-case-003-arm-a` 〜 `arm-d`

Case 002/003の成果物を先に生成していても、実行順はCase 001→002→003を維持する。成果物が準備済みであることは、前倒しで実行することを意味しない。

## 7. 実験用ツール

次のものはKJ Atlas本体の機能ではなく、比較条件を保つための実験ハーネスである。

- `validate_cognitive_launch_packets.py`
  - 固定した問い、必須出力、各条件の差が意図どおりかを、不整合時は失敗として確認する。
- `prepare_cognitive_frozen_source_bundle.py`
  - 製品スナップショットから、各条件に見せてよい製品証拠だけを抽出する。
- `prepare_cognitive_case001_skill_bundle.py`
  - B/D用の正本 `src/ja-JP` だけを抽出する。スキルスナップショットは3ケース共通。
- `validate_cognitive_arm_packages.py`
  - A〜Dへ製品資料、スキル、開始文書、起動用入力が意図した境界で入っているかを検査する。
- `validate_cognitive_run_records.py`
  - 生の実行記録に必須情報が揃っているかを検査する。
- `build_cognitive_blind_package.py`
  - 条件名や方法情報を外したブラインドレビュー用資料を生成する。
- （凍結時）`.github/workflows/cognitive-dogfood-freeze.yml`
  - 凍結入力の事前検証と、Case 001〜003のA〜D、計12件の新規セッション用artifact生成に使用した。2026-09-02のActions停止で現行mainから削除済み。

実験用ツールの不足を、そのままKJ Atlas製品の機能不足へ読み替えない。

## 8. 所見の振り分け

詳細は `cognitive-dogfood-execution-plan.md` のP4を正本とする。

- F0: 実行記録やカードとして保持する。
- F1: 既存Issueへ証拠を戻す。
- F2: 既存Issueで扱えず、かつ再現可能で実行可能な課題だけを新しいIssueメモにする。
- F3: `ADR-0047` の実使用トリガーを満たす場合だけADR候補とする。

とくにInquiryJourneyのAI支援候補は、Case 001〜003の少なくとも2ケースで同じ種類の手動摩擦が再現するまで、T9から先へ進めない。

## 9. 外部現実への接続

内部の認知dogfoodは、第三者にとっての価値を証明するものではない。

正本は次のとおりである。

- `../issues/issue-VALUE-REALNESS-01-third-party-beachhead-validation.md`
- `../issues/issue-PRODUCT-POSITION-01-primary-job-and-switch-reason.md`
- `../issues/issue-PRACTICE-CULTURE-01-cultural-fit-and-product-invariants.md`

第三者による検証を開始するときは、`VALUE-REALNESS-01` の「現在の実行準備状態」「現在残っている外部入力」「検証開始時の入口」から次へ進む。

- `third-party-value-validation-execution-plan.md`
- `third-party-value-participant-brief.md`
- `third-party-value-session-launch-checklist.md`
- `third-party-value-session-record-template.md`
- `third-party-value-publication-boundary.md`
- `third-party-value-analysis-plan.md`
- `validate_third_party_value_protocol.py`
- （準備時workflow。現行mainではActions停止）`.github/workflows/third-party-value-protocol.yml`

Case 001〜003で得た価値、切替理由、認知増分は、第三者が自分の実資料を持ち込んだときに、支持・修正・縮小・棄却される**仮説**として渡す。

手順一式が準備済みでも、第三者による検証セッションが未実施なら `VALUE-REALNESS-01` は完了しない。協力者がいない段階で新しいKPI、テレメトリ、重複した検証手順を増やし、実証の代わりにしない。

## 10. 変更境界

最初の有効なCase 001の生の実行記録を保存した後は、結果に合わせて次を変更しない。

- 固定した問い。
- Round 1の資料manifest。
- 製品スナップショットとスキルスナップショット。
- A/B/C/Dそれぞれに適用する条件。
- 必須出力。

実験を実行できない欠陥、破損、重大な安全上・権限上の理由がある場合は、旧条件を上書きせず、逸脱として履歴を残す。