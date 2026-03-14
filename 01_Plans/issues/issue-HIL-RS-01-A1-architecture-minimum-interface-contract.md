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
- DecisionQueueRef: `DQ-A1-01`, `DQ-A1-02`, `DQ-A1-03`, `DQ-A1-04`（Resolved）

## 0) Phase進行ログ（Plan → Execute → Verify）

### Phase 1: Read & Baseline

- 対象3ファイル再Read（Phase開始同期）:
  1. `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  2. `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  3. `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
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

### Phase 1.1: 事前想定との差分（今回Read時点）

- 差分1: `0.3) Human decision fix` が旧確定値（`schemaVersion=v1.0`, `overridePolicy=two-person`）のままで、
  A1契約正本 `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の確定値（`1.0.0`, `human_dual_control_only`）と不一致。
- 差分2: Decision Queue参照が `DQ-HIL-A1-*` 表記のままで、`DQ-A1-01..04` のResolved記録と一致しない。

### Phase 1.2: 未確定契約項目の列挙（必須/任意/禁止・schemaVersion・tie-break）

- `A1-CRITIQUE-IF`
  - 必須: `critiqueId | targetRef | critiqueType | createdAt | iteration`
  - 任意: `comment | constraintHints`
  - 禁止: 単一正解への自動確定、`reviewed`自動更新、PII生値保存
  - `schemaVersion=1.0.0`
- `A1-REDIFF-IF`
  - 必須: `proposalId | basedOnIteration | diffOps[] | traceKey`
  - 任意: `rationale`
  - 禁止: 逆操作不能な片方向差分、trace欠落、SafeMode違反を誘発する暗黙実行
  - `schemaVersion`: N/A（構造契約として `diffOps` 最小単位を固定）
- `A1-ATTR-IF`
  - 必須: `reviewState | reviewedAt | reviewerRef`
  - 任意: `reviewContext | ownerRef`
  - 禁止: AIのみで`human_reviewed`遷移、生ID保存、`reviewEvents`欠如時の閲覧不可化
  - `schemaVersion=1.0.0`
- tie-break順序:
  - 本A1契約では未定義（N/A）。順序規約は `issue-FB-P2C-01-a1-interface-contract.md` の `deterministicTieBreakOrder` に分離管理。

#### Phase 2進行前の修正方針

- 方針1: A1契約の確定値は Architecture正本に統一する。
- 方針2: Decision Queueは `DQ-A1-01..04` のResolved表記へ揃える。

#### Phase 2進行前の修正結果

- 結果1: `schemaVersion` は `1.0.0` へ統一済み。
- 結果2: `overridePolicy` は `human_dual_control_only` へ統一済み。
- 結果3: Decision Queue参照は `DQ-A1-01..04` で統一済み。

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

- `DQ-A1-01`: **Resolved**（CritiqueInputContract.requiredFields 固定）。
- `DQ-A1-02`: **Resolved**（CritiqueInputContract.schemaVersion=`1.0.0` 固定）。
- `DQ-A1-03`: **Resolved**（ReviewAttributionContract.auditFields 固定）。
- `DQ-A1-04`: **Resolved**（ReviewAttributionContract.overridePolicy=`human_dual_control_only` 固定）。
- 反映方針: A1契約の単一正本は `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` とし、本issueは実行管理ログを保持する。


## 0.4) Phase 1 未確定I/F項目の再判定（項目名/判定条件）

- 判定対象:
  1. `CritiqueInputContract.requiredFields`
  2. `CritiqueInputContract.schemaVersion`
  3. `ReviewAttributionContract.auditFields`
  4. `ReviewAttributionContract.overridePolicy`
  5. `contractLinkLocked`
  6. `sharedResourceFreeze`
- 判定条件:
  - 各項目が `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` に固定値として存在すること。
  - `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` を更新しないことが明文化されていること。
- 判定結果:
  - 1〜4: **Fixed**（`DQ-A1-01..04` Resolved）
  - 5〜6: **Fixed**（Phase 3で証跡テンプレを追加し、Proceed条件へ昇格）
  - 未確定I/F項目: **0件**

