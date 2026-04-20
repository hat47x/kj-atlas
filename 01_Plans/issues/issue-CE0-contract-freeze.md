# Issue Draft: CE0 Contract Freeze（Stream C / CE契約群 / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream C（CE契約群）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-contract-freeze.md` のみ
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（このレーンの絶対条件 / CE SSOT）
- CE0をCE契約のSSOT（single source of truth）とし、CE1/CE2/CE4は**参照のみ**で利用する。
- 本Issueは**計画・契約先行のみ**を扱う。実装（`03_Implement/**`）と共有統合ファイルは対象外。
- CE0契約IDは再定義禁止（freeze対象）：`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- 未承認決定を確定扱いしない（承認待ち論点は `held`）。
- 強制ワークフローは `Phase 1 Read → Phase 2 Plan → Phase 3 ADR CDC → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed`。
- **各Phase開始時は本Issueを最新再読してから開始する（再読省略禁止）。**
- 自己修復は Verify で最大3回まで。4回目相当は即停止する。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### 最新再読チェック（Phase開始ゲート）
- 対象ファイル: `issue-CE0-contract-freeze.md`（本書のみ）
- CE0 SSOT再定義禁止 / 実装禁止 / 指定外編集禁止を再確認
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

## Phase 2 Plan（I/F Mock Freeze計画: ContextQuery / ContextBundle / Review 境界をI/Fのみ固定）
### 最新再読チェック（Phase開始ゲート）
- Phase 1の固定語彙・No-Go語彙・Scopeを再読し、差分ゼロを確認してから着手する。

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

Freeze判定（全て必須）:
- 参照方向は `CE0 -> (CE1, CE2, CE4)` の一方向のみ（逆参照での再定義禁止）。
- CE1/CE2/CE4は contract本文の複製を行わず、Contract ID参照のみ記述する。
- 参照先に差分が必要な場合は CE0再起票（本Issue）を経由し、下流Issueで先行確定しない。

## Phase 3 ADR CDC（方針差分時のみ Context / Decision / Consequences を記録し承認待ち）
### 最新再読チェック（Phase開始ゲート）
- CDCは「差分検知時のみ起票」の原則を再読し、未検知時の不要起票を禁止する。

### CDC条件（変更が発生した場合のみ記録）
- 差分検知ログ（Phase 1起点）: 契約ID衝突 / No-Go語彙揺れ / Scope逸脱のいずれかがあればCDC化する。
- **Context**: 何の衝突・曖昧性を解消するか。
- **Decision**: 既存契約IDを再定義せず、参照境界のみを明確化したこと。
- **Consequences**: CE1/CE2/CE4の依存先が一意化されること。
- **Approval**: 反映状態は `held` とし、承認前確定を禁止する。
- 衝突未検知時（`contract_id_collision=0` かつ `vocabulary_collision=0` かつ `scope_deviation=0`）はCDCを起票しない。

### ADR CDC起票テンプレ（必要時のみ）
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

### 凍結判定
- Contract ID collision = 0
- Vocabulary collision = 0（`Consensus Graph / WorkingGraph / ContextProjectionGraph`）
- 承認前は `provisional`、承認後のみ `frozen`

## Phase 4 Execute（Plan反映のみ。契約再定義・実装変更なし）
### 最新再読チェック（Phase開始ゲート）
- CE0 Contract IDs再定義禁止、proposal-only、safeMode既定維持を再確認する。

### Execute Plan（実行前固定）
- 5 Issue横断で契約語彙を照合し、再定義を除去する。
- CE1/CE2/CE4への handoff を「参照のみ」に統一する。
- No-Go語彙が全Issueで同一かを確認し、揺れがあれば修正する。
- AC/DoD不足があれば CE0側で補完提案を先に明文化し、承認前は `held` とする。

### AC/DoD不足ドラフト（CE0で先に固定）
- AC不足候補A: 「read-only参照」の判定根拠が曖昧
  - 追記案: `Matrix` に「許可される変更はリンク更新/注記のみ」を必須条件として明記済みであることをDoDに含める。
- AC不足候補B: No-Go語彙の表記揺れによる誤判定
  - 追記案: 5語彙ID（`preview_bypass` ほか）を照合キーに固定し、自然言語は同義語扱いに限定する。
- AC不足候補C: CDC発火条件の見落とし
  - 追記案: `contract_id_collision | vocabulary_collision | scope_deviation` のいずれか検知時は `held` 記録を必須化する。
- Status: `held`（承認待ち。確定運用は承認後）

### Execute
- collision=0 / safeMode regression=0 を満たす記述へ整理。
- 検証失敗時は自己修復を最大3回まで実施し、4回目相当は停止する。

## Phase 5 Verify（docs-check自己検証）
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

## Phase 6 Proceed（次工程向け固定契約の出力）
### 最新再読チェック（Phase開始ゲート）
- Verify結果とAC/DoDを再読し、未達項目があれば Proceed せず `held` に戻す。

### Fixed contract handoff
- Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
- 禁止事項: direct write / auto-apply / preview bypass / AI review昇格 / safeMode緩和
- 検証条件: collision=0, SafeMode regression=0, docs-check pass

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊
