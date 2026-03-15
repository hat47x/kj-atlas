# Issue Draft: HIL-RS-02 A1 Governance/Contract hardening

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Related Backlog: `HIL-RS-02`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `02_Architecture/review_attribution.md`
- Expected verification level: `docs-check`

## 1) 背景

- HIL-RS-02でA2/A3を安全に開始するため、A1で契約変更差し戻し導線と未確定管理を強化する必要がある。

## 2) 目的

- A2/A3開始条件（契約固定・責務分離・停止条件）を明文化し、未確定事項の誤確定を防ぐ。

## 3) スコープ

- A1契約参照先、変更差し戻し手順、Decision Queue更新基準の文書化。

## 4) 非スコープ

- 実装コード変更。
- schemaVersionの再定義。

## 5) 受入条件

- AC-1: A1開始/停止/再開条件が文書化される。
- AC-2: human_dual_control_only と SafeMode維持が明示される。
- AC-3: A2/A3は「A1完了までDraft維持」と明記される。
- AC-4: A1差し戻し経路（未承認契約変更要求→Pending登録→再判定）が明文化される。
- AC-5: A2/A3へ引き渡す契約境界（変更禁止項目）が明文化される。

### DoD（A1完了定義）

1. A1の開始条件・停止条件・再開条件・差し戻し経路が本issue単体で追跡可能。
2. Decision Queueは全項目が `Pending` で管理され、確定扱いの項目が存在しない。
3. A2/A3の開始条件が「A1完了 + 承認ログ充足」に固定されている。
4. docs-check（validator / unittest / diff check）が成功している。

## 6) 検証方法

- `rg -n "SafeMode|human_dual_control_only|A1→A2→A3" 01_Plans/issues/issue-HIL-RS-02-*.md 01_Plans/adr/ADR-0027-hil-rs-02-next-phase-execution-plan.md`
- `python 01_Plans/issues/validate_active_issue_memos.py`

## 7) 依存関係

- `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 8) リスク

- A1定義が曖昧なままA2/A3をOpen化すると、契約逸脱が発生する。

## 9) 着手順

1. A1開始条件固定
2. 停止/再開条件固定
3. A2/A3 Draft境界反映
4. Decision QueueのPending運用固定


## 10) 開始/停止/再開条件（A1固定）

- 開始条件:
  - `ADR-0026` / `ADR-0027` とA1契約正本（SSOT）で矛盾がない。
  - A2/A3はDraft維持である。
- 停止条件:
  - 未承認の契約変更要求を確定扱いした場合。
  - SafeMode既定ON / share-export漏えい防止 / `human_dual_control_only` の後退が必要になった場合。
  - Self-Correctionが3回を超えた場合。
- 再開条件:
  - Decision Queueへ未確定事項をPendingで登録し、承認ログが追記される。
  - A1差し戻し経路（本issue）で再判定が完了する。

### 差し戻し経路（A1 contract return path）

1. 契約変更要求を検知した時点でA2/A3を `Draft` 維持（Open化禁止）。
2. 変更要求を `Decision Queue` の新規項目として `Pending` 登録。
3. `Architecture Owner` と `Plan Owner` が承認可否を記録するまで確定扱いしない。
4. 承認後にA1で契約本文を更新し、再判定ログを追記してからA2/A3開始可否を再評価する。

### A2/A3へ渡す契約境界（変更禁止項目）

- `human_dual_control_only` の制約定義。
- SafeMode既定ON。
- share/export 漏えい防止の既定ポリシー。
- `schemaVersion` / `overridePolicy` の識別子整合。
- `contractLinkLocked=true` / `sharedResourceFreeze=true`。

上記はA1完了時点で凍結し、A2/A3では変更要求を直接反映せず、必ずA1へ差し戻す。

## 11) フェーズ実行ログ（Plan → Execute → Verify → Proceed）

### Phase 1: Read同期
- Plan: A1→A2→A3依存、停止条件、禁止境界を再確認する。
- Execute: `ADR-0026` / `ADR-0027` / 本issue / 次フェーズissueを再読。
- Verify: 依存順序・Draft維持条件・SafeMode制約を照合。
- Proceed: 差分がなければPhase 2へ進む。

### Phase 2: Plan
- Plan: AC/DoD不足を洗い出し、追補案を作成する。
- Execute: AC-4/AC-5とDoDを追加し、A1契約の完了定義を固定。
- Verify: A2/A3開始条件がA1完了依存に固定されていることを確認。
- Proceed: 合意待ち項目はDecision Queueへ `Pending` で登録してPhase 3へ進む。

### Phase 3: Execute
- Plan: 開始/停止/再開/差し戻し導線を運用可能にする。
- Execute: 差し戻し経路と変更禁止項目を明文化。
- Verify: 「未承認変更の確定扱い禁止」が明文化されているか確認。
- Proceed: A1契約境界を固定してPhase 4へ進む。

### Phase 4: Verify
- Plan: AC/DoD照合とdocs-check実施。
- Execute: validator / unittest / diff checkを実行。
- Verify: 失敗時は最大3回までSelf-Correction、超過時は停止。
- Proceed: すべて成功時のみPhase 5へ進む。

### Phase 5: Proceed
- Plan: A2へ渡す契約境界を凍結して引き継ぐ。
- Execute: 本issueに変更禁止項目とDraft解除条件を残す。
- Verify: A2/A3はA1完了までOpen化不可であることを最終確認。
- Proceed: Stream AはA2/A3開始可能状態の宣言で停止。

## 12) Decision Queue（未確定管理）

| QueueID | Topic | Status | Owner | Next Action |
|---|---|---|---|---|
| DQ-HIL-RS-02-A1-001 | A2 mock fixture命名揺れの吸収方針 | Pending | Architecture Owner | A2 kickoff reviewで承認 |
| DQ-HIL-RS-02-A1-002 | A3運用文書でのSSOT参照表記統一 | Pending | Documentation Owner | A3 handoff reviewで承認 |