## 0.5) Phase 2 ADR記述（承認記録済み）

### Context

- Stream Aの変更は契約固定に限定され、上位方針（ADR-0026のDecision）を変更しない。
- `contractLinkLocked=true` / `sharedResourceFreeze=true` は運用固定値の明文化であり、新規アーキ判断の追加ではない。

### Decision

- ADR追加/更新は不要とする。
- ただし、**承認待ち状態**として「契約固定値の変更要求が発生した場合のみ人間判断にエスカレーションする」ガードを維持する。

### Consequences

- A2/A3は本A1契約を参照して着手可能。
- 契約固定値の変更は統合フェーズの人間承認を必須とし、ストリーム内の推測変更を禁止する。



## 0.6) Phase 4 Handoff固定（A2/A3向け最終宣言）

- Single Reference（固定）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Contract IDs（固定）: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`
- Fixed Values（固定）:
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`
- Freeze Flags（固定）:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 変更凍結宣言:
  - A1契約本文は凍結済みとし、変更は統合フェーズの人間判断でのみ実施する。

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


## 11) Phase 3/4 固定証跡と受け渡し（Stream A）

### 11.1 Contract Freeze Evidence

- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- single reference: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- locked contract IDs: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`

### 11.2 A2/A3固定リンク・固定値一覧

- Fixed Link:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Fixed Values:
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `CritiqueInputContract.requiredFields=critiqueId|targetRef|critiqueType|createdAt|iteration`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.auditFields=reviewState|reviewedAt|reviewerRef|auditRecordedAt`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`

### 11.3 変更凍結宣言

- A2/A3実行中は、上記Fixed Link/Fixed Valuesの変更を凍結する。
- 変更が必要な場合は統合フェーズへ移管し、人間判断（Security Officer + System Owner）を必須とする。

### 11.4 Blocked解除条件（Stream B/C/D handoff）

- Stream B（A2実装）は、`contractLinkLocked=true` かつ `DQ-A1-01..04=Resolved` の両条件を満たした場合のみ着手可能。
- Stream C（A3文書同期）は、Single Reference が `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の1件に固定されている場合のみ着手可能。
- Stream D（統合判定）は、`sharedResourceFreeze=true` を維持したまま A2/A3 の成果を受領し、共有リソース更新を統合フェーズへ集約する。
- いずれか1条件でも未達の場合、Blocked継続とし人間判断へエスカレーションする。

## 9) Stream D受入監査ログ（2026-03-13 rerun-3）

### Context

- Stream Dで対象5ファイル再読（Phase 1-5）を実施し、A/B/C完了報告受領済み状態とA1契約リンク固定状態を再確認した。
- `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` の3契約IDと単一参照先 `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` の複線化は検出されなかった。

### Decision

- A1契約は既存確定値を維持し、追加の契約変更・ADR更新は不要と判断する。
- Stream D統合では A1→A2→A3 依存を保持し、Gate 0未承認時のA2/A3 Block継続を明示する。

### Consequences

- A2/A3は「契約参照のみ」の前提を維持したまま再開判定を行える。
- Decision Queueの解消済み項目（`DQ-A1-01..04`）と未決項目（`DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01`）の境界が明確に維持される。

## 10) Stream A 再同期ログ（2026-03-14 / Phase 1→4）

### Plan

- Scopeを `01_Plans/issues/issue-HIL-RS-01*` と `02_Architecture/*interface*` に固定し、編集禁止境界（`03_Implement/**` / 共有リソース3ファイル）を再確認した。
- Verify観点を `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `schemaVersion` / `overridePolicy` / `contractLinkLocked` / `sharedResourceFreeze` に限定した。

### Execute

- 対象再読（Phase 1）:
  - `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 未固定I/Fの再列挙（Phase 1）:
  - APIシグネチャ: 未固定項目なし（0件）。
  - 型/requiredFields: 未固定項目なし（0件）。
  - `schemaVersion`: 未固定項目なし（0件、`1.0.0`固定）。
  - 判定条件（`overridePolicy`/tie-break/freeze flags）: 未固定項目なし（0件）。
