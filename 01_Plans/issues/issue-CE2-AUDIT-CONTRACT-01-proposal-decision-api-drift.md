# Issue: CE2-AUDIT-CONTRACT-01 proposal判断APIの語彙・response・永続化契約を再統合する

- Type: Bug
- Status: Done
- Source Issue: CE2-low-risk-ai-assist
- Priority: P1
- Owner: Maintainer
- Scope: `02_Architecture/api.md`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/tests/test_ce2_proposal_api.py`, `03_Implement/frontend/src/api/client.ts`
- Related ADR/Spec: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md`, `01_Plans/issues/issue-SEC-AUDIT-LOG-01-proposal-decision-reason-unmasked-in-server-log.md`, `02_Architecture/llm_quality_strategy.md`
- Expected verification level: `integration`

## 三要素整合（ADR-0067）

- **業務設計（Business）**: 人間のAdopt／Reject／Hold判断を監査記録へ残すjourneyが、frontendから422または500にならず完遂できる必要がある。AIの自動確定は引き続き禁止する。
- **データ設計（Data）**: 公開API正本は`merge_decision_logs`への追記を記載するが、現行routeはserver logだけを出力する。proposal判断の正本、tenant／documentとの結合key、reasonの機微情報境界を決定する必要がある。
- **機能設計（Function）**: request語彙、response shape、永続化の3点が正本・frontend・backend model・route・testで一致していないため、本Issueで契約を再決定する。

## 課題

- 現在の問題1: `02_Architecture/api.md`とfrontend clientは`decision: adopt | reject | hold`を使用するが、backend routeはこれらを明示的に422とし、`accepted | rejected | held`だけを受理する。
- 現在の問題2: 公開APIはresponseを`{recorded: boolean}`とする一方、backend testは`proposalId/status/reviewState/recordedAt`を期待する。現行`ProposalDecisionAuditResponse`にはfieldが一つもなく、routeは4つのextra fieldを渡してPydantic validation errorとなりHTTP 500になる。
- 現在の問題3: 公開APIは`merge_decision_logs`への追記を表明するが、routeは構造化server logだけを出力してDBへ永続化しない。proposal requestには現状document／tenant結合に必要な識別情報もない。
- 現在の問題4: 任意の自由記述`reason`をserver logへ無加工で出力しており、`SEC-AUDIT-LOG-01`の未決事項と同時に解決する必要がある。
- 利用者または開発への影響: 同梱frontendのproposal判断送信は常に422となり、backend testが送る別語彙では500となる。正常成功経路が存在せず、監査済みと誤認される一方で判断は正本へ残らない。

## 対応方針

- 実施すること: 人間操作語彙（`adopt/reject/hold`）とlifecycle値（`accepted/rejected/held`）を別概念として明示し、requestからlifecycleへの写像を一箇所に固定するか、公開request自体をlifecycle語彙へ変更するかを決定する。
- 実施すること: responseを受領確認だけにするか、更新後lifecycleを返すかを決定し、OpenAPI、frontend型、Pydantic model、route、testを同時更新する。
- 実施すること: proposal判断の永続正本を既存`merge_decision_logs`へ置く場合はtenant／document／proposalの結合key、冪等性、順序、transaction、認可を定義する。これらが不足する間は「監査記録済み」を返さずfail closedにする。
- 実施すること: `reason`は通常server logへ本文を出さず、採択した監査正本のsize limit、sanitize、閲覧権限、retentionに従わせる。
- 実施しないこと: response modelへ現在routeが渡すfieldを機械的に足すだけの修正、frontendだけをbackendの暫定語彙へ合わせる修正、server logを永続監査正本とみなすこと。

## 契約checkpoint（2026-08-11）

- `merge_decision_logs`は類似統合判断の`MergeDecisionRecord`専用であり、異なるpayloadを混在させると既存のgroup/snapshot復元APIが壊れるため流用しない。専用の追記型`ai_proposal_decision_events`を正本とする。
- request語彙は人間操作の`adopt/reject/hold`、保存するlifecycleは`accepted/rejected/held`とし、backendの一箇所で写像する。
- requestは`docId/proposalId/sourceBundleHash/idempotencyKey/decision/reason?`とする。actor/reviewerはclient申告を廃止し、認証・tenant解決後のserver-owned reviewer referenceだけを保存する。
- proposal生成成功時に本文を持たない`ai_proposals`相関registryへtenant・Document・proposal ID・kind・source bundle hashを保存し、判断時に一致を必須化する。任意のproposal IDを監査済みにできないよう未登録IDは404にする。
- 同じidempotency keyかつ同じ内容の再送は同じreceiptを返す。keyの内容不一致、異なる終端判断、終端後のholdは409とする。`held`から一度だけ`accepted`または`rejected`へ進められる。
- reason本文は監査表にも通常logにも保存しない。UTF-8 byte長とSHA-256だけを保存し、最大1000文字に制限する。
- 成功responseは`recorded/eventId/proposalId/status/reviewState/recordedAt`とし、`reviewState`はAI出力そのものの人間レビュー済み昇格を意味しないため`unreviewed`を維持する。

