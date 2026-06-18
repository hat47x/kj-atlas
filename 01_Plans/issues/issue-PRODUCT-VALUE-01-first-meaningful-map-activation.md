# Issue Draft: PRODUCT-VALUE-01 初回価値実感と最初の意味ある配置

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Product Value contract steward; accountable owner remains Productization Program Owner)
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `04_Documentation/installation.md`, `04_Documentation/operations.md`
- Related Backlog: `PRODUCT-VALUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-VALUE-01
- RequirementStatement: 初回利用者が、サンプルまたは自分のメモから、カード、まとまり、保留点を含む最初の意味ある配置へ迷わず到達できるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ブラウザでkj-atlasを初回利用する / 操作=サンプルを開く、または短いメモを入力してカード化し、少なくとも1つのまとまりまたは保留点を作る / 期待結果=「何を置き、何をまだ決めていないか」が画面上で分かる / 除外=高度なAI提案、自動分類、クラウド同期。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / import-sanitize
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending（`ADR-0032` はAccepted済み。Open前の反復E2E手順、fixture、証跡保存先が未固定）
- DecisionQueueRef（未確定時の参照先）: `PRODUCT-QA-01` value gate evidence packet / `MVP-EXIT-01`

## 1) 課題 / Problem statement

- 現在の製品化issueは画面入口、パネル、共有前確認を扱っているが、利用者が最初に価値を実感する「意味ある配置」までの完了条件が明確でない。
- kj-atlas の価値は、単に文書を開くことではなく、考え途中の素材をカード、まとまり、保留点として扱えることにある。
- 初回成功経路が未定義のままだと、機能説明やサンプル表示はあっても、利用者が次の作業へ進む確信を得にくい。

## 2) 背景 / Context

- `ADR-0031` は開始/文書入口を製品化UIの基本領域にした。
- `ADR-0032` は V0/V1 として、開始と外在化を価値ループに位置づけた。
- `domain.md` は、保留、違和感、可逆性を本プロダクトの中核概念として定義している。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 初回でカードと保留点を作れない場合、意味の保留という価値が体験されない。
- 安全（THREAT_MODEL / SafeMode）: 初回取り込み時に検証とSafeMode状態を見せることで、不正ファイルや意図しない共有を避けやすい。
- 企業・行政要件（enterprise_architecture）: 教育コストを下げ、短い導入説明で標準操作に入れることは組織導入で重要である。
- 後方互換（schemas）: 既存document/view/packを壊さず、開始導線と受入シナリオを追加する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 初回開始導線、サンプル、短いメモ入力、カード化、保留点表示、公開文書の導入手順。
- 変更の最小単位:
  - 「最初の意味ある配置」を、カード3件以上、まとまりまたは保留点1件以上、保存または共有前確認へ到達可能な状態として暫定定義する。
  - サンプルまたは入力例から同じ経路を確認できるE2Eを用意する。
- 非目標:
  - AIによる自動分類。
  - 利用者行動の個人追跡。
  - アカウントやクラウド履歴の実装。

## 5) 受入条件 / Acceptance criteria

- [ ] 初回利用者が、サンプルまたは短いメモ入力からカードを作れる。
- [ ] 少なくとも1つのまとまり、関係、または保留点を作る操作が画面上で分かる。
- [ ] まだ決めていないことが、失敗や未完了ではなく作業状態として見える。
- [ ] SafeModeと取り込み検証状態が初回経路の中で確認できる。
- [ ] `Tab` / `Enter` / `Space` で初回経路の主要操作へ到達できる。
- [ ] 公開文書の導入手順が、この初回成功経路と矛盾しない。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 「最初の意味ある配置」の最小状態をUI/データ/文書で定義する。
- [ ] T2 サンプルまたは短い入力例からカード、まとまり、保留点を作るワイヤーフローを作成する。
- [ ] T3 初回経路をキーボード操作と小画面で確認する。
- [ ] T4 Playwrightで代表初回経路をE2E化する。
- [ ] T5 `installation.md` / `operations.md` / `public_index.md` の導入手順と同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test --reporter=line`
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `git diff --check -- 01_Plans 02_Architecture 03_Implement/frontend 04_Documentation`
- 期待結果:
  - 初回経路がE2Eで再現でき、サンプルまたは短い入力から最初の意味ある配置へ到達できる。
