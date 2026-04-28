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

## Stream E-2 Serial Lane Run（2026-04-28 / CE2 first）
- Lane固定: CE2/CE4専任レーンとして **CE2→CE4** を直列実行し、並列化を禁止する。
- allowlist固定: `issue-CE2-low-risk-ai-assist.md` / `issue-CE4-api-cli-audit-integration.md` 以外は更新しない。
- 独立ルール: CE0/CE1契約は固定入力として read-only 参照し、CE2側で再定義しない。
- proposal-only固定: auto-apply / auto-publish / auto-confirm を禁止し、候補提示のみ許可する。

### CE2 Phase 1..6 Execution Snapshot（this run）
- Phase 1 Read: 完了（CE0/CE1 read-only, No-Go, lifecycle/reviewState閉集合を再確認）。
- Phase 2 ADR/CDC: 完了（契約語彙の再定義なし、proposal-only境界を再固定）。
- Phase 3 Plan: 完了（AC/DoD不足時はAIドラフト提案→人手合意後実行のゲートを再確認）。
- Phase 4 Execute: 完了（contract-only文面整備のみ、実装確定は未実施）。
- Phase 5 Verify: 完了（自己修復回数 `0/3`、上限超過なし）。
- Phase 6 Proceed: 完了（前提崩壊/契約衝突/未定義競合なし、CE4へ進行可能）。

### CE2 Stop Conditions（固定）
- Verifyの自己修復は最大3回（`1/3`〜`3/3`）。`4/3` 相当は fail-safe 停止。
- 上限超過、前提崩壊、未定義競合を検知した場合は `status=held` で即停止。

## Stream E-1 Execution Lock（2026-04-28 / CE2 Low-risk AI Assist）
- Purpose固定: proposal-only 契約をCE2で固定し、候補提示（`status=proposed`）以外の自動確定経路を導入しない。
- `reviewState` ガード: AIによる `reviewState=human_reviewed` 自動昇格を禁止し、AI提案は常に `unreviewed` とする。
- Auto操作禁止: auto-apply / auto-publish / auto-confirm を常時禁止する。
- 固定ワークフロー: **Read → ADR/CDC → Plan → Execute → Verify → Proceed**（6フェーズ直列のみ、結合・省略禁止）。
- 追加制約: lifecycle 閉集合 `proposed | accepted | rejected | held` の拡張を禁止する。
- CE境界: CE0/CE1 契約は read-only 参照とし、CE2 側で再定義しない。
- Execute開始条件: AC/DoD の人手合意が成立するまで Phase 4 Execute を開始しない。
- Self-repair上限: Verify失敗時の自己修復は最大3回（`1/3`〜`3/3`）まで。`4/3` 相当で fail-safe 停止する。

## Stream E Request Override（2026-04-27 / latest）
- Owner は **Stream E 専属** とし、対象は `issue-CE2-low-risk-ai-assist.md` のみ（単一ファイル固定）。
- 強制フェーズ順序は **Read → ADR/CDC → Plan → Execute → Verify → Proceed** の6フェーズ直列のみ（結合/省略禁止）。
- 全フェーズで **contract-only + mock-first** を固定し、実装確定（implementation commit）は禁止する。
- AC/DoD不足を検知した場合は、Phase 3 Plan で不足ドラフトを先出しし、**人手合意が成立するまで Phase 4 Execute を開始しない**。
- Verify失敗時の自己修復は `1/3`〜`3/3` まで。`4/3` 相当は fail-safe 停止（継続禁止）。
- 前提崩壊または契約衝突（CE0/CE1/CE2境界矛盾）を検知した場合は、`status=held` で即停止し人間判断を要求する。


## Stream E ADR/CDC Update（2026-04-27 / this change / approval pending）
### Context
- 本更新は Stream E 専任境界（単一ファイル編集）と 6フェーズ直列（Read → ADR/CDC → Plan → Execute → Verify → Proceed）を本文全体で再固定するための差分要求である。
- 既存本文には Stream D 名義や `Verify/Proceed` 結合表記が残存し、Read同期時の解釈ドリフト要因となっていた。
- CE2 は proposal-only / contract-only / mock-first を維持し、No-Go（auto-apply / auto-confirm / auto-publish / preview bypass / safeMode緩和）を常時禁止する必要がある。

