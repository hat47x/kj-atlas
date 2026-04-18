# Issue: HIL-RS-02 A3 strict-mode例外運用 文書同期（Stream F）

- Type: Documentation Sync
- Status: Draft
- Lifecycle: DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed -> StoppedForClarification
- Priority: P1
- Owner: Stream F
- Source Issue: TBD
- Expected verification level: `docs-check`
- Scope:
  - `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
  - `02_Architecture/strict_mode_exception_approval_flow.md`
  - `04_Documentation/operations.md`
  - `04_Documentation/security.md`
  - `04_Documentation/security_operational_guidelines.md`
  - `04_Documentation/e2e_testing.md`
- Out of scope:
  - `01_Plans/project-progress-dashboard.md`
  - `01_Plans/issues/README.md`
  - `03_Implement/*`
- Related ADR/Spec:
  - `ADR-0019`
  - `ADR-0027`
  - `02_Architecture/strict_mode_exception_approval_flow.md`

## 1) Context

strict mode 例外運用（AUTH-OPS-03）は D1〜D4 固定値で運用するが、文書間で状態語彙・導線・責務分離のドリフトが混在すると運用停止条件が曖昧化する。

特に A3 同期では次を同時に満たす必要がある。

1. 用語一致（Security Officer / System Owner / Platform Operator）
2. 責務分離一致（2者承認と実行責務分離）
3. 固定値一致（D1〜D4）
4. 導線一致（architecture -> security -> guidelines -> e2e、operationsはrunbook整合）

## 2) Decision

Stream F は docs-only でスコープ内6ファイルのみ更新し、strict mode 例外運用の canonical 表現を次で固定する。

- 状態語彙: `DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed` と `StoppedForClarification`
- D1〜D4 固定値:
  - D1: Security Officer先行、承認TTL=4h
  - D2: tenant単位、最大2h
  - D3: 2者共同判定、代理承認なし
  - D4: 変更台帳+監査ID相互参照、48hレビュー、15m一次/60m二次エスカレーション
- フェイルセーフ: D1〜D4 の不整合を検知した時点で即停止（TODO化しない）

## 3) Consequences

- 文書横断ドリフト（用語/責務/固定値/導線）の再発検知が容易になる。
- `operations.md` は原則参照先だが、canonical語彙・固定値ドリフト是正が必要な場合のみスコープ内で最小修正できる。
- Verify 失敗時は自己修復を最大3回までに制限し、4回目相当は停止して差分を記録する。

## 4) Phase Plan（固定）

### Phase 1 Read

- `strict_mode_exception_approval_flow.md` を正本として再読。
- `security.md` / `security_operational_guidelines.md` / `e2e_testing.md` の語彙・固定値・導線を棚卸し。

### Phase 2 ADR必要時のCDC明文化

- ADR変更が必要な場合のみ Context / Decision / Consequences を追記して承認待ちへ遷移。
- ADR不要の場合は issue 側 CDC を正本として作業継続。

### Phase 3 Plan（AC/DoD）

- AC-1: 役割語彙が3文書+アーキ文書で一致。
- AC-2: 状態語彙が canonical に一致。
- AC-3: D1〜D4 固定値が一致。
- AC-4: 導線（architecture -> security -> guidelines -> e2e）が明示され、operations runbookが同値語彙で整合。
- AC-5: dashboard / issues README / 実装コードを編集しない（`operations.md` はスコープ内のため必要最小限の同期修正のみ許可）。
- AC-6: docs-check を再現可能コマンドで記録。

DoD:
- 上記 AC を全て満たし、`git diff --check` が成功。
- D1〜D4 不整合ゼロを証跡付きで確認。

### Phase 4 Execute

- 許可ファイルのみ更新。
- alias語彙（Requested / ExceptionActive など）を canonical へ収束。
- 参照リンクと停止条件の明文化を同期。

### Phase 5 Verify / Proceed

実行コマンド:

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
rg -n "Security Officer|System Owner|Platform Operator|DraftRequest|ApprovalPending|Approved|ActiveException|RollbackPending|Closed|StoppedForClarification|D1|D2|D3|D4|4h|2h|48h|15m|60m" \
  02_Architecture/strict_mode_exception_approval_flow.md \
  04_Documentation/operations.md \
  04_Documentation/security.md \
  04_Documentation/security_operational_guidelines.md \
  04_Documentation/e2e_testing.md
rg -n "operations\.md|security\.md|security_operational_guidelines\.md|e2e_testing\.md" \
  02_Architecture/strict_mode_exception_approval_flow.md \
  04_Documentation/operations.md \
  04_Documentation/security.md \
  04_Documentation/security_operational_guidelines.md \
  04_Documentation/e2e_testing.md
git diff --check
```

Proceed 条件:

- すべての Verify コマンドが成功。
- D1〜D4 不整合が0件。
- 編集禁止ファイルへの差分が0件。

## 5) Fail-safe（即停止条件）

1. D1〜D4 固定値に不整合が出た場合。
2. `StoppedForClarification` を回避する運用文言が混入した場合。
3. SafeMode既定ON / share-export漏えい防止の後退表現が混入した場合。
4. 許可外ファイル編集が必要になった場合。

停止時は以下を記録する。

- 不整合箇所（ファイル+行）
- 発生フェーズ
- 修復案（最小差分）
- 再開条件

## Stream C Normalization Update (2026-04-12)

### Scope Alignment（計画整流化限定）
- 本issueは HIL-RS 計画系整流化のA3メモとして扱い、実装作業を開始条件にしない。
- Stream Cが固定する対象は次の2点のみ。
  1. ゲート条件の明文化
  2. 差戻し導線（契約不一致はA1へ戻す）の固定

### Phase Execution Record（1〜6）
1. **Phase 1 Read**: 対象3ファイルを再読し、相互参照の整合を確認。
2. **Phase 2 ADR明文化（CDC）**: 既存CDCを優先し、ADR改定不要を確認。
3. **Phase 3 Plan**: AC/DoD不足に `A1 external-wait禁止` と `rollback route固定` を追加。
4. **Phase 4 Execute**: 状態遷移契約を `A1 Done && pendingDecisionQueueCount==0` に統一。
5. **Phase 5 Verify**: docs-check + 差分検証を実施（失敗時は3回修復まで）。
6. **Phase 6 Proceed**: 4回目相当失敗または曖昧点残存時は質問化して停止。

### State Transition Contract（A3側の取り扱い）
- A3は `A1 Done && pendingDecisionQueueCount==0` のときのみ Open/Proceed 可。
- NoGo時は `Draft/Open(hold)` を維持し、契約差分をA1へ差戻す。

### Failure-stop Rule（3回超停止）
- 修復は最大3回。
- 3回超過時は停止し、未解決点を質問として明示する。


## Stream G A3 Execution Log (2026-04-16)

- Phase 1 Read: D1〜D4 / 役割語彙 / 状態語彙 / 導線（architecture -> security -> guidelines -> e2e）を再確認。
- Phase 2 ADR CDC: 既存決定（AUTH-OPS-03固定値）で充足し、ADR更新不要を確認。
- Phase 3 Plan: AC/DoD を再固定し、`operations.md` は原則参照・必要時のみ最小修正で同期する方針を明示。
- Phase 4 Execute: `security.md` / `security_operational_guidelines.md` / `e2e_testing.md` の canonical 同期を実施。
- Phase 5 Verify: docs-check + `rg` + `git diff --check` を実行し、D1〜D4不整合0件を確認。
- Phase 6 Proceed: fail-safe条件（D1〜D4不整合 / safeMode後退 / 許可外編集 / 3回修復超過）が非成立で継続可能。

## Stream B HIL Umbrella Planning Update (2026-04-16)

### Phase 1 Read（対象3ファイル再Read）
- 各Phase開始時に次の3ファイルを再Readし、A3メモの整合前提を再確認。
  1. `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  2. `issue-HIL-RS-02-next-phase-delivery-plan.md`
  3. `issue-HIL-RS-02-A3-operations-documentation-sync.md`
- A3は umbrella planning 配下で `A1 Done && pendingDecisionQueueCount==0` が成立するまで `Draft/Open(hold)` を維持。

### Phase 2 ADR CDC（先行明文化）
- Context: A3は文書同期レーンだが、Stream Bでは許可3ファイル以外を編集しない。
- Decision: A3のProceedは上位2ファイルと同じGo条件（A1完了・Pending=0・固定値一致）を満たす場合のみ。
- Consequences: 条件未達・固定値不一致・未承認確定化はA3単独で解決せずDecision Queueへ返却し、A1契約正本へ差し戻す。

### Phase 3 Plan
- AC/DoD不足時はドラフト提案を記録し、合意後にのみ Execute へ進む。
- A3 planning AC: `3-file reread`, `CDC先行`, `No unauthorized file edit`, `Self-repair<=3`。

### Phase 4 Execute
- 本issueに A3のNoGo条件（`A1!=Done || pendingDecisionQueueCount>0`）と差戻し導線を固定。
- `02_Architecture/*` と `04_Documentation/*` は参照のみとし、本更新では未編集を維持。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "Stream B HIL Umbrella Planning Update \(2026-04-16\)|A1 Done && pendingDecisionQueueCount==0|Draft/Open\(hold\)|Decision Queue|Self-repair<=3|No unauthorized file edit" 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Verify失敗時の自己修復は最大3回。超過時は停止して差分記録。

### Phase 6 Proceed
- Proceed許可: Go条件成立 + Verify pass + 許可外編集0件。
- Proceed不可: NoGo条件成立時、未確定をYes/No質問化してDecision Queueへ戻す。

## Stream F A3 Rerun-05 (2026-04-18)

### Phase 1 Read
- D1〜D4固定値・役割語彙・状態語彙を `strict_mode_exception_approval_flow.md` / `operations.md` / `security.md` / `security_operational_guidelines.md` / `e2e_testing.md` で再読。

### Phase 2 ADR CDC
- AUTH-OPS-03 固定値は既存決定で充足。方針変更がないため追加ADR/CDCは起票しない。

### Phase 3 Plan（AC/DoD）
- AC: 語彙一致・責務分離・導線一致（architecture -> security -> guidelines -> e2e）・固定値一致（D1〜D4）。
- DoD: docs-check + diff-check 成功、ドリフト0件。

### Phase 4 Execute
- `operations.md` の状態語彙を canonical に収束（DraftRequest / ApprovalPending / ActiveException）。
- `e2e_testing.md` の docs-check コマンドへ `operations.md` を追加。

### Phase 5 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "Security Officer|System Owner|Platform Operator|DraftRequest|ApprovalPending|Approved|ActiveException|RollbackPending|Closed|StoppedForClarification|D1|D2|D3|D4|4h|2h|48h|15m|60m" 02_Architecture/strict_mode_exception_approval_flow.md 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/security_operational_guidelines.md 04_Documentation/e2e_testing.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**。D1〜D4不整合0件の場合のみ Proceed し、不一致が1件でも再発した場合は `StoppedForClarification` として停止する。

## Stream G A3 Operations Documentation Sync (2026-04-18)

### Phase 1 Read
- 対象正本と運用文書を再読し、`Security Officer / System Owner / Platform Operator` の用語一致、状態語彙（`DraftRequest -> ApprovalPending -> Approved -> ActiveException -> RollbackPending -> Closed` + `StoppedForClarification`）、D1〜D4（4h / 2h / 代理承認なし / 48h+15m/60m）の一致を確認。
- 読取対象: `02_Architecture/strict_mode_exception_approval_flow.md`, `04_Documentation/operations.md`, `04_Documentation/security.md`, `04_Documentation/e2e_testing.md`。

### Phase 2 CDC明文化（Context / Decision / Consequences）
- Context: AUTH-OPS-03 の固定値は既に確定済みで、A3は docs-only 同期の監査精度を維持する段階。
- Decision: 追加仕様決定は行わず、既存 canonical 語彙・責務分離・固定値を維持する。未承認事項の確定扱いは禁止。
- Consequences: ドキュメント間ドリフトの再発防止を優先し、差分が不要な場合は issue ログ更新のみで監査証跡を残す。

### Phase 3 用語/責務/固定値（D1〜D4）同期
- 同期結果: 差分不要（既存文書で用語・責務・固定値が同値）。
- 2者承認（Security Officer + System Owner）と実行責務分離（Platform Operator）を維持していることを確認。
- D1〜D4 不整合は 0 件（停止条件非該当）。

### Phase 4 Verify（docs-check）
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg -n "Security Officer|System Owner|Platform Operator|DraftRequest|ApprovalPending|Approved|ActiveException|RollbackPending|Closed|StoppedForClarification|D1|D2|D3|D4|4h|2h|48h|15m|60m" 02_Architecture/strict_mode_exception_approval_flow.md 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/e2e_testing.md`
- `rg -n "operations\\.md|security\\.md|security_operational_guidelines\\.md|e2e_testing\\.md" 02_Architecture/strict_mode_exception_approval_flow.md 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/e2e_testing.md`
- `git diff --check`

### Phase 5 Proceed（監査ログ化）
- 判定: **Ready**（docs-check 全件成功、D1〜D4 不整合 0 件、許可外ファイル編集 0 件）。
- 停止条件評価:
  - 未承認決定の確定扱い: 該当なし
  - 用語不一致の解消不能（3回超過）: 該当なし
  - 未定義競合: 該当なし
