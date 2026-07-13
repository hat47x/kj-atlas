# Issue Draft: PRODUCT-OPS-02 サポート診断バンドル方針の策定

- Type: Feature request
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/`, `04_Documentation/diagnostics.md`, `04_Documentation/operations.md`, `04_Documentation/data_handling.md`, `SUPPORT.md`, `01_Plans/adr/`
- Related Backlog: `PRODUCT-OPS-02`
- Related ADR/Spec: `01_Plans/issues/issue-PRODUCT-OPS-01-support-diagnostics-error-recovery.md`, `01_Plans/adr/ADR-0053-support-diagnostics-bundle-boundary.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `THREAT_MODEL.md`, `04_Documentation/diagnostics.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Expected verification level: `e2e`

## Draft→Open 2026-06-21
診断バンドル方針策定を開始可能。優先度Could、GoNoGoGate=Optional。

## 検討記録 2026-07-11: 方針スライス完了（ADR-0053 Proposed 起票）

- 本Issueの最初のスライス「仕様とADR要否を決める」を実施した。
- 判断: バンドル形式（許可リスト方式 `diag-bundle.v1`）を固定するため **ADRが必要** →
  `01_Plans/adr/ADR-0053-support-diagnostics-bundle-boundary.md` を **Proposed** で起票。
  - 採用提案: 明示操作・ローカル生成・プレビュー必須・許可リスト方式。製品は送信経路を持たない。
  - 不採用: 自動収集・サポート基盤送信連携（案C）。現状維持のみ（案A）も転記事故リスク残存のため不採用提案。
  - 許可/禁止リストは本Issue §5.1 の初期案を基に、A1エラーエンベロープ・provider種別名・件数のみ等へ具体化した。
- 実装（UI導線・マスクテスト・e2e、T1/T3〜T5）は **ADR-0053 の Accepted 後**に着手する。
  2026-07-13に安全側の修正（生UserAgent・Document.id・error.messageの除外）を加えてAccepted。実装は未完のためIssueはIn Progressを維持する。

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-OPS-02
- RequirementStatement: サポートへ共有できる診断バンドルを導入するか、導入する場合に何を含め、何を必ず除外し、利用者がどこで確認・キャンセルできるかを決定する。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=利用者が保存失敗、backend未接続、取り込み失敗、共有前警告などの問題をサポートへ相談したい / 操作=診断バンドル作成または診断情報共有の導線を開く / 期待結果=共有前に内容、マスク状態、共有してはいけない情報が分かり、未承認の自動送信が起きない / 除外=自動ログ送信、チケットシステム連携、未加工本文や秘密情報を含むバンドル。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed（`ADR-0053` Accepted 2026-07-13）
- DecisionQueueRef（未確定時の参照先）: Resolved（実装は`ADR-0053`のallowlistと着手ゲートに従う）

## 1) 課題 / Problem statement

- `PRODUCT-OPS-01` で、画面上の復帰導線と手動診断共有の基本方針は整備された。
- 一方、実運用ではサポート担当者が再現情報、環境情報、SafeMode状態、エラー種別をまとめて受け取れると切り分けが速くなる。
- ただし、診断バンドルは未加工本文、API key、token、password、内部URL、個人情報を混入させるリスクがある。方針を決めずに実装すると、安全な共有境界が曖昧になる。

## 2) 背景 / Context

- `PRODUCT-OPS-01` は、自動ログ送信、診断パッケージ仕様、サポート基盤連携を固定する場合はADR化すると定めている。
- `04_Documentation/diagnostics.md` は、共有してよい情報と共有しない情報を分け、復旧判断へ渡せる粒度の診断メモを作る方針を示している。
- `THREAT_MODEL.md` と SafeMode 方針は、未レビュー本文や秘密情報の共有を既定で抑止する前提である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: サポートへ渡す情報が揃うと、問題発生時の中断時間を減らせる。ただし、利用者が安心して共有できることが価値の前提である。
- 安全（THREAT_MODEL / SafeMode）: 診断バンドルは share/export と同等の外部共有リスクを持つため、SafeMode、マスク、プレビュー、明示操作を必須条件にする。
- 企業・行政要件（enterprise_architecture）: 組織導入では、サポート共有の承認、保持期間、監査責任、外部送信可否が組織ごとに異なる。
- 後方互換（schemas）: Document schema や保存形式を変更せず、診断出力とUI導線の追加として扱う。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 診断バンドルの許可項目/禁止項目の仕様。
  - 画面上の作成、プレビュー、コピー/ダウンロード、キャンセル導線。
  - `diagnostics.md`、`operations.md`、`SUPPORT.md` のサポート共有手順。
  - 必要な場合はADRで、バンドル形式、自動収集範囲、送信有無、保持責任を固定する。
- 変更の最小単位:
  - まず仕様とADR要否を決める。
  - 実装する場合も、最初はローカル作成と手動共有に限定し、自動送信は別判断にする。
- 非目標:
  - 未承認の自動ログ送信。
  - チケットシステム連携。
  - 未加工の文書本文、取り込みファイル全文、秘密情報、個人情報を含むバンドル。
  - 組織共通の保持期間や送信先を製品側で一律規定すること。

## 5) 受入条件 / Acceptance criteria

- [ ] 診断バンドルに含めてよい情報と含めてはいけない情報が、画面と文書の両方で一致している。
- [ ] 利用者がバンドル作成前に、マスク状態、含まれる情報、共有先に渡す前の確認事項を理解できる。
- [ ] バンドル作成は明示操作でのみ開始し、自動送信は行わない。
- [ ] SafeMode ON 時は、未レビュー本文、カード本文、取り込みファイル全文、API key、token、password、個人情報、内部URLの機微部分が出力されない。
- [x] 自動送信、サポート基盤連携、固定バンドル形式、組織横断の保持方針を採用する場合は、実装前にADRが起票されている。（`ADR-0053-support-diagnostics-bundle-boundary.md` を Proposed で起票済み。2026-07-11）
- [ ] unit/integration/e2e のいずれかで、許可項目と禁止項目のマスクが検証されている。UI導線を実装する場合は e2e でプレビュー、キャンセル、コピー/ダウンロードを確認する。

### 5.1 許可項目/禁止項目（`ADR-0053` Accepted値）

| 区分 | 固定値 | 備考 |
| --- | --- | --- |
| 含めてよい | 生成時刻、検証済みapp revision/build ID、正規化済みbrowser family/major・OS family、固定障害分類、明示的な障害コンテキストのHTTP status、SafeMode状態、provider種別、Document version/updatedAt、card/island/edge件数、既知A1 errorCode/contractId/occurredAt | 許可値だけから新規オブジェクトへ射影する。SafeMode ON/OFFで境界を変えない。 |
| 条件付き | なし | v1では組織識別子になり得る値を「マスクすれば可」としない。追加はADR更新を要する。 |
| 含めない | Document id/title、entity id/ref、全本文、raw UserAgent、URL/referrer/cookie/header/request/response、error message/stack/cause、環境変数、endpoint/model名、API key/token/password、個人識別子、ログ、画像 | SafeMode ON/OFF に関わらず常時除外する。自由記述の再現メモは既存の手動共有経路に残し、JSONへ混ぜない。 |

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 診断バンドルの許可項目/禁止項目を確定し、`diagnostics.md` と `SUPPORT.md` に反映する。
- [x] T2 自動送信、固定バンドル形式、保持方針を採用するかを判断し、必要ならADRを起票する。（判断: 自動送信・基盤連携は不採用、形式は `diag-bundle.v1` 許可リスト方式を提案。`ADR-0053` Proposed 起票、2026-07-11。T1/T3以降はADR Accepted後）
- [ ] T3 ローカル作成/手動共有に限定する場合のUI導線を設計する。
- [ ] T4 マスク処理のunit/integrationテストを追加する。
- [ ] T5 UIを実装する場合は、プレビュー、キャンセル、コピー/ダウンロード、禁止項目不在をe2eで確認する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "PRODUCT-OPS-02|診断バンドル|support bundle|自動ログ送信|API key|token|password|未加工本文" 01_Plans 04_Documentation SUPPORT.md 03_Implement`
  - `git diff --check -- 01_Plans 04_Documentation SUPPORT.md 03_Implement`
  - 実装時: `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run`
  - 実装時: `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/<support-bundle-spec>.spec.ts --reporter=line`
