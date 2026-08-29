# Issue Draft: DATA-MAINT-03 高権限データライフサイクル方針の判断

- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `01_Plans/issues/done/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`, `01_Plans/issues/done/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`, `02_Architecture/data_model_operations_overview.html`, `02_Architecture/enterprise_architecture.html`, `02_Architecture/api.md`
- Related Backlog: `DATA-MAINT-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/issues/done/issue-DATA-MAINT-04-metadata-only-audit-viewing.md`, `02_Architecture/data_model_operations_overview.html`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Expected verification level: `docs-check`

## Done 2026-06-20
全AC(5/5)・全タスク(5/5)達成。高権限操作の分類表完成。ADR-0035により削除/アーカイブ/所有者移管/管理者本文閲覧/保持期限管理を組織判断領域として分離。

## Requirement meta I/F（共通キー）

- RequirementID: DATA-MAINT-03
- RequirementStatement: 削除、アーカイブ、所有者移管、管理者本文閲覧、監査ログ閲覧、保持期限管理を製品標準機能にするか、組織ごとの運用判断に留めるかを決める。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=Productization Program Owner、Security officer、Platform operatorが本番導入可否を判断する / 操作=高権限データ操作の方針案を読む / 期待結果=実装してよい操作、ADRが必要な操作、組織判断に委ねる操作が区別できる / 除外=本Issue内での削除API、管理UI、本文横断閲覧機能の実装。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure

## Decision resolution 2026-07-13

`ADR-0035` を「高権限操作を標準機能にしない境界」としてAcceptedした。削除・アーカイブ・所有者移管の包括解禁は不採用であり、管理者本文閲覧・横断検索・保持期限自動化も標準導線へ追加しない。本文を含まない監査メタデータ閲覧の境界整理だけを `DATA-MAINT-04` で継続できる。本決定により、本IssueのDoneとDecisionStatusが一致した。

## 1) 課題 / Problem statement

- `DATA-MAINT-01` は、読み取り中心の棚卸し、バックアップ、復旧確認、本文を含まない支援情報共有を整理した。
- 一方で、削除、アーカイブ、所有者移管、管理者本文閲覧、監査ログ閲覧、保持期限管理は、導入組織の責任・監査・法務判断に強く依存する。
- これらを標準機能として実装すると、SafeMode、共有範囲、個人情報、未レビュー情報、監査保持、復旧不能性に影響するため、設計方針なしに実装へ進めない。

## 2) 背景 / Context

- `ADR-0033` は、Admin maintenance ops を `L0: Planned` とし、削除/保管期限/所有者移管/復旧手順を完了扱いにしない。
- `02_Architecture/data_model_operations_overview.html` は、アーカイブ・削除・所有者移管をMVPでは実装しないと明記している。
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

- [x] 高権限操作ごとに、MVPでは禁止/保留/組織判断/実装候補のいずれかが明示されている。
- [x] ADRが必要な操作と、内部issueだけで進められる操作が分かれている。
- [x] SafeMode、share/export、public exposure、review attribution、merge decision logへの影響が記載されている。
- [x] 実装する場合の最小検証レベル（docs-check/unit/integration/e2e）が定義されている。
- [x] `DATA-MAINT-01` のStop条件を解除する条件が明示されている。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 高権限操作の分類表を作る。
- [x] T2 Productization Program Owner / Security officer / Platform operator の承認観点を整理する。
- [x] T3 ADR化が必要な操作を選別し、ADR候補のDecision内容を準備する。
- [x] T4 実装候補を管理API、CLI、運用手順、外部監査連携に分ける。
- [x] T5 `DATA-MAINT-01`、`DATA-CONTRACT-01`、`PRODUCT-QA-01` のゲート条件へ戻す。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check -- 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`
  - `rg -n "DATA-MAINT-03|削除|アーカイブ|所有者移管|管理者本文閲覧|保持期限|ADR" 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md 02_Architecture/data_model_operations_overview.html 02_Architecture/api.md`
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

## 11) 高権限操作の初期分類（2026-05-31）

この分類は、実装許可ではなく判断支援である。製品標準機能として採用する操作が1つでもある場合は、ここで示した論点をADRに移し、権限、監査、復旧、共有抑制、検証レベルを固定してから実装Issueへ進める。

| 操作 | MVPでの分類 | 判断理由 | ADR要否 | 最小検証レベル |
|---|---|---|---|---|
| ドキュメントのアーカイブ | 保留 / 実装候補 | 削除より復旧可能性は高いが、一覧表示、共有、review pack、復旧時の扱いが変わる。 | 製品標準の状態遷移にする場合はADR。組織内の手動退避手順に留める場合はissueで足りる。 | docs-check + integration。UIを持つ場合はe2e。 |
| ドキュメントの削除 | 原則保留 / MVPでは禁止 | `documents` と `merge_decision_logs` の整合、review attribution、復旧不能性、共有済み成果物との関係に影響する。 | 必須。物理削除、論理削除、復旧可能削除のいずれを選ぶかをADRで固定する。 | integration + e2e + security review。 |
| 所有者移管 | 保留 | 所有者は共有範囲、レビュー責任、監査上の説明責任に関わる。単なるID付け替えでは扱えない。 | 必須。移管理由、承認者、履歴、通知、review attributionとの関係をADRで固定する。 | integration + e2e。 |
| 管理者本文閲覧 / 横断検索 | MVPでは禁止 | 利用者が安心して考え途中の情報を預ける価値に直結し、SafeModeや共有抑制の前提を変える。 | 必須。例外運用を認める場合でも、目的、範囲、記録、通知、代替手段をADRで固定する。 | e2e + security review。 |
| 監査ログ閲覧 | 実装候補 / 範囲限定 | 読み取り専用のメタデータ閲覧は運用価値があるが、本文や未レビュー情報を含むと高リスクになる。 | メタデータ限定の一覧はissueで開始可能。保持方針や本文連動を含む場合はADR。 | integration。UIを持つ場合はe2e。 |
| 保持期限管理 | 組織判断 / 製品標準は保留 | 保持期間は法務、契約、組織ポリシーに依存し、製品一律の既定値は混乱を招きやすい。 | 自動削除や標準保持期間を製品が持つ場合はADR。判断材料の文書化だけならissueで足りる。 | docs-check。自動処理を持つ場合はintegration + e2e。 |

## 12) ADR化と内部issue化の分岐基準

- ADRが必要な変更:
  - 利用者本文、未レビュー情報、共有範囲、所有者、削除不能性、保持期限のいずれかを製品標準の振る舞いとして変える。
  - 管理者やSupportが、通常利用者の導線を越えて本文や履歴へアクセスできるようになる。
  - SafeMode、share/export、review pack、public exposure、review attribution、merge decision logの意味が変わる。
  - 組織ごとの判断事項だったものを、製品の既定値または自動処理として固定する。
- 内部issueで進められる変更:
  - 既存データを読み取り専用で棚卸しし、本文や未レビュー情報を含めない。
  - 各組織が検討するための判断材料、チェックリスト、復旧演習の証跡を整理する。
  - 管理API/UIを追加せず、既存の監査イベントやテスト証跡の参照性を改善する。

## 13) Stop解除条件

`DATA-MAINT-01` の高権限操作に関するStop条件は、少なくとも次の条件を満たすまで解除しない。

- 対象操作が、禁止、保留、組織判断、実装候補のいずれかに分類されている。
- 製品標準として実装する操作について、ADRで権限、承認、監査、復旧不能性、共有抑制、検証レベルが固定されている。
- 管理API、管理UI、CLI、外部監査連携のいずれで提供するかが、一般利用者の通常操作導線から分離されている。
- `DATA-CONTRACT-01` のDocumentV2支援レベル、`PRODUCT-QA-01` のリリースゲート、`DATA-MODEL-OPS-01` のCRUD境界と矛盾しない。

## 14) ADR-0035 proposal intake（2026-06-01）

### Context

- 本Issueの分類表により、削除、アーカイブ、所有者移管、管理者本文閲覧、監査ログ閲覧、保持期限管理のリスクとADR要否は整理済みである。
- ただし `DecisionStatus=Pending` のままだと、実装側が「どれかを製品標準機能として採用する余地がある」と誤読しやすい。
- `ADR-0033` は Admin maintenance ops を `L0: Planned` に留める判断であり、高権限操作を次の製品化準備段階で標準機能にしない判断までは明文化していない。

### Decision

- `ADR-0035` を起票し、高権限データライフサイクル操作の製品境界を提案する。
- ADR案では、削除、アーカイブ、所有者移管、管理者本文閲覧、保持期限自動化を標準機能にしない。監査ログ閲覧は、本文を含まないメタデータ閲覧候補に限り内部issueで検討可能とする。
- 本IssueはまだDoneにしない。`ADR-0035` がAcceptedになるまで、`DecisionStatus=Pending` を維持する。

### Consequences

- `DATA-MAINT-01` のStop条件は維持されるが、解除条件の参照先が `Future ADR` ではなく具体的な `ADR-0035` になった。
- `PRODUCT-QA-01` / `MVP-EXIT-01` は、削除や管理者本文閲覧の未実装を単純な欠落ではなく、提案中の製品境界として評価できる。
- ADRがAcceptedされた場合は、本Issueを `DecisionStatus=Fixed` / Doneへ進め、標準機能にしない操作と将来issueに残す操作を最終整理する。

### Verify

- `git diff --check -- 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 02_Architecture/data_model_operations_overview.html 02_Architecture/api.md`
- `rg -n "ADR-0035|高権限|管理者本文閲覧|所有者移管|保持期限|標準機能にしない|メタデータ閲覧" 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 02_Architecture/data_model_operations_overview.html 02_Architecture/api.md`

## 15) DATA-MAINT-04 split for metadata-only audit viewing（2026-06-01）

### Context

- `ADR-0035` は、監査ログ閲覧について、本文を含まないメタデータ閲覧候補に限り内部issueで検討できるとした。
- 一方で、「監査ログ閲覧」を広く解釈すると、本文閲覧、未レビュー情報閲覧、横断検索、保持期限管理、削除履歴管理と混ざりやすい。
- 本Issueは高権限操作全体の判断待ちを扱うため、本文を含まない監査メタデータ閲覧候補だけを分離して追跡できる器が必要である。

### Decision

- `DATA-MAINT-04` をDraft issueとして起票し、本文を含まない監査メタデータ閲覧の候補、除外情報、権限、検証レベルを整理する。
- `DATA-MAINT-04` は `ADR-0035` がAcceptedされるまでDraftのまま維持する。これは実装許可ではなく、ADR-0035の境界が固まった後にOpen化できるようにするための準備である。
- 本文、未レビュー情報、横断検索、保持期限、自動削除、所有者移管、監査ログを共有する標準導線は `DATA-MAINT-04` の外に置き、必要な場合は別ADRを必須とする。

### Consequences

- `DATA-MAINT-03` は、ADR-0035の決定待ちと高権限操作全体のStop条件を維持する。
- `DATA-MAINT-04` により、将来検討できる低リスク寄りの監査メタデータ閲覧候補と、ADRが必要な本文アクセス系の高権限機能を分けて追跡できる。
- `PRODUCT-QA-01` / `MVP-EXIT-01` は、監査閲覧の未実装を単純な欠落ではなく、Draft issue化された将来候補として扱える。ただしADR-0035がAcceptedされるまではリリースGoの根拠にしない。

### Verify

- `git diff --check -- 01_Plans/issues/issue-DATA-MAINT-04-metadata-only-audit-viewing.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 02_Architecture/data_model_operations_overview.html 02_Architecture/api.md`
- `rg -n "DATA-MAINT-04|監査メタデータ|本文を含まない|ADR-0035|audit metadata|audit viewing" 01_Plans/issues/issue-DATA-MAINT-04-metadata-only-audit-viewing.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 02_Architecture/data_model_operations_overview.html 02_Architecture/api.md`

## 16) ADR-0035 acceptance packet sync（2026-06-02）

### Context

- `ADR-0035` はまだ `Proposed` であり、本Issueの `DecisionStatus=Pending` は維持する。
- ただし、Deciders が承認時に確認すべき点がADR本文だけでは散らばって読めるため、Accepted化の判断材料を `Acceptance readiness packet` としてADR側に集約した。
- この更新は高権限操作の実装許可ではなく、むしろ誤って通常の管理機能として実装しないためのStop境界を明確にするものである。

### Decision

- 本Issueは `Status=Open` / `DecisionStatus=Pending` を維持する。
- `ADR-0035` をAcceptedにする前の確認項目を、次の5点に固定した。
  1. 削除、アーカイブ、所有者移管、管理者本文閲覧、保持期限自動化を標準機能にしない。
  2. 保持期間、削除義務、承認者、保管先、暗号化方式を製品一律の規定として固定しない。
  3. Support、Platform operator、管理者が標準導線で本文や未レビュー情報を横断閲覧しない。
  4. 本文を含まない監査メタデータ閲覧だけを `DATA-MAINT-04` で検討可能にする。
  5. 未実装の高権限操作を、単独のリリース阻害ではなく明示された製品境界として扱えるかを確認する。

### Consequences

- `ADR-0035` がAcceptedされた場合、本Issueは `DecisionStatus=Fixed` へ進める候補になる。ただし、実装Issueへの移行はしない。
- `DATA-MAINT-04` はAccepted後にOpen化可否を判断できるが、本文閲覧、未レビュー情報閲覧、横断検索、保持期限、自動削除、所有者移管へ拡張する場合は別ADRを必須とする。
- 本番導入組織が削除、保持期限、所有者移管、管理者本文閲覧を必須機能と判断する場合は、`PRODUCT-QA-01` / `MVP-EXIT-01` のリリース条件へ戻す。
- この更新では `ADR-0035` のStatus、runtime behavior、API、UI、公開文書、SafeMode、share/export の既定を変更しない。

### Verify

- `git diff --check -- 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`
- `rg -n "Acceptance readiness packet|Accepted 後の実装停止条件|DATA-MAINT-04|標準機能にしない|本文を含まない|DecisionStatus=Pending" 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`

---

## 17) DATA-MAINT-03 decision handoff readiness（2026-06-02）

### Context

- `ADR-0035` は `Proposed` のままであり、本Issueの `DecisionStatus=Pending` を維持する。
- 本Issueは高権限データライフサイクル操作を実装するためのIssueではなく、Deciders が標準機能にしない境界、別ADR必須の境界、内部issueで検討できる境界を判断するための証跡を保持する。
- 本更新は `DATA-MAINT-01`、`DATA-MAINT-04`、`PRODUCT-QA-01`、`MVP-EXIT-01` への参照整理であり、API/UI/CLI/runtime behavior を変更しない。

### Decision handoff matrix

| Decision area | Current route | Required evidence before movement | Stop condition |
| --- | --- | --- | --- |
| Document deletion | 標準機能にしない。再検討時は別ADRを必須とする。 | 削除モデル、監査保持、不可逆性と復旧の関係、共有済み成果物への影響 | 本Issueから delete/archive API/UI/CLI を実装する |
| Document archive | 将来の状態遷移候補に留める。 | 一覧、共有、review pack、復旧、検索への影響、利用者に見える状態モデル | archive を単純な soft delete として扱う |
| Ownership transfer | 別ADRを必須とする。 | 移管理由、承認者、通知、レビュー帰属、判断ログ上の説明責任 | owner ID の置換だけで所有者移管を表現する |
| Admin body browsing / cross-search | MVP/製品化の標準導線から除外する。 | 目的、範囲、通知、代替手段、監査、SafeMode と共有/エクスポートへの影響 | support/platform operator の標準導線に本文または未レビュー情報を含める |
| Audit metadata viewing | `DATA-MAINT-04` Draft 候補に限定する。 | メタデータのみの範囲、除外フィールド、権限モデル、検証レベル | 本文、未レビュー情報、横断検索、保持期限を `DATA-MAINT-04` に混在させる |
| Retention automation | 組織判断または法務判断の領域として扱う。 | 保持期間、削除/アーカイブの意味、法域、バックアップと復旧への影響 | 本Issueで製品既定の保持期限や自動削除を定義する |

### Stakeholder acceptance route

- Productization Program Owner: 未解決の高権限ライフサイクル操作を、隠れた実装漏れではなく明示された製品境界として扱えることを確認する。
- Security officer: 標準の support/admin 導線が、document body、未レビューの review text、review pack body、横断検索を露出しないことを確認する。
- Platform operator: 本文を含まない棚卸しや復旧の証跡は参照できるが、本Issueから高権限の変更操作を要求しない。
- Support: 本文を含まない診断用メタデータは将来候補として要求できるが、本文アクセスは別ADR/Issueを必須とする。

### Go / Hold / Stop

- Go: `ADR-0035` がAcceptedされ、本Issueがどの操作を標準機能にしないか、どの操作を別ADR必須にするかを確認できた場合に限り、`DecisionStatus=Fixed` 候補へ進める。
- Hold: `ADR-0035` がProposedのまま、または `DATA-MAINT-04` がDraftのままである間は、本IssueをPendingに維持する。
- Stop: 本Issueから admin API/UI/CLI mutation、本文閲覧、自動保持、削除、アーカイブ、所有者移管、広範な監査閲覧を実装しようとする要求を検知した場合は停止する。

### Verify / Proceed

- Verify command remains docs-check only:
  - `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
  - `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py`
  - `git diff --check -- 01_Plans\issues\issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`
  - `rg -n "DATA-MAINT-03 decision handoff|Decision handoff matrix|Document deletion|Ownership transfer|Admin body browsing|Audit metadata viewing|Retention automation|DecisionStatus=Pending|ADR-0035|DATA-MAINT-04" 01_Plans\issues\issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`
- Proceed: docs-only の判断引き継ぎとして Conditional-Go。ADR/API/UI/runtime/status は変更しない。
- Stop: runtime/API/UI/CLI の変更、`ADR-0035` のStatus変更、`DATA-MAINT-04` のStatus変更、高権限ライフサイクル操作の実装要求。

---

## 18) ADR-0035 maintainer decision packet（2026-06-06）

### Context

- `ADR-0035` は `Proposed` のままであり、本Issueは `Status=Open` / `DecisionStatus=Pending` を維持する。
- 製品境界の提案内容は、Project Maintainers が Accepted 化できるかを判断できる段階まで整理された。
- この更新では `ADR-0035` のStatus、`DATA-MAINT-04` のStatus、API/UI/CLI/runtime behavior、SafeMode、share/export、公開文書、リリース権限を変更しない。

### Decision handoff

Maintainer への推奨判断経路:

1. 現在の製品化段階では高権限ライフサイクル操作を標準機能にしない、という境界に合意できる場合に限り `ADR-0035` を Accepted にする。
2. 削除、アーカイブ、所有者移管、管理者本文閲覧/横断検索、保持期限自動化は、特定操作を後続ADRでAcceptedするまで実装対象外に置く。
3. 本文を含まない監査メタデータ閲覧だけを低リスク寄りの候補として `DATA-MAINT-04` に残し、Draft-to-Open gate で止める。
4. 組織ごとの保持期間、法的削除義務、承認経路、保管先、暗号化詳細は、プロジェクト共通の既定値ではなく導入組織の判断事項として扱う。

