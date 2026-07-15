# Project Progress Dashboard

- Status: Informative current snapshot; ADR / issue memoが正本
- Last verified: 2026-07-15 JST
- Evidence command: `python 01_Plans/triage_actionable_plans.py`
- Upstream: `01_Plans/issues/README.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`
- Downstream: Maintainerの着手順判断、release gate再評価

## Audience

現在の優先順位と停止条件を短時間で確認したいMaintainer、Contributor、Reviewer、生成AIを対象とする。

## Goal

現在のActive集合、release状態、次の1手、人間だけが確定できるgateを、過去の実行ログを読まずに把握できるようにする。

## Non-goal

- ADRやissue memoのDecision、AC、証拠本文を複製すること。
- 過去件数、解消済みDecision Queue、per-rerunログを現在の指示として残すこと。
- このsnapshotだけでrelease Go、SafeMode緩和、Schema変更を承認すること。

## Outcome

読者は正本へ遡りながら、今すぐ着手できる作業、blocker、再判定条件を選べる。

## Current snapshot

### Plan state

| Item | Current value | Source |
|---|---:|---|
| Active issue memos | 31 | `issues/README.md` |
| Ready | 14 | triage |
| Parked / blocked | 17 | triage |
| Draft / Open / In Progress | 17 / 8 / 6 | filesystem metadata |
| Actionable ADRs linked by triage | 0 | triage |
| Triage stopper | 0 | triage |

Active全件とSource Issueは `issues/README.md`、着手順は `triage_actionable_plans.py` の出力を正とする。本ダッシュボードへ全31件を複製しない。

### In-progress lanes

| Lane | Issue | Current boundary |
|---|---|---|
| Documentation | `DOC-ARCH-02` | Card/DocumentV2合成型とH-D履歴分離済み。H-A〜H-CとAPI縮約を継続 |
| Documentation | `DOC-USER-JOURNEY-01` | 初回利用ガイドの独立dry-run待ち |
| Product value | `PRODUCT-VALUE-01` | 最初の意味ある配置の証拠維持 |
| Product value | `PRODUCT-VALUE-02` | 保留・違和感・根拠不足workflowの証拠維持 |
| Product value | `PRODUCT-VALUE-03` | レビュー可能な成果物packageの証拠維持 |
| External connection | `EXT-CONN-01` | read-only MCPのHTTP輸送・threat model追補が残課題 |

### Release state

**Full release: No-Go.** 最新のprogram gate正本は `MVP-EXIT-01`、品質gate正本は `PRODUCT-QA-01` とする。

技術・証拠上の未完了:

- `CE1-CONTRACT-01`: `ContextBundle.queryId`、`schemaVersion`、handoff metadataの所属を照合し、closed-world v1を文書・backend・frontendで一意にする。破壊的変更が必要ならADR-0047 R-4で停止する。
- PostgreSQL: 修正済みの正準環境変数で、Docker-capable環境の実サービスに対する統合test証拠を得る。
- `PRODUCT-QA-01` / `MVP-EXIT-01`: 上記結果と2026-07-14完了のARIA構造修正を取り込み、gateを再判定する。

人間またはrelease authorityだけが確定できるgate:

- 物理キーボード受入とスクリーンリーダー受入。
- release screenshotの最終承認。
- 最終program approval。
- 正式な組織承認やpackage public contract / 署名 / 承認workflowを導入する場合の承認。

完了済みのため「未実施」へ戻さない証拠:

- `DX-E2E-07` / `QA-MONKEY-13`: 2026-07-15にDone。UI契約driftとAlt+Shift+2階層選択バグはmainへ統合済み。
- Compose / environment rehearsal: 2026-07-11実施、全項目Pass。人間の最終判断を代替しない。
- Support diagnostics / recovery rehearsal: 2026-07-11実施、全項目Pass。判断ログ実データを含む次回演習はfollow-up。
- ADR-0052由来の構造的ARIA修正: `UI-QUALITY-A11Y-03` が2026-07-14 Done、axe延期ルール0件。

## Safety invariants

次はsnapshot更新やrelease gate処理で緩和しない。

- SafeMode既定ON。
- `provider=none`既定。
- AI出力はproposal-only。
- `human_reviewed` は人間の明示操作だけで昇格。
- patch + approval と可逆性を維持。
- share/export前確認、redaction、import sanitizeを維持。
- score / rank / confidence / priorityを人の判断代替として外部投影しない。

変更がこのいずれかへ影響する場合は、dashboardではなく上流ADR / Architecture / Security文書から先に更新する。

## Current decisions that must not be reopened accidentally

- GitHub Issues正本運用は開始していない。Action SSOTは内部issue memo、外部受付はDiscussions。
- H-PV1 / H-PV2 / H-PV3の代理承認は、記録済みの現行evidence packetに限り有効。final shipment authorityは発生しない。
- HIL / FBの古いApproval Record、GOV exception、pending queueは、2026-06-20のMaintainer判断で解消済み。current issueが明示的に再起票しない限りblockerへ戻さない。
- ADR/issue層でAIが代理処理できる人間判断待ちは0。残りは技術証拠またはrelease authority gateである。
- 新規設計ADRより、Accepted ADRとReady issueのexecutionを優先する。新ADRはADR-0047 R-1..4に該当する場合だけ起票する。

## Next actions

1. **CE1 contract reconciliation** — `CE1-CONTRACT-01` でlogical bundleとHTTP envelopeを分離し、v1 keysetを一意にする。
2. **Integration evidence** — Docker-capable環境で正準PostgreSQL CI pathを実行し、skipのない結果を記録する。
3. **Gate refresh** — 2の後、`PRODUCT-QA-01` と `MVP-EXIT-01` を最新mainで再判定する。`DX-E2E-07`、`QA-MONKEY-13`、ARIA-03を未完扱いへ戻さない。
4. **Documentation integrity** — `DOC-ARCH-02` のH-A〜H-C、`DOC-USER-JOURNEY-01` の独立dry-run、`DX-DOC-02` のfail-closed化を続ける。
5. **Human acceptance** — 技術gateがgreenになった後、物理キーボード、スクリーンリーダー、release screenshot、final program approvalを権限者が実施する。

優先順位が競合する場合は、P0 release gate、安全不変条件、P1 current contract / docs integrityの順で判断し、個別issueのPriorityと依存をtriageで再確認する。

## Verification record

2026-07-15 Docs slice:

- issue validator: 31 active rowsを検証しpass。
- triage: active=31 / ready=14 / blocked=17 / actionable ADRs=0 / stopper=0。
- validator unit tests: 10 passed。
- CE1 backend contract tests: 18 passed（`test_context_bundle_routes.py`）。
- CE1 frontend contract tests: 9 passed（`query_preview.test.ts`）。
- E2E / Compose: 本Docs sliceでは再実行していない。release状態は各gate memoの最新証拠を参照する。

## Update rules

- ADR / issue memoを先に更新し、その後にこのsnapshotを同期する。
- 数値はtriageとfilesystem metadataから再計算し、手計算の継ぎ足しをしない。
- Done issueや解消済みgateをCurrent snapshotへ残さない。再発した場合は新しい現行証拠と再開理由をissueへ記録する。
- per-rerunログ、過去件数、古いQueueはgit履歴へ委譲する。
- gitだけでは失われる一次証拠をarchiveする場合は、`Informative`、対象期間、Retention reason、current SSOTへの逆リンクを必須とする。