## 受入条件

- [x] request decision語彙とproposal lifecycle語彙の関係が公開APIで一意に定義され、frontend／backend／testが一致する。
- [x] 成功response shapeがOpenAPIとPydantic modelで一致し、正常requestが500にならない。
- [x] 判断が永続化された場合だけ成功を返し、同一proposalへの再送・競合・DB失敗時の契約が定義される。
- [x] tenant境界とdocument／proposal結合を検証し、別tenantのproposalへ判断を記録できない。
- [x] `reason`が通常server logへ無加工で残らず、上限・sanitize・retention・閲覧境界がテストされる。
- [x] proposal-only、human-final、no-auto-apply、`reviewState=unreviewed`の既存安全境界を後退させない。
- [x] backend API test、frontend client test、SQLite integration、tenant越境negative testが成功する。

## 責任分界（REQ-DEF-02）

- 実行責任（R）: Maintainer／実装担当
- 受入判定（A）: Maintainer
- 契約チェックポイント: `api.md`の公開契約、CE2 lifecycle、`merge_decision_logs` schema、tenant-scoped API precondition、監査metadata sanitizer
- 停止基準: proposalをDocumentとtenantへ一意に結合できない、またはreasonの正本・閲覧境界を決められない場合は、永続化API実装を進めずDraftを維持する。

## 検証計画

- 実行する確認: `test_ce2_proposal_api.py`を正常・未知語彙・再送・DB失敗・tenant越境へ拡張し、frontend API client testとSQLite integrationを実行する。OpenAPI生成結果と`api.md`のrequest／responseを契約testで照合する。
- 期待結果: 同梱frontendからの人間判断が一度だけ正しいtenantの監査正本へ記録され、成功responseが契約どおり返り、自由記述や資格情報が通常ログへ漏れない。

## 補足

- 2026-08-11のSQLite基準backend全回帰は`870 passed / 6 skipped / 34 deselected`で、本不整合1件と別途修正済みのtenant session version不具合1件がfailした。session不具合修正後、本件が既知の残存backend failureとなる。
- `SEC-AUDIT-LOG-01`はreason方針の判断材料として本Issueへ統合して解決し、独立したserver-log修正だけを先行させない。

## 完了記録（2026-08-11）

- migration `20260811_0023`で生成相関registry`ai_proposals`、追記正本`ai_proposal_decision_events`、競合制御projection`ai_proposal_decision_states`を追加した。3表はtenant+Document複合外部keyを持ち、PostgreSQLではENABLE/FORCE RLSとtenant policyを持つ。
- APIはclient申告actorを廃止し、Document write認可で解決したserver-owned reviewer referenceを保存する。Document不在は404、idempotency内容不一致・終端後変更・source bundle不一致は409とする。
- `hold -> adopt|reject`だけを許可し、同一idempotency keyの同一再送は同じevent receiptを返す。reasonは最大1000文字で、本文を保存・log出力せずSHA-256とUTF-8 byte数だけを保存する。
- frontendは監査成功後にisland summaryを適用する順序へ変更した。session再検証によるrequest再送でも同じidempotency keyを使う。
- source bundle相関を持たない外部貼付proposalはCE2 endpointから外し、架空hashを作らず`EXT-AGENT-AUDIT-01`へ正しい相関連鎖を分離した。
- SQLite/API/migration/RLS静的対象は`23 passed / 3 deselected`、SQLite基準全回帰は任意起動の外部LLM疎通だけを除き`881 passed / 3 skipped / 53 deselected`、frontend全回帰は`1409 passed`、TypeScript型検査はpassした。実DBpromotionはPostgreSQL 16（RLSを含む）`23 passed`、MySQL 8.4/MariaDB 11.4 `2 passed`、SQL Server 2022、CockroachDB 26.2、Oracle Free 23.26が各`1 passed`。
