# Third-Party Value Validation — Session Launch Checklist

- Status: Required before first material entry in each third-party session
- Date: 2026-08-31
- Related: `VALUE-REALNESS-01`, `third-party-value-validation-execution-plan.md`, `third-party-value-participant-brief.md`, `third-party-value-session-record-template.md`, `third-party-value-publication-boundary.md`

## 1. Purpose

第三者価値検証では、本人の実資料または本人が妥当と認める匿名化資料を扱う。

`public Gitへcommitしない` ことだけではdata handlingの説明として十分ではない。実行時にAI機能、外部provider、network endpoint、ログ、保存先等を使う場合、資料がparticipant/operatorの管理環境外へ出る可能性がある。

このchecklistは、**最初の実資料をKJ Atlasへ入力する前に、そのsessionで実際に使うruntime data pathを確認し、participantが理解した範囲だけで続行する**ためのoperator gateである。

製品の一般的なprivacy保証を新たに定義するものではない。sessionで実際に確認できた事実だけを記録し、不明点は不明のまま扱う。

## 2. Runtime identity

- Session ID: `<record at execution>`
- KJ Atlas version/commit: `<record at execution>`
- Execution mode: local / self-hosted / hosted / other / unknown
- Device / host under participant or operator control: yes / no / mixed / unknown
- Network connection required for the planned workflow: yes / no / conditional / unknown

version、mode、data pathのいずれかが確認できない場合、実資料投入前に解消するか、その不確実性を理由に停止する。

## 3. AI / external processing path

planned workflowでAI機能を使う場合だけ記入する。使わない場合は `AI disabled for this session` と明記する。

- AI enabled for this session: yes / no
- AI provider / endpoint actually used: `<name / endpoint class / N/A / unknown>`
- Material sent outside the KJ Atlas process/device: yes / no / partial / unknown
- What may be sent: `<raw material / selected cards / derived text / metadata / none / unknown>`
- Transport destination known: yes / no / N/A
- Provider-side retention/logging known: yes / no / N/A
- Operator-side request/response logging enabled: yes / no / unknown / N/A
- Relevant credentials/accounts belong to: participant / operator / organization / other / N/A

`unknown` が残り、participantの資料条件上その不確実性を許容できない場合は、AI機能を無効化する、資料をさらに匿名化する、代替資料へ切り替える、またはsessionを停止する。

**検証を完遂するためにdata-control条件を緩めない。** ここで停止すること自体をno-use / governance evidenceとして記録できる。

## 4. Storage / capture path

- Raw material retained after session: yes / no / partial
- KJ Atlas document/export retained: yes / no / partial
- Operator notes retained: yes / no / partial
- Audio recording: yes / no
- Video/screen recording: yes / no
- Screenshot/export capture: yes / no
- Storage location class: participant-controlled / operator-private / organization-controlled / other / none
- Planned retention period or deletion point: `<record at execution>`
- Automatic cloud sync affecting the working directory: yes / no / unknown

raw materialをpublic Gitへ自動同期される場所へ置かない。安全な保存先を説明できない場合は保存しない。

## 5. Publication boundary

- Public Git contains raw material: **no**
- Public Git contains raw transcript/audio/video: **no**
- Public Git contains identifiable artifact by default: **no**
- Candidate public evidence: sanitized derivative / existence note / none
- Participant-approved public scope: `<record before publication, not assumed at launch>`

session参加への同意とpublic Gitへの公開同意を同一視しない。公開は別gateとする。

## 6. Withdrawal / deletion understanding

開始前に最低限次を確認する。

- [ ] participantは途中停止できる。
- [ ] public commit前のworking materialについて、撤回時の扱いを確認した。
- [ ] public Gitへ一度公開した情報はclone/fork/cache等から完全回収できない可能性を説明した。
- [ ] public公開はsession完遂の条件ではない。

## 7. Participant-facing disclosure

operatorは実資料投入前に、sessionで実際に該当する範囲だけを平易に説明する。

最低限、次がparticipantに理解されたことを確認する。

- どの資料を扱うか。
- その資料がdevice/processの外へ送られるか。
- AIを使うか。使う場合、分かる範囲でどこへ送られるか。
- 何をsession後に保存するか。
- public Gitへ何を置かないか。
- 不明点が残る場合、続行せず止められること。

説明のためにKJ Atlasの価値仮説を教える必要はない。S0 baselineの中立性を維持する。

## 8. Launch verdict

実資料投入前に1つを選ぶ。

- `GO`: runtime data pathと保存範囲が資料条件に適合し、participantが理解して続行を選んだ。
- `GO-WITH-REDUCTION`: AI無効化、匿名化、保存なし等へ縮小して続行する。
- `STOP-DATA-BOUNDARY`: data-control / provider / storage不確実性のため停止する。
- `STOP-PARTICIPANT`: participantが続行しないことを選んだ。
- `STOP-OTHER`: その他。

Launch verdict: `<record at execution>`

Reason / reduction applied: `<record at execution>`

`STOP-*` は無効sessionを意味しない。資料統制やruntime境界がKJ Atlas利用を成立させないという、有効な第三者価値証拠になり得る。

## 9. Operator rule

**Launch verdictが空欄、またはruntime data pathに資料条件と両立しない未解決の `unknown` がある状態で実資料を投入しない。**

このchecklistを、参加者の法的同意書や組織の情報セキュリティ承認の代替として扱わない。必要な承認が別に存在する場合は、それを満たさない限り開始しない。