- 未実施時の理由・代替検証:
  - UI実装前は、Playwright操作計画、スクリーンショット、文書上の受入シナリオで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: サンプルを表示するだけにする。利用者が自分の素材で価値を得る経路が残らないため採用しない。
- 代替案B: AI自動分類を初回価値にする。LLMなしの既定構成で価値が成立しなくなるため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 初回導線が長くなり、利用者が作業面へ入る前に疲れる。
- 影響範囲: frontend shell、sample data、公開文書、E2E。
- ロールバック手順: 初回価値経路をサンプル専用の補助導線へ戻し、既存の文書入口は維持する。

## 10) Additional context

- ADR化が必要になる条件: 初回経路をルーティング、ローカル履歴、ユーザープロファイルの仕様として固定する場合。


## 11) 価値実現シリアル（Hypothesis → Action → Evidence → Decision）

- 価値仮説: 初回利用者は「最初の意味ある配置」を10分以内に完了できると、継続利用意図が成立する。
- 行動:
  1. サンプルを開く、または短いメモを入力する。
  2. カードを3件以上作成する。
  3. まとまりまたは保留点を1件以上作る。
  4. 保存または共有前確認へ遷移する。
- 証拠:
  - E1: 初回経路E2E結果（成功/失敗、所要時間）。
  - E2: 画面上で「カード3+ / まとまりor保留1+」を確認できるスクリーン状態。
  - E3: SafeMode/取り込み検証表示の確認結果。
- 判定（Go/No-Go）:
  - Go: E1〜E3が全て取得され、E2Eで初回経路成功率が80%以上（5試行中4成功以上）。
  - No-Go: 証拠欠落、または初回経路成功率が80%未満。

## 12) KPI定義（定義可能・再測定可能・比較可能）

- KPI-01 `first_meaningful_map_success_rate`
  - 定義: 初回経路試行における成功試行数 / 総試行数。
  - 再測定: 同一E2Eシナリオを5試行実行する。
  - 比較: 変更前後で成功率差分を比較する。
- KPI-02 `time_to_first_meaningful_map_p50`
  - 定義: 初回経路完了時間の中央値（秒）。
  - 再測定: 同一入力条件で時間計測を取得する。
  - 比較: 版間で中央値を比較する。
- KPI-03 `safe_entry_visibility_rate`
  - 定義: 初回経路でSafeMode/検証表示を確認できた試行割合。
  - 再測定: E2Eまたは手動受入で確認項目を固定する。
  - 比較: UI変更前後で割合を比較する。


---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。


## Stream I 要件契約固定パック（2026-05-18）

### Phase 1: Read同期サマリ
- 重複論点: 画面導線の分かりやすさ、SafeMode境界、検証証跡要件。
- 曖昧論点: Open化の判定条件と、依存関係が契約依存か実装依存かの境界。
- 欠落補完: 価値→要件→受入→測定の追跡行と、Draft→Open判定を明文化。

### Phase 2-3: ADR要素 + 要件契約
| Context | Decision | Consequences |
| --- | --- | --- |
| 上流価値定義（ADR-0001/0031/0032）を実装入口へ接続する必要がある。 | AC/DoDを機械検証可能な粒度で固定し、未確定はDecision Queueへ隔離する。 | 下流実装Streamは要件の再発明をせず、検証可能なIssue単位で着手できる。 |

### 価値→要件→受入→測定 対応表（最小）
| 価値仮説 | 要件（Requirement） | 受入条件（AC） | 測定（Evidence/KPI） |
| --- | --- | --- | --- |
| 利用者が安全に判断を共有できる。 | SafeMode境界を保持し、共有前確認を必須化する。 | SafeMode/公開範囲/未レビュー状態を実行前に提示できる。 | docs-check + E2E記録 + 文言一致確認。 |
| 要件から実装へ手戻りなく移行できる。 | AC/DoDをOpen前に固定し、未確定はPending化する。 | Draft→Open条件を満たしたIssueのみ実装に着手する。 | checklist充足率、No-Go件数、Pending解消件数。 |

### Phase 4: Draft→Open 条件（要件側ゲート）
- [ ] `DecisionStatus=Fixed` の要求のみでACが評価可能（PendingはDecision Queueへ退避済み）。
- [ ] 依存が `契約依存`（schema/api/policy/ops）と `実装依存`（UI/Backend/E2E）に分離されている。
- [ ] Validation plan のコマンドがこのIssue本文だけで再実行可能。

### Phase 5-6: Verify / Proceed 引き継ぎ条件
- Verify合格条件: 価値仮説とACの1対1追跡が可能で、非検証要件が残っていない。
- Proceed条件: 実装ストリームが「どのACをどのテストで満たすか」を追加解釈なしで決定できる。
- フェイルセーフ: 上流価値定義との矛盾・非検証要件・競合編集を検出した場合はOpen化を停止する。

## Open化判定メタ（Draft gate解除条件）

### Open化に必要な最小条件（全件必須）
- [ ] O-OPEN-01: `Owner` が `TBD` ではなく、実行責務者（個人またはロール）に確定している。
- [ ] O-OPEN-02: 依存Issue/ADRごとに `依存待ち理由` と `再開条件` が1:1で明示されている。
- [ ] O-OPEN-03: `Acceptance criteria` と `Validation plan` が `Expected verification level` と一致している。
- [ ] O-OPEN-04: docs-only範囲外の要求が本文に混入していない（本memoの範囲と矛盾しない）。

### 依存待ち理由（未解消時は Draft 維持）
| Dependency | 依存待ち理由 | 再開条件 | Owner |
|---|---|---|---|
| 上位ADR/関連Issue | 上位合意または境界仕様の最終確定待ち | 参照先に承認IDまたは確定コミットを追記 | Platform Architecture Owner / 各Issue Owner |
| QA検証経路 | `e2e`/`integration` の実行経路と証跡フォーマット未固定 | 実行経路（Compose/SQLite/例外）を1件固定し、判定ログ形式を定義 | QA Lead |
| 実行責務 | 実装担当とレビュー担当の分離未確定 | RACI（R/A）を本文に追記し通知記録を残す | PM/Triage |

### Proceed / Stop
- Proceed（Open化可）: O-OPEN-01〜04がすべて充足。
- Stop（Draft維持）: 依存先不明 / Status正規化不能 / 競合ファイル検出時は更新停止し、理由を `Additional context` に記録。



## Stream H Contract Finalization (2026-05-20)

### Scope confirmation
- Stream H dedicated; plan/ADR layer only; no implementation code edits.
- Target backlog: `MVP-EXIT-01` / `PRODUCT-VALUE-01..03` only.

### C/D/C lock (Context / Decision / Consequences)
| Context | Decision | Consequences |
| --- | --- | --- |
| PRODUCT-VALUE-01 requires Open-ready contract quality before downstream execution. | AC/DoD/KPI/audit fields are locked for docs-only verification first. | Downstream streams can execute without re-interpreting value intent. |

### KPI + audit scorecard mapping
- KPI field quality gate: definition / formula / evidence / re-measurement must all exist.
- Audit field quality gate: `reviewer`, `date`, `artifact id`, `decision`, `re-decision condition` must be explicit.

### AC / DoD final lock
- [ ] AC-F1 Hypothesis→Action→Evidence→Decision chain is explicit.
- [ ] AC-F2 Go/No-Go rule is explicit and binary-decidable.
- [ ] AC-F3 KPI definitions are re-measurable by docs-only procedure.
- [ ] DoD-F1 No cross-stream implementation dependency is required for contract validation.
- [ ] DoD-F2 Safety boundary wording (SafeMode/share-export/review attribution) is consistent with ADR-0032.

### Verify (non-dependency)
- Result: Contract validation is executable without waiting for other stream code merges.
- Reason: Inputs are issue text completeness and evidence schema only.

