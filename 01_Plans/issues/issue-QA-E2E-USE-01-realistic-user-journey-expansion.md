# Issue Draft: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft (dependency-locked for Stream J planning)
- Source Issue: N/A
- Priority: P1
- Owner: Stream H (planning only)
- Scope: `01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` のみ（実装コード変更禁止）
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

## Stream H phase protocol（dependency-locked planning）

本Issueは実装移行前の計画最適化フェーズとして、以下の固定順序でのみ更新する（**Phase 1..6直列実行 + 毎Phase Read同期必須**）。

1. ADR明文化（C/D/C）を先に固定
2. Read同期（ADR-0019 / 関連Issue再読）
3. AC/DoD具体化（測定可能な判定式へ変換）
4. 依存条件の明記（解除条件・禁止事項の固定）
5. Verify（計画としての検証項目を自己点検、失敗時は3回まで修復）
6. Proceed（依存未解除のため **Proceed=Not Allowed** を明記）

### Proceed rule（固定）

- Proceed = Not Allowed（dependency-locked）
- Proceed可能化条件（将来）:
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline` が Go 判定
  - `issue-HIL-RS-02-next-phase-delivery-plan` の同期完了
  - 本Issueの Go 条件（4.1）を満たす実装計画がレビュー承認済み

## Phase 1. ADR明文化（C/D/C）

### C: Context

- 現行E2Eはスモーク中心で、実利用の縦断フロー（再編集・レビュー・安全共有）を十分に担保できていない。
- ジャーニー定義が曖昧なままでは、E2Eが「形式上の実行」に留まり、価値検証が不可能になる。
- dependency lock中に実装へ進むと、前提依存の崩れにより計画整合が破綻する。

### D: Decision

- 実利用ジャーニーを **最低3本（推奨4本）**、各ジャーニーに「前提/操作/観測点/期待結果/失敗時記録」を固定して定義する。
- safeMode/share-export/review attribution を GoNoGoGate の必須判定軸とし、実装前に判定式を文書固定する。
- dependency lock 解除前は計画更新のみに限定し、実装・テストコード更新は行わない。
- Verify失敗時は **最大3回修復** し、超過時または依存崩れ検知時は **Stop** する。

### C: Consequence

- E2E価値検証の再現性が向上し、実行可否判定が曖昧にならない。
- 依存ロック下でも、実装移行後に即時着手できる判定可能な運用仕様を維持できる。
- 安全境界後退（safeMode既定緩和、share/export誤開放、review昇格逸脱）を検知可能な状態で引き渡せる。
- Verify運用が上限付き修復ループになるため、無制限な再試行を防止できる。

### 1.1 Read同期チェックリスト（毎Phase再読）

- [x] `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md` を再読し、E2E目的を「仕様評価前の結合バグ除去」に固定。
- [x] safeMode既定ON / share-export fail-closed / import sanitize を安全境界として再確認。
- [x] 本Issueのスコープが docs-only（本ファイルのみ編集）であることを再確認。

## Phase 2. Read同期（ADR-0019整合）

- `ADR-0019` の原則に従い、本Issueは「仕様評価前の結合バグ除去」を目的に据える。
- safeMode既定ON・share/export漏えい防止は安全境界として最優先で固定する。
- 本フェーズは **計画確定のみ** とし、実装ファイル変更は実施しない。

### 1.1 Read同期チェックリスト（毎Phase再読）

- [x] `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md` を再読し、E2E目的を「仕様評価前の結合バグ除去」に固定。
- [x] safeMode既定ON / share-export fail-closed / import sanitize を安全境界として再確認。
- [x] 本Issueのスコープが docs-only（本ファイルのみ編集）であることを再確認。

## Phase 3. Plan（AC/DoD補完）

### 3.1 実利用ジャーニー定義（判定可能版）

1. **Journey-A: Authoring Continuity**（作成→再配置→保存復元）
   - 前提: 新規docをfixtureで作成、safeMode=ON。
   - 操作: card作成→island再配置→保存→再読込。
   - 観測点:
     - 保存前後でカード件数が一致。
     - relation件数が欠損しない。
     - pending shelf件数が意図せず変化しない。
   - 期待結果: 再読込後に位置・relation・pending整合が崩れない。
   - 失敗時記録: doc_id、fixture_id、操作ステップ、期待値/実測値差分。
   - 非依存条件: DOM class名、描画レイヤ内部実装、state管理方式に依存しない。

2. **Journey-B: Review Governance**（編集→差分→review attribution）
   - 前提: unreviewed/human_reviewed混在fixture。
   - 操作: 編集→diff確認→humanレビュー操作→状態再確認。
   - 観測点:
     - diff生成が成功し、変更対象が記録される。
     - `human_reviewed` への昇格イベントが人手操作でのみ発生。
     - 非人手経路（自動/AI）で昇格が発生しない。
   - 期待結果: review attribution 境界（human only）が維持される。
   - 失敗時記録: review対象ID、昇格トリガー、イベントログ要約。
   - 非依存条件: UI部品名、ボタン配置、内部イベント名に依存しない。

3. **Journey-C: Safe Sharing Gate**（レビュー→共有/エクスポート判定）
   - 前提: unreviewed本文を含むdoc、safeMode=ON。
   - 操作: share/exportを試行→レビュー条件を満たして再試行。
   - 観測点:
     - 初回試行が fail-closed（拒否/警告）になる。
     - 条件充足後の再試行でのみ許可される。
     - safeMode既定ONがセッション中に緩和されない。
   - 期待結果: share/export境界で unreviewed 含有時の拒否が再現される。
   - 失敗時記録: 試行時safeMode値、拒否理由、再試行時の許可条件。
   - 非依存条件: ダイアログ文言、通知トースト文面、送信実装方式に依存しない。

4. **Journey-D: Import-to-Safe-Export**（sanitize境界、推奨）
   - 前提: markdown/zip入力fixture（正常系+悪性入力）。
   - 操作: import sanitize→編集→share/export判定。
   - 観測点:
     - sanitize逸脱入力が reject される。
     - 正常入力のみ後段フローへ進める。
     - 後段でも safeMode/share-export gate が維持される。
   - 期待結果: sanitize境界と共有境界の二重安全が維持される。
   - 失敗時記録: 入力fixture種別、sanitize判定、後段gate判定。
   - 非依存条件: パーサ内部実装、中間データ構造、エラーメッセージ文面に依存しない。

### 3.2 追加AC（確定）

- [ ] AC-01: Journey-A〜Cを必須、Dを推奨として文書化する（計3本以上）。
- [ ] AC-02: 各Journeyに前提/操作/観測点/期待結果/失敗時記録を明記する。
- [ ] AC-03: Journey-Cに「safeMode既定ON時 fail-closed」を明示する。
- [ ] AC-04: share/export境界で unreviewed 含有時の拒否アサーションを必須化する。
- [ ] AC-05: review attribution の昇格境界（human only）を必須アサーション化する。
- [ ] AC-06: GoNoGoGate判定式（4.1）を満たさない場合は実装マージ不可とする。
- [ ] AC-07: 各Journeyの期待結果を contract アサーションとして定義し、実装依存アサーションを禁止する。

### 3.3 DoD（確定）

- [ ] DoD-01: 3本以上のジャーニーに前提/操作/観測点/期待/除外を明記。
- [ ] DoD-02: safeMode/share-export回帰検知要件を assertion レベルで記述。
- [ ] DoD-03: Expected verification level=e2e と実行コマンドが一致。
- [ ] DoD-04: フェイルセーフ停止条件（未定義依存/境界後退/self-correction>3）を明記。
- [ ] DoD-05: 実装着手条件（Phase 6）を満たすまでコード変更しない。
- [ ] DoD-06: ケース記述に実装依存語（固定CSSセレクタ/内部関数名/コンポーネント固有ID）が含まれていない。
- [ ] DoD-07: dependency lock 維持を明記し、Proceedを発火しない運用注記を保持。

## Phase 4. Execute（Issue本文整備のみ）

- 毎Phase Read同期ルールに従い、Phase 4開始時点でも `ADR-0019` と依存Issue状態を再確認する。
- 本Issue本文のみを更新し、`03_Implement/*` およびテストコード変更は行わない。
- dependency-locked protocol を維持し、実装前倒し判断を禁止する。

## Phase 5. Verify（実行可否判定 + self-correction）

- 毎Phase Read同期ルールに従い、Verify前に `ADR-0019` / dependency状態 / Proceed rule を再読したうえで判定する。

### 5.1 判定可能性チェック

- [x] 各Journeyに前提/操作/観測点/期待結果/失敗時記録が定義されている。
- [x] Journey-A〜Cが必須ジャーニーとして固定されている。
- [x] safeMode既定ON + share/export fail-closed が必須判定軸に入っている。
- [x] review attribution human-only昇格が必須判定軸に入っている。
- [x] dependency lock下で Proceed=Not Allowed が維持されている。

### 5.2 self-correction log（最大3回）

1. 修正1: Journey記述へ「観測点」を追加し、実行可否判定の曖昧さを解消。
2. 修正2: 各Journeyへ「失敗時記録」を追加し、失敗時トリアージの再現性を補強。
3. 修正3: GoNoGo判定式とProceed ruleの関係を再記述し、依存未解決時の誤Proceedを防止。

- self-correction count: 3 / 3（上限内）
- 逸脱時停止規則: self-correction が 3 回を超過、または dependency gate 崩れを検知した場合は Proceed 判定を行わず Stop に遷移する。

## Phase 6. Proceed（dependency-locked）

- 毎Phase Read同期ルールに従い、最終判定前に `ADR-0019` と依存Issue状態の再読結果を反映する。

### 6.1 GoNoGoGate 判定式（実装移行判定、将来適用）

以下をすべて満たした場合のみ、将来の実装Issueで Proceed=Allowed を検討できる。

1. Dependency Gate:
   - `issue-FB-P0-2A2B2C-stream-c-planning-baseline` が Go。
   - `issue-HIL-RS-02-next-phase-delivery-plan` が同期完了。
2. Journey Gate:
   - Journey-A〜C の contract assertion がテスト設計へ展開済み。
3. Safety Gate:
   - safeMode既定ON / share-export fail-closed / review human-only の3境界が未緩和。
4. Evidence Gate:
   - 失敗時記録フォーマット（doc_id/fixture_id/期待値実測差分等）が運用手順へ反映済み。

### 6.2 現在判定（2026-05-08）

- Dependency状態: 未解除
- Proceed: **Not Allowed（維持）**
- 判定: **Hold**

### 6.3 Hold / Open候補 / Stop判定

- Hold:
  - 本Issueは dependency-locked planning として保持する。
- Open候補（将来別Issue化）:
  1) Journey-A〜C を Playwrightケースへ写像する実装Issue
  2) 失敗時記録テンプレートを `04_Documentation/e2e_testing.md` へ反映する運用Issue
- Stop条件:
  - 実装・テストコード変更要求が入った場合
  - 依存未解決のまま Proceed/確定宣言が要求された場合
  - 指定外ファイル編集要求が入った場合

## Stream E Ready化設計 pass（2026-05-09 / Plan→Execute→Verify→Proceed）

### Phase 1: Read同期（ブロッカー/依存/DoD不足）
- Blocker: 依存Issueの承認証跡（Approval Record: 日時/承認者/対象/判断/evidence）が未確定の場合は `ProceedDecision: Hold` を維持する。
- Dependency: 本Issueで定義済みの依存関係を read-only で再確認し、依存先の未確定値をこのIssue側で確定しない。
- DoD gap: 「実装レーンが即着手可能な入力/出力/担当/解除条件」の4点が散在している場合、Phase 3で1ブロックに集約する。

### Phase 2: 仕様明文化（Context / Decision / Consequences）
- Context: 本Issueは Draft/Blocked を Ready化するための計画文書であり、実装や運用確定値の追加はスコープ外。
- Decision: `Proceed/Hold/Stop` の三値判定、`self-correction <= 3`、`docs-check` 優先を固定し、依存未解除時は `Hold` を維持する。
- Consequences: 先行依存が解決した時点で、実装レーンは追加解釈なしで着手可否を判定できる。

### Phase 3: Ready化（AC/DoD・入力/出力・担当・依存解除条件）
- AC/DoD Readyセット（本Issueで確認すべき共通最小セット）:
  - [ ] AC-R1: 受入条件が測定可能な判定文（done/pending/hold いずれか）で記録されている。
  - [ ] AC-R2: `ProceedDecision` と `Dependency status` が矛盾しない。
  - [ ] DoD-R1: 実装禁止境界（docs-only / proposal-only など）が明示されている。
  - [ ] DoD-R2: `Hold` 継続条件と `Stop` 条件（上限超過・競合未解決）が明示されている。
- 入力（Implementation lane input）:
  - 承認証跡、依存Issueの最新判定、固定語彙（Go/NoGo・Proceed/Hold/Stop・pass/fail/blocked）。
- 出力（Implementation lane output expectation）:
  - 着手可否の単一判定（Proceed or Hold/Stop）と、着手時に守る制約チェックリスト。
- 担当:
  - System Owner: Go/NoGo最終判定。
  - Platform Operator: 実行/保管/運用ログ整備。
  - Security Officer: 公開境界・safeMode/漏えい防止の最終確認。
- 依存解除条件:
  - 依存Issueの Approval Record 5項目が確定し、相互参照リンクで追跡可能であること。

### Phase 4: 引継ぎ（実装レーン即着手チェックリスト）
- [ ] H1: Scope逸脱なし（本Issue外の仕様確定をしていない）。
- [ ] H2: AC/DoDの未完了項目が `pending/hold` で可視化されている。
- [ ] H3: 実装開始ゲート（Proceed条件）が1箇所に集約されている。
- [ ] H4: Verifyコマンド（validator/rg/diff-check）が再実行可能。
- [ ] H5: 依存未解除時は `Hold` を維持し、推測で `Proceed` しない。

### Verify結果（本pass）
- 判定: `Hold` 維持（依存証跡未確定のため）。
- self-correction: `1/3`（上限内）。
- Stop条件再確認: 4回目相当の修復要求、または依存競合未解決時は `Stop`。
