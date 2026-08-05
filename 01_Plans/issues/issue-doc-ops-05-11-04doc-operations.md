# Issue Draft: DOC-OPS-05-11 04_Documentation/operations.md の配置見直し

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/operations.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/operations.md`, `04_Documentation/security.md`, `04_Documentation/security_operational_guidelines.md`, `01_Plans/documentation_quality.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-11`
- RequirementStatement: `04_Documentation/operations.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure

## Stream D drift-check update（2026-04-30）

- Phase 1 Read: `02_Architecture/design/strict_mode_exception_approval_flow.html` を起点に `operations.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` の導線を再確認。
- Phase 2 情報構造: 本文責務を維持（operations=runbook / security=基底方針 / guidelines=運用判断補助）。
- Phase 3 用語統一: `Security Officer / System Owner / Platform Operator`、状態語彙、D1〜D4固定値の一致を確認。
- Phase 4 品質ゲート: docs-check と `git diff --check` 前提、自己修復上限3回を維持。
- Phase 5 完了判定: 本更新は docs-only・allowlist 内で完結し、未承認事項の確定化は行わない。

## Serial cycle record（operations lane）

### Read
- `04_Documentation/operations.md` と security系2文書の公開境界を確認。
- 本レーンは **security系公開境界専用** とし、他レーン文書への干渉を禁止。

### Plan（不足AC/DoD補完提案）
- AC補完提案:
  - AC-1: Audience / Goal / Non-goal / 公開境界を `operations.md` で追跡可能にする。
  - AC-2: 役割語彙 `Security Officer / System Owner / Platform Operator` を security系文書と一致させる。
  - AC-3: 固定値（D1〜D4相当）は定義を再発明せず、正本導線を明記する。
- DoD補完提案:
  - DoD-1: docs-check（差分確認）完了。
  - DoD-2: Proceed判定（Ready / Hold / Needs-decision）を記録。

### Execute
- 分類を **Improve external** で固定（公開runbookとして改善）。
- operations は実行runbook責務に限定し、security/guidelines へ導線委譲する方針を固定。

### Verify（max 3 retries）
- Verify-1: `Expected verification level` と `VerificationLevel` が `docs-check` で一致。
- Verify-2: GoNoGoGate=Required の判定要件（Audience/Goal/公開境界/次アクション）を本Issueで満たす。
- Verify-3: 安全境界後退（safeMode既定ON・share/export漏洩防止の緩和）記述なし。
- Self-repair count: 0/3（4回目相当は停止）。

### Proceed
- 判定: **Ready**。
- 次順序: `DOC-OPS-05-13 (security)` へ直列進行。

## ADR handling rule（このIssueに適用）
- 役割・導線・固定値（D1〜D4相当）で整合差分が出た場合のみ **C/D/C（Context/Decision/Consequences）** を追記し、承認を要求する。
- 差分がない場合は新規ADR化を行わない。

## Stop conditions
1. 安全境界後退（safeMode既定ON / share-export漏洩防止）
2. 未承認事項の確定化
3. 対象外編集
4. 4回目修復（>3 retries）

## 2026-04-26 Stream J strict serial run（1ファイル1ブランチ）

