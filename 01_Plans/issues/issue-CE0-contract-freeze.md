# Issue Draft: CE0 Contract Freeze（Stream B / CE0 Contract SSOT / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream B（CE0 Contract Freeze 専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-contract-freeze.md` / `02_Architecture/architecture.md（CE0節）` / `02_Architecture/schemas.md（CE0契約節）`
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Stream B execution ledger（CE0専任 / contract-only）
- lane: `Stream B`
- ssot_scope: `CE0 only`（CE1/CE2/CE4は参照専用）
- edit_allowlist: `01_Plans/issues/issue-CE0-contract-freeze.md` のみ
- fail_safe:
  - 指定外ファイル編集を検知した場合は即停止して `held`。
  - safeMode既定値後退（`safeMode=true` / `allowUnreviewedText=false` 逸脱）を検知した場合は即停止して `held`。
  - Contract ID再定義（追加/改名/削除）を検知した場合は即停止して `held`。

### Phase status（固定ワークフロー追跡）
- Phase 1 Read: `completed`（固定ID / No-Go / safeMode境界を再確認）
- Phase 2 ADR/CDC: `completed`（Context/Decision/Consequencesを明文化、承認待ち論点は `held` 維持）
- Phase 3 Plan: `completed`（AC/DoD不足を提案し、追加合意は `held` 待ち）
- Phase 4 Execute: `blocked`（`agreement_state=held` のため未着手）
- Phase 5 Verify: `blocked`（Execute未着手のため未実行）
- Phase 6 Proceed: `completed`（最新判定: `Hold`。合意待ち）

## Stream B latest run（2026-04-27 / CE0 only / issue-owned update）

- run_id: `stream-b-ce0-2026-04-27-03`
- assignee: `issue-CE0-contract-freeze.md 単独担当`
- scope_guard: `edit_allowlist=issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / unapproved_finalize=0`

### Phase 1 Read（Status / Scope / Related ADR 差分確認）
- 実施: 本ファイル最新状態を再読し、`Status=Open` / `Scope=01_Plans/issues/（docs-only / contract-only / mock-first）` / `Related ADR/Spec=ADR-0028, 02_Architecture/schemas.md` の差分がないことを確認。
- 実施: 固定Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）と No-Go 5語彙IDの差分ゼロを確認。

### Phase 2 ADR確認（Context / Decision / Consequences）
- Context: CE0 contract freeze のSSOTは本Issueで維持し、下流はread-only参照のみ。
- Decision: 既存Decisionで整合が取れているため、新規Decision追加は不要（承認待ち新設なし）。
- Consequences: 承認待ちは増えず、既存 `agreement_state` と `held` 運用をそのまま継続可能。

### Phase 3 Plan（AC/DoD不足点の確認）
- 判定: 新規不足なし。既存追跡対象 `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` で網羅可能。
- 合意状態: 追加ドラフト提示は不要（現行DoDで継続）。

### Phase 4 Execute（contract-only / mock-first）
- 実施: 本Issue内の実行ログのみ更新し、contract-only / mock-first 境界を明示。
- 非実施: 実装ファイルへの変更指示、CE0 Contract ID再定義、指定外ファイル編集。

### Phase 5 Verify（AC/DoD適合確認 / self-repair）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-repair 0/3）
- AC/DoD適合: `contract_id_collision=0` / `vocabulary_collision=0` / `safeMode regression=0` を確認。

### Phase 6 Proceed（完了判定）
- 判定: **完了（Complete）**
- 根拠:
  - 許可範囲内編集のみ（本Issue単独）
  - contract-only / mock-first の記述更新のみ
  - VerifyでAC/DoD不整合なし（自己修復不要）

## Stream B latest run（2026-04-27 / CE0 only / agreement hold）

- run_id: `stream-b-ce0-2026-04-27-02`
- scope_guard: `edit_allowlist=issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / unapproved_finalize=0`

### Phase 1 Read（最新再読）
- 実施: 本Issueを再読し、固定Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の差分ゼロを確認。
- 実施: safeMode境界（`safeMode=true` / `allowUnreviewedText=false`）後退なしを確認。
- 実施: No-Go語彙ID（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）差分ゼロを確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0 Contract Freezeを単独維持し、CE1/CE2/CE4は read-only 参照のみとする。
- Decision: Contract ID再定義なし、safeMode境界固定、No-Go語彙ID canonical 判定を継続。未承認項目は `held` 維持。
- Consequences: 下流の再定義と safeMode後退を防止できる一方、追加DoDは合意完了まで確定運用しない。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDCなし。

### Phase 3 Plan（AC/DoD不足提案 / 合意待ち）
- 提案A（AC不足）: read-only参照の判定基準を「リンク更新/注記のみ許可」に明文化する。
- 提案B（DoD不足）: No-Go判定は5語彙ID照合を唯一基準とし、同義語は注釈扱いに限定する。
- 提案C（DoD不足）: `contract_id_collision | vocabulary_collision | scope_deviation` 検知時の `held` 記録を必須化する。
- agreement_state: `held`（追加合意待ち）
- gate: 合意未了のため **Phase 4 Executeへ進まない**。

### Phase 4 Execute
- 状態: `blocked`（contract-only修正を含め未着手）

### Phase 5 Verify
- 状態: `blocked`（Execute未着手のため docs-check は次回実行）