### Proceed / Hold / Stop

- Proceed: `ADR-0035` が現行内容でAcceptedされた場合、後続sliceで本Issueを `DecisionStatus=Fixed` 候補へ進め、`DATA-MAINT-04` のOpen-readinessを別途確認する。
- Hold: Maintainer が追加証跡や文言修正を必要とする場合、本IssueをPendingのまま維持し、実装issueを開く前に `ADR-0035` を更新する。
- Stop: この引き渡しを、管理系mutation API、管理UI、本文閲覧、文書横断検索、削除/アーカイブ、所有者移管、保持期限自動化の実装許可として扱う要求を検知した場合は停止する。

### Verify

- `git diff --check -- 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`
- `rg -n "Maintainer decision packet|ADR-0035 maintainer decision packet|Accept as written|Request changes|Reject|DecisionStatus=Pending|DATA-MAINT-04" 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`
- Proceed for this slice: docs-only の判断引き渡し改善として継続可能。ADR status と実装状態は変更しない。

---

## 19) Current-main decision freshness（2026-06-13）

### Context

- `main` は高権限データライフサイクル操作の分類、ADR-0035の提案、DATA-MAINT-04のDraft分離を含んでいる。
- ただし `ADR-0035` はまだ `Proposed` であり、本Issueは `Status=Open` / `DecisionStatus=Pending` のまま維持する。
- この更新は、2026-06-13時点で人間が次に判断すべき内容を短く取り出すためのdocs-only更新である。API/UI/CLI/runtime behavior、SafeMode、share/export、公開文書、ADR status、`DATA-MAINT-04` status は変更しない。

### Human-owned decision checklist

- Project Maintainers: `ADR-0035` を Accept as written / Request changes / Reject のどれで扱うかを明示する。
- Productization Program Owner: 導入想定組織が、削除、アーカイブ、所有者移管、保持期限自動化、管理者本文閲覧、文書横断検索を本番導入の前提条件にしているか確認する。
- QA Lead: 上記のいずれかが前提条件になる場合、`PRODUCT-QA-01` / `MVP-EXIT-01` のリリースゲートへ明示的に戻す。
- Codex: 判断が出るまで、高権限ライフサイクル操作の実装issueを開かず、既存のStop条件と検証証跡を維持する。

### Proceed / Hold / Stop

- Proceed: Maintainers が `ADR-0035` を現行内容でAcceptedにした場合、後続sliceで本Issueを `DecisionStatus=Fixed` 候補へ進める。
- Hold: Maintainers の判断が未完了、または導入想定組織の必須条件確認が未完了の場合、本IssueをPendingのまま維持する。
- Stop: この更新を、削除、アーカイブ、所有者移管、保持期限自動化、管理者本文閲覧、文書横断検索、監査本文閲覧、本文共有の実装許可として扱う要求を検知した場合は停止する。

### Verify

- `git diff --check -- 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`
- `rg -n "Current-main decision freshness|Human-owned decision checklist|Accept as written|Request changes|Reject|DecisionStatus=Pending|DATA-MAINT-04" 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`
- Proceed for this slice: docs-only の判断鮮度更新として継続可能。ADR status と実装状態は変更しない。