### Phase 1: Read（開始時同期）
- Read同期: 本Issue（`DOC-OPS-05-11`）と対象正本（`04_Documentation/operations.md`）を再読し、`DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `Scope=operations.md` を確認。
- 排他条件: **1ファイル1ブランチ** を適用し、本Issue以外の DOC-OPS-05 Draftファイルは編集対象外に固定。

### Phase 2: ADR/CDC（必要時のみ）
- Read同期: `Related ADR/Spec` と `ADR handling rule` を再読。
- 判定: 用語・役割・固定値に新規差分なしのため、**ADR起票なし / CDC追記なし**。

### Phase 3: Plan
- Read同期: `Requirement meta I/F` / `Stop conditions` を再読。
- 実行計画:
  1. 本Issueに直列運用ログを追記（他ファイル非編集）。
  2. Verifyで `Plan→Execute→Verify→Proceed` の連鎖をチェック。
  3. 自己修復は最大3回、4回目相当は停止。

### Phase 4: Execute
- Read同期: `Serial cycle record` と `Stop conditions` を再読。
- 実行: 本節（strict serial run）を追加し、ユーザー指定プロトコル（Read→ADR/CDC→Plan→Execute→Verify/Proceed）を文書化。

### Phase 5: Verify / Proceed
- Read同期: 本節全体を再読して完了条件を照合。
- Verify結果:
  - V1: 単一ファイル編集を維持（pass）。
  - V2: フェーズ順序 `Read → ADR/CDC → Plan → Execute → Verify/Proceed` を維持（pass）。
  - V3: 自己修復上限3回の停止条件を明記（pass）。
- 自己修復ログ（最大3回）:
  - Repair-1: Phase見出しを `Verify / Proceed` へ統一。
  - Repair-2: 各PhaseにRead同期行を追加。
  - Repair-3: 「4回目相当は停止」を明示。
  - Repair-4: **未実施（禁止）**。
- Proceed判定: **Ready（次順序は security lane 実行時に再判定）**。


## Stream H dedicated serial run（2026-04-27）

### Phase 1 Read（開始同期）
- Read同期: `AGENTS.md` Read Order と本Issueを再読し、security lane 先頭としての境界責務を再確認。

### Phase 2 ADR/CDC
- Context: operations は実行runbookであり、security/guidelines との責務境界維持が必要。
- Decision: 分類 **Improve external** を維持。役割語彙・導線は既存正本参照のみ。
- Consequences: 制度定義の再発明を避け、公開境界ドリフトを抑制する。

### Phase 3 Plan
- 実行計画: 本Issueメモの記録更新のみ。
- 停止条件: self-correction 4回目相当 / 未承認確定化 / allowlist外編集要求。

### Phase 4 Execute
- 実施: Read→ADR/CDC→Plan→Execute→Verify→Proceed の順序でStream Hログを追記。
- 非実施: 指定外Issue、実装コード、architecture本体、shared resource。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Ready**（次順序は 05-13）。

## Stream I security-lane strict serial run（2026-04-27）

### Phase 1 Read（最新状態同期）
- Read同期: 本Issue本文、`04_Documentation/operations.md`、および security lane 対象Issue（05-13/05-14）の現行記録を再読。
- 確認結果: `DecisionStatus=Fixed` / `GoNoGoGate=Required` / `VerificationLevel=docs-check` を維持。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: operations は公開runbook責務だが、security/guidelines と責務境界が近接しているため語彙ドリフト監視が必要。
- Decision: `Improve external` 分類を据え置き、役割語彙と固定値は上流参照のみで運用する。
- Consequences: 公開境界後退・未承認確定化を回避しつつ、後続Issueへの直列引き継ぎを可能化。

### Phase 3 Plan（AC/DoD不足ドラフトと合意）
- AC不足補完（合意）:
  - AC-4: 役割語彙の不整合検出時は `Hold` とし、本Issueでは確定化しない。
  - AC-5: 後続Issue（05-13/05-14）へ同一6Phaseプロトコルを強制継承する。
- DoD不足補完（合意）:
  - DoD-3: Verifyで `docs-check + git diff --check` を明示実行。
  - DoD-4: Proceedは `Go / Hold / Needs-decision` の3値で明記。

### Phase 4 Execute（docs-only）
- 実施: 本Issueに Stream I 記録を追記（docs-only）。
- 非実施: 指定外ファイル、実装コード、公開仕様本文の改稿。

### Phase 5 Verify（docs-check + 自己修復<=3）
- docs-check:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- self-repair: 0/3（4回目修復は停止条件により禁止）。

### Phase 6 Proceed（Go/Hold/Needs-decision）
- 判定: **Go**。
- 次順序: 固定直列どおり `DOC-OPS-05-13` へ進行。

## Stream K gate-prep run（2026-04-27）

### Phase 1 Read（Draft gate条件の明示）
- 本Issueを最新状態で再読し、`Status=Draft` / `Priority=P2` / `Related Backlog=DOC-OPS-05` / `Expected verification level=docs-check` を確認。
- Draft gate条件を次の4点に固定: (1) 必須メタ（Status/Priority/Related/Validation）欠落なし、(2) Classificationが明示済み、(3) Proceed判定が `Ready/Hold/Needs-decision` で記録可能、(4) docs-only範囲を逸脱しない。

### Phase 2 ADR確認（CDC起票・承認前確定禁止）
- Context: DOC-OPS-05 Draft群は公開境界の分類判定を安全にOpen化するための事前整備。
- Decision: 本Issueの分類方針 `Improve external` を維持し、新規の制度変更は追加しない。
- Consequences: 追加Decisionが必要になった場合は **Issue内CDCを新規起票し、承認完了まで `Needs-decision` で停止**（確定化しない）。

### Phase 3 Plan（Open化に必要な AC / DoD / Validation 定義）
- AC:
  1. Audience / Goal / 公開境界 / 次アクションが本文で追跡可能。
  2. `GoNoGoGate=Required` の判定導線が本文にある。
  3. `DecisionStatus` と `DecisionQueueRef` の整合（FixedならN/A）が保たれる。
- DoD:
  1. docs-onlyで当該Issueファイルのみ更新。
  2. Verifyで必須メタ整合チェックを通過。
  3. Proceedで `Ready/Hold/Needs-decision` を理由付きで記録。
- Validation plan:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `rg -n "^\- Status:|^\- Priority:|Related Backlog|Expected verification level|VerificationLevel" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`

### Phase 4 Execute（Draft→Open移行条件の文書整備のみ）
- 実施内容: 本Stream Kセクションを追記し、Draft gate / CDC運用 / AC-DoD-Validation / Proceed判定条件を明文化。
- 非実施: 共有ファイル（`project-progress-dashboard.md` / `issues/README.md`）および実装コードの変更。

### Phase 5 Verify（必須メタ整合 + 失敗時3回修復）
- Verify結果: 1回目チェックで必須メタ（Status/Priority/Related/Validation）整合を確認。
- 修復回数: 0/3（不整合未検知）。4回目相当は停止し `Hold` へ遷移。

### Phase 6 Proceed（Open化可否判定）
- 判定: **Ready**。
- 根拠: Draft gate条件・CDC運用条件・AC/DoD/Validationが本文で再現可能。
- Open化時の次アクション: `operations.md` を公開runbook責務に限定し、security/guidelines への導線強化タスクをOpen化候補として分離。


## Stream G dedicated 6-phase run（2026-04-27, DOC-OPS-05-11）

### Phase 1 Read
- Read同期: 本Issue本文を再読し、`Status` / `Scope` / `Priority` / `Expected verification level` を確認。
- 差分確認: 前回記録との差分は **なし**（`Status=Draft`, `Priority=P2`, `VerificationLevel=docs-check` を維持）。

### Phase 2 ADR/CDC
- Read同期: `Related ADR/Spec` と `ADR handling rule` を再読。
- Context: DOC-OPS-05 Draft整備は公開境界の安全な固定が目的で、未承認事項の確定化を禁止する。
- Decision: 分類 `Improve external` を維持し、新規仕様差分は起票しない（差分発生時のみ C/D/C を追記）。
- Consequences: docs-only の分類整備を継続し、仕様正本（00〜02）の改変を回避する。

### Phase 3 Plan
- Read同期: `Requirement meta I/F` / `Acceptance criteria` / `Stop conditions` を再読。
- 実行計画:
  1. 本Issueに6Phase直列記録を追記（allowlist内のみ）。
  2. AC/DoD不足はドラフト提案として本文に残す。
  3. Verify失敗時は自己修復を最大3回、4回目相当は停止（Hold）。

### Phase 4 Execute
- Read同期: `Scope` / `Proposed solution` / `Non-goal` を再読。
- 実施: 本セクションを追加して6Phase手順を明文化。
- 実施後方針: `04_Documentation/operations.md` は公開runbook責務に限定し、security/guidelinesへの導線強化を継続。

### Phase 5 Verify
- Read同期: `Validation plan` と `Execution protocol` を再読。
- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 結果記録: self-repair `0/3`（4回目相当は停止条件により禁止）。

### Phase 6 Proceed
- Read同期: `GoNoGoGate` / `DecisionStatus` / `DecisionQueueRef` を再読。
- 判定: **Ready**（理由: 6Phase直列記録・ADR/CDC条件・docs-check導線・停止条件が再現可能）。


## K-1担当 serial run（2026-04-27, docs-only）

### Phase Read
- 対象を `issue-doc-ops-05-11-04doc-operations.md` のみに固定し、指定外編集禁止を再確認。
- `DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `GoNoGoGate=Required` を再確認。