### Self-correction (<=3)
1. Normalized gate terms to `Go / Conditional Go / No-Go`.
2. Removed ambiguous wording that implied implementation readiness was required at this phase.
3. Added explicit audit metadata requirements for approval traceability.

### Approval-wait packet
- This section + ADR-0032 Stream H block are the approval bundle for PRODUCT-VALUE-01.

## Draft Gate Assessment 2026-05-23: Open readiness

- Assessment scope: 計画層のreadiness確認のみ。`Status: Draft` は維持し、実装着手や公開文書更新はこの追記では行わない。
- Gate result: Draft維持。`DecisionStatus=Pending` と `Owner: TBD` が残っており、Open化は時期尚早。
- Proposed RACI: R=Product Value Stream Lead（未割当）, A=Productization Program Owner, C=QA Lead / Platform Architecture Owner, I=Documentation Maintainer。CodexはOwner確定までissue本文と証跡パックの整備を支援する。
- O-OPEN status:
  - O-OPEN-01: Blocked. `Owner` が `TBD` のため、実行責務者をロールまたは個人で確定する必要がある。
  - O-OPEN-02: Partial. ADR-0032の価値実現モデル、ADR-0031の開始導線、E2E証跡経路の依存は見えているが、各依存の再開条件がまだ本文上で完結していない。
  - O-OPEN-03: Partial. ACとValidation planはいずれもe2e前提だが、5試行中4成功以上を測る具体シナリオ、入力fixture、画面状態の保存先が未固定。
  - O-OPEN-04: Pass for assessment. この追記はOpen判定の整理であり、docs-only範囲外の実装要求を追加しない。
- 契約依存:
  - `ADR-0032`: 「最初の意味ある配置」を価値実感のGo/No-Go単位としてFixedにする根拠。
  - `ADR-0031`: 初回入口、文書入口、SafeMode表示の画面配置方針。
  - `02_Architecture/value_traceability.md`: 価値仮説、受入条件、KPIの追跡表。
- 実装/証跡依存:
  - 初回利用の入力fixture（サンプルまたは短いメモ）と、カード3件以上、まとまりまたは保留点1件以上を確認するE2E。
  - SafeMode/取り込み検証状態が初回経路内で見えることを示すスクリーンショットまたはPlaywright trace。
- Next action:
  - `Owner` 確定後、初回成功経路のE2Eシナリオ名、fixture名、証跡保存先を本文へ追記する。
  - ADR-0032でDecisionStatusをFixedにできる承認IDまたは確定コミットを得るまではOpen化しない。

## Draft Gate Reassessment 2026-05-27: owner fixed, ADR-0032 still blocking Open

- Assessment scope: 計画層のDraft維持理由を、担当未確定ではなくADR-0032承認待ちと証跡経路の最終固定へ絞り込む。
- Gate result: **Draft維持**. OwnerはCodexの契約・証跡整備責務として確定したが、`DecisionStatus=Pending` と `ADR-0032` Proposed が残るためOpen化しない。
- RACI:
  - R: Codex (Product Value contract steward)
  - A: Productization Program Owner
  - C: QA Lead / Platform Architecture Owner / Documentation Maintainer
  - I: Frontend Lead
- O-OPEN status:
  - O-OPEN-01: Pass. OwnerはCodexに確定し、最終説明責任はProductization Program Ownerに分離した。
  - O-OPEN-02: Partial. `ADR-0032` がAcceptedまたは明示承認されるまでは価値ゲートの正本化が未完了。
  - O-OPEN-03: Partial. `realistic_user_journey_expansion.spec.ts` を主経路にする方針は固定したが、5試行中4成功以上を測る反復実行手順と証跡保存先が未固定。
  - O-OPEN-04: Pass. 本更新は契約整理であり、実装変更や公開文書変更を直接要求しない。
