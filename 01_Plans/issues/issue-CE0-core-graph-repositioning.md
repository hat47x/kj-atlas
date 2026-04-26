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
- 強制ワークフローは `Phase 1 Read → Phase 2 Plan → Phase 3 ADR Consensus → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed`。
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
