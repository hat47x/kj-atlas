# Issue Draft: DATA-MAINT-01 管理・復旧・棚卸し運用の整備

- Type: Feature request
- Status: Done

## Done 2026-06-21
全5タスク完了（T1-T5 at contract/docs-check level）。DecisionStatus Fixed（DATA-MAINT-03 Doneにより高権限操作分類確定済み）。
実装（管理API/CLI/UI、PostgreSQL実環境復旧演習）は別issueに分離。
- Source Issue: N/A
- Priority: P2 (Stream D third)
- Owner: Codex
- Scope: `01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`, `02_Architecture/data_model_operations_overview.html`（本Streamでは契約整理のみ）
- Related Backlog: `DATA-MAINT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`, `01_Plans/issues/issue-DATA-MAINT-04-metadata-only-audit-viewing.md`, `02_Architecture/data_model_operations_overview.html`, `02_Architecture/enterprise_architecture.html`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DATA-MAINT-01
- RequirementStatement: 想定ステークホルダーが組織運用で必要とする、ドキュメント一覧、アーカイブ/削除、バックアップ、復旧、ユーザー棚卸し、データ検証の最小運用を設計・実装できるようにする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=Platform operatorが小規模組織でkj-atlasを運用する / 操作=文書一覧、利用停止ユーザー確認、バックアップ、復旧演習を行う / 期待結果=標準手順で安全に状況確認と復旧ができる / 除外=大規模マルチテナント管理、法務上の保持期限自動判定。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure / share-export

## Dependency graph（Stream I）

- Upstream（先行固定）: `DATA-MODEL-OPS-01`（MVP運用境界の正本化）, `DATA-CONTRACT-01`（DocumentV2契約ドリフト整理）
- Parallel（並行整備）: なし
- Downstream（後続依存）: `DATA-MAINT-03`（高権限データライフサイクル方針）, `ADR-0035`（標準機能にしない製品境界の提案）, `DATA-MAINT-04`（本文を含まない監査メタデータ閲覧のDraft候補。運用runbook確定後の実装Issueは別途分割）
- Blocker条件: support level未確定、またはDocument復旧時の契約整合チェック観点が未定義

依存仕分け（Phase 4 Execute）:
- 契約先行で解消済み:
  - `DATA-MODEL-OPS-01`: CRUD境界語彙（L1/L1.5/L2/L2.5/L3/L0）を固定。
  - `DATA-CONTRACT-01`: `DocumentV2` support level / version gate / `PUT create-if-absent` 契約を固定。
- 実装待ち:
  - 復旧runbook実体、SQLite/PostgreSQL演習、棚卸しAPI/CLI候補の実装比較。


## 1) 課題 / Problem statement

- MVPはDocumentスナップショット保存を中心にしており、データをメンテナンスする標準手段が限定的である。
- 管理者が、どの文書が存在するか、誰の主体に紐づくか、いつバックアップし、どう復旧するかを確認する標準導線が不足している。
- `users` / `user_identities` は事前登録できるが、棚卸し、無効化、削除、矛盾検知の標準運用がまだ薄い。

## 2) 背景 / Context

- `documents` はドキュメント全体をJSONとして保存するため、部分修復や削除時の安全確認に標準手順が必要である。
- `merge_decision_logs` は判断ログとしてDocumentに従属するため、Document削除や復旧時の扱いを明確にする必要がある。
- 企業・行政運用では、認証/認可だけでなく、保管、復旧、棚卸し、監査への接続が導入判断に影響する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 利用者が安心して思考の途中状態を保存するには、運用者が復旧と保全の責任を果たせる必要がある。
- 安全（THREAT_MODEL / SafeMode）: バックアップや支援時に未レビュー情報や個人情報を不必要に共有しない設計が必要である。
- 企業・行政要件（enterprise_architecture）: 管理者、セキュリティ担当、サポートの分担が曖昧だと本番導入しにくい。
- 後方互換（schemas）: スナップショット形式を維持しつつ、検証・復旧手順を追加する必要がある。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - Backend: 管理用一覧、検証、アーカイブ/削除、ユーザー棚卸し、復旧補助APIの要否整理。
  - Frontend: 管理者向け画面またはCLI/運用コマンドの入口整理。
  - Documentation: バックアップ、復旧、支援時の共有前確認、データ破損時の手順。