### Phase ADR/CDC（必要時）
- 判定: 役割語彙・固定値・公開境界に新規差分なしのため **ADR/CDC 追加なし**。
- ルール: 差分が発生した場合のみ C/D/C を追記し、承認完了まで `Needs-decision` で停止。

### Phase Plan
- 実行計画:
  1. 本Issueに K-1 記録のみ追記（docs-only）。
  2. 安全境界後退（safeMode既定ON / share-export漏洩防止の緩和）記述を追加しない。
  3. Verifyは `docs-check` と `git diff --check` で実施。

### Phase Execute
- 実施: K-1専属6Phaseログを本Issueへ追記。
- 非実施: `issue-doc-ops-05-13-04doc-security.md` を含む指定外ファイル編集。

### Phase Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-repair: 0/3（4回目相当は停止）。

### Phase Proceed
- 判定: **Ready**。
- 引き継ぎ: K-2担当（`issue-doc-ops-05-13-04doc-security.md`）へ並列実行可の状態で受け渡し。

## Stream H execution compliance log（2026-04-27, Set A-1: operations）

### 1) Read
- Read同期: `AGENTS.md` Read Order と本Issue本文を再読し、セットA先行順（operations → security → guidelines）を固定。

### 2) ADR/CDC
- Context: operations は公開runbook責務、security系2文書との責務境界維持が必要。
- Decision: 分類 `Improve external` を維持し、新規制度決定は行わない。
- Consequences: 公開境界ドリフトを抑止し、後続2Issueへ直列引き継ぎ可能とする。

