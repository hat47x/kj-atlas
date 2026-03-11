# Issue Draft: HIL-RS-01 A1 Architecture最小I/F契約固定（Critique/再提案差分/レビュー帰属）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Related Backlog: `HIL-RS-01`
- Related ADR/Spec: `ADR-0026`, `ADR-0001`, `00_Prompt/domain.md`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`, `02_Architecture/review_attribution.md`, `02_Architecture/schemas_review_attribution.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `HIL-RS-01-A1`
- RequirementStatement: Critique入力/再提案差分/レビュー帰属の最小I/F契約を固定し、A2/A3が契約参照のみで着手可能な状態にする。
- PriorityClass: Must
- AcceptanceScenario: 前提=A1着手時点でADR-0026がAccepted、操作=I/F契約と非目標・検証計画を文書化、期待結果=A2/A3が契約未確定待ちなしで着手可能、除外=実装コード変更
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: `DQ-HIL-A1-01`, `DQ-HIL-A1-02`（いずれも案Aで確定済み）

## 0) Phase進行ログ（Plan → Execute → Verify）

### Phase 1: Read & Baseline

- Read対象（再確認済み）:
  - `ADR-0026`
  - `ADR-0001`
  - `02_Architecture/review_attribution.md`
  - `02_Architecture/schemas_review_attribution.md`
  - 本issue本文
- 未固定箇所（baseline）:
  1. Critique入力I/Fの必須/任意/禁止が未分離。
  2. 再提案差分I/Fの可逆操作（before/after）とtraceKeyが未固定。
  3. レビュー帰属I/FのA1最小境界と既存review_attributionとの接続が未固定。
  4. A2/A3参照先契約ファイルが未固定。

### Phase 2: ADR明文化・合意判定

#### Context

- A1で扱う変更は、既存 `ADR-0026` D2（契約先行）の具体化に限定される。
- 価値軸（保留・可逆・HIL反復）および安全制約（SafeMode既定ON・share/export漏えい防止）への変更要求は発生していない。

#### Decision

- 判定: **ADR追加/更新は不要**。
- 根拠:
  - `ADR-0026` D2（契約先行）を具体化する下位契約化であり、意思決定追加を伴わない。
  - 安全条件（SafeMode既定ON・漏えい防止）および価値軸（保留・可逆・HIL反復）を変更しない。

#### Consequences

- A1は文書契約の固定に集中し、A2/A3の着手待ちを発生させない。
- 将来、契約ID・安全制約・可逆要件そのものを変更する場合は、ADR承認待ちで停止する。

### Phase 3: Contract Fix（必須/任意/禁止の固定）

- `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` の3契約を、必須/任意/禁止で分解して固定済み。
- A2/A3は単一参照先 `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` のみを参照し、独自I/Fを追加しない。
- 禁止事項（SafeMode後退、share/export漏えい防止の弱化、PII生値保存）は3契約の共通境界として固定。


### Phase 3追記: Contract Fix確定値（Decision Queue解消）

- CritiqueInputContract
  - `schemaVersion`: `"1.0.0"`
  - `requiredFields`: `critiqueId | targetRef | critiqueType | createdAt | iteration`
- ReviewAttributionContract
  - `schemaVersion`: `"1.0.0"`
  - `auditFields`: `reviewState | reviewedAt | reviewerRef | auditRecordedAt`
  - `overridePolicy`: `human_dual_control_only`（`ai_only_override` / `safemode_relaxation` / `share_export_leakage_relaxation` を禁止、承認は `SecurityOfficer+SystemOwner`）

- Decision Queue: `DQ-A1-01..04` は上記固定により **Resolved**。

### Phase 4: Verify（Plan → Execute → Verify → Proceed）

- Plan: 契約ID3件と単一参照先1件の単一定義を3ファイル横断で検証する。
- Execute: `rg` により契約ID/参照先の出現箇所を収集し、重複定義の有無を確認する。
- Verify: 契約ID3件の重複定義なし、単一参照先の複線化なしを確認する。
- Proceed: A2/A3着手条件（契約ID固定・禁止境界固定）を満たしたため、handoff可能と判定する。


## 0.1) Plan宣言（対象/非対象・停止条件）

