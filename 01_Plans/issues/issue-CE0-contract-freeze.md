# Issue Draft: CE0 Contract Freeze（Stream C / CE契約専任 / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream C（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-contract-freeze.md` のみ
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（このレーンの絶対条件）
- 本Issueは**計画・契約先行のみ**を扱う。実装（`03_Implement/**`）と共有統合ファイルは対象外。
- CE0契約IDは再定義禁止：`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- 未承認決定を確定扱いしない（承認待ち論点は `held`）。
- safeMode後退、auto-apply許容、未承認確定化を検知したら即停止。
- 強制ワークフローは `Plan → Execute → Verify → Proceed`。

## Phase 1) Read（CE0契約ID群・NoGo語彙・safeMode境界の再確認）
### 固定I/F（参照のみ）
- `CE0-CTX-IF`: ContextQuery必須キー + deterministic `bundleHash`。
- `CE0-SAFEMODE-IF`: safeMode既定ON、`allowUnreviewedText=false` 既定。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみ。
- `CG-01..05`: `Working -> Consensus` は `patch + approval` のみ。

### No-Go語彙（固定）
- Query Preview bypass
- Consensus direct write
- auto-apply / auto-publish
- AIによる review 自動昇格
- safeMode既定緩和

## Phase 2) Plan（CE1/CE2/CE4への参照境界を再定義なしで設計）
- CE1参照境界: `ContextQuery/ContextBundle` + hash決定論（`CE0-CTX-IF`参照のみ）。
- CE2参照境界: proposal-only + review自動昇格禁止（`CE0-REVIEW-IF`参照のみ）。
- CE4参照境界: 監査4点 `query/bundle/proposal/apply` と fail-closed（`CG-01..05`参照のみ）。
- safeMode境界は `CE0-SAFEMODE-IF` を上位正本として固定し、下流Issueで再定義しない。

## Phase 3) ADR CDC（変更時のみ Context / Decision / Consequences を明文化）
### CDC条件（変更が発生した場合のみ記録）
- **Context**: 何の衝突・曖昧性を解消するか。
- **Decision**: 既存契約IDを再定義せず、参照境界のみを明確化したこと。
- **Consequences**: CE1/CE2/CE4の依存先が一意化されること。

### 凍結判定
- Contract ID collision = 0
- Vocabulary collision = 0（`Consensus Graph / WorkingGraph / ContextProjectionGraph`）
- 承認前は `provisional`、承認後のみ `frozen`

## Phase 4) Execute（collision=0 / safeMode regression=0 を満たす整理）
- 5 Issue横断で契約語彙を照合し、再定義を除去する。
- CE1/CE2/CE4への handoff を「参照のみ」に統一する。
- No-Go語彙が全Issueで同一かを確認し、揺れがあれば修正する。
- 検証失敗時は自己修復を最大3回まで実施し、4回目相当は停止する。

## Phase 5) Verify / Proceed（docs-check と再開条件の記録）
### Acceptance Criteria
- [ ] Contract ID collision = 0
- [ ] Vocabulary collision = 0
- [ ] SafeMode regression = 0
- [ ] No-Go語彙一致（direct write / auto-apply / preview bypass）
- [ ] CE1/CE2/CE4参照境界を再定義なしで説明可能

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Proceed（再開条件）
- 再開条件1: `collision=0` を維持したまま差分説明が可能。
- 再開条件2: `safeMode regression=0` を維持。
- 再開条件3: No-Go検知時は即停止→原因切り分け→3回以内に自己修復。