---

## 20) Post-2386 current-main decision freshness (2026-06-14)

### Context

- Candidate mainline reviewed: `origin/main@4a8156ffccddbfbcb3704a34899d3f644eda0185`.
- The post-2386 branch reachability and release-gate records are current, and no unmerged `codex/*` branch updated on or after 2026-06-06 remains outside main.
- This does not change the high-privilege data lifecycle decision. `ADR-0035` is still `Proposed`, this issue remains `Status=Open` / `DecisionStatus=Pending`, and `DATA-MAINT-04` remains a Draft issue.
- This update is docs-only. It does not change API, UI, CLI, runtime behavior, SafeMode, share/export defaults, public documentation, ADR status, or release authority.

### Current boundary

- No implementation permission is granted from this issue for deletion, archive, ownership transfer, admin body browsing, cross-document body search, retention automation, or broad audit viewing.
- The only lower-risk candidate still separated from this issue is metadata-only audit viewing in `DATA-MAINT-04`, and it remains blocked by the Draft-to-Open gate until `ADR-0035` is Accepted or replaced by an equivalent accepted ADR.
- If maintainers decide that any high-privilege operation should become a standard product capability, that decision requires a separate accepted ADR and a split implementation issue.

### Proceed / Hold / Stop

- Proceed: Project Maintainers explicitly Accept, replace, or reject `ADR-0035`; if accepted as written, a later slice may move this issue toward `DecisionStatus=Fixed` without opening implementation work.
- Hold: `ADR-0035` remains `Proposed`, or `DATA-MAINT-04` remains Draft without the required maintainer/security/productization confirmation.
- Stop: any request to implement high-privilege lifecycle operations, admin body access, cross-document body search, retention automation, or broad audit viewing directly from this issue.

