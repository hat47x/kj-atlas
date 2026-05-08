# Issue Draft: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft (dependency-locked for Stream H planning)
- Source Issue: N/A
- Priority: P1
- Owner: Stream G (planning only)
- Scope: `01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`（必要時最小、実装コード変更禁止）
- Dependencies: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`（FB-P0収束をGo条件として固定）, `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`（HIL-RS-02計画同期完了まで実装着手禁止）
- Related Backlog: `QA-E2E-USE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-E2E-USE-01
- RequirementStatement: 現在のE2E検証を、実運用に近いユーザージャーニー（作成→編集→レビュー→安全共有）で再現できるシナリオ群へ拡張し、回帰検知力を向上させる。
- PriorityClass: Must
- AcceptanceScenario:
  - 前提: seedデータまたはfixtureから起動し、safeMode既定ONの状態でテスト開始できる。
  - 操作: カード作成/配置、差分確認、review attribution更新、share/export判定を1フローで実行する。
  - 期待結果: 主要導線が安定して完走し、安全境界（safeMode・share/export制御）に回帰がない。
  - 除外: SSO本番連携、外部LLMプロバイダ実通信、長時間負荷試験。
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export / import-sanitize
- VerificationLevel: e2e
- DecisionStatus: Hold-for-Dependency-Gate
- DecisionQueueRef: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`
- ContractPolicy: E2Eケース定義は contract レベルで固定し、実装詳細（DOM構造・内部関数名・一時的UI文言）へ依存しない。
- DependencyLockPolicy: FB-P0収束 + HIL-RS-02計画同期が完了するまで `Hold-for-Dependency-Gate` を維持し、`Proceed` 判定を出さない。

## Stream G phase protocol（dependency-locked planning）

本Issueは実装移行前の計画最適化フェーズとして、以下の固定順序でのみ更新する。

1. Read同期（ADR-0019 / 関連Issue再読）
2. AC/DoD具体化（測定可能な判定式へ変換）
3. 依存条件の明記（解除条件・禁止事項の固定）
4. Verify（計画としての検証項目を自己点検）
5. Proceed（依存未解除のため **Proceed=Not Allowed** を明記）

### Proceed rule（固定）

- Proceed = Not Allowed（dependency-locked）
- Proceed可能化条件（将来）:
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline` が Go 判定
  - `issue-HIL-RS-02-next-phase-delivery-plan` の同期完了
  - 本Issueの Go 条件（4.1）を満たす実装計画がレビュー承認済み

## Phase 1. Read同期（ADR-0019整合）

- `ADR-0019` の原則に従い、本Issueは「仕様評価前の結合バグ除去」を目的に据える。
- safeMode既定ON・share/export漏えい防止は安全境界として最優先で固定する。
- 本フェーズは **計画確定のみ** とし、実装ファイル変更は実施しない。
### 1.1 Read同期チェックリスト（毎Phase再読）

- [x] `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md` を再読し、E2E目的を「仕様評価前の結合バグ除去」に固定。
- [x] safeMode既定ON / share-export fail-closed / import sanitize を安全境界として再確認。
- [x] 本Issueのスコープが docs-only（本ファイルのみ編集）であることを再確認。


## Phase 2. ADR明文化（C/D/C）

### C: Context
- 現行E2Eはスモーク中心で、実利用の縦断フロー（再編集・レビュー・安全共有）を十分に担保できていない。

### D: Decision
- 実利用ジャーニーを3本以上、AC/DoD付きで固定し、safeMode/share-export境界の回帰検知を必須アサーションとして定義する。
- GoNoGoGateをRequiredとし、実装着手前に合格基準を文書固定する。

### C: Consequence
- 実装フェーズでの迷いを排除し、E2E追加時の判定一貫性を確保する。
- 安全境界後退（safeMode既定緩和、share/export誤開放）を即時に検知できる。

## Phase 3. Plan（不足AC/DoD補完提案）

### 3.1 実利用ジャーニー定義（3本以上）

