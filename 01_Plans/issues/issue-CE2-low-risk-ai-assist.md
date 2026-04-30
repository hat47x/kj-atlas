# Issue Draft: CE2 Low-Risk AI Assist（CE2意思決定準備 / proposal-only contract lock）

- Type: Process / Decision preparation
- Status: Draft
- Priority: P1
- Owner: Stream F（CE2意思決定準備専任）
- Scope: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ（single-file fixed）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `ADR-0001`, `02_Architecture/schemas.md`
- Dependencies: `CE-2`
- Expected verification level: `docs-check`

## Fixed Operation Contract（2026-04-29）

- proposal-only 原則を固定し、AIは候補提示（`status=proposed`）のみを実施する。
- `accepted / rejected` は人間責務。AIによる自動確定経路は作成しない。
- Auto操作（`auto-apply / auto-confirm / auto-publish`）を禁止する。
- `reviewState` は `unreviewed | human_reviewed` の閉集合とし、AI提案は常に `unreviewed`。
- lifecycle は `proposed | accepted | rejected | held` の閉集合を維持する。
- 監査4点（`query / bundle / proposal / apply`）が欠損した場合は fail-closed。
- **合意未取得時は CE2実装へ進まない（Proceed禁止）。**

## Phase Contract（Read → Context/Decision/Consequences → Risk Compare → Hold/Stop-Ready → Proceed）

### Phase 1: Read（held理由と承認条件抽出）
- CE2が `held` である理由を明文化する（安全境界・責務境界・監査欠損リスク）。
- 承認条件を抽出し、チェックリスト化する。
- CE0/CE1/CE4 は read-only 参照とし、CE2側で語彙再定義しない。
- 差分ドリフト・契約衝突・前提崩壊を検知した場合は即 `status=held` 維持。

### Phase 2: Context / Decision / Consequences 候補（複数案）
- ADR関連差分は **CD&C（Context / Decision / Consequences）** を必須化する。
- 最低3案を作成し、各案に「採用時の利点」「不採用時の根拠」を付与する。
- 合意前はすべて「候補（Draft）」として扱い、確定語を使用しない。

#### Option A: Strict Minimal（最小変更）
- Context: CE2で必要最小限の文書固定のみ行い、実装示唆を一切増やさない。
- Decision候補: proposal-only境界と承認ゲート文言のみ強化。
- Consequences候補: 低リスクだが、将来の実装開始時に補足整理コストが残る。

#### Option B: Balanced Gate（推奨）
- Context: CE2着手前に承認条件・停止条件・監査条件を等量で固定する。
- Decision候補: proposal-only境界に加え、承認チェックと逆戻り条件を明文化。
- Consequences候補: リスクと再開性のバランスが良く、意思決定ログを再利用しやすい。

#### Option C: Evidence-Heavy（監査強化）
- Context: 監査証跡の粒度を最大化し、例外処理の分岐まで先に定義する。
- Decision候補: fail-closed 条件と監査4点の拡張チェックを追加。
- Consequences候補: 監査性は高いが、準備コストとレビュー負荷が増加する。

### Phase 3: リスク・逆戻りコスト比較
- 各案について「安全リスク」「運用負荷」「逆戻りコスト（rework）」を比較する。
- 比較は定性3段階（Low / Medium / High）で固定し、曖昧語を避ける。

| Option | 安全リスク | 運用負荷 | 逆戻りコスト | 総評 |
| --- | --- | --- | --- | --- |
| A: Strict Minimal | Low | Low | Medium | 早いが、後工程で再整理が発生しやすい |
| B: Balanced Gate | Low | Medium | Low | **推奨**。合意形成と再開性の均衡が取れる |
| C: Evidence-Heavy | Low | High | Low | 強固だが重い。短期の意思決定速度は低下 |

### Phase 4: 合意取得待ち状態の明確化（停止可能化）
- 合意未取得時の状態を `status=held` として明示し、停止可能な記述へ固定する。
- 停止中に許可される操作は「候補更新」「根拠追記」「比較表更新」のみ。
- 停止中に禁止される操作は「実装開始」「契約確定扱い」「承認済み表現への変更」。
- 人間判断待ち論点（Pending）を明示し、次回再開条件を1行で記録する。

### Phase 5: Proceed（承認取得時のみ次工程へ）
- Proceed条件は **全承認条件充足 + 明示承認ログ** を満たした場合のみ true。
- 承認が1件でも不足する場合は `status=held` 継続。

#### Proceed Gate Checklist
- [ ] proposal-only が維持されている（自動確定経路なし）
- [ ] `accepted/rejected` が人間責務として明記されている
- [ ] CD&C と承認ゲートがADR関連差分に適用されている
- [ ] 監査4点の欠損時 fail-closed が明記されている
- [ ] リスク・逆戻りコスト比較が最新化されている
- [ ] 人間の明示承認（日時・承認者・対象）が記録されている

## Acceptance Criteria（AC）

- [ ] 本Issueは single-file scope（本ファイルのみ編集）を維持する。
- [ ] proposal-only 原則と No-Go（auto-apply / auto-confirm / auto-publish禁止）が明示される。
- [ ] `accepted/rejected` の人間責務と `reviewState` 閉集合が明示される。
- [ ] 5 Phase（Read / CD&C案 / リスク比較 / 合意待ち明確化 / Proceed条件）が直列で明示される。
- [ ] CD&C は複数案（最低3案）と比較表を含む。
- [ ] 合意未取得時に実装へ進まない fail-safe が明示される。

## Definition of Done（DoD）

- [ ] ACを満たし、矛盾する旧運用文言が削除されている。
- [ ] `status=held` 運用（合意前は実行しない）が保持されている。
- [ ] docs-check（目視差分確認）で契約逸脱がない。
- [ ] CE境界（CE0/CE1/CE2/CE4）の責務分離が維持されている。
- [ ] Proceed条件が「承認取得時のみ」であることが明記されている。

## Fail-safe Stop Conditions（即停止）

- 合意未取得のまま次工程（実装・確定運用）へ進む要求。
- Self-Correction `4/3` 相当（最大3回超過）。
- safeMode既定ONや未レビュー保護など安全境界の後退要求。
- 未定義競合（契約衝突・語彙衝突・責務分離崩壊）の検知。

## Validation Plan

- 実行コマンド:
  - `git diff -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
- 期待結果:
  - single-file scope で、5 Phase契約・CD&C複数案・リスク比較・held維持・Proceed条件（承認取得時のみ）が確認できる。
- 未実施時の理由・代替検証:
  - なし（docs-checkのみ）。
