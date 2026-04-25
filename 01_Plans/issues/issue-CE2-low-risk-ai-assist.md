# Issue Draft: CE2 Low-Risk AI Assist（Stream E専任 / CE契約群 / proposal-only / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream E（CE2専任 / proposal-only契約固定）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE2-low-risk-ai-assist.md` のみ
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`


## Stream E Assignment Lock（2026-04-23）
- 担当範囲は Stream E 専任とし、CE2 proposal-only 契約固定のみを扱う。
- 編集許可は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみに限定し、それ以外は編集禁止。
- lifecycle は閉集合 `proposed | accepted | rejected | held` のみを許可し、拡張しない。
- AI による `human_reviewed` 昇格は禁止し、`reviewState` の人手昇格のみ許可する。
- auto-apply は禁止し、提案は常に proposal-only 境界に留める。
- フェイルセーフは lifecycle拡張 / review昇格違反 / safeMode後退 / 指定外編集を即停止条件とする。

## Operator Directive（固定）
- 専有編集ファイルは `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ。
- CE2は **proposal-only** を固定し、実装・auto-apply は常時禁止。
- AIによる `reviewState=human_reviewed` への昇格は常時禁止（人手操作のみ）。
- CE0/CE1 契約は **参照専用** とし、CE2側で再定義・拡張しない。
- 強制フェーズ順序は **Phase 1 Read（必須再読）→ Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed** のみ。
- AC/DoD不足時は、AIが不足項目のドラフトを提示し、**人手合意が成立するまで Phase 4 Execute を開始しない**。
- 自己修復・再試行は最大3回まで。**3回超過（4回目相当）で fail-safe 停止**。
- Stopper: 自動確定 / 自動公開 / レビュー自動昇格が要求された時点で即停止する。

## Stream E phase contract（2026-04-25 追記）
- **Phase 1 Read**: 閉集合（`proposed | accepted | rejected | held`）/禁止事項（auto-apply・AI review自動昇格・safeMode後退）/Read同期チェックを必須とする。
- **Phase 2 ADR/CDC**: 契約語彙の変更要求がある場合のみ CDC を明文化し、承認完了まで `status=held` を維持する。
- **Phase 3 Plan**: AC/DoD不足時は不足ドラフト提示に限定し、人手合意成立まで **Phase 4 Execute を開始しない**。
- **Phase 4 Execute**: 契約文言更新のみに限定し、実装指示・自動適用手順・運用権限付与を記載しない。
- **Phase 5 Verify**: 禁止遷移・safeMode後退・指定外編集を検査し、自己修復は最大3回（`1/3`〜`3/3`）まで。
- **Phase 6 Proceed**: 条件未充足時は `held` で停止し、確定扱いで次工程へ渡さない。
- **Fail-safe**: 自動確定 / 自動公開 / レビュー自動昇格要求を検知した時点で即停止する。

## Stream E hard constraints（2026-04-23 明文化）
- 対象編集は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ（単一ファイル固定）。
- lifecycle は閉集合 `proposed | accepted | rejected | held` のみを許可する。
- `proposal-only` を固定し、auto-apply は常時禁止とする。
- AIは `reviewState=human_reviewed` へ昇格しない（人手のみ）。
- 実行フェーズは `Read（必須再読）→ ADR/CDC → Plan → Execute → Verify → Proceed` の順序固定。
- 各Phase開始時に Read同期を必須化し、差分検知時は `status=held` で停止する。
- AC/DoD不足時は AIドラフト提示のみに限定し、人手合意まで Execute を禁止する。
- 自己修復は最大3回（`1/3`〜`3/3`）まで。`4/3` 相当は fail-safe 停止。

## Phase Compliance Ledger（運用記録テンプレ / 毎Phase開始時に更新）
- Purpose: 各Phase開始時の Read 同期と固定契約の再確認を記録し、proposal-only 契約逸脱を防止する。
- Self-Correction Counter: `0/3`（検証失敗ごとに `+1`。`4/3` 相当は fail-safe 停止）
- Allowed State Set（固定）:
  - lifecycle: `proposed | accepted | rejected | held`
  - reviewState: `unreviewed | human_reviewed`
- Forbidden Actions（固定）:
  - auto-apply
  - AIによる `reviewState=human_reviewed` 自動昇格
  - safeMode既定緩和 / preview bypass

### Phase start checklist（全Phase共通）
- [ ] 開始時 Read 同期を実施し、前Phaseとの差分有無を確認した。
- [ ] 差分が検知された場合、`status=held` を設定して停止した（次Phaseへ進まない）。
- [ ] proposal-only 契約固定（実装禁止 / auto-apply禁止）を再確認した。
- [ ] `reviewState` の閉集合（`unreviewed | human_reviewed`）維持を再確認した。
- [ ] AC/DoD未合意の場合、`status=held` のまま Execute 非開始を確認した。
- [ ] Self-Correction Counter が `3/3` 以内であることを確認した（超過時は停止）。