- 変更の最小単位:
  - まず読み取り中心の棚卸しとバックアップ/復旧演習を設計する。
  - 削除や所有者移管は、ADRが必要なデータライフサイクル変更として分ける。
- 非目標:
  - 大規模SaaS型のテナント管理。
  - 法域ごとの保持期限自動判定。
  - サポート担当が利用者本文を自由閲覧できる管理機能。

## 5) 受入条件 / Acceptance criteria

- [x] Platform operatorが文書件数、更新日時、ユーザー事前登録状態を確認できる。→ `data_model_operations_overview.html` §5.1 ドキュメント棚卸し/ユーザー棚卸し（`id`/`version`/`updated_at`、payload本文閲覧は運用標準にしない）。
- [x] バックアップと復旧の標準手順が、SQLite/PostgreSQLそれぞれで説明されている。→ §5.1 バックアップ/復旧確認（SQLiteは停止時スナップショット、PostgreSQLは `pg_dump` 等、T3）。
- [x] Document削除/アーカイブの要否とリスクが整理され、実装する場合はGo/No-Go条件がある。→ §5.1 アーカイブ・削除・所有者移管（MVPでは実装しない。実装する場合はADRと専用issue必須、T4 + ADR-0035）。
- [x] サポート共有用の情報から、不要な本文や未レビュー情報を除外する方針が明示されている。→ §5.1 ドキュメント棚卸し（`payload_json` 本文の閲覧を運用標準にしない）＋ ADR-0035。
- [x] `merge_decision_logs` とDocument復旧の整合条件が検証される。→ §5.1 復旧確認（`Document.version`、schema version gate、`merge_decision_logs.doc_id`、時系列、L1/L1.5優先復旧）。
- [x] 管理操作は監査・認可境界と整合し、一般利用者の操作導線に混入しない。→ §5.1 末尾（書き込み系管理APIは一般利用者の操作導線から分離し、監査・認可・データライフサイクルの契約を先行）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 管理・復旧で必要な最小ユースケースをRACI付きで整理する。
- [x] T2 読み取り中心の管理API/CLI/画面の候補を比較する。
- [x] T3 バックアップ/復旧手順をSQLite/PostgreSQL別に定義する。
- [x] T4 Document削除/アーカイブ/所有者移管のADR要否を判定する。
- [x] T5 代表的な復旧演習をintegration testまたはrunbook検証で確認する。

