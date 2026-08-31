# Third-Party Value Validation Execution Plan

- Status: Prepared before first third-party session
- Date: 2026-08-30
- Related issue memos: `VALUE-REALNESS-01`, `PRODUCT-POSITION-01`, `PRACTICE-CULTURE-01`
- Related cognitive dogfood: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`
- Related ADR: `ADR-0032`, `ADR-0042`, `ADR-0047`, `ADR-0057`

## 1. 目的

KJ Atlasの内部設計・dogfoodで成立した価値仮説を、第三者が**自分の実資料**を持ち込む現実へ接地する。

この検証は「好評か」「KJ法として正しく使えたか」を測るものではない。第三者が既存の仕事からKJ Atlasへ切り替える理由、戻る理由、途中で止める理由、不要と判断する理由を、実資料・操作・成果物へ戻れる形で観察する。

検証の目的は次の二つを分離して保持する。

1. **Product-value validation**: 実在する利用仕事、switch reason、reuse reasonが生じるか。
2. **External-reality grounding**: internal dogfoodの自己参照的な価値仮説が、外部材料によって支持だけでなく縮小・修正・棄却され得るか。

## 2. 実行順

### V0 — Protocol freeze

第三者の反応を見る前に次を固定する。

- session record template。
- 参加条件 / 除外条件。
- privacy / data handling。
- baseline聞き取り。
- stopping / withdrawal条件。
- value / friction / no-use / counterevidenceの観察単位。
- finding triage。

V0では採用率、NPS、利用時間等のKPIを設定しない。

### V1 — Primary beachhead session

初期候補である定性/UX/デザイン/プロダクト調査系の実践者が、自分の題材を持ち込み、既存workflowとの比較を行う。

### V2 — Contrast practice session

V1と異なる実践文化の第三者、または同等に異質な文脈を1件以上扱う。

国籍・世代・職種ラベルではなく、次の局所的な作法が異なる文脈を選ぶ。

- 誰が意味を確定するか。
- 合意を必要とするか。
- 匿名性が必要か。
- 根拠公開範囲。
- 同期/非同期。
- 個人/共同分析。
- 長期再訪の必要性。
- 視覚キャンバスへの依存可能性。

### V3 — KJ integration

V1/V2の観察を、あらかじめ用意した「価値」「UX」「文化」分類へ入れない。

生カードとして保持し、訴えの近さから束ね、表札、対立、空白を作る。内部dogfood由来の仮説カードとはprovenanceを分ける。

### V4 — Product decision return

第三者材料を次へ返す。

- `PRODUCT-POSITION-01`: primary job / switch reason。
- `PRACTICE-CULTURE-01`: invariant / adaptable surfaceの仮説。
- `VALUE-REALNESS-01`: value realness。
- 既存issue: 既存problem statementへ直接接続する場合。
- 新issue / ADR: 下記triage gateを満たす場合のみ。

## 3. Participant / material eligibility

### 参加条件

次をすべて満たす。

- 扱う題材の意味・文脈を本人が説明できる。
- 現在その仕事をどう行っているか、少なくとも比較可能なbaselineを説明できる。
- KJ Atlasを使う/使わない判断を自由に述べられる。
- sessionを途中停止できる。
- 記録対象と保存範囲に同意できる。

KJ法経験、KJ Atlasへの好意、OSSへの関心は必須条件にしない。

### 資料条件

優先順位:

1. 本人が実際に扱っている資料。
2. 本人が意味を保持した匿名化資料。
3. 実資料を持ち込めない場合のみ、本人が現実的と認める代替資料。

次は無断で持ち込まない。

- 個人情報・機密情報。
- 契約上外部ツールへ投入できない資料。
- 第三者の同意が必要な生データ。
- 公開範囲が不明な組織資料。

「実資料を安全に持ち込めない」こと自体が導入障壁なら、回避せずno-use / governance evidenceとして記録する。

## 4. Session structure

### S0 — Baseline before product-value vocabulary

KJ Atlasの価値仮説を説明する前に記録する。

- 今回の仕事は何か。
- 現在の道具・手順。
- どこで困るか。
- どこは現状で十分か。
- 成果物を誰にどう渡すか。
- 後から何へ戻る必要があるか。

「根拠」「異論」「再訪」等を重要価値として先に誘導しない。

### S1 — Material intake

資料の意味、量、媒体、機密性、更新可能性を確認する。

最初からKJカードへ綺麗に分割することを求めない。必要なら大きい単位のまま始める。

### S2 — Externalization

カード化、原文/観察への接地、重複/違和感/不明点の保持を行う。

観察対象:

- カード化が意味の保持に役立つ/壊す瞬間。
- 過度な細分化。
- 出所へ戻る必要が生じる瞬間。
- 視覚表象が理解を変える瞬間。

### S3 — KJ integration

束ね、表札、配置、対立、孤立、空白を扱う。

観察対象:

- 新しい関係が立ち上がる。
- 既存workflowと同じ結論しか出ない。
- 早く整理されすぎる。
- 異論や孤立材料が邪魔に感じられる/役立つ。
- 人間の確定操作が必要/不要と感じられる。

### S4 — Decision / narrative return

構造を文章、issue、調査課題、保留等へ戻す。

観察対象:

- 元資料へ説明可能に戻れるか。
- 何を決めなかったかが残るか。
- 成果物を他者へ渡せるか。
- 既存workflowへの転記負担。

### S5 — Revisit test

可能ならsession内または後続の短い再訪で、成果物だけから作業を再開する。

- なぜその束/表札/判断になったか戻れるか。
- 古い判断を変更しやすいか。
- 何が失われているか。

### S6 — Independent post-use explanation

利用者自身の語彙で聞く。

- 何が役立ったか。
- 何が余計だったか。
- 既存手段の方が良い箇所。
- 次に同じ種類の仕事があれば何を使うか。その理由。
- KJ Atlasを使わない条件。
- 誰には合わないと思うか。

「また使いますか」のYes/Noだけを価値証拠にしない。

## 5. Observation unit

1件の観察は、可能な限り次を一緒に保持する。

- **Trigger**: 何をしていたか。
- **Material**: どの資料/カード/構造か。
- **Observed behavior / statement**: 何が起きたか。
- **Immediate consequence**: 判断、探索、混乱、停止等がどう変わったか。
- **Artifact evidence**: 変更前後の成果物や参照。
- **Operator inference**: 推論は事実と分離する。

価値語に変換する前の「土の匂い」を残す。

## 6. Evidence classes

次を同じ重要度で収集する。

- **Value moment**: KJ Atlasを使ったために仕事が具体的に変わった瞬間。
- **Friction**: 操作・概念・表現・連携上の負担。
- **No-use reason**: 使わない方が合理的な理由。
- **Existing-workflow sufficiency**: 現行手段で十分な範囲。
- **Counterevidence**: 内部価値仮説に反する観察。
- **Unexpected value**: 内部仮説になかった便益。
- **Stop / withdrawal**: 完遂しなかった理由。
- **Practice-culture tension**: 権限、声、合意、根拠、統制、時間、表現、accessibilityとの摩擦。

「使わない」をfailure bucketへ押し込まない。

## 7. Practice-culture metadata

session recordへ最小限の文脈を残すが、KJ束ねには使わない。

- individual / collaborative。
- synchronous / asynchronous。
- meaning authorityの所在。
- consensus required / not required / mixed。
- evidence visibility。
- anonymity needs。
- data-control constraints。
- accessibility considerations。

国籍・民族・世代等を製品挙動の文化型として分類しない。

## 8. Privacy / data handling

- 個人追跡テレメトリを導入しない。
- session recordは同意された範囲だけ保持する。
- 必要なら原資料を保存せず、artifact reference / anonymized excerpt / operator observationだけを残す。
- 公開repoへ記録する内容と、非公開の一時session materialを分ける。
- 協力者名・所属の公開をvalue evidenceの条件にしない。
- withdrawal後に何を削除/保持するか、session開始前に決める。

## 9. Stop conditions

次は有効な結果であり、無理に完遂させない。

- 利用者が既存手段で十分と判断する。
- 方法が仕事へ合わない。
- 資料統制上、安全に続行できない。
- 操作負担が得られる便益を上回る。
- 視覚キャンバス等のaccessibility障壁で成立しない。
- 題材が意味探索を必要とせず、KJ Atlasを使う理由がない。

停止理由そのものをraw evidenceとして保存する。

## 10. Finding triage

### V-F0 — Observation / KJ card

単一sessionの所見、利用者固有の好み、未再現の機能案はまずここに留める。

### V-F1 — Existing issue

既存problem statement / acceptance criteriaへ直接戻せる摩擦は、重複issueを作らず証拠を返す。

### V-F2 — New issue memo

次をすべて満たす場合のみ。

- 実利用で再現可能。
- 既存issueで被覆できない。
- 実行可能な変更/検証がある。
- acceptance criteria / verification levelを書ける。
- 利用者の「使わない」を無理に機能要求へ読み替えていない。

### V-F3 — ADR candidate

`ADR-0047` の実使用トリガーを満たす場合のみ。

- データ/権限/共有/安全契約の横断的trade-off。
- 新しい利用段階への移行。
- 非機能境界超過。
- 破壊的schema/contract変更。

## 11. Cross-session synthesis

V1/V2終了後、次を**先に分類せず**KJ統合する。

- value moments。
- no-use reasons。
- friction。
- counterevidence。
- practice-culture tensions。
- unexpected value。

その後に初めて、内部仮説ごとに次を判定する。

- support。
- modify。
- narrow。
- reject。
- unresolved。

同じ観察が複数仮説へ効くことを許す。

## 12. Exit gates

### V1 gate

- 1件のprimary beachhead第三者sessionが完遂または明確な停止理由を持つ。
- baseline / raw observations / artifact evidence / no-use reasonを記録できる。

### V2 gate

- 異なる実践文脈のsessionが1件以上ある。
- 共通価値と文脈固有摩擦を区別できるだけのraw materialがある。

### V3 gate

- 先入観分類をせずKJ統合を一度実施した。
- 内部dogfood由来仮説と第三者由来観察のprovenanceが残る。

### V4 gate

- `PRODUCT-POSITION-01` のprimary job / switch reasonをsupport / modify / narrow / reject / unresolvedのいずれかへ動かせる。
- 「新issueを作らない」「対象市場を狙わない」も正当な結論として残せる。
- ADRは実使用triggerがある場合だけ候補化する。

## 13. Cognitive dogfoodとの境界

Case 001〜003の結果は、第三者sessionへ「正解」として提示しない。

内部dogfoodから得た仮説は、S0 baselineの後まで利用者へ価値語として教えない。第三者の独立した言葉と行動を先に取得する。

内部所見と第三者所見が衝突した場合、どちらかへ早く統合せず、対立カードとして保持する。