## Lane guard（固定）
- proposal lifecycle は `proposed | accepted | rejected | held` を固定し、再定義しない。
- lifecycle は閉集合（closed set）として扱い、`proposed | accepted | rejected | held` 以外への拡張を禁止する。
- CE2 proposal lifecycle は `proposed | accepted | rejected | held` 以外を許可しない（固定）。
- CE2は **proposal-only 契約固定**（実装禁止）。
- CE1/CE0契約は参照専用（CE2で再定義しない）。
- auto-apply は常時禁止。
- `reviewState=human_reviewed` のAI自動昇格は禁止（人手のみ）。
- `reviewState` は `unreviewed | human_reviewed` のみ許可し、AI提案は常に `unreviewed` に固定する。
- 強制ワークフローは `Phase 1 Read（必須再読）→ Phase 2 ADR/CDC → Phase 3 Plan（AC/DoD補完）→ Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed` に固定する。
- 各Phase開始時は必ず Read を実施し、前Phaseの固定契約との差分有無を確認してから進行する。
- 各Phase開始時の Read 同期で差分を検知した場合は `status=held` で停止し、Planに差し戻して合意を再取得する。
- AC/DoD が不足する場合は AI が補完案を提示し、人手合意が取れるまで Execute を開始しない。
- 編集許可は `issue-CE2-low-risk-ai-assist.md` のみ。実装コード・共有統合・他CE issue編集は禁止。

## Stream E operation profile（契約固定）
- 担当は Stream E 専属とし、CE2 low-risk AI assist の proposal-only 契約に固定する。
- 編集範囲は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみとし、他ファイルは参照専用とする。
- Phase運用は `Phase 1 Read（必須再読）→ Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute（status: proposed|accepted|rejected|held）→ Phase 5 Verify（auto-apply禁止・review auto promotion禁止）→ Phase 6 Proceed` を固定する。
- `accepted/rejected/held` は人手判断の結果としてのみ遷移可能とし、AIは `proposed` の候補提示に限定する。
- 状態語彙の追加要求、SafeMode後退要求、または自己修復3回超過時は fail-safe で即停止する。

### Stream E fixed gate（本Issue内での運用固定）
- Gate-1（proposal-only）: CE2は提案文言の作成・更新に限定し、実装/auto-apply経路を作らない。
- Gate-2（lifecycle固定）: `proposed | accepted | rejected | held` 以外の語彙を導入しない。
- Gate-3（review昇格禁止）: AI提案の `reviewState` は常に `unreviewed`。`human_reviewed` は人手操作のみ。
- Gate-4（AC/DoD先行）: AC/DoD不足時は先にドラフト提案と人手合意を完了し、Executeに進まない。
- Gate-5（自己修復上限）: 検証失敗時の自己修復は最大3回。4回目相当は fail-safe 停止。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### Phase 1 gate（固定）
- proposal-only 契約固定、`reviewState` 制約、No-Go語彙（`auto-apply` / AI review自動昇格 / `preview bypass` / `safeMode既定緩和`）を開始時に必ず確認する。
- 差分検知時は `status=held` とし、Resolve前に次Phaseへ進まない。

### Read同期スナップショット
- 固定語彙: `sourceBundleHash` / proposal lifecycle / `equivalenceKey + bundleHash`（CE4同値判定参照）
- No-Go語彙: `auto-apply` / AI review自動昇格 / `preview bypass` / `safeMode既定緩和`
- `reviewState` 語彙: `unreviewed | human_reviewed`（昇格は人手のみ）

### Phase 1 逸脱候補チェックリスト（列挙固定）
- lifecycleが `proposed | accepted | rejected | held` 以外の語彙を含む。
- `reviewState` が `unreviewed | human_reviewed` 以外を含む、またはAIが `human_reviewed` 昇格主体として記述されている。
- No-Go語彙（`auto-apply` / `preview bypass` / `safeMode既定緩和`）を許可・示唆する文言がある。
- CE0/CE1契約の再定義・拡張をCE2側で行う文言がある。
- proposal-only契約を逸脱して、実装・反映・適用をAI実行可能と読める文言がある。

### Contract IDs
- `CE2-PROPOSAL-IF`
- `CE2-LIFECYCLE-IF`
- `CE2-DRIFT-STOP-IF`
- `CE2-NO-AUTOAPPLY-IF`

### Proposal I/F
- 必須: `proposalId/diff/sourceBundleHash/rationale/status/reviewState`
- `status`: `proposed | accepted | rejected | held`
- `reviewState`: `unreviewed | human_reviewed`