- 期待結果:
  - 方針段階では、自動送信や固定バンドル形式が未承認のまま実装されていないことを確認できる。
  - 実装段階では、禁止項目がバンドルに含まれず、利用者が共有前に内容を確認できる。
- 未実施時の理由・代替検証:
  - UI未実装段階では docs-check と issue/ADR整合確認に限定し、e2e は実装PRで実行する。

## 8) 代替案 / Alternatives considered

- 代替案A: 現行の手動診断メモだけを維持する。安全だが、サポート時の再現情報が不足しやすい。
- 代替案B: すべてのログを自動送信する。利用者同意、組織承認、機微情報混入のリスクが大きいため採用しない。
- 代替案C: 診断バンドルを作るが、送信は利用者の手動共有に限定する。最初の候補として扱う。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: バンドルに機微情報が混入する。利用者が自動送信されたと誤解する。サポートがバンドルだけで復旧判断を確定してしまう。
- 影響範囲: frontend diagnostics UI、export/share safety wording、support documentation、operations runbook。
- ロールバック手順: UI導線を非表示に戻し、手動診断メモの既存導線へ戻す。文書上は診断バンドルを「未採用」に戻し、必要ならADRを Superseded または Rejected として記録する。

## 10) Additional context

- 親Issue: `PRODUCT-OPS-01`
- 関連する品質ゲート: `PRODUCT-QA-01` G6 診断とサポート
- ADR化が必要になる条件:
  - 診断バンドル形式を製品仕様として固定する。
  - 自動収集または自動送信を採用する。
  - サポート基盤、チケットシステム、外部ストレージと連携する。
  - 組織横断の保持期間、送信先、承認者を製品側で一律規定する。

## 11) Draft-to-Open readiness packet（2026-06-06）

本Issueは、現時点では Draft のまま維持する。Open化の判断は「診断バンドルを実装するか」ではなく、「どの範囲なら安全に仕様検討を始められるか」を確認するために行う。

### Open化候補

| 候補 | Open化可否 | ADR要否 | 理由 |
| --- | --- | --- | --- |
| A. 手動診断メモの改善 | Open化不要。`PRODUCT-OPS-01` と公開診断文書の範囲で継続できる | 不要 | 既存方針内で、利用者が手作業で非機微情報を整理するだけである。 |
| B. ローカル生成・手動共有の診断バンドル | 条件付きでOpen化候補 | 原則不要。ただし形式を製品仕様として固定する場合はADR | 自動送信せず、利用者がプレビューしてコピー/ダウンロードする範囲なら、まず内部issueで設計できる。 |
| C. 自動収集または自動送信 | Open化前にADR必須 | 必須 | 利用者同意、組織承認、保持責任、送信先、監査責任が変わる。 |
| D. サポート基盤・チケットシステム連携 | Open化前にADR必須 | 必須 | 外部システム、保持期間、アクセス権限、削除/訂正責任を固定する必要がある。 |
| E. 組織横断の保持期間・送信先・承認者を製品既定にする | Open化前にADR必須 | 必須 | 組織ごとの法務・契約・監査判断を製品が一律に決めることになる。 |

### Minimum safe bundle boundary

条件付きでOpen化できる最小候補は、Bの「ローカル生成・手動共有」に限る。この場合も、次をすべて満たすまでは実装Issueへ進めない。

- 作成は利用者の明示操作だけで開始する。
- 共有前に、含まれる情報、除外された情報、マスク状態をプレビューできる。
- 自動送信、外部保存、チケット起票、バックグラウンド収集は行わない。
- SafeMode ON/OFF に関わらず、未加工本文、カード本文、取り込みファイル全文、API key、token、password、cookie、個人名、メールアドレス、機密メモ、内部URLの機微部分を既定除外にする。
- document id や内部URLなど、組織内識別子になりうる値は、必要性を説明できる場合だけマスク済みで含める。
- UIを持つ場合は、プレビュー、キャンセル、コピー/ダウンロード、禁止項目不在を e2e で確認する。

### Human decision route

- Productization Program Owner: 診断バンドルが、利用者の復帰と問い合わせ準備に本当に必要かを判断する。
- Security officer: 含めてよい情報、必ず除外する情報、マスク後でも残る組織識別子の扱いを確認する。
- Platform Operator: サポートに渡す情報が、復旧判断に足りるか、かつ秘密情報なしで再現調査に使えるかを確認する。
- Support owner: 受け取った診断情報で確定判断をせず、再現手順・環境・非機微ログとして扱う運用に合意する。

### Proceed / Hold / Stop

- Proceed: Bの範囲に限定し、ADR不要なローカル生成・手動共有候補として、Open化可否をProductization Program Owner / Security officerが承認した場合。
- Hold: バンドル形式、含める値、UI導線、マスク規則、検証レベルのいずれかが曖昧な場合。
- Stop: 自動送信、外部保存、チケット連携、固定保持期間、組織横断の送信先、未加工本文または秘密情報を含む診断出力を要求された場合。

### Verify

- `git diff --check -- 01_Plans/issues/issue-PRODUCT-OPS-02-support-diagnostics-bundle-policy.md`
- `rg -n "Draft-to-Open readiness|Minimum safe bundle boundary|自動送信|外部保存|チケット|未加工本文|API key|token|password|Proceed|Hold|Stop" 01_Plans/issues/issue-PRODUCT-OPS-02-support-diagnostics-bundle-policy.md`
- Proceed for this slice: docs-only の判断整理として継続可能。Issue status、ADR status、API/UI/runtime behavior は変更しない。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