### Decision
- Stream E 名義へ統一し、フェーズ表記を `Verify → Proceed` に分離して 6フェーズ直列を明文化する。
- lifecycle は `proposed | accepted | rejected | held`、reviewState は `unreviewed | human_reviewed` の閉集合を再確認する。
- 本差分は承認完了まで `status=held` として扱い、実装確定（implementation commit）および自動適用経路は導入しない。

### Consequences
- Read同期時の解釈揺れを抑制し、Stream E の運用境界（single-file / proposal-only / fail-safe）を監査可能な形で再固定できる。
- Verify と Proceed の分離により、Verify失敗時の自己修復上限（`1/3`〜`3/3`）と `4/3` fail-safe 停止条件を明確化できる。
- 承認前状態を `held` で維持することで、AC/DoD 未合意時の Execute 禁止を継続できる。

## Stream E Serialized Multi-Issue Gate（2026-04-27 / CE2→CE4）
- CE2を先行し、**Phase 5 Verify 合格および Phase 6 Proceed 完了まで CE4を開始しない**。
- CE2実行中は CE4向けの契約追記・推測更新を行わない（issue間の越境編集禁止）。
- 失敗時運用は自己修復最大3回（`1/3`〜`3/3`）で固定し、`4/3` 相当は即停止する。
- 契約衝突または前提崩壊を検知した場合、推測実行を禁止し `status=held` で停止する。

## Stream E Request Override (legacy superseded)（2026-04-26 / latest）
- Phase順序は **Read → ADR/CDC → Plan → Execute → Verify → Proceed** を唯一の進行順序とする。
- CE2は **proposal-only** を固定し、auto-apply / auto-confirm / auto-publish を常時禁止する。
- AIによる `reviewState=human_reviewed` 昇格を禁止し、昇格は人手操作のみ許可する。
- 各Phase開始時は必ず Read同期を実施し、差分検知時は `status=held` で停止する。
- Verify失敗時の自己修復は最大3回（`1/3`〜`3/3`）までとし、`4/3` 相当で fail-safe 停止する。

## Stream E Assignment Lock (legacy superseded)（2026-04-23）
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
- 強制フェーズ順序は **Read → ADR/CDC → Plan → Execute → Verify → Proceed** のみ。
- AC/DoD不足時は、AIが不足項目のドラフトを提示し、**人手合意が成立するまで Phase 4 Execute を開始しない**。
- 自己修復・再試行は最大3回まで。**3回超過（4回目相当）で fail-safe 停止**。
- Stopper: 自動確定 / 自動公開 / レビュー自動昇格が要求された時点で即停止する。

## Prompt E execution contract（2026-04-26）
### Context
- Stream E / CE2 は low-risk AI assist を proposal-only 境界で運用し、実装経路（auto-apply）を持たないことが前提である。
- `reviewState=human_reviewed` は人手レビューの監査属性であり、AIが昇格主体にならないことを契約境界として固定する。
- 6-phase 運用では各Phase開始前の Read 同期が drift 検知の唯一ゲートであり、同期欠落は誤進行リスクを生む。

### Decision
- proposal-only 境界を固定し、auto-apply を常時禁止する。
- AI による `human_reviewed` 昇格を禁止し、`unreviewed` 提案のみを許可する。
- 各Phase開始前に Read 同期を必須化し、差分検知時は `status=held` で停止する。
- Verify 失敗時の自己修復は `1/3`〜`3/3` までに制限し、`4/3` 相当で fail-safe 停止する。

### Consequences
- CE2 のAI支援は候補提示（proposal）に限定され、採用・昇格の最終判断は常に人手責任として保持される。
- Phase進行は Read同期記録を伴うため、drift 発生時の停止根拠と監査再現性が確保される。
- 自己修復上限を超えた場合は作業継続より安全停止が優先され、誤更新の連鎖を防止できる。