### No-Go / safeMode境界
- auto-apply 禁止
- AIによる `human_reviewed` 自動昇格禁止
- `CE0-SAFEMODE-IF` を参照し、CE2側で緩和しない

## Phase 2 ADR/CDC（必要時のみ実施：契約語彙変更要求の承認待ちを固定）
- 開始時Read: Phase 1 Read（必須再読）で固定した lifecycle / reviewState / No-Go語彙との差分を再確認する。
- 差分検知時: `status=held` を維持し、差分解消と人手合意が完了するまで Plan から先へ進まない。
- Execute開始ゲート: AC/DoD不足時はAIがドラフト提案のみ行い、人手合意前は Phase 4 Execute を開始しない。
- AC/DoD不足時: AIは不足項目のドラフトのみ提示し、合意済みAC/DoDが揃うまで `status=held` を維持する。禁止事項要求が出た時点で即停止する。
- Scope（固定）: proposal-only契約の文言整備のみ。契約語彙の追加・再定義・実装仕様化は対象外。
- Non-goals（固定）: 実装変更、auto-apply導入、review自動昇格、safeMode既定緩和、他issue編集。
- Validation（固定）: lifecycle/reviewState/No-Go語彙/`sourceBundleHash` 整合を文面上で確認し、Verifyでdocs-checkを実行する。
- Stop Conditions（固定）: 未合意AC/DoD、契約再定義要求、No-Go許可要求、指定外ファイル差分、自己修復4回目相当。
- CE1参照境界: `sourceBundleHash` 比較キーのみ依存。
- CE4参照境界: `proposal/apply` 監査語彙を共通化し、同値判定は `equivalenceKey + bundleHash` を参照のみで利用。
- I/F固定項目: `proposalId` / `diff` / `sourceBundleHash` / `rationale` / `status` / `reviewState`
- CE2のAI支援は候補提示（proposal）に限定し、採用判定は人手のみ。
- `status=accepted` は人手承認の結果としてのみ遷移し、AIの自動採用は禁止。
- AC固定: PlanフェーズのAI支援は候補提示（複数案）に限定し、自動確定（auto-confirm）を禁止する。
- `reviewState=human_reviewed` は人手操作のみで遷移可能（AI提案は `unreviewed` 固定）。
- drift検知時は `status=held` で停止。
- CE2独自のquery語彙追加は禁止（再定義防止）。

### ADR/CDC（必要時のみ実施）
- 条件: CE2契約語彙（lifecycle / `sourceBundleHash` / `reviewState` / No-Go語彙）に変更要求が出た場合。
- 手順: CDCを明文化し、`status=held` で承認待ちに遷移してから次Phaseへ進む。
- 比較対象: `CE0-REVIEW-IF`, `CE0-SAFEMODE-IF`, `CE1-CTXB-IF`（参照のみ）。
- 判定: 不一致が1件でもあれば差分理由のみ記録し、CE2で再定義しない。
- ADR記述は必要時のみ `Context / Decision / Consequences` を明文化し、承認待ち中は `held` を維持する。

## Phase 3 Plan（AC/DoD補完：候補提示限定・自動採用禁止・review自動昇格禁止を固定）
- 開始時Read: Phase 2 ADR/CDC の合意内容を再読し、未合意項目があれば `held` で停止する。
- 差分検知時: `status=held` で停止し、勝手に解釈して更新しない。
- 実行開始条件: AC/DoDの人手合意が完了していること（未合意なら Execute 開始禁止）。
- proposal lifecycle は `proposed | accepted | rejected | held` に固定し、別名・追加語彙を導入しない。
- `reviewState` は `unreviewed | human_reviewed` の閉集合のみを許可し、AI提案は常に `unreviewed` に固定する。
- auto-apply と AIによる `reviewState=human_reviewed` 自動昇格を明示的に禁止する。
- 実行内容は proposal-only 契約文言の更新に限定し、実装手順・実行権限の記述は行わない。
- reviewed-only既定: Executeの検討対象は `human_reviewed` を優先し、`unreviewed` は明示許可がある場合のみ比較対象に含める。
- AIの実行結果は `status=proposed` 候補提示に限定し、`accepted/rejected/held` の確定遷移は人手判断に限定する。
- 差分検知ログ: proposal lifecycle、`sourceBundleHash`、No-Go語彙の不一致。
- **Context**: proposal lifecycle / review遷移 / drift-stop の衝突有無。
- **Decision**: proposal-only + no-auto-apply + human-only昇格を維持。
- **Consequences**: CE4監査で proposal/apply の追跡可能性が固定化。
- **Approval**: 差分発生時の反映状態は `held`。
- 追跡可能性要件: すべての提案変更は `proposalId` をキーに `patch/diff` と `sourceBundleHash` を紐付け、監査時に再現可能であること。
- 可逆比較要件: 変更前後の差分は常に reversible diff（戻し可能な比較）で記録し、片方向の確定更新を行わない。
- 監査導線: `proposal` と `apply` の監査トレースを分離し、CE2は proposal-only 契約境界を維持する。
- 監査証跡要件: `query/bundle/proposal/apply` の4点セット語彙を欠損なく残し、CE4へread-onlyで受け渡す。