T1-T4は、`02_Architecture/data_model_operations_overview.html` の `5.1 管理・復旧・棚卸しの最小運用境界` で契約レベルの整理を完了した。T5は `DATA-MAINT-02` の代表SQLite復旧演習とrunbook検証結果を受けて、親issueの境界確認として完了扱いにする。実装、管理UI/API、PostgreSQL実環境での復旧演習は本IssueのStop条件を維持し、別issueで扱う。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check -- 01_Plans/issues 02_Architecture`
  - `rg -n "DATA-MAINT-01|棚卸し|バックアップ|復旧確認|アーカイブ|所有者移管|Support|L1\\.5|L2\\.5|ADR" 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md 02_Architecture/data_model_operations_overview.html`
- 期待結果:
  - 管理・復旧の最小運用境界が、IssueとArchitecture文書で追跡できる。
- 未実施時の理由・代替検証:
  - Stream Dは非実装スコープのため、RACI・契約境界・Stop条件の文書整合で代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: DBを直接操作する手順だけを正式運用にする。誤操作と権限逸脱のリスクが高いため採用しない。
- 代替案B: 管理画面を一気に作る。権限・監査・削除方針が未確定のままUIが先行するため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 管理機能が過剰に強くなり、サポート担当が本文や未レビュー情報へアクセスしやすくなる。
- 影響範囲: Backend API、認可、運用文書、監査、DB移行。
- ロールバック手順: 書き込み系管理操作を無効化し、読み取り中心の棚卸しと手動バックアップ手順に戻す。

## 10) Additional context

- ADR化が必要になる条件: 削除、保管期限、所有者移管、監査保持、管理者閲覧権限を方針として固定する場合。

---

## 11) 運用境界（含む / 含まない）

- 含む:
  - 管理・復旧・棚卸しのrunbook要件整理（SQLite/PostgreSQL）。
  - 例外時のRACI（Platform operator / Security officer / Support）定義。
  - Document復旧時の`merge_decision_logs`整合チェック要件。
- 含まない:
  - 本Issue内での管理API/管理UI実装。
  - 法域別の保持期限自動判定。
  - サポート担当への本文閲覧権限付与。

## 12) 受入条件の補完（AC gap fill）

- [x] AC-01: 障害種別（破損/誤削除/契約ドリフト）ごとに一次対応SLA目安を記述する。
- [x] AC-02: 復旧演習結果に `成功条件 / 中断条件 / エスカレーション先` を明記する。
- [x] AC-03: 共有前確認（未レビュー本文・PII抑制）を復旧runbookに組み込む。

## 13) 例外時フロー（提出成果）

1. 障害検知・起票（Support）。
2. 影響分類（Contract / Maintenance / Support）。
3. 共有制御（safeMode既定ON、二次共有抑止）。
4. 復旧方式選択（DB restore / Document再投入）。
5. 整合確認（`documents` と `merge_decision_logs`）。
6. 事後レビューと境界表更新。

## Stream I Phase status

- Phase 1 Read: 完了（Read Order上流と関連ADRを確認済み）
- Phase 2 ADR/論点分離: 完了（契約ドリフト、運用保守、俯瞰境界を独立Issue化）
- Phase 3 Plan: 完了（受入条件・非目標・検証計画を明文化）
- Phase 4 Execute: 完了（Draft本文・依存関係・AC gapを更新）
- Phase 5 Verify: 完了（`git diff --check` と `rg` による整合確認を実施）
- Phase 6 Proceed/Stop: Proceed（DB実装変更なし。Issue計画整備のみ継続可能）


## 14) Stream D fail-safe判定（Stop/Proceed）

- 後方互換ルール: `schemas.md` の version gate 運用を前提にし、復旧手順で契約判定を先行させる。
- support level: 復旧対象を `L1/L1.5` 優先、`L2/L2.5` は「埋め込み往復保持まで」として扱う。
- 運用責務衝突: 削除・所有者移管・閲覧権限は未確定（Pending）のため、実装着手条件を満たすまで **Stop**。
- 判定: **Stop**（DecisionStatus=Pendingのため、契約整備以外へ進まない）。

## 15) Stream D → 下流引き渡しチェックリスト

- [x] 復旧手順は `L1/L1.5` を標準運用対象、`L2/L2.5` を契約整合チェック対象として分離した。
- [x] 共有前確認（未レビュー本文・PII抑制・safeMode既定ON）を復旧runbook要件に含めた。
- [x] `documents` と `merge_decision_logs` の整合検証を復旧フロー必須条件として固定した。
- [x] Pending論点（削除/所有者移管/管理者閲覧権限）は ADR化前に実装しない Stop 条件として明示した。

## 16) Stream D verification note（2026-05-20）

- 本Issueは契約・運用境界の計画文書として維持し、backend/frontend実装検証は対象外とする。
- 進行判定は `Status / Priority / Dependencies / Related ADR` と Stop条件（Section 14）の整合で行う。
- 実装着手は `DecisionStatus=Fixed` 化と ADR承認後に別Issueで管理する。


## 17) Stream D phase sync（2026-05-20）

### Context
- DecisionStatus=Pending のため、運用runbook実装へ進む前に契約前提の固定が必要。

### Decision
- 本Issueは docs-check に限定し、復旧実装・管理UI/API実装は別Issueへ分離する。
- Verify/調整が3回超過または上位契約崩壊時はStopを継続する。

### Consequences
- Stream Dの停止条件が明文化され、前提未確定のまま実装へ越境するリスクを抑制できる。

## 18) Stream B phase sync（2026-05-20）

### Context
- Stream B 対象範囲で、schema/CRUD境界/運用責務の差分を再読した。

### Decision
- `DocumentV2` support level は `L1/L1.5/L2/L2.5/L3/L0` を固定し、未分類を `L2.5` として扱う。
- backward compatibility は version gate 優先で固定し、`version: 2` の非互換変更を禁止する。
- DB/API依存が未確定の統合点は read-only contract として公開し、mock-first で検証する。

### Consequences
- Plan→Execute→Verify→Proceed の判定を docs-check で再現できる。
- Self-correction は最大3回で停止条件を維持し、越境実装を防止できる。

## 19) Stream D Phase execution log（2026-05-20）

1. Read: `DATA-MODEL-OPS-01` / `DATA-CONTRACT-01` / `data_handling.md` の関連境界を再読。
2. Context/Decision/Consequences: Pending論点と Stop条件を維持する判断を再確認。
3. CRUD境界固定: 復旧対象を `L1/L1.5` 優先、`L2/L2.5` は契約整合チェック対象に限定。
4. ドリフト監査反映: `Document.version` と `documents`/`merge_decision_logs` 整合確認を必須化。
5. 運用復旧手順整備: docs-only runbook導線（safeMode既定ON/PII抑制）を明文化。
6. Verify: docs-checkでIssue/Architecture間の語彙一致を確認。
7. Self-correction<=3: 3回超過でStop継続。
8. Final: DecisionStatus=Pendingの間は実装へ越境しない。

## 20) Stream D maintenance runbook boundary（2026-05-24）

### Context

- `DATA-MODEL-OPS-01` のサポートレベル整理により、MVPで標準保守するデータと、契約のみ保持するデータの境界が明確になった。
- ただし、Platform operator / Security officer / Support が本番導入前に必要とする、棚卸し、バックアップ、復旧確認、支援情報共有、削除/所有者移管のGo/No-Goがまだ一覧化されていなかった。

### Decision

- `02_Architecture/data_model_operations_overview.html` に `5.1 管理・復旧・棚卸しの最小運用境界（DATA-MAINT-01）` を追加し、運用ごとに主担当、承認者、対象データ、MVPで許容する手段、必須確認、Stop/ADR化条件を固定した。
- MVPで許容する管理運用は、読み取り専用の棚卸し、環境標準のバックアップ、検証環境での復旧確認、本文を含まない支援情報共有に限定する。
- ドキュメント本文の横断閲覧、アーカイブ、削除、所有者移管、ユーザーライフサイクル管理、SCIM、書き込み系管理API/UIは、ADRまたは別issueで合意するまで実装しない。

### Consequences

- T1-T4は契約レベルで完了した。T5は `DATA-MAINT-02` から返された代表SQLite復旧演習とrunbook検証をもって、本Issueの境界確認として完了扱いにする。
- `DecisionStatus=Pending` と Stop判定は維持する。今回の更新は、実装へ進むための承認ではなく、実装を始める前に必要な判断材料の整理である。
- バックアップ保持期間、暗号化、外部保管、法域ごとの保持期限は、製品一律の規定ではなく、各組織が検討する運用方針として扱う。

### Verify

- `git diff --check -- 01_Plans/issues 02_Architecture`
- `rg -n "DATA-MAINT-01|棚卸し|バックアップ|復旧確認|アーカイブ|所有者移管|Support|L1\\.5|L2\\.5|ADR" 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md 02_Architecture/data_model_operations_overview.html`

## 21) DATA-MAINT-02 recovery evidence handoff（2026-05-24）

### Context

- `DATA-MAINT-02` は、本Issueから分離した代表的な復旧演習のフォローアップである。
- PR #2259 は、SQLite上で `documents` と `merge_decision_logs` を対象にバックアップ、復旧、整合確認を行うbackend integration testを追加した。
- PR #2260 は、PostgreSQL演習がローカル環境では `docker` コマンド不在のため未実施であることを記録し、Docker利用可能環境での再実施条件を残した。
- PR #2260 は、公開文書の復旧手順を、各組織が判断するための最小限の支援情報として整理した。保持期間、暗号化、保管先、法域ごとの要件は、製品一律の規定ではなく組織ごとの検討事項として扱う。

### Decision

- 本IssueのT5は、代表SQLite復旧演習とrunbook検証が揃ったため、親issueの境界確認として完了扱いにする。
- PostgreSQL実環境での復旧演習は、`DATA-MAINT-02` の再実施条件として維持する。これを理由に、新しいADRは起票しない。
- 削除、アーカイブ、所有者移管、管理者による本文閲覧、書き込み系管理API/UIのStop条件は変更しない。これらは引き続きADRまたは別issueで合意するまで実装しない。

### Consequences

- `DATA-MAINT-01` は、管理・復旧・棚卸しの設計境界と代表復旧証跡を持つ状態になった。
- 製品リリース全体は、PostgreSQL compose演習、候補版レベルのリリースゲート記録、主要操作E2E証跡が揃うまで Conditional / No-Go を維持する。
- 本handoffは、既存の運用境界を実装へ進める承認ではなく、上流issueへ証跡を戻すための整理である。

### Verify

- PR #2259: SQLite復旧integration testを追加し、GitHub Actions `CI` run 9082 が success。
- PR #2260: PostgreSQL演習の未実施理由と再実施条件を記録し、GitHub Actions `CI` run 9084 が success。
- `git diff --check -- 01_Plans/issues`
- `01_Plans/issues/validate_active_issue_memos.py`
- `01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `01_Plans/triage_actionable_plans.py`
- `01_Plans/tests/test_triage_actionable_plans.py`
## 22) DATA-MAINT-02 recovery exercise handoff（2026-05-25）

### Context

- `DATA-MAINT-02` で、代表Documentと `merge_decision_logs` を持つSQLite隔離DBのバックアップ/復旧演習をintegration testとして追加した。
- 復元後に `Document.version`、Document `id`、card review flags、embedded merge suggestion decision、`merge_decision_logs` のgroup/snapshot順序、SafeModeによるexportブロックを確認した。
- PostgreSQL compose演習は、現在のローカルPowerShell環境で `docker` / `docker compose` が利用できないため未実施とし、再開条件を `DATA-MAINT-02` に記録した。

### Decision

- T5は **Conditional Go** として完了扱いにする。SQLite代表演習はGo、PostgreSQL本番相当演習は環境準備後に再判定する。
- 本IssueのStop条件は維持する。削除、アーカイブ、所有者移管、管理者本文閲覧、保持期間、暗号化、外部保管の方針固定は、引き続きADRまたは別issueなしに実装しない。

### Evidence

- `03_Implement/backend/tests/test_data_maintenance_recovery_exercise.py`
- `03_Implement/backend/.venv/Scripts/python.exe -m pytest tests/test_data_maintenance_recovery_exercise.py -q --basetemp .pytest_tmp_data_maint_02 -p no:cacheprovider` -> Pass: 1 test
- `03_Implement/backend/.venv/Scripts/python.exe -m pytest --basetemp .pytest_tmp_data_maint_02_full -p no:cacheprovider` -> Pass: 257 passed / 19 skipped