- ADR明文化判定（Phase 2）:
  - 新規Decision追加は不要（既存Context/Decision/Consequencesで閉じており、未定義競合なし）。
- 契約固定（Phase 3）:
  - `contractLinkLocked=true` / `sharedResourceFreeze=true` の維持を再確認。
  - 単一参照先 `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` を再固定。
- ハンドオフ（Phase 4）:
  - B/C向け変更禁止項目（契約ID・schemaVersion・requiredFields・overridePolicy・freeze flags）を再掲し、凍結継続を宣言。

### Verify

- `rg` による横断確認で、契約ID複線化・参照先分岐・固定値逸脱は未検出。
- Self-Correctionは不要（1回目検証で合格）。

### Proceed

- A1は **contract fixed / handoff ready** 状態を維持。
- 失敗条件（契約リンク未固定、未定義競合、freeze flag欠落）が生起した場合のみ停止し、人間判断へエスカレーションする。

## Phase 4 Handoff（A2/A3固定配布）

- 固定I/F一覧:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `deterministicTieBreakOrder`（`FB-P2C-01` Gate 0提出パケット）
- Single Reference（契約本文SSOT）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Freeze条件:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 変更禁止条件:
  - A2は `03_Implement/**` のみ、A3は `04_Documentation/**` のみを編集対象とする。
  - A2/A3は契約ID、schemaVersion、requiredFields、overridePolicy、deterministicTieBreakOrder を変更してはならない。
  - **A2/A3は契約変更禁止**。


## 14) Stream A Finalization Record（2026-03-14）

### Phase 1: Read/Baseline（Plan → Execute → Verify → Proceed）
- Plan: 契約ID・`schemaVersion`・判定順序（対象外/N/A）・単一参照先を再抽出する。
- Execute: `issue-HIL-RS-01*` 2件と `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` を再読込。
- Verify: 差分判定は **差分0**（`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`、`schemaVersion=1.0.0`、`overridePolicy=human_dual_control_only` が一致）。
- Proceed: Phase 2へ進行。

### Phase 2: ADR要否判定（Plan → Execute → Verify → Proceed）
- Plan: 上位方針変更の有無を `ADR-0026` D2 と照合する。
- Execute: 変更対象をA1契約文面の固定化に限定。
- Verify: **ADR追加不要**（上位方針の追加/変更なし、既存方針の具体化のみ）。
- Proceed: Phase 3へ進行。

### Phase 3: 契約固定（Plan → Execute → Verify → Proceed）
- Plan: 単一参照先・契約ID・互換条件を固定リンクとして再宣言する。
- Execute: 以下をA2/A3向け固定リンクとしてロック。
  - `A1-CRITIQUE-IF` → `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md#21-critique入力ifcontract-key-a1-critique-if`
  - `A1-REDIFF-IF` → `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md#22-再提案差分ifcontract-key-a1-rediff-if`
  - `A1-ATTR-IF` → `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md#23-レビュー帰属ifcontract-key-a1-attr-if`
- Verify: 固定リンクの参照先は1件（SSOT）で複線化なし。
- Proceed: Phase 4へ進行。

### Phase 4: Verify/Handoff（Plan → Execute → Verify → Proceed）
- Plan: AC/DoD・契約一貫性・境界外編集ゼロを確認して下流入力を確定する。
- Execute: `rg` による契約ID照合、編集ファイル境界照合。
- Verify:
  - AC/DoD: Pass
  - 契約ID一貫性: Pass
  - 境界外編集: 0件
- Proceed（A2/A3入力契約）:
  - 入力契約: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`（上記固定リンクのみ参照）。
  - 禁止事項: 契約ID・`schemaVersion`・`requiredFields`・`overridePolicy` の変更、SSOT複線化、共有リソース更新。
  - 差し戻し条件: 契約ID衝突、`schemaVersion` 不一致、SafeMode/漏えい防止後退、境界外編集発生。
