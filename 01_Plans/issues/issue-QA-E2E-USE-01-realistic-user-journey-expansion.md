# Issue Draft: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Ready-for-Implementation
- Source Issue: N/A
- Priority: P1
- Owner: Stream F
- Scope: `01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`（本フェーズは計画確定のみ）
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
- DecisionStatus: Fixed-for-Execution
- DecisionQueueRef: `01_Plans/issues/decision-pack-2026-03-human-judgement.md`

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
   - 期待: 再読込後に位置・relation・pending整合が崩れない。

2. **Journey-B: Review Governance**（編集→差分→review attribution）
   - 前提: unreviewed/human_reviewed混在fixture。
   - 操作: 編集→diff確認→humanレビュー操作→状態再確認。
   - 期待: `human_reviewed`昇格は人手経路のみ成功し、AI/自動昇格経路が存在しない。

3. **Journey-C: Safe Sharing Gate**（レビュー→共有/エクスポート判定）
   - 前提: unreviewed本文を含むdoc、safeMode=ON。
   - 操作: share/exportを試行→レビュー条件を満たして再試行。
   - 期待: 初回はfail-closed（拒否/警告）、条件充足後のみ許可。

4. **Journey-D: Import-to-Safe-Export**（sanitize境界）
   - 前提: markdown/zip入力fixture（正常系+悪性入力）。
   - 操作: import sanitize→編集→share/export判定。
   - 期待: sanitize逸脱入力は拒否され、安全入力のみ後段に進める。

### 3.2 追加AC（確定）

- [ ] AC-01: Journey-A〜Cを必須、Dを推奨として文書化する（計3本以上）。
- [ ] AC-02: Journey-Cに「safeMode既定ON時 fail-closed」を明示する。
- [ ] AC-03: share/export境界で unreviewed 含有時の拒否アサーションを必須化する。
- [ ] AC-04: review attribution の昇格境界（human only）を必須アサーション化する。
- [ ] AC-05: GoNoGoGate判定式（下記）を満たさない場合は実装マージ不可とする。

### 3.3 DoD（確定）

- [ ] DoD-01: 3本以上のジャーニーに前提/操作/期待/除外を明記。
- [ ] DoD-02: safeMode/share-export回帰検知要件を test assertion レベルで記述。
- [ ] DoD-03: Expected verification level=e2e と実行コマンドが一致。
- [ ] DoD-04: フェイルセーフ停止条件（未定義依存/境界後退/self-correction>3）を明記。
- [ ] DoD-05: 実装着手条件（Phase 6）を満たすまでコード変更しない。

## Phase 4. Execute（シナリオ境界・安全境界・除外条件の固定）

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
- [ ] T3: Journey-B/Cを追加し、安全境界回帰を共通アサーション化。
- [ ] T4: Journey-D（sanitize境界）を拡張実装（推奨）。
- [ ] T5: `04_Documentation/e2e_testing.md` 同期更新（同一PR）。

### 4.3 固定境界（実装準備のための凍結）

- **シナリオ境界**: 必須=Journey-A/B/C、推奨=Journey-D。
- **安全境界**: safeMode既定ON、share/export fail-closed、review attribution human-only、import sanitize。
- **除外条件**: SSO本番連携、外部LLM実通信、長時間負荷試験は本Requirementの対象外。

## Phase 5. Verify（docs-check + 実行計画妥当性）

- Expected verification level は `e2e`。
- 実行要件（実装フェーズで必須）:
  - `npm run test:e2e`
  - `npm run test:e2e -- --grep "Journey-(A|B|C|D)|realistic journey|safe share"`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 判定整合:
  - 上記コマンドで Journey-A〜C が再現され、AC/DoDに対応するアサーションが確認できること。
  - 測定可能指標（下記 V-E2E-*）が記録され、閾値を満たすこと。

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

## Phase 6. Proceed/Stop（実装着手条件）

実装着手は、以下を満たした場合のみ許可（未達ならStop）。

1. 本Issueの `Status=Ready-for-Implementation` が維持されている。
2. AC-01〜AC-05 / DoD-01〜DoD-05 が未矛盾で固定されている。
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