1. **Journey-A: Authoring Continuity**（作成→再配置→保存復元）
   - 前提: 新規docをfixtureで作成、safeMode=ON。
   - 操作: card作成→island再配置→保存→再読込。
   - 契約アサーション: 再読込後に位置・relation・pending整合が崩れない。
   - 非依存条件: DOM class名、描画レイヤ内部実装、state管理方式に依存しない。

2. **Journey-B: Review Governance**（編集→差分→review attribution）
   - 前提: unreviewed/human_reviewed混在fixture。
   - 操作: 編集→diff確認→humanレビュー操作→状態再確認。
   - 契約アサーション: `human_reviewed`昇格は人手経路のみ成功し、AI/自動昇格経路が存在しない。
   - 非依存条件: UI部品名、ボタン配置、内部イベント名に依存しない。

3. **Journey-C: Safe Sharing Gate**（レビュー→共有/エクスポート判定）
   - 前提: unreviewed本文を含むdoc、safeMode=ON。
   - 操作: share/exportを試行→レビュー条件を満たして再試行。
   - 契約アサーション: 初回はfail-closed（拒否/警告）、条件充足後のみ許可。
   - 非依存条件: ダイアログ文言、通知トースト文面、送信実装方式に依存しない。

4. **Journey-D: Import-to-Safe-Export**（sanitize境界）
   - 前提: markdown/zip入力fixture（正常系+悪性入力）。
   - 操作: import sanitize→編集→share/export判定。
   - 契約アサーション: sanitize逸脱入力は拒否され、安全入力のみ後段に進める。
   - 非依存条件: パーサ内部実装、中間データ構造、エラーメッセージ文面に依存しない。

### 3.2 追加AC（確定）

- [ ] AC-01: Journey-A〜Cを必須、Dを推奨として文書化する（計3本以上）。
- [ ] AC-02: Journey-Cに「safeMode既定ON時 fail-closed」を明示する。
- [ ] AC-03: share/export境界で unreviewed 含有時の拒否アサーションを必須化する。
- [ ] AC-04: review attribution の昇格境界（human only）を必須アサーション化する。
- [ ] AC-05: GoNoGoGate判定式（下記）を満たさない場合は実装マージ不可とする。
- [ ] AC-06: 各Journeyの期待結果を contract アサーションとして定義し、実装依存アサーションを禁止する。

### 3.3 DoD（確定）

- [ ] DoD-01: 3本以上のジャーニーに前提/操作/期待/除外を明記。
- [ ] DoD-02: safeMode/share-export回帰検知要件を test assertion レベルで記述。
- [ ] DoD-03: Expected verification level=e2e と実行コマンドが一致。
- [ ] DoD-04: フェイルセーフ停止条件（未定義依存/境界後退/self-correction>3）を明記。
- [ ] DoD-05: 実装着手条件（Phase 6）を満たすまでコード変更しない。
- [ ] DoD-06: ケース記述に実装依存語（固定CSSセレクタ/内部関数名/コンポーネント固有ID）が含まれていない。
- [ ] DoD-07: dependency lock 維持を明記し、Proceedを発火しない運用注記を保持。
- [ ] DoD-08: Verify結果として「計画完了/実装未着手/依存未解除」を3点セットで記録。

## Phase 4. Execute（計画固定：シナリオ境界・安全境界・除外条件の凍結）

### 4.1 Go/No-Go Gate（Required）

**Go条件（全て必須）**
1. Journey-A〜CのACが満たされること。
2. safeMode既定ON + share/export fail-closed回帰が検知可能であること。
3. review attribution昇格境界（human only）の回帰検知があること。
4. `npm run test:e2e` と対象grep実行手順が文書化されること。

**No-Go条件（1つでも該当で停止）**
- 未定義依存が残る。
- safeMode/share-export境界が後退する。
- Verify自己修復（self-correction）が3回を超える。

### 4.2 タスク分解（計画確定版）

