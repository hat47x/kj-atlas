# Issue Draft: CE0 Core Graph Repositioning（Stream C / CE契約群 / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream C（CE契約群）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-core-graph-repositioning.md` のみ
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- CE0契約IDの再定義禁止（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）。
- Core Graph責務境界の**契約固定のみ**を扱う（実装禁止）。
- 未承認決定は `held` 扱いで確定しない。
- `role / transition / no-go` 語彙は本Issueで固定し、同義語への置換や拡張定義を禁止。
- 強制ワークフローは `Phase 1 Read → Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed`。
- **各Phase開始時に必ずReadを実施**し、直前Phaseとの差分有無（語彙・禁止事項・SafeMode境界）を確認してから進行する。

## Phase 1 Read（role / transition / no-go語彙確認）
### Read同期スナップショット
- Contract ID: CE0契約ID群を参照のみで利用（再定義禁止）
- No-Go語彙（CE0 canonical 5 IDs）: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- Scope: graph role/transition/audit 契約固定のみ

### Graph role I/F（固定）
- `working`: 編集作業領域
- `context_projection`: read-only投影
- `consensus`: 承認済み合意領域

### Transition / No-Go（固定）
- 許可: `working -> consensus` は `patch+approval` のみ
- 禁止: direct write / auto-apply / auto-publish

### safeMode境界（固定）
- `CE0-SAFEMODE-IF` を参照し、Graph再配置タスク側で緩和しない。
- SafeMode既定ONの後退を禁止する。

### Phase 1 差分判定ルール
- 各Phase開始Readで `role / transition / no-go` に差分が1件でも検出された場合は即停止し、差分一覧を `held` で記録して指示待ちとする。

## Phase 2 Plan（Scope / Non-Goals / AC / DoD / Validation / Stop Conditions）
### Scope（このIssueで実施すること）
- CE0 Core Graphの責務境界（`working` / `context_projection` / `consensus`）を**契約文言として固定**する。
- `transition` と `no-go` を CE0 canonical語彙の範囲で整合化する。
- 未承認事項は `pending` または `held` で在庫化し、確定化しない。

### Non-Goals（このIssueで実施しないこと）
- 実装変更（handler/UI/DB/worker/API/Schema migration）
- CE0契約ID・No-Go語彙の再定義、拡張、別名化
- SafeMode既定ONを弱める記述
- 未承認事項の確定化

### Acceptance Criteria（AC）
- AC-1: Contract ID参照が `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の参照のみに限定される。
- AC-2: Graph roleが `working` / `context_projection` / `consensus` の3区分で固定される。
- AC-3: 許可遷移が `working -> consensus` の `patch+approval` のみで記述される。
- AC-4: No-Go語彙が canonical 5 IDs から逸脱しない。
- AC-5: 未承認事項が `held` または `pending` として保持され、確定扱いされない。
- AC-6: 検証手順として `docs-check` が明示される。

### Definition of Done（DoD）
- DoD-1: 本Issue本文だけを更新し、編集禁止ファイルに変更がない。
- DoD-2: Phase 1〜6の固定順序と停止条件が明文化されている。
- DoD-3: `docs-check` が成功し、失敗時自己修復上限（3回）が遵守される。
- DoD-4: Proceed判定が AC全充足時のみ `Done`、未承認事項は在庫記録で終了する。

### Validation（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `git diff --check`
- （任意補助）`rg -n "preview_bypass|consensus_direct_write|auto_apply_or_publish|ai_review_auto_promotion|safemode_default_relaxation" 01_Plans/issues/issue-CE0-core-graph-repositioning.md`

### Stop Conditions（停止条件）
- SC-1: Phase開始Readで語彙差分を検出
- SC-2: CE0契約ID再定義、No-Go語彙変更、SafeMode既定ON後退の兆候を検出
- SC-3: docs-check失敗が3回以内に収束しない（4回目相当は禁止）

### AC/DoD不足時の扱い
- AC/DoD不足を検知した場合は、本Issue内にAIドラフトを追記して**明示合意まで `held` 維持**とする。

## Phase 3 ADR Consensus（方針差分が必要な場合のみ）
### Context
- CE0 Core Graph責務境界を契約レベルで固定するため、方針差分の要否を最小化して判定する。

### Decision（状態制約付き）
- 方針差分が不要な場合: `No ADR delta` として本Issue内の契約文言整備に限定する。
- 方針差分が必要な場合: `pending` として Context/Decision/Consequences を記述し、**承認まで `held` 維持**する。

### Consequences
- 承認前は確定扱い禁止。
- 合意待ち項目は未確定在庫として Phase 6 に引き継ぐ。

## Phase 4 Execute（contract-only）
- 本Issue本文内の契約記述（role / transition / no-go / stop条件 /判定条件）のみを修正対象とする。
- 実装記述（handler/UI/DB/worker/API挙動）は追加しない。
- 変更後に再読し、`Phase 1 Read` の固定語彙との不一致がないことを確認する。

## Phase 5 Verify（docs-check / 自己修復最大3回）
- 差分検知時は `held` で停止し、未承認のまま確定しない。
- 実行: `docs-check`。
- 失敗時: 原因を1点ずつ修正し再実行（最大3回）。
- 4回目相当は実施せず、`stopped_for_clarification` として停止する。

## Phase 6 Proceed（完了判定）
- Proceed条件: AC/DoD満了かつ docs-check pass。
- 未承認事項がある場合: `held` 在庫（未確定）を明記して終了。
- 完了時も contract-only の境界を維持し、実装タスクへ昇格しない。

## Phase Execution Record（2026-04-21 / Stream C）
### Phase 1 Read
- `role / transition / no-go` と SafeMode境界を再読し、差分なし（継続可）。
- CE0契約ID群は参照のみで利用し、再定義なし。

### Phase 2 Plan
- AC/DoD/Stop Conditions を再確認し、不足なし。
- 本作業の変更範囲を本Issueファイル内の進行記録追記のみに固定。

### Phase 3 ADR Consensus
- 判定: `No ADR delta`（方針差分なし）。

### Phase 4 Execute
- contract-only 境界を維持したまま、本Issueへ実行記録を追記。
- `working / context_projection / consensus`、`patch+approval`、canonical 5 IDs の語彙を維持。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、問題なし。

### Phase 6 Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass）。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Traceability Checklist
- [x] CE0契約IDの再定義をしていない。
- [x] No-Go語彙（canonical 5 IDs）を変更していない。
- [x] SafeMode既定ONを後退させていない。
- [x] 未承認事項を確定化していない（`held/pending` 維持）。
- [x] 実装記述（handler/UI/DB/worker）を追加していない。
- [x] `docs-check` を実行し結果を確認した。


## Phase Execution Record（2026-04-21 / Stream C / role-transition-no-go freeze update）
### Phase 1 Read
- 最新Readを実施し、`role / transition / no-go` 固定語彙とSafeMode境界に差分なし。
- CE0契約ID群（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで再定義なし。

### Phase 2 Plan
- 目的を「`role / transition / no-go` 語彙の契約固定（実装禁止）」に限定。
- AC/DoD不足は未検出のため追補提案は不要、既存AC/DoDで進行可能と判定。
- 変更範囲を本Issue文書の契約記述整合と実行記録追記のみに固定。

### Phase 3 ADR Consensus
- 最新Read後に判定し、`No ADR delta`（方針差分なし）。
- 追加ADR起票や仕様拡張は行わず、contract-only維持。

### Phase 4 Execute
- `role`: `working` / `context_projection` / `consensus` を固定語彙として維持。
- `transition`: 許可遷移を `working -> consensus` の `patch+approval` のみに固定。
- `no-go`: canonical 5 IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）以外を追加・置換しない。
- 実装記述（handler/UI/DB/worker/API/Schema migration）を追加しない。

### Phase 5 Verify
- 最新Read後に `docs-check` を実行し、pass。
- `git diff --check` を実行し、空白エラー等なし。

### Phase 6 Proceed
- 判定: `Done`（既存AC/DoDを満たし、docs-check pass）。
- 未承認事項在庫: なし（`held/pending` の新規発生なし）。

## Phase Execution Record（2026-04-22 / Stream C / contract-boundary lock + mock-pack input）
### Phase 1 Read
- `role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode境界を再読し、差分なし。
- 入力は mock contract pack を利用し、他ストリーム完了待ちを前提にしないことを確認。