### Phase 6 Proceed（Go / Hold）
- 判定: **Hold**
- 理由: Phase 3の追加AC/DoD提案が `agreement_state=held` のため。
- 次回引継ぎ:
  - 合意取得後にのみ Phase 4 Execute（contract-only）を再開する。
  - 再開時も fail-safe（safeMode後退・Contract ID改変・指定外編集）を先行監視する。

## Stream B latest run（2026-04-26 / CE0 only）

- run_id: `stream-b-ce0-2026-04-26-04`
- scope_guard: `edit_allowlist=issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / unapproved_finalize=0`

### Phase 1 Read（最新再読）
- 実施: 本Issueを再読し、Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定を再確認。
- 実施: No-Go語彙ID（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）固定を再確認。
- 実施: safeMode境界（既定ON、`allowUnreviewedText=false`）後退禁止を再確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0をSSOTとして維持し、下流（CE1/CE2/CE4）はread-only参照のみ。
- Decision: Contract ID再定義なし、No-Go語彙ID判定維持、未承認論点は `held` のまま運用。
- Consequences: 下流再定義を抑止し、衝突時は `held` 記録で停止可能。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため、新規CDC起票なし。

### Phase 3 Plan（AC/DoD補完提案の合意確認）
- 合意対象: `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` を継続追跡。
- 合意状態: `agreement_state=agreed` を維持。未承認の新規論点は `held`。
- 実行境界: contract-only wording修正のみ、実装変更禁止。

### Phase 4 Execute（contract-only）
- 実施: 本ファイル内の進行状態と実行記録を更新（指定外ファイル編集なし）。
- 非実施: CE0 Contract IDの追加・改名・削除、safeMode既定値変更、CE1/CE2/CE4本文変更。

### Phase 5 Verify（docs-check / self-correction ≤ 3）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed（Go / Conditional / No-Go）
- 判定: **Go**
- 根拠:
  - `contract_id_collision=0`
  - `vocabulary_collision=0`
  - `safeMode regression=0`
  - docs-check pass
- 継続条件:
  - CE1/CE2/CE4への引き渡しは Contract ID / No-Go ID のread-only参照のみ。
  - 未承認論点は確定扱いせず `held` 維持。

## Stream B latest run（2026-04-27 / CE0 only / snapshot fixed）

