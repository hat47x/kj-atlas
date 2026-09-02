# Issue: COGNITIVE-EVAL-01 KJ Atlasとcultural-substrate-weavingの認知増分を比較測定する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer
- Scope: `01_Plans/dogfood/`, `01_Plans/issues/`
- Related ADR/Spec: `ADR-0032`, `ADR-0042`, `ADR-0047`, `ADR-0057`, `00_Prompt/kj_technique.md`, `COGNITIVE-DOGFOOD-01`, `DOMAIN-W-ITERATION-01`, `02_Architecture/api.md`
- External method: `hat47x/cultural-substrate-weaving`
- Expected verification level: docs-check

## 課題

- 現在の問題:
  - 「生成AIを使うと認知能力が上がる」「KJ Atlasを使うと深く考えられる」「文化的体系を併用すると視野が広がる」という表現は、そのままでは検証不能である。
  - AI出力の長さ、論点数、流暢さ、利用者の好感度は、認知成果の質と一致しない。むしろ自動化バイアスや認知オフロードにより、見かけ上の生産性と判断品質が逆転する可能性がある。
  - KJ Atlasと `cultural-substrate-weaving` を同時に導入すると、どちらが効いたのか、相互作用があるのかを分離できない。
  - 評価のために新しい履歴・proposal監査schemaを作ると、実験instrumentationが製品契約を不必要に膨らませる。KJ Atlasには既に長期探究用InquiryJourneyとAI proposal auditがあるため、製品状態と実験記録を分けて再利用する必要がある。
- 利用者または開発への影響:
  - 測定系がなければ、dogfoodの成功体験が自己強化され、プロダクト/スキル双方の過大評価につながる。
  - 実験都合のschemaを製品へ混ぜると、認知dogfoodを続けるほど本体が研究装置化し、一般利用の複雑性を増やす逆効果が起こり得る。

## 基本仮説

「高度な認知能力」を単一スコアとして扱わず、**人間とAIの認知系が、探索・注意・記憶・推論・根拠評価・反証・停止をどれだけ適切に制御できるか**へ分解する。

本issueでは、最終的な能力向上を次の形で操作的に定義する。

> 同一の開いた課題に対して、重要な根拠・異論・空白を保持したまま、より多くの生存所見を発見し、誤ったAI提案への依存を減らし、後から再検証・訂正できる成果へ変換できること。

## 比較設計

同一課題・同一ソーススナップショットを使い、可能な範囲で次の4条件を比較する。

| Arm | 外部表象 | cultural-substrate-weaving | 目的 |
|---|---|---|---|
| A | 通常チャット/文書 | なし | 基準線 |
| B | 通常チャット/文書 | あり | スキル単体の増分 |
| C | KJ Atlasキャンバス | なし | キャンバス/KJ外部表象の増分 |
| D | KJ Atlasキャンバス | あり | 組合せと相互作用 |

必要な代表ケースでは、人間のみ/AIなしの参照条件を追加してもよいが、常時必須にはしない。

### 比較の汚染防止

- 各armは独立コンテキストで開始し、他armの中間成果を見せない。
- ソース資料の版と問いを固定する。
- 順序効果を減らすため、実行順はケースごとに入れ替える。
- 最終成果の評価は可能な範囲でarm名を隠して行う。
- 一つのarmで発見した新資料を他armへ追加する場合は、追加後の比較ラウンドとして全armへ同条件で与える。

## 製品状態と実験instrumentationの分離

### 長期探究状態

C/Dでは、製品上の再訪・分岐・意味上の節目は既存 `InquiryJourneyV1 / RoundSnapshotV1 / RoundHandoffV1 / CardLineageEdgeV1` を使う。認知dogfood専用の履歴schemaは作らない。

A/Bでは同じ製品機能を使えないため、比較再現に必要な版付きraw artifactを実験ディレクトリへ保存する。

`experiment Round 1 / Round 2` は資料投入フェーズであり、W型 `RoundStage` と同じ概念ではない。C/Dでstageを変えるかは、実験フェーズではなく人間が意味上の探究段階をどう判断したかで決める。

### AI提案と人間判断

KJ Atlas C/Dで正式AI proposal APIを使用した場合、製品側には既存契約を使用する。

- proposal生成: `proposalId`, `status="proposed"`, `reviewState="unreviewed"`
- 人間判断: `/ai/proposals/audit` の `accepted | rejected | held`
- proposal registryとDocument/source bundleの整合をserver側で検証する。

これを認知評価のために別schemaへ置き換えない。

ただし4arm比較では、A/Bにも同じ観測面を作り、`modify`（部分採用・修正）、採否理由、後から判明した妥当性を保持する必要がある。そのため `cognitive-dogfood-run-record-template.md` の **experiment proposal ledger** を共通正本として使い、C/Dでは可能な範囲で既存proposal/audit eventを参照する。

つまり:

- **product audit** = 製品内で起きた提案と正式な人間判断の監査。
- **experiment ledger** = A〜Dを同じ尺度で比較するための研究記録。`later_verdict`や`modify`を含む。

experiment ledgerの存在だけを理由に新しいproduct API/schemaを起票しない。

