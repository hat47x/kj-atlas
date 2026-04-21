# Issue Draft: CE0 Contract Freeze（Stream B / CE0 Contract SSOT / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream B（CE0 Contract Freeze 専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-contract-freeze.md` のみ
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（このレーンの絶対条件 / CE SSOT）
- CE0をCE契約のSSOT（single source of truth）とし、CE1/CE2/CE4は**参照のみ**で利用する。
- 本Issueは**計画・契約先行のみ**を扱う。実装（`03_Implement/**`）と共有統合ファイルは対象外。
- CE0契約IDは再定義禁止（freeze対象）：`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- CE0 Contract IDの追加・改名・削除を禁止する（freeze中の再定義不可）。
- safeMode既定値（ON, `allowUnreviewedText=false`）の後退を禁止する。
- 推測実装（speculative implementation）を禁止し、記載根拠は本Issue内の固定語彙/固定I/Fに限定する。
- 致命エラー（Fail-safe該当）検知時は即停止し、`held` へ戻す。
- 未承認決定を確定扱いしない（承認待ち論点は `held`）。
- 強制ワークフローは **`Phase 1 Read → Phase 2 Plan（AC/DoD補完） → Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed`**。
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

## Phase 2 Plan（I/F Mock Freeze計画 + AC/DoD補完）
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

### AC/DoD補完提案の合意明記（Phase 2）
- 合意対象: AC不足候補A/B/C の補完方針そのもの（実装や下流再定義は含めない）。
- 合意記録:
  - `agreement_scope`: CE0契約本文の語彙固定と判定根拠の明確化のみ。
  - `agreement_state`: `held`（承認待ち）
  - `agreement_note`: 承認前は運用確定扱いせず、Phase 3では「契約語彙統一」と「禁止事項単一化」の編集に限定する。
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

## Phase 3 Execute（Plan反映のみ。契約再定義・実装変更なし）
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
- CE0 SSOT本文のみを整備し、下流Issueは Contract ID参照で解釈可能な状態に保つ。
- CE1/CE2/CE4への handoff は「参照のみ（本文複製なし）」で表現を固定する。
- No-Go語彙IDの照合観点をCE0に明記し、下流への受け渡しは語彙ID参照のみとする。
- Phase 2で `held` 化したAC/DoD補完提案は、承認前に確定扱いしない。

### Execute結果条件
- `collision=0` / `safeMode regression=0` を満たす記述へ整理。
- 検証失敗時は自己修復を最大3回まで実施し、4回目相当は停止する。

## Phase 4 Verify（docs-check自己検証）
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

## Phase 5 Proceed（次工程向け固定契約の出力）
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

### CE1/CE2/CE4向け参照I/F一覧（read-only handoff）
- CE1（Context Bundle consumer）: `CE0-CTX-IF` / `CG-01` / `CG-02`
- CE2（Review governance consumer）: `CE0-REVIEW-IF` / `CE0-SAFEMODE-IF` / `CG-03` / `CG-04`
- CE4（Audit & fail-closed consumer）: `CG-01..05` / `CE0-SAFEMODE-IF`
- 共通条件: Contract ID参照のみ、本文複製禁止、再定義禁止、差分要求はCE0再起票

### Handoff boundary record（参照専用境界の記録）
- Boundary mode: read-only reference（CE1/CE2/CE4は参照専用、再定義不可）。
- Transfer unit: Contract ID + No-Go ID のみ（契約本文の複製なし）。
- Escalation rule: 境界逸脱の要求は `scope_deviation` としてCDC `held` を起票し、承認完了まで停止。

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊
