# Issue Draft: DATA-MAINT-01 管理・復旧・棚卸し運用の整備

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/backend/`, `03_Implement/frontend/`, `04_Documentation/operations.md`, `02_Architecture/data_model_operations_overview.md`
- Related Backlog: `DATA-MAINT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/enterprise_architecture.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DATA-MAINT-01
- RequirementStatement: 想定ステークホルダーが組織運用で必要とする、ドキュメント一覧、アーカイブ/削除、バックアップ、復旧、ユーザー棚卸し、データ検証の最小運用を設計・実装できるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=Platform operatorが小規模組織でkj-atlasを運用する / 操作=文書一覧、利用停止ユーザー確認、バックアップ、復旧演習を行う / 期待結果=標準手順で安全に状況確認と復旧ができる / 除外=大規模マルチテナント管理、法務上の保持期限自動判定。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0033`

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

- [ ] Platform operatorが文書件数、更新日時、ユーザー事前登録状態を確認できる。
- [ ] バックアップと復旧の標準手順が、SQLite/PostgreSQLそれぞれで説明されている。
- [ ] Document削除/アーカイブの要否とリスクが整理され、実装する場合はGo/No-Go条件がある。
- [ ] サポート共有用の情報から、不要な本文や未レビュー情報を除外する方針が明示されている。
- [ ] `merge_decision_logs` とDocument復旧の整合条件が検証される。
- [ ] 管理操作は監査・認可境界と整合し、一般利用者の操作導線に混入しない。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 管理・復旧で必要な最小ユースケースをRACI付きで整理する。
- [ ] T2 読み取り中心の管理API/CLI/画面の候補を比較する。
- [ ] T3 バックアップ/復旧手順をSQLite/PostgreSQL別に定義する。
- [ ] T4 Document削除/アーカイブ/所有者移管のADR要否を判定する。
- [ ] T5 代表的な復旧演習をintegration testまたはrunbook検証で確認する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check -- 01_Plans 02_Architecture 03_Implement 04_Documentation`
  - `cd 03_Implement/backend && python -m pytest`
  - `rg -n "DATA-MAINT-01|backup|restore|archive|provision" 01_Plans 02_Architecture 03_Implement 04_Documentation`
- 期待結果:
  - 管理・復旧の最小運用が、文書と実装の両方で追跡できる。
- 未実施時の理由・代替検証:
  - 実装前は、RACI、API候補、runbook案、リスク表で代替する。

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

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
