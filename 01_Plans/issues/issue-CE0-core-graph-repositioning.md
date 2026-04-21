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
- 強制ワークフローは `Phase 1 Read → Phase 2 Plan → Phase 3 ADR CDC → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed`。
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

## Phase 3 ADR CDC（方針差分が必要な場合のみ）
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

### Phase 3 ADR CDC
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

### Phase 3 ADR CDC
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
