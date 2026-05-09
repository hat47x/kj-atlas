# Issue Draft: CE2 Low-Risk AI Assist（CE2意思決定準備 / proposal-only contract lock）

- Type: Process / Decision preparation
- Status: Draft
- Priority: P1
- Owner: Stream E（CE2 Open化準備専任 / proposal-only）
- Scope: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ（single-file fixed）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `ADR-0001`, `02_Architecture/schemas.md`
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（契約依存）, `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`（I/F依存; mockで切断可能）
- Dependency status: `未確定（CE-2 Open判定待ち）`
- CE1 contract status: `参照限定（CE1完了待ちは不要。mock contract参照のみ）`
- Expected verification level: `docs-check`

## Mission contract（Stream H 統合 / CE2専任）

- 本Issueは **proposal-only の成熟化** のみを扱う（実装変更禁止）。
- `human-final / no-auto / fail-closed` の3原則を明文化維持する。
- CE0/CE1依存は **read-only参照** とし、CE2側で確定要求を出さない。
- 判定は `Proceed / Hold` の二値ではなく `Proceed / Hold / Stop(held)` 三値で運用する。

## Stream E CE2 Open化準備アップデート（2026-05-09 / proposal-only, dependency-locked）

### Phase 1: Read（Draft理由・依存・不足証跡）
- 現在値: `Status=Draft` / `Dependency status=未確定` / `Expected verification level=docs-check`。
- Draft維持理由: CE0承認証跡とCE1 read-only確定証跡が CE2 本文内で「実値確認済み」として未充足。
- 不足証跡:
  - Approval Record 実値（`approved_at / approved_by / target / decision / evidence`）
  - CE0確定証跡への参照整合（承認日時・承認責務の一致）
  - CE1契約参照が「追加確定要求なし」であることの確認記録

### Phase 2: ADR CDC（low-risk 定義境界の固定）
#### Context
- CE2 は low-risk AI assist の Open 判定準備タスクであり、実装タスクではない。
- dependency-locked 前提のため、CE0/CE1 未確定項目は推測で補完しない。

#### Decision（low-risk boundary）
- low-risk の成立条件を次で固定する（すべて満たすまで Hold）:
  1. **proposal-only**: AI提案は `status=proposed` のみ。
  2. **human-final**: `accepted/rejected` は人間責務のみ。
  3. **no-auto**: `auto-apply/auto-confirm/auto-publish` 禁止。
  4. **fail-closed**: 監査4点欠損・`sourceBundleHash!==bundleHash` は `held`。
  5. **read-only dependency**: CE0/CE1 は参照限定、CE2側から実装前提を要求しない。
- 上記5条件のいずれかが未証跡なら Open 化しない。

#### Consequences
- Open化判定は厳格化されるが、依存推測・擬似確定・未承認Proceedを抑止できる。

### Phase 3: Plan（AC/DoD: proposal-only, mock-ready, hold条件）
#### AC（Open判定準備）
- [ ] AC-P1: proposal-only / human-final / no-auto / fail-closed の4条件が本文内で矛盾なく同時成立。
- [ ] AC-P2: mock利用境界（Yes/No/Conditional）が依存別に明示され、承認事実のmock代替を禁止。
- [ ] AC-P3: CE0/CE1依存に対し、未確定時は `Hold` を維持する条件が明示される。
- [ ] AC-P4: Approval Record 最小項目が空欄時は Proceed 不可である。

#### DoD（proposal品質）
- [ ] DoD-P1: Context/Decision/Consequences と AC の対応が1対1で追跡可能。
- [ ] DoD-P2: 実装指示・運用確定値追加・依存推測補完が本文に存在しない。
- [ ] DoD-P3: docs-checkコマンドが再実行可能で、single-file scope逸脱がない。
- [ ] DoD-P4: Proceed判定は依存未解決時に必ず `Hold` へ収束する。

#### Hold条件（固定）
- CE0/CE1の確定証跡が未提示。
- Approval Record 実値が未充足。
- self-correction が3回を超過。

### Phase 4: Execute（本Issueのみ更新）
- 本更新は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ変更。
- 実装・他Issue編集・依存値の推測補完は実施しない。

### Phase 5: Verify（依存矛盾なし / 推測実装なし / docs-check）
- V1 依存整合: CE0/CE1 は read-only dependency として記述され、確定を推測していない。
- V2 境界整合: proposal-only / no-auto / fail-closed / human-final が維持されている。
- V3 実施整合: docs-check 実行で文書品質を確認する。

### Phase 6: Proceed（依存未解決時Hold固定）
- 判定: **Hold 固定（Draft継続）**。
- 解除条件: CE0/CE1確定証跡 + Approval Record実値 + AC/DoD全充足を人間確認後に限る。

## Evidence matrix（Open判定の必要証跡）

| ID | 証跡項目 | 必須値 | 未充足時の判定 |
| --- | --- | --- | --- |
| E-01 | CE0承認証跡 | `approved_at/by/target/decision/evidence` 全項目 | Hold |
| E-02 | CE1 read-only契約確認 | 追加確定要求なしの記録 | Hold |
| E-03 | human-final確認 | `accepted/rejected` が人間責務で固定 | Stop(held) |
| E-04 | no-auto確認 | `auto-apply/auto-confirm/auto-publish` 禁止明記 | Stop(held) |
| E-05 | fail-closed確認 | 監査4点欠損/Hash不一致で `held` | Stop(held) |

## Approval Record（空欄禁止テンプレート）

| field | value | status |
| --- | --- | --- |
| approved_at | `TBD` | missing |
| approved_by | `TBD` | missing |
| target | `CE2 Open readiness` | preset |
| decision | `TBD (Proceed/Hold/Stop)` | missing |
| evidence | `TBD (link or doc-id)` | missing |

> `missing` が1つでもある場合、Proceedは禁止し `Hold` を維持する。

## Fixed Operation Contract（2026-05-01）

- proposal-only 原則を固定し、AIは候補提示（`status=proposed`）のみを実施する。
- `accepted / rejected` は人間責務。AIによる自動確定経路は作成しない。
- Auto操作（`auto-apply / auto-confirm / auto-publish`）を禁止する。
- 自動review昇格（AI/システム起因で `unreviewed -> human_reviewed` へ遷移）を禁止する。
- `reviewState` は `unreviewed | human_reviewed` の閉集合とし、AI提案は常に `unreviewed`。
- lifecycle は `proposed | accepted | rejected | held` の閉集合を維持する。
- 監査4点（`query / bundle / proposal / apply`）が欠損した場合は fail-closed。
- Verify判定は `sourceBundleHash === bundleHash` を必須条件として固定し、不一致時は fail-closed（`held`）とする。
- **合意未取得時は CE2実装へ進まない（Proceed禁止）。**

## Validation Plan

- 実行コマンド:
  - `git diff -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git status --short`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git diff --check -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
- 期待結果:
  - single-file scope で、Phase 1〜6、Evidence/Approval Record、Proceed/Hold/Stop条件が確認できる。
  - docs-check がゼロエラーで、proposal-only / no-auto / mock-isolated dependency の3条件に反証がない。