- [ ] T1: 既存E2E棚卸しと Journey-A〜D のマッピング（Smoke/Core/Safety分類を含む）。
- [ ] T2: Journey-A（縦断基本）を最初に実装。
- [ ] T2: Journey-A（縦断基本）を最初に**実装対象として指定**（本フェーズでは実装しない）。
- [ ] T3: Journey-B/Cを追加し、安全境界回帰を共通アサーション化。
- [ ] T4: Journey-D（sanitize境界）を拡張実装（推奨）。
- [ ] T5: `04_Documentation/e2e_testing.md` 同期更新（同一PR）。

### 4.3 固定境界（実装準備のための凍結）

- **シナリオ境界**: 必須=Journey-A/B/C、推奨=Journey-D。
- **安全境界**: safeMode既定ON、share/export fail-closed、review attribution human-only、import sanitize。
- **除外条件**: SSO本番連携、外部LLM実通信、長時間負荷試験は本Requirementの対象外。
- **契約固定境界**: 判定対象は利用者に観測可能な入出力/状態遷移のみとし、内部実装変更で破綻しないこと。



### 4.4 Execute完了条件（Plan→Execute→Verify→Proceed の直列性を固定）

- [ ] E-01: Phase 3で定義したJourney/AC/DoDを変更せずに凍結する（追加・削除・意味変更を行わない）。
- [ ] E-02: 固定した計画をVerify入力として参照し、Verify結果でのみProceed可否を判定する。
- [ ] E-03: self-correction試行回数を記録し、`0/3` から開始する。

## Phase 5. Verify（e2e観点の判定可能性確認）

- Expected verification level は `e2e`。
- 実行要件（実装フェーズで必須）:
  - `npm run test:e2e`
  - `npm run test:e2e -- --grep "Journey-(A|B|C|D)|realistic journey|safe share"`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 判定整合:
  - 上記コマンドで Journey-A〜C が再現され、AC/DoDに対応するアサーションが確認できること。
  - 測定可能指標（下記 V-E2E-*）が記録され、閾値を満たすこと。
  - アサーションは contract レベル（観測可能な振る舞い）で記述され、実装依存を含まないこと。

- docs-check（本フェーズ）:
  - `python 01_Plans/issues/validate_active_issue_memos.py` が成功し、本Issueメモの構造整合が確認できること。
  - GoNoGoGate/AC/DoD/停止条件の記述が相互矛盾しないこと。

### 5.1 測定可能なテスト指標（Verify必須）

- V-E2E-01 実行成功率: Journey-A/B/C の各シナリオが `pass`（3/3必須、Dは推奨）。
- V-E2E-02 安全境界アサーション件数:  
  - safeMode既定ON検証 >= 1  
  - share/export fail-closed検証 >= 1  
  - review attribution human-only検証 >= 1  
  - import sanitize検証 >= 1（Journey-D採用時は必須）
- V-E2E-03 Flake管理: 同一コミットで2回連続実行し、Journey-A/B/Cの結果差分が0件。
- V-E2E-04 所要時間上限: core（Journey-A/B/C）合計実行時間を記録し、基準時間から20%超過時は要因分析を添付。
- 判定ルール:
  - V-E2E-01〜03のいずれか未達は **No-Go**。
  - V-E2E-04は超過時に即Failではなく、要因分析未添付なら **No-Go**。
  - Verify自己修復（self-correction）は3回まで。4回目が必要な場合は **Stop**。

## Phase 6. Proceed/Stop（実装着手条件 / dependency gate fixed）

### self-correction カウンタ（本Issue運用）

- 現在値: `0/3`
- ルール: Verifyの自己修復は最大3回。`4回目相当` が必要になった時点で即Stop。

実装着手は、以下を満たした場合のみ許可（未達ならStop）。

1. 本Issueの `Status=Draft (dependency-locked)` が維持され、依存解消時のみ `Ready-for-Implementation` へ昇格する。
2. AC-01〜AC-06 / DoD-01〜DoD-06 が未矛盾で固定されている。
3. GoNoGoGate=Required の判定式に曖昧さがない。
4. `04_Documentation/e2e_testing.md` 同期更新タスクが同一PR対象に含まれる。
5. フェイルセーフ3条件（未定義依存/境界後退/self-correction>3）を停止基準として実装計画に転記済み。

---

## リスクとロールバック / Risks & rollback