## 23) DATA-MAINT-03 split and verification intake（2026-05-31）

### Context

- PR #2280 は、`DATA-MODEL-OPS-01` をDoneへ進め、ER/CRUD俯瞰とMVP運用境界の証跡を整理した。ただしmain未反映の間は、本Issue側では参照証跡として扱う。
- PR #2281 は、`DATA-CONTRACT-01` の契約ドリフト検証結果を追記し、`DocumentV2` / API / frontend / backend の支援レベル整合を再確認した。
- 本Issueは、読み取り専用の棚卸し、環境標準のバックアップ、検証環境での復旧確認、本文を含まない支援情報共有までは運用境界を持つ。一方で、削除、アーカイブ、所有者移管、管理者本文閲覧、監査ログ閲覧、保持期限管理は、組織の責任・監査・法務判断に強く依存する。

### Decision

- 高権限データライフサイクル操作は、本Issueの曖昧な残課題として残さず、`DATA-MAINT-03` に分割して追跡する。
- `DATA-MAINT-01` は引き続き `Status=Open` / `DecisionStatus=Pending` とする。今回の更新は実装承認ではなく、読み取り中心の運用境界と高権限操作の判断待ちを分けるための整理である。
- 削除、アーカイブ、所有者移管、管理者本文閲覧、監査ログ閲覧、保持期限管理のいずれかを製品標準機能にする場合は、`DATA-MAINT-03` で対象操作・権限・監査・復旧不能性・共有抑制・検証レベルを整理し、必要に応じてADRを先行する。

