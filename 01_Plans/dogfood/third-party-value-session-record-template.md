# Third-Party Value Session Record Template

> `VALUE-REALNESS-01` / `PRACTICE-CULTURE-01` の第三者実利用を、価値感想ではなく実資料・操作・停止理由へ戻れる形で記録する。
> このテンプレートはKJ Atlasの価値語彙を参加者へ先に教えるための質問票ではない。

## 0. Session metadata

- Session ID:
- Date:
- Operator:
- Participant alias:
- Participation basis: volunteer / collaborator / other
- Practice context summary:
- KJ Atlas version/commit:
- Session launch checklist reference:
- Launch verdict: GO / GO-WITH-REDUCTION / STOP-DATA-BOUNDARY / STOP-PARTICIPANT / STOP-OTHER
- Data handling agreement:
- Public / private record boundary:
- Withdrawal / deletion agreement:

### 0.1 Runtime data path actually used

- Execution mode: local / self-hosted / hosted / other / unknown
- AI enabled: yes / no
- AI provider / endpoint actually used: N/A / <record>
- Material sent outside KJ Atlas process/device: yes / no / partial / unknown
- What was sent externally: none / raw material / selected cards / derived text / metadata / other / unknown
- Provider-side retention/logging known: yes / no / N/A
- Operator-side request/response logging: yes / no / unknown / N/A
- Raw material retained after session: yes / no / partial
- KJ Atlas document/export retained: yes / no / partial
- Audio/video/screen capture used: yes / no / partial
- Storage location class: participant-controlled / operator-private / organization-controlled / other / none
- Planned retention/deletion point:

Record actual runtime behavior, not the product's general capability. If a field remained `unknown`, explain why it was acceptable for this material or why the session stopped.

## 1. Eligibility / safety check

- [ ] Participant can explain the material/context.
- [ ] Existing workflow can be described.
- [ ] Participant can stop at any time.
- [ ] Material can be handled under agreed permissions.
- [ ] No unapproved personal/confidential/third-party material is being introduced.
- [ ] Runtime AI/network/storage path was explained before first material entry.
- [ ] Any unresolved data-path uncertainty is compatible with the material conditions, or the session stopped before material entry.
- [ ] Session participation and public-Git publication were treated as separate decisions.

Deviation / limitation:

## 2. Baseline — before product-value vocabulary

### 2.1 Job to be done

- What is the participant trying to accomplish?
- What counts as a useful output today?
- Who consumes the output?

### 2.2 Existing workflow

- Tools:
- Steps:
- What already works well:
- Where friction occurs:
- What must remain traceable/revisitable:
- What does not need special handling:

### 2.3 Existing-workflow sufficiency hypothesis

- Participant says existing workflow is sufficient when:
- Participant says change would be worthwhile if:

> Operator inference is recorded separately. Do not rewrite the participant's account into KJ Atlas value vocabulary here.

## 3. Material context

- Material type(s):
- Approximate volume:
- Media: text / image / audio / mixed / other
- Update frequency:
- Sensitivity / confidentiality:
- Source ownership / authority:
- Can raw material be retained?: yes / no / partial
- If not, what evidence can be retained?:

## 4. Practice-context metadata

Use only for later omission checking. Do not group KJ cards by these fields.

- Individual / collaborative:
- Synchronous / asynchronous:
- Meaning authority:
- Consensus required: yes / no / mixed
- Evidence visibility:
- Anonymity needs:
- Data-control constraints:
- Accessibility considerations:
- Other local practice norms:

## 5. Raw observation log

| Obs ID | Stage | Trigger / material | Observed behavior or statement | Immediate consequence | Artifact evidence | Operator inference |
|---|---|---|---|---|---|---|
| O-001 | S1-S6 |  |  |  |  |  |

Do not normalize the observation into `value`, `UX issue`, or `culture issue` during collection.

## 6. Value / friction / counterevidence ledger

Fill after or near the end of the session, referring back to raw Obs IDs.

| Evidence ID | Type | Observation refs | What changed | Existing workflow comparison | Confidence |
|---|---|---|---|---|---|
| E-001 | value moment / friction / no-use / existing-workflow sufficient / counterevidence / unexpected value / stop |  |  |  |  |

## 7. Stage notes

### S1 — Material intake

- What was difficult to bring into KJ Atlas?
- What should remain outside the product?
- Did data-control constraints change the session?
- Did AI/provider/network/storage constraints require a reduced workflow?:

### S2 — Externalization

- Meaning-preserving cardization examples:
- Meaning loss / over-splitting examples:
- Need to return to sources:
- Visual representation effect:

### S3 — KJ integration

- New relationship discovered:
- Nothing new beyond existing workflow:
- Premature organization / closure:
- Dissent / isolated material treatment:
- Human-confirmation usefulness / burden:

### S4 — Decision / narrative return

- Can the participant explain the output from source material?:
- What remained undecided?:
- Handoff / export usefulness:
- Transcription or duplication burden:

### S5 — Revisit

- Could the work be resumed?:
- Could earlier reasoning be reconstructed?:
- What was lost?:
- What was easier/harder than the existing workflow?:

### S6 — Independent post-use explanation

Record participant wording as closely as practical.

- What helped?
- What was unnecessary?
- Where was the existing workflow better?
- What would they use next time, and why?
- When would they not use KJ Atlas?
- Who/what work does it seem unsuitable for?

## 8. Stop / withdrawal

- Session completed: yes / no / partial
- Stop point:
- Stop reason:
- Was stopping a product failure, a fit judgment, a data-control constraint, an accessibility barrier, or something else?:
- Did runtime data-path uncertainty or external processing contribute?:
- What should **not** be inferred from the stop?:

Stopping is a valid outcome. Do not convert it automatically into a feature request.

If the session stopped before material entry because the runtime data path was unacceptable or insufficiently known, preserve that as `no-use / governance evidence`; do not mark it invalid merely because no KJ artifact was produced.

## 9. Artifact references

- KJ Atlas document / InquiryJourney:
- Before/after screenshots or exports, if consented:
- Anonymized evidence:
- Existing-workflow comparison artifact:
- Material intentionally not retained:
- Private runtime/data-path evidence reference, if any:

## 10. Participant-level interpretation

Do this only after raw observations are recorded.

### 10.1 Switch reason

- Did a concrete switch reason emerge?: yes / no / unresolved
- Evidence:

### 10.2 Reuse reason

- Would there be a reason to reuse KJ Atlas for a similar job?: yes / no / conditional / unresolved
- Evidence / condition:

### 10.3 No-use reason

- Strongest reason not to use KJ Atlas:
- Is it rational under the participant's context?:
- Is it primarily workflow/value, runtime data boundary, practice fit, accessibility, or another condition?:

### 10.4 Primary-job relationship

- Candidate primary job supported:
- Candidate primary job narrowed/modified:
- Evidence that the hypothesized job is not needed:

## 11. Internal-hypothesis return

Do not show this section to the participant before S6.

| Internal hypothesis | Third-party evidence | Verdict | Explanation |
|---|---|---|---|
|  |  | support / modify / narrow / reject / unresolved |  |

If third-party evidence conflicts with cognitive dogfood, preserve the conflict instead of selecting the internal account by default.

## 12. Finding triage

| Finding | Raw evidence refs | Triage | Existing issue / new memo / ADR trigger | Why |
|---|---|---|---|---|
|  |  | V-F0 / V-F1 / V-F2 / V-F3 |  |  |

Rules:

- V-F0: raw observation/card remains enough.
- V-F1: return evidence to an existing issue.
- V-F2: new issue only when reproducible, uncovered, actionable, and testable.
- V-F3: ADR only when `ADR-0047` real-use trigger is present.

A single session's provider/storage condition is not automatically a product requirement. Preserve the raw no-use reason first.

## 13. Candidate follow-up sources / sessions

- Missing evidence:
- Candidate contrast context:
- Why another session could change the conclusion:

Do not add follow-up participants merely to confirm a preferred conclusion.

## 14. Session validity

- Independent baseline captured before value vocabulary: yes / no / N/A if stopped before baseline
- Raw observations preserved: yes / no
- Counterevidence / no-use was allowed: yes / no
- Participant could stop: yes / no
- Runtime data path disclosed before first material entry: yes / no / N/A because no material entered
- Data handling followed agreement: yes / no
- Public-Git publication treated separately from session participation: yes / no
- Operator inference separated from observation: yes / no
- Known contamination / leading:

Session validity verdict: valid / partial / invalid

A `STOP-DATA-BOUNDARY` or other pre-material stop can still be valid evidence if the stopping condition and participant decision were captured without leading. Invalid/partial sessions remain in the record with the reason; do not silently delete them.