## 測定軸

### M1 生存所見 / discovery increment

- 基準線になかった新しい問い、関係、反証、状態、遷移、空白のうち、対象の事実へ戻しても成立するもの。
- 単純な論点数ではなく、重複・言い換え・体系語を除去した後に残るものを数える/記述する。

### M2 根拠接地 / provenance grounding

- 主要主張から原資料、コード、ADR、issue、観察カードへ戻れる割合と質。
- 根拠不明のもっともらしい一般論、架空の仕様、出典の取り違えを失敗として記録する。
- 時点の違う資料が同居する場合、古い主張にsourceが付いているだけでは成功としない。現在状態との時間関係まで解釈できるかを見る。

### M3 異論・残差保持 / dissent and residual preservation

- 少数カード、孤立カード、反対証拠、未解決、不確実性が最終成果で消えていないか。
- 「きれいな合意」へ吸収した件数/事例を負の証拠として残す。

### M4 早期収束耐性 / premature-closure resistance

- 初期仮説・最初のAI案・既存ADR分類へ不当に固定されず、反証に応じて構造を変更できたか。
- 新しい証拠で島/表札/判断が動いた履歴を正の証拠とする。

### M5 AI依存校正 / appropriate reliance

- AI提案が正しいときに有用に採用し、誤り・無関係・過剰一般化のときに棄却/修正できたか。
- 採用率の高さは評価しない。誤提案の見逃しと有用提案の不使用を分ける。
- KJ Atlas内の正式proposalではproduct auditを証拠に使えるが、arm間比較はexperiment ledgerで揃える。
- Case 001では人工的な偽情報を注入せず、R3/DOGFOOD-31/32に自然発生した「初期記述→後段訂正」を事前登録し、古い主張への過剰依存を測る。

### M6 再訪・訂正可能性 / revisability

- 数日後または材料追加後に、なぜその判断になったかを再構成できるか。
- 元資料を失わずに束ね/表札/関係/結論を変更できるか。
- C/Dでは既存InquiryJourneyのsnapshot/handoff/lineageがこの再訪に実際に役立ったか、単なる保存負担だったかも記録する。

### M7 注意・探索制御 / attention orchestration

- 重要だが目立たない材料、空白、対立、時間変化、未到達状態へ注意を再配分できたか。
- AIが大量に生成した派手な論点へ注意が偏った事例も記録する。

### M8 決定への変換品質 / decision usefulness

- 最終成果が、具体的なissue、保留理由、追加調査、ADRトリガー、実装変更、棄却判断へ変換可能か。
- 後続実装/レビューで撤回された場合も結果として追跡する。
- `DOMAIN-W-ITERATION-01` T9については、手動中核の実使用で観察したAI支援不足/不要判断を具体的な判断材料として返せるかも含む。

### M9 認知摩擦 / cognitive friction

- 方法が要求する有益な立ち止まりと、単なる操作負担を分ける。
- 「速いほど良い」は前提にしないが、摩擦が価値を生まず離脱原因になる場合は製品課題として残す。
- InquiryJourneyのsnapshot/handoff/分岐操作についても、再訪価値を生む摩擦か、実作業を中断する無益な摩擦かを分ける。

## 認知制御の失敗類型

比較時は、少なくとも次を観察する。

- premature classification: 生材料を既知カテゴリへ先に押し込む。
- anchoring: 最初のAI案/既存設計へ固定される。
- stale-evidence anchoring: issueタイトルや初期記述を、後段の訂正を読まず現在事実として扱う。
- automation bias: AI提案を根拠確認なしで採用する。
- cognitive offloading: 人間側が比較・判断・反証を放棄する。
- provenance loss: 結論から元資料へ戻れなくなる。
- dissent collapse: 対立・少数・保留を一つの整った説明へ溶かす。
- verbosity illusion: 長さ/網羅感を深さと誤認する。
- framework capture: 文化的体系の語彙や構造が対象を上書きする。
- framework echo: 対象が既に内在化した同型原理を外部体系で再増幅し、独立した増分と誤認する。
- canvas ritualization: KJ操作を行うこと自体が目的化し、対象側の増分がない。
- instrumentation leakage: 実験のための記録要求が製品設計へ不必要に混入する。
- endless exploration: 新しい対象側増分がないのに探索を続ける。

## 現在の実行準備状態

R10継続dogfoodで、比較実験の準備状態と未実行部分を再点検した。

- Case 001〜003の問い、product snapshot、skill snapshot、A〜Dのtreatment、required outputは凍結済みである。
- frozen source bundle、skill bundle、arm package、run record、blind packageには既存のvalidatorとcontract testがある。
- `cognitive-dogfood-index.md` の現在地は `P1: Case 001 Arm C ready / raw run未取得` であり、比較証拠そのものはまだ得られていない。
- valid armは、比較設計の既知情報から隔離されたfresh contextで開始する。この設計者側の継続dogfoodコンテキストをA〜Dへ再利用しない。
- C/DではKJ AtlasキャンバスとInquiryJourneyを実際の外部表象として操作する。チャット内の代理JSON編集をC/D実走へ読み替えない。
- product snapshotの固定はarm間比較の内的妥当性を守るためのものであり、その後の改善を含むcurrent mainの絶対評価とは区別して解釈する。

