# 第三者価値検証 実行計画

- 状態: 最初の第三者session開始前に準備済み
- 日付: 2026-08-30
- 関連issue memo: `VALUE-REALNESS-01`, `PRODUCT-POSITION-01`, `PRACTICE-CULTURE-01`
- 関連する認知dogfood: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`
- 関連ADR: `ADR-0032`, `ADR-0042`, `ADR-0047`, `ADR-0057`

## 1. 目的

KJ Atlasの内部設計やdogfoodから生まれた価値仮説を、第三者が**自分の実資料**を持ち込む現実へ接地する。

この検証は、「好評だったか」「KJ法として正しく使えたか」を測るものではない。第三者が現在の仕事からKJ Atlasへ切り替える理由、既存手段へ戻る理由、途中で止める理由、そもそも不要だと判断する理由を、実資料、操作、成果物へ戻れる形で観察する。

検証では、次の2つの目的を混同せずに保持する。

1. **Product-value validation**: 実在する利用仕事、切替理由、再利用理由が生じるかを確かめる。
2. **External-reality grounding**: 内部dogfoodで作られた自己参照的な価値仮説が、外部材料によって支持されるだけでなく、縮小・修正・棄却され得るかを確かめる。

## 2. 実行順

### V0 — 検証手順の凍結

第三者の反応を見る前に、次を固定する。

- session record template。
- 参加条件と除外条件。
- privacy / data handling。
- baselineの聞き取り方法。
- stopping / withdrawal条件。
- value / friction / no-use / counterevidenceの観察単位。
- findingの振り分け方法。

V0では、採用率、NPS、利用時間などのKPIを置かない。

### V1 — Primary beachhead session

初期候補である定性調査、UX、デザイン、プロダクト調査等の実践者に、自分の題材を持ち込んでもらい、現在のworkflowと比較する。

### V2 — 異なる実践文脈でのsession

V1とは実践上の作法が異なる第三者、または同程度に異なる文脈を少なくとも1件扱う。

国籍、世代、職種といった属性ラベルで「文化」を決めない。次のような、実際の仕事上の作法が異なる文脈を選ぶ。

- 誰が意味を確定するか。
- 合意を必要とするか。
- 匿名性が必要か。
- 根拠をどこまで公開できるか。
- 同期作業か、非同期作業か。
- 個人分析か、共同分析か。
- 長期的な再訪が必要か。
- 視覚キャンバスにどの程度依存できるか。

### V3 — KJ統合

V1 / V2で得た観察を、あらかじめ用意した「価値」「UX」「文化」等の分類へ入れない。

まず生カードとして保持し、訴えの近さから束ね、表札、対立、孤立、空白を立ち上げる。内部dogfoodから生まれた仮説カードとはprovenanceを分ける。

### V4 — 製品判断へ戻す

第三者から得た材料を、必要に応じて次へ戻す。

- `PRODUCT-POSITION-01`: primary job / switch reason。
- `PRACTICE-CULTURE-01`: invariant / adaptable surfaceの仮説。
- `VALUE-REALNESS-01`: value realness。
- 既存issue: 既存problem statementへ直接つながる場合。
- 新しいissue / ADR: 後述する振り分け条件を満たす場合だけ。

## 3. 参加者と資料の条件

### 参加条件

次をすべて満たすことを基本とする。

- 扱う題材の意味や文脈を本人が説明できる。
- 現在その仕事をどう行っているか、少なくとも比較可能なbaselineを説明できる。
- KJ Atlasを使う・使わないという判断を自由に述べられる。
- sessionを途中で止められる。
- 何を記録し、どこまで保存するかに同意できる。

KJ法の経験、KJ Atlasへの好意、OSSへの関心は参加条件にしない。

### 資料条件

資料は次の順で優先する。

1. 本人が実際に扱っている資料。
2. 本人自身が意味を保持したまま匿名化した資料。
3. 実資料を安全に持ち込めない場合だけ、本人が現実的だと認める代替資料。

次の資料を無断で持ち込まない。

- 個人情報や機密情報を含む資料。
- 契約上、外部ツールへ投入できない資料。
- 第三者の同意が必要な生データ。
- 公開範囲が明確でない組織資料。

実資料を安全に持ち込めないこと自体が導入障壁である場合は、問題を回避して検証を成立させようとしない。no-use reason / governance evidenceとしてそのまま記録する。

## 4. Sessionの進め方

### S0 — 価値語彙を提示する前のbaseline

KJ Atlasの価値仮説を説明する前に、利用者自身の言葉で次を確認する。

- 今回取り組む仕事は何か。
- 現在使っている道具と手順。
- どこで困っているか。
- どこは現在の方法で十分か。
- 成果物を誰へ、どのように渡すか。
- 後から何へ戻る必要があるか。

「根拠」「異論」「再訪」等を重要価値として先に示し、回答を誘導しない。

### S1 — 資料の受け入れ

資料の意味、量、媒体、機密性、更新可能性を確認する。

最初からKJカードへ整然と分割することを求めない。必要であれば、大きな単位のまま始める。

### S2 — 外部化

カード化、原文や観察への接地、重複、違和感、不明点の保持を行う。

主に次を観察する。

- カード化が意味の保持に役立った瞬間、逆に意味を壊した瞬間。
- 細分化しすぎた場面。
- 出所へ戻る必要が生じた場面。
- 視覚表象によって理解が変わった場面。

### S3 — KJ統合

束ね、表札、配置、対立、孤立、空白を扱う。

主に次を観察する。

- 新しい関係が立ち上がったか。
- 既存workflowと同じ結論しか得られなかったか。
- 早く整理されすぎなかったか。
- 異論や孤立した材料が、邪魔に感じられたか、役立ったか。
- 人間による確定操作が必要だったか、余計だったか。

### S4 — 判断や叙述へ戻す

できあがった構造を、文章、issue、調査課題、保留事項などへ戻す。

主に次を観察する。

- 元資料へ戻って説明できるか。
- 何を決めなかったかが残っているか。
- 成果物を他者へ渡せるか。
- 既存workflowへ転記する負担がどの程度あるか。

### S5 — 再訪

可能であればsession内、または後日の短い再訪で、成果物だけを手掛かりに作業を再開する。

- なぜその束、表札、判断になったかを辿れるか。
- 古い判断を変更しやすいか。
- 何が失われているか。

### S6 — 利用後の説明

最後は、利用者自身の語彙で聞く。

- 何が役立ったか。
- 何が余計だったか。
- 既存手段の方が良かったところはどこか。
- 次に同じ種類の仕事があれば何を使うか。その理由は何か。
- KJ Atlasを使わない条件は何か。
- どのような人や仕事には合わないと思うか。

「また使いますか」というYes / Noだけを価値の証拠にしない。

## 5. 観察の単位

1件の観察は、可能な限り次を一緒に保持する。

- **Trigger**: 何をしていたときか。
- **Material**: どの資料、カード、構造に関することか。
- **Observed behavior / statement**: 何が起きたか、何と言ったか。
- **Immediate consequence**: 判断、探索、混乱、停止等がどう変わったか。
- **Artifact evidence**: 変更前後の成果物や参照先。
- **Operator inference**: 操作者の推論。観察事実とは分離して記録する。

価値語にまとめる前の、具体的な状況と感触を残す。

## 6. 収集する証拠

次を同じ重要度で集める。

- **Value moment**: KJ Atlasを使ったことで仕事が具体的に変わった瞬間。
- **Friction**: 操作、概念、表現、連携上の負担。
- **No-use reason**: 使わない方が合理的だった理由。
- **Existing-workflow sufficiency**: 現在の手段で十分だった範囲。
- **Counterevidence**: 内部の価値仮説に反する観察。
- **Unexpected value**: 内部仮説にはなかった便益。
- **Stop / withdrawal**: 完遂しなかった理由。
- **Practice-culture tension**: 権限、声、合意、根拠、統制、時間、表現、accessibilityとの摩擦。

「使わない」という結果を、失敗として別枠へ押し込まない。

## 7. 実践文脈として残すmetadata

session recordには、必要最小限の実践文脈を残す。ただし、このmetadataをKJカードの分類基準には使わない。

- individual / collaborative。
- synchronous / asynchronous。
- 意味を確定する権限の所在。
- consensus required / not required / mixed。
- evidence visibility。
- anonymity needs。
- data-control constraints。
- accessibility considerations。

国籍、民族、世代等を製品挙動の「文化型」として分類しない。

## 8. Privacyと資料の扱い

- 個人を追跡するtelemetryを導入しない。
- session recordは、本人が同意した範囲だけを保持する。
- 必要であれば原資料そのものは保存せず、artifact reference、匿名化した抜粋、操作者の観察だけを残す。
- 公開repositoryへ残す内容と、非公開で一時的に扱うsession materialを分ける。
- 協力者の氏名や所属を公開することを、value evidenceの条件にしない。
- withdrawalがあった場合に何を削除し、何を保持するかをsession開始前に決めておく。
- raw materialをpublic Gitへ一度入れてから削除する運用を前提にしない。公開履歴へ入れる前にpublication boundaryを確認する。

## 9. 停止条件

次はすべて有効な結果であり、無理にsessionを完遂させない。

- 利用者が現在の手段で十分だと判断した。
- 方法そのものが仕事に合わなかった。
- 資料統制上、安全に続行できなかった。
- 操作負担が得られる便益を上回った。
- 視覚キャンバス等のaccessibility上の障壁によって成立しなかった。
- 題材が意味探索を必要とせず、KJ Atlasを使う理由がなかった。

停止理由そのものをraw evidenceとして保存する。

## 10. Findingの振り分け

### V-F0 — Observation / KJ card

単一sessionだけの所見、利用者固有の好み、まだ再現していない機能案は、まずここに留める。

### V-F1 — 既存issue

既存problem statement / acceptance criteriaへ直接戻せる摩擦は、重複issueを作らず、既存issueへ証拠を返す。

### V-F2 — 新しいissue memo

次をすべて満たす場合だけ起票する。

- 実利用で再現可能である。
- 既存issueでは扱えない。
- 実行可能な変更または検証がある。
- acceptance criteria / verification levelを書ける。
- 利用者の「使わない」を無理に機能要求へ読み替えていない。

### V-F3 — ADR候補

`ADR-0047`の実使用トリガーを満たす場合だけ候補にする。

- データ、権限、共有、安全契約にまたがるtrade-offが必要になった。
- 新しい利用段階へ移行した。
- 非機能境界を越える必要が生じた。
- 破壊的なschema / contract変更が必要になった。

## 11. Session間の統合

V1 / V2が終わった後、次を**あらかじめ分類せずに**KJ統合する。

- value moments。
- no-use reasons。
- friction。
- counterevidence。
- practice-culture tensions。
- unexpected value。

その後で初めて、内部仮説ごとに次のいずれかを判定する。

- support。
- modify。
- narrow。
- reject。
- unresolved。

同じ観察が複数の仮説へ影響することを許す。

## 12. 各段階の終了条件

### V1

- primary beachheadの第三者sessionを1件実施し、完遂または明確な停止理由が残っている。
- baseline / raw observations / artifact evidence / no-use reasonを記録できる。

### V2

- V1とは異なる実践文脈のsessionを少なくとも1件実施している。
- 共通する価値と文脈固有の摩擦を区別できるだけのraw materialがある。

### V3

- 先入観となる分類を置かず、KJ統合を一度行っている。
- 内部dogfood由来の仮説と第三者由来の観察について、provenanceが残っている。

### V4

- `PRODUCT-POSITION-01`のprimary job / switch reasonを、support / modify / narrow / reject / unresolvedのいずれかへ動かせる。
- 「新しいissueを作らない」「この対象市場を狙わない」ことも正当な結論として残せる。
- ADRは、実使用トリガーがある場合だけ候補にする。

## 13. 認知dogfoodとの境界

Case 001〜003の結果を、第三者sessionへ「正解」として提示しない。

内部dogfoodから得た仮説は、S0のbaselineを取る前に利用者へ価値語として教えない。第三者自身の言葉と行動を先に取得する。

内部所見と第三者所見が衝突した場合は、どちらかへ急いで統合しない。対立したままカードとして保持し、その衝突自体を次の検討材料にする。