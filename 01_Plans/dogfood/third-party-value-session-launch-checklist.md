# 第三者価値検証 — Session開始前チェックリスト

- 状態: 各第三者sessionで、最初の実資料を入力する前に必ず確認する
- 日付: 2026-08-31
- 関連文書: `VALUE-REALNESS-01`, `third-party-value-validation-execution-plan.md`, `third-party-value-participant-brief.md`, `third-party-value-session-record-template.md`, `third-party-value-publication-boundary.md`

## 1. 目的

第三者価値検証では、本人の実資料、または本人が妥当だと確認した匿名化資料を扱う。

`public Gitへcommitしない`だけでは、資料がどこを通り、どこに残るかの説明として十分ではない。実行時にAI機能、外部provider、network endpoint、ログ、保存先等を使う場合、資料の一部が参加者または操作者の管理する端末・processの外へ送られる可能性がある。

このチェックリストは、**最初の実資料をKJ Atlasへ入力する前に、そのsessionで実際に使うデータ経路を確認し、参加者が理解・許容できる範囲でのみ続行する**ための操作者用gateである。

KJ Atlas製品全体について新しいprivacy保証を定義するものではない。sessionで実際に確認できた事実だけを記録し、分からないことは`unknown`のまま扱う。

## 2. 実行環境

- Session ID: `<record at execution>`
- KJ Atlas version / commit: `<record at execution>`
- Execution mode: local / self-hosted / hosted / other / unknown
- 参加者または操作者が管理するdevice / host上で動くか: yes / no / mixed / unknown
- 予定するworkflowでnetwork接続が必要か: yes / no / conditional / unknown

version、実行mode、data pathのいずれかを確認できない場合は、実資料を入れる前に確認する。確認できず、その不確実性を資料条件として許容できない場合は開始しない。

## 3. AI・外部処理の経路

予定するworkflowでAI機能を使う場合だけ記入する。使わない場合は`AI disabled for this session`と明記する。

- AI enabled for this session: yes / no
- AI provider / endpoint actually used: `<name / endpoint class / N/A / unknown>`
- KJ Atlasのprocess / device外へ資料が送られるか: yes / no / partial / unknown
- 外部へ送られ得る内容: `<raw material / selected cards / derived text / metadata / none / unknown>`
- 送信先を確認できているか: yes / no / N/A
- provider側のretention / loggingを確認できているか: yes / no / N/A
- 操作者側のrequest / response logging: yes / no / unknown / N/A
- 使用するcredential / accountの管理主体: participant / operator / organization / other / N/A

`unknown`が残り、参加者の資料条件としてその不確実性を許容できない場合は、AI機能を無効化する、匿名化を強める、別資料へ切り替える、またはsessionを停止する。

**検証を完遂するために、資料統制の条件を緩めない。** ここで停止した場合も、「この条件では使えない」というno-use / governance evidenceとして記録できる。

## 4. 保存・記録の経路

- Raw materialをsession後も保持するか: yes / no / partial
- KJ Atlas document / exportを保持するか: yes / no / partial
- 操作者メモを保持するか: yes / no / partial
- Audio recording: yes / no
- Video / screen recording: yes / no
- Screenshot / export capture: yes / no
- 保存場所の区分: participant-controlled / operator-private / organization-controlled / other / none
- 保持期間または削除時点: `<record at execution>`
- 作業directoryに影響する自動cloud sync: yes / no / unknown

raw materialをpublic Gitへ自動同期される場所へ置かない。安全な保存先を説明できない場合は、保存しない運用を選ぶ。

## 5. 公開範囲

- Public Git contains raw material: **no**
- Public Git contains raw transcript / audio / video: **no**
- Public Git contains identifiable artifact by default: **no**
- Candidate public evidence: sanitized derivative / existence note / none
- Participant-approved public scope: `<record before publication, not assumed at launch>`

sessionへの参加とpublic Gitへの公開を同じ同意として扱わない。公開は別のgateで判断する。

## 6. 中止・撤回と削除についての確認

開始前に最低限、次を確認する。

- [ ] 参加者は途中で停止できる。
- [ ] public commit前のworking materialについて、撤回時の扱いを確認した。
- [ ] public Gitへ一度公開した情報は、clone / fork / cache等から完全には回収できない可能性を説明した。
- [ ] public公開はsession完遂の条件ではない。

## 7. 参加者への説明

操作者は、実資料を入力する前に、そのsessionで実際に該当する範囲だけを平易な言葉で説明する。

少なくとも、次が参加者に理解されたことを確認する。

- どの資料を扱うか。
- その資料が端末やprocessの外へ送られるか。
- AIを使うか。使う場合、確認できている範囲でどこへ何が送られるか。
- session後に何を保存するか。
- public Gitへ何を置かないか。
- 不明点が残る場合は、続行せず停止できること。

この説明のためにKJ Atlasの価値仮説を教える必要はない。S0 baselineの中立性を守る。

## 8. 開始判定

実資料を入力する前に、次のいずれかを選ぶ。

- `GO`: data pathと保存範囲が資料条件に適合し、参加者が理解したうえで続行を選んだ。
- `GO-WITH-REDUCTION`: AI無効化、追加匿名化、保存なし等へ条件を縮小して続行する。
- `STOP-DATA-BOUNDARY`: data-control / provider / storageの不確実性または不適合により停止する。
- `STOP-PARTICIPANT`: 参加者が続行しないことを選んだ。
- `STOP-OTHER`: その他の理由で停止する。

Launch verdict: `<record at execution>`

Reason / reduction applied: `<record at execution>`

`STOP-*`は無効sessionを意味しない。資料統制やruntime境界によってKJ Atlasの利用が成立しなかった、という第三者価値の証拠になり得る。

## 9. 操作者の最終確認

**Launch verdictが空欄、またはruntime data pathに資料条件と両立しない未解決の`unknown`がある状態では、実資料を入力しない。**

このチェックリストは、参加者の法的同意書や、所属組織が必要とする情報セキュリティ承認の代わりにはならない。別途必要な承認がある場合は、それを満たさない限り開始しない。