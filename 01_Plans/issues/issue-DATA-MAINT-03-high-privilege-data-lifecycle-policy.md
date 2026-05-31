# Issue Draft: DATA-MAINT-03 高権限データライフサイクル方針の判断

- Type: Security
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`, `01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/enterprise_architecture.md`, `02_Architecture/api.md`
- Related Backlog: `DATA-MAINT-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `02_Architecture/data_model_operations_overview.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DATA-MAINT-03
- RequirementStatement: 削除、アーカイブ、所有者移管、管理者本文閲覧、監査ログ閲覧、保持期限管理を製品標準機能にするか、組織ごとの運用判断に留めるかを決める。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=Productization Program Owner、Security officer、Platform operatorが本番導入可否を判断する / 操作=高権限データ操作の方針案を読む / 期待結果=実装してよい操作、ADRが必要な操作、組織判断に委ねる操作が区別できる / 除外=本Issue内での削除API、管理UI、本文横断閲覧機能の実装。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: Future ADR for data lifecycle and privileged maintenance operations

## 1) 課題 / Problem statement

- `DATA-MAINT-01` は、読み取り中心の棚卸し、バックアップ、復旧確認、本文を含まない支援情報共有を整理した。
- 一方で、削除、アーカイブ、所有者移管、管理者本文閲覧、監査ログ閲覧、保持期限管理は、導入組織の責任・監査・法務判断に強く依存する。
- これらを標準機能として実装すると、SafeMode、共有範囲、個人情報、未レビュー情報、監査保持、復旧不能性に影響するため、設計方針なしに実装へ進めない。

## 2) 背景 / Context

- `ADR-0033` は、Admin maintenance ops を `L0: Planned` とし、削除/保管期限/所有者移管/復旧手順を完了扱いにしない。
- `data_model_operations_overview.md` は、アーカイブ・削除・所有者移管をMVPでは実装しないと明記している。
- `api.md` は、管理者向け一覧、削除、アーカイブ、所有者移管、保管期限管理を非MVPまたは別Issueで扱う拡張としている。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 利用者が安心して考え途中の情報を預けるには、誰が本文や履歴に触れるかを事前に説明できる必要がある。
- 安全（THREAT_MODEL / SafeMode）: 管理者本文閲覧や削除は、未レビュー情報の共有抑制や復旧可能性を直接変える。
- 企業・行政要件（enterprise_architecture）: 権限分掌、監査保持、削除権限、所有者移管は組織の内部統制に関わる。
- 後方互換（schemas）: 物理削除やライフサイクル状態追加は、Document復旧、merge decision log、review attributionの整合を変える可能性がある。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 高権限データ操作の分類表とGo/No-Go条件。
  - ADR化が必要な条件の整理。
  - `DATA-MAINT-01`、`DATA-CONTRACT-01`、`PRODUCT-QA-01` への判断導線。
- 変更の最小単位:
  - まず本Issueで、操作ごとのリスク、必要承認、実装前提、検証レベルを定義する。
  - 製品標準として実装する操作が1つでもある場合、ADRを起票してから実装Issueへ分割する。
- 非目標:
  - このIssueで削除、アーカイブ、所有者移管、管理者本文閲覧、監査ログ閲覧を実装しない。
  - 法域ごとの保持期限や削除義務を製品一律ルールとして決めない。

## 5) 受入条件 / Acceptance criteria

- [ ] 高権限操作ごとに、MVPでは禁止/保留/組織判断/実装候補のいずれかが明示されている。
- [ ] ADRが必要な操作と、内部issueだけで進められる操作が分かれている。
- [ ] SafeMode、share/export、public exposure、review attribution、merge decision logへの影響が記載されている。
- [ ] 実装する場合の最小検証レベル（docs-check/unit/integration/e2e）が定義されている。
- [ ] `DATA-MAINT-01` のStop条件を解除する条件が明示されている。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 高権限操作の分類表を作る。
- [ ] T2 Productization Program Owner / Security officer / Platform operator の承認観点を整理する。
- [ ] T3 ADR化が必要な操作を選別し、ADR候補のDecision内容を準備する。
- [ ] T4 実装候補を管理API、CLI、運用手順、外部監査連携に分ける。
- [ ] T5 `DATA-MAINT-01`、`DATA-CONTRACT-01`、`PRODUCT-QA-01` のゲート条件へ戻す。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check -- 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`
  - `rg -n "DATA-MAINT-03|削除|アーカイブ|所有者移管|管理者本文閲覧|保持期限|ADR" 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md 02_Architecture/data_model_operations_overview.md 02_Architecture/api.md`
- 期待結果:
  - 未決の高権限操作が、DATA-MAINT-01の曖昧な残課題ではなく、独立した判断待ちissueとして追跡できる。
- 未実施時の理由・代替検証:
  - なし。

## 8) 代替案 / Alternatives considered

- 代替案A: `DATA-MAINT-01` に未決論点を残し続ける。復旧・棚卸しの完了範囲と高権限操作の判断待ちが混ざるため採用しない。
- 代替案B: すぐADRを作る。現時点では採用する製品方針が未決のため、まずIssueで選択肢と承認観点を整理する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 高権限操作が通常運用の延長として扱われ、本文閲覧や削除が過剰に実装される。
- 影響範囲: API、管理UI、監査、復旧、公開文書、セキュリティレビュー。
- ロールバック手順: 高権限操作を実装Issueから外し、読み取り中心の棚卸しとバックアップ/復旧確認に戻す。

## 10) Additional context

- `DATA-MAINT-01` のStop条件を解除するには、本Issueまたは後続ADRで少なくとも対象操作、権限、監査、復旧不能性、共有抑制、検証レベルを固定する必要がある。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
