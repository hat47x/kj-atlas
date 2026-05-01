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

## Mandatory Workflow（Plan → Read-Sync → Execute → Verify→ Proceed）

1. **Plan**: CE2のAC/DoD・非機能制約・停止条件を先に固定する。
2. **Read-Sync**: `ADR-0028` / `ADR-0001` / `schemas.md` の語彙と契約を照合し、矛盾を解消する。
3. **Execute**: 本Issue内で Phase 1〜5 を更新し、CE2判断材料のみを具体化する（実装禁止）。
4. **Verify（最大3回自動修復）**:
   - V1: single-file scope逸脱チェック
   - V2: proposal-only / human decision / fail-closed 文言チェック
   - V3: Phase欠落・表の不整合チェック
   - 3回以内に修復不能な場合は `status=held` で停止。
5. **Proceed**: 人間承認ログ確認後のみ次Phaseへ引き継ぐ。

## Phase 1: 受入条件・非機能制約（safeMode含む）

### 受入条件（CE2計画の成立条件）
- proposal-only のまま AI補助案を作成し、`accepted/rejected` は人間判断として固定されている。
- CE2計画文に「実装禁止」「自動確定禁止」「未承認時は held 継続」が併記されている。
- safeMode既定ON、未レビュー保護、監査欠損時fail-closed の3点が後退しない。

### 非機能制約（NFR）
- **Security**: 未レビュー提案の外部共有・自動公開を許可しない。
- **Auditability**: `query/bundle/proposal/apply` の4点監査を欠損なく追跡可能にする。
- **Traceability**: 判定根拠を Phaseごとに再読可能（誰が何を承認したか復元可能）。
- **Reversibility**: 合意前は常に `held` に戻せる（不可逆操作禁止）。

## Phase 2: 依存I/Fの列挙と mock方針

### 依存I/F（実装せず、契約のみ列挙）
- Decision Input I/F: 人間レビュー入力（`accepted/rejected/held` の判定記録）。
- Proposal I/F: AI候補出力（`status=proposed`, `reviewState=unreviewed`）。
- Audit I/F: 監査4点の存在検査（欠損時 fail-closed）。
- Policy I/F: safeMode と No-Go（auto-* 禁止）制約の適用確認。

### mock方針（計画フェーズ限定）
- **Mock-Decision-Log**: 承認者・日時・対象をダミー値で記録し、ログ形式のみ検証。
- **Mock-Audit-Matrix**: 4点監査の有無を `present/missing` で評価。
- **Mock-Policy-Gate**: auto-* 要素が混入した場合に `blocked` を返す判定表。
- 実データ接続・実運用ログ接続は CE2範囲外（次Phaseへ持ち越し）。

## Phase 3: リスク台帳（誤提案 / 漏洩 / 監査不能）

| Risk ID | リスク | 兆候 | 影響 | 予防策 | 検知時アクション |
| --- | --- | --- | --- | --- | --- |
| R-CE2-01 | 誤提案の採択圧力 | AI提案が確定語で記述される | 人間判断の形骸化 | proposal-only表現を固定、確定語禁止 | `held` へ戻し文言を修正 |
| R-CE2-02 | 未レビュー情報の漏洩 | share/export相当の導線が追加される | 安全境界逸脱 | safeMode既定ONと未レビュー保護を明記 | fail-closed、Proceed停止 |
| R-CE2-03 | 監査不能 | 監査4点のいずれか欠損 | 後追い検証不能 | 4点必須チェックを運用前提化 | 欠損補完まで `held` 継続 |

## Phase 4: Draft→Open 移行条件

DraftからOpenへ移行できるのは、以下を **全件** 満たした場合のみ。

- CD&C（Context / Decision / Consequences）が本Issue内で明文化されている。
- 依存I/Fと mock方針が記録され、実装作業へ越境していない。
- リスク台帳（R-CE2-01〜03）に予防策と停止条件が紐付いている。
- 人間承認ログの最小項目（日時・承認者・対象・判断）が記録されている。
- 「未承認なら held 継続」の fail-safe が残っている。

## Phase 5: AC/DoD 判定と実装タスク引継ぎ文

### AC（Acceptance Criteria）
- [ ] CE2計画が proposal-only の範囲に限定されている。
- [ ] Phase 1〜4（受入/NFR・I/F+mock・リスク台帳・移行条件）が記述済み。
- [ ] safeMode既定ON、未レビュー保護、監査欠損fail-closed が後退していない。
- [ ] 承認未取得時に Proceed しない条件が明示されている。

### DoD（Definition of Done）
- [ ] single-file scope を維持し、他ストリーム領域を編集していない。
- [ ] CE2判断材料が再読可能（文言・表・条件が矛盾しない）。
- [ ] Verify 3段（scope / contract / phase integrity）を通過している。
- [ ] 次工程へ渡す「実装禁止解除条件」が1文で明示されている。

### 実装タスクへの引継ぎ文（承認後に使用）
> CE2は proposal-only 契約・safeMode境界・監査4点必須を満たした計画として承認済み。実装フェーズは本契約を変更せず、`accepted/rejected` 人間責務と fail-closed を維持すること。

## ADR Rule（CE2でADR草案を扱う場合）

- ADR草案は **Context / Decision / Consequences** を最小3節で記載する。
- 承認獲得までは ADR状態を Draft のまま維持し、実装Phaseへ遷移しない。
- CE2で新規ADR草案を起票する場合、対象は `01_Plans/adr/` 配下に限定し、本Issueから相互参照を追加する。

## Fail-safe Stop Conditions（即停止）

- 合意未取得のまま次工程（実装・確定運用）へ進む要求。
- Self-Correction `4/3` 相当（最大3回超過）。
- safeMode既定ONや未レビュー保護など安全境界の後退要求。
- 未定義競合（契約衝突・語彙衝突・責務分離崩壊）の検知。

## Validation Plan

- 実行コマンド:
  - `git diff -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git status --short`
- 期待結果:
  - single-file scope で、Phase 1〜5、I/Fとmock方針、リスク台帳、Draft→Open条件、Proceed条件（承認時のみ）が確認できる。
- 未実施時の理由・代替検証:
  - なし（docs-checkのみ）。