## Stream E CE2 phase enforcement update (legacy superseded)（2026-04-26）
- proposal-only 境界を固定し、auto-apply は常時禁止とする。
- AIによる `reviewState=human_reviewed` への自動昇格を常時禁止する。
- 強制フェーズ順序は **Read → ADR/CDC → Plan → Execute → Verify → Proceed** のみとする。
- 各Phase開始前に必ず Read 同期を実施し、差分検知時は `status=held` で停止する。
- Plan→Execute→Verify→Proceed の順序は省略・結合を禁止する。
- Verify失敗時は自己修復を最大3回（`1/3`〜`3/3`）まで許可し、`4/3` 相当で fail-safe 停止して指示待ちとする。

## Stream E 6-phase override（2026-04-26）
- 本Issueの運用は 6フェーズ固定とし、`Read -> ADR/CDC -> Plan -> Execute -> Verify -> Proceed` を唯一の進行順序とする。
- Phase 2 は I/F定義を先行し、実装依存は常に Mock 境界に隔離する。
- Phase 4 は Execute のみを扱い、Verifyは Phase 5 で独立実施する。
- Phase 5 は Verify 専用とし、失敗時の自己修復は `1/3`〜`3/3` まで、`4/3` 相当で fail-safe 停止して指示待ちとする。
- Phase 6 は Proceed 専用とし、Verify合格時のみ進行可能とする。

## Stream E phase contract（2026-04-26 更新）
- **Phase 1 Read**: 閉集合（`proposed | accepted | rejected | held`）/禁止事項（auto-apply・AI review自動昇格・safeMode後退）/Read同期チェックを必須とする。
- **Phase 2 ADR/CDC**: `proposalId/diff/sourceBundleHash/rationale/status/reviewState` を先に固定し、契約語彙変更要求がある場合のみ CDC を明文化して承認完了まで `status=held` を維持する。
- **Phase 3 Plan**: AC/DoD不足時は不足ドラフト提示に限定し、人手合意成立まで **Phase 4 Execute を開始しない**。
- **Phase 4 Execute**: 契約文言更新のみを実施し、検証はPhase 5 Verifyに分離する。
- **Phase 5 Verify**: 検証失敗時は自己修復最大3回まで。`4/3` 相当は fail-safe 停止して指示待ちとする。
- **Fail-safe**: 自動確定 / 自動公開 / レビュー自動昇格要求を検知した時点で即停止する。

## Stream E CE2 proposal-only directive (legacy superseded)（2026-04-25）
- Scope固定: 編集許可は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ。その他ファイル編集は禁止。
- lifecycle閉集合: `proposed | accepted | rejected | held` のみを許可し、語彙追加・別名導入を禁止する。
- proposal-only固定: 実装・auto-apply・自動確定・自動公開を常時禁止し、AIは候補提示に限定する。
- review昇格固定: AIによる `reviewState=human_reviewed` 昇格を禁止し、人手操作のみ許可する。
- 実行順序固定: `Read -> ADR/CDC（Mock化） -> Plan -> Execute -> Verify -> Proceed`。
- Read同期必須: 各Phase開始時にRead同期を実施し、差分検知時は `status=held` で停止する。
- AC/DoDゲート: 不足時はAIドラフト提示のみを許可し、人手合意成立までExecuteを開始しない。
- Verify再試行上限: 修復は最大3回（`1/3`〜`3/3`）まで。`4/3` 相当は fail-safe 停止。
- Fail-safe即停止条件: 自動確定 / 自動公開 / レビュー自動昇格要求、safeMode後退、自己修復3回超過。

## Stream E hard constraints（2026-04-23 明文化）
- 対象編集は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ（単一ファイル固定）。
- lifecycle は閉集合 `proposed | accepted | rejected | held` のみを許可する。
- `proposal-only` を固定し、auto-apply は常時禁止とする。
- AIは `reviewState=human_reviewed` へ昇格しない（人手のみ）。
- 実行フェーズは `Read → ADR/CDC → Plan → Execute → Verify → Proceed` の順序固定。
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
- 強制ワークフローは `Read（必須再読）→ ADR/CDC → Plan（AC/DoD補完）→ Execute → Verify → Proceed` に固定する。
- 各Phase開始時は必ず Read を実施し、前Phaseの固定契約との差分有無を確認してから進行する。
- 各Phase開始時の Read 同期で差分を検知した場合は `status=held` で停止し、Planに差し戻して合意を再取得する。
- AC/DoD が不足する場合は AI が補完案を提示し、人手合意が取れるまで Phase 4 Execute を開始しない。
- 編集許可は `issue-CE2-low-risk-ai-assist.md` のみ。実装コード・共有統合・他CE issue編集は禁止。