- Fixed evidence route candidate:
  - 初回価値シナリオ: `e2e/realistic_user_journey_expansion.spec.ts`
  - 補助viewport/focus確認: `e2e/header_toolbar_layout.spec.ts`
  - SafeMode/share確認: `src/ui/SharePanel.test.ts` と代表E2Eの共有前確認ステップ
  - 公開文書同期: `04_Documentation/public_index.md`, `installation.md`, `operations.md`, `acceptance_check.md`
### Evidence route refinement 2026-06-02

This refinement keeps `Status: Draft`. It does not authorize frontend implementation, public documentation changes, or release approval. Its purpose is to make the first meaningful map value gate executable once `ADR-0032` or an explicit Productization Program Owner approval allows the issue to move to Open.

Minimum representative scenario:

1. Start from either the bundled sample or a short user memo with 3 to 5 claims.
2. Create at least 3 cards without requiring advanced settings or AI automation.
3. Create at least 1 meaningful grouping, relation, or hold point that the user can see on the map.
4. Confirm that SafeMode/import validation status is visible before any share or export action.
5. Reach save, review, or share-preflight without reading internal project documentation.

Required evidence packet before Open:

| Evidence item | Required content | Gate handoff |
| --- | --- | --- |
| Scenario fixture | Input text/sample name, expected cards, expected grouping or hold point | `PRODUCT-QA-01` V0/V1 |
| Mouse operation trace | Click path from first screen to cards/grouping/hold point | G2 / G4 |
| Keyboard operation trace | `Tab`, `Enter`, and `Space` reach the same core path | G2 / G4 |
| Safe entry evidence | Screenshot or trace showing SafeMode and import validation state | G1 / G5 |
| Decision record | Go/Conditional Go/No-Go and remaining blocker | `MVP-EXIT-01` |

No-Go conditions for this value gate:

- The user must read architecture, AGENTS, or internal issue text to complete the first path.
- The first path creates only isolated cards and no visible grouping, relation, or hold point.
- SafeMode or import validation status is hidden until after a share/export action.
- The scenario cannot be replayed with a stable fixture and saved evidence.

- Reopen/Open condition:
  - `ADR-0032` Accepted は充足済み。以後はProductization Program Ownerが本Issueの証跡パケットをOpen前提として承認する。
  - 反復E2E手順、入力fixture、画面状態の保存先が本文で固定される。
  - 上記完了後、StatusをOpenへ変更し、`PRODUCT-QA-01` のValue Gate V0/V1へ戻す。

## Current status sync 2026-06-03: ADR accepted, evidence route still pending

- Current decision source:
  - `ADR-0032-product-value-realization-model.md` is `Accepted` as of 2026-05-31.
  - `ADR-0040-domain-expression-first-class-strategy.md` records the Maintainer delegated decision that breaks the previous `ADR-0032 Proposed` loop.
- Current gate result: **Draft維持**. The value model itself is no longer waiting on ADR acceptance, but this issue still needs a fixed, replayable evidence route before Open.
- Remaining blocker now:
  - a representative first-run fixture or sample name;
  - expected card/grouping/hold-point state;
  - mouse and keyboard operation traces;
  - screenshot or trace storage location;
  - `PRODUCT-QA-01` and `MVP-EXIT-01` decision record linkage.
- This sync does not authorize implementation, public documentation publication, or release approval.

## Evidence route update 2026-06-04: representative keyboard trace candidate

- Candidate: `codex/keyboard-operation-evidence-20260604`
- Status impact: **Draft remains**. This update adds a replayable keyboard-operation evidence candidate but does not by itself open the value gate.
- Evidence added:
  - `03_Implement/frontend/e2e/keyboard_release_candidate_flow.spec.ts` covers a keyboard-only route from the first-run start panel to sample loading, search, card selection, critique memo input, share preflight, close, and focus return.
  - `03_Implement/frontend/src/canvas/CanvasShell.tsx` no longer lets global Space-pan handling suppress Space activation for focused controls.
- Evidence packet mapping:
  - Keyboard operation trace: partially satisfied for the representative route.
  - Scenario fixture: partially satisfied by `doc_keyboard_release_candidate`; the fixture still needs product-owner acceptance as a meaningful first-map scenario.
  - Safe entry evidence: partially satisfied by SafeMode copy in the share preflight; screenshot/trace storage remains pending.
  - Decision record: linked through `PRODUCT-QA-01` and `MVP-EXIT-01` gate records dated 2026-06-04.
- Remaining blockers before Open:
  - Productization Program Owner must accept the representative sample/fixture as value-bearing rather than merely operability-bearing.
  - Mouse trace, screenshot/trace bundle location, and first-map grouping/hold-point expectations remain incomplete.
  - Full shipment still depends on `PRODUCT-QA-01` release gates, including screenshots, full regression, Compose startup, and final program approval.
## Evidence route update 2026-06-04: first meaningful map mouse trace candidate

- Candidate branch: `codex/first-value-mouse-evidence-20260604`
- Status impact: **Draft remains**. This update adds a replayable mouse-operation evidence candidate, but it does not by itself open the value gate.
- Evidence added:
  - `03_Implement/frontend/e2e/first_meaningful_map_mouse_flow.spec.ts` covers a mouse path from the first-run start panel to sample loading, two-card selection, and first visible island creation.
- Evidence packet mapping:
  - Scenario fixture: partially satisfied by `doc_first_meaningful_map_mouse`.
  - Mouse operation trace: partially satisfied for the representative route.
  - Expected grouping/hold-point state: partially satisfied by `Island 1` containing the two selected first-value cards.
  - Keyboard operation trace: covered separately by #2312, which is now part of mainline evidence.
  - Safe entry evidence and screenshot/trace storage remain pending.
- Remaining blockers before Open:
  - Productization Program Owner must accept the fixture and `Island 1` grouping as a value-bearing first-map scenario.
  - Safe entry screenshot/trace bundle location and decision linkage into `PRODUCT-QA-01` / `MVP-EXIT-01` remain incomplete.
  - Full shipment still depends on release gates, screenshots, full regression, Compose startup, and final program approval.

## Mainline evidence intake 2026-06-04: keyboard and mouse traces landed

- Candidate mainline: `origin/main@f04c45c473422047472af35cec1c431b835f621d`
- Status impact: **Draft remains**. The required replayable keyboard and mouse traces are now on `main`, but this issue still needs human product-value acceptance and a stable screenshot/trace bundle location before Open.
- Evidence now canonical on `main`:
  - #2312 merged `03_Implement/frontend/e2e/keyboard_release_candidate_flow.spec.ts`, covering keyboard-only sample opening, search, card selection, critique memo input, share preflight, close, and focus return.
  - #2313 merged `03_Implement/frontend/e2e/first_meaningful_map_mouse_flow.spec.ts`, covering mouse sample opening, two-card selection, `Create Island`, and visible `Island 1` confirmation.
- Evidence packet status:

| Evidence item | Current status | Remaining Open blocker |
| --- | --- | --- |
| Scenario fixture | Partially satisfied by `doc_keyboard_release_candidate` and `doc_first_meaningful_map_mouse`. | Productization Program Owner must accept these fixtures as value-bearing first-map scenarios, not only operability fixtures. |
| Mouse operation trace | Satisfied for the representative route by #2313. | Confirm that `Island 1` with two selected first-value cards is the intended first meaningful grouping/hold point. |
| Keyboard operation trace | Satisfied for the representative route by #2312. | UX reviewer must accept the Tab/Enter/Space path as natural enough for release-candidate operation. |
| Safe entry evidence | Partially satisfied by SafeMode/share-preflight visibility in the keyboard route. | Store or reference a first-value-specific screenshot/trace bundle that shows SafeMode, import/sample entry state, and the resulting first island. |
| Decision record | Partially satisfied by 2026-06-04 PRODUCT-QA / MVP-EXIT evidence records. | Final product-value gate decision must explicitly cite this issue after human fixture, screenshot, and grouping acceptance. |

- Next human task queue:
  - H-PV1: Productization Program Owner reviews both fixtures and decides whether they represent the promised first value moment for a standard user.
  - H-PV2: UX reviewer confirms that the keyboard and mouse paths are natural enough for a representative release-candidate workflow.
  - H-PV3: QA Lead approves where the first-value screenshot/trace bundle will live and what file names or artifact references must be cited from this issue.
