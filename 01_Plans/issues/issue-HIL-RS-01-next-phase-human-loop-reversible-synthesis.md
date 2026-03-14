# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related Backlog: HIL-RS-01
- Related ADR/Spec: `ADR-0026`, `ADR-0001`, `00_Prompt/domain.md`, `02_Architecture/review_attribution.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- `ENV-ARCH-01` は Close 判定済みだが、次フェーズの作業起点（Backlog/依存順序/停止条件）が未固定だと再開時に手戻りが発生する。
- プロジェクト目的（意味の保留・単一正解の否定・可逆性）に直結する次タスクを、再開可能な粒度で固定する必要がある。

## 2) 背景 / Context

- `phase-exit-evaluation-ENV-ARCH-01-2026-03-11.md` で、次Backlog IDの Open 化が引き継ぎ条件として明示されている。
- `ADR-0001` では P-01/P-02/P-04 が価値軸として固定され、HIL反復が要求される。
- `domain.md` は AI が単一正解を断定しないこと、保留状態を勝手に解消しないことを拘束する。

### このIssueが保持する内容（実行管理SSOT）

- 次フェーズ（HIL-RS-01）の実行順序と依存関係
- AC達成状況
- 検証コマンドと結果

## 3) 提案する解決策 / Proposed solution

- 変更対象: docs/plans（契約先行）
- 実行パッケージ:
  - A1: Architecture契約起票（Critique入力・再提案差分・レビュー帰属）
  - A2: Frontend実装起票（候補比較/入力/差分可視を分離）
  - A3: Documentation同期起票（操作手順・制約・検証手順）
- 非目標:
  - LLM provider 抽象の再設計
  - SafeMode既定ONを緩める変更
  - 単一スコア/ランキング提示

## 4) 受入条件 / Acceptance criteria

- [x] `ADR-0026` と本issueで、目的/非目標/停止条件が一致している。
- [x] A1→A2→A3 の依存順序が明示され、各タスクが再開可能粒度で定義されている。
- [x] 安全制約（SafeMode既定ON、share/export漏えい防止を弱めない）が明記されている。
- [x] docs-check の結果が再現可能コマンドで記録される。
- [ ] `issues/README.md` と `project-progress-dashboard.md` の Active 状態が同期される（統合フェーズで実施）。

## 4.1) Stream A 合意ログ（Context / Decision / Consequences）

### Context

- Stream A は A1 契約の固定を担当し、共有リソース更新（`issues/README.md` / `project-progress-dashboard.md`）は編集禁止。
- A2/A3 が待ちなく着手するには、契約ID（`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`）と単一参照先を先に固定する必要がある。

### Decision

- A1契約の単一正本を `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` に固定する。
- 本issueでは依存順序・非目標・停止条件・検証コマンドのみ確定し、共有リソース同期は統合フェーズへ移譲する。
- ADR追加/更新の判定は「不要」とし、A1で上位方針変更が必要になった場合のみ承認待ち停止に移行する。

### Consequences

- A2/A3 は契約解釈待ちなしで作業開始できる。
- Active一覧同期は未完タスクとして残るため、統合フェーズでの追実施が必須となる。

## 4.1.1) Phase 1: Read/Baseline（Stream A記録）

- Read対象（対象3ファイル）:
  1. `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  2. `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  3. `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Baseline確認結果:
  - 契約ID3点（`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`）は3ファイルに整合して存在。
  - 単一参照先は `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` に固定済み。
- 事前想定との差分:
  - 契約未固定は検出されず、差分は「未固定箇所なし（0件）」。

## 4.1.2) Phase 2: ADR明文化（要否判定）

### Context

- Stream A の作業は既存 `ADR-0026` D2（A1契約先行）を文書レベルで固定する範囲に限定される。
- 上位方針（価値軸・安全制約・停止条件）の変更要求は発生していない。

### Decision