- 失敗モード: シナリオ増加に伴うCI時間増大、flake増加。
- 影響範囲: Frontend E2Eパイプライン、リリース判定時間。
- ロールバック: 追加シナリオを `core` / `nightly` タグで分離し、安定化まで段階昇格。

## Additional context

- 関連Issue: `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`, `01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
- ADR化トリガー: CI許容時間超過が継続し、E2Eレベル設計の方針変更が必要な場合。


### Stop条件（明示）

- 未定義依存が発生した場合は **Stop**（推測補完禁止）。
- 安全境界（safeMode/share-export/import sanitize/review human-only）の曖昧化または後退が生じる場合は **Stop**。
- Verify自己修復が3回を超える見込みとなった時点で **Stop**。


## Stream D QA pass（2026-05-06 / E2E-UNIT独立推進）

### Phase 1: Read & ギャップ抽出
- Read対象を再確認し、E2E要件は `ADR-0019` と本Issueの contract 方針に一致していることを確認。
- ギャップ抽出:
  1. 優先順位（回帰/境界/性能）の明示順が本文で分散している。
  2. 実行手順の「誰が何を完了とするか」がDoD本文に集約されていない。
  3. 他レーン非干渉の検証観点が明文化されていない。

### Phase 2: AC/DoDドラフト提示・合意（docs-only）
- AC追記ドラフト:
  - AC-D1: 回帰（Journey-A/B/C pass）を最優先ゲートとして明記する。
  - AC-D2: 境界（safeMode/share-export/review attribution/import sanitize）を第2優先で必須化する。
  - AC-D3: 性能（V-E2E-04）は回帰・境界を満たした上で評価する従属ゲートとする。
- DoD追記ドラフト:
  1. 実行担当（QA）と判定責務（Go/No-Go判定者）をIssue本文で追跡可能にする。
  2. Verifyログに self-correction カウンタ（0/3起点）を必ず残す。

### Phase 3: テスト観点の優先順位付け（回帰/境界/性能）
1. 回帰: Journey-A/B/Cの再現性・flakeゼロを最優先。
2. 境界: safeMode既定ON, share/export fail-closed, human-only昇格, sanitize拒否を次優先。
3. 性能: core実行時間（V-E2E-04）を第3優先で監視し、超過時は要因分析を必須化。

### Phase 4: 実行手順と完了定義の明文化
- 実行手順（実装フェーズ適用）:
  1. `npm run test:e2e`
  2. `npm run test:e2e -- --grep "Journey-(A|B|C|D)|realistic journey|safe share"`
  3. `python 01_Plans/issues/validate_active_issue_memos.py`
- 完了定義:
  - V-E2E-01〜03を満たし、V-E2E-04超過時は要因分析付きで記録。
  - self-correction が `3/3` を超えない。
  - No-Go条件ゼロを確認して Proceed 判定。

### Phase 5: Verify（他レーン非干渉確認）
- 非干渉チェック:
  - 本更新は `01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` の計画記述に限定。
  - 実装コード（`03_Implement/*`）および他Issue本文は未編集。
  - unit計画への越境指示は行わず、E2E境界内で完結。
- Fail-safe:
  - 不整合・依存崩壊を検知した場合は Stop。
  - self-correction は最大3回。4回目相当が必要な時点で停止して指示待ち。

## Stream F independent pass (2026-05-06)

### Phase 1 Read同期
- `AGENTS.md` の Stream F 対象境界を再確認し、本メモの編集範囲を QA/I18N/RM の独立検証記録に限定した。
- 上流方針（`ADR-0019`, SafeMode既定ON, share/export fail-closed）との整合を再確認した。

### Phase 2 依存確認（モック契約基準）
- 依存 I/F は contract-first とし、内部実装詳細ではなく観測可能な入出力・状態遷移を判定対象に固定した。
- 先行依存（I18N→MID→RS→SEC / PUB境界）に矛盾がないかを確認し、矛盾時は Proceed せず Stop する条件を維持した。

### Phase 3 Plan / Execute / Verify / Proceed
- Plan: AC/DoD/Go-NoGo と検証コマンドの対応を再点検した。
- Execute: docs-only で判定文面を整備し、実装コード変更は行わない方針を維持した。
- Verify: 本メモ記載の証跡形式（Command/Result/Decision/Next action）で再実行可能性を確認した。
- Proceed: 依存未解決・環境制約・境界後退のいずれかがある場合は Hold/Stop を優先する。

### Phase 4 Self-Correction（最大3回）
- 自己修復上限を `3回` に固定し、4回目相当が必要な場合は Fail-safe 停止を適用する。
- 修復時は「欠落AC補完 → 判定再確認 → 証跡更新」の順で最小差分更新のみ許容する。

### Phase 5 Stopper
- 停止トリガー: 依存矛盾、SafeMode境界後退、GoNoGo未充足、または自己修復上限超過。
- 停止時は未達項目と再開前提（必要I/F・実行環境・判定根拠）を本メモへ追記して引き継ぐ。


## Stream H dependency lock (2026-05-07 / planning freeze)

- FB-P0収束・HIL-RS-02計画同期を **実装着手の前提依存** として固定する。
- 着手条件（全必須）:
  1. `issue-FB-P0-2A2B2C-stream-c-planning-baseline` が Done/Closed で、P0収束が証跡付きで確認できる。
  2. `issue-HIL-RS-02-next-phase-delivery-plan` の依存解消状態（A1依存とDecision Queue条件）が本Issueに同期されている。
  3. 本IssueのAC/DoD/GoNoGoが上記2依存と矛盾しない。
- ProceedDecision（現時点）: **Hold**。
- Stopper: 依存未解消、依存状態の再現不可、またはA1完了前の実装要求が出た場合は即Stop。

## Stream G sync pass（2026-05-07 / dependency-gate clarification）

### Phase 1: Read同期
- 再読対象を固定: `ADR-0019` / `04_Documentation/e2e_testing.md` / `issue-FB-P0-2A2B2C-stream-c-planning-baseline` / `issue-HIL-RS-02-next-phase-delivery-plan`。
- 本Issueは docs-only planning であり、実装コード変更禁止を再確認。

### Phase 2: AC/DoDの具体化（測定可能条件）
- AC-ME-01: Journey-A/B/C は Verifyで `pass=3/3` を必須、Journey-D は `pass=0/1以上` を推奨として別集計。
- AC-ME-02: 安全境界アサーション（safeMode既定ON / share-export fail-closed / review attribution human-only）を各1件以上必須。
- AC-ME-03: Flake検出として同一コミット2連続実行で Journey-A/B/C の差分0件を必須。
- DoD-ME-01: Verifyログに `V-E2E-01..04` を全項目記録（未記録1件でもNo-Go）。
- DoD-ME-02: Verifyログに self-correction カウンタを `n/3` 形式で残す。
- DoD-ME-03: `Proceed=Not Allowed` と dependency lock 理由を同一節に明記。

### Phase 3: 依存ゲート（契約クローズ条件）
- Gate-E2E-01（FB-P0）: `issue-FB-P0-2A2B2C-stream-c-planning-baseline` の Go 判定記録が存在すること。
- Gate-E2E-02（HIL-RS-02）: `issue-HIL-RS-02-next-phase-delivery-plan` で検証スコープ同期完了が明示されること。
- Gate-E2E-03（契約固定）: 本Issue内で Journey-A/B/C 必須、Go/No-Go式、停止条件（未定義依存/境界後退/self-correction>3）が同時に `done`。
- Open化条件: Gate-E2E-01〜03 が全て closed のときのみ `Ready-for-Implementation` へ遷移可能。

### Phase 4: Verify（最大3回）
- Verify-1（docs整合）: `python 01_Plans/issues/validate_active_issue_memos.py` 成功。
- Verify-2（差分健全性）: `git diff --check` 成功。
- Verify-3（任意）: 追加修復が必要な場合のみ再実行し、`self-correction 3/3` 超過なら Stop。
- 本pass結果: self-correction `1/3`、Proceedは dependency-locked のため Not Allowed 維持。
