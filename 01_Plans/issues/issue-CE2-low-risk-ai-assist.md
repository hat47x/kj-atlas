# Issue Draft: CE2 Low-Risk AI Assist（proposal-only contract lock）

- Type: Process / Documentation quality
- Status: Draft（`status=held` until human agreement）
- Priority: P1
- Owner: Stream E（CE2専任）
- Scope: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ（single-file fixed）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

## Fixed Operation Contract（2026-04-28）

- proposal-only 原則を固定し、AIは候補提示（`status=proposed`）のみを実施する。
- `accepted / rejected` は人間責務。AIによる自動確定経路は作成しない。
- Auto操作（`auto-apply / auto-confirm / auto-publish`）を禁止する。
- `reviewState` は `unreviewed | human_reviewed` の閉集合とし、AI提案は常に `unreviewed`。
- lifecycle は `proposed | accepted | rejected | held` の閉集合を維持する。
- 監査4点（`query / bundle / proposal / apply`）が欠損した場合は fail-closed。

## Phase Contract（Read → Plan → Execute → Verify → Proceed）

### Phase 1: Read
- 各Phase開始時に Read 同期を必須化する。
- CE0/CE1/CE4 は read-only 参照とし、CE2側で語彙再定義しない。
- 差分ドリフト・契約衝突・前提崩壊を検知した場合は即 `status=held`。

### Phase 2: Plan
- AC/DoD不足を検知した場合は「不足ドラフト提案」のみ実施する。
- 人間合意が成立するまで `status=held` を維持し、Executeへ進まない。
- ADR関連差分は **CD&C（Context / Decision / Consequences）** を明文化し、承認ゲート通過前は `held` 固定。

### Phase 3: Execute
- contract-only（docs patch/diff 記録）に限定する。
- 実装確定・自動適用・自動公開の経路は導入しない。
- AI提案の `reviewState` は `unreviewed` 固定。

### Phase 4: Verify
- proposal-only 境界、review境界、人間責務境界の後退がないことを確認する。
- 監査4点（`query / bundle / proposal / apply`）の追跡可能性を確認する。
- Self-Correctionは最大3回（`1/3`〜`3/3`）。`4/3` 相当は fail-safe 停止。

### Phase 5: Proceed
- [ ] proposal-only が維持されている（自動確定経路なし）
- [ ] `accepted/rejected` が人間責務として明記されている
- [ ] CD&Cと承認ゲートがADR関連差分に適用されている
- [ ] 監査4点の欠損時 fail-closed が明記されている
- [ ] Self-Correction超過・安全境界後退・未定義競合が未発火

## Acceptance Criteria（AC）

- [ ] 本Issueは single-file scope（本ファイルのみ編集）を維持する。
- [ ] proposal-only 原則と No-Go（auto-apply / auto-confirm / auto-publish禁止）が明示される。
- [ ] `accepted/rejected` の人間責務と `reviewState` 閉集合が明示される。
- [ ] Phaseは Read→Plan→Execute→Verify→Proceed の5段直列として明示される。
- [ ] ADR関連差分の CD&C 明文化 + 承認ゲートが明示される。
- [ ] Verifyに Self-Correction最大3回と fail-safe 停止条件が明示される。

## Definition of Done（DoD）

- [ ] ACを満たし、矛盾する旧運用文言が削除されている。
- [ ] `status=held` 運用（合意前は実行しない）が保持されている。
- [ ] docs-check（目視差分確認）で契約逸脱がない。
- [ ] CE境界（CE0/CE1/CE2/CE4）の責務分離が維持されている。

## Fail-safe Stop Conditions（即停止）

- Self-Correction `4/3` 相当（最大3回超過）。
- safeMode既定ONや未レビュー保護など安全境界の後退要求。
- 未定義競合（契約衝突・語彙衝突・責務分離崩壊）の検知。

## Validation Plan

- 実行コマンド:
  - `git diff -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
- 期待結果:
  - single-file scope で、5 Phase契約と proposal-only/CD&C/承認ゲート/停止条件が確認できる。
- 未実施時の理由・代替検証:
  - なし（docs-checkのみ）。
