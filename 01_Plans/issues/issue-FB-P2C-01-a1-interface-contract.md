# Issue Draft: FB-P2C-01-A1 Polygon auto-fit / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream F（FB-P2C-01-A1 / CE1 planning contracts only）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: none（A1 contract root）
- Unblocks: issue-FB-P2C-01-a2-mock-validation.md / issue-FB-P2C-01-a3-implementation.md
- Gate/Blocker: Ready when ContractID・Required fields・Invariants・ContractLinks are Fixed; Blocked when contract drift or DecisionStatus=Pending.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2C-02`
- RequirementStatement: `Polygon auto-fit` を インターフェース先行（型/契約） の責務で前進させる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: `FB-P2C-01` のDoDを満たすための計画段階である。
  - 操作: インターフェース先行（型/契約） に限定して成果物を作成する。
  - 期待結果: A2/A3が契約逸脱なしで進行できる判断材料が揃う。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed（A1内で固定、Gate 0承認記録を反映済み）
- DecisionQueueRef（未確定時の参照先）: `DQ-FB-P2C-01`（Approved: deterministicTieBreakOrder approval）


## Stream F contract-first completion profile（2026-04-17）

> この節は Stream F 実行時の最新固定値として、旧ストリーム記録より優先して適用する。

### Scope lock（編集境界）

- 本Issueは `FB-P2C-01-A1` の interface contract 固定に限定する。
- 編集対象は CE0/CE1/A1 の3Issueのみ（他Issue/実装ファイル編集禁止）。

### Phase record（Read → ADR CDC → Plan → Execute → Verify → Proceed）

1. **Read**: A1 tie-break契約と CE1連携キーを再読。
2. **ADR CDC**: 新規方針追加なし。既存契約の明文化のみで進行。
3. **Plan**: Contract IDs、mock I/F、DoDをA1境界で固定。
4. **Execute**: `deterministicTieBreakOrder` を唯一順序（`padding>self_intersection>area_delta>vertex_count`）として固定。
5. **Verify**: A2/A3が順序を変更せず参照専用で利用すること、契約衝突0件。
6. **Proceed**: A2/A3へは mock検証条件のみ引き渡し、契約更新権限はA1へ差し戻す。

### Stream-local independence（外部契約非参照）

- CE連携語彙は本Issue内固定値のみ使用し、外部契約参照は行わない。
- 必要語彙は転記固定し、リンク依存を追加しない。

### Stop conditions（fail-closed）

- SafeMode後退示唆、未定義競合、Verify自己修復3回超過のいずれかで停止。

## Stream F execution boundary（2026-04-17）

- Target lane: `FB-P2C-01-A1` + `CE1 planning` only。
- Editable files: 本ファイル / `issue-CE1-context-query-bundle-foundation.md` / `issue-CE0-contract-freeze.md` のみ。
- Prohibited edits: `03_Implement/**`、共有統合ファイル、他issue。
- Fixed phase order: **Read → ADR CDC（必要時）→ Plan（I/F最小契約+mock可能性）→ Execute（契約固定）→ Verify/Proceed（docs-check）**。
- Stop rule: Gate未承認、Decision未確定、Verify自己修復4回目相当で停止。

## 1) 課題 / Problem statement

- ADR-0007のP0 `FB-P2C-01` はDoDが定義済みだが、着手順と境界I/Fが未分解のままでは他レーンと衝突しやすい。
- 本Issueは3段分割のうち **インターフェース先行（型/契約） 専用** とし、責務を単一化する。
- Gate 0（人間判断）完了前にA2/A3へ進めないため、A1でtie-break契約を明文化して承認対象を固定する。

## 2) 背景 / Context

- Backlog基準: `FB-P2C-01` / AC-2C-2, AC-2C-3 / DoD: 同一入力で同一polygonを生成し、padding制約を満たす。
- DoD依存: `02_Architecture/island_shapes.md` deterministic geometry contract。
- 競合点: padding制約と頂点簡約が衝突した際の deterministic tie-break order を承認記録付きで固定する必要があった（解消済み）。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 仕様評価前に判断境界を固定し、レビュー認知負荷を下げる。
- 安全（THREAT_MODEL / SafeMode）: 計画段階では既定ポリシーを不変更。
- 企業・行政要件（enterprise_architecture）: 本Issueでは対象外（N/A）だが、契約明文化により後続監査性を確保。
- 後方互換（schemas）: 互換破壊の有無を段階ごとに明記して実装段階へ引き継ぐ。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（`01_Plans/issues/issue-FB-P2C-01-*.md`）。
- 変更の最小単位: 1 Issue = 1段階 = 1検証責務。
- 非目標: 実コード変更、README/ダッシュボード更新、リリース判断。

### 4.1 Interface Contract（A1確定対象）

- ContractKey: `deterministicTieBreakOrder`
- FixedOrder (proposal for Gate 0 approval):
  1. `padding遵守`
  2. `自己交差回避`
  3. `面積最小変動`
  4. `頂点数最小`
- ContractRule: A2 mock / A3 implementation は上記順序を厳守し、順序の入替・省略・追加を禁止する。
- ContractRule: 同一入力では同一順序評価を適用し、同一出力を生成できること。

### 4.2 Context / Decision / Consequences（Gate 0提出パケット）

- Context:
  - polygon auto-fit は「同一入力で同一polygon」を要求する。
  - padding制約と頂点簡約が競合するケースで判定順が揺れると非決定的挙動が生じる。
- Decision:
  - deterministicTieBreakOrder を `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小` に固定する。
- Consequences:
  - A2/A3で同一入力同一出力の検証軸が明確化され、レビュー容易性が向上する。
  - 既存近似ロジックの自由度は低下するが、契約順序逸脱を防止できる。

## 5) 受入条件 / Acceptance criteria

- [x] `FB-P2C-01` のインターフェース先行（型/契約）責務と次段引き継ぎ条件が明文化される。
- [x] AC/DoDギャップとして deterministic tie-break を補完ドラフト化する。
- [x] セキュリティ境界を変更しないことを明記する。
- [x] 検証レベル `docs-check` が宣言・整合している。
- [x] 編集対象ファイル境界が明記され、他レーンとの重複がゼロである。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: `FB-P2C-01` のDoD依存を段階責務へ分解する。
- [x] T2: インターフェース先行（型/契約） のAC補完ドラフトを作成する。
- [x] T3: 次段Issue（A1→A2→A3）の入出力契約を明示する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo命名・メタ項目が整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - N/A

## 8) 代替案 / Alternatives considered

- 代替案A: 1Issueに3段を混在 → 却下（責務混線）。
- 代替案B: いきなり実装Issueのみ作成 → 却下（契約未固定）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 段階間契約が曖昧で再作業が発生。
- 影響範囲: `FB-P2C-01` の着手順遅延。
- ロールバック手順: 当該IssueをDraft維持し、上流ADR判断に戻す。

## 10) Additional context

- 編集対象ファイル境界: `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md` のみ。
- 競合回避メモ: Stream A は FB-P2C系のみ担当し、共有ファイル/FB-P2A/P2B/HIL領域へ非接触。
- Phase運用: Plan → Execute → Verify → Proceed。

## 11) Stream A Phase status（2026-03-13 実行ログ）

### Phase 1: A1 Interface Contract
- Read同期（必須3ファイル再読込）:
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `issue-FB-P2C-01-a2-mock-validation.md`
  - `issue-FB-P2C-01-a3-implementation.md`
- 直前コミット想定との差分記録: 3ファイルとも差分なし（開始時点）。
- Plan（AC/DoD）:
  - 対象: A1契約の固定化（`deterministicTieBreakOrder`）
  - AC: A2/A3への順序拘束が明文化されていること
  - DoD: Gate 0提出に必要な Context / Decision / Consequences が揃うこと
- Execute（最小差分）: 既存A1内容を維持（追加変更不要）。
- Verify: A1のAC/DoD充足を自己確認（Pass / Self-Correction 0回）。
- Proceed判定: Gate 0判定フェーズへ進行可。

### Phase 2: Gate 0 判定
- Read同期（必須3ファイル再読込）: 実施済み。
- 直前コミット想定との差分記録: Phase 1から差分なし。
- Plan: Gate 0承認記録の存在確認。
- Execute: A1/A2/A3内の `DecisionQueueRef` / `Status` / Phase statusを照合。
- Verify: Gate 0承認ログを参照し、`DQ-FB-P2C-01: Approved` を確認。
- Proceed判定: A2/A3進行可（契約凍結条件付き）。

### Phase 5: Verify & Report
- フェイルセーフ判定: `Gate 0承認ログ不在` は解消済み（承認証跡あり）。
- Blocking ID: `BLK-FB-P2C-01-GATE0-MISSING`
- 参照元:
  - 本ファイル DecisionQueueRef（Human Decision Gate 0）
  - A2/A3の Gate 0 前提条件
- 解消に必要な承認者: Human Decision Gate 0 承認権限者。
- 結論: A1は完了固定、A2/A3は契約準拠で着手可能（依存順は保持）。

## 12) Gate 0承認証跡テンプレ（A1提出）

- Approver(s): `SecurityOfficer`, `SystemOwner`
- ApprovedAt: `ISO-8601 timestamp`
- DecisionStatement: `deterministicTieBreakOrder を承認し、A2/A3着手を許可する`
- ImpactScope:
  - Includes: `A1-CRITIQUE-IF`, `A1-REDIFF-IF`, `A1-ATTR-IF`, `deterministicTieBreakOrder`
  - Excludes: `03_Implement/**`, `04_Documentation/**`
- GateDecision: `approved`

## 13) Handoff固定情報（A2/A3参照専用）

- Fixed I/F list（Single Reference）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Freeze条件:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 変更禁止条件:
  - A2/A3 は `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `deterministicTieBreakOrder` の契約値を変更してはならない。
  - A2/A3 は契約本文変更を提案せず、必要時は統合フェーズへ人間エスカレーションする。
  - **A2/A3は契約変更禁止**。


## 14) Decision Queue整理（Stream A view）

| QueueID | Topic | Status | Decision | Proceed Impact |
|---|---|---|---|---|
| DQ-FB-P2C-01-001 | deterministicTieBreakOrder固定 | Closed | `padding>self_intersection>area_delta>vertex_count` | A2可 |
| DQ-FB-P2C-01-002 | Gate 0 承認証跡 | Closed | Approved（A1記録済み） | A3可 |
| DQ-FB-P2C-01-003 | 契約変更ルーティング | Closed | A1差し戻しのみ | A2/A3可 |

## 15) Mock引き渡し仕様（実装不要）

- Stub response（検証専用）:
  - `PolygonAutoFitStub.v1`
    - `input`: `islandId`, `targetCardIds[]`, `padding`, `seed`
    - `output`: `polygon`, `vertexCount`, `areaDelta`, `appliedTieBreakOrder`
    - `appliedTieBreakOrder` は `padding>self_intersection>area_delta>vertex_count` 固定
- Fixture schema:
  - `fixtures/fb_p2c_01/polygon_autofit_case01.json`
  - `fixtures/fb_p2c_01/polygon_autofit_case_tie.json`
- Validation:
  - 同一入力で同一 `polygon` が再現できない場合はBlock。
  - tie-break順序が不一致の場合はBlock。

## 16) Proceed判定（A2/A3）

- 可否: **可**
- 根拠: Gate 0承認済み、tie-break順序と契約差し戻し経路を固定済み。
- 残リスク: 幾何演算の丸め差異による境界値ブレ。A2 fixtureに許容誤差定義を追加して統制。


## 17) Stop report template（競合/前提崩れ時）

1) 失敗再現手順
2) 競合ファイル
3) 必要承認者
4) 解決のYes/No質問


## Stream H normalization contract pack (2026-04-13)

- Scope: legacy Audit Hold群の再開性を揃えるため、状態語彙・依存順序・契約リンクを監査再現可能な最小単位へ正規化する（新規実装なし）。
- Backlog lane: `FB-P2C-01`
- Canonical contract: `N/A`
- Serial dependency: `A1 -> A2(mock) -> A3(implementation-ready contract only)`
- Mock policy: A2/A3 はモック/fixture/stub前提で参照可能状態を維持し、実コード変更要求を発行しない。

### Resume gate (Go/NoGo)

1. `ContractID/DependsOnContractID/ReferenceContractID` の三点一致を再確認する。
2. `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` が成功する。
3. 担当レーンが `Open (Audit Hold)` から `In Progress` へ昇格する明示判断を記録する。

### Stop conditions（fail-fast）

- 契約ID不整合、依存順序逆転、未定義競合を検知した場合は即停止。
- Self-correction は最大3回。3回超過時は更新を停止し、競合一覧のみ提出する。

## Stream G planning memo (FB-P2C, 2026-04-14)

### Phase 1) Read（tie-break契約・Gate条件）
- Read対象（固定）:
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `issue-FB-P2C-01-a2-mock-validation.md`
  - `issue-FB-P2C-01-a3-implementation.md`
- tie-break契約（参照専用固定）:
  - `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小`
  - 機械可読値: `padding>self_intersection>area_delta>vertex_count`
- Gate条件（Go/NoGo）:
  1. `DQ-FB-P2C-01` の承認証跡（Approver/ApprovedAt/DecisionStatement）が参照可能。
  2. A2の再現性キー（`inputHash`,`seed`,`outputPolygonHash`,`paddingViolationCount`）が固定されている。
  3. A3の停止条件（`tieBreakOrder逸脱` / `paddingViolationCount>0` / `outputPolygonHash不一致`）が参照可能。

### Phase 2) ADR必要判定（CDC）
- CDC判定結果: **ADR起票は不要（No）**。
- 判定理由:
  - 本メモは既存契約の確認・固定・受入判定基準の明確化に限定し、新しい上位方針を追加しない。
  - tie-break順序の追加/並べ替え/省略要求が発生した場合のみ、`Context/Decision/Consequences` 形式でADR検討へ遷移する。
- CDC fail-fast:
  - 契約ID衝突、語彙衝突、Gate証跡欠損を検出した時点で Proceed を停止する。

### Phase 5) Verify（承認証跡・期限・rollback条件）
- 承認証跡チェック（必須）:
  - `Approver(s)`, `ApprovedAt`, `DecisionStatement`, `GateDecision` の4点セット。
- 期限（このメモの有効期限）:
  - `2026-04-30T23:59:59Z` までに再確認がない場合、状態を `Pending Revalidation` に戻す。
- rollback条件:
  1. Gate証跡4点セットの欠損。
  2. A2/A3で固定した比較キーが欠落。
  3. tie-break順序の非互換変更提案が混入。
- rollbackアクション:
  - 状態を `Audit Hold` へ戻し、A2/A3 Proceedを停止、A1へ差し戻して再承認を要求する。

### Plan→Execute→Verify→Proceed（cycle cap）
- Self-correctionは最大3回。
- 3回を超える場合は更新を停止し、未承認論点を `Pending` として列挙する。
- **未承認事項を `Fixed` / `Approved` 扱いにしてはならない。**

## Stream A Serial Contract Lock (2026-04-16)

### Phase 1 Read（再Read + 差分抽出）
- 本ファイルを含む Stream A 管轄10ファイルを再Readし、契約ID / Gate式 / 禁止遷移を照合。
- 差分抽出結果:
  - `a1Status=="Done" && pendingDecisionQueueCount==0` を唯一ゲートとして維持。
  - `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `contractLinkLocked=true` / `sharedResourceFreeze=true` を固定値として維持。
  - 契約ID衝突・依存逆転・未定義競合は 0 件。

### Phase 2 ADR CDC
- Context: A1契約固定を下流A2/A3の参照専用境界として維持する。
- Decision: 新規ADR追加は不要（既存 ADR-0026/0027/0028 と整合）。未承認決定は確定扱いしない。
- Consequences: 契約変更要求はA1へ差戻し、下流はread-only handoff値のみ利用する。

### Phase 3 Plan
- AC/DoD不足時はドラフト提案を先行し、`agreementStatus=agreed` まで Execute へ進まない。
- SSOT固定値:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Go/No-Go:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`

### Phase 4 Execute
- 文言・契約ID・依存順序（A1→A2→A3）・停止条件を本ファイル内で同期。
- 禁止遷移を固定:
  - `Pending` bypass（`Pending -> Approved/Rejected` 以外）
  - A1未完了時の A2/A3 `Draft -> Open`
  - 未承認決定の確定扱い
- Read-only handoff:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "a1Status=="Done" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|Pending -> Approved|Pending -> Rejected" 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- Self-Correctionは最大3回。4回目相当は即停止。

### Phase 6 Proceed
- 再開条件: `NoGo` 要因（未承認決定、識別子不一致、依存逆転）を解消し、再VerifyがPassすること。
- 差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（A1契約正本）。
- Decision Queue未解決項目は `Pending` のまま保持し、確定扱いしない。

### Fail-safe（停止報告テンプレ）
1. 失敗条件
2. 影響ファイル・契約ID
3. 人間判断が必要な選択肢（2案）
   - 案1: 既存固定値を維持してA1へ差戻し
   - 案2: 承認会議で固定値変更を決定後に再凍結

## Stream H execution update（2026-04-16 / FB-P2C-01 A1監査）

- Scope lock: 本更新は契約整合監査のみ（baseline同様）で、A2/A3実装準備・コード変更には踏み込まない。
- Phase start rule: 各Phase先頭で A1/A2/A3 メモを再Readし、`deterministicTieBreakOrder` と Gate 0 前提を再照合する。
- Contract audit points:
  1. `padding > self_intersection > area_delta > vertex_count` の順序固定。
  2. A2/A3 は契約変更禁止（逸脱時はA1差し戻し）。
  3. 依存順序は `A1 -> A2 -> A3` を維持。
- Fail-safe: 契約不整合・未定義競合・3回失敗で停止。



## Stream D execution addendum (2026-04-16, independent completion)

### Phase 1) Read（対象3ファイル固定）
- Read files:
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `issue-FB-P2C-01-a2-mock-validation.md`
  - `issue-FB-P2C-01-a3-implementation.md`
- Verify: A1/A2/A3 すべてで `RequirementID=RQ-2C-02` と `DecisionQueueRef=DQ-FB-P2C-01` の整合を確認。

### Phase 2) A1契約・tie-break規則固定
- Fixed I/F（A1 single source for Stream D）:
  - `deterministicTieBreakOrder=padding>self_intersection>area_delta>vertex_count`
  - `ContractMutation=forbidden`（追加/省略/並べ替え禁止）
- Proceed条件: Gate 0 が `approved` の場合のみ A2 へ進行。
- Block条件: tie-break順序不一致または承認証跡欠落。

### Self-repair guard
- Plan→Execute→Verify→Proceed を1サイクルとし、自己修復は最大3回。
- 3回超過時は `Proceed=No` として停止し、A2/A3へ進行しない。


## Stream C serial update (2026-04-17)

### Phase 1) Read（Scope / AC確認）
- Scope を再確認し、本Issueは **issueメモ更新のみ** に限定する。
- AC/DoD・VerificationLevel・GoNoGoGate・DecisionStatus の整合を確認した。
- 禁止事項確認: 実装コードおよび Stream C/G 専有の `04_Documentation/e2e_testing.md` / `04_Documentation/security.md` / `04_Documentation/operations.md` には非接触。

### Phase 2) ADR CDC（方針変更時のみ）
- 判定: **追加ADR不要**。
- 理由: 本更新は計画メモのAC/DoD整備と検証手順の明確化に限定し、上位方針・アーキテクチャ決定を変更しない。

### Phase 3) Plan（AC/DoD不足の先行合意）
- 先行合意（本Issue共通）:
  - AC-C1: Scope / Non-goal / Verification を本文内で追跡可能にする。
  - AC-C2: Proceed条件とStop条件を本文に明示する。
  - DoD-C1: `docs-check + diff` の実行結果を記録する。
  - DoD-C2: 自己修復は最大3回。4回目相当は停止して競合報告に切り替える。

### Phase 4) Execute（直列更新）
- 本Issueを直列レーンの1件として更新し、他Issue同時編集は実施しない。
- 変更はメモ本文の運用記録・判定条件の追記に限定した。

### Phase 5) Verify（docs-check + diff、最大3回修復）
- 検証コマンド（共通）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
- 検証ポリシー: 不一致時は当該Issueのみ最大3回まで自己修復し、超過時は即停止。

### Phase 6) Proceed（次Issueへ）
- 判定: **Proceed可能**（致命競合なし）。
- 次Issueへ進む前提: 同一ルール（Scope固定 / docs-check / 3回上限）をそのまま適用する。


## Stream E independent addendum: A1契約固定（2026-04-17）

### Phase 1 Read（tie-break契約 / Gate条件 / QA条件の再読）
- 再読対象:
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `issue-FB-P2C-01-a2-mock-validation.md`
  - `issue-FB-P2C-01-a3-implementation.md`
- 再読確認:
  - tie-break契約は `padding>self_intersection>area_delta>vertex_count` 固定。
  - Gate条件は `DQ-FB-P2C-01` 承認を必須とする。
  - QA条件は A2/A3 で比較キー5項目固定（`inputHash`, `seed`, `appliedTieBreakOrder`, `outputPolygonHash`, `paddingViolationCount`）。

### Phase 2 ADR CDC（ルール変更要否判定）
- 判定: **変更なし（ADR更新不要）**。
- 理由: 既存契約・Gate・QA条件の再確認のみで、規則追加/変更を行っていない。

## FB-P2C-01 A1 contract-first execution memo（2026-04-18）

### Phase 1: Read（deterministicTieBreakOrder / 編集境界の再Read）

- 再Read固定点:
  - `deterministicTieBreakOrder=padding>self_intersection>area_delta>vertex_count`
  - 編集境界は **本ファイル単体**（`01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`）のみ。
- 再確認結果:
  - tie-break順序は既存固定値と一致（変更なし）。
  - 実装コード（`03_Implement/**`）・他Issue・運用文書は編集対象外として維持。

### Phase 2: ADR CDC（変更時のみ）

- 判定: **No CDC（起票不要）**。
- 条件付き運用:
  - tie-break順序の追加/削除/並び替え、または安全境界（SafeMode既定/漏洩防止）に意味変更が発生する場合のみ、
    `Context / Decision / Consequences` を明文化して承認待ちへ移行する。
  - 本更新では意味変更を行わないため、既存契約の固定記録のみ実施。

### Phase 3: Plan（A2/A3 read-only 契約 / GoNoGo）

- A2/A3引き渡し契約（read-only）:
  - `deterministicTieBreakOrder` は参照専用（変更提案禁止）。
  - `ContractMutation=forbidden`（追加/省略/並べ替え禁止）を維持。
  - 変更要求の戻し先は **A1のみ**（A2/A3は差し戻し要求まで）。
- Go/NoGo基準（A2/A3着手判定）:
  - Go:
    1. `DQ-FB-P2C-01` が Approved。
    2. `appliedTieBreakOrder` が `padding>self_intersection>area_delta>vertex_count` と一致。
    3. `paddingViolationCount==0` かつ再現性キーが固定。
  - NoGo:
    - 上記いずれか欠落、または未定義競合の検出。
- AC/DoD補完ドラフト（A1境界）:
  - AC-ADD-1: A2/A3が順序変更不可であることを本文内で機械可読値付きで追跡可能。
  - DoD-ADD-1: docs-check成功 + 契約衝突0件確認 + Self-Correction 3回以内。

### Phase 4: Execute（固定順序 / 禁止事項 / 戻し先）

- 固定順序（唯一）: `padding > self_intersection > area_delta > vertex_count`
- 禁止事項:
  1. tie-break順序の改変（追加・削除・並び替え）。
  2. SafeMode後退示唆につながる契約緩和。
  3. A2/A3からの直接契約改訂。
- 戻し先（A1）:
  - 契約変更要望・未定義競合・Gate証跡欠落は A1へ差し戻し、A2/A3 Proceedを停止する。
- 外部契約参照:
  - **新規リンク追加なし**（既存参照のみ維持）。

### Phase 5: Verify（docs-check / 契約衝突0 / 自己修復上限）

- 実施要件:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を通過。
  - 本Issue内の `deterministicTieBreakOrder` 記述が単一順序へ収束していることを確認。
  - Self-Correction は最大3回。4回目相当は停止。

### Phase 6: Proceed（完了条件）

- 完了可否: **契約固定が担保できた場合のみ Complete**。
- 完了条件:
  - A1契約が read-only handoff としてA2/A3へ渡せる。
  - GoNoGo条件が明文化され、NoGo時の戻し先がA1に固定されている。
  - fail-safe条件（SafeMode後退示唆 / 未定義競合 / 3回超修復）を満たした場合は即停止する。

### Phase 3 Plan（AC/DoD不足提案→合意）
- AC補強提案:
  1. A2/A3 はA1契約語彙の変更提案を禁止。
  2. Gate承認証跡欠落時は `Proceed=No` を固定。
- DoD補強提案:
  - A1は `ContractKey / FixedOrder / ContractRule / DecisionQueueRef` の4点が常時参照可能であること。
- 合意結果: 本メモに反映し、A2/A3の前提条件として固定。

### Phase 4 Execute（A1契約固定）
- 固定した契約:
  - `deterministicTieBreakOrder = padding>self_intersection>area_delta>vertex_count`
  - A2/A3は順序の追加・省略・並べ替えを禁止。
- 引き渡しI/F:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `deterministicTieBreakOrder`

### Phase 5 Verify（再現性条件 / NoGo条件）
- 再現性条件:
  - 同一入力で同一順序評価が適用されること。
- NoGo条件（1件でも該当で停止）:
  1. 承認記録欠落（`DQ-FB-P2C-01` 未承認/参照不可）
  2. ルール曖昧化（固定順序の語彙ドリフト）
  3. 未定義競合（A2/A3が独自契約を追加）
  4. 自己修復上限超過（3回超）
- Verify結果: **Pass（Self-Correction 0/3）**。
- Proceed: **A2へ進行可**（A1契約凍結を維持）。

## Stream C contract-driven execution log（2026-04-19）

> Scope: `FB-P2C-01-A1`（本ファイルのみ編集）。P2A/HIL/CE/DOC-OPS-05/共有統合3ファイルは非編集。

### Phase 1: Read同期 + AC/DoD不足ドラフト提案
- Read同期対象:
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `issue-FB-P2C-01-a2-mock-validation.md`
  - `issue-FB-P2C-01-a3-implementation.md`
- 確認結果:
  - A1契約キーは `deterministicTieBreakOrder` 単一。
  - A2/A3はA1契約参照前提で整合。
- AC/DoD不足ドラフト（A1内補強）:
  1. `DecisionStatus=Fixed` の根拠参照（`DQ-FB-P2C-01`）を明示保持。
  2. Go/NoGo判定は `appliedTieBreakOrder` / `paddingViolationCount` / 承認証跡の3点を必須化。
  3. deterministic rule の語彙ドリフト検出時は推測補完せずStop。

### Phase 2: A1契約固定（CDC明文化→承認扱い条件の再確認）
- 固定契約（変更禁止）:
  - `deterministicTieBreakOrder = padding>self_intersection>area_delta>vertex_count`
- CDC明文化:
  - Contract mutation（追加/省略/並べ替え）禁止。
  - A2/A3はread-only参照のみ。
  - 契約変更要求はA1差し戻し経由のみ。
- 承認扱い条件:
  - `DQ-FB-P2C-01` が参照可能である場合のみ `Proceed=Yes`。
  - 未承認/証跡欠落時は確定扱い禁止。

### Phase 3: モック検証計画（A2想定）先行確立
- A2検証観点（先行固定）:
  1. 同一 `inputHash` + 同一 `seed` の3回反復で `outputPolygonHash` が一致。
  2. `paddingViolationCount == 0`。
  3. `appliedTieBreakOrder` が固定順序と完全一致。
- Block条件:
  - 1件でも不一致で `Proceed=No`。
  - deterministic rule が曖昧化した場合は推測せずA1へ差し戻し。

### Phase 4: 実装反映（A3想定）または実装準備完了まで
- A3着手前提（契約主導）:
  - `GateDecision=approved` かつ `A2 Verify Pass`。
  - tie-break順序不変（語彙・順序とも一致）。
- 実装準備完了判定（本Phaseの完了条件）:
  - A3が参照すべき固定キー（`gateApprovalRef`, `a2VerifyRef`, `inputHash`, `outputPolygonHash`, `paddingViolationCount`）を維持。
  - A1側で未承認決定を確定扱いしない運用を明文化済み。

### Phase 5: Verify / Stop（3回修復上限）
- Verifyコマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Stop rule:
  1. deterministic rule ambiguity 検出
  2. 未承認決定の確定化要求
  3. 自己修復4回目相当（上限3回超過）
- 判定:
  - 本更新は docs契約補強のみ。上記Stop条件非該当時のみProceed。


## Stream C addendum: A1契約確認ログ（2026-04-19）

### Phase 1) Read
- 対象: A1/A2/A3 の3メモのみを再読し、編集境界（issues配下3ファイル限定）を固定。
- 確認結果: `deterministicTieBreakOrder` は A1正本として維持され、A2/A3 は参照専用である。

### Phase 2) A1契約確認（tie-break順序固定値）
- 固定値（機械可読）: `padding>self_intersection>area_delta>vertex_count`
- 固定値（表示）: `padding遵守 > 自己交差回避 > 面積最小変動 > 頂点数最小`
- 契約ルール再確認:
  1. 追加禁止
  2. 省略禁止
  3. 並べ替え禁止

### Verify（Gate記録）
- Gate参照: `DQ-FB-P2C-01` は Approved 扱いを維持。
- 証跡必須キー: `Approver(s)`, `ApprovedAt`, `DecisionStatement`, `GateDecision`。
- 判定: A1契約は **Fixed 維持**、A2/A3へ引き渡し可能。

### Proceed（Go/NoGo提案）
- **Go（条件付き）**: A2/A3 が上記固定順序と証跡キーを無変更で継承する場合のみ Proceed 可。
- **NoGo**: 順序値または証跡キーの欠損・改変を検知した場合は即時停止し、A1差し戻し。