- 判定: **ADR追加不要**。
- 運用: 上位方針変更が新たに発生した場合のみ、承認取得までA2/A3着手を停止する。

### Consequences

- Stream A は契約IDと単一参照先の固定に集中し、A2/A3の待ちを解消できる。
- ADR起票コストを増やさず、既存ADRへの整合を維持できる。


### 4.1.3) Phase 3: Contract Fix（Stream A確定）

- 単一正本 `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` にて、以下を固定。
  - CritiqueInputContract: `schemaVersion=1.0.0`、`requiredFields=critiqueId|targetRef|critiqueType|createdAt|iteration`
  - ReviewAttributionContract: `schemaVersion=1.0.0`、`auditFields=reviewState|reviewedAt|reviewerRef|auditRecordedAt`、`overridePolicy=human_dual_control_only`
- Decision Queue（A1）: `DQ-A1-01..04` を解消済みとし、A2/A3は参照専用で利用する。

### 4.1.4) Phase 4: Verify / Proceed（Stream A再検証）

- Verify（対象3ファイル再Read + docs-check）:
  - `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` は対象3ファイルで一致。
  - 単一参照先は `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` のみ。
  - `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg ...` を再実行して整合を確認。
- Proceed（A2/A3 handoff条件固定）:
  1. A2は `03_Implement/**` のみ編集し、A1契約IDを参照専用で利用する。
  2. A3は `04_Documentation/**` のみ編集し、契約本文を変更しない。
  3. 共有リソース（`01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md`）は統合フェーズまで更新しない。
  4. Self-Correctionは0/3回で完了（追加修正不要）。

### 4.1.5) Stream A Final Pass（Plan → Execute → Verify → Proceed）