## Phase 4 Execute（patch/diff追跡可能性を明文化）
- 開始時Read: Phase 3 Plan で合意した AC/DoD を必須再読し、未合意項目があれば `status=held` で停止する。
- 実行内容は proposal-only 契約文言の更新に限定し、実装手順・自動適用経路・権限付与手順を記載しない。
- proposal lifecycle は `proposed | accepted | rejected | held` の閉集合を維持し、語彙追加を行わない。
- AI提案の `reviewState` は `unreviewed` 固定とし、`human_reviewed` への昇格は人手操作のみに限定する。
- 禁止事項要求（auto-apply / 自動確定 / 自動公開 / レビュー自動昇格 / safeMode既定緩和）を受けた時点で即停止する。
- 追跡可能性要件として `proposalId` と `patch/diff` と `sourceBundleHash` を紐付け、監査時に再現可能な記録を保持する。

## Phase 5 Verify（safeMode後退ゼロを検証）
- 開始時Read: Phase 4 Execute の変更差分（proposal-only / no-auto-apply / human-only昇格）を再確認する。
- 差分検知時は `status=held` とし、自己修復カウンタを1増分して再同期する。
- docs-check（3点セット）を実行し、検証失敗時の自己修復は最大3回（`1/3`〜`3/3`）までとする。
- lifecycle は `proposed|accepted|rejected|held` の閉集合を維持し、`reviewState=human_reviewed` のAI昇格を許可しない。
- SafeMode後退、禁止事項要求、指定外ファイル差分を検知した場合は fail-safe で即停止する。

### Verify commands
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] auto-apply経路0件
- [ ] 候補提示（proposal）限定であり、自動採用経路0件
- [ ] 自動確定（auto-confirm）経路0件
- [ ] 自動公開（auto-publish）経路0件
- [ ] AI自動昇格0件
- [ ] lifecycle語彙が `proposed|accepted|rejected|held` 以外を含まない
- [ ] docs-check（3点セット）を実行し、自己修復は最大3回以内で収束
- [ ] 変更対象ファイルが `issue-CE2-low-risk-ai-assist.md` のみである

## Phase 6 Proceed（未確定は保留、3回超過や前提崩壊で停止）
- 開始時Read: Verify結果と fail-safe 判定条件（3回超過 / 前提崩壊 / 競合）を再確認する。
- 差分検知時: `status=held` を維持し、Proceedを実行せず停止する。
- 3回超過（4回目相当）または前提崩壊を検知した場合は Proceed を中止し、fail-safe 停止する。
- Proceed出力境界: A/Bテスト・UI検証へ渡す成果は mock 境界（I/F語彙・期待入出力・監査キー）に限定し、実装指示や自動適用手順を含めない。
### Fixed contract handoff
- Contract IDs: `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF`
- 禁止事項: auto-apply / AI review昇格 / safeMode緩和
- 禁止事項（追加）: auto-confirm / auto-publish
- 検証条件: lifecycle固定, drift-stop有効, docs-check pass
- handoff先: CE4監査（read-only）
- 未確定事項は `held` を維持し、確定扱いで次工程へ渡さない。

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 契約再定義要求の発生
- 未定義ファイル競合
- 指定外ファイル差分の発生
- SafeMode後退の兆候
- 依存前提崩壊（参照契約の欠損・整合不能を含む）
- 自動確定 / 自動公開 / レビュー自動昇格の要求


## Stream E execution log（2026-04-23）
- Phase 1 Read: Read Order（上流文書）と本Issue本文を再読して契約固定を同期。
- Phase 2 ADR/CDC: 契約語彙変更要求時のみCDCを明文化し、承認待ちは`held`を維持。
- Phase 3 Plan: AC/DoD不足時はドラフト提案のみ提示し、人手合意まで Execute を開始しない。
- Phase 4 Execute: 本Issueファイル内のみを更新し、指定外ファイルは未変更。
- Phase 5 Verify: docs-check 3点セット（validator / unittest / `git diff --check`）で差分妥当性を確認。
- Phase 6 Proceed: Go（Verify通過。契約固定を維持したまま次工程へ引き渡し可能）。
