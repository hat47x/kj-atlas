# Issue Draft: DOC-OPS-03 意思決定支援の進捗ダッシュボード作成計画

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner + PM/Triage
- Scope: `01_Plans/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0002`, `ADR-0007`, `01_Plans/issues/README.md`
- Dependencies: N/A
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- 現状は複数文書を横断しないと「今どこまで進んだか」「どの判断が必要か」を直感的に把握しづらい。
- 人間の意思決定を支援する「単一ダッシュボード」需要が明確化した。
- 人間の意思決定を支援するため、`01_Plans/` 配下にダッシュボード本体を作成して運用を開始する。

## 2) 背景 / Context

- 直近の意思決定（ENV-ARCH-01 / AUTH-OPS-03）で、進捗と判断待ちの可視化ニーズが増大。
- `DOC-OPS-02` は文書横断改善計画だが、体感的な進捗把握に特化した単一ファイル要件は未実装。
- `01_Plans/` 配下にダッシュボードを1ファイルで管理し、今後の意思決定と進捗確認の入口とする。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 意思決定の速度と再現性を向上する。
- 安全（THREAT_MODEL / SafeMode）: 直接的な仕様変更は伴わないが、判断遅延による運用ミスを予防する。
- 企業・行政要件（enterprise_architecture）: 承認主体・判断待ち項目の可視化は監査説明性を補助する。
- 後方互換（schemas）: スキーマ影響なし（docs-only）。

## 4) 提案する解決策 / Proposed solution

- 本Issueで実施すること:
  - `01_Plans/` 配下にダッシュボード本体ファイルを1つ作成する。
  - 最小要件（進捗・判断待ち・決定ログ・次の1手）を実装する。
- 本Issueで実施しないこと（非目標）:
  - backend/frontend 実装コードの変更。
  - ADRやスキーマの仕様変更。

## 5) AC/DoD不足の先行提案（着手前）

- 不足1: 実行プロトコル（Plan→Execute→Verify→Proceed）が受入条件に明示されていない。
  - 提案: ダッシュボード本文に4段階運用手順を追加し、各段階の出力（計画・差分・検証結果・次アクション）を固定する。
- 不足2: 自己修正上限（Self-Correction最大3回）が受入条件に未反映。
  - 提案: 検証セクションに「不一致時は最大3回まで修正し、それでも解消しない場合は停止」を明記する。
- 不足3: 競合検知時の停止条件が明文化されていない。
  - 提案: Active issue状態やDecision Queueに矛盾がある場合は、更新停止と人間判断待ちへ遷移する条件を追加する。

## 6) 受入条件 / Acceptance criteria

- [x] `01_Plans/` 配下にダッシュボード本体ファイルが1つ作成される。
- [x] ダッシュボードに「進捗サマリ」「Active issue集約」「人間判断待ち」「決定ログ」「次の1手」が含まれる。
- [x] ダッシュボードに `Plan→Execute→Verify→Proceed` の運用手順が追記される。
- [x] 検証セクションに「Self-Correction最大3回」「競合検知時は停止」が明記される。
- [x] 期待検証レベルを `docs-check` として満たす。
- [x] `01_Plans/issues/README.md` からダッシュボードへ辿れる。

## 7) 実装タスク分解 / Task breakdown

- [x] T1: ダッシュボード本体ファイルへ運用プロトコルを追記。
- [x] T2: AC/DoD不足を先行提案として issue memo に記録。
- [x] T3: Active issue index（`01_Plans/issues/README.md`）の導線文言を同期。
- [x] T4: docs-check 検証を実行し結果を記録。

## 8) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "DOC-OPS-03|ダッシュボード|進捗サマリ|人間判断待ち" 01_Plans`
- 期待結果:
  - issue memo 検証が成功し、ダッシュボード要件キーワードが検索可能。

## 9) 代替案 / Alternatives considered

- 代替案A: issue memoだけを更新し、ダッシュボード作成は延期する。
  - 却下理由: 意思決定支援の即効性が得られない。
- 代替案B: 既存READMEに進捗表を追記して代替する。
  - 却下理由: 「01_Plansに1つだけのダッシュボード」要件と分離管理方針に合わない。

## 10) リスクとロールバック / Risks & rollback