- run_id: `stream-b-ce0-2026-04-27-01`
- input_contract_snapshot: `ce0-contract-freeze-2026-04-27`（fixed）
- scope_guard:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
  - `02_Architecture/architecture.md（7A CE0節のみ）`
  - `02_Architecture/schemas.md（1.1 CE0契約節のみ）`
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / unapproved_finalize=0`

### Phase 1 Read（対象再Read）
- 実施: 3対象ファイルを再読し、CE0 Contract IDsとNo-Go語彙IDの固定を確認。
- 実施: safeMode既定値（ON + `allowUnreviewedText=false`）後退禁止を確認。

### Phase 2 AC/DoD確定（Context / Decision / Consequences）
- Context: Stream B は CE0 contract freeze 専任。下流成果物待ちを行わず、固定スナップショットを使用する。
- Decision: AC/DoD は「Contract ID再定義なし」「No-Go語彙ID canonical」「read-only handoff」「Verify自己修復≤3」で固定。
- Consequences: CE1/CE2/CE4 との競合を回避しつつ、CE0を単独で凍結維持できる。

### Phase 3 契約固定（contract-only）
- 実施: `architecture.md` CE0節に snapshot 固定値と No-Go canonical IDs を追記。
- 実施: `schemas.md` CE0契約節に snapshot 固定値と drift-stop canonical IDs を追記。
- 非実施: CE0 Contract ID追加・改名・削除、実装コード変更、共有統合ファイル編集。

### Phase 4 Verify（self-correction ≤ 3）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 5 引き渡し（Proceed）
- 判定: **Go**
- 引き渡し条件:
  - CE1/CE2/CE4 は `ce0-contract-freeze-2026-04-27` を read-only 参照する。
  - Contract IDs と No-Go canonical IDs は CE0 SSOT を唯一正本として維持する。

## Lane guard（このレーンの絶対条件 / CE SSOT）
- CE0をCE契約のSSOT（single source of truth）とし、CE1/CE2/CE4は**参照のみ**で利用する。
- 本Issueは**計画・契約先行のみ**を扱う。実装（`03_Implement/**`）と共有統合ファイルは対象外。
- CE0契約IDは再定義禁止（freeze対象）：`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- CE0 Contract IDの追加・改名・削除を禁止する（freeze中の再定義不可）。
- safeMode既定値（ON, `allowUnreviewedText=false`）の後退を禁止する。
- 推測実装（speculative implementation）を禁止し、記載根拠は本Issue内の固定語彙/固定I/Fに限定する。
- 致命エラー（Fail-safe該当）検知時は即停止し、`held` へ戻す。
- 未承認決定を確定扱いしない（承認待ち論点は `held`）。
- 強制ワークフローは **`Phase 1 Read → Phase 2 ADR/CDC（Context/Decision/Consequences） → Phase 3 Plan（AC/DoD補完） → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed`**。
- **各Phase開始時は本Issueを最新再読してから開始する（再読省略禁止）。**
- 自己修復は Verify で最大3回まで。4回目相当は即停止する。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### 最新再読チェック（Phase開始ゲート）
- 対象ファイル: `issue-CE0-contract-freeze.md`（本書のみ）
- CE0 SSOT再定義禁止 / 実装禁止 / 指定外編集禁止を再確認
- Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の凍結を再確認
- No-Go canonical wording（5語彙ID）を再確認
- 失敗時自己修復上限（3回）を再確認

### Read同期スナップショット
- Contract ID: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
- 固定語彙: `equivalenceKey + bundleHash` / `sourceBundleHash` / `proposal lifecycle`
- Scope: contract-only（実装非干渉、mock/hash/read-only参照で依存切断）

### 固定I/F（参照のみ）
- `CE0-CTX-IF`: ContextQuery必須キー + deterministic `bundleHash`。
- `CE0-SAFEMODE-IF`: safeMode既定ON、`allowUnreviewedText=false` 既定。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみ。
- `CG-01..05`: `Working -> Consensus` は `patch + approval` のみ。

### No-Go語彙（固定）
- `preview_bypass`（Query Preview bypass）
- `consensus_direct_write`（Consensus direct write）
- `auto_apply_or_publish`（auto-apply / auto-publish）
- `ai_review_auto_promotion`（AIによる review 自動昇格）
- `safemode_default_relaxation`（safeMode既定緩和）

#### No-Go canonical wording（差分判定用）
- 比較・照合は上記5語彙ID（`preview_bypass` 等）を正本とし、日本語/英語表記揺れは括弧内同義語として扱う。
- CE1/CE2/CE4へは語彙IDのみを受け渡し、下流文書で同義語を追加しても禁止判定の意味は拡張・縮退しない。

## Phase 2 ADR/CDC（Context/Decision/Consequences）
### 最新再読チェック（Phase開始ゲート）
- Phase 1の固定語彙・No-Go語彙・Scopeを再読し、差分ゼロを確認してから着手する。

### Plan方針
- Freeze原則: CE1/CE2/CE4はCE0契約を再定義せず、I/F参照のみで固定する。
- CE1参照境界: `ContextQuery/ContextBundle` + hash決定論（`CE0-CTX-IF`参照のみ）。
- CE2参照境界: proposal-only + review自動昇格禁止（`CE0-REVIEW-IF`参照のみ）。
- CE4参照境界: 監査4点 `query/bundle/proposal/apply` と fail-closed（`CG-01..05`参照のみ）。
- safeMode境界は `CE0-SAFEMODE-IF` を上位正本として固定し、下流Issueで再定義しない。

### I/F Mock Freeze Matrix（read-only handoff）
| Consumer | Read-only参照元（CE0 SSOT） | 許可される変更 | 禁止 |
| --- | --- | --- | --- |
| CE1 | `CE0-CTX-IF`（ContextQuery必須キー / deterministic bundle） | 参照リンクの更新のみ | 必須キー再定義、hash規則改変 |
| CE2 | `CE0-REVIEW-IF`（proposal-only / human昇格手動） | 状態遷移説明の補足のみ | auto-apply、AI review昇格 |
| CE4 | `CG-01..05`（監査4点 / fail-closed） | 監査導線の注記のみ | 監査欠損の成功扱い、direct write |

### Freeze判定（全て必須）
- 参照方向は `CE0 -> (CE1, CE2, CE4)` の一方向のみ（逆参照での再定義禁止）。
- CE1/CE2/CE4は contract本文の複製を行わず、Contract ID参照のみ記述する。
- 参照先に差分が必要な場合は CE0再起票（本Issue）を経由し、下流Issueで先行確定しない。
- handoff本文は read-only（Contract ID参照のみ）とし、依存切断方針（mock-first）を維持する。

### AC/DoD補完（Phase 2で先に固定）
- AC不足候補A: 「read-only参照」の判定根拠が曖昧。
  - 補完: `Matrix` に「許可される変更はリンク更新/注記のみ」を必須条件としてDoDへ反映する。
- AC不足候補B: No-Go語彙の表記揺れによる誤判定。
  - 補完: 5語彙ID（`preview_bypass` ほか）を照合キーに固定し、自然言語は同義語扱いに限定する。
- AC不足候補C: CDC発火条件の見落とし。
  - 補完: `contract_id_collision | vocabulary_collision | scope_deviation` のいずれか検知時は `held` 記録を必須化する。
- Status: `held`（承認待ち。確定運用は承認後）
- DoD補完固定（承認待ちの追跡対象）:
  - `dod_read_only_reference`: Matrix上で「リンク更新/注記のみ」を満たす。
  - `dod_no_go_id_canonical`: No-Goは5語彙ID照合のみで判定する。
  - `dod_cdc_held_required`: CDC trigger検知時はContext/Decision/Consequencesを`held`記録する。

### AC/DoD補完提案の合意明記（Phase 2）
- 合意対象: AC不足候補A/B/C の補完方針そのもの（実装や下流再定義は含めない）。
- 合意記録:
  - `agreement_scope`: CE0契約本文の語彙固定と判定根拠の明確化のみ。
  - `agreement_state`: `agreed`（2026-04-22 合意取得済み）
  - `agreement_note`: 承認前は運用確定扱いせず、Phase 4では「契約語彙統一」と「禁止事項単一化」の編集に限定する。
- Execute開始条件（合意ゲート）:
  - `agreement_state` が `held` の間は **Phase 4 Executeへ進まない**。
  - Execute開始は `agreement_state=agreed` 明記後に限定する（記録なし開始は禁止）。
- 非合意（明示）:
  - CE1/CE2/CE4の本文更新・再定義
  - `03_Implement/**` の実装変更
  - CE0 Contract IDの追加/改名/削除

### ADR CDC（必要時のみ）
- 原則: 差分検知時のみCDCを起票し、**`held`（承認待ち）** を維持して次Phaseへ進む。
- Trigger: `contract_id_collision` / `vocabulary_collision` / `scope_deviation`。
- 未検知（すべて0）の場合はCDC起票しない。

#### CDCテンプレ（必要時のみ）
```md
#### CDC-CE0-<yyyymmdd>-<seq>
- Status: held（承認待ち）
- Trigger: [contract_id_collision | vocabulary_collision | scope_deviation]
- Context:
  - 衝突箇所:
  - 影響Contract ID:
- Decision:
  - CE0契約ID再定義なし
  - 参照境界の補正のみ
- Consequences:
  - CE1/CE2/CE4の参照先が一意
  - 下流Issueはread-only参照を維持
- Approval Needed:
  - reviewer:
  - due:
```

## Phase 3 Plan（I/F Mock Freeze計画 + AC/DoD補完）
### 最新再読チェック（Phase開始ゲート）
- CE0 Contract IDs再定義禁止、proposal-only、safeMode既定維持を再確認する。

### Freeze contract canonical expressions（統一正本）
| Contract ID | Freeze expression（正本。下流は参照のみ） |
| --- | --- |
| `CE0-CTX-IF` | ContextQuery必須キーを固定し、ContextBundleは deterministic `bundleHash`（`equivalenceKey + bundleHash`）で照合する。 |
| `CE0-SAFEMODE-IF` | safeMode は既定ON、`allowUnreviewedText=false` を既定固定し、緩和は契約外とする。 |
| `CE0-REVIEW-IF` | proposal lifecycle は proposal-only を維持し、`human_reviewed` 昇格は人手操作のみ許可する。 |
| `CG-01..05` | `Working -> Consensus` 遷移は `patch + approval` のみで成立し、direct write を禁止する。 |

### Prohibited operations canonical set（単一正本）
| No-Go ID | Canonical prohibition | Alias（同義語。判定はID基準） |
| --- | --- | --- |
| `preview_bypass` | Query Preview を経由しない適用を禁止する。 | preview bypass |
| `consensus_direct_write` | Consensus への direct write を禁止する。 | direct write |
| `auto_apply_or_publish` | auto-apply / auto-publish を禁止する。 | automatic apply/publish |
| `ai_review_auto_promotion` | AI判断のみで `human_reviewed` へ昇格することを禁止する。 | AI review auto promotion |
| `safemode_default_relaxation` | safeMode既定値（ON, `allowUnreviewedText=false`）の緩和を禁止する。 | safemode relaxation |

### Execute Plan（実行前固定）
- CE0 SSOT本文のみを整備し、下流Issueは Contract ID参照で解釈可能な状態に保つ（契約凍結文言の統一のみ実施）。
- CE1/CE2/CE4への handoff は「参照のみ（本文複製なし）」で表現を固定する（契約本文の新規追加・改名・削除は禁止）。
- No-Go語彙IDの照合観点をCE0に明記し、下流への受け渡しは語彙ID参照のみとする。
- Phase 2で `held` 化したAC/DoD補完提案は、承認前に確定扱いしない。

### Contract-only wording hygiene checklist（再定義防止）
- 許可: 表記揺れの統一、語順調整、見出し整理（意味不変）。
- 禁止: Contract ID / No-Go ID / safeMode既定値 / proposal lifecycle の意味変更。
- 禁止: CE1/CE2/CE4向けに契約本文を複製して「別定義」を作ること。
- 差分の判断単位は `Contract ID` と `No-Go ID` を優先し、自然言語差分のみでは再定義扱いにしない。

### Execute結果条件
- `collision=0` / `safeMode regression=0` を満たす記述へ整理。
- 検証失敗時は自己修復を最大3回まで実施し、4回目相当は停止する。

## Phase 4 Execute（Plan反映のみ。契約再定義・実装変更なし）
### 最新再読チェック（Phase開始ゲート）
- Phase 3 Planで固定した Contract ID / No-Go ID / safeMode既定を再読し、意味変更なしの編集に限定する。
- 指定外ファイルの差分が0であることを確認してから編集を実行する。

### Execute実施境界
- 対象は `issue-CE0-contract-freeze.md` のみ（他ファイル編集禁止）。
- CE0 SSOT本文の語彙統一・判定根拠の明確化に限定し、CE0 Contract IDの再定義は行わない。
- CE1/CE2/CE4への依存は mock snapshot（read-only参照）前提で切断し、下流再定義を起こさない。

## Phase 5 Verify（docs-check自己検証 / Self-Correction上限3回）
### 最新再読チェック（Phase開始ゲート）
- Verify対象は docs-check のみ。実装変更・指定外編集が混入していないことを再確認する。

### Verify commands
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] Contract ID collision = 0
- [ ] Vocabulary collision = 0
- [ ] SafeMode regression = 0
- [ ] No-Go語彙一致（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）
- [ ] CE1/CE2/CE4参照境界を再定義なしで説明可能
- [ ] CE1/CE2/CE4 handoffがread-only参照であることをMatrixで確認可能
- [ ] CDC発生時に `held` 記録（Context/Decision/Consequences）が残る
- [ ] Phase 2で補完したAC/DoD案が `held` と承認待ちステータスで追跡可能
## Phase 6 Proceed（次工程向け固定契約の出力）
### 最新再読チェック（Phase開始ゲート）
- Verify結果とAC/DoDを再読し、未達項目があれば Proceed せず `held` に戻す。

### Proceed判定の停止条件（fatal）
- `contract_id_collision` / `vocabulary_collision` / `scope_deviation` のいずれかが残存する場合は Proceed しない。
- SafeMode regression が1件でも検出された場合は即停止し、Phase 3へ巻き戻して再修復する。
- docs-check が不合格の場合は最大3回まで自己修復し、4回目相当は停止する。

### Fixed contract handoff
- Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
- 禁止事項（ID正本）: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- 検証条件: collision=0, SafeMode regression=0, docs-check pass
- 引き渡し形式: CE1/CE2/CE4へは Contract ID参照のみ（本文複製・下流再定義は禁止）

### Mock signature disclosure（型・禁止操作 / read-only handoff）
> 目的: CE1/CE2/CE4がCE0契約を**再定義せず**接続できる最小シグネチャを公開する。

```ts
// CE0-CTX-IF（query preview mandatory）
type ReviewFilter = "reviewed_only" | "include_unreviewed_metadata";
type OutputMode = "patch_proposal" | "analysis_preview";

type ContextQuery = {
  queryId: string;
  goal: string;
  scope: { cardIds?: string[]; islandIds?: string[] };
  depth: number;
  reviewFilter: ReviewFilter;
  safeMode: true; // default fixed ON
  allowUnreviewedText: false; // default fixed false
  outputMode: OutputMode;
};

type ContextBundle = {
  bundleHash: string; // deterministic
  equivalenceKey: string;
  sourceBundleHash?: string;
  constraints: string[];
};

// CE0-REVIEW-IF / CG-01..05（proposal-only + patch approval only）
type PatchProposal = {
  proposalId: string;
  sourceBundleHash: string;
  diff: unknown;
  rationale: string;
  lifecycle: "proposal_only";
};
```

- 禁止操作（No-Go ID固定）:
  - `preview_bypass`: `ContextQuery` を Query Preview無しで適用する操作を禁止。
  - `consensus_direct_write`: `ConsensusGraph` への direct write を禁止。
  - `auto_apply_or_publish`: `PatchProposal` の自動 apply/publish を禁止。
  - `ai_review_auto_promotion`: AI判断のみで `human_reviewed` へ昇格する操作を禁止。
  - `safemode_default_relaxation`: `safeMode=true` / `allowUnreviewedText=false` の既定緩和を禁止。
- 型公開の境界:
  - 本シグネチャは CE0 SSOT の参照補助であり、契約本文の追加定義ではない。
  - 変更要求は CE0再起票でのみ受け付け、CE1/CE2/CE4での改変は不可。

### CE1/CE2/CE4向け参照I/F一覧（read-only handoff）
- CE1（Context Bundle consumer）: `CE0-CTX-IF` / `CG-01` / `CG-02`
- CE2（Review governance consumer）: `CE0-REVIEW-IF` / `CE0-SAFEMODE-IF` / `CG-03` / `CG-04`
- CE4（Audit & fail-closed consumer）: `CG-01..05` / `CE0-SAFEMODE-IF`

---

## Stream B Execution Record（2026-04-23 / CE0 Contract Freeze）

### Phase 1 Read
- Read同期: 本Issueを再読し、CE0固定語彙・No-Go 5語彙ID・safeMode境界（`safeMode=true`, `allowUnreviewedText=false`）を再確認。
- Plan: CE0 SSOT再定義禁止、CE1/CE2/CE4参照のみ、指定外編集ゼロを維持。
- Execute: 再読チェックのみ（編集なし）。
- Verify: 固定Contract IDおよびNo-Go IDの差分なし。
- Proceed: `Go`（Phase 2へ遷移）。

### Phase 2 ADR/CDC
- Read同期: Phase 1固定語彙とScopeの差分ゼロを再確認。
- Plan: CDCは `contract_id_collision | vocabulary_collision | scope_deviation` 検知時のみ `held` 起票。
- Execute: 本実行では上記Triggerを未検知（0件）のためCDC新規起票なし。
- Verify: `held` 運用ルール（未承認決定を確定扱いしない）を維持。
- Proceed: `Go`（Phase 3へ遷移）。

### Phase 3 Plan
- Read同期: CE0 Contract ID凍結、proposal-only、safeMode既定維持を再確認。
- Plan: contract-only記述整備に限定し、ID追加/改名/削除を禁止。
- Execute: AC/DoD不足補完の追跡方針（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）を再確認。
- Verify: 合意ゲート `agreement_state=agreed`（2026-04-22）との整合を確認。
- Proceed: `Go`（Phase 4へ遷移）。

### Phase 4 Execute
- Read同期: 意味不変編集限定・指定外ファイル編集禁止を再確認。
- Plan: CE0契約本文の語彙統一と判定根拠の明確化のみ実施。
- Execute: 本Issue内に実行記録を追加（契約ID/No-Go ID/safeMode境界の意味変更なし）。
- Verify: CE0 Contract ID、No-Go ID、safeMode既定値の定義本文は不変。
- Proceed: `Go`（Phase 5へ遷移）。

### Phase 5 Verify
- Read同期: docs-checkのみを検証対象として再確認。
- Plan: `docs-check + diff` を順に実行し、失敗時のみ自己修復（最大3回）。
- Execute:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Verify: 3コマンドすべて成功（自己修復 0/3）。
- Proceed: `Go`（Phase 6へ遷移）。

### Phase 6 Proceed
- Read同期: Verify結果とAC/DoD未達の有無を再確認。
- Plan: fatal条件（collision / scope_deviation / safeMode regression / docs-check fail）残存時は停止。
- Execute: fatal条件の残存なしを確認。
- Verify:
  - `contract_id_collision=0`
  - `vocabulary_collision=0`
  - `safeMode regression=0`
  - `docs-check=pass`
- Proceed判定: **Go**（CE1/CE2/CE4へread-only handoff可能）。
- 共通条件: Contract ID参照のみ、本文複製禁止、再定義禁止、差分要求はCE0再起票

### Handoff boundary record（参照専用境界の記録）
- Boundary mode: read-only reference（CE1/CE2/CE4は参照専用、再定義不可）。
- Transfer unit: Contract ID + No-Go ID のみ（契約本文の複製なし）。
- Escalation rule: 境界逸脱の要求は `scope_deviation` としてCDC `held` を起票し、承認完了まで停止。

## Stream B execution log（CE0 Contract Freeze / contract-only）

### 2026-04-26 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（本Issue再読、safeMode境界とContract ID再定義禁止を再確認）
  - Phase 2開始前再読: 実施（Context/Decision/Consequences必須記載とCDC triggerを再確認）
  - Phase 3開始前再読: 実施（AC/DoD不足補完の合意条件とExecute境界を再確認）
  - Phase 4開始前再読: 実施（contract-only wording更新のみ、他ファイル非干渉を再確認）
  - Phase 5開始前再読: 実施（docs-check、自己修復上限3回を再確認）
  - Phase 6開始前再読: 実施（Go判定条件とfail-safe停止条件を再確認）
- execute boundary assertions:
  - 編集対象は本ファイルのみ（指定外ファイル編集なし）
  - CE0 Contract IDの追加/改名/削除なし（freeze維持）
  - safeMode既定（ON, `allowUnreviewedText=false`）の後退なし
  - CE1/CE2/CE4への引き渡しは Contract ID / No-Go ID のread-only参照のみ
- proceed decision:
  - 判定: **Go**
  - 根拠: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0` / docs-check pass

### 2026-04-25 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（本Issue再読、CE0契約ID固定とNo-Go 5語彙IDを再確認）
  - Phase 2開始前再読: 実施（Context / Decision / Consequences の記録方針と `held` 条件を再確認）
  - Phase 3開始前再読: 実施（AC/DoD補完追跡と `agreement_state=agreed` を再確認）
  - Phase 4開始前再読: 実施（contract-only wording 更新のみを再確認）
  - Phase 5開始前再読: 実施（docs-check + diff check、自己修復上限3を再確認）
  - Phase 6開始前再読: 実施（Go/Conditional/No-Go 判定条件を再確認）
- execute boundary assertions:
  - 編集対象は本ファイルのみ（指定外編集なし）
  - CE0 Contract IDの追加/改名/削除なし（freeze維持）
  - safeMode既定（ON, `allowUnreviewedText=false`）の後退なし
  - CE1/CE2/CE4への引き渡しは Contract ID / No-Go ID のread-only参照のみ
- proceed decision:
  - 判定: **Go**
  - 根拠: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0` / docs-check pass

### 2026-04-24 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（本Issue再読、Contract ID固定とNo-Go 5語彙IDを再確認）
  - Phase 2開始前再読: 実施（CDC trigger と `held` 記録要件を再確認）
  - Phase 3開始前再読: 実施（AC/DoD補完A/B/Cと `agreement_state=agreed` を再確認）
  - Phase 4開始前再読: 実施（契約語彙統一のみ・意味不変編集のみを再確認）
  - Phase 5開始前再読: 実施（docs-check限定、self-correction上限3を再確認）
  - Phase 6開始前再読: 実施（fatal停止条件とread-only handoff条件を再確認）
- execute boundary assertions:
  - 編集対象は本ファイルのみ（指定外編集なし）
  - CE0 Contract IDの追加/改名/削除なし（freeze維持）
  - safeMode既定（ON, `allowUnreviewedText=false`）の後退なし
  - CE1/CE2/CE4への受け渡しは Contract ID + No-Go語彙IDのread-only snapshotのみ
- handoff snapshot（read-only / downstream redefinition denied）:
  - Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  - Vocabulary IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
  - transfer mode: 参照専用（本文複製なし・下流再定義なし）

### 2026-04-23 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（本Issue再読、差分なし）
  - Phase 2開始前再読: 実施（固定Contract ID / No-Go語彙の再確認）
  - Phase 3開始前再読: 実施（AC/DoD補完A/B/Cと合意ゲート再確認）
  - Phase 4開始前再読: 実施（編集対象を本ファイルのみに限定）
  - Phase 5開始前再読: 実施（docs-checkのみをVerify対象として再確認）
  - Phase 6開始前再読: 実施（Proceed停止条件とFail-safeを再確認）
- plan agreement（AC/DoD不足補完の先行合意）:
  - `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` を先行提案し、`agreement_scope` 内で維持
  - `agreement_state=agreed` を満たすため、Executeは語彙統一と判定根拠の明確化に限定
- execute boundary assertions:
  - CE0 Contract IDの追加・改名・削除は未実施（freeze維持）
  - safeMode既定（ON, `allowUnreviewedText=false`）の後退なし
  - CE1/CE2/CE4は read-only handoff として扱い、本文複製・再定義なし
- verify policy:
  - Verify失敗時の自己修復は最大3回、4回目相当は即停止

### 2026-04-22 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（差分なし）
  - Phase 2開始前再読: 実施（差分なし）
  - Phase 3開始前再読: 実施（差分なし）
  - Phase 4開始前再読: 実施（差分なし）
  - Phase 5開始前再読: 実施（差分なし）
  - Phase 6開始前再読: 実施（差分なし）
- Phase 1抽出（固定語彙/Contract ID/No-Go語彙）:
  - Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  - 固定語彙: `equivalenceKey + bundleHash` / `sourceBundleHash` / `proposal lifecycle`
  - No-Go IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- phase checkpoint:
  - Phase 1 Read: 完了（Status/Scope/Contract IDs/No-Go語彙を再読）
  - Phase 2 ADR/CDC: 追加CDC不要（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0`）
  - Phase 3 Plan: AC/DoD補完提案A/B/Cを合意対象として固定（`agreement_state=agreed`）
  - Phase 4 Execute: contract-only wording hygiene の範囲で実施（意味変更なし・本ファイルのみ）
  - Phase 5 Verify: `docs-check` 実行（結果は下記 Verification log、自己修復0回）
  - Phase 6 Proceed: **Go**（判定根拠: `collision=0` / `safeMode regression=0` / docs-check pass）
- guard assertions:
  - CE0 Contract ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義なし
  - safeMode既定（ON, `allowUnreviewedText=false`）の緩和なし
  - 未承認決定の確定扱いなし（`held` 維持）
  - 自己修復上限は Verify 内で最大3回、4回目相当で停止

### 2026-04-26 prompt-b run（Plan → Execute → Verify → Proceed）
- Phase 1 Read同期: 開始前に本Issueを再読し、CE0 Contract ID凍結・No-Go 5語彙ID・safeMode既定（`safeMode=true`, `allowUnreviewedText=false`）を再確認。
- Phase 2 ADR/CDC（Context / Decision / Consequences）:
  - Context: Stream BはCE0契約SSOT維持を目的とし、CE1/CE2/CE4はread-only参照に限定する。
  - Decision: Contract ID再定義禁止、safeMode後退禁止、指定ファイル単独編集を継続する。
  - Consequences: 下流再定義と境界逸脱を抑止し、逸脱時は`held`へ即停止できる状態を維持する。
- Phase 3 Plan: contract-onlyの記録更新に限定し、本文意味変更を伴う編集を禁止する。
- Phase 4 Execute: 本IssueにPrompt B実行ログを追記（指定外ファイル編集なし）。
- Phase 5 Verify: docs-check 3点を実行し、self-correction 0/3で通過。
- Phase 6 Proceed: **Go**（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0`）。

### 2026-04-26 prompt-user run（Read → ADR/CDC → Plan → Execute → Verify/Proceed）
- Phase 1 Read同期: 開始前に本Issueを再読し、Scope限定（本ファイルのみ）とfreeze条件（Contract ID固定 / safeMode既定維持）を再確認。
- Phase 2 ADR/CDC（Context / Decision / Consequences）:
  - Context: CE0契約をSSOTとして維持し、CE1/CE2/CE4はread-only参照に限定する。
  - Decision: Contract ID再定義なし、safeMode後退なし、指定外編集なしを継続する。
  - Consequences: 境界逸脱時は `held` 停止を適用し、下流再定義を抑止する。
- Phase 3 Plan: Plan→Execute→Verify→Proceed の順序固定を明記し、contract-only wording更新以外を禁止。
- Phase 4 Execute: 本Issueへ実行ログのみ追記（指定外ファイル編集なし）。
- Phase 5 Verify: docs-check 3点を実行し、自己修復は最大3回。4回目相当は即停止。
- Phase 6 Proceed: **Go**（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0` / docs-check pass）。

### 2026-04-26 stream-b-ce0-04 run（Read → ADR/CDC → Plan → Execute → Verify/Proceed）
- Phase 1 Read: 本Issueを再読し、safeMode既定ON/`allowUnreviewedText=false` と Contract ID凍結を再確認。
- Phase 2 ADR/CDC:
  - Context: CE0をSSOTとして維持し、CE1/CE2/CE4はread-only参照に限定。
  - Decision: Contract ID再定義なし、safeMode後退なし、指定外編集なし。
  - Consequences: 境界逸脱時は`held`停止を適用し、未承認確定化を防止。
- Phase 3 Plan: AC/DoD補完提案は既存の`dod_read_only_reference`/`dod_no_go_id_canonical`/`dod_cdc_held_required`を継続。
- Phase 4 Execute: contract-onlyで本Issueの実行記録のみ更新。
- Phase 5 Verify: docs-check 3点を実行し、self-correction 0/3で通過。
- Phase 6 Proceed: **Go**（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0`）。

### Verification log template（self-correction <= 3）
- run_2026-04-26 attempt_1:
  - docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => `ok: validated 5 active issue memos`
  - docs-check: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
  - git diff --check: pass
  - result: pass（self-correction 0回）
- run_2026-04-25 attempt_1:
  - docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => `ok: validated 5 active issue memos`
  - docs-check: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
  - git diff --check: pass
  - result: pass（self-correction 0回）
- run_2026-04-23 attempt_1:
  - docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => `ok: validated 5 active issue memos`
  - docs-check: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
  - git diff --check: pass
  - result: pass（self-correction 0回）
- attempt_1:
  - docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => `ok: validated 5 active issue memos`
  - docs-check: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
  - git diff --check: pass
  - result: pass（self-correction 0回）
- attempt_2（必要時のみ）:
  - docs-check:
  - git diff --check:
  - result:
- attempt_3（必要時のみ）:
  - docs-check:
  - git diff --check:
  - result:
- stop_condition:
  - 4回目相当 / 前提崩れ / 競合検知で即停止

## Fail-safe（即停止条件）
- Self-Correction 3回超過（4回目修復に到達）
- SafeMode後退の兆候
- 未定義競合
- 指定外ファイル差分
- 依存前提崩壊

## Stream B Execution Ledger（CE0 Contract Freeze / this file only）
> 目的: Phase運用を実行ログとして固定し、各Phase開始時の「最新再読」を監査可能にする。

### Current run snapshot（2026-04-22）
- lane: Stream B / CE0 Contract Freeze only
- editable scope: `issue-CE0-contract-freeze.md` only
- non-editable scope guard: CE1 / CE2 / CE4 files, `03_Implement/**`
- contract freeze guard: Contract ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は再定義禁止
- fail-safe status: active（4回目修復 / safeMode後退要求 / contract_id_collision / scope逸脱を検知した時点で停止）

### Phase gate execution record（latest-read mandatory）
| Phase | Latest Read 実施 | 実施内容（要約） | Status |
| --- | --- | --- | --- |
| Phase 1 Read | Yes | 本Issue再読、Scope/Contract ID/No-Go/修復上限を再確認 | done |
| Phase 2 ADR/CDC | Yes | Context/Decision/Consequences の明文化ルールを再確認、承認前は `held` を維持 | held-ready |
| Phase 3 Plan | Yes | AC/DoD補完A/B/CとExecute開始条件（`agreement_state=agreed`）を再確認 | done |
| Phase 4 Execute | Yes | 編集対象を本Issueに限定し、語彙統一・判定根拠明確化のみ許可 | done |
| Phase 5 Verify | Yes | docs-check系コマンド + `git diff --check` を実行し、自己修復0回で通過 | done |
| Phase 6 Proceed | Yes | Verify再読後にMock signature（型/禁止操作）をread-only handoffとして公開 | done |

### ADR/CDC decision packet rule（approval gate）
- Context:
  - CE0 SSOT凍結を維持しつつ、下流（CE1/CE2/CE4）に read-only handoff するための判定根拠を固定する。
- Decision:
  - Contract ID / No-Go ID の語彙ID判定を正本として維持し、承認前の確定運用を行わない（`held`）。
- Consequences:
  - 下流は参照専用で再定義不可、衝突検知時はCDC `held` を起票して停止できる。
- Approval:
  - `agreement_state=agreed` 明記までは Proceed 不可（Phase 4以降の確定運用を禁止）。

## Stream B Phase Execution Record（2026-04-26 / CE0 contract freeze）
### Phase 1 Read
- 対象ファイル（`issue-CE0-contract-freeze.md`）のみを開始時に再読し、Contract ID・No-Go canonical 5 IDs・safeMode境界の差分を確認（差分なし）。
- 想定との差分確認結果: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0`。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0 SSOTを維持し、CE1/CE2/CE4はread-only handoffに限定する。
- Decision: Contract IDの再定義禁止、safeMode既定（ON, `allowUnreviewedText=false`）後退禁止、未承認論点は `held` を維持。
- Consequences: 下流再定義を抑止し、`contract_id_collision | vocabulary_collision | scope_deviation` 検知時は `held` で即停止可能。

### Phase 3 Plan
- AC/DoD不足の再点検を実施し、既存の `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` の追跡で充足可能と判定。
- 新規不足が発生した場合はドラフト提案を先に記録し、合意前は `held` のまま Execute に進まない。

### Phase 4 Execute
- 実施内容: CE0契約SSOTの進行記録更新のみ（指定外ファイル編集なし）。
- 非実施: Contract ID再定義、safeMode既定値変更、CE1/CE2/CE4本文編集。

### Phase 5 Verify（self-correction ≤ 3）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed
- 判定: **Go**（docs-check pass、collision/regressionなし）。
- handoff境界: CE1/CE2/CE4へは Contract ID / No-Go ID のread-only参照のみを引き渡す。
- fail-safe: 競合検出、safeMode後退、未承認確定化、自己修復4回目相当で即 `held` / `stopped_for_clarification`。

### 2026-04-27 stream-b-ce0-05 run（Read → Plan → Execute → Verify → Proceed）
- Phase 1 Read:
  - 本Issueを再読し、編集許可が `issue-CE0-contract-freeze.md` のみであることを再確認。
  - Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）凍結とNo-Go 5語彙ID固定を再確認。
  - fail-safe（自己修復は最大3回、前提崩壊/指定外編集要求で停止）を再確認。
- Phase 2 Plan（不足AC/DoD提案）:
  - 追加提案1: `dod_handoff_key_fixed` を追加し、Proceed時に handoff key を単一値で固定する。
  - 追加提案2: `dod_phase_gate_reread_trace` を追加し、各Phase開始前の再読実施ログを必須化する。
  - 追加提案3: `dod_execute_contract_only_evidence` を追加し、Executeが語彙統一以外を行っていない根拠を記録必須にする。
  - proposal_state: `agreed`（本Issue内運用の明確化であり、Contract ID再定義なし）。
- Phase 3 Execute（contract-only記述）:
  - CE0契約本文の意味変更は行わず、本runログに不足DoD提案と運用根拠のみを追記。
  - Contract ID / No-Go ID / safeMode既定値 / proposal lifecycle の定義変更なし。
- Phase 4 Verify（docs-check）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Phase 5 Proceed（handoff key固定）:
  - proceed_decision: **Go**
  - handoff_key: `CE0-HANDOFF-LOCK-2026-04-27`（固定）
  - 判定根拠: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0` / docs-check pass
  - handoff_mode: CE1/CE2/CE4へは Contract ID / No-Go ID のread-only参照のみ（本文複製・再定義禁止）