- No ADR is needed for this intake. ADR routing is required only if the accepted first-value scenario changes the product value model, release authority, SafeMode/share policy, or first-run product boundary.

## Mainline E2E rerun 2026-06-06: first-value mouse and keyboard traces

- Candidate mainline: `origin/main@762aad281792a508034d0ba9715c77d2432d84b2`.
- Status impact: **Draft remains**. This rerun proves the representative traces are executable on current `main`; it does not replace human product-value acceptance, release screenshots, Compose startup, or final program approval.
- Environment note: the Codex host did not expose `npm` or PATH `node.exe` for this run. Vite and Playwright were executed with bundled Node.js:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`
  - Vite was started directly with `node .\node_modules\vite\bin\vite.js --host 127.0.0.1 --port 4173`.
- Verification command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/keyboard_release_candidate_flow.spec.ts e2e/first_meaningful_map_mouse_flow.spec.ts --reporter=line`
- Result: **pass, 2 tests**.

### Evidence packet update

| Evidence item | Current status after rerun | Remaining Open blocker |
| --- | --- | --- |
| Scenario fixture | Reconfirmed executable for `doc_keyboard_release_candidate` and `doc_first_meaningful_map_mouse`. | Productization Program Owner must accept the fixtures as value-bearing first-map scenarios. |
| Mouse operation trace | Reconfirmed pass for sample open, two-card selection, `Create Island`, and visible `Island 1`. | Confirm that `Island 1` with the two first-value cards is the intended first meaningful grouping/hold point. |
| Keyboard operation trace | Reconfirmed pass for sample open, search, card selection, critique memo, share preflight, close, and focus return. | UX reviewer must accept the Tab/Enter/Space path as natural enough for representative operation. |
| Safe entry evidence | Reconfirmed through the keyboard route's SafeMode share-preflight assertion. | QA Lead still needs a release evidence bundle or screenshot reference that can be cited from this issue. |
| Decision record | This section adds a current-main rerun record. | Final Open decision must cite H-PV1/H-PV2/H-PV3 outcomes. |

- No ADR is needed for this rerun. ADR routing remains limited to changes in product value model, release authority, SafeMode/share policy, or first-run product boundary.

## Mainline E2E rerun 2026-06-07: keyboard release-candidate trace

- Candidate mainline: `origin/main@14b2d9d44cbae54aee10ab9f13e3396a3f153035`.
- Status impact: **Draft remains**. This rerun proves the representative keyboard trace is still executable on current `main`; it does not replace human product-value acceptance, release screenshots, Compose startup, or final program approval.
- Environment note: the Codex host did not expose `npm` or PATH `node.exe` for this run. Vite and Playwright were executed with bundled Node.js:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`
  - Vite was started directly with `node .\node_modules\vite\bin\vite.js --host 127.0.0.1 --port 4173`.
- Verification command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/keyboard_release_candidate_flow.spec.ts --reporter=line`
- Result: **pass, 1 test**.

### Evidence packet update

| Evidence item | Current status after rerun | Remaining Open blocker |
| --- | --- | --- |
| Keyboard operation trace | Reconfirmed pass for sample open, search, card selection, critique memo, share preflight, close, and focus return. | UX reviewer must accept the Tab/Enter/Space path as natural enough for representative operation. |
| Safe entry evidence | Reconfirmed through the keyboard route's SafeMode share-preflight assertion. | QA Lead still needs a release evidence bundle or screenshot reference that can be cited from this issue. |
| Decision record | This section adds a current-main rerun record and is synchronized into `PRODUCT-QA-01`. | Final Open decision must cite H-PV1/H-PV2/H-PV3 outcomes. |

- No ADR is needed for this rerun. ADR routing remains limited to changes in product value model, release authority, SafeMode/share policy, or first-run product boundary.

## Fixture manifest 2026-06-17: PV01 first meaningful map evidence packet entry