現在の次の実行入口は、`cognitive-dogfood-index.md`、`cognitive-dogfood-execution-plan.md`、Case 001のlaunch packet、`cognitive-dogfood-cd-ui-runbook.md` である。

raw run取得前に、新しいKPI、別schema、追加preflightを増やして実走の代替にしない。現在の主要な未投入条件は、隔離された実行コンテキストとC/Dの実UI操作である。

## cultural-substrate-weavingとの責任分界

実験で見つかった問題は、直ちにスキル修正へ入れず次に帰属させる。

1. **KJ Atlas製品**: 外部表象/UI/API/保持/提案契約の問題。
2. **cultural-substrate-weaving**: 文化体系探索またはKJ統合を実行/検証するために必要な方法規則の問題。
3. **caller/domain context**: ソフトウェア設計の品質基準、問いの置き方、領域固有の判断。
4. **model behavior**: 特定モデルの流暢さ、過剰要約、追従性等で、スキル固有ではないもの。
5. **experiment design**: arm汚染、資料差、評価者バイアス、instrumentation leakage等。

`cultural-substrate-weaving` の現行 `AGENTS.md` が定義する「スキルに属するもの/呼び出し側に属するもの」の境界を優先する。

## 対応方針

- 実施すること:
  1. `COGNITIVE-DOGFOOD-01` の事前登録済みCase 001〜003を4armへ流す。
  2. armごとに生出力・キャンバス成果・採否・根拠・判断を保存する。
  3. C/Dでは長期状態に既存InquiryJourney、正式AI提案に既存proposal auditを再利用し、実験メタデータだけをrun recordへ置く。
  4. M1〜M9を、定量可能なものは件数/比率、困難なものは具体例とblind reviewで評価する。
  5. 1ケースごとの勝敗ではなく、複数ケースで再現する差を探す。
  6. スキル変更後は、変更を生んだケースだけでなく過去ケースにも再適用し、局所最適化/回帰を検査する。
- 実施しないこと:
  - 総合「IQ向上スコア」を作ること。
  - 文章量、処理速度、利用者好感度だけで勝敗を決めること。
  - 単一モデル・単一課題の結果を一般化すること。
  - 方法に都合の悪いarm結果を除外すること。
  - experiment proposal ledgerをproduct監査schemaへ昇格すること。
  - experiment source snapshotをInquiryJourney snapshotと同一視すること。
  - T9のAI支援不足を証明するために手動中核の摩擦を過大評価すること。

## 受入条件

- [x] 3つの異なる開発課題をCase 001〜003として、Case 001実行前に事前登録した。
- [ ] 3ケースすべてで4arm比較を実施する。
- [ ] 各ケースでM1〜M9のうち測定可能/不能を明示し、不能項目をゼロ扱いしない。
- [ ] blindまたはarm匿名化レビューを少なくとも代表ケースで実施する。
- [ ] KJ Atlas固有増分、スキル固有増分、組合せ相互作用、負の相互作用を区別して記述する。
- [ ] 少なくとも1件、自然発生した誤/旧AI・資料主張への依存校正を比較する。
- [ ] C/Dで既存InquiryJourneyを使用し、M6/M9における実益と摩擦を記録する。
- [ ] C/Dの正式AI proposalを使用する場合は既存product auditとexperiment ledgerの対応を記録し、新監査schemaを作らない。
- [ ] `DOMAIN-W-ITERATION-01` T9へ、実使用に基づく `AI支援が必要 / 現行手動で十分 / 条件付き / 未判定` の材料を返す。
- [ ] スキル変更候補は帰属判定と回帰検査を通してから `cultural-substrate-weaving` 側へ反映する。
- [ ] 結果が増分なし/悪化でもそのまま結論として保持する。

## 検証計画

- 実行する確認:
  - ケースごとに固定入力manifestとarm別artifactを保存する。
  - 最終判定には「何が新しく立ち、対象へ戻して生存したか」と「何を誤って失ったか」を必ず含める。
  - C/DではInquiryJourney snapshot/handoff/lineageと正式proposal auditを、製品側に既に存在する範囲で使用する。
  - 数日後のrevisitまたは後続実装結果を可能なケースで追跡する。
- 期待結果:
  - KJ Atlas、スキル、両者の組合せのどこに実在する認知増分があるか、またはないかを反証可能な形で示せる。
  - 認知dogfood自体が、既存InquiryJourneyのT9 AI支援判断を前進させる現実の利用証拠になる。
  - 実験にしか必要ないinstrumentationを製品契約へ混入させずに評価できる。

## 補足

- 外部研究上も、人間-AI補完性は自明ではなく、信頼校正、役割分担、注意の編成、監査可能な共有成果物が重要とされる。したがって「AIを足した条件が勝つ」ことを前提にしない。
- 認知摩擦は一律に悪としない。AIへの過剰依存を減らすためには、判断前の立ち止まり等のforcing functionが有効な場合がある一方、受容性を下げることもあるため、M5とM9を分けて観察する。
