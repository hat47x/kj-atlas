# Issue Draft: DATA-MAINT-04 本文を含まない監査メタデータ閲覧の製品境界

- Type: Security
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `01_Plans/issues/issue-DATA-MAINT-04-metadata-only-audit-viewing.md`, `01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`（Done 2026-06-20）, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/api.md`
- Related Backlog: `DATA-MAINT-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md`, `02_Architecture/data_model_operations_overview.md`, `02_Architecture/api.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Expected verification level: `integration`

## Draft→Open 2026-07-13
DATA-MAINT-03 Done + ADR-0035 Acceptedにより依存充足。監査メタデータ閲覧の製品境界定義を開始可能。ただし実装許可ではなく、本文なしallowlistとread-only権限の固定が先である。

## Requirement meta I/F（共通キー）

- RequirementID: DATA-MAINT-04
- RequirementStatement: Security officer / Audit operator が、利用者本文や未レビュー情報に触れずに、共有・エクスポート・Context操作などの監査メタデータを確認できる最小境界を定義する。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`ADR-0035` がAcceptedまたは後続ADRで同等の境界が固定される / 操作=監査メタデータ閲覧の対象項目、権限、除外情報、検証レベルを読む / 期待結果=本文を含まない読み取り専用の監査閲覧候補と、ADRが必要な高権限閲覧が区別できる / 除外=本文閲覧、未レビュー情報閲覧、横断検索、保持期限管理、削除、所有者移管、監査ログを共有する標準導線。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed（`ADR-0035` Accepted 2026-07-13）
- DecisionQueueRef（未確定時の参照先）: Resolved（`ADR-0035` Accepted 2026-07-13）

## 1) 課題 / Problem statement

- `ADR-0035` は、監査ログ閲覧について「本文を含まないメタデータ閲覧候補に限り、内部issueで検討できる」とした。
- ただし、監査閲覧という言葉は、本文、未レビュー情報、横断検索、保持期限、削除履歴などを含む高権限機能として誤読されやすい。
- 誤読されたまま実装へ進むと、管理者本文閲覧やSupport向け横断検索を標準導線に入れてしまい、SafeMode、share/export、public exposure、review attribution の境界を暗黙に変える。

## 2) 背景 / Context

- `api.md` は、Document監査イベントとCE4監査契約を持つが、監査ログ閲覧UIや保持期限管理は含めていない。
- `data_model_operations_overview.md` は、Export / Context audit event を派生/読み取り中心のデータとして扱い、アプリ本体に監査ログ閲覧UIを持たない前提を書いている。
- `DATA-MAINT-03` は、高権限操作のうち監査ログ閲覧だけを、本文を含まない範囲で内部issue化可能と分類した。
- `ADR-0035` は2026-07-13にAcceptedされ、本IssueのOpen化前提は満たされた。ただし本Issueは実装許可ではなく、本文なしメタデータのallowlistとread-only境界を固定する検討器である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 利用者が安心して思考途中の情報を扱うには、運用者が確認できるものと確認できないものを説明できる必要がある。
- 安全（THREAT_MODEL / SafeMode）: 本文や未レビュー情報を監査閲覧に混ぜると、SafeModeと共有抑制の価値が弱くなる。
- 企業・行政要件（enterprise_architecture）: Security officer / Audit operator は、本文を読まずに操作事実や安全境界の逸脱有無を確認できることが望ましい。
- 後方互換（schemas）: 既存の監査イベントやDocumentV2の保存契約を変更せず、まず閲覧候補の項目と権限境界を固定する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 監査メタデータ閲覧で扱ってよい項目、扱ってはいけない項目、権限、監査証跡、検証レベルの整理。
  - `api.md` と `data_model_operations_overview.md` にある既存監査イベント契約との整合確認。
  - 実装へ進む場合の専用API/CLI/UI issue分割条件。
- 変更の最小単位:
  - まず本Issueで、本文を含まない読み取り専用メタデータの候補と、ADRが必要な高権限閲覧を分ける。
  - `ADR-0035` AcceptedによりOpen化済みだが、返却allowlist・権限・検索条件・監査証跡を固定するまで実装へ進めない。
- 非目標:
  - 本Issueで監査閲覧API、管理UI、CLI、外部監査連携を実装しない。
  - 本文、未レビュー情報、添付ファイル、Document JSON全体、review pack本文、diff本文を閲覧対象にしない。
  - 保持期限、自動削除、所有者移管、管理者本文閲覧、横断検索の方針を固定しない。

## 5) 受入条件 / Acceptance criteria

- [x] `ADR-0035` がAcceptedまたは後続ADRで同等の境界が固定されてからOpen化される。（2026-07-13充足）
- [x] 監査メタデータとして扱ってよい項目と、扱ってはいけない本文/未レビュー情報/横断検索項目が分かれている。
- [x] Security officer / Audit operator / Platform operator / Support の閲覧責務が分離されている。
- [x] SafeMode、share/export、public exposure、review attribution、merge decision logへの影響が記載されている。
- [x] 実装へ進む場合の最小検証レベルが integration として定義され、UIを持つ場合は e2e へ引き上げる条件が明記されている。
- [x] ADRが必要になる条件が明記されている。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 監査メタデータ閲覧候補を、本文を含まない項目に限定して定義する。
- [x] T2 閲覧主体と権限境界を RACI で整理する。
- [x] T3 `api.md` の既存 audit endpoint / CE4 audit 契約と矛盾しないことを確認する。
- [x] T4 実装候補を API / CLI / UI / 外部監査連携に分け、各候補の検証レベルを定義する。
- [x] T5 ADR化が必要になる拡張条件を `DATA-MAINT-03` と照合する。

## 6.1) 事前Open化ベースライン（2026-06-01）

以下は実装許可ではなく、Accepted後にOpen化した本Issueで維持する最小境界である。

### 扱ってよい監査メタデータ候補