- Candidate mainline: `origin/main@4fe6740678dd970a18eacab094ec4e99c53496c5`.
- Fixture source: `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts`.
- Fixture builder: `buildFirstMeaningfulMapDocument()`.
- Fixture document ID: `doc_first_meaningful_map_mouse`.
- Representative E2E: `03_Implement/frontend/e2e/first_meaningful_map_mouse_flow.spec.ts`.
- Status impact: **Draft remains**. This manifest names the reusable fixture entry for the PV01 evidence packet; it does not create Productization Program Owner / QA Lead acceptance, release screenshots, or shipment approval.

### Evidence packet mapping

| Evidence item | Manifest status | Remaining Open blocker |
| --- | --- | --- |
| Scenario fixture | Named and stored in `product_value_fixtures.ts`; default cards are `first value user problem`, `first value observation memo`, and `first value decision anchor`. | Productization Program Owner must accept this as a value-bearing first-map scenario for a standard user. |
| Mouse operation trace | Existing E2E opens the sample, selects the first two cards, creates `Island 1`, and verifies the selection context. | UX reviewer must accept the mouse route as natural enough for release-candidate evidence. |
| Keyboard operation trace | Still covered by the separate keyboard release-candidate route, not by this PV01 fixture builder. | Decide whether the PV01 packet can cite the existing keyboard route or needs a fixture-specific keyboard trace. |
| Safe entry evidence | Not added by this manifest. | QA Lead still needs screenshot or trace evidence showing SafeMode/import/sample-entry state with this fixture. |
| Decision record | This section provides the fixture identity that Product QA and MVP-EXIT can cite later. | Final Open decision must cite human acceptance and the screenshot/trace bundle location. |

- No ADR is needed for this manifest. ADR routing remains limited to changes in the first-value definition, release authority, SafeMode/share policy, first-run product boundary, or fixture meaning.

## First-value share preflight evidence 2026-06-19

- Candidate mainline: `origin/main@bd7e7ee35275b25f0f17defe02cbde619dbaa0a8`.
- Fixture: `buildFirstMeaningfulMapDocument()` / `doc_first_meaningful_map_mouse`.
- Representative E2E: `03_Implement/frontend/e2e/first_value_share_preflight.spec.ts`.
- Screenshot: `04_Documentation/assets/screenshots/product-value-first-island-share-preflight.png`.
- Automated evidence:
  - The start panel exposes `SafeMode: ON` before the user opens the sample.
  - The user selects two cards and creates the first visible island.
  - Share & Reproduce continues to show SafeMode ON, excludes unreviewed drafts, and reports 5 remaining review signals.
  - The preflight reports 2 unreviewed cards, 3 unknown claims, no critique targets, and no evidence links, contradictions, or evidence gaps.
- Verification result: targeted Playwright **1 passed**; the Product Value capture script regenerated all six screenshots.

### Evidence packet update

| Evidence item | Current status after this slice | Remaining Open blocker |
| --- | --- | --- |
| Scenario fixture | Replayed from start panel through first island and share preflight with one deterministic fixture. | Productization Program Owner must accept the fixture as a meaningful first-value scenario. |
| Mouse operation trace | Existing first-island E2E remains available. | UX reviewer must accept the route as natural for standard users. |
| Keyboard operation trace | Existing keyboard release-candidate flow remains available. | Decide whether separate-fixture keyboard evidence is sufficient for PV01 acceptance. |
| Safe entry evidence | **Satisfied for automated evidence.** SafeMode is visible at entry and again before sharing; unreviewed drafts are excluded. | Human screenshot/copy and accessibility acceptance remain required. |
| Decision record | This issue now names the E2E and screenshot locations. | Product QA / MVP-EXIT must consume the merged evidence before Open-gate decision. |

- Status impact: **Draft remains**. The automated first-value and SafeMode evidence packet is now connected, but fixture meaning, natural operation, keyboard evidence sufficiency, and human accessibility acceptance remain human decisions.
- No new ADR is needed. The slice verifies the accepted first-value and SafeMode boundaries without changing product scope, persistence, or release authority.
