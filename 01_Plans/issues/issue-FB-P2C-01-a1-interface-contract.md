# Issue Draft: FB-P2C-01-A1 Polygon auto-fit / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream H（audit normalization only）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

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