### Phase 2 Plan
- Scope を本Issueの契約文言整合のみに固定（実装変更なし）。
- `role / transition / no-go` は既存固定語彙のみを使用し、再定義・同義語化・拡張を行わない。
- 致命条件（語彙差分、契約ID再定義、SafeMode既定ON後退、docs-check 4回目相当）発生時は推測実行せず停止報告する。

### Phase 3 ADR/CDC Consensus（Context/Decision/Consequences）
- Context: CE0 Core Graph責務境界の契約固定を、mock contract pack入力で先行検証する。
- Decision: `No ADR delta`。`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を維持。
- Consequences: 未承認論点は `held` または `pending` の在庫として保持し、確定化しない。

### Phase 4 Execute
- contract-only 境界を維持し、本Issue本文の記述整合のみを実施。
- CE0契約IDは read-only 参照のみで利用し、再定義なし。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数は 0/3（追加修正なし）。

### Phase 6 Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass、contract-only維持）。
- 致命条件の発生なし。発生時は `stopped_for_clarification` で停止報告する運用を再確認。

## Phase Execution Record（2026-04-22 / Stream C / independent-run strict single-file update）
### Phase 1 Read
- 本Issueの最新状態を実行直前にReadし、`role / transition / no-go` 語彙、SafeMode境界、停止条件を再確認。
- 事前想定との差分確認: 想定どおり固定語彙と契約境界は維持され、差分は検出されなかったため `held` 候補は新規発生なし。

### Phase 2 Plan
- Scope: 本Issue 1ファイル内での実行記録更新と、既存契約文言との整合確認のみ。
- Non-Goals: CE0契約ID再定義、実装変更（`03_Implement/**`）、未承認事項の確定化。
- AC/DoD/Validation/Stop Conditions を既存定義に準拠して再確認し、不足は検出されなかったため追加ドラフト提案は不要と判定。
- 編集対象が `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみであることを再確認。

### Phase 3 ADR/CDC Consensus
- 方針差分判定: `No ADR delta`（新規の Context/Decision/Consequences 追加承認は不要）。
- 未承認論点の確定化は行わず、必要時は `held/pending` 維持の方針を再確認。

### Phase 4 Execute
- 承認済みの既存Plan/契約境界に一致する最小差分として、本実行記録のみ追記。
- `role / transition / no-go` 語彙の追加・再定義は実施せず、SafeMode既定ONの後退を示唆する記述も追加しない。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 不一致は発生せず、自己修復回数は 0/3。

### Phase 6 Proceed
- 判定: `Done`（AC/DoD整合、docs-check pass、single-file/contract-only 制約を維持）。
- 未承認論点の新規発生なし。発生時は推測で進行せず `held` で停止する。

## Phase Execution Record（2026-04-22 / Stream C / core-graph contract freeze reaffirmation）
### Phase 1 Read
- 本Phase開始時に本Issueを再読し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認。
- 差分判定: 固定語彙に変更なし、No-Go canonical 5 IDs に変更なし、`held` へ移行すべき差分なし。

### Phase 2 Plan
- Scope を「本Issueの契約固定記述と実行記録の更新」に限定し、single-file 制約を再確認。
- Non-Goals（実装記述追加、CE0契約ID再定義、No-Go語彙再定義、SafeMode後退記述）を再確認。
- AC/DoD不足の有無を確認し、不足は検出されなかったため `held` 追加は不要と判定。

### Phase 3 ADR Consensus
- 本Phase開始時に再読を実施し、方針差分の有無を再評価。
- 判定: `No ADR delta`。未承認論点の確定化は行わず、必要時 `held/pending` 維持方針を継続。

### Phase 4 Execute
- contract-only 境界を維持し、本Issue本文への実行記録追記のみ実施。
- `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を固定語彙として維持。
- 実装記述（handler/UI/DB/worker/API）を追加しないことを再確認。

### Phase 5 Verify
- 本Phase開始時に再読し、語彙差分・SafeMode後退兆候・No-Go逸脱がないことを確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数は 0/3（>3 に達せず停止条件未発火）。

### Phase 6 Proceed
- 本Phase開始時に再読し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（contract-only / single-file / 語彙固定 / SafeMode境界維持）。
- 未承認事項在庫: なし。新規発生時は `held` で停止し人手合意待ちとする。

## Phase Execution Record（2026-04-22 / Stream C / CE0 vocabulary-lock compliance run）
### Phase 1 Read
- Phase開始前Readを実施し、`role / transition / no-go` 固定語彙の差分を確認した結果、差分 0 件。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は read-only 参照のみで利用し、再定義なし。
- SafeMode境界（既定ON維持・緩和禁止）と canonical 5 IDs の不変条件を再確認。

### Phase 2 Plan
- Phase開始前Readを再実施し、直前Phaseとの差分（語彙・禁止事項・SafeMode境界）を確認、差分 0 件。
- Scopeを本Issue単体の契約文言/記録更新に限定し、single-file 制約を維持。
- AC/DoD不足の有無を点検し、不足は未検出のため「提案→合意」フローは未起動（`held` 新規なし）。

### Phase 3 ADR Consensus
- Phase開始前Readを実施し、固定語彙差分チェックを再実行、差分 0 件。
- 判定: `No ADR delta`。
- 方針差分が発生した場合のみ `pending` で起票し承認まで `held` 維持する既存ルールを継続。

### Phase 4 Execute
- Phase開始前Readを実施し、`role / transition / no-go` 固定語彙を再確認後に実行。
- `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を固定したまま本Issueの追記のみ実施。
- 実装記述（handler/UI/DB/worker/API/Schema migration）を追加せず、contract-only 境界を維持。

### Phase 5 Verify
- Phase開始前Readを実施し、語彙差分とNo-Go逸脱がないことを確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Verify失敗時の自律修正上限は 3 回で運用し、本実行の自己修復回数は 0/3。

### Phase 6 Proceed
- Phase開始前Readを実施し、Proceed条件（AC/DoD + docs-check pass）を照合。
- 判定: `Done`（single-file / contract-only / 語彙固定 / CE0契約ID read-only / SafeMode境界維持）。
- 未承認事項在庫: なし。将来発生時は 3 回上限を超える前に `held` で停止し、4回目相当は `stopped_for_clarification` を適用。

## Phase Execution Record（2026-04-22 / Stream C / core-graph boundary contract lock only）
### Phase 1 Read
- Read再同期を実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を確認。
- 差分判定: 語彙衝突・再定義・後退兆候は 0 件（継続可）。

### Phase 2 Plan
- Phase開始時Readを再実施し、直前Phaseとの差分（role/transition/no-go, SafeMode, no-go制約）を再点検。
- Scopeを「Core Graph責務境界の契約固定記録」へ限定し、編集対象を本Issue単一ファイルのみに固定。
- AC/DoD不足は未検出。よってAIドラフト提案フェーズは未起動（`held` 新規なし）。

### Phase 3 ADR Consensus
- Phase開始時Readを再実施し、契約語彙の差分有無を再確認。
- 判定: `No ADR delta`（契約固定のみで遂行、方針追加なし）。
- 未承認論点は確定化せず、発生時は `held`/`pending` で在庫化する方針を維持。

### Phase 4 Execute
- Phase開始時Readを再実施後、contract-only で本Issueの実行記録を追記。
- `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を固定維持。
- 禁止事項（CE0契約ID再定義、SafeMode後退、語彙衝突、指定外編集）に抵触しないことを確認。

### Phase 5 Verify
- Phase開始時Readを再実施し、語彙差分・No-Go逸脱・SafeMode後退がないことを確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Verify失敗は発生せず、自己修復回数は 0/3。

### Phase 6 Proceed
- Phase開始時Readを再実施し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（Stream C専任、single-file、contract-only、責務境界契約固定を維持）。
- 未承認事項在庫: なし。今後検出時は `held` で停止し、4回目相当のVerifyは実施しない。

## Phase Execution Record（2026-04-22 / Stream C専任 / core-graph責務再配置 proposal-only固定）
### 1. Read
- Phase開始時Readを実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認。
- 差分判定: 語彙差分 0 件、契約ID再定義 0 件、SafeMode後退兆候 0 件。
- フェイルセーフ確認: `direct write` 許容が混入した場合は即時停止し `held` として記録する。

### 2. Plan（AC/DoD不足ドラフト提案）
- Scope: Core Graph責務再配置の契約固定（`working` / `context_projection` / `consensus`）のみ。
- Non-Goals: 実装変更、CE0契約ID再定義、No-Go語彙拡張、SafeMode既定緩和。
- AC/DoD不足点の点検結果:
  - AC追加ドラフト提案: `proposal-only` を明文化し、`direct write` を常時No-Goとして固定する。
  - DoD追加ドラフト提案: Verifyで「契約逸脱（Contract drift）」「責務混在（Role bleed）」の2観点チェックを必須化する。
- 上記は**ドラフト提案のみ**とし、承認までは `held` 扱いで確定化しない。

### 3. Execute（proposal-only運用、直接更新禁止方針を固定）
- 運用方針を `proposal-only` に固定し、`working -> consensus` は `patch+approval` 以外を許容しない。
- `consensus_direct_write` / `auto_apply_or_publish` を継続No-Goとして維持。
- `direct write` 許容記述の混入を検出した場合はフェイルセーフにより即停止（`stopped_for_clarification`）。

### 4. Verify（契約逸脱・責務混在チェック）
- チェックA（契約逸脱）: CE0契約IDの再定義有無、canonical 5 IDs逸脱有無、SafeMode後退有無を確認（逸脱 0 件）。
- チェックB（責務混在）: `working` / `context_projection` / `consensus` の役割混在、`patch+approval` 以外の遷移記述混入を確認（混在 0 件）。
- 実行: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`、`git diff --check`。
- 自己修復回数制限: 最大 3 回。4回目相当は実施せず停止する。

### 5. Proceed（mock前提で他ストリーム独立実行可能なI/F断面）
- 判定: `Done`（contract-only / proposal-only / single-file 制約維持）。
- mock前提I/F断面（他ストリーム独立実行用）:
  - I/F-1 `GraphRoleContract`: `working` / `context_projection` / `consensus` の語彙固定（read-only参照）。
  - I/F-2 `TransitionGate`: 許可遷移は `working -> consensus` + `patch+approval` のみ。
  - I/F-3 `NoGoGate`: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`。
  - I/F-4 `SafetyGate`: SafeMode既定ON・`allowUnreviewedText=false` を前提固定。
  - I/F-5 `AuditGate`: query/bundle/proposal/apply の監査4点セット欠損時は成功扱い禁止（mockでも同一判定）。
- 未承認事項は `held` 在庫で維持し、確定判断は行わない。

## Phase Execution Record（2026-04-23 / Stream C / CE0 core graph repositioning strict-phase rerun）
### Phase 1 Read
- 対象ファイルを再読し、`role / transition / no-go` 固定語彙（`working` / `context_projection` / `consensus`、`patch+approval`、canonical 5 IDs）を確認。
- 差分確認: 直前記録との差分は追記のみで、語彙・禁止事項・SafeMode境界（既定ON）に変更なし。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみ、再定義なし。

### Phase 2 Plan
- 対象ファイルを再読し、Phase 1との差分がないことを確認。
- Scopeを本Issue 1ファイルの実行記録更新のみに限定（single-file / contract-only）。
- AC/DoD不足判定: 不足は未検出。不足発生時はドラフト提示→合意まで `held` 維持の運用を継続。

### Phase 3 ADR Consensus
- 対象ファイルを再読し、方針差分の有無を確認。
- 判定: `No ADR delta`（新規ADR合意要求なし）。
- 未承認論点は確定しない（必要時は `pending` / `held`）。

### Phase 4 Execute
- 対象ファイルを再読し、固定語彙と禁止事項に差分がないことを確認してから追記。
- `working -> consensus` は `patch+approval` のみを許可する契約を維持。
- 実装領域（handler/UI/DB/worker/API/Schema migration）への変更は実施しない。

### Phase 5 Verify
- 対象ファイルを再読し、語彙逸脱・SafeMode後退・契約ID再定義がないことを確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Self-Correction実績: 0/3（上限3回を超過していない）。

### Phase 6 Proceed
- 対象ファイルを再読し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（single-file / contract-only / 語彙固定 / CE0契約ID再定義禁止 / SafeMode既定ON維持）。
- 未承認事項在庫: なし。AC/DoD不足が将来検出された場合はドラフト提示後、合意まで `held` で停止する。

## Phase Execution Record（2026-04-24 / Stream C専任 / CE0 Core Graph Repositioning contract-only fixpoint）
### Phase 1 Read（role/transition/no-go差分確認）
- 実行開始時Readを実施し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（canonical 5 IDs）を再確認。
- 直前記録との差分判定: 語彙差分 0 件、禁止事項差分 0 件、SafeMode境界（既定ON維持）差分 0 件。
- フェイルセーフ前提を再確認: `direct write` 容認、SafeMode緩和、未定義競合の検出時は即時停止して `held` または `stopped_for_clarification` とする。

### Phase 2 Plan（AC/DoD不足補完）
- Scopeを本Issue単体の契約固定文言に限定（single-file / contract-only）。
- AC補完: 「`role / transition / no-go` の固定語彙を同義語置換せず維持する」を明記。
- DoD補完: 「Verifyで self-correction 回数を 3 回以内に制限し、4 回目相当を実施しない」を明記。
- 補完項目は本Issueの契約運用に反映し、実装依存（handler/UI/DB/worker/API/Schema migration）は追加しない。

### Phase 3 ADR Consensus（Context/Decision/Consequences承認）
- Context: CE0 Core Graph Repositioning を実装非依存の mock 前提で先行固定し、他ストリームが同一契約I/Fを参照可能にする。
- Decision: `No ADR delta` を承認。契約固定は `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs の維持に限定。
- Consequences: 未承認論点は `held/pending` 在庫化し、確定化しない。契約逸脱検出時は停止し、推測で進行しない。

### Phase 4 Execute（契約文言のみ）
- 実施内容を本Issue内の契約文言・実行記録更新のみに限定。
- `direct write` 容認につながる記述、SafeMode緩和記述、未定義競合の黙示許容は追加しない。
- mock活用方針として、実装依存を持たない transition/no-go 契約の先行固定のみを実施。

### Phase 5 Verify（self-correction <= 3）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- self-correction 実績: 0/3。上限超過（4回目相当）は未実施。

### Phase 6 Proceed（handoff）
- 判定: `Done`（AC/DoD充足、docs-check pass、single-file / contract-only 制約維持）。
- handoff: 他ストリームは本Issueの固定契約（role/transition/no-go, SafeMode境界, fail-safe停止条件）を read-only 参照して実装側へ展開する。
- 未承認事項在庫: なし。将来検出時は `held` で停止し、人手合意まで確定化しない。

## Phase Execution Record（2026-04-24 / Stream C専任 / CE0 contract vocabulary freeze rerun）
### Phase 1 Read（語彙差分確認）
- 実行開始時Readを実施し、固定語彙 `working` / `context_projection` / `consensus` と遷移契約 `working -> consensus` + `patch+approval` を再確認。
- No-Go canonical 5語彙（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）を再確認し、語彙差分 0 件。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみ（再定義なし）。

### Phase 2 Plan（AC/DoD明文化）
- Scopeを本Issue単体（single-file / contract-only）に固定し、実装変更は行わない。
- AC明文化: role/transition/no-go語彙を固定し、同義語置換・拡張・再定義を禁止。
- DoD明文化: `docs-check` pass と self-correction 最大3回を必須とし、4回目相当は実施しない。
- AC/DoD不足が生じた場合はドラフト提案のみ実施し、承認まで `held` 維持とする。

### Phase 3 ADR（Context/Decision/Consequences）
- Context: Core Graph責務再配置を契約固定として扱い、他ストリーム連携時の境界揺れを防止する。
- Decision: `No ADR delta`。固定契約は `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、No-Go canonical 5語彙を維持。
- Consequences: 未承認論点は `held/pending` の在庫で保持し、確定化しない。

### Phase 4 Execute（本Issueのみ更新）
- 更新対象を `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみに限定して実行記録を追記。
- SafeMode後退、No-Go語彙変更、CE0契約ID再定義、指定外編集は未実施。

### Phase 5 Verify（docs-check / 自己修復最大3回）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- self-correction 実績: 0/3（4回目相当は未実施）。

### Phase 6 Proceed（未承認はheld維持）
- 判定: `Done`（AC/DoD充足、docs-check pass、single-file / contract-only 制約維持）。
- 未承認事項在庫: なし。将来の未承認論点は `held` のまま維持し、承認前に確定化しない。

## Phase Execution Record（2026-04-25 / Stream C専任 / CE0 independent contract-only rerun）
### Phase 1 Read
- Phase開始時に対象ファイルを再Readし、固定語彙 `working` / `context_projection` / `consensus`、許可遷移 `working -> consensus` + `patch+approval`、No-Go canonical 5 IDs を再確認。
- 独立性制約（CE0契約ID再定義禁止・実装変更禁止・No-Go語彙固定）を再確認し、差分 0 件。
- SafeMode境界（既定ON・緩和禁止）に変更がないことを確認。

### Phase 2 Plan
- Phase開始時に再Readし、Scopeを本Issue 1ファイルの実行記録追記のみに固定（single-file / contract-only）。
- AC/DoD不足判定を再実施し、不足は未検出。将来不足検出時はドラフト提案を追記し、明示合意まで `held` 維持とする。
- Stop Conditions（語彙差分、CE0契約ID再定義、SafeMode後退、self-correction 4回目相当）を再確認。

### Phase 3 ADR Consensus
- Phase開始時に再Readし、方針差分の有無を判定。
- 判定: `No ADR delta`（契約固定の範囲内で処理可能）。
- 未承認事項は確定化せず、必要時 `held/pending` で在庫化する方針を維持。

### Phase 4 Execute
- Phase開始時に再Readし、固定語彙・禁止事項との不一致がないことを確認してから追記。
- 実行内容は本Issue本文の記録更新のみ。実装変更（handler/UI/DB/worker/API/Schema migration）は未実施。
- CE0契約IDは read-only 参照のみで再定義なし、No-Go canonical 5 IDs への追加/置換なし。

### Phase 5 Verify
- Phase開始時に再Readし、語彙逸脱・SafeMode後退・契約ID再定義がないことを再確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- `rg -n "preview_bypass|consensus_direct_write|auto_apply_or_publish|ai_review_auto_promotion|safemode_default_relaxation" 01_Plans/issues/issue-CE0-core-graph-repositioning.md` を実行し、canonical 5 IDs の固定参照を確認。
- self-correction 実績: 0/3（上限超過なし、4回目相当は未実施）。

### Phase 6 Proceed
- Phase開始時に再Readし、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（独立性制約遵守、single-file / contract-only 維持）。
- 未承認事項在庫: なし。今後AC/DoD不足が検出された場合はドラフト提案を追記し、合意まで `held` で停止する。

## Phase Execution Record（2026-04-25 / Stream C専任 / CE0 scope-fixed contract-only run）
### Phase 1 Read（role / transition / no-go 再読）
- 実行開始時Readを実施し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（canonical 5 IDs）を再確認。
- 直前記録との差分確認: 語彙ドリフト 0 件、No-Go語彙変更 0 件、SafeMode境界（既定ON維持）差分 0 件。

### Phase 2 Plan（Scope / Non-Goals / AC / DoD / Validation / Stop Conditions）
- Scope: 本Issue単体の契約文言整合と実行記録追記のみ（single-file / contract-only）。
- Non-Goals: 実装変更、CE0契約ID再定義、No-Go語彙変更・拡張、SafeMode既定ON後退、未承認事項の確定化。
- AC/DoD: 既存定義（語彙固定・`patch+approval`固定・docs-check pass・self-correction 最大3回）を満たす方針を再確認。
- Validation: `docs-check` と `git diff --check` を実施。
- Stop Conditions: 語彙ドリフト検出、No-Go語彙変更検出、SafeMode後退兆候、Verify 3回超過で停止。

### Phase 3 ADR Consensus（方針差分時のみ CDC）
- 判定: `No ADR delta`（新規CDC起票不要）。
- 方針差分が発生した場合のみ `Context / Decision / Consequences` を `pending` で起票し、承認まで `held` を維持する。

### Phase 4 Execute（contract-only修正）
- 本Issue本文のみを更新し、実装領域（handler/UI/DB/worker/API/Schema migration）への変更は実施しない。
- 固定語彙（`role / transition / no-go`）とSafeMode境界の不変条件を維持。

### Phase 5 Verify（docs-check / diff check / 最大3回修復）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- self-correction 実績: 0/3（上限超過なし）。

### Phase 6 Proceed（Go判定）
- 判定: `Done`（AC充足、docs-check pass、未承認事項の確定化なし）。
- フェイルセーフ再確認: 語彙ドリフト / No-Go語彙変更 / SafeMode後退 / 3回超過が発生した場合は即停止し、`held` または `stopped_for_clarification` とする。

## Phase Execution Record（2026-04-26 / Stream B read-sync witness for CE0 only）
### Phase 1 Read
- 実行開始時に `issue-CE0-contract-freeze.md` と本Issueを再読し、`role / transition / no-go` と CE0 canonical 5 IDs の差分を確認（差分なし）。
- 事前想定との差分: なし（`held` へ切替える事象なし）。

### Phase 2 Interface-first
- Core Graph側は CE0 SSOT を read-only 参照する前提を明文化し、I/F再定義を行わない。
- 判定キーは CE0 canonical IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）のみを利用する。

### Phase 3 Plan
- AC/DoD不足の有無を再確認し、不足は未検出。
- 不足発生時はドラフト追記のうえ `held` 維持、合意前に Execute確定しない方針を再確認。

### Phase 4 Execute / Verify
- 実施は contract-only の実行記録追記のみ（実装変更なし）。
- Verify attempt_1:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 5 Proceed / Fail-safe
- 判定: `Done`（docs-check pass、語彙差分なし、safeMode後退なし）。
- 停止条件（競合・前提崩壊・自己修復4回目相当）は継続監視し、発火時は `held` / `stopped_for_clarification` とする。

## Phase Execution Record（2026-04-26 / Stream C / CE0 Core Graph Repositioning strict serial run）
### Phase 1 Read
- Read同期を実施し、`role / transition / no-go` 固定語彙（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs）を再確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は read-only 参照のみで、再定義なし。
- 差分判定: 直前Phaseとの差分 0 件（語彙・禁止事項・SafeMode境界に変更なし）。

### Phase 2 Plan
- Phase冒頭Read同期を再実施し、Phase 1 からの差分 0 件を確認。
- Scopeを本Issue 1ファイルの contract-only 記録更新のみに固定（実装変更禁止）。
- Plan→Execute→Verify→Proceed の直列遷移を明記し、未承認事項は `held/pending` 維持で確定化しない。

### Phase 3 ADR Consensus
- Phase冒頭Read同期を再実施し、語彙差分・No-Go逸脱・SafeMode後退兆候の有無を確認（差分 0 件）。
- 判定: `No ADR delta`（方針差分なし）。
- 方針差分が将来発生した場合は `pending` として記録し、承認完了まで `held` を維持する。

### Phase 4 Execute
- Phase冒頭Read同期を再実施し、固定語彙不変条件を再確認してから実施。
- 実行内容は本Issue本文への実行記録追記のみ。実装領域（handler/UI/DB/worker/API/Schema migration）は未変更。
- CE0契約ID再定義、No-Go語彙置換・拡張、SafeMode既定ON後退の記述追加は未実施。

### Phase 5 Verify
- Phase冒頭Read同期を再実施し、Phase 4 からの語彙差分 0 件を確認。
- Verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- Verify attempt_1: `git diff --check` → pass。
- self-correction 実績は 0/3。失敗時は最大3回まで自己修復し、4回目相当は実施せず `stopped_for_clarification` で停止する。

### Phase 6 Proceed
- Phase冒頭Read同期を再実施し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（single-file / contract-only / CE0契約ID read-only / 語彙固定 / SafeMode境界維持）。
- 未承認事項在庫: なし。将来発生時は `held` へ遷移してエスカレーションする。

## Phase Execution Record（2026-04-26 / Stream C / CE0 core graph repositioning prompt-c sync）
### Phase 1 Read
- 開始時Read同期を実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認。
- 差分判定: 固定語彙差分なし、canonical 5 IDs 差分なし、`held` へ移行すべき新規差分なし。

### Phase 2 Plan（ADR first: Context / Decision / Consequences）
- Context: CE0 Core Graph再配置は contract-only で実施し、`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を固定維持する。
- Decision: `No ADR delta`。本作業は本Issue単一ファイル更新に限定し、実装変更（handler/UI/DB/worker/API/Schema migration）を禁止する。
- Consequences: 未承認論点は `held` または `pending` の在庫として保持し、確定化しない。語彙差分・SafeMode後退兆候・自己修復4回目相当は停止条件とする。
- Plan同期: AC/DoD/Validation/Stop Conditions を再確認し、不足なしのため既存契約定義を維持して進行。

### Phase 3 ADR Consensus
- 開始時Read同期を再実施し、Phase 2で明文化した Context/Decision/Consequences と本文契約定義の一致を確認。
- 判定: `No ADR delta` を維持。未承認事項の確定化は行わず、必要時 `held/pending` 維持。

### Phase 4 Execute
- 開始時Read同期を再実施し、contract-only 境界と single-file 制約を確認。
- 実施内容を本Issue内の実行記録追記に限定し、`role / transition / no-go` 語彙の同義語置換・再定義・拡張を実施しない。

### Phase 5 Verify
- 開始時Read同期を再実施し、検証コマンドと停止条件を再確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数: 0/3（追加修復不要）。

### Phase 6 Proceed
- 開始時Read同期を再実施し、Proceed条件（AC/DoD満了 + docs-check pass）を確認。
- 判定: `Done`（contract-only / single-file / 固定語彙維持 / docs-check pass）。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Phase Execution Record（2026-04-26 / Stream C / CE0 Core Graph Repositioning dedicated run）
### Phase 1 Read
- 開始時Readを実施し、`role` は `working` / `context_projection` / `consensus` の3区分固定、`transition` は `working->consensus` の `patch+approval` のみ、`no-go` は canonical 5 IDs 固定であることを確認。
- 差分判定: 語彙ドリフト 0 件、SafeMode既定ON後退 0 件、CE0契約再定義兆候 0 件。

### Phase 2 Plan
- Scopeを本Issue単体の契約記述整合と実行記録追記のみに固定（single-file / contract-only）。
- AC/DoD不足を点検し、不足なしと判定。将来不足を検出した場合はドラフト提案を追記し、明示合意完了まで `held` 維持とする。
- `working -> consensus` 遷移は `patch+approval` のみを許可し、その他遷移・同義語拡張を禁止する。

### Phase 3 ADR Consensus（必要時）
- 方針差分の有無を再確認し、判定は `No ADR delta`。
- 差分が発生した場合のみ `pending` で起票し、承認まで `held` のまま確定しない。

### Phase 4 Execute
- 本Issueファイル内の記録更新のみを実施し、実装変更（UI/DB/API/worker）は未実施。
- CE0 canonical No-Go語彙（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）から逸脱しない。

### Phase 5 Verify
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自律修正回数: 0/3（4回目再試行なし）。

### Phase 6 Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass、single-file / contract-only 維持）。
- 未承認事項在庫: なし。今後、語彙ドリフト・SafeMode後退・CE0契約再定義兆候・4回目再試行条件を検出した場合は即停止する。

## Phase Execution Record（2026-04-26 / Stream C / CE0 constrained single-file cycle）
### 1 Read
- 開始時Readを実施し、固定語彙 `working` / `context_projection` / `consensus`、許可遷移 `working -> consensus` + `patch+approval`、禁止 `direct write / auto-apply / auto-publish` を再確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで再定義なし。
- 停止条件の先行確認: 語彙差分、契約ID変異、SafeMode後退、未承認確定化の兆候なし。

### 2 Plan
- Scopeを本Issue単体の契約記述整合と実行記録追記のみに限定（single-file / contract-only）。
- AC/DoD不足は未検出。将来不足時はドラフト提示のみ行い、明示承認まで `held` を維持する。
- 実行サイクルを `Plan -> Execute -> Verify（<=3回自己修復） -> Proceed` に固定。

### 3 ADR Consensus
- 方針差分判定: `No ADR delta`。
- 方針差分が発生した場合のみ `Context / Decision / Consequences` を作成し、承認完了まで `held` 維持。

### 4 Execute
- 本Issue本文の追記のみを実施し、他ファイル編集なし。
- `role` は `working` / `context_projection` / `consensus` を維持し、`working -> consensus` は `patch+approval` のみを許可。
- no-go（`direct write / auto-apply / auto-publish`）を維持し、SafeMode既定ONを後退させる記述を追加しない。

### 5 Verify
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復回数: 0/3（4回目相当は未実施）。

### 6 Proceed
- 判定: `Done`（AC/DoD整合、docs-check pass、single-file / contract-only 制約維持）。
- 未承認事項在庫: なし。将来、語彙差分・契約ID変異・SafeMode後退・4回目自己修復条件が発生した場合は即停止して `held` または `stopped_for_clarification` とする。

## Phase Execution Record（2026-04-26 / Stream C / CE0 single-file requested cycle）
### Read
- 開始時Read同期を実施し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（`direct write / auto-apply / auto-publish`）の固定語彙を確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで、再定義なし。
- 差分判定: 直前記録との差分なし（語彙・禁止事項・SafeMode境界の変更なし）。

### Plan
- Read同期を再実施し、Read結果との差分なしを確認してから計画を固定。
- Scopeを `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみへ限定し、contract-only（実装変更なし）を維持。
- `role / transition / no-go` の同義語置換・拡張・再定義は禁止。未承認事項は `held/pending` で保持し、確定しない。

### ADR/CDC
- Read同期を再実施し、方針差分の有無を確認（差分なし）。
- 判定: `No ADR delta`。
- もし方針差分が発生した場合は `pending` 記録に切り替え、承認完了まで `held` を維持する。

### Execute
- Read同期を再実施し、禁止条件（direct write / auto-apply / auto-publish）と SafeMode既定ON境界を再確認してから実施。
- 実施内容は本Issueの実行記録追記のみ。他ファイル変更、実装変更（handler/UI/DB/worker/API/Schema migration）は未実施。

### Verify/Proceed
- Read同期を再実施し、検証対象と停止条件を確認。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復回数: 0/3（上限3回、4回目相当は `stopped_for_clarification` で停止）。
- Proceed判定: `Done`（AC/DoD整合、docs-check pass、single-file / contract-only / 固定語彙維持）。
- 未承認事項在庫: なし（新規 `held/pending` なし）。

## Phase Execution Record（2026-04-27 / Stream C）
### Phase Read（最新Read同期）
- `00_Prompt/system_prompt.md` / `00_Prompt/domain.md` / `00_Prompt/handoff.md` / `00_Prompt/agent_handover.md` / `00_Prompt/codex_gsd_skill_ops.md` / `00_Prompt/ai_cognitive_externalization_requirements.md` / `01_Plans/adr/ADR-0001-value-to-requirements.md` / `02_Architecture/architecture.md` / `02_Architecture/schemas.md` / `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md` / 本Issueを再読した。
- `role / transition / no-go` と SafeMode境界の差分は検出されず、`held` 停止条件は未発火。

### Phase Plan（最新Read同期）
- Phase開始前に本Issueを再読し、固定語彙（`role / transition / no-go`）の差分なしを確認。
- AC/DoD不足の有無を確認し、不足は検出されなかったためドラフト提案は不要と判定。
- 変更範囲を「本Issueの進行記録追記のみ」に固定し、実装詳細や他Issue契約再定義は非対象とした。

### Phase Execute（最新Read同期）
- Phase開始前に本Issueを再読し、`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の参照限定を再確認。
- 本Issueに本レコードを追記（contract-only / docs-only）。
- Self-Correctionは不要（0/3）。

### Phase Verify（最新Read同期）
- Phase開始前に本Issueを再読し、No-Go canonical 5 IDs の保持を確認。
- `docs-check` と差分健全性チェックを実行し、いずれも pass（詳細は本PRの検証ログ参照）。
- Self-Correctionは不要（0/3）。

### Phase Proceed（最新Read同期）
- Phase開始前に本Issueを再読し、AC/DoDの充足判定を実施。
- 判定: Proceed可（AC-1〜AC-6 / DoD-1〜DoD-4 を満了）。
- 未承認事項の新規発生なし。`held` 在庫の追加なしで終了。

## Phase Execution Record（2026-04-27 / Stream C / strict Phase 1-6 rerun）
### Phase 1 Read（Read同期）
- Phase開始時に本IssueをRead同期し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（canonical 5 IDs）を再確認。
- 差分検知結果: 語彙・禁止事項・SafeMode境界の差分は 0 件。停止条件（差分検知時 `held`）は未発火。

### Phase 2 Plan（Read同期）
- Phase開始時に再Readし、Phase 1との差分がないことを確認してから計画を固定。
- Scopeを `01_Plans/issues/issue-CE0-core-graph-repositioning.md` の契約固定記述更新のみに限定（implementation禁止 / single-file）。
- 差分検知結果: 0 件。差分が発生した場合は即停止し承認待ちへ移行する条件を再確認。

### Phase 3 ADR/CDC（Read同期）
- Phase開始時に再Readし、方針差分（ADR/CDC起票要否）を確認。
- 判定: `No ADR delta`（契約固定の範囲で完了可能）。
- 差分検知結果: 0 件。差分が出た場合は `pending` 記録後に `held` で停止する。

### Phase 4 Execute（Read同期）
- Phase開始時に再Readし、固定語彙と禁止事項の不一致がないことを確認後に本記録のみ追記。
- `role / transition / no-go` の再定義・同義語置換・拡張は未実施。実装記述（handler/UI/DB/worker/API/Schema migration）追加なし。
- 差分検知結果: 0 件（契約境界の逸脱なし）。

### Phase 5 Verify（Read同期 / self-heal <= 3）
- Phase開始時に再Readし、検証対象と停止条件（4回目相当で停止）を確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し pass。
- `git diff --check` を実行し pass。
- Self-Correction実績: 0/3（4回目相当なし）。

### Phase 6 Proceed（Read同期）
- Phase開始時に再Readし、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（contract-only / implementation禁止 / single-file 制約維持）。
- 未承認事項在庫: なし。差分検知時停止ルールを維持したまま終了。

## Phase Execution Record（2026-04-27 / Stream C / requested Phase 1→2(ADR/CDC)→3→4→5→6）
### Phase 1 Read
- 開始時Readを実施し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（canonical 5 IDs）とSafeMode境界を再確認した。
- 差分判定: 語彙・禁止事項・SafeMode境界の差分は 0 件。停止条件（前提崩れ / 未定義競合）未発火。

### Phase 2 ADR/CDC確認
- 開始時Readを再実施し、方針差分の有無を確認した。
- 判定: `No ADR delta`（契約固定の範囲で継続可能）。
- 未承認論点を確定化せず、必要時は `pending` または `held` で在庫化する運用を維持。

### Phase 3 Plan（AC/DoD補完）
- 開始時Readを再実施し、直前Phaseとの差分なしを確認してから計画を固定した。
- AC/DoDは既存定義で充足可能と判断し、追加補完は不要（不足検知なし）。
- Scopeを本Issue単独の契約記述更新に限定し、実装変更・契約ID再定義・語彙拡張を非対象とした。

### Phase 4 Execute
- 開始時Readを再実施し、固定語彙と禁止事項の不一致がないことを確認したうえで本レコードのみ追記した。
- contract-only / docs-only / single-file 境界を維持し、他ファイル編集は未実施。

### Phase 5 Verify（自己修復最大3回）
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復回数: 0/3。4回目相当は未実施。

### Phase 6 Proceed/Stop
- 判定: `Proceed=Done`（AC/DoD整合 + docs-check pass）。
- 停止条件（前提崩れ / 未定義競合 / 3回超過）は未発火。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Phase Execution Record（2026-04-27 / Stream C専任 / CE0 Core Graph contract-only phase-cycle sync）
### Phase 1 Read（role / transition / no-go 再同期）
- Phase開始時Readを実施し、固定語彙 `working` / `context_projection` / `consensus` を再確認。
- `working -> consensus` は `patch+approval` のみ許可であることを再確認。
- canonical No-Go 5 IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）を再確認し、差分 0 件。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで再定義なし。

### Phase 2 Plan（contract-only / single-file）
- Scopeを本Issue単体の契約記述と実行記録追記に限定。
- Non-Goals（実装変更、語彙再定義、SafeMode後退、未承認事項の確定化）を再確認。
- AC/DoD不足は未検出。新規ドラフト提案は不要と判定。

### Phase 3 ADR Consensus
- 方針差分判定を実施し、結果は `No ADR delta`。
- 方針差分が将来発生する場合のみ Context/Decision/Consequences を追記し、承認まで `held` を維持するルールを継続。

### Phase 4 Execute（contract文言のみ更新）
- 編集対象を `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみに固定して更新。
- `role / transition / no-go` 固定語彙を維持し、同義語置換・拡張定義を行わない。
- SafeMode既定ON境界を後退させる記述を追加しない。

### Phase 5 Verify（docs-check / self-repair <= 3）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Verify失敗は発生せず、自己修復回数は 0/3。

### Phase 6 Proceed
- Proceed条件（AC/DoD充足 + docs-check pass）を満たすことを確認。
- 判定: `Done`（contract-only / single-file / 語彙固定 / SafeMode境界維持）。
- 未承認事項在庫: なし。将来発生時は `held/pending` で在庫化し、確定しない。

## Phase Execution Record（2026-04-27 / Stream C / user-requested phase order strict run）
### Phase 1 Read（語彙差分チェック）
- Phase開始時に `role / transition / no-go` 語彙差分チェックを実施し、差分 0 件（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を維持）。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで再定義なし。
- SafeMode境界（既定ON維持、緩和禁止）に差分なし。

### Phase 2 Plan（語彙差分チェック）
- Phase開始時に再Readし、`role / transition / no-go` と禁止事項の差分を再確認、差分 0 件。
- Scopeを本Issue単体の記録追記に限定（docs-only / contract-only / single-file）。
- 禁止事項（実装変更、CE0契約ID再定義、No-Go語彙変更）を再確認。

### Phase 3 ADR Consensus（Context / Decision / Consequences、語彙差分チェック）
- Phase開始時に語彙差分チェックを実施し、差分 0 件。
- Context: CE0 Core Graph責務境界を契約固定のまま維持し、未承認事項の確定化を回避する必要がある。
- Decision: `No ADR delta`。既存契約（role/transition/no-go、SafeMode境界）を維持し、新規承認事項は追加しない。
- Consequences: 未承認論点が発生した場合は `held` または `pending` を維持し、承認完了まで確定しない。

### Phase 4 Execute（語彙差分チェック）
- Phase開始時に語彙差分チェックを実施し、差分 0 件。
- 本Issueへの実行記録追記のみを実施（実装記述追加なし、他ファイル編集なし）。
- contract-only 境界と固定語彙を維持。

### Phase 5 Verify（語彙差分チェック / 自己修復最大3回）
- Phase開始時に語彙差分チェックを実施し、差分 0 件。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復回数: 0/3（上限超過なし）。

### Phase 6 Proceed（語彙差分チェック）
- Phase開始時に語彙差分チェックを実施し、差分 0 件。
- 判定: `Done`（Read → Plan → ADR Consensus → Execute → Verify → Proceed の順序を満たし、docs-check pass）。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。


## Phase Execution Record（2026-04-27 / Stream C / CE0 Core Graph Repositioning strict serial run）
### Phase 1 Read
- Phase開始時Read同期を実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認した。
- 差分判定: 語彙・禁止事項・SafeMode境界の差分は 0 件で、停止条件は未発火。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Phase開始時Read同期を再実施し、方針差分の有無を確認した。
- Context: CE0 Core Graph責務境界を proposal-only の契約固定として維持する必要がある。
- Decision: `No ADR delta`（契約語彙固定で継続、未承認事項は確定しない）。
- Consequences: 未承認事項が発生した場合は `pending` または `held` で在庫化し、承認まで確定化しない。

### Phase 3 Plan（契約境界・非目標・検証）
- Phase開始時Read同期を再実施し、Phase 2との差分なしを確認してから計画を固定した。
- Plan: single-file / docs-only / contract-only を維持し、Core Graph直接更新を許容しない（proposal-only前提を維持）。
- Non-Goals: 実装変更、CE0契約ID再定義、No-Go語彙拡張、SafeMode既定ON後退、未承認事項の確定化。
- Verification plan: `docs-check` と `git diff --check` を実行し、失敗時は自己修復最大3回で打ち切る。

### Phase 4 Execute（契約文面のみ）
- Phase開始時Read同期を再実施し、差分 0 件を確認してから本Issue本文の実行記録のみ追記した。
- 編集対象は `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみとし、他ファイル編集は行わない。

### Phase 5 Verify（安全境界と整合）
- Phase開始時Read同期を再実施し、語彙・禁止事項・SafeMode境界の差分 0 件を確認した。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- Self-Correction実績: 0/3（上限超過なし）。

### Phase 6 Proceed（Go / Conditional / No-Go）
- Phase開始時Read同期を再実施し、Proceed判定条件（AC/DoD充足 + docs-check pass）を確認した。
- 判定: `Go=Done`（contract-only / proposal-only / single-file 制約を維持）。
- Conditional/No-Go該当: なし。未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Phase Execution Record（2026-04-27 / Stream C / CE0 strict serial rerun-2）
### Phase 1 Read
- Phase開始時Read同期を実施し、`role / transition / no-go` 固定語彙（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs）を再確認。
- 差分判定: 語彙・禁止事項・SafeMode境界の差分は 0 件。ドリフトは未検出。

### Phase 2 ADR/CDC
- Phase開始時Read同期を再実施し、方針差分の有無を確認。
- Context: CE0 Core Graph Repositioning は contract-only で契約固定を継続する。
- Decision: `No ADR delta`（CE0契約ID再定義なし、語彙固定維持、未承認事項の確定化なし）。
- Consequences: 未承認事項が発生した場合は `held` または `pending` で管理し、承認まで確定しない。

### Phase 3 Plan
- Phase開始時Read同期を再実施し、Phase 2との差分なしを確認。
- Scope: 本Issue 1ファイルの実行記録追記のみ（single-file / docs-only / contract-only）。
- Non-Goals: 実装変更、CE0契約ID再定義、語彙同義語拡張、SafeMode既定ON後退、未承認事項の確定化。

### Phase 4 Execute
- Phase開始時Read同期を再実施し、固定語彙・禁止事項・SafeMode境界の差分なしを確認して実行。
- 実行内容は本Issue本文への追記のみ。実装ファイル・他ドキュメントは変更しない。

### Phase 5 Verify
- Phase開始時Read同期を再実施し、語彙差分・禁止事項逸脱・SafeMode境界ドリフトがないことを確認。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- self-correction 実績: 0/3（上限超過なし）。

### Phase 6 Proceed
- Phase開始時Read同期を再実施し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（Read → ADR/CDC → Plan → Execute → Verify → Proceed の固定順序を満たす）。
- フェイルセーフ該当: なし（語彙・禁止事項・safeMode境界ドリフトなし、未承認事項確定化要求なし、self-correction上限超過なし）。

## Phase Execution Record（2026-04-28 / Stream C / CE0 core graph boundary contract freeze run）
### Phase 1 Read
- 固定語彙と既存契約との差分を再読し、`working` / `context_projection` / `consensus` の3語彙、`working -> consensus` + `patch+approval`、canonical 5 IDs の差分が 0 件であることを確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみとし、再定義・拡張・別名化を行わないことを確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0 Core Graph Repositioning の目的は責務境界契約の固定であり、語彙再定義・拡張を禁止したまま運用する必要がある。
- Decision: `No ADR delta`。契約は既存固定を維持し、`working` は編集作業領域、`context_projection` は read-only投影、`consensus` は承認済み合意領域として責務境界を固定する。
- Consequences: 未承認論点は `held` または `pending` の在庫として扱い、推測確定を禁止する。

### Phase 3 Plan
- AC/DoD不足を点検し、契約境界・禁止事項・検証導線（docs-check）を満たすための追補は不要と判定。
- Planを single-file / docs-only / contract-only に固定し、実装変更・依存仕様の推測確定・指定外編集要求への追従を非目標として明示。

### Phase 4 Execute
- 契約文言整備のみを実施し、責務境界契約を以下で固定:
  - `working`: 編集作業領域（proposal生成は可、合意領域への直接反映は不可）
  - `context_projection`: read-only投影（直接編集不可）
  - `consensus`: 承認済み合意領域（`patch+approval` 経由のみ更新可）
- 語彙再定義・同義語置換・拡張定義は実施しない。

### Phase 5 Verify（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数は 0/3。上限超過・前提崩れ・指定外編集要求は発生なし。

### Phase 6 Proceed（Go / Conditional / No-Go）
- 判定: `Go=Done`（AC/DoD整合、docs-check pass、contract-only維持）。
- Conditional: なし。
- No-Go: 該当なし（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation` の新規発生なし）。
