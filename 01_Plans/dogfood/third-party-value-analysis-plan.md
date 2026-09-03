# 第三者価値検証 — 分析計画

- 状態: 最初の第三者session開始前に事前登録済み
- 日付: 2026-08-31
- 関連文書: `VALUE-REALNESS-01`, `PRODUCT-POSITION-01`, `PRACTICE-CULTURE-01`
- 入力: `third-party-value-session-record-template.md`の記録、`third-party-value-session-launch-checklist.md`の開始判定、公開・利用に同意されたsanitized artifact

## 1. 目的

第三者sessionの結果を見た後で、KJ Atlasに有利な評価基準や分類を作らないよう、分析の順序と判定単位を先に固定する。

本計画は、採用率、NPS、平均利用時間等を評価するものではない。少数の初期実利用から、**何が実際の仕事を変えたのか、何は変えなかったのか、何が利用そのものを成立させなかったのか**を、元の証拠へ戻れる形で統合する。

## 2. 分析単位

最初の分析単位は参加者そのものではなく、session recordに残したraw observationとartifact evidenceである。

次を1件の意味単位として保持する。

- trigger / material。
- observed behavior または participant statement。
- immediate consequence。
- artifact evidence。
- operator inference。観察事実とは分離して扱う。

ただし、`STOP-DATA-BOUNDARY`等により**実資料を入力する前にsessionが停止した場合は、launch checklistに残したruntime data-pathの事実、参加者の停止判断、その理由をraw observation相当として扱う。** KJ artifactが存在しないことだけを理由に除外しない。

「この人はKJ Atlasに向いている／向いていない」といった人物分類を、主要な分析単位にしない。

## 3. 最初に行わないこと

- value / UX / culture / feature request等の既成分類へ、最初からカードを入れる。
- 参加者ごとにpositive / negative scoreを付ける。
- 発言数、カード数、session時間を成果指標にする。
- 「また使いたい」というYes / Noだけでvalue realnessを判定する。
- 内部dogfoodの価値仮説に合う観察だけを先に抜き出す。
- no-use / stop / existing-workflow sufficiencyを失敗データとして除外する。
- `STOP-DATA-BOUNDARY`を、「製品を実際に使っていない」という理由だけで除外する。
- 実践文脈のmetadataをKJ束ねの分類キーにする。

## 4. KJ統合の順序

### A. 生カード化

session recordから、意味を保ったまま生カードを作る。

- 可能な限りparticipant wording / observable eventを保つ。
- operator inferenceは別カード、または推論であることを明示した記述として扱う。
- value vocabularyへ先に言い換えない。
- 一連の出来事が1つの体験としてまとまっている場合は、細かく切りすぎない。
- 実資料投入前に停止した場合は、`runtime condition → participant decision → immediate consequence`を1つの体験として保持し、実際には起きていない操作体験を補わない。

### B. 束ねと表札

カードの訴えの近さから束ねる。

- participant IDやpractice metadataを主な束ね基準にしない。
- opposing cardsを「どちらも大事」とまとめて対立を消さない。
- 孤立カードを無理に既存の束へ入れない。
- no-use reasonとvalue momentが同じ構造の両側を表す場合は、対立関係として保持する。
- provider / network / storage境界によるno-useを、操作UXや一般的なprivacy不安へ自動的に言い換えない。

### C. A型図解

最低限、次を見える形にする。

- 実際に生じた価値。
- 既存workflowで十分だった領域。
- 使わない理由。
- 操作、概念、data-control、accessibility上の摩擦。
- runtime AI / provider / network / storage境界によって成立しなかった利用条件。
- 予想していなかった価値。
- 内部仮説への反証。
- 参加者や文脈を越えて現れた関係。
- 文脈依存に見える関係。
- まだ説明できない空白。

### D. B型文章化

A型図解から文章化し、その後に原カードへ戻って次を確認する。

- 強い言い換えによってparticipantの意味を変えていないか。
- 少数意見や否定的材料が消えていないか。
- operator inferenceをparticipant factへ昇格していないか。
- 「社会一般」へ過剰に一般化していないか。
- 1回のsessionで生じたdata-boundary stopを、恒久的な製品要求へ飛躍させていないか。

## 5. 内部仮説へ戻す

KJ統合を行った後で初めて、内部仮説へ戻す。

各仮説は次の5値で扱う。

- **support**: 仮説の重要部分が、第三者の独立した観察によって支えられた。
- **modify**: 仮説の方向は残るが、内容、条件、説明を変える必要がある。
- **narrow**: 特定の仕事、文脈、条件へ限定すれば成立する。
- **reject**: 観察と整合せず、仮説を維持する根拠が弱い。
- **unresolved**: 証拠不足、または相反する証拠が残っている。

`support`の件数を総合点にしない。