### Consequences

- `DATA-MAINT-01` は、管理・復旧・棚卸しの最小運用境界を扱う親issueとして維持できる。
- `DATA-MAINT-03` は、管理者や運用者が通常の保守作業を越えて利用者本文、履歴、削除不能性、所有権へ影響する操作を判断するための専用issueになる。
- 管理API、管理UI、CLI、外部監査連携に高権限操作を追加する作業は、`DATA-MAINT-03` または後続ADRの判断が固定されるまで着手しない。

### Verify

- `git diff --check -- 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 02_Architecture/data_model_operations_overview.html`
- `rg -n "DATA-MAINT-03|削除|アーカイブ|所有者移管|管理者本文閲覧|保持期限|ADR" 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md 02_Architecture/data_model_operations_overview.html 02_Architecture/api.md`

## 24) ADR-0035 / DATA-MAINT-04 判断ルート同期（2026-06-01）

### Context

- PR #2285 で `ADR-0035` が main に反映された。`ADR-0035` は、削除、アーカイブ、所有者移管、管理者本文閲覧、保持期限自動化を、MVP/製品化の標準管理機能にしない境界として提案している。
- PR #2287 で `DATA-MAINT-04` が Draft issue として main に反映された。`DATA-MAINT-04` は、本文を含まない監査メタデータ閲覧の候補であり、`ADR-0035` が Accepted または置き換えられるまで着手しない。
- この親issueのヘッダーと依存メタデータには、具体的な判断先ができた後も「将来ADR」相当の表現が残っていた。

### Decision

- 抽象的な将来判断先ではなく、`ADR-0035` と `DATA-MAINT-04` を明示的な参照先にする。
- `DATA-MAINT-01` は引き続き `Status=Open` / `DecisionStatus=Pending` とする。今回の同期は、実装承認でも親issueの完了判断でもない。
- 読み取り専用の棚卸し、バックアップ、復旧演習、本文を含まない支援情報共有までを、この親issueで整理済みの計画・証跡境界として扱う。削除、所有者移管、本文閲覧、保持期限、監査閲覧の実装は、後続issue/ADRの判断ルートに分ける。

### Consequences

- 実装者は、曖昧な将来判断待ちではなく、具体的な参照先をたどってGo/No-Goを確認できる。
- `DATA-MAINT-03` は高権限ライフサイクル操作の判断issue、`ADR-0035` は製品境界の Proposed ADR、`DATA-MAINT-04` は本文を含まない監査メタデータ閲覧の Draft 候補として維持する。
- `PRODUCT-QA-01` / `MVP-EXIT-01` は、`ADR-0035` / `DATA-MAINT-03` と必要な運用証跡が解決するまで、`DATA-MAINT-01` を完全なリリース許可済みとして扱わない。

### Verify

- `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py`
- `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py`
- `git diff --check -- 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`
- `rg -n "将来ADR|ADR-0035|DATA-MAINT-04|DecisionQueueRef|監査メタデータ" 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`