- 失敗モード: ダッシュボード項目が不足し意思決定支援にならない。
- 影響範囲: 運用判断の遅延、参照文書の往復コスト。
- ロールバック手順: 最小要件5項目に絞って再構成し、リンク導線を優先して復旧する。

## 11) Additional context

### ダッシュボードの最小要件

- プロジェクト状況サマリ（フェーズ別進捗）
- Active issue のステータス集約（Draft/Open/In Progress）
- 人間判断待ち項目（意思決定キュー）
- 直近の決定ログ（何が決まり、何が未決か）
- 次の1手（再開コマンド/編集対象）




## 12) 状態整合ログ（2026-03-08）

- `project-progress-dashboard.md` / `issues/README.md` / `decision-pack-2026-03-human-judgement.md` の Active・Decision Queue・次の1手を同期。
- 競合停止条件（3回自己修正超過、前提崩壊、未定義競合）をダッシュボード本文へ固定。
- Active一覧と実態が一致することを docs-check で確認。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream E execution log（2026-05-06 / rerun-69）

- Scope限定: shared統合リソース3ファイル + DOC-OPS issueのみに編集範囲を限定。
- 直列Phase実行: Read同期 → DOC-OPS境界（B/C/D・SoD）チェック → Plan→Execute→Verify→Proceed を1サイクル実行。
- Verify結果: `validate_active_issue_memos.py` と unittest 成功、`rg` 監査で `Self-Correction>3` / 競合 / 整合崩壊の該当なし。

## Stream L execution log（2026-05-18）

### Phase 1: Read同期（事実分類）
- `python 01_Plans/triage_actionable_plans.py` を実行し、Active母集団を **44件（Ready=9 / Blocked=35）** として再分類した。
- `Blocked` の内訳は Draft gate 起因が中心で、推測による状態更新は実施しない方針を維持した。
- `invalid Status metadata` は4件（`Open準備完了 (Ready for Open)`）を検知し、運用停止条件（metadata不正多発）に該当するため、状態遷移更新は行わず修正フロー定義へ回した。

### Phase 2: ADR要素明文化（進捗運用観点）
- Context: Active件数が旧公開固定値（件数47系）と乖離しており、triage基準での再計測値を運用基準に採用する必要がある。
- Decision: ダッシュボード契約は **triage実測値を唯一の更新根拠** とし、推測更新を禁止する。
- Consequences: Dashboard/decision-pack/README の同期時に、実測値と不一致なら更新停止＋修正フローへ遷移する。

### KPI定義（DOC-OPS-03運用）
- 処理速度（Throughput）: `週次 Done遷移件数 / 週次 Active母集団件数`。
- ブロッカー解消率（Blocker Resolution Rate）: `当週 Blocked→Ready 遷移件数 / 週初 Blocked件数`。
- 再オープン率（Reopen Rate）: `Done→Open|In Progress へ戻った件数 / 当週 Done遷移件数`。

### Phase 3: ダッシュボード契約固定
- 優先度・依存・状態遷移は `triage_actionable_plans.py` 出力（classification/dependency_stage/priority）を正本とする。
- invalid status 修正フローを固定:
  1. `validate_active_issue_memos.py` と `triage_actionable_plans.py` の両方で不正値を検知。
  2. 該当issueを `Draft/Open/In Progress/Done/Blocked` の許容値へ正規化。
  3. 再実行で `Triage errors (stopper)=0` を確認するまで統合更新を停止。

### Phase 4-6: Execute / Verify / Proceed
- Execute: 本Issueに進捗運用契約（KPI/修正フロー）を追記。
- Verify: triage・validator・unit test を実行し、現時点は triage error 4件を継続検知（既知課題として記録）。
- Proceed（次アクション）:
  1. 週次: triage実行→KPI集計→decision-pack更新（推測更新禁止）。
  2. 日次: invalid metadata件数と Blocked→Ready 遷移の差分監査。
  3. フェイルセーフ: invalid metadata多発が継続し3回修復を超える場合、意思決定者へエスカレーション。

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `progress dashboard planning`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-03` の公開境界を再確認。
- Decision: ダッシュボード計画そのものは変更せず、残Open化準備をDOC-PUBLICとDOC-OPS-05各票に分散記録する方針を維持した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
