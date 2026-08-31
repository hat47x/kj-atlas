# Third-Party Value Validation — Analysis Plan

- Status: Pre-registered before first third-party session
- Date: 2026-08-31
- Related: `VALUE-REALNESS-01`, `PRODUCT-POSITION-01`, `PRACTICE-CULTURE-01`
- Input: `third-party-value-session-record-template.md` records, `third-party-value-session-launch-checklist.md` launch verdicts, and consented/sanitized artifacts

## 1. 目的

第三者sessionの結果を見た後で、KJ Atlasに有利な評価基準や分類を作らないため、分析の順序と判定単位を先に固定する。

本計画は採用率、NPS、平均利用時間等を評価するものではない。少数の初期実利用から、**何が実際の仕事を変え、何が変えず、何が成立を妨げたか**を根拠へ戻れる形で統合する。

## 2. 分析単位

最初の分析単位はparticipantではなく、session recordのraw observationとartifact evidenceである。

次を1件の意味単位として保持する。

- trigger / material。
- observed behavior or participant statement。
- immediate consequence。
- artifact evidence。
- operator inference（事実とは分離）。

ただし、`STOP-DATA-BOUNDARY` 等で**実資料投入前にsessionが停止した場合は、launch checklistのruntime data-path事実、participantの停止判断、その理由をraw observation相当として扱う**。KJ artifactが存在しないことを理由に除外しない。

「この人はKJ Atlasに向いている/向いていない」のような人物分類を主要分析単位にしない。

## 3. 最初に行わないこと

- value / UX / culture / feature request等の既成分類へカードを投入する。
- participantごとにpositive / negative scoreを付ける。
- 発言数・カード数・session時間を成果指標にする。
- 「また使いたい」のYes/Noだけでvalue realnessを判定する。
- 内部dogfoodの価値仮説に合う観察だけを先に抜き出す。
- no-use / stop / existing-workflow sufficiencyを失敗データとして除外する。
- `STOP-DATA-BOUNDARY` を「製品を実際に使っていない」ことだけを理由に除外する。
- 実践文化メタデータをKJ束ねの分類キーにする。

## 4. KJ integration sequence

### A. Raw cardization

session recordから、意味を保ったまま生カードを作る。

- 可能な限りparticipant wording / observable eventを保つ。
- operator inferenceは別カードまたは明示した推論として扱う。
- value vocabularyへ先に言い換えない。
- 一連の出来事が一つの体験を表している場合、細切れにしすぎない。
- pre-material stopでは、`runtime condition → participant decision → immediate consequence` を一つの体験として保持し、架空の操作体験を補わない。

### B. Grouping / label

カードの訴えの近さから束ねる。

- participant IDやpractice metadataを主な束ね基準にしない。
- opposing cardsを「どちらも大事」へ溶かさない。
- 孤立カードを無理に既存束へ入れない。
- no-use reasonとvalue momentが同じ構造の両側を表す場合、対立関係として保持する。
- provider/network/storage境界によるno-useを、操作UXや一般的privacy不安へ自動的に言い換えない。

### C. A-type diagram

最低限次を可視化する。

- 生じた価値。
- 既存workflowで十分な領域。
- 使わない理由。
- 操作/概念/data-control/accessibility上の摩擦。
- runtime AI/provider/network/storage境界で成立しなかった利用条件。
- 予想外の価値。
- 内部仮説への反証。
- participant/contextを越えて現れた関係。
- 文脈依存に見える関係。
- 未説明の空白。

### D. B-type prose

A型図解から文章化し、その後に原カードへ戻って次を検査する。

- 強い言い換えでparticipantの意味を変えていないか。
- 少数/否定的材料が消えていないか。
- operator inferenceをparticipant factへ昇格していないか。
- 「社会一般」へ過剰一般化していないか。
- 単一sessionのdata-boundary stopを恒久的な製品要求へ飛躍させていないか。

## 5. Hypothesis return

KJ統合を行った後に初めて、内部仮説へ戻す。

各仮説について次の5値を使う。

- **support**: 仮説の重要部分が第三者の独立した観察で支えられた。
- **modify**: 仮説の方向は残るが、内容・条件・説明を変える必要がある。
- **narrow**: 特定の仕事・文脈・条件に限定すれば成立する。
- **reject**: 観察が仮説と整合せず、維持する根拠が弱い。
- **unresolved**: 証拠不足または相反する証拠が残る。

「support」の件数を総合点にしない。