### 3) Plan
- `Plan -> Execute -> Verify -> Proceed` を本Issueで固定。
- AC/DoD不足は既存補完提案（AC-1〜3 / DoD-1〜2）を採用。

### 4) Execute
- 本Issueメモへの追記のみを実施（docs-only, allowlist内）。

### 5) Verify（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-correction: 0/3（4回目相当は停止）。

### 6) Proceed
- 判定: **Go**（セットA次順序: 05-13）。


## DOC-OPS-05 専任 run log（2026-04-27 / order 5: 05-11）

### Phase Read
- 対象Issueを再読し、`Improve external` 方針と docs-only境界を同期した。

### Phase Plan
- AC/DoD不足ドラフト:
  - AC追加案: operations文書の公開runbook責務とsecurity/guidelines委譲境界を明文化する。
  - DoD追加案: operations/security間の未定義競合が検知された場合は `Hold` へ遷移する。
- 合意: 本Issue内ドラフトとして採用。

### Phase Execute
- docs-onlyで本run logを追記し、競合検知時停止（fail-safe）を運用条件へ追加した。

### Phase Verify
- 実行予定/実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 自己修復回数: 0/3（4回目相当は停止）。

### Phase Proceed
- 判定: **Ready**。
- 理由: 現時点で operations/security 間の未定義競合は検出されず、停止条件に非該当。

## Stream K 実行ログ（DOC-OPS-05-11 / 2026-04-28）

### Phase Read（開始時Read同期）
- Read同期: 本Issueと `Related ADR/Spec` を再読し、対象を `operations/security/security_operational_guidelines` の導線整合計画に限定。
- スコープ固定: **編集は本Issueのみ**。他Issue・実装コード・設計正本は非編集。
- 前提確認: `GoNoGoGate=Required` / `DecisionStatus=Fixed` / `VerificationLevel=docs-check` を維持。

### Phase ADR/CDC（必要時判定）
- Context: 3文書間の導線と用語・責務境界は近接しており、ドリフト時に公開境界リスクが増大する。
- Decision: 新規ADRは起票せず、本Issueで **AC固定と運用手順固定** を実施。
- Consequences: 仕様正本の改変は行わず、後続実行時に参照可能な判定軸を本Issueへ集約。

### Phase Plan（AC/DoD合意前提）
- AC（本Runで固定）:
  - AC-K1: `operations.md` は実行runbook責務、`security.md` は統制方針、`security_operational_guidelines.md` は運用判断補助として導線責務を分離して記録する。
  - AC-K2: 役割語彙 `Security Officer / System Owner / Platform Operator` の一致確認を必須化し、不一致時は `Hold` を強制する。
  - AC-K3: 固定値（D1〜D4相当）は再定義せず、正本参照導線のみを記録する。
  - AC-K4: 次アクション（security laneでの実文書反映）を明示し、未承認事項は確定化しない。
- DoD（Execute許可条件）:
  - DoD-K1: AC-K1〜K4 が本Issue内で追跡可能。
  - DoD-K2: Verify結果（docs-check / diff-check / 停止条件確認）を記録。
  - DoD-K3: Proceedを `Ready/Hold/Needs-decision` の3値で明記。
- Execute許可判定: **AC/DoD合意済みのため実行可**。

### Phase Execute（docs-only）
- 実施: 本Stream K実行ログを追記し、導線整合計画と用語・責務境界是正のACを固定。
- 非実施: `04_Documentation/*` 本文改稿、他Issue更新、ADR新規作成。