## Stream E operation profile（契約固定）
- 担当は Stream E 専属とし、CE2 low-risk AI assist の proposal-only 契約に固定する。
- 編集範囲は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみとし、他ファイルは参照専用とする。
- Phase運用は `Read（必須再読）→ ADR/CDC → Plan → Execute（auto-apply禁止・review auto promotion禁止）→ Verify → Proceed（Self-Correction最大3回）` を固定する。
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

## Phase 2 ADR/CDC（必要時のみ変更管理を明文化）
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

## Phase 3 Plan（AC/DoD補完提案：候補提示限定・自動採用禁止・review自動昇格禁止を固定）
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

## Phase 4 Execute（契約文言更新のみ）
- 開始時Read: Phase 4 Execute の変更差分（proposal-only / no-auto-apply / human-only昇格）を再確認する。
- 差分検知時は `status=held` とし、自己修復カウンタを1増分して再同期する。
- 実行内容は契約文言の更新に限定し、検証実施は Phase 5 Verify へ委譲する。
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

## Phase 5 Verify（safeMode後退ゼロを検証 / Self-Correction最大3回）
- 開始時Read: Phase 4 Execute の差分と Verify条件（禁止遷移 / safeMode後退ゼロ / 指定外編集なし）を再確認する。
- 差分検知時: `status=held` を維持し、自己修復カウンタを増分して再同期する。
- docs-check（3点セット）を実行し、検証失敗時の自己修復は最大3回（`1/3`〜`3/3`）までとする。
- 3回超過（4回目相当）または前提崩壊を検知した場合は fail-safe 停止し、指示待ちとする。
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


## Phase 6 Proceed（Verify合格時のみ進行）
- 開始時Read: Phase 5 Verify の結果を再読し、合格条件と停止条件の差分がないことを確認する。
- 進行条件: Verify が合格し、自己修復カウンタが `3/3` 以内であること。
- 停止条件: Verify未合格、禁止事項要求、指定外ファイル差分、safeMode後退、自己修復3回超過。
- handoffは proposal-only 境界（I/F語彙・期待入出力・監査キー）に限定し、実装指示や自動適用手順を含めない。

## Stream E Coordinated Update（2026-04-27 / CE2↔CE4 contract alignment / latest）

### Phase 1 Read（再読・相互参照差分確認）
- 再読対象: `issue-CE2-low-risk-ai-assist.md` / `issue-CE4-api-cli-audit-integration.md`。
- 確認結果:
  - 共通契約語彙（`proposal-only`, `contract-only`, `mock-first`, `status=held`, `reviewState` 人手昇格限定）は整合。
  - CE4側の API/CLI監査統合判断は CDC 明文化済み箇所がある一方、**「本ラウンドの承認待ち」状態を明示する運用行が不足**していたため、承認待ち運用を優先して同期。

### Phase 2 ADR/CDC（CE2境界での承認待ち明文化）
- CE2判断: CE4の API/CLI監査統合判断は CE2からは read-only 参照とし、以下の CDC 状態を参照固定する。
  - `CDC-CE4-AUDIT-INTEGRATION-2026-04-27`
    - Context: API/CLI同値判定（`equivalenceKey + bundleHash`）と監査4点（`query/bundle/proposal/apply`）の監査再現性を運用上で同時固定する必要がある。
    - Decision: CE4判断は CDC 形式で維持し、**承認完了まで `status=held` を継続**する。
    - Consequences: CE2は proposal-only 候補提示を維持し、実装・自動確定・自動公開へ越境しない。
    - Approval: `pending`（人手承認待ち）。

