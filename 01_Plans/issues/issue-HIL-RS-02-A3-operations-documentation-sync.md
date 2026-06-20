# Issue Draft: HIL-RS-02 A3 Operations Documentation Sync（Stream G preflight）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Ready -> Hold -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Priority: P1
- Owner: Stream B（HIL-RS-02-A3 運用文書同期準備）
- Scope: `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`（docs planning only）
- Out of scope: 実装変更、allowlist外Issue/ADR編集、契約再定義、`04_Documentation/**` 本体編集
- Related ADR/Spec: `ADR-0027`, `ADR-0028`, `ADR-0039`, `02_Architecture/strict_mode_exception_approval_flow.md`
- Dependencies: `issue-HIL-RS-02-A1-governance-contract-hardening.md`（Done 2026-06-20）, `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

## Draft→Open 2026-06-20
HIL-RS-02-A3 Open化。A1 gate充足（HIL-RS-01-A1 Done + HIL-RS-02-A1 Done + pendingDecisionQueueCount=0 per ADR-0039）。
運用文書同期準備を開始可能。SafeMode不変条件維持。

## Contract Freeze Reference（read-only）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

## Stream G Protocol
- Required order: **Phase 1 Read → Phase 2 Plan（A1完了前提ゲート明文化）→ Phase 3 Execute（準備項目・受入条件先行定義）→ Phase 4 Verify（整合検証・修復上限3回）→ Phase 5 Stopper（A1未完了のまま実装へ進まない）**
- Verify repair loop: `<=3`
- Hard stop: pending bypass / fixed key rewrite / safeMode後退 / scope外編集

## Phase 1 Read
### Plan
- 対象2ファイルを再読し、A3 roleを「運用同期準備」に限定する。
### Execute
- 未決事項: `Approval Record pending`, `A1未完`, `Open gate未達`。
### Verify
- 未決事項が gate 判定式へ接続済みであること。
### Proceed
- Proceed=Yes

## Phase 2 Plan（A1完了前提のゲート明文化）
### Plan
- ADR-0027統治制約とA3本文を一致させる。
### Execute
- Context: A3は契約再定義ノードではない。
- Decision: `mock I/F preparation only` を維持し、契約変更要求を拒否する。
- Consequences: **A1 DoneまではDraft固定（Open化禁止）**。
### Verify
- C/D/C欠落なし、かつ「契約再定義しない」方針が明文化済み。
### Proceed
- Proceed=Yes（Pending注記維持）

## Phase 3 Execute（準備項目・受入条件の先行定義）
### Plan
- A3里程標を運用同期観点で固定し、AC/DoD不足を提案する。
### Execute
- M1: 用語同期（Security Officer / System Owner / Platform Operator）
- M2: 同期導線固定（`02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md`）
- M3: Gateログ・検証証跡の記録
### Verify
- 里程標がAC/DoDへ接続され、修復は3回以内であること。
### Proceed
- Proceed=Yes

## Phase 4 Execute
### Plan
- A3前倒し準備を行うが、A1依存解消までは状態遷移を行わない。
### Execute
- 変更はplanning記述のみ。`A1 Done未達時のA3 Open禁止` を明記維持。
### Verify
- allowlist内更新のみ、実装コード/04_Documentation本体は未変更であること。
### Proceed
- Proceed=Yes

## Phase 5 Stopper（A1未完了のまま実装へ進まない）
### Plan
- A1未完了時の停止条件を明文化し、実装着手禁止をゲート化する。
### Execute
- Stopper-1: `A1 Done未達` の間は planning以外の変更を禁止。
- Stopper-2: `fixedKeysDiff>0` / `pending bypass` / `scope violation` を即停止条件として維持。
- Stopper-3: `Current: Hold` を維持し、Open/In Progress遷移を禁止。
### Verify
- Stopper条件がGo/Hold/Stop判定と矛盾せず、修復回数が3回以内であること。
### Proceed
- Proceed=Hold（A1完了待ち）

## Draft解除条件（Draft -> Ready）
- [x] Scope が planning-only かつ allowlist内1ファイルに限定。
- [x] Contract Freeze Reference が read-only で固定され、再定義禁止が明記。
- [x] A1依存（Approval Record pending / A1未完 / Open gate未達）が gate に接続済み。
- [x] ADR C/D/C で「A3は契約再定義ノードではない」が固定。
- [x] Proceed 判定（Go/Hold/Stop）と Current=Hold が整合。

## Ready定義（実行開始条件）
- [x] Plan: M1-M3（用語同期・導線固定・証跡記録）が確定。
- [x] Execute: planning文面更新のみ、実装/04_Documentation本文編集なし。
- [x] Verify: DOC-OPS-02 4観点チェックを明示し、結果をGateへ反映可能。
- [x] Proceed: A1完了ログ未着時は Hold 維持、Open化しない。

## 依存切断条件（Ready維持のための独立性）
- [x] A1依存は状態判定（Go/Hold）にのみ反映し、本文契約の編集依存を持たない。
- [x] Stream Gで先行実施するのは「運用同期準備（語彙/導線/証跡）」のみ。
- [x] fixedKeysDiff==0 を維持する限り、未承認でも Draftへ逆戻しせず Ready+Holdで待機可能。

## 受入条件（Execute完了判定）
- [ ] AC-1: Status=Ready へ遷移し、Draft解除条件が明示される。
- [ ] AC-2: A1未完時は `Current: Hold` を維持し、Open化禁止を明記。
- [ ] AC-3: DOC-OPS-02の4観点が欠落なく保持される。
- [ ] AC-4: fixed key再定義・pending bypass・scope外編集が0件。

## 検証導線（Verify手順）
1. `rg -n "Status:|Lifecycle:|Draft解除条件|Ready定義|依存切断条件|Go:|Hold:|Stop:|Current" 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
2. `git diff -- 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
3. `git status --short`

## Ready判定
- 判定: **Ready + Hold（A1承認待ち）**
- 根拠: Draft解除条件を満たすが、A1承認未了のため Open化しない。


## Stop条件（Prompt G適用）
- A1固定値不一致（`fixedKeysDiff>0`）
- 共有資源競合（`sharedResourceFreeze`違反、または共有資源の二重更新要求）
- 承認前提崩壊（pending bypass / unrecorded approval inference / dual-control破綻）


## Stream E同期メモ（2026-05-07）
- DOC-OPS-02固定順（Architecture→Documentation→Plans→AGENTS）に合わせ、A3は documentation sync の準備状態で停止。
- 用語/役割/導線/固定値（D1〜D4）の同値確認のみ実施。
- A1承認完了ログ受領まで `Current: Hold` を維持し、Open昇格を行わない。

## Stream A proceed gate lock（2026-05-10）

### Dependency and status gate
- A3は `A1 -> A2 -> A3` 依存の末端であり、A1完了前は `Hold` 維持。
- `Current: Hold` を解除できるのは `a1Status=="Done" && pendingDecisionQueueCount==0` のみ。

### Contract read-only boundaries
- 参照対象: `freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`。
- A3側での再定義禁止: APIシグネチャ変更、最小型変更、監査イベント名変更。

### Mock usage（A3準備で許可）
- 許可: 用語・導線・証跡テンプレート整合確認。
- 不許可: 承認状態推測、A1契約値の補完確定、Open昇格判定代行。


## Stream C execution record（2026-05-10, Documentation/Ops）

### Phase 1: Read
- `02_Architecture/strict_mode_exception_approval_flow.md`（正本）と `04_Documentation/operations.md` / `security.md` / `security_operational_guidelines.md` の語彙・役割・導線・D1〜D4 を再確認。

### Phase 2: Plan
- AC/DoD不足として、`operations.md` 側に「監査導線クイックチェック（4観点+停止条件+証跡）」を追記する方針を固定。
- 品質ゲートを docs-only（`git diff --check` + `rg`照合 + `git status --short`）で先行定義。

### Phase 4: Execute
- 運用本文の契約再定義は行わず、runbook 側へ監査導線チェック手順を追加。
- `Current: Hold` は維持（A1完了まで Open/In Progress へ遷移しない）。

### Phase 5: Verify
- 4観点（用語/役割/導線/固定値）と停止語彙（`StoppedForClarification`）の一致を確認。
- 修復回数は 0/3（初回で収束）。

### Phase 6: Proceed
- 未確定論点（A1承認ログ未着）は保留のまま切り出し、推測補完は行わない。
- 判定: **Ready + Hold 維持**。


## Typecheck follow-up（2026-05-10, additional instruction）

- 実行コマンド: `cd 03_Implement/frontend && npm run typecheck`
- 結果: **Fail（exit code 2）**
- 失敗内容（scope外の既存不整合）:
  - `src/domain/hil_rs_client_apply.integration.test.ts(17,3)` `schemaVersion` が `Document` 型に存在しない。
  - `src/domain/hil_rs_client_apply.integration.test.ts(42,7)` `Document` を `DocumentV2` へ代入不可（`islands` 欠落）。
  - `src/domain/hil_rs_client_apply.integration.test.ts(43,7)` 同上。
- 判定: Stream C の編集許可範囲外（`03_Implement/**`）のため、本Issueでは修正を行わず、実装ストリームへ切り出して対処する。


## Stream B update（2026-05-10, HIL-RS-02-A3 運用文書同期準備）

### Read（対象ファイル最新状態確認）
- 対象を再確認: 本Issue草案（A3）と A3専用運用文書の同期準備メモのみを対象にし、A1/A2・README index・dashboard・実装コードは非対象。
- 現在状態: `Status: Hold（A1 Approval Pending）` を維持し、A1完了前に Open 化しない前提を再固定。
- 未確定: A1承認ログ未着、decision queue の Pending 解消未確認。

### Plan（A1未完前提で「Openしない準備項目」のみ定義）
- 準備項目P1: DOC-OPS-02の4観点（用語/役割/導線/固定値）をA3側チェックリストとして明文化。
- 準備項目P2: Verify時の証跡コマンドを docs-only に限定（`rg`, `git diff --check`, `git status --short`）。
- 準備項目P3: A1未完了時の遷移を `Ready + Hold` に固定し、`Open/In Progress` への遷移条件を A1完了ログ受領に限定。

### Execute（docs草案・検証手順・ロールバック）
- docs草案:
  - A3は「運用文書同期準備」専任であり、契約再定義ノードではないことを明記。
  - 承認待ち論点を `Context / Decision / Consequences` で保持し、推測補完を禁止。
- 検証手順（docs-only）:
  1. `rg -n "Status:|Current: Hold|Open化|Context:|Decision:|Consequences:" 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
  2. `git diff --check -- 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
  3. `git status --short`
- ロールバック:
  - `git restore -- 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
  - ロールバック後に `Current: Hold` と C/D/C の記録保持を再確認。

### Verify（AC/DoD + リンク整合）
- AC/DoD確認:
  - AC-2（A1未完時 Hold維持）を最優先ゲートとして再確認。
  - DoDとして docs-only 範囲逸脱が 0 件であることを確認。
- リンク整合:
  - 参照リンクは `ADR-0027`, `ADR-0028`, `02_Architecture/strict_mode_exception_approval_flow.md` のまま維持。
  - A1/A2本文への直接編集導線を追加しない（read-only参照のみ）。

### Proceed（A1完了までDraft/Conditional維持）
- 判定: **Ready + Hold（Conditional）**。
- A1完了条件未達のため、A3は Draft/Conditional の運用を維持し、Open化を実施しない。

### Approval pending record（Context / Decision / Consequences）
- Context: A1の承認・固定値整合が未確定であり、A3がOpen化するとDOC-OPS-02の固定順序に対して誤同期リスクがある。
- Decision: A3は `Current: Hold` を維持し、実施は「準備項目の文書化・検証手順・ロールバック定義」に限定する。
- Consequences: A1完了ログ受領までは運用本文のOpen遷移を停止。承認待ちの論点を明示的に残し、後続で可逆に再開できる。

## Stream D docs-sync readiness handoff（2026-06-13）

### Sync targets（準備対象 / 本Streamでは編集しない）
- `04_Documentation/operations.md`
- `04_Documentation/security.md`
- `04_Documentation/data_handling.md`
- `04_Documentation/narratives.md`
- 必要時のみ `03_Implement/frontend/docs/e2e_testing.md` を開発者向け検証手順として参照する。

### Open化条件
- A1 Done 証跡が存在する。
- `pendingDecisionQueueCount==0`。
- `Approval Record` と held items が人間承認で解消済み。
- DOC-OPS-02 の4観点（用語、役割、導線、固定値）を A3の受入条件へ転記できる。

### Stop conditions
- A1未完了のまま `04_Documentation/` 本文更新を要求する。
- `Pending` を承認済みとして説明する。
- SafeMode/share/export 境界を弱める運用文書にする。
- Frontend実装詳細をDocs同期の前提として確定する。

### Handoff classification
- Stream D 判定: **Docs Stream handoff ready / Draft-Hold維持**。
- 本Streamでは同期対象とStop条件のみを記録し、`04_Documentation/` は編集しない。