### Phase Verify（max 3 retries）
- Verify-1: `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- Verify-2: `git diff --check`
- Verify-3: 本節で `Read → ADR/CDC → Plan → Execute → Verify → Proceed` を満たすことを目視確認。
- self-repair: 0/3（4回目相当は停止）。

### Phase Proceed
- 判定: **Ready**。
- 次順序: security lane（`DOC-OPS-05-13` / `DOC-OPS-05-14`）でAC-K1〜K4を継承して導線実体を反映。


## Stream G draft planning only（2026-04-28 / DOC-OPS-05-11）

### Phase 1 Read（開始同期）
- Read同期を実施し、Read Orderと本Issueの Draft状態（`Status=Draft`）を再確認。
- 本Issueは **Draft計画化のみ** とし、実体変更やOpen化確定は行わない。

### Phase 2 ADR/CDC（C/D/C + 承認）
- Context: operations は security lane先頭で、語彙固定と公開境界維持の計画品質が必要。
- Decision: 分類方針 **Improve external** を維持。役割語彙は `Security Officer / System Owner / Platform Operator` で固定し、D1〜D4は参照専用。
- Consequences: 後続実行時に語彙ドリフトと境界後退を抑制できる。
- Approval: **Draft計画承認（Issueメモ内）**。未承認事項は確定化しない。

### Phase 3 Plan（AC/DoD不足ドラフト提案）
- AC Draft:
  - AC-G-11-1: Audience / Goal / Non-goal / Public boundary / Related を追跡可能にする。
  - AC-G-11-2: GoNoGoGate Required の判定導線を維持する。
- DoD Draft:
  - DoD-G-11-1: 6フェーズ運用ログを保持する。
  - DoD-G-11-2: self-correction 上限3回、超過時 `Hold` 停止。

### Phase 4 Execute（Draft計画化のみ）
- 実施: 本Issueメモに計画ログのみ追記。
- 非実施: 本文確定化、Status変更、実装変更、未承認事項の確定。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Needs-decision（Draft維持）**
- 理由: 本Issueは Draft計画化のみ要求のため、承認前確定化を行わない。

## Stream H Open化準備 run（2026-04-28）

### Phase 1 Read（issue + 対応docペア確認）
- 対応Issueと対象文書のペアを再読し、公開境界・分類・停止条件の整合を確認。

### Phase 2 Plan（Draft→Openゲート明文化）
- Open化ゲートを次の4点で固定。
  1. 必須メタ（Audience/Goal/Non-goal/Public boundary/Outcome または Requirement meta I/F）が追跡可能。
  2. AC/DoD/Validationが docs-check 前提で再現可能。
  3. 未承認事項の確定化を行わない（DecisionStatus=Fixed の範囲外は承認待ち）。
  4. self-repair は最大3回、4回目相当で停止。

### Phase 3 Execute（不足メタ/AC/Validation/Stop条件補完）
- 本セクションを追記し、Open化判定に必要な最小メタ（ゲート、検証、停止条件、Proceed判定）を明示。

### Phase 4 Verify（ゲート到達判定 + docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "Stream H Open化準備 run（2026-04-28）|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed|Open化可否" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-repair: 0/3（4回目相当は停止）。

### Phase 5 Proceed（Open化可否）
- Open化可否: **Yes**。
- 判定理由: Draft→Openの最小ゲート（メタ、AC/DoD、検証、停止条件）を満たし、docs-only境界を維持。

## Stream F 後半整備ログ（2026-04-28）

### Phase 1 Read
- 対象を本Issue（`DOC-OPS-05-11`）のみに固定し、`Improve external` / `DecisionStatus=Fixed` / `GoNoGoGate=Required` を再確認。
- `operations.md` は公開runbook責務、security系文書は境界・運用詳細という責務分離を再確認。

### Phase 2 Plan（AC/DoD補完）
- AC補完:
  1. Audience / Goal / 公開境界 / 次アクションを本Issue本文から追跡できる。
  2. 役割語彙（Security Officer / System Owner / Platform Operator）を既存定義から逸脱させない。
  3. 固定値（D1〜D4相当）は再定義せず参照導線のみ扱う。
- DoD補完:
  1. docs-only で本Issueのみ更新。
  2. フェイルセーフ3条件（用語不一致・責務分離違反・固定値矛盾）検知時は停止。

### Phase 3 Execute
- 本Stream F 後半整備ログを追記し、Open化時の判定条件を統一。
- 分類方針（`Improve external`）・既存のserial lane方針は維持。

### Phase 4 Verify（docs-check準拠）
- 実施コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- フェイルセーフ確認結果: 用語不一致・責務分離違反・固定値矛盾は **未検知**（検知時は `Hold`）。

### Phase 5 Proceed（Open化条件）
- 判定: **Ready**。
- Open化条件（全て必須）:
  1. `Improve external` 判定と公開runbook責務の境界が本文で追跡可能。
  2. `GoNoGoGate=Required` と `VerificationLevel=docs-check` が一致。
  3. `DecisionStatus=Fixed` / `DecisionQueueRef=N/A` が維持。
  4. フェイルセーフ3条件（用語・責務分離・固定値）違反なし。
- いずれか未達時は **Needs-decision** または **Hold** とし、Open化しない。

## Stream L security公開境界メモ整備（2026-04-28, 5Phase直列）

### Phase 1 Read（開始同期）
- Read同期: 本Issueの `Requirement meta I/F` / `SecurityGateImpact=public-exposure` / `Stop conditions` を再読。
- Read同期: security公開境界の責務分離（operations=実行runbook、security=統制、guidelines=運用判断補助）を再確認。
- スコープ固定: **編集対象は本Issueのみ**（指定外編集禁止）。

### Phase 2 Plan（AC/DoD不足提案 → 合意）
- AC不足提案:
  - AC-L1: 公開境界メモとして Audience/Goal/Public boundary/Next action を本Issue単体で追跡可能にする。
  - AC-L2: 役割語彙 `Security Officer / System Owner / Platform Operator` の一致確認を必須化し、不一致時は `Hold`。
  - AC-L3: 固定値（D1〜D4相当）は再定義せず、正本参照導線のみ記録する。
- DoD不足提案:
  - DoD-L1: Verifyで `validate_active_issue_memos.py --files <this file>` と `git diff --check` を記録する。
  - DoD-L2: Proceedを `Ready / Hold / Needs-decision` の3値で明記する。
- 合意記録: **上記 AC-L1〜L3 / DoD-L1〜L2 を本Runの合意済み基準として固定**。

### Phase 3 ADR/CDC（必要時のみ、CD&C先行）
- Read同期: `ADR handling rule` を再読。
- 判定: 本Runで新規の役割語彙差分・導線差分・固定値差分は発生なし。
- 結果: **CD&C追記なし / 新規ADR承認待ちなし**（承認待ちが発生した場合はこのPhaseで停止し、承認完了まで次Phaseへ進まない）。

### Phase 4 Execute（docs-only）
- 実施: Stream L（本節）を追記し、security公開境界メモの運用基準を5Phase直列で固定。
- 非実施: `04_Documentation/*` 本文改稿、他Issue編集、実装コード編集。

### Phase 5 Verify / Proceed（修復上限つき）
- Verifyコマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 修復ログ:
  - Repair-1: 未実施
  - Repair-2: 未実施
  - Repair-3: 未実施
  - Repair-4: **禁止（停止条件）**
- 競合判定: 競合なし（競合発生時は停止）。
- Proceed判定: **Ready**（security公開境界メモ整備を本Issue内で完了）。


## Stream E phase run（2026-04-29）

### 1) Read（Draft gate条件抽出）
- Draft gate確認: `Improve external`、`GoNoGoGate=Required`、`VerificationLevel=docs-check`。

### 2) Context / Decision / Consequences
- Context: operations は公開runbookだが security系文書と責務境界が近接。
- Decision: 分類は **Improve external 維持**。
- Consequences: Open化時は security/guidelines への導線を保持し境界ドリフトを抑止。

### 3) AC/DoD・Open化条件の明文化
- Open化条件: Audience/Goal/Boundary/Next action を1読で追跡可能であること。
- DoD: Proceed三値、Verify結果、停止条件（修復>3で停止）を維持。

### 4) Plan→Execute→Verify（自己修復）
- Plan/Execute: 本Issueメモのみ更新。
- Verify: docs-check方針維持、自己修復 0/3。

### 5) Proceed
- 判定: **Ready**。
- 理由: Open化判断に必要な情報が揃い、未承認確定化もない。

## Stream L strict serial run（2026-04-29, operations → security fixed）

### Phase 1 Read（開始時同期）
- Read同期: `AGENTS.md` Read Order・本Issue・`04_Documentation/operations.md` を再読し、`DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `GoNoGoGate=Required` を確認。
- 差分判定: 想定差分（役割語彙・固定値・公開境界）**なし**。差分発生時停止ルールを維持。

### Phase 2 ADR/CDC（必要時のみ）
- Context: operations は実行runbook責務、security側へ責務を越境しないことが厳密独立性の条件。
- Decision: 新規ADR不要（既存 `Improve external` 維持）。差分発生時のみ C/D/C を起票し承認完了まで停止。
- Consequences: 本フェーズは docs-only の同期ログ追記に限定できる。

### Phase 3 Plan
- 実行計画:
  1. 本Issueへ Stream L 記録を追記（allowlist内）。
  2. 直列順 `operations → security` を固定し、security編集は operations 完了後に開始。
  3. self-correction は 0〜3 回に制限し、4回目相当は停止。

### Phase 4 Execute
- 実施: operations lane の同期記録のみ更新。
- 非実施: `issue-HIL-RS-02-A3-operations-documentation-sync.md` を含む対象外ファイル編集、実装コード変更、公開安全境界の緩和。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-correction: 0/3（4回目相当は停止）。

### Phase 6 Proceed
- 判定: **Ready**（security lane へ直列遷移可）。
- 次順序: 固定どおり `DOC-OPS-05-13` を開始。


## Stream H DOC-OPS-05 serial update（2026-04-30）

### Phase 1 Read同期
- Read Order（00→02）と本Issue、対象Docを再読し、docs-only制約を確認。

### Phase 2 章ごとのAC定義
- AC固定: Audience / Goal / Non-goal / Public boundary / Related / GoNoGoGate / VerificationLevel(docs-check)。

### Phase 3 章単位更新（直列）
- 本Issueに対応する章のみを更新対象として直列処理し、未承認事項の確定化は行わない。

### Phase 4 docs-check / link-check
- `git diff --check` と `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md` を実行対象とする。
- 自己修復回数: 0/3（4回目相当はHold停止）。

### Phase 5 issue更新
- 判定: **Ready**（停止条件非該当、docs-only維持）。

## Stream G DOC-OPS-02 sync run（2026-04-30）

### Phase 1 Read同期
- `02_Architecture/design/strict_mode_exception_approval_flow.html` -> `02_Architecture/design/enterprise_architecture.html` -> `04_Documentation/operations.md` -> `04_Documentation/security.md` を固定順序で再読し、語彙・責務・固定値の一致を確認。

### Phase 2 Plan（AC/DoD補完）
- AC/DoD不足なしを確認。docs-only / 最小差分 / 未承認事項の非確定化を維持。

### Phase 3 Sync
- DOC-OPS-02の4観点（用語/役割/導線/固定値D1〜D4）で運用runbookの整合を再確認し、不一致ゼロを記録。

### Phase 4 Verify
- self-correction: 0/3。
- 判定: D1〜D4（4h / tenant+2h / 代理承認なし / 48h+15m/60m）と
  `Security Officer / System Owner / Platform Operator` の整合は維持。

### Phase 5 Proceed
- 状態: **Ready**（停止条件非該当）。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-11-04doc-operations.md` | `04_Documentation/operations.md` | 既存本文の Decision / Proposed classification を継承 |

### Phase 2: Plan（AC / DoD 統一テンプレ）
- AC（統一）
  - 読者タスク完遂性: Audience / Goal / Non-goal が追跡可能。
  - 用語統一: 役割語彙と判定語彙（Move internal / Improve external / GoNoGo）を統一。
  - 参照導線: Related ADR/Spec と対象04文書の相互参照を明記。
- DoD（統一）
  - 相互参照が明記される。
  - 品質ゲート（`docs-check` + `git diff --check`）が明記される。
  - 更新責務（Issue整備担当 / 04_Documentation改稿担当の分離）が明記される。

### Phase 3: Execute（標準セクション）
- 目的: DOC-OPS-05対象Issueを、公開境界を崩さず運用できる品質に正規化する。
- 範囲: 本Issue本文（`01_Plans/issues`）のみ。
- 非対象: `04_Documentation/**` 本文改稿、`03_Implement/**`、shared統合3ファイル。
- 検証観点: メタ項目充足 / 優先度矛盾なし / リンク表記整合 / docs-check一致。
- 停止条件: scope逸脱検知、自己修復4回目相当、未承認確定化要求。
- 並行実行可能フラグ: **No (security-lane serial)**。

### Phase 4: Verify（重複・矛盾・リンク）
- 重複Issue: 既存DOC-OPS-05連番内で対象重複なし（本Issue固有対象）。
- 優先度矛盾: `Priority=P2` 系列で整合（高優先度との衝突なし）。
- リンク切れ: Related ADR/Spec は既存記載を継承し、解決不能リンクは本パスでは未検出。
- 自己修復: 0/3（本更新時点）。

### Phase 5: Proceed（04_Documentation改訂担当への引継ぎ）
- 引継ぎメモ: 本Issueは「本文改稿を行わず、品質ゲートと参照導線を固定」済み。
- 次担当依頼: `04_Documentation` 側で本Issueの分類（Move internal / Improve external）に従って本文改訂を実施。
- ゲート条件: 改訂後は `docs-check` を再実行し、Issue側の分類・用語・導線と一致確認すること。


## Stream G dedicated run（2026-05-10）

### Phase 1 Read
- `04_Documentation/operations.md` を再読し、導線欠落（冒頭からの正本参照リンク不足）を確認。
- 役割分離（Security Officer / System Owner / Platform Operator）は本文中で散在し、一覧性が弱いことを確認。

### Phase 2 Plan
- 冒頭に「クイック導線」を追加して、Architecture→Documentation の固定順序を即時追跡可能にする。
- ロール責務を表形式で追加し、2者承認と実行責務分離を一目で確認できるようにする。
- 意味変更は行わず、可読性・導線・整合性のみを改善する。

### Phase 3 Execute
- `operations.md` に `0.0 クイック導線` と `0.0.1 ロールと責務分離` を追加。
- 定点レビュー日時を 2026-05-10 時点の運用表記へ更新（値の意味変更なし）。

### Phase 4 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 5 Proceed
- 判定: **Ready**。
- 未解決: 環境別チェックリスト（single-node / HA / air-gapped）は本Issueの既知ギャップとして継続委譲。

## Stream H serial completion log（2026-05-18）

### Phase 1: Read
- 本Issueと対応する `04_Documentation` 文書を再読し、docs-only と allowlist 制約を再確認。

### Phase 2: Plan
- 共通契約（Audience / Goal / Non-goal / Public boundary / Related）と品質ゲート（可読性・検証可能性・保守性）を適用。

### Phase 3: Execute
- 章構造・用語・相互リンク規約を統一し、各文書に「運用手順 / 判断基準 / 失敗時対応」を必須化。

### Phase 4: Verify
- `git diff --check` と issue memo validator（対象ファイル）を検証対象とする。
- self-correction: 0/3（4回目相当は Hold）。

### Phase 5: Proceed
- 判定: **Ready**（DOC-OPS-05 直列処理対象として継続可能）。

## 16) Open readiness gate（DOC-OPS-05 machine-check）

- Batch: `C (11-14)`
- GateStatus: `Conditional`（現時点のIssue StatusはDraftのため、Open化は本ゲートの充足を条件とする）
- DraftReasonClass: `open-trigger-not-executed`
- BlockingIssueIDs: `none`
- OpenTrigger:
  1. `Status` を Draft から Open へ変更。
  2. `Expected verification level` と `VerificationLevel` が `docs-check` で一致。
  3. `GoNoGoGate=Required` に対する判定条件（Ready/Hold/Needs-decision）が本文中で一意。
  4. `DecisionStatus=Fixed` の場合、`DecisionQueueRef` は `N/A` であること。
- MechanicalChecks:
  - `rg -n "^- Status:|Expected verification level|VerificationLevel|GoNoGoGate|DecisionStatus|DecisionQueueRef" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `rg -n "Open readiness:|状態分類:|Phase 5: Proceed" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- Proceed verdict (Phase 6): `Open可能（条件付き）`

## Stream G Documentation Ops log（2026-05-20, 5Phase + CDC）

### Phase 1 Read同期
- `02_Architecture/design/strict_mode_exception_approval_flow.html` → `02_Architecture/design/enterprise_architecture.html` → `04_Documentation/operations.md` → `04_Documentation/security.md` の固定順序で再読。
- DOC-OPS-02 の4観点（用語/役割/導線/固定値D1〜D4）を再確認。

### Phase 2 Context / Decision / Consequences
- Context: operations runbook の公開境界と security 文書群の導線整合を維持する必要がある。
- Decision: 役割語彙（Security Officer / System Owner / Platform Operator）と D1〜D4 は再定義せず、正本参照を維持する。
- Consequences: 公開境界の後退と未承認事項の確定化を防止し、docs-only で監査可能な更新に限定できる。

### Phase 3 用語・導線・公開境界
- 用語: 3ロール語彙の揺れゼロを確認。
- 導線: strict mode 正本→enterprise→operations→security の順を維持。
- 公開境界: 内部運用手順を公開文書へ持ち込まない方針を維持。

### Phase 4 Verify
- `rg -n "Security Officer|System Owner|Platform Operator|D1|D2|D3|D4|公開境界" 04_Documentation/operations.md 04_Documentation/security.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（docs-only / scope内 / 停止条件非該当）。
- 3回失敗停止ルール: 維持（未到達）。

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `operations`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-05-11` の公開境界を再確認。
- Decision: operations は運用者向け公開候補として、起動/停止/確認/共有前確認を扱い、組織固有承認履歴や内部計画を含めない境界を明記した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