- Plan:
  - 確認対象を `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / 単一参照先 / freeze flags に限定。
- Execute:
  - 対象3ファイルを再Readし、契約ID・固定値・禁止境界を照合。
- Verify:
  - 事前想定との差分: **0件**（契約ID・`schemaVersion`・`overridePolicy`・single reference の不一致なし）。
  - `contractLinkLocked=true` / `sharedResourceFreeze=true` を維持確認。
- Proceed:
  - A1契約本文は凍結継続とし、変更要求は統合フェーズの人間判断へエスカレーションする。

## 4.2) Stream A Critical Path Gate（A2/A3着手条件）


### A1依存の固定文言（A2/A3着手前に必須確認）

- 参照先ファイル: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`（単一正本）
- 契約ID: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`
- 禁止境界:
  1. A2は `03_Implement/**` 以外を編集しない。
  2. A3は `04_Documentation/**` 以外を編集しない。
  3. `01_Plans/issues/README.md` と `01_Plans/project-progress-dashboard.md` は統合フェーズまで編集しない。
- 停止条件: 契約IDまたは参照先の複線化が検出された場合、A2/A3は着手停止。


- Contract IDs（固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
- Single Reference（固定）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 対象:
  - A1契約IDと参照先の単一化、およびA2/A3の禁止境界（編集スコープ分離）固定。
- 非対象:
  - 共有リソース更新（`01_Plans/issues/README.md`, `01_Plans/project-progress-dashboard.md`）
  - `03_Implement/**`, `04_Documentation/**` の変更
- 停止条件:
  - 契約ID/参照先の複線化が検出された場合は停止し、A2/A3着手を保留する。
  - SafeMode既定ONまたはshare/export漏えい防止の後退が示唆される場合は停止する。

## 4.4) Phase 3/4 Execute記録（Contract Fix → Verify）

- Phase 3: Contract Fix
  - 契約ID3点と単一参照先を再確認し、複線化を禁止境界として固定。
  - SafeMode既定ON・share/export漏えい防止後退禁止を維持。
  - A2編集境界=`03_Implement/**`、A3編集境界=`04_Documentation/**`を固定。
- Phase 4: Verify（Plan → Execute → Verify → Proceed）
  - Plan: 3ファイル横断で契約IDと単一参照先の重複有無を検証。
  - Execute: `rg` で契約ID/参照先の出現箇所を抽出。
  - Verify: 複線化なし、共有リソース編集要求なしを確認。
  - Proceed: A2/A3着手可（契約先行維持）を判定。
  - Self-correction: 0/3回（追加修復不要）。

## 4.5) Phase 5: Proceed / Handoff（A2/A3固定）

- Contract IDs（handoff固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
- Single Reference（handoff固定）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 禁止境界（handoff固定）:
  1. A2は `03_Implement/**` 以外を編集しない。
  2. A3は `04_Documentation/**` 以外を編集しない。
  3. `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` は統合フェーズまで編集しない。
- Fail-safe:
  - Self-correctionが3回を超える場合、前提崩れまたは未定義競合として即停止し、推測実行を行わない。

## 4.6) Stream A 引き渡し固定パケット（再掲・最終）

- 固定値一覧:
  - `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true` / `sharedResourceFreeze=true`
- 禁止変更一覧:
  - 契約ID、`schemaVersion`、`requiredFields`、`overridePolicy` の変更禁止。
  - 単一参照先（`02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`）の複線化禁止。
  - 共有リソース（`01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md`）更新禁止。
- 開始条件（A2/A3）:
  - `DQ-A1-01..04` が Resolved であること。
  - 契約ID3点と単一参照先がA1 issue/Architecture正本で一致していること。
  - 未定義競合（`schemaVersion` / `requiredFields` / `overridePolicy`）が0件であること。

## 4.3) Stream C 進捗ログ（Documentation同期）

- 実施内容: `04_Documentation/operations.md` / `security.md` / `e2e_testing.md` を A1 契約 + B 実装確定内容に同期。
- 同期点: UI導線名（A2-1/2/3）確定、validator制約（PII最小化・可逆差分・人間レビュー帰属）を運用制約へ反映。
- 検証: docs-check 3件 + HIL-RS関連 vitest 3件のコマンドを運用文書へ記録。

## 5) 実装タスク分解 / Task breakdown

- [x] T1: `ADR-0026` の status を Decider判断に応じて確定（Proposed→Accepted/Rejected）する。
- [x] T2: A1用 issue（Architecture最小I/F定義）を作成し、契約境界を固定する。
- [ ] T3: A2用 issue（Frontend分割実装）を作成し、UI変更時の screenshot方針を含む検証計画を付与する。
- [x] T4: A3用 issue（Documentation同期）を作成し、運用手順と制約を更新する。
- [x] T5: `phase-exit-evaluation-HIL-RS-01-<date>.md` の評価テンプレを用意する（`01_Plans/phase-exit-evaluation-HIL-RS-01-2026-03-13.md`）。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|hil_rs_01_a1_minimum_interface_contract" 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 期待結果:
  - A1契約ID 3件と単一参照先 1件が3ファイルで整合して検出される。
- 未実施時の理由・代替検証:
  - docs-check が実行不能な場合は `rg` 出力で契約IDと参照先の単一性を手動照合する。

## 7) 代替案 / Alternatives considered

- 代替案A: ENV-ARCH系の微修正を継続して次フェーズ定義を後ろ倒しする。
  - 却下理由: 価値直結機能（HIL反復）への着手が遅れる。
- 代替案B: ADRなしで実装先行する。
  - 却下理由: 00〜02優先の階層ルールに反し、スコープドリフトを招く。

## 8) リスクとロールバック / Risks & rollback

- 失敗モード: タスク分解が粗く、再開時に優先順位が曖昧化する。
- 影響範囲: plan/architecture/frontend/documentation の同期運用。
- ロールバック手順: HIL-RS-01 を Draft に戻し、`ADR-0026` の Decision 節を縮小して再承認する。

## 9) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 安全制約または保留/可逆性の定義変更が必要になった場合。


## 10) Stream B/C連携メモ（参照のみ）

- Stream A は契約固定のみを担当し、A2/A3の実装詳細は本Issueで管理しない。
- A2は `03_Implement/**`、A3は `04_Documentation/**` の境界を維持して別ストリームで実施する。

## 11) Stream A I/F固定 受け渡しパケット（凍結宣言）

- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- Fixed Link: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Fixed Contract IDs:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
- Fixed Values:
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`
- Freeze Declaration:
  - A2/A3はFixed Link/Fixed Valuesを参照専用とし、変更を禁止する。
  - 変更要否が生じた場合は統合フェーズで人間判断へエスカレーションする。

## 12) Stream D Phase 1-5 同期ログ（2026-03-13 rerun-3）

### Context

- 対象5ファイル（本issue / `HIL-RS-01-A1` / `issues/README.md` / `project-progress-dashboard.md` / `decision-pack`）をPhase開始ごとに再読し、A/B/C完了報告・契約リンク・Decision Queueの整合を再点検した。
- `ADR-0026` の既定（A1契約先行、A1→A2→A3直列、安全制約維持）からの逸脱要求は検出されなかった。

### Decision

- HIL方針の変更は不要と判定し、ADR明文化の追加は行わない。
- Decision Queueは `DQ-HIL-EXEC-01=Ready` / `DQ-FB-P2C-01=Approved` / `DQ-OPS-SOURCE-01=Open` を維持する。
- 次の1手は「Ready 1件の運用逸脱監査」と「Open 2件の期限管理」に限定し、A1→A2→A3依存と停止条件を維持する。

### Consequences

- 共有リソース3点（README/dashboard/decision-pack）の相互整合が維持され、未承認決定の確定扱いは発生しない。
- Gate 0承認記録反映後はA2/A3をProceed可能とし、契約本文変更禁止で誤差分を防止する。
- Stream D側の再開判定チェックリスト（未固定箇所0件 / 契約リンク固定 / Queue未決2件 / 停止条件違反0件）を継続利用できる。

## 4.2) Stream A Critical Path 固定宣言（Gate解除準備）

### Phase 1 Read同期（差分列挙）
- Read対象:
  - `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- 再確認結果:
  - HIL契約ID `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` は固定済み。
  - 単一参照先は `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` に固定。
  - 差分: deterministicTieBreakOrder の Gate 0 証跡テンプレが不足（本対応で補完）。

### Phase 2 ADR要否判定
- Context: A1作業は既存 `ADR-0026` D2 の下位具体化に限定。
- Decision: ADR追加/更新は不要。
- Consequences: 下流A2/A3は契約参照のみで着手可能。

### Phase 3 契約固定
- `FB-P2C-01` の `deterministicTieBreakOrder` を Gate 0提出パケットとして固定。
- Gate 0 承認証跡テンプレ（承認者/日時/決定文/影響範囲）を Architecture SSOTへ追加。

### Phase 4 Handoff
- 配布固定I/F: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `deterministicTieBreakOrder`
- Freeze条件: `contractLinkLocked=true`, `sharedResourceFreeze=true`
- 変更禁止: **A2/A3は契約変更禁止**。


## 12) Stream A Critical Path Completion（2026-03-14）

- Completion: `契約/I-F固定` は完了。A2/A3は待ちなしで着手可能。
- Fixed Contract IDs: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`
- SSOT: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Compatibility lock:
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`
- Downstream input contract:
  - A2: 実装時に上記固定値を読み取り専用で使用する。
  - A3: 運用文書に上記固定値を転記し、追加解釈を導入しない。
- Downstream prohibited changes:
  - 契約本文/契約IDの改変、`schemaVersion` 変更、共有リソース更新。
- Return conditions:
  - 契約衝突・不整合を検出した場合は統合フェーズへ差し戻し（人間判断必須）。