- 変更対象ファイル:
  - `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 非対象ファイル:
  - `01_Plans/issues/README.md`
  - `01_Plans/project-progress-dashboard.md`
  - 実装コード（`03_Implement/**`）
- 停止条件:
  - ADR更新が必要と判定された場合は実装を停止し、承認待ちとする。
  - 契約IDと参照先が単一化できない場合はA2/A3着手不可として停止する。
  - Self-Correctionは最大3回とし、4回目が必要な場合は前提崩れとして停止する。


## 0.2) Proceed固定handoff（A2/A3向け）

- Contract IDs（固定）: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`
- Single Reference（固定）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 禁止境界（固定）:
  1. A2は `03_Implement/**` のみ、A3は `04_Documentation/**` のみを編集する。
  2. 共有リソース（`01_Plans/issues/README.md`, `01_Plans/project-progress-dashboard.md`）は統合フェーズまで更新しない。
  3. SafeMode既定ONとshare/export漏えい防止を弱める変更を行わない。


## 0.3) Human decision fix（DQ確定記録）

- DQ-HIL-A1-01: **案Aで確定**（`intent/evidenceRefs/riskClass` を必須化、schemaVersion `v1.0` 凍結）。
- DQ-HIL-A1-02: **案Aで確定**（`reviewerId/reviewStage/approvedAt/overrideReason` を必須化、`overridePolicy=two-person` 固定）。
- 反映方針: 本issueを正本として確定内容を保持し、`project-progress-dashboard.md` は本issueとADRの確定情報を統合表示する参照レイヤとして同期する。

## 1) 課題 / Problem statement

- HIL-RS-01の実行順でA1契約が未固定だと、A2（Frontend実装）とA3（Documentation同期）が同一論点を重複解釈して競合する。
- Critique入力/再提案差分/レビュー帰属の境界を最小契約として確定しない限り、下流で「実装先行→仕様後追い」の逆流が発生する。

## 2) 背景 / Context

- `ADR-0026` D2は契約先行を明示し、A1を最初の実行タスクとして起票することをProceedに定義している。
- `domain.md` と `ADR-0001` は、保留維持・単一正解の否定・Human-in-the-loop反復を価値軸として拘束する。
- レビュー帰属は `review_attribution` 系仕様と整合させる必要がある。

## 3) 提案する解決策 / Proposed solution

- 変更対象: Docs/Architecture（契約定義のみ）
- 参照先契約（固定）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 契約最小単位:
  1. Critique入力I/F（入力必須項目、任意項目、禁止事項）
  2. 再提案差分I/F（差分単位、可逆操作、トレースキー）
  3. レビュー帰属I/F（人間承認フラグ、承認者識別、タイムスタンプ）
- 非目標:
  - LLM Provider再設計
  - Frontendコンポーネント実装
  - SafeMode既定ONの緩和

## 4) 受入条件 / Acceptance criteria

- [x] Critique入力/再提案差分/レビュー帰属の3契約が、必須/任意/禁止を含めて記述されている。
- [x] 安全条件（SafeMode既定ON、share/export漏えい防止の後退禁止）が契約制約として明記されている。
- [x] A2/A3が参照する契約IDと参照先ファイルを明示し、契約未固定箇所が0件である。
- [x] A2/A3の並列可能条件（編集境界分離、共有リソース同時編集禁止）が明文化されている。
- [x] Validation planにdocs-check 3コマンドが記載され、再現可能である。

### AC判定メモ

- 契約ID:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
- 参照先:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 契約未固定箇所:
  - 0件（A1契約本文で固定済み）

## 5) DoD（Definition of Done）

- [x] A1 issue本文にAC/非目標/停止条件/検証計画が揃っている。
- [x] docs-check（validator + unittest + rg確認）が成功している。

> 注: `issues/README.md` / `project-progress-dashboard.md` は本ストリーム編集禁止のため、同期は統合フェーズへ移譲する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: A1 issue本文に契約3点の境界定義を記述する。
- [x] T2: A2/A3並列条件（可能条件/禁止条件）を本文に固定する。
- [x] T3: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` に契約IDと必須/任意/禁止を固定する。
- [x] T4: docs-checkを実行し、結果を記録する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "HIL-RS-01-A1|A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|ADR-0026" 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 02_Architecture/hil_rs_01_a1_minimum_interface_contract.md 01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`
- 期待結果:
  - A1契約ID 3件と参照先1件が検出され、ADR-0026との整合が確認できる。
- 未実施時の理由・代替検証:
  - 実行環境制約でpython実行不可の場合、`rg`出力と差分レビューで同期状態を手動確認する。

## 8) 代替案 / Alternatives considered

- 代替案A: A2実装を先行し、I/Fは実装差分から逆算する。
  - 却下理由: 00〜02先行ルール違反となり、契約ドリフトを誘発する。
- 代替案B: A1とA3を統合して単一issueにする。
  - 却下理由: 設計契約と運用同期の責務境界が曖昧化する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 契約粒度が粗く、A2/A3が再度判断待ちになる。
- 影響範囲: `01_Plans/`, `02_Architecture/`, `04_Documentation/` の同期運用。
- ロールバック手順: A1をDraftへ戻し、契約境界を再分割して再起票する。

## 10) Additional context

- 関連Issue: `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- Stream B/C handoff（契約ID・参照先固定）:
  - `A1-CRITIQUE-IF` → `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
  - `A1-REDIFF-IF` → `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
  - `A1-ATTR-IF` → `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- A2/A3並列可能条件:
  1. A2は `03_Implement/**` の範囲でA1契約IDのみ参照し、共有ファイル（README/dashboard）を編集しない。
  2. A3は運用文書更新に限定し、A2と同一ファイルを編集しない。
  3. 共有リソース更新は統合フェーズ専用コミットに集約する。
