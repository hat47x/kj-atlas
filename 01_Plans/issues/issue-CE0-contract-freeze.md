# Issue Draft: CE0 Contract Freeze（Stream B / CE契約専任 / planning-only）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream B（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（このレーンの絶対条件）
- 本Issueは**計画・契約先行のみ**を扱う。実装（`03_Implement/**`）は対象外。
- CE0契約IDは再定義禁止：`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- 未承認決定を確定扱いしない（承認待ち論点は `held` 扱い）。
- safeMode後退・自動確定化（auto-apply/auto-publish/auto-review昇格）を禁止する。
- 実装指示が混入した場合は **Stop**（planning lane fail-safe）。

## Phase 1) Read同期（ADR-0028整合確認）
### 固定I/F（ADR-0028 D2/D6準拠）
- `CE0-CTX-IF`: ContextQuery必須キーと deterministic `bundleHash`。
- `CE0-SAFEMODE-IF`: safeMode既定ON、`allowUnreviewedText=false` 既定。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみ。
- `CG-01..05`: `Working -> Consensus` は `patch + approval` のみ。

### 禁止事項（No-Go）
- Query Preview bypass
- Consensus direct write
- auto-apply / auto-publish
- AIによる review 自動昇格
- safeMode既定緩和

## Phase 2) Plan（AC/DoD不足時の提案）
### 補強提案（不足がある場合のみ追加）
- AC不足時は「衝突ゼロ」「safeMode後退ゼロ」「参照境界の再定義ゼロ」を最小セットとして補完する。
- DoD不足時は「契約語彙単一正本」「実装依存記述なし」「検証手順の再現可能性」を補完する。
- 補強提案は CE0既存契約（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の参照に限定し、再定義しない。

## Phase 3) ADR CDC（必要時のみ: CE0契約凍結）
### CDC（Contract Definition Check）
- Contract ID collision = 0
- Vocabulary collision = 0（`Consensus Graph / WorkingGraph / ContextProjectionGraph`）
- CE1/CE2/CE4 は CE0契約を**参照のみ**で使用し、再定義しない

### 承認ゲート
- Freeze候補を「固定契約」「禁止事項」「停止条件」の3ブロックで提示
- 承認前は `provisional`、承認後のみ `frozen`

## Phase 4) Execute（Issue粒度・依存・検証計画の確定）
### CE1/CE2のmock前提I/F分離（参照境界固定）
- CE1へ渡す境界: `ContextQuery/ContextBundle` + hash決定論（`CE0-CTX-IF`参照）
- CE2へ渡す境界: proposal-only + review自動昇格禁止（`CE0-REVIEW-IF`参照）
- 共通: safeMode境界は `CE0-SAFEMODE-IF` の参照のみ（CE1/CE2側で再定義しない）

### CE4連携契約（API/CLI/Audit）定義
- CE4へ渡す必須監査導線: `query / bundle / proposal / apply`
- CE4同値判定の前提: `equivalenceKey + bundleHash`
- 欠損成功扱い禁止（fail-closed）

## Phase 5) Verify / Proceed（検証可能性・再開可能性チェック）
### Acceptance Criteria
- [ ] Contract ID collision = 0
- [ ] Vocabulary collision = 0
- [ ] SafeMode regression = 0
- [ ] No-Go語彙（direct write / auto-apply / preview bypass）一致
- [ ] CE1/CE2/CE4への参照境界が再定義なしで説明可能

### Definition of Done
- [ ] 5 Issue間で契約語彙が単一正本化されている
- [ ] 実装依存記述を含まない
- [ ] `docs-check` で差分説明可能

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- 自己修復は最大3回。4回目相当は停止。

### Proceed（実装ストリーム向けI/F配布）
- `CE0-CTX-IF`
- `CE0-SAFEMODE-IF`
- `CE0-REVIEW-IF`
- `CG-01..05`

> Proceed条件: `collision=0` かつ `safeMode regression=0`。未達時は fail-safe 停止。