## 25) DATA-MAINT-01 operational readiness packet（2026-06-02）

### Context

- `DATA-MAINT-01` は引き続き Open / P2 の親Issueとして、管理・復旧・棚卸し運用の最小境界を整理する。
- `ADR-0035`、`DATA-MAINT-03`、`DATA-MAINT-04` は明示的な参照先であり、本Issueから高権限操作や本文閲覧機能を実装許可しない。
- 本更新は実装承認ではなく、Platform operator / Security officer / Support / Productization が同じ証跡で Go/No-Go を判断できるように、運用readinessを1か所にまとめる。

### Operational readiness evidence

| Readiness item | Minimum evidence | Primary stakeholder | Stop condition |
| --- | --- | --- | --- |
| Supported data surface | `documents` and `merge_decision_logs`; `DocumentV2` support level `L1/L1.5` first, `L2/L2.5` as contract-alignment check only | Platform operator | `L2/L2.5` を完全サポート扱いする |
| Allowed maintenance action | read-only inventory, environment-standard backup, SQLite recovery exercise, bodyless support metadata sharing | Platform operator / Support | admin API/UI/CLI実装、本文閲覧、削除、アーカイブ、所有権移管 |
| Recovery evidence | backup source, restore target, restored document count, `merge_decision_logs` consistency, `Document.version` gate result | Platform operator | restore count mismatch or version drift treated as pass |
| Support evidence | metadata-only bundle, SafeMode default ON, no unreviewed body text, explicit reason and recipient | Support / Security officer | document body or unreviewed review text included by default |
| Privileged lifecycle boundary | deletion, archival, ownership transfer, retention automation, body audit viewing are routed to `DATA-MAINT-03` / `ADR-0035` / `DATA-MAINT-04` | Security officer | parent issue used as direct implementation approval |
| Productization gate | SQLite recovery evidence accepted; PostgreSQL compose rehearsal, release-candidate E2E, viewport/screenshot, and privileged lifecycle gates remain separate | Productization Program Owner | DATA-MAINT-01 treated as full release approval |

### Stakeholder operating view

- Platform operator can use this issue to confirm what data can be inventoried, backed up, restored, and checked without high-privilege product operations.
- Security officer can use this issue to detect when a requested operation has crossed into privileged lifecycle policy and must be handled by `DATA-MAINT-03` / `ADR-0035`.
- Support can use this issue to prepare bodyless diagnostic context, but cannot use it to justify sharing document bodies or unreviewed review content.
- Productization can use this issue as maintenance-readiness input, but must continue to rely on `PRODUCT-QA-01` / `MVP-EXIT-01` for release readiness.

### Implementation guard

- Do not implement admin API, admin UI, CLI mutation commands, document body browsing, deletion, archival, ownership transfer, or retention automation from this parent issue.
- Do not treat `DATA-MAINT-04` bodyless metadata viewing as production-ready until its Draft gate is explicitly lifted.
- Do not treat PostgreSQL recovery rehearsal as complete until Docker/Compose execution evidence is captured in the dedicated follow-up lane.
- If a requested maintenance action needs document body access, user lifecycle mutation, retention policy, or legal/organizational approval, keep this issue at planning boundary and route the decision to the appropriate child issue or ADR.

### Verify / Proceed

- Verify command remains docs-check only:
  - `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
  - `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py`
  - `git diff --check -- 01_Plans\issues\issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`
  - `rg -n "DATA-MAINT-01 operational readiness|Supported data surface|Allowed maintenance action|Recovery evidence|Support evidence|Privileged lifecycle boundary|Productization gate|Implementation guard|DATA-MAINT-04|ADR-0035" 01_Plans\issues\issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`
- Proceed: Conditional-Go for docs-only maintenance-readiness reference.
- Stop: Any implementation request, document body access, privileged lifecycle mutation, PostgreSQL rehearsal being marked complete without evidence, or DATA-MAINT-01 being treated as full release approval.