| 区分 | 候補項目 | 根拠 | 制約 |
| --- | --- | --- | --- |
| 共通イベント | `eventType`, `schemaVersion`, `occurredAt` / `timestamp`, `traceId` | `api.md` のDocument監査イベント / CE4監査契約 | 本文や添付ファイルをたどれる追加payloadを付けない。 |
| 対象参照 | `docId` または既存イベントの対象ID、`eventVersion` | `GET /docs/{doc_id}` / export audit / access-control監査 | Document JSON全体、カード本文、diff本文、review pack本文は返さない。 |
| 操作情報 | `action`, `exportKind`, `operation`, `channel`, `command`, `result`, `rejectReasonCode` | export audit / context audit / CE4監査4点 | 操作事実の確認に限定し、検索条件として本文語句を受け付けない。 |
| SafeMode / 共有境界 | `safeMode`, `readOnly`, `visibility`, `decision.allow`, `decision.reason`, `policyRefPresent` | access-control監査とshare/export境界 | `policyRef` 生値、roles/groups生値、共有先の個人情報は返さない。 |
| CE4同値性 | `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `sourceBundleHash` | CE4 API/CLI監査契約 | hashは同値性確認に限って扱い、元queryやbundle本文を復元・表示しない。 |
| Actor最小情報 | `principalType`, masked principal id, `actorRef` など既存契約の匿名化済み参照 | strict provisioning / review attribution境界 | email、生IdP subject、外部UID、氏名の横断検索を含める場合は別ADR。 |

### 除外する情報

- 利用者本文、カード本文、島の本文、添付ファイル、Document JSON全体。
- 未レビュー情報、根拠未確認の要約、review pack本文、diff本文、ContextBundle本文。
- `policyRef` 生値、roles/groups生値、IdP subject、external UID、API key、token、secret。
- 削除履歴管理、保持期限管理、所有者移管、管理者本文閲覧、本文横断検索。
- 監査メタデータを標準機能として共有する導線。必要な場合は別ADRで目的、共有先、除外項目、証跡、無効化手順を固定する。

### RACI

| 主体 | 責務 | このIssueでの扱い |
| --- | --- | --- |
| Security officer | 監査閲覧の目的、除外情報、共有抑制の妥当性を確認する | Accountable。Open化前に `ADR-0035` のAcceptedまたは同等ADRを確認する。 |
| Audit operator | 本文を読まずに操作事実、SafeMode逸脱、監査4点の欠損を確認する | Responsible。読み取り専用メタデータだけを扱う。 |
| Platform operator | 監査イベントの保存先、adapter設定、traceIdの追跡可能性を確認する | Consulted。DBや外部adapterの直接閲覧を標準導線にしない。 |
| Support | 利用者から受け取った再現情報と照合する | Informed。本文や未レビュー情報を閲覧する主体にはしない。 |
| Document owner | 自分のドキュメントの共有範囲と成果物を説明する | Consulted。監査閲覧の標準権限は持たせない。 |

### API / 実装候補の検証境界

- Draft中は `api.md` の既存 audit endpoint / CE4契約を変更しない。閲覧API、管理UI、CLI、外部監査連携も実装しない。
- `ADR-0035` Accepted後にOpen化する場合、最初の候補は読み取り専用のメタデータ一覧/詳細契約に限定する。最小検証レベルは integration とし、UIを追加する場合は代表的なマウス操作・キーボード操作を含む e2e を必須にする。
- 監査送信の fail-open dispatcher 方針と、閲覧系の権限判定は分けて検証する。送信失敗が本体処理を止めないことと、閲覧権限が緩むことを混同しない。
- 本文、未レビュー情報、横断検索、保持期限、自動削除、所有者移管、監査メタデータの標準共有導線に進む場合は、`DATA-MAINT-03` と照合したうえで別ADRを先行する。

## 6.2) Open readiness packet（2026-06-02）

本IssueをDraftからOpenへ進める場合、`ADR-0035` のAcceptedまたは同等ADRに加えて、次のOpen化証跡を先にそろえる。これは実装許可ではなく、実装Issueを分割できる状態かを判断するための入口条件である。

### Representative read-only scenarios

| Scenario | 操作主体 | 目的 | 返してよい情報 | Stop条件 |
| --- | --- | --- | --- | --- |
| A1 share/export event lookup | Audit operator | 共有またはexportの発生有無と安全境界を確認する | event type, timestamp, traceId, docId, exportKind, safeMode, result, rejectReasonCode | review pack本文、カード本文、共有先個人情報、policyRef生値を返す場合 |
| A2 CE4 audit completeness check | Security officer | query/bundle/proposal/apply の監査4点が欠けていないか確認する | equivalenceKey, queryCanonicalHash, bundleHash, sourceBundleHash, command, result | 元query、bundle本文、proposal本文、Document JSON全体を復元または表示する場合 |
| A3 access-control decision review | Platform operator | `external_http` / `noop` / `mock` 境界とfail-safe結果を確認する | adapter type, decision.allow, decision.reason, policyRefPresent, timeout bucket | roles/groups生値、IdP subject、bearer token、API keyを返す場合 |
| A4 support correlation | Support | 利用者から共有されたtraceIdと操作事実を照合する | traceId, occurredAt, eventType, masked actorRef, result | Supportが本文、未レビュー情報、横断検索結果を閲覧できる場合 |

### Open化チェックリスト

- [x] `ADR-0035` がAccepted、または同等の後続ADRで「本文を含まない監査メタデータ閲覧だけを検討可能」と固定されている。（2026-07-13充足）
- [ ] A1-A4 のどれを最初の実装候補にするかを1つだけ選ぶ。複数同時に進める場合は別issueへ分割する。
- [ ] 返却項目、検索条件、権限、監査証跡、エラー時の表示方針を、本文を含まない範囲で固定する。
- [ ] UIを持つ場合は、マウス操作とキーボード操作の代表シナリオ、フォーカス順、viewport evidence、スクリーンショットを `PRODUCT-QA-01` へ渡す。
- [ ] API/CLIだけで始める場合も、本文・未レビュー情報・secret・生IdP識別子が返らないことを integration test で確認する。

### 実装へ進めない条件

- Accepted済み `ADR-0035` の本文禁止・標準機能外境界を緩和して実装へ進もうとしている。
- 監査メタデータ閲覧と、管理者本文閲覧、横断検索、保持期限管理、自動削除、所有者移管、削除履歴管理が混ざっている。
- Support または Platform operator が、利用者本文、未レビュー情報、Document JSON全体、review pack本文、diff本文を標準導線で閲覧できる。
- 監査メタデータを外部へ共有する標準導線を製品が持つ。必要な場合は目的、共有先、除外項目、記録、無効化手順を別ADRで固定する。

## 6.3) Open化前の人間判断パケット（2026-06-06、2026-07-13解決済み履歴）

本IssueはまだDraftであり、以下は実装許可ではない。`ADR-0035` がAcceptedまたは同等ADRで置き換えられた後、Security officer / Productization Program Owner / Project Maintainers がOpen化可否を短時間で判断できるようにするための確認パケットである。

| 判断項目 | 推奨初期値 | 人間が確認すること | 未確認時の扱い |
| --- | --- | --- | --- |
| Open化可否 | Hold | `ADR-0035` の境界がAccepted済みであり、本文を含まない監査メタデータ閲覧だけを検討対象にしてよいか | Draft継続 |
| 最初の候補 | A1 share/export event lookup | 共有/エクスポートの安全境界確認が、本文閲覧なしでも運用価値を持つか | 候補未選択として分割しない |
| 提供面 | APIまたはCLI優先、UIは後続 | 管理画面を先に作る必要があるか。UIを持つ場合はマウス/キーボード/e2e証跡を用意できるか | UI着手不可 |
| 閲覧主体 | Audit operator / Security officer | SupportやPlatform operatorを本文閲覧主体にしないことで運用上問題がないか | Support向け本文閲覧要求は別ADR |
| 返却項目 | A1-A4の許可項目に限定 | `policyRef` 生値、roles/groups生値、IdP subject、本文、diff、review pack本文が返らないこと | integration未達 |
| リリースゲート扱い | 製品境界 / 条件付き証跡 | 監査メタデータ閲覧の未実装を単独No-Goにしないか、導入組織が必須とするか | `PRODUCT-QA-01` / `MVP-EXIT-01` へ戻す |

初期実装候補を選ぶ場合は、A1だけを独立issueに分割する。A2-A4、UI、外部監査連携、メタデータ共有導線は同じPRに混ぜない。A1であっても、検索条件に本文語句を受け付ける、review pack本文を返す、共有先の個人情報を返す、またはSupport向け標準導線にする場合は、本Issueでは進めず別ADRを先行する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py`
  - `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py`
  - `git diff --check -- 01_Plans/issues/issue-DATA-MAINT-04-metadata-only-audit-viewing.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 02_Architecture/data_model_operations_overview.md 02_Architecture/api.md`
  - `rg -n "DATA-MAINT-04|監査メタデータ|本文を含まない|ADR-0035|audit metadata|audit viewing" 01_Plans/issues/issue-DATA-MAINT-04-metadata-only-audit-viewing.md 01_Plans/issues/issue-DATA-MAINT-03-high-privilege-data-lifecycle-policy.md 01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md 02_Architecture/data_model_operations_overview.md 02_Architecture/api.md`