### Verify

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py --root 01_Plans --format text`
- `git diff --check -- 01_Plans\issues\issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`
- `rg -n "Post-2386 current-main decision freshness|4a8156ffccddb|DecisionStatus=Pending|DATA-MAINT-04|ADR-0035|metadata-only audit viewing" 01_Plans\issues\issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`

---

## 21) Post-2398 governance-context decision freshness (2026-06-14)

### Context

- Current mainline reviewed: `origin/main@e6a72667dbd3794b1903264887642932f11515d9`.
- Recent CE checkpoint merges (#2395 through #2398) refreshed contract, context-bundle, AI-assist, and audit-integration readiness records, but did not change the high-privilege data lifecycle boundary.
- `ADR-0039` right-sizes project governance for the personal-OSS / pre-release phase. It reduces process weight for ordinary documentation and planning updates, but it does not implicitly accept `ADR-0035` or authorize high-privilege lifecycle implementation.
- This update is docs-only. It does not change API, UI, CLI, runtime behavior, SafeMode, share/export defaults, public documentation, ADR status, or release authority.

### Current boundary

- `ADR-0035` remains `Status: Proposed`.
- This issue remains `Status=Open` / `DecisionStatus=Pending`.
- `DATA-MAINT-04` remains Draft; metadata-only audit viewing is still a candidate discussion area, not implementation permission.
- No implementation permission is granted for deletion, archive, ownership transfer, admin body browsing, cross-document body search, retention automation, or broad audit viewing.
- If maintainers want any high-privilege operation to become a standard product capability, that choice still requires an explicit accepted ADR or an explicitly accepted replacement decision.

### Proceed / Hold / Stop

- Proceed: Project Maintainers explicitly choose Accept as written, Request changes, or Reject for `ADR-0035`; if accepted as written, a later slice may move this issue toward `DecisionStatus=Fixed` without opening implementation work.
- Hold: `ADR-0035` remains `Proposed`, or a maintainer response only says to continue general work without selecting a decision option for this high-privilege boundary.
- Stop: any request treats `ADR-0039`, this issue update, or recent CE checkpoint merges as implicit acceptance of `ADR-0035` or as permission to implement high-privilege lifecycle operations.

### Verify

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py --root 01_Plans --format text`
- `git diff --check -- 01_Plans\issues\issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans\adr\ADR-0035-privileged-data-lifecycle-boundary.md`
- `rg -n "Post-2398 governance-context decision freshness|e6a72667dbd3794|ADR-0039|DecisionStatus=Pending|Status: Proposed|DATA-MAINT-04|implicit acceptance" 01_Plans\issues\issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans\adr\ADR-0035-privileged-data-lifecycle-boundary.md`

---