## 6. Primary job / switch reason判定

`PRODUCT-POSITION-01` へ返す候補は、少なくとも次を満たす必要がある。

1. 具体的な仕事の状況に結び付く。
2. 既存workflowとの差が説明できる。
3. 参加者の発言だけでなく、可能ならartifact / behavior上の変化がある。
4. KJ Atlasの機能名ではなく利用者の仕事として表現できる。
5. 使わない条件も対として説明できる。

例として「カードを束ねられる」はswitch reasonではない。「既存の要約では消える異論を残したまま、後から判断根拠へ戻る必要がある仕事」のように、仕事・条件へ戻す。

ただし、この例文そのものを参加者へ提示しない。

pre-material stopではartifact変化がないため、switch reasonの正証拠にはしない。一方で、**そのruntime/data-control条件下では利用仕事が成立しないというno-use / boundary evidence**として扱える。

## 7. Practice-culture analysis

`PRACTICE-CULTURE-01` へ返す際は、国籍/民族/世代/職種で文化型を作らない。

観察された差をまず次の関係として読む。

- meaning authority。
- consensus requirement。
- voice / anonymity。
- evidence visibility。
- data control。
- synchronous / asynchronous work。
- long-term revisit。
- expression / accessibility。

その後にのみ、既存の暫定不変条件を `support / modify / reject / unresolved` で評価する。

## 8. Cross-session threshold

初期V1/V2は統計的一般化を目的としない。

次を区別する。

- **single-context evidence**: 1つのsession/文脈でのみ観察。
- **cross-context recurrence**: 異なる実践文脈で同型の構造が再現。
- **context conflict**: 一方では価値、他方では摩擦/不要となる。
- **insufficient variation**: 比較した文脈が実質同質で結論不能。

2件で再現したから普遍価値とはしない。再現は次の検証優先度を上げる証拠として扱う。

同じprovider/storage設定で複数sessionが止まった場合、それだけで文脈横断再現とはみなさない。実践文脈とruntime条件の双方を確認する。

## 9. Finding triage

KJ統合後の所見を次へ振り分ける。

### V-F0

- 単一session所見。
- 未再現仮説。
- participant固有の好み。
- 追加資料/対照文脈待ち。
- 単一sessionのprovider/network/storage条件によるno-use。

### V-F1

既存issueのproblem statement / acceptance criteriaへ直接戻せる実使用証拠。

### V-F2

次をすべて満たす場合の新issue memo。

- 実利用で再現可能。
- 既存issueでは被覆不能。
- 実行可能な変更/検証がある。
- acceptance criteria / verification levelを書ける。
- 「使わない」を無理に機能要求へ変換していない。

### V-F3

`ADR-0047` のreal-use triggerを満たす場合だけADR候補。

- 横断的data / permission / sharing / safety trade-off。
- 利用段階の実質的変化。
- 非機能境界超過。
- 破壊的contract/schema変更。

## 10. Cognitive dogfoodとの比較

第三者分析をCase 001〜003の「正解確認」に使わない。

内部dogfoodの所見と第三者材料が異なる場合、次のいずれかを検討する。

- 内部dogfood固有の自己参照効果。
- 第三者文脈固有の制約。
- product maturity / onboarding差。
- runtime data boundary差。
- evidence不足。
- 本当に価値仮説が誤っている可能性。

衝突は解消すべきノイズではなく、次のKJ材料として保持する。

## 11. Publication / epistemic audit

公開用の分析を書いた後、`third-party-value-publication-boundary.md` に従って次を確認する。

- privacyのために省略した情報を、存在しないかのように扱っていない。
- publicに出せない証拠について、検証可能性の制限を明記した。
- participant wordingを匿名化の過程で強く一般化していない。
- 少数ケースから社会一般へ外挿していない。
- private launch/data-path evidenceをpublic説明から省略した場合、その省略でstop理由の意味を変えていない。

## 12. Exit condition

V1/V2後に最低限次を説明できれば、初期分析を完了とする。

- 具体的に生じたvalue moment。
- 既存workflowが十分だった領域。
- 最も強いno-use reason。
- runtime/data-control境界で成立しなかった条件（存在する場合）。
- 内部仮説を修正/縮小/棄却するcounterevidence。
- context間で共通/対立した構造。
- 次に必要な実利用検証。
- F0/F1/F2/F3 triage。

結論が `value realness not established` または `existing workflow sufficient`、あるいは `data boundary prevents safe use in this context` でも有効な完了結果である。