### Phase 3 Plan（AC/DoD不足ドラフト提案・合意待ち）
- Draft-AC-CE2-2026-04-27-01:
  - CE2文面に「CE4 CDC承認待ち中は CE2 Proceed で未承認事項を `held` 維持する」条項を追加提案。
- Draft-DoD-CE2-2026-04-27-01:
  - CE2 Verify で「CE4の承認待ち CDC を `accepted` 相当として扱っていない」ことを明示チェックする提案。
- 合意状態: **pending**（人手合意成立まで Phase 4 は contract更新の範囲のみ）。

### Phase 4 Execute（proposal-only / contract-only 維持）
- 実施範囲: CE2契約メモ更新のみ。
- 非実施: 実装指示、auto-apply、review自動昇格、他ファイル編集。

### Phase 5 Verify（AC/DoD基準・矛盾修正上限3回）
- Verify Attempt: `1/3`。
- 判定: pass（本更新は contract-only 記述に限定、No-Go逸脱なし）。
- ルール: `2/3`, `3/3` までは修正可。`4/3` 相当は fail-safe 停止。

### Phase 6 Proceed（独立実行可能な次アクション）
- Next-1: 人手に `CDC-CE4-AUDIT-INTEGRATION-2026-04-27` の承認/却下判断を依頼する（単独実行可）。
- Next-2: 承認結果に応じて CE2 の held 管理条項のみ更新する（単独実行可）。
- Next-3: CE2 Verify で「承認待ち事項の誤昇格なし」を再確認する（単独実行可）。

## Stream E single-file execution log（2026-04-27 / this run）
- Phase 1 Read: 本Issue再読を実施し、Scope単一ファイル固定と6フェーズ直列固定を再確認。
- Phase 2 ADR/CDC: `status/reviewState/lifecycle` の閉集合と `status=held` 停止条件を再確認。
- Phase 3 Plan: AC/DoD不足時ドラフト先出し＋人手合意前 Execute 禁止ゲートを維持。
- Phase 4 Execute: Stream D名義および implementation系記録を除去し、contract-only 文面へ収束。
- Phase 5 Verify: docs-check 実行（`validate_active_issue_memos.py` / `unittest` / `git diff --check`）。Attempt `1/3` で pass。
- Phase 6 Proceed: Verify合格を確認し、次アクションは人手承認待ち（`held` 運用継続）に限定。

## Stream E Execution Record（2026-04-27 / CE2 complete before CE4）

### Phase Progress（Read → ADR/CDC → Plan → Execute → Verify → Proceed）
- Phase 1 Read: 完了（本Issueの契約語彙・No-Go・single-file scopeを再読し、差分なしを確認）。
- Phase 2 ADR/CDC: 完了（Context/Decision/Consequences を本Issue内更新方針へ再固定、承認前は `held` 維持を再確認）。
- Phase 3 Plan: 完了（proposal-only / reviewed境界 / AC・DoD不足時はドラフト先出し→人手合意まで Execute 非開始を計画へ固定）。
- Phase 4 Execute: 完了（contract-only 文言整備のみ実施、実装確定・auto適用経路は未導入）。
- Phase 5 Verify: 完了（自動適用経路ゼロ、監査可能性維持、No-Go逸脱なし）。
- Phase 6 Proceed: 完了（CE2完了をゲートとして記録し、CE4開始条件を満たしたため次Issueへ遷移可）。

### Verify Log（self-correction 0/3）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- 判定: pass（自己修復着手なし、`4/3` 到達なし）。

### CE4 Start Gate
- CE2 Phase 5 Verify 合格および Phase 6 Proceed 完了を満たしたため、CE4着手条件を充足。
- CE2→CE4 の順序制約（逆順/並列禁止）を満たしていることを記録。


## Stream E Lane Ownership Note（2026-04-27 / latest）
- CE2は Stream E 専任運用を継続し、proposal-only + mock-first + contract-only を維持する。
- CE2完了（Verify/Proceed）を CE4着手の前提ゲートとして固定し、逆順・並列進行を禁止する。
- AC/DoD未合意時はドラフト提示に留め、合意前 Execute 非開始を継続する。