- 期待結果:
  - DATA-MAINT-04がOpenとして追跡され、本文なしallowlistとread-only境界が固定されるまで実装に進まない。
  - 監査閲覧候補が本文を含まない範囲に限定され、本文閲覧や横断検索はADR必須として残る。
- 未実施時の理由・代替検証:
  - 本Issue作成時点では実装を行わないため、docs-checkとtriage整合を検証する。Open化または実装分割時にintegration以上を実施する。

## 8) 代替案 / Alternatives considered

- 代替案A: 監査ログ閲覧を `DATA-MAINT-03` に残し続ける。本文閲覧や削除と混ざり、内部issueで進められる低リスク候補が見えにくくなるため採用しない。
- 代替案B: ADR-0035のAcceptedを待たずにOpen化する。2026-06-06時点で不採用とし、2026-07-13のAccepted後に正規Open化した。
- 代替案C: 監査閲覧UIを先に作る。権限と除外項目が未固定のままUIが先行するため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 「監査メタデータ閲覧」が本文横断検索、未レビュー情報閲覧、保持期限管理、削除履歴管理へ拡大解釈される。
- 影響範囲: API、管理UI、Support導線、SafeMode、share/export、public exposure、review attribution、merge decision log。
- ロールバック手順: DATA-MAINT-04をDraftに戻し、監査閲覧候補を `DATA-MAINT-03` / ADR-0035 の本文アクセス禁止境界へ戻す。実装済みの場合は該当API/UI/CLIを無効化し、本文を含まない棚卸し証跡だけを残す。

## 10) Additional context

- ADR化が必要になる条件:
  - 本文、未レビュー情報、添付ファイル、Document JSON全体、review pack本文、diff本文を閲覧対象に含める。
  - 管理者本文閲覧、横断検索、保持期限管理、自動削除、所有者移管と接続する。
  - 監査メタデータを標準機能として共有する導線を製品が持つ。
  - SafeMode、share/export、public exposure、review attribution、merge decision log の意味が変わる。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