## 6. Primary job / switch reasonの判定

`PRODUCT-POSITION-01`へ戻す候補は、少なくとも次を満たす必要がある。

1. 具体的な仕事の状況に結び付いている。
2. 既存workflowとの違いを説明できる。
3. 参加者の発言だけでなく、可能であればartifact / behavior上の変化がある。
4. KJ Atlasの機能名ではなく、利用者の仕事として表現できる。
5. 使わない条件も対として説明できる。

たとえば「カードを束ねられる」はswitch reasonではない。「既存の要約では消える異論を残したまま、後から判断根拠へ戻る必要がある仕事」のように、仕事と条件へ戻して表現する。

ただし、この例文そのものを参加者へ提示しない。

実資料投入前に停止した場合はartifact変化がないため、switch reasonを支持する正の証拠にはしない。一方で、**そのruntime / data-control条件では利用仕事が成立しないというno-use / boundary evidence**として扱う。

## 7. 実践文脈の分析

`PRACTICE-CULTURE-01`へ戻す際は、国籍、民族、世代、職種による文化型を作らない。

観察された差は、まず次の関係として読む。

- meaning authority。
- consensus requirement。
- voice / anonymity。
- evidence visibility。
- data control。
- synchronous / asynchronous work。
- long-term revisit。
- expression / accessibility。

その後にだけ、既存の暫定不変条件を`support / modify / reject / unresolved`で評価する。

## 8. Sessionを越えた再現の扱い

初期V1 / V2では、統計的一般化を目的としない。

次を区別する。

- **single-context evidence**: 1つのsession / 文脈でのみ観察された。
- **cross-context recurrence**: 異なる実践文脈で、同型の構造が再現した。
- **context conflict**: 一方では価値になり、他方では摩擦または不要になった。
- **insufficient variation**: 比較した文脈が実質的に同質で、結論できない。

2件で再現しただけで普遍価値とはしない。再現は、次の検証優先度を上げる証拠として扱う。

また、同じprovider / storage設定で複数sessionが止まった場合、それだけで文脈横断の再現とはみなさない。実践文脈とruntime条件の両方を確認する。

## 9. Findingの振り分け

KJ統合後の所見を次へ振り分ける。

### V-F0

- 単一sessionの所見。
- まだ再現していない仮説。
- participant固有の好み。
- 追加資料や対照文脈を待つ必要がある所見。
- 単一sessionのprovider / network / storage条件によるno-use。

### V-F1

既存issueのproblem statement / acceptance criteriaへ直接戻せる実使用証拠。

### V-F2

次をすべて満たす場合だけ、新しいissue memoを作る。

- 実利用で再現可能である。
- 既存issueでは扱えない。
- 実行可能な変更または検証がある。
- acceptance criteria / verification levelを書ける。
- 「使わない」を無理に機能要求へ変換していない。

### V-F3

`ADR-0047`のreal-use triggerを満たす場合だけADR候補とする。

- 横断的なdata / permission / sharing / safety trade-off。
- 利用段階の実質的な変化。
- 非機能境界の超過。
- 破壊的なcontract / schema変更。

## 10. 認知dogfoodとの比較

第三者分析を、Case 001〜003で得た結論の「正解確認」に使わない。

内部dogfoodの所見と第三者材料が異なる場合、少なくとも次の可能性を検討する。

- 内部dogfood固有の自己参照効果。
- 第三者文脈固有の制約。
- product maturity / onboardingの差。
- runtime data boundaryの差。
- evidence不足。
- 価値仮説そのものが誤っている可能性。

衝突は、解消すべきノイズではなく、次のKJ材料として保持する。

## 11. 公開と認識上の制約の監査

公開用の分析を書いた後、`third-party-value-publication-boundary.md`に従って次を確認する。

- privacyのために省略した情報を、存在しなかったかのように扱っていない。
- publicに出せない証拠について、第三者が再確認できないという制約を明記した。
- participant wordingを匿名化の過程で強く一般化していない。
- 少数のCaseから社会一般へ外挿していない。
- privateなlaunch / data-path evidenceを公開説明から省いた場合、その省略によって停止理由の意味を変えていない。

## 12. 初期分析の終了条件

V1 / V2の後に、最低限次を説明できれば初期分析を完了とする。

- 具体的に生じたvalue moment。
- 既存workflowが十分だった領域。
- 最も強いno-use reason。
- runtime / data-control境界によって成立しなかった条件。存在する場合のみ。
- 内部仮説を修正・縮小・棄却するcounterevidence。
- 文脈間で共通した構造、または対立した構造。
- 次に必要な実利用検証。
- F0 / F1 / F2 / F3の振り分け。

結論が`value realness not established`、`existing workflow sufficient`、あるいは`data boundary prevents safe use in this context`であっても、有効な完了結果とする。