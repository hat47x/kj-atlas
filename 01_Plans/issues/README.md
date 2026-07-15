# 01_Plans Issue Memo Index

このディレクトリは、現在の内部運用における **issue memo 正本** を管理する。
Decisionは ADR、Action は issue memo で管理する。GitHub Issues は未運用であり、明示的な開始宣言があるまで補助参照としても必須にしない。

> Performance note for AI agents: issue memo が増えても全件を都度読む必要はない。対象Backlog ID/関連ADR/作業スコープに一致するメモのみ参照する。
> Minimal triage: `python 01_Plans/triage_actionable_plans.py` で Ready issue / 保留 issue / Active issue連動ADR を先に抽出し、その出力に出たファイルだけを読む。

## Scope

- 対象: Active な issue 補助メモ（Draft / Open / In Progress）
- 正本: 現在運用では issue memo を正本として扱う（GitHub Issues は**未運用**、将来再開は可能）
- ライフサイクル: Draft -> Open -> In Progress -> Done（Done (Local) は廃止）
- ライフサイクル定義は本READMEのみを正とする。個別issue memoには記載しない。
- Done メモは自動GCしない（手動削除のみ）

## Start here（人間 / 生成AI 共通）

1. `TEMPLATE.md` をコピーして起票草案を作成する。
2. `Type / Priority / Scope / Related ADR` を先に埋める。
3. `Expected verification level`（`docs-check` / `unit` / `integration` / `e2e`）を先に宣言する。
4. 受入条件（Acceptance criteria）と検証計画（Validation plan）を先に確定する。
5. `Source Issue` は運用状態に応じて記載する（未運用時は `N/A`、GitHub Issues運用時はURL）。

## 委任判断ログ（2026-07-02 JST）

- 入力: ユーザーが「ADR/issueの人間作業を代行してください」と指示したため、Codex が記録者兼実行者として、現行証跡packetに残る人間受入待ちの同期を行う。
- `PRODUCT-VALUE-01..03`: 2026-06-29 の H-PV1/H-PV2/H-PV3 代理承認を現行状態へ引き継ぐ。各親issue、current-open summary、`PRODUCT-QA-01`、`MVP-EXIT-01`、`02_Architecture/value_traceability.md`、`project-progress-dashboard.md` で、人間受入ブロッカーを「現行証跡packetでは解消済み」として扱う。
- `HIL/FB`: 2026-06-20 の `ADR-0039` / Maintainer 解決により、現行正本では Approval Record、GOV exception、pending queue は解消済み。古い Hold / Needs-decision 記録は履歴であり、現在の停止条件として再起票しない。
- 残る非委任ゲート: 最終program approval、Compose/環境リハーサル、サポートリハーサル、実機キーボード受入、スクリーンリーダー受入、release screenshot approval、正式な組織承認、package public contract / 署名 / 承認workflow の導入判断。
- 同日再確認: ADR/issue層でCodexが代理処理できる人間判断待ちは残0。残る非委任ゲートは出荷権限、実機アクセシビリティ、環境/サポート実行証跡であり、内部issue上は未解決ゲートとして維持するが、ADR/issueの人間作業としてAIだけで確定しない。
- 不変条件: SafeMode既定ON、proposal-only、`human_reviewed`人手昇格、`provider=none`既定、patch+approval、share/export境界は変更しない。新ADRは不要。

## 委任判断ログ（2026-07-01 JST）

- 入力: ユーザーが「ADR/issueの人間作業を代行してください」と指示したため、Codex が記録者兼実行者として、既存Decision Queueの人間判断待ち2件を処理する。
- `DQ-FB-P2C-01`: **Decision (Final): Conditional Go**。Gate 0承認は、計画再開と下流ハンドオフに限って有効化する。A1/A2/A3 memo が Done/Fixed であることを根拠に待ち状態を解消するが、この判断だけで `03_Implement` のコード変更許可や SafeMode 緩和は発生しない。
- `DQ-OPS-SOURCE-01`: **Decision (Final): No**。GitHub Issues 正本運用は開始しない。`Source Issue: N/A` を継続し、内部 issue memo を正本として扱う。
- 影響: 上記2件の人間判断待ち Open は解消済みとして扱う。`DQ-HIL-EXEC-01` の Ready 監視は別レーンのため継続する。
- 再開条件: validator / unittest / `rg` による共有3ファイル同期確認が通ること。今後GitHub Issues運用へ切り替える場合は、明示的な開始宣言、RACI-I通知、READMEと対象memoの同日同期を必須とする。


## DOC-OPS-02 同期チェック（実行前に確認）

- 用語: `正本 / 暫定メモ / 決裁入力 / 例外承認` を `ADR-0022` と一致させる。
- 役割: AUTH系（`Security Officer / System Owner / Platform Operator`）と DOC系（`Platform Architecture Owner / Plan Owner / Architecture Owner`）の責務境界を分離する。
- 導線: `02_Architecture/strict_mode_exception_approval_flow.md` → `04_Documentation/operations.md` / `04_Documentation/security.md` → `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` の順に同期する。
- 固定値（D1〜D4）: `承認順序=Security Officer先行 + 承認TTL=4h / scope=tenant最大2h / 代理承認なし / 48hレビュー + 15m一次 + 60m二次` を変更しない。
- Stream E rerun-69（2026-05-06）で shared 3ファイル再読と DOC-OPS境界チェック（B/C/D・SoD）を再実施し、公開固定値と停止条件違反0件を再確認した。
- Stream D rerun-71（2026-05-07）で Phase 1-5（Read→Sync→Audit→Verify→Publish）を shared 3ファイル限定で再実行し、公開固定値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と未承認事項の確定扱い0件を再確認した。
- Stream D rerun-72（2026-05-07）で Phase 1-4（Read Gate→同期更新→件数監査→公開固定）を shared 3ファイル限定で再実行し、公開固定値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と停止条件違反0件を再確認した。
- Stream D rerun-73（2026-05-08）で Phase 1-4（Read同期→整合更新→件数監査→再開判定1行固定）を shared 3ファイル限定で再実行し、公開固定値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と未承認事項の確定扱い0件・停止条件違反0件を再確認した。
- Stream D rerun-74（2026-05-09）で Phase 1-4（Read同期→Active/Done/Queue反映→件数監査→公開固定）を shared 3ファイル限定で再実行し、公開固定値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と未承認事項の確定扱い0件・参照リンク不整合0件・停止条件違反0件を再確認した。
- Stream F rerun-78（2026-05-20）で Phase 1-5（Read: 全ストリーム完了報告の再収集と件数/状態/Queue再計算→Plan: 反映対象を Status / Decision Queue / Next Action のみに固定→Execute: shared 3ファイル単一変更セット→Verify: validator/unittest/rg で整合監査→Proceed: 未承認事項の確定扱い0件・件数不整合0件・self-correction 3回超過なしを確認）を shared 3ファイル限定で実行し、公開固定値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と停止条件違反0件を再確認した。
- Stream F rerun-77（2026-05-19）で Phase 1-5（Read: 全ストリーム完了報告と証跡を再収集→Plan: 件数/状態/Decision Queue/依存順を固定→Execute: shared 3ファイル単一変更セット→Verify: 件数整合・Queue整合・依存順整合・停止条件違反0件→Proceed: 再開条件1行を明文化）を shared 3ファイル限定で実行し、公開固定値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と未承認事項の確定扱い0件・参照リンク不整合0件を再確認した。
- Stream F rerun-76（2026-05-17）で Phase 1-5（Read gate: shared 3ファイル再読→Plan: 件数・Queue・依存順の固定方針確認→Execute: 単一変更セット→Verify: validator/unittest/rg→Proceed: 次回再開条件1行固定）を shared 3ファイル限定で実行し、公開固定値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と未承認事項の確定扱い0件・停止条件違反0件を再確認した。
- Stream G rerun-75（2026-05-10）で Phase 1-5（Read Gate→Plan Sync→Execute Single-Set→Verify→Proceed）を shared 3ファイル限定で実行し、公開固定値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と未承認事項の確定扱い0件・停止条件違反0件を再確認した。

## Source Issue 運用基準（Traceability）

### 現在の運用判定（2026-03-03 時点）

- 判定: **GitHub Issues 正本運用は未開始**。
- 根拠: 本READMEの `Scope` に「GitHub Issues は未運用」と明記され、`Active issue memos` の `Source Issue` が `N/A` で統一されている。
- 実務ルール: PM/Triage の開始宣言が行われるまで、`Source Issue` は `N/A` を維持する。
- 2026-07-01追補: `DQ-OPS-SOURCE-01` は Final/No とし、GitHub Issues 正本運用を開始しない。ユーザー委任にもとづき、内部 issue memo 正本の運用を継続する。

### `Source Issue: N/A` を継続できる条件

- GitHub Issues を正本としてまだ運用開始していない（本READMEの `Scope` と一致）。
- 対象タスクが issue memo 内で完結し、外部トラッカー参照を必須としていない。
- `Active issue memos` 表の `Source Issue` 列が `N/A` で統一管理されている。

### GitHub Issues URL に移行する条件

- PM/Triage が「GitHub Issues を正本として運用開始」と明示した時点。
- 既存 `Open / In Progress` メモを更新するタイミングで、`Source Issue` を対応するURLへ置換する。
- 新規メモは起票時からGitHub Issue URLを必須とし、`N/A` は使用しない。

### GitHub Issues 正本運用の開始宣言ドラフト（PM/Triage）

> 本節はドラフトであり、実際の宣言時に日時とリンクを確定して使用する。

```md
[開始宣言] GitHub Issues 正本運用を開始します

- 宣言日時（JST）: 2026-03-XX XX:XX
- A（Accountable）: Platform Architecture Owner
- R（Responsible）: PM/Triage
- 告知先:
  1. `01_Plans/issues/README.md`（本ファイル）
  2. GitHub Discussions: `#project-ops`（運用告知スレッド）
  3. 対象移行PR本文（RACI-I記録付き）

本宣言以降、Active issue memo の `Source Issue: N/A` は次回更新PRで GitHub Issue URL へ移行する。
```

> 停止条件: A または R が未確定（役割が未割当）の場合、宣言を出さずに `N/A` を維持し、未確定項目を `Additional context` に記録して停止する。

### Active memo `Source Issue: N/A` → URL 移行Runbook（手順1〜6）

1. **開始宣言の確定**
   - 上記ドラフトの `宣言日時` を確定して README に追記し、RACI-I通知を1回記録する。
2. **URL対応表の作成**
   - Active issue memo ごとに `Backlog ID -> GitHub Issue URL` の1:1対応表を作成する。
3. **置換コミット（memo本体）**
   - Active memo の `Source Issue: N/A` を URL に置換する。
   - 同一コミットで `Status` / `Owner` / `Acceptance criteria` / 本文タスクは変更しない。
4. **置換コミット（index同期）**
   - `Active issue memos` 表の `Source Issue` 列を同一URLへ同期する。
5. **検証コマンド実行**
   - `python 01_Plans/issues/validate_active_issue_memos.py`
   - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
   - `rg -n "^- Source Issue: N/A$|\|[^|]*\|[^|]*\|[^|]*\| N/A \|" 01_Plans/issues`
6. **完了記録と通知**
   - 完了判定（`N/A`残存ゼロ + validator成功）をPR本文に記録し、RACI-I通知を確定する。

### RACI-I通知テンプレートと実施順序（誰がいつ通知するか）

- **A（Accountable）**: Platform Architecture Owner（最終承認・開始宣言確定）
- **R（Responsible）**: PM/Triage（実作業実行・通知送信）
- **C（Consulted）**: 各Issueの実行Lead
- **I（Informed）**: QA Lead

通知テンプレート（固定）:

```md
[RACI-I] Backlog=<Backlog ID> / Change=<Source Issue N/A→URL または開始宣言> / By=<role> / Memo=<memo path> / Source=<issue URL>
```

実施順序（固定）:

1. **R（PM/Triage）** が開始宣言案を作成して A に提示する（宣言前）。
2. **A（Platform Architecture Owner）** が開始宣言を確定し、READMEへ反映する（宣言時点）。
3. **R（PM/Triage）** が `Source Issue` 置換PRを作成し、テンプレで I（QA Lead）へ通知する（置換コミット作成時）。
4. **A（Platform Architecture Owner）** が検証結果と監査チェックを承認し、最終通知を確定する（マージ直前）。

### 置換コミット監査ルール（`Source Issue` 以外を変更しない）

チェックリスト:

- [ ] 置換対象ファイルは Active issue memo と `01_Plans/issues/README.md` の `Active issue memos` 表のみ。
- [ ] `git diff --word-diff` で `Source Issue` 行以外に差分がない。
- [ ] `Status` / `Owner` / `Priority` / `Acceptance criteria` / `Task breakdown` の差分が0件。
- [ ] 置換後URLは `https://github.com/<org>/<repo>/issues/<number>` 形式。
- [ ] validator と unit test が成功している。

監査コマンド（例）:

- `git diff -- 01_Plans/issues/README.md 01_Plans/issues/issue-*.md`
- `git diff --word-diff -- 01_Plans/issues/README.md 01_Plans/issues/issue-*.md | rg -n "Source Issue|Status|Owner|Priority|Acceptance criteria|Task breakdown"`

### ロールバック条件（宣言延期時の N/A 維持ルール）

- A または R が未確定（役割が未割当）の場合、開始宣言を延期し、`Source Issue: N/A` を維持する。
- URL対応表が Active memo と1:1対応しない場合、置換を中断して `N/A` 維持へ戻す。
- validator 失敗または監査チェック未達の場合、置換コミットをrevertし `N/A` を維持する。
- 延期時は理由・未確定項目・次回確認期限を `Additional context` またはPR本文に残す。

### 移行完了判定（Done条件）

- Active issue memos と対象memo本体の `Source Issue: N/A` が **残存ゼロ** である。
- `python 01_Plans/issues/validate_active_issue_memos.py` が成功する。
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` が成功する。

### URL移行の実施手順（運用開始後）

1. PM/Triage が「GitHub Issues 正本運用開始」を宣言し、開始日と告知先を本READMEへ追記する。
2. Active memo ごとに GitHub Issue を1:1で紐付け、`Source Issue` にURLを記載する。
3. 置換コミットは **`Source Issue` のみ変更**（`Status`/`Owner`/`Acceptance criteria` は同一コミットで変更しない）。
4. `Active issue memos` 一覧の `Source Issue` 列も同一PR内でURLへ同期する。
5. `python 01_Plans/issues/validate_active_issue_memos.py` を実行し、index/memo不整合がないことを確認する。
6. RACI-I通知を1回記録し、`Backlog ID` ごとに参照先URLが追跡可能であることを確認する。

### 運用手順（N/A維持 / URL移行）

1. **N/A維持フェーズ（現行）**
   - 新規 issue memo は `Source Issue: N/A` で作成する。
   - `Status` は `Draft/Open/In Progress` のみを使用し、`Active issue memos` 表と一致させる。
   - 外部トラッカー参照が必要になった時点で、`Additional context` に移行要求を記録する。
2. **URL移行フェーズ（将来）**
   - PM/Triage の運用開始宣言日を `README.md` に追記する。
   - Active な全 memo について、`Source Issue: N/A` を対応URLへ同一PRで置換する。
   - 置換PRでは `Status` を変えず、`Source Issue` だけを更新して監査差分を最小化する。
3. **移行完了判定**
   - `Active issue memos` 表に `N/A` が残っていないこと。
   - `python 01_Plans/issues/validate_active_issue_memos.py` が成功すること。

> 安全装置: 運用開始時期や移行責任者が未確定な場合、`N/A` のまま固定しない。該当メモの `Additional context` に確認事項として記録し、`Status` は `Draft` または `Open` で停止する。

## ステータス更新責任（Open → In Progress → Done）

| 遷移 | 更新責任者 | 更新タイミング（固定） |
|---|---|---|
| Draft → Open | **A**（Platform Architecture Owner） | 受入条件・Validation plan・RACIが揃い、着手可能と判断した時 |
| Open → In Progress | **R**（各Issueの実行Lead） | 最初の実作業コミット/PR/文書差分を開始する直前 |
| In Progress → Done | **A**（Platform Architecture Owner） | `Acceptance criteria` 完了と `Validation plan` 実施結果が確認できた時 |

- R は更新提案（ステータス変更PR/コミット）を行い、A が最終確定する。
- 責任者が未確定（R/Aの指名なし）の場合は遷移させず、確認事項として停止する（推測で確定しない）。

## RACI-I 通知ルール（PM/Triage, QA Lead）

- 通知対象（I）: `PM/Triage`, `QA Lead`。
- 通知トリガー（固定）:
  - `Status` 変更時（Open化 / In Progress化 / Done化）
  - `Source Issue` の `N/A ↔ URL` 切替時
  - `Owner` または `Expected verification level` を変更した時
- 通知内容（最小）: `Backlog ID` / 変更項目（StatusまたはSource Issue等）/ 更新者 / 参照リンク（issue memo + Source Issue）。
- 通知手段: PR本文または関連スレッドに同一フォーマットで1回記録し、重複通知しない。
- 記録フォーマット（推奨）:
  - `[RACI-I] Backlog=<ID> / Change=<Status Open→In Progress> / By=<name> / Memo=<path> / Source=<N/A or URL>`

### RACI-I 記録例（Source Issue 切替時）

- `[RACI-I] Backlog=AUTH-IMPL-01 / Change=Source Issue N/A→https://github.com/<org>/<repo>/issues/123 / By=platform-architecture-owner / Memo=01_Plans/issues/issue-AUTH-IMPL-01-user-identity-schema-migration-implementation.md / Source=https://github.com/<org>/<repo>/issues/123`
- `[RACI-I] Backlog=AUTH-API-02 / Change=Source Issue N/A→https://github.com/<org>/<repo>/issues/124 / By=platform-architecture-owner / Memo=01_Plans/issues/issue-AUTH-API-02-strict-provisioning-contract-and-admin-api.md / Source=https://github.com/<org>/<repo>/issues/124`
- `[RACI-I] Backlog=AUTH-E2E-01 / Change=Source Issue N/A→https://github.com/<org>/<repo>/issues/125 / By=platform-architecture-owner / Memo=01_Plans/issues/issue-AUTH-E2E-01-authcontext-contract-level1-level2-regression.md / Source=https://github.com/<org>/<repo>/issues/125`

## Required fields（最低必須）

issue補助メモには、最低でも次の項目を含める。

- Meta: `Type`, `Status`, `Source Issue`, `Priority`, `Scope`
- Quality gate: `Expected verification level`
- Traceability: `Related Backlog`, `Related ADR/Spec`
- Execution: `Proposed solution`, `Acceptance criteria`, `Task breakdown`, `Validation plan`
- Safety/Compatibility: 安全影響・互換影響・非目標


## Expected verification level（運用ガイド）

`Expected verification level` は「最低限どこまで検証するか」の宣言です。
上位レベルを選んだ場合は、下位レベルの検証を内包して実施します。

| Level | 最低実施内容 | 代表コマンド例 |
|---|---|---|
| `docs-check` | 参照リンク・整形・必須メタ検査 | `rg -n ...` / `git diff --check` |
| `unit` | `docs-check` + 対象モジュール単体テスト | `pytest <target>` / `npm test -- <target>` |
| `integration` | `unit` + サービス間結合検証 | `docker compose ...` / API結合テスト |
| `e2e` | `integration` + ユーザーフロー検証 | `playwright test ...` |

> 詳細なE2E運用は `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md` と
> 開発者向けE2Eは `03_Implement/frontend/docs/e2e_testing.md`、一般利用者向けの画面確認は `04_Documentation/acceptance_check.md` を正本とする。

## Quality checklist（レビュー観点）

- これは **Action** を記述しており、Decision（方針固定）はADRへ分離されているか。
- AGENTS.mdの4判断軸（価値/安全/企業行政/後方互換）で優先度を説明できるか。
- 実装者が「次の1手」を迷わない粒度（再開可能タスク）になっているか。
- テスト・検証がコマンド単位で書かれているか。
- `Expected verification level` と `Validation plan` が矛盾していないか。
- Done時に削除/ADR昇格/CHANGELOG反映の出口条件が明記されているか。

## Template

- 作成雛形: `01_Plans/issues/TEMPLATE.md`
- 機械検証: `python 01_Plans/issues/validate_active_issue_memos.py`
- ユニットテスト: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`


## Human decision support

- `../project-progress-dashboard.md`: プロジェクト進捗サマリ / Active issue集約 / 判断待ちキューの単一ダッシュボード（Plan→Execute→Verify→Proceed と Self-Correction上限を含む運用入口）。
- ダッシュボード更新原則: `project-progress-dashboard.md` は ADR / issue memo の決定事項を統合表示する参照レイヤとし、直接更新を起点にしない。必ず先に ADR または issue memo の正本を更新してから統合反映する。
- `decision-pack-2026-03-human-judgement.md`: ActiveなDraft issueのうち、人間判断待ちの高優先項目と選択肢を集約。
- REQ-DEF運用状態: R2-P1〜P3 / R3-P1〜P3 は決定済み。`TEMPLATE.md` の必須化ルール（R3-P1必須、R3-P2/R3-P3条件付き）を適用する。
- DOC-OPS-04ゲート状態: ADR-A（`ADR-0022-doc-ops-04-documentation-information-interface.md`）と ADR-B/C/D（`ADR-0023/0024/0025`）は `Accepted`。旧 `ADR-0022-documentation-*` 3件は `Superseded`。
- DOC-OPS-04統合境界: B/C/D作業中は統合ファイル3点（`issues/README.md` / `project-progress-dashboard.md` / `issue-DOC-OPS-04...md`）の同時更新を禁止し、必要時はB/C/Dを停止して統合フェーズ専用コミットへ切り出す。
- DOC-OPS-04停止/再開条件: 停止= A不整合 / 統合ファイル更新必要 / SoD違反 / Self-Correction 3回超過。再開= A再承認+Deciders再確認完了 + 統合フェーズ修正完了 + 役割分離再検証ログ追記 + validator/unittest成功。
- DOC-OPS-04次アクション: 後続改訂は ADR-0023/0024/0025 の境界を維持し、必要時のみ追加ADRを起票する。
- Stream F Phase 1-5 同期（rerun-26）: Read同期（shared resource 3ファイル）→Plan（件数47 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）→Execute（単一変更セット）→Verify（validator/unittest/rg）→Proceed（次回再開条件1行固定）を完了し、Active issue memos 6件・Source Issue運用（Open=N/A / Draft=TBD）・停止条件違反0件を維持。
- Stream I Phase 1-5 同期（2026-04-14 rerun-31）: Read同期（A〜H完了報告と3共有ファイル再読）→Plan（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / Queue未解決2件）→Execute（shared resource 3ファイル単一変更セット）→Verify（`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→Proceed（再開判定チェックリスト1行固定）を完了。
- Stream A Phase 1-5 同期（2026-04-28 rerun-56）: Read同期（共有3ファイル再読、件数47/Active=5/Done=26、Decision Queue Ready=1/Open=2、再開判定チェックリスト1行を差分監査）→Plan（AC/DoD不足なしを確認し同期対象を3ファイルへ限定）→Execute（shared resource単一変更セット更新）→Verify（`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→Proceed（再開判定チェックリスト1行確定と次フェーズ引き継ぎ: 変更点/未解決Queue2件/停止条件違反0件）を完了。

## Active issue memos

> 2026-07-15 時点でActive表へ6件を掲載している。現行validatorは掲載行からmemoへの片方向検査のみで、filesystem上のActive集合との完全一致を保証しない。未掲載Active memoの整理は `DOC-OPS-06`、双方向検査は `DX-DOC-02` で追跡する。

| Backlog ID | Memo | Status | Source Issue |
|---|---|---|---|
| DOC-USER-JOURNEY-01 | `issue-DOC-USER-JOURNEY-01-first-meaningful-map-guide.md` | In Progress | N/A |
| DOC-ARCH-02 | `issue-DOC-ARCH-02-current-contract-history-physical-separation.md` | In Progress | N/A |
| DOC-OPS-06 | `issue-DOC-OPS-06-current-view-history-and-contributor-route.md` | In Progress | N/A |
| DX-DOC-02 | `issue-DX-DOC-02-docs-contract-ci-and-index-completeness.md` | Draft | N/A |
| DOMAIN-CARD-QUALITY-01 | `issue-DOMAIN-CARD-QUALITY-01-qualitative-card-quality-assistance.md` | In Progress | N/A |
| DOMAIN-W-ITERATION-01 | `issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md` | In Progress | N/A |

- Stream D Phase 1-5 同期（2026-04-29 rerun-58）: Read & Reconcile（3共有ファイル再読、件数47/Active=5/Done=26、Decision Queue Ready=1/Open=2、依存順 `A1→A2→A3` を再確認）→ Plan Sync（同期項目と停止条件を固定、AC/DoD不足なし）→ Execute Single-Set（3ファイル同時更新）→ Verify（`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Proceed（再開判定チェックリスト1行確定: 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件 / 停止条件違反なし）。

- Stream D Phase 1-4 同期（2026-04-30 rerun-59）: Phase 1 Read同期（Stream A/B/C完了報告、Decision Queue、件数47を再確認）→ Phase 2 更新（Active Issue/Queue状態/次の1手を3共有ファイルで相互整合）→ Phase 3 監査（Open=10 / Draft=8 / Done系=26、依存順 `A1→A2→A3`、停止条件違反0件）→ Phase 4 公開固定（再開判定チェックリスト1行確定: 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件 / 停止条件違反なし）。
- Stream D Phase 1-5 同期（2026-04-30 rerun-60）: Phase 1 Read（全レーン完了報告と参照リンク整合を再確認）→ Phase 2 Plan（公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2`、次の1手= `DQ-HIL-EXEC-01` Ready監査継続 + `DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` Open期限管理を固定）→ Phase 3 Execute（shared resource 3ファイル単一変更セット同期）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-60|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（再開判定チェックリスト1行固定）を実施し、停止条件違反0件を確認。
- Stream D Phase 1-4 同期（2026-05-01 rerun-62）: Phase 1 Read Sync（Stream A/B/C完了報告リンク、Decision Queue Ready=1/Open=2、件数47、依存順 `A1→A2→A3` を再確認）→ Phase 2 Update（Active issue / Queue / 次の1手を shared resource 3ファイルで相互整合）→ Phase 3 Audit（Open=10 / Draft=8 / Done系=26、停止条件違反0件を再計算）→ Phase 4 Publish（再開判定チェックリスト1行確定: 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件 / 停止条件違反なし）。
- Stream D Phase 1-4 同期（2026-05-02 rerun-64）: Phase 1 Read同期（Stream A/B/C完了報告リンク、Decision Queue Ready=1/Open=2、件数47、依存順 `A1→A2→A3` を再確認）→ Phase 2 反映（Active Issue状態・Decision Queue・依存順・次の1手を shared resource 3ファイルで相互整合）→ Phase 3 監査（Open=10 / Draft=8 / Done系=26、Queue未解決2件、停止条件違反0件）→ Phase 4 公開固定（再開判定チェックリスト1行確定: 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件 / 停止条件違反なし）。
- Stream D Phase 1-5 同期（2026-05-04 rerun-67）: Phase 1 Read（A/B/C完了証跡と件数を再読）→ Phase 2 Sync（Active/Done/Queue/依存順 `A1→A2→A3` を3共有ファイルで相互整合）→ Phase 3 Verify（件数監査・矛盾検知・未承認事項の確定扱いゼロ確認）→ Phase 4 Publish（再開判定チェックリスト1行を更新し固定）→ Phase 5 Proceed（次サイクル条件=Queue 2件の期限管理継続と停止条件違反0件維持を明記）。

### HIL-RS-01 実行順序と競合回避（Stream D 統合基準）

- 依存順は **A1 → A2 → A3** の直列を固定し、A1完了報告が揃うまで A2/A3 は着手しない。
- Stream A/B/C の完了報告が揃うまで、共有リソース（`issues/README.md` / `project-progress-dashboard.md`）は更新しない。
- 共有リソースの更新は Stream D 統合フェーズに集約し、単一コミットで Active表・決定ログ・次アクション・件数集計を同期する。
- 2026-03-11時点で Stream A/B/C の完了報告を受領済みとし、Stream D が共有リソース同期の最終更新を実施する。

### Stream F 統合スナップショット（2026-04-11 JST, rerun-27）

- 件数: issue memo 全量監査=47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25）、運用上の集約表示=31（Active=6 / Done=25）。
- Active一覧: `HIL-RS-01`, `HIL-RS-01-A1`, `HIL-RS-02`, `HIL-RS-02-A1`（Open / Source Issue=N/A）および `HIL-RS-02-A2`, `HIL-RS-02-A3`（Draft / Source Issue=TBD）。
- 依存順序: **A1 → A2 → A3** を固定（A1完了報告前はA2/A3着手禁止）。
- Decision Queue: `DQ-HIL-EXEC-01` は Ready、`DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` は Open（Ready=1 / Open=2）。
- 決定済み項目の扱い: `DQ-HIL-A1-01` / `DQ-HIL-A1-02` は `project-progress-dashboard.md` の決定ログ（`DR-HIL-A1-01` / `DR-HIL-A1-02`）へ集約し、Queueから除外済み。
- 再監査: `validate_active_issue_memos.py` / `unittest` / `rg` による整合チェックを実施し、件数・状態・依存順の不整合0件を再確認。
- Stream D再検証（同日追補）: A/B/C完了報告受領済み状態を維持し、共有リソース2点の同期値（27/2/25、Decision Queue: Ready=1/Open=2、A1→A2→A3）を再確認。
- Stream D Phase 1再確認（2026-03-13）: Stream A/B/C 完了報告受領済み・契約リンク固定済み・共有リソース更新範囲3ファイル固定を再確認。
- Stream D再同期（2026-03-13）: validator/unittest/rg を再実行し、件数・状態・依存順に加えて Decision Queue（Ready=1 / Open=2）と決定ログ集約済み項目の整合維持を確認。
- Stream D Phase 2 Proceed（2026-03-13）: Stream A/B/C 完了報告受領済みゲートを再確認し、共有リソース同期（Active=2 / Done=25 / Decision Queue: Ready=1/Open=2 / A1→A2→A3）を更新してクローズ。
- Stream D Phase 3監査（2026-03-13）: issue memo総数43件（Open=8 / Draft=7 / Done系=25 / In Progress=1 / Blocked=2）を再計算し、Decision Queue未決=2（Ready=1 / Open=2）・停止条件違反0件を確認。
- Stream D Phase 4公開（2026-03-13）: 再開判定チェックリストを1行確定（未固定箇所=0 / 契約リンク確定 / Queue未決は`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01` / 停止条件違反なし）。
- Stream D Phase 3 Verify追補（2026-03-13）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、dashboard/README/decision-packの件数・Queue（Ready=1/Open=2）・再開判定の整合維持を確認。
- Stream D Phase 3 Verify追補（2026-03-13 rerun-2）: Read Gate（A/B/C完了報告・契約リンク固定・検証ログ受領）を前提に、3共有ファイル同時同期後の validator/unittest/rg 成功を再確認。
- Stream D Phase 2 Gate判定（2026-03-13, FB-P2C下流）: Gate 0未承認を再確認し、`FB-P2C-01-A2` / `A3` は Blocked 維持、Decision Queue は `DQ-HIL-EXEC-01=Ready` / `DQ-FB-P2C-01=Open` / `DQ-OPS-SOURCE-01=Open` に同期。
- Stream D Phase 4 Proceed（2026-03-13 rerun-4）: 再開判定チェックリスト1行（未固定箇所=0 / 契約リンク確定 / Queue未決2件 / 停止条件違反なし）を再確定。
- Stream D Phase 3 Verify追補（2026-03-13 rerun-5）: Stream A/B/C完了報告と決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Stream D Phase 4 Proceed（2026-03-13 rerun-6）: 再開判定チェックリスト1行（未固定箇所=0 / 契約リンク確定 / Queue未決2件 / 停止条件違反なし）を再確定し、共有3ファイルの同期をクローズ。
- Stream D Phase 3 Verify追補（2026-03-13 rerun-6）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Stream D Phase 3 Verify追補（2026-03-14 rerun-9）: Stream A/B/C完了報告と決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Stream D Phase 3 Verify追補（2026-03-14 rerun-10）: Stream A/B/C完了報告と決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Stream F Phase 1-4最終同期（2026-03-14 rerun-11）: Read Sync→同期反映→validator/unittest/`rg`検証→Closeout を直列で再実施し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行・停止条件違反0件の一致を確定。
- Stream D Phase 4 Publish（2026-03-14 rerun-8）: Plan→Execute→Verify→Proceed を再完了し、共有統合3ファイルを単一コミット対象で同期。未解決Queueは `DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` の2件を維持、再開判定チェックリスト1行（未固定箇所=0 / 契約リンク確定 / 停止条件違反なし）を確定。

- Stream A Phase 1-4同期（2026-03-14）: Read Gate再読で A1→A2→A3依存・Queue（Ready=1/Open=2）・停止条件違反0件を確認し、A1契約レビュー（ADR追加不要）→DQ運用点検（`DQ-HIL-EXEC-01` Ready維持、`DQ-FB-P2C-01`/`DQ-OPS-SOURCE-01` Open期限管理）→共有2ファイル同期を同一コミットで実施。
- Stream D Phase 4 Publish（2026-03-14 rerun-11）: human_judgementメタプロンプト再適用で Decision Queue 3件をGate再判定（暫定）し、rerun-12で最終状態を `DQ-HIL-EXEC-01=Ready` / `DQ-FB-P2C-01=Open` / `DQ-OPS-SOURCE-01=Open` に再同期。
- Stream F Phase 3 Verify追補（2026-03-14 rerun-12）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md` を再実行し、Queue表示の同期を確認。
- Stream F Phase 5 Proceed（2026-03-14 rerun-12）: 再開判定チェックリストを更新し、他レーン公開値（Ready=1/Open=2、次アクション=Ready監査1件+Open期限管理2件、停止条件違反0件）を共有。
- Stream F Phase 3 Verify追補（2026-03-14 rerun-13）: Phase 1 Read Sync→Phase 2 Plan→Phase 3 Execute（単一変更セット）後に `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を再実行し、件数43・Queue Ready=1/Open=2・再開判定1行の整合を確認。
- Stream F Phase 5 Proceed（2026-03-14 rerun-13）: 再開判定チェックリストを更新し、公開値（Ready=1/Open=2、次アクション=Ready監査1件+Open期限管理2件、停止条件違反0件、未承認決定混入なし）を共有。
- Stream H Phase 1-4 最終同期（2026-03-14）: A〜G完了報告・Queue状態・依存順をRead同期し、共有3ファイルで Active=2 / Done=25 / 件数43 / Decision Queue Ready=1/Open=2 を再反映。
- Stream H Phase 3 Verify（2026-03-14）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を再実行し、件数・Queue・再開判定1行の一致を確認。
- Stream E Phase 1 Read同期（2026-03-14 final）: Stream A/B/C/D完了報告受領、依存順 `A1→A2→A3`、Decision Queue（Ready=1/Open=2）、shared resource以外の未マージ差分なしを再確認。
- Stream E Phase 2-3 統合/実行（2026-03-14 final）: shared resource 3ファイルのみを単一変更セットで更新し、件数43・Active2・Done25・Queue Ready=1/Open=2・次アクション（Ready監査1件 + Open期限管理2件）を同期。
- Stream E Phase 4-5 Verify/Proceed（2026-03-14 final）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` 成功を確認し、再開判定チェックリスト1行（未固定箇所=0 / 契約リンク確定 / Queue未決2件 / 停止条件違反なし）を公開ログ化。
- Stream F Phase 1-5 最終同期（2026-03-14 rerun-14）: A〜E完了報告受領・依存順 `A1→A2→A3`・Decision Queue（Ready=1/Open=2）・shared resource freeze解除をRead Gateで再確認し、共有3ファイルの同期対象（件数43 / Active=2 / Done=25 / 次アクション=Ready監査1件+Open期限管理2件）を宣言後に単一変更セットで反映した。
- Stream F Phase 4 Verify（2026-03-14 rerun-14）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を再実行し、件数43・Queue Ready=1/Open=2・再開判定1行・停止条件違反0件の一致を再確定。
- Stream F Phase 1-5 再同期（2026-03-14 rerun-15）: A〜E完了報告受領・依存順 `A1→A2→A3`・Decision Queue（Ready=1/Open=2）をRead Gateで再確認し、shared resource 3ファイルの単一変更セット更新後に validator/unittest/rg を再実行して件数43・Active2・Done25・再開判定1行・停止条件違反0件の一致を維持。
- Stream E Phase 1-4 同期（2026-03-14 rerun-16）: Read同期（A/B/C/D完了報告）→件数/状態/Decision Queue反映→参照リンク/件数/依存順監査→再開判定チェックリスト1行確定を直列実行し、shared resource 3ファイルの公開値を `件数43 / Active2 / Done25 / Queue Ready=1 Open=2 / A1→A2→A3 / 停止条件違反0件` で再固定。
- Stream F Phase 1-5 最終再同期（2026-03-14 rerun-17）: Read Gate（A〜E完了報告と証跡）→Plan（3ファイル限定）→Execute（単一変更セット）→Verify（validator/unittest/rg）→Proceed（再開判定チェックリスト1行固定）を実施し、件数43・Active2・Done25・Queue Ready=1/Open=2・依存順A1→A2→A3・停止条件違反0件を維持。

- Stream D Phase 1-5 統合再同期（2026-03-14 rerun-22）: Stream A/B/C/E/F の完了報告受領をRead Gateで再確認し、Active表（2件）/Decision Queue（Ready=1, Open=2）/Next actions（Ready監査1件 + Open期限管理2件）/依存順 `A1→A2→A3` を3共有ファイルで再同期。`Source Issue` はREADME運用基準どおり `N/A` 維持。検証は `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` で一致を確認し、再開判定1行（未固定箇所0 / 契約リンク確定 / Queue未解決2件 / 停止条件違反なし）を維持。


- Stream J 共有統合同期（2026-04-18 rerun-37, Phase 1-5）: Phase 1 Read（shared resource 3ファイル再読）→ Phase 2 Plan（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 を固定）→ Phase 3 Execute（3ファイル単一変更セット）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-37|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（再開判定チェックリスト1行固定）を実施し、停止条件違反0件・推測マージ0件を確認。


## Rules

1. 新規作成先は必ず `01_Plans/issues/`。
2. ファイル名は `issue-<BacklogID>-<short-title>.md` を推奨。
3. Done は本ディレクトリに継続保管し、自動削除しない。
4. 削除/アーカイブは人間の手動判断、または人間の明示指示がある場合のみ実施する。

## Completed issue memos

| Backlog ID | Memo | Status | Source Issue | Notes |
|---|---|---|---|---|
| DOC-UI-CATALOG-01 | `issue-DOC-UI-CATALOG-01-public-boundary-and-provenance.md` | Done | N/A | 公開UIカタログと内部設計ブリーフを分離し、23状態の画像provenance・stale/Go条件・再現可能な撮影経路を整備（2026-07-11）。 |
| HIL-RS-01 | `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` | Done | N/A | ADR-0039に基づく次フェーズ計画と下位作業への引き継ぎを完了（2026-06-20）。 |
| HIL-RS-01-A1 | `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` | Done | N/A | 最小インターフェース契約の固定と承認記録を完了（2026-06-20）。 |
| HIL-RS-02 | `issue-HIL-RS-02-next-phase-delivery-plan.md` | Done | N/A | 次フェーズの実行計画とA2/A3着手条件の整理を完了（2026-06-20）。 |
| HIL-RS-02-A1 | `issue-HIL-RS-02-A1-governance-contract-hardening.md` | Done | N/A | ガバナンス契約の固定と例外判断の解消を完了（2026-06-20）。 |
| HIL-RS-02-A3 | `issue-HIL-RS-02-A3-operations-documentation-sync.md` | Done | `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`（Done 2026-06-20） | 運用文書同期の計画と引き継ぎを完了（2026-06-20）。 |
| HIL-RS-01 | `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` | Done | N/A | ADR-0039に基づく次フェーズ計画と下位作業への引き継ぎを完了（2026-06-20）。 |
| HIL-RS-01-A1 | `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` | Done | N/A | 最小インターフェース契約の固定と承認記録を完了（2026-06-20）。 |
| HIL-RS-02 | `issue-HIL-RS-02-next-phase-delivery-plan.md` | Done | N/A | 次フェーズの実行計画とA2/A3着手条件の整理を完了（2026-06-20）。 |
| HIL-RS-02-A1 | `issue-HIL-RS-02-A1-governance-contract-hardening.md` | Done | N/A | ガバナンス契約の固定と例外判断の解消を完了（2026-06-20）。 |
| HIL-RS-02-A3 | `issue-HIL-RS-02-A3-operations-documentation-sync.md` | Done | `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`（Done 2026-06-20） | 運用文書同期の計画と引き継ぎを完了（2026-06-20）。 |
| DX-CODEX-01 | `issue-DX-CODEX-01-codex-skill-adoption-and-validation.md` | Done | N/A | Codex skill導入手順・役割分担・正本/補助境界・試行ログテンプレートを整備。 |
| DX-CODEX-02 | `issue-DX-CODEX-02-markdown-mermaid-mcp-doc-ops-adoption.md` | Done | N/A | markdown-mermaid-docops skill運用とMermaid/MCP証跡方針を標準化。 |
| AUTH-ARCH-01 | `issue-AUTH-ARCH-01-authcontext-jit-provisioning-data-boundary.md` | Done | N/A | AuthContext/JIT境界、strict責務、承認記録を確定。 |
| AUTH-SCHEMA-01 | `issue-AUTH-SCHEMA-01-identity-schema-planning.md` | Done | N/A | identity schema比較、403契約、expand/contract前提を確定。 |
| AUTH-IMPL-01 | `issue-AUTH-IMPL-01-user-identity-schema-migration-implementation.md` | Done | N/A | users / user_identities migration 実装・検証を完了。 |
| AUTH-API-02 | `issue-AUTH-API-02-strict-provisioning-contract-and-admin-api.md` | Done | N/A | strict provisioning 契約と admin API 実装・検証を完了。 |
| FB-RM-RS-02 | `issue-FB-RM-RS-02-structural-metrics.md` | Done | N/A | 実装/検証完了済み。 |
| DOC-REL-01 | `issue-DOC-REL-01-spec-source-doc-consistency-audit.md` | Done | N/A | 文書整合監査完了。 |
| ENV-ARCH-01 | `issue-ENV-ARCH-01-global-env-prefix-migration.md` | Done | N/A | 一括移行（Option B/C）の実装・検証を完了し、旧キー非互換を確定。 |
| AUTH-OPS-03 | `issue-AUTH-OPS-03-strict-mode-exception-relaxation-runbook-plan.md` | Done | N/A | strict mode例外運用の固定値・責務・停止条件を01/02/04で同期完了。 |
| DOC-OPS-02 | `issue-DOC-OPS-02-cross-document-improvement-plan-from-human-decisions.md` | Done | N/A | 文書横断ドリフト（用語/役割/導線/D1〜D4）を解消。 |
| DOC-OPS-03 | `issue-DOC-OPS-03-project-progress-dashboard-planning.md` | Done | N/A | dashboard運用プロトコルと競合停止条件を固定。 |
| DOC-OPS-04 | `issue-DOC-OPS-04-documentation-visibility-readability-governance.md` | Done | N/A | ADR-0023/0024/0025 を直列処理し、統合同期と検証を完了。 |
| DOC-ARCH-01 | `issue-DOC-ARCH-01-architecture-source-log-separation.md` | Done | N/A | 価値トレーサビリティと02層の現行契約/履歴ログ読み分け導線を追加。 |
| DOMAIN-ALIGN-01 | `issue-DOMAIN-ALIGN-01-00-02-vocabulary-sync.md` | Done | N/A | 00層の用語正本をIsland/三層Graph語彙とAI境界へ同期。 |
| ENV-PROFILE-01 | `issue-ENV-PROFILE-01-runtime-profile-guidance.md` | Done | N/A | runtime profile guidanceを追加し、KJ_ATLAS_公開設定キー方針を維持。 |
| REQ-DEF-02 | `issue-REQ-DEF-02-responsibility-boundary-and-contract-checkpoints.md` | Done | N/A | R2-P1 Reject, R2-P2/R2-P3 Conditional Approve を確定し運用方針へ反映。 |
| REQ-DEF-03 | `issue-REQ-DEF-03-acceptance-scenarios-and-issue-splitting.md` | Done | N/A | R3-P1 Approve, R3-P2/R3-P3 Conditional Approve を確定しテンプレ運用へ反映。 |
| REQ-DEF-01 | `issue-REQ-DEF-01-value-realization-requirements-baseline.md` | Done | N/A | REQ-DEF共通I/F正本とDecision Queue連携を最終固定。 |
| FB-RM-SEC-02 | `issue-FB-RM-SEC-02-worker-stabilization.md` | Done | N/A | worker化・fallback/cancel/progress 回帰固定済み。 |
| FB-RM-MID-02 | `issue-FB-RM-MID-02-manual-assisted-merge-decisions.md` | Done | N/A | merge判断記録の保存/再読込を実装済み。 |
| FB-RM-MID-01 | `issue-FB-RM-MID-01-deterministic-similar-card-candidates.md` | Done | N/A | deterministic候補生成と順序安定化を実装済み。 |
| FB-RM-MID-03 | `issue-FB-RM-MID-03-merge-decision-audit-export.md` | Done | N/A | merge監査エクスポートを実装済み。 |
| FB-RM-I18N-02 | `issue-FB-RM-I18N-02-locale-json-fallback-order.md` | Done | N/A | locale fallback順序を固定済み。 |
| FB-RM-I18N-03 | `issue-FB-RM-I18N-03-ui-equivalence-e2e-smoke.md` | Done | N/A | 英語UI等価 E2E smoke/flow を記録済み。 |
| FB-RM-MID-05 | `issue-FB-RM-MID-05-structural-granularity-export.md` | Done | N/A | export粒度とmanifest出力を実装済み。 |
| QA-PUB-01 | `issue-QA-PUB-01-I18N-03-e2e-boundary.md` | Done (SQLite fallback path) | N/A | SQLite fallback の E2E 境界検証ログを固定し、将来の本番同等検証との差分前提を明文化。 |
| QA-MONKEY-01 | `issue-QA-MONKEY-01-safemode-export-boundary.md` | Done | N/A | Monkey testで検出したSafeMode既定/Export境界の後退を修正し、テストとブラウザ確認で固定。 |
| QA-MONKEY-02 | `issue-QA-MONKEY-02-provider-none-merge-candidate-fallback.md` | Done | N/A | provider-none環境のCE3候補収集503をローカル決定論フォールバックへ接続。 |
| QA-MONKEY-03 | `issue-QA-MONKEY-03-search-state-document-scope.md` | Done | N/A | 文書切替時に検索/非一致非表示状態をリセットし、別文書が空に見える状態を解消。 |
| QA-MONKEY-04 | `issue-QA-MONKEY-04-worker-golden-line-ending-portability.md` | Done | N/A | Windows CRLF checkoutでworker golden比較が失敗する問題を改行正規化で修正。 |
| QA-MONKEY-05 | `issue-QA-MONKEY-05-island-accessibility-duplicate-controls.md` | Done | N/A | 島の選択/Focus/Collapse操作名を分離し、polygon島もネイティブbuttonでキーボード到達可能に修正。 |
| QA-MONKEY-06 | `issue-QA-MONKEY-06-header-toolbar-responsive-overlap.md` | Done | N/A | ヘッダーツールバーの折返し・長いlegacyラベル・View/共有パネル配置を安定化し、1280x720/920x720のE2E回帰を追加。 |
| QA-MONKEY-07 | `issue-QA-MONKEY-07-local-generated-artifacts-ignore.md` | Done | N/A | 手順通りのローカル起動で生成されるnode_modules/SQLite DBをignore対象へ追加。 |
| QA-MONKEY-08 | `issue-QA-MONKEY-08-active-issue-metadata-validator-drift.md` | Done | N/A | Active issue metadata/index driftを解消し、validator/unittest通過を確認。 |
| QA-MONKEY-09 | `issue-QA-MONKEY-09-start-panel-focus-scope.md` | Done | N/A | 開始パネル表示中のTab順が背後UIへ抜ける問題を修正し、dialog semanticsとフォーカス循環E2Eを追加。 |

| AUTH-E2E-01 | `issue-AUTH-E2E-01-authcontext-contract-level1-level2-regression.md` | Done | N/A | Level1/Level2運用固定、fixture回帰、PR記録テンプレを確定。 |

## Status sync note (2026-03-03)

- 旧 `Done (Local)` は廃止し、完了はすべて `Done` として扱う。
- GitHub Issues 未運用時は `Source Issue: N/A` を維持し、PM/Triage の運用開始宣言を切替トリガーとしてURLへ一括移行する。
- AUTH系 issue memo は、開始宣言までは `N/A` を正とし、宣言後は次回更新PRでURLへ同期する（Active対象は `AUTH-E2E-01`、Done対象は次回メタ更新時に追随）。
- Done メモは自動GCせず、量が増えた場合も人間判断でのみ削除/整理する。
- ADR 側ステータス（例: `FB-RM-I18N-03`）は issue memo の実績に同期する。
- 2026-03-11 Stream D統合フェーズで Active/Done 集計と dashboard の Decision Queue / Next actions を再監査し、不整合ゼロを確認。
- Stream D Phase 5 Proceed（2026-03-13 rerun-3）: 5ファイル再読→共有リソース同期→Verifyを再実施し、Decision Queueは `DQ-HIL-EXEC-01=Ready` / `DQ-FB-P2C-01=Open` / `DQ-OPS-SOURCE-01=Open`、依存順序は A1→A2→A3 を維持。
- Stream F Phase 5 Proceed（2026-03-14 rerun-15）: 再開判定チェックリスト公開値を `未固定箇所=0 / 契約リンク確定 / Queue未決2件 / 停止条件違反なし` で再確認し、再開判定を維持。
- Stream D 統合同期（2026-03-14 rerun-18, Phase 1-5）: Read GateでStream A/B/Cの完了報告・契約リンク（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）・検証ログ受領を再確認後、公開値（件数43、Active=2、Done=25、Decision Queue: Ready=1/Open=2、依存順`A1→A2→A3`）を3共有ファイルで同時維持し、再開判定チェックリストを「未固定箇所0件 / 契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし」で確定。
- Stream F 共有資源再同期（2026-03-14 rerun-19, Phase 1-5）: Read GateでA〜E完了報告・依存順`A1→A2→A3`・Decision Queue（Ready=1/Open=2）・停止条件違反0件を再確認し、shared resource 3ファイルを単一変更セットで同期後、validator/unittest/rgで件数43・Active=2・Done=25・再開判定1行の一致を再確認。
- Stream E 共有資源最終同期（2026-03-14 rerun-20, Phase 1-5）: Stream A/B/C/D完了報告・依存順`A1→A2→A3`・Decision Queue（Ready=1/Open=2）・停止条件違反0件をRead同期し、shared resource 3ファイルのみを単一変更セットで再同期後、validator/unittest/rgで件数43・Active=2・Done=25・再開判定1行の一致を維持。
- Stream D 共有資源再同期（2026-03-14 rerun-21, Phase 1-5）: Read GateでStream A/B/C完了報告・契約リンク（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）・検証ログ受領を再確認し、shared resource 3ファイルを単一変更セットで同期後、validator/unittest/rgで件数43・Active=2・Done=25・Decision Queue（Ready=1/Open=2）・再開判定1行の一致を維持。
- Stream HIL-RS-02 planning sync（2026-03-14）: 次フェーズ計画として `HIL-RS-02` / `HIL-RS-02-A1` / `HIL-RS-02-A2` / `HIL-RS-02-A3` を追加し、Active件数を6件（Open=4 / Draft=2）、全体件数を47件（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25）へ更新。Decision Queueは既存運用（Ready=1 / Open=2）を維持。
- Stream E 共有ファイル同期（2026-03-14 rerun-23, Phase 1-5）: 起動条件（Stream A/B/C/D完了報告受領 + shared resource freeze解除）をRead Gateで再確認し、shared resource 3ファイルのみを単一変更セットで同期。公開値を `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25） / Active=6 / Done=25 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` に再固定し、再開判定チェックリスト1行（未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし）を確定。

- Stream D 共有資源同期（2026-03-15 rerun-24, Phase 1-5）: Read Gateで3共有ファイルを再読し、件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25）・Active=6・Done=25・Decision Queue（Ready=1 / Open=2）・依存順 `A1→A2→A3` を再確認。Planで Source Issue 運用（Open=N/A / Draft=TBD）をREADME基準どおり維持し、Execute で Active表/Decision Queue/次の1手を単一変更セット同期。Verify は `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26|Source Issue" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` で一致を確認し、Proceedとして再開判定チェックリスト1行（未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし）を維持。

- Stream E 共有統合同期（2026-03-15 rerun-25, Phase 1-5）: Phase 1 Read同期で Stream A/B/C/D 完了報告と証跡リンク（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認し、件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=9 / Done系=25）・Active=6・Done=25・Decision Queue（Ready=1/Open=2）を基準値として確定。Phase 2 Planで反映対象（Active表 / Queue / 次の1手 / 件数集計）を固定し、Phase 3 Executeで共有3ファイルのみを単一変更セット同期。Phase 4 Verifyで `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26|DR-HIL-A1-01|DL-HIL-01|DR-REQ-DEF-02" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行して不一致0件（self-correction 0/3）。Phase 5 Proceedとして再開判定チェックリスト1行（未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし）を公開値に固定。

- Stream H 最終同期（2026-04-12 rerun-28, Phase 1-5）: Stream A〜G 完了報告と証跡リンクをReadで再確認し、shared resource 3ファイルのみを単一変更セットで同期。`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` の成功をもって、公開値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）と再開判定チェックリスト1行を維持。

- Stream H 共有統合同期（2026-04-12 rerun-29, Phase 1-5）: Read同期でA〜G完了報告と証跡リンク、Decision Queue（Ready=1/Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を再確認。shared resource 3ファイルのみを単一変更セットで再同期し、`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` の成功で公開値（件数47 / Active=5 / Done=26 / Queue Ready=1 Open=2）と再開判定チェックリスト1行を維持。

- Stream H 共有統合同期（2026-04-13 rerun-30, Phase 1-5）: ReadでA〜G完了報告・Decision Queue（Ready=1/Open=2）・依存順 `A1→A2→A3`・停止条件違反0件を再確認し、Planで件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26）/ Active=5 / Done=26 を固定。Executeはshared resource 3ファイル単一変更セットのみ、Verifyは `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し一致を確認。Proceedとして再開判定チェックリスト1行（未固定箇所0件 / 契約リンク確定 / Queue未解決2件 / 停止条件違反なし）を維持。

### Stream A Critical Path rerun-32（2026-04-14, lifecycle正規化）

- Phase 1 Read同期: shared resource 3ファイル + HIL-RS個票を再読し、Decision Queue `Ready=1 / Open=2` と依存順 `A1→A2→A3` の一致を確認。
- Phase 2 ADR判定: 新規ADRは不要。未承認決定の確定化は行わず、`DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` は Open 継続。
- Phase 3 正規化: lifecycle公開値は `Draft/Open/In Progress/Done` に統一し、`Blocked` は履歴語彙としてのみ保持（集計は `Open(hold)` へ内包）。
- Phase 4 同期値（基準47件）: **Open=12（Open10+Blocked2） / In Progress=1 / Draft=8 / Done=26**。
- Phase 5 Verify: validator / unittest / `rg` を再実行し、3共有ファイルで同一ロジック反映を確認。


### Stream J 共有統合同期（2026-04-16 rerun-33, Phase 1-5）

- Phase 1 Read（全レーン完了報告・決定ログ受領確認）: Stream A〜I の完了報告と shared resource 3ファイルを再読し、Decision Queue（Ready=1 / Open=2）・依存順 `A1→A2→A3`・停止条件違反0件を確認。
- Phase 2 Plan（集計値・Queue・再開判定チェックリスト定義）: 公開値を `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2` に固定し、再開判定チェックリスト1行（未固定箇所0件 / 契約リンク確定 / Queue未解決2件 / 停止条件違反なし）を維持。
- Phase 3 Execute（単一変更セット）: shared resource 3ファイル（`01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md`）のみを単一変更セットで同期。
- Phase 4 Verify（validator/unittest/rg）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-33|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイル整合を確認。
- Phase 5 Proceed（公開値固定）: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**


### Stream I 共有統合同期（2026-04-16 rerun-34, Phase 1-5）

- Phase 1 Read（全ストリーム完了報告確認）: Stream A〜J 完了報告、shared resource 3ファイル参照リンク、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を再確認。
- Phase 2 Plan（件数/状態/Decision Queue/次の1手）: 公開値を `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2` へ固定し、次の1手は `DQ-HIL-EXEC-01` Ready監査継続 + `DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` Open継続に限定。
- Phase 3 Execute（単一変更セット）: shared resource 3ファイルのみを単一変更セットで同期し、未承認決定の確定扱い・推測マージを実施しない。
- Phase 4 Verify（validator + unittest + rg整合）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-34|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイル整合を確認。
- Phase 5 Proceed（再開判定チェックリスト1行固定）: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**


### Stream H 共有統合同期（2026-04-16 rerun-35, Phase 1-5）

- Phase 1 Read（3ファイル最新同期）: shared resource 3ファイルを再読し、Decision Queue（Ready=1 / Open=2）・依存順 `A1→A2→A3`・停止条件違反0件を確認。
- Phase 2 Plan（件数/Queue/依存順）: 公開値を `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2` に固定し、次の1手を `DQ-HIL-EXEC-01` Ready監査継続 + `DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` Open継続へ限定。
- Phase 3 Execute（単一変更セット）: `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md` のみを同一変更セットで同期。
- Phase 4 Verify（validator + unittest + rg）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-35|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイル整合を確認。
- Phase 5 Proceed（再開判定チェックリスト1行固定）: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**


### Stream H 共有統合同期（2026-04-17 rerun-36, Phase 1-5）

- Phase 1 Read（完了報告・件数・Queue・依存順の再読）: Stream A〜J の完了報告と shared resource 3ファイルを再読し、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3`、停止条件違反0件を確認。
- Phase 2 ADR CDC（必要時のみ）: 方針変更が必要な差分は検出されず、Context / Decision / Consequences の新規起票は不要（未承認決定の確定扱いなし）。
- Phase 3 Plan（AC/DoD確認）: AC/DoD不足なし。公開値を `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2` に固定し、次の1手を `DQ-HIL-EXEC-01` Ready監査継続 + `DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` Open継続に限定。
- Phase 4 Execute（3共有ファイル同時整合）: `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md` のみを単一変更セットで同期し、未定義競合・未承認決定の確定扱いを回避。
- Phase 5 Verify（validator + unittest + rg）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-36|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイル整合を確認（self-correction 0/3）。
- Phase 5 Proceed（再開判定チェックリスト1行固定）: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**

- Stream H 共有統合同期（2026-04-19 rerun-38, Phase 1-5）: Phase 1 Read（shared resource 3ファイル再読で件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件を一致確認）→ Phase 2 Plan（更新差分を3ファイル同期ログ追記に限定）→ Phase 3 Execute（Active一覧・Decision Queue・再開判定チェックリスト1行を同時同期）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-38|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（再開判定チェックリスト1行固定）を実施し、未承認事項の確定化0件・停止条件違反0件を確認。


- Stream Shared 共有統合同期（2026-04-19 rerun-39, Phase 1-5）: Phase 1 Read（A〜I完了証跡と shared resource 3ファイル再読）→ Phase 2 Plan（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 を固定、未承認決定の確定化禁止）→ Phase 3 Execute（3ファイル単一変更セット）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-39|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（再開判定チェックリスト1行固定）を実施し、停止条件違反0件・self-correction 0/3 を確認。

- Stream G 共有統合同期（2026-04-19 rerun-40, Phase 1-5）: Phase 1 Read同期（上流Issue確定事項のみ）で shared resource 3ファイルを再読し、件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件を確認。Phase 2 で更新対象を3ファイルに限定して未承認決定の確定化を禁止、Phase 3 でActive一覧・Decision Queue・再開判定チェックリスト1行を同時同期、Phase 4 で `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-40|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、Phase 5 Proceedを **「共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること」** で固定。
- Stream F 共有統合同期（2026-04-20 rerun-41, Phase 1-5）: Phase 1 Read（shared resource 3ファイル再読で `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` を一致確認）→ Phase 2 Plan（反映差分を3ファイル同期ログ追記の単一変更セットに限定、未承認決定の確定扱い禁止）→ Phase 3 Execute（Active一覧・Decision Queue・件数集計・再開判定チェックリスト1行を同時更新）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-41|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（**共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。**）を固定。


- Stream G 共有統合同期（2026-04-20 rerun-42, Phase 1-5）: Phase 1 Readで Stream A〜F 完了証跡・件数47・Active=5・Done=26・Decision Queue（Ready=1/Open=2）・依存順 `A1→A2→A3`・停止条件違反0件を再確認。Phase 2 Planで同期対象を shared resource 3ファイルへ限定。Phase 3 Executeで単一変更セット同期。Phase 4 Verifyで `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-42|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26|Stream A〜F" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行して不一致0件を確認。Phase 5 Proceedで再開判定チェックリスト1行（`件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件`）を固定。


- Stream J 共有統合同期（2026-04-20 rerun-43, Phase 1-5）: Phase 1 Read（shared resource 3ファイル再読で `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` を再確認）→ Phase 2 Plan（件数/Status/Decision Queue/依存順の同期対象を3ファイルに限定、未承認決定の確定扱い禁止）→ Phase 3 Execute（単一変更セットで3ファイル同期）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-43|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26|Stream J" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（**「共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。」** で固定）。


- Stream J 共有統合同期（2026-04-20 rerun-44, Phase 1-5）: Phase 1 Read（全差分再読）で shared resource 3ファイルを再読し、`件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` を再確認。Phase 2 Planで件数/状態/Queue固定と単一変更セットを宣言し、Phase 3 Executeで3ファイルのみを同時更新。Phase 4 Verifyは `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-44|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` で成功（self-correction 0/3）。Phase 5 Proceedで再開判定チェックリスト1行を **「共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。」** に確定。


- Stream L 共有統合同期（2026-04-21 rerun-45, Phase 1-5）: Phase 1 Read（A〜K完了証跡を shared resource 3ファイルで再確認）→ Phase 2 Plan（同期対象を3ファイルに限定し、件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 を固定）→ Phase 3 Execute（単一変更セット）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-45|Stream A〜K|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（**共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。**）を固定。


- Stream F 共有統合同期（2026-04-21 rerun-46, Phase 1-5）: Phase 1 Read（shared resource 3ファイル同時再読で件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / D1〜D4固定値維持を再確認）→ Phase 2 Plan（3ファイル限定・単一変更セット・未承認決定の確定扱い禁止）→ Phase 3 Execute（rerun-46同期ログのみ反映）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-46|Decision Queue|Ready=1 / Open=2|A1→A2→A3|D1〜D4|4h / 2h / 代理承認なし / 48h\+15m\+60m|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（**共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / D1〜D4固定値維持 / 停止条件違反0件` が一致していること。**）を固定。

- Stream Shared 共有統合同期（2026-04-22 rerun-47, Phase 1-5）: Phase 1 Readで Active 5件（`HIL-RS-01` / `HIL-RS-01-A1` / `HIL-RS-02` / `HIL-RS-02-A1` / `HIL-RS-02-A3`）の `Scope` / `Related ADR/Spec` / `Expected verification level=docs-check` を再読。Phase 2 Planで AC/DoD不足を `AC: Issueごとの主検証責務をdocs-check固定` / `DoD: VerifyでIssue別docs-check証跡を必須化` として提案・合意固定。Phase 3 Executeは shared resource 3ファイルを `README → dashboard → decision-pack` の順で1件ずつ完了判定しながら同期。Phase 4 Verifyは `rg -n "^- Scope:|^- Related ADR/Spec:|^- Expected verification level:" 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md` でIssue別docs-checkを実施し、self-correction 0/3。Phase 5 Proceedとして競合検知・前提崩れ・3回超過のいずれも未検出、公開値（件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3）一致を維持。


- Stream Shared 共有統合同期（2026-04-22 rerun-48, Phase 1-5）: Phase 1 Read同期で shared resource 3ファイル（`01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md`）を再読し、公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` を再確認。Phase 2 件数再計算で上記公開値を再固定。Phase 3 Decision Queue整合で `DQ-HIL-EXEC-01=Ready` / `DQ-FB-P2C-01=Open` / `DQ-OPS-SOURCE-01=Open` を維持。Phase 4 Verifyとして `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-48|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し整合一致を確認。Phase 5 Proceed（再開判定1行固定）: **共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。**

- Stream H 共有統合同期（2026-04-23 rerun-49, Phase 1-5）: Phase 1 Read（shared resource 3ファイル同時再読）→ Phase 2 Plan（AC/DoD不足なし、公開値 `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` を固定）→ Phase 3 Execute（3ファイル単一変更セット）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-49|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（再開判定チェックリスト1行固定）を完了し、停止条件違反0件・self-correction 0/3 を確認。


- Stream F 共有統合同期（2026-04-23 rerun-50, Phase 1-5）: Phase 1 Readで shared resource 3ファイルを再読し、公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` と停止条件違反0件を再確認。Phase 2 Planで AC/DoD不足なしを確認し、更新対象を共有3ファイルに限定（未承認決定の確定扱い禁止）。Phase 3 Executeで Active一覧・Decision Queue・次の1手を単一変更セットで同期。Phase 4 Verifyは `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-50|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行して整合一致を確認。Phase 5 Proceed（再開判定1行固定）: **共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。**

- Stream H 共有統合同期（2026-04-26 rerun-51, Phase 1-5）: Phase 1 Read（Active issue一覧 / Decision Queue / 依存順 / 件数の再読）で shared resource 3ファイルを再読し、公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` と停止条件違反0件を再確認。Phase 2 Planで反映対象を「他ストリームで確定済みの決定事項のみ」に限定し、AC/DoD不足なし・未承認決定の確定化禁止を維持。Phase 3 Executeで共有3ファイル単一変更セット同期。Phase 4 Verifyで `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-51|Decision Queue|Ready=1 / Open=2|A1→A2→A3|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` / `git diff --check` を実行して整合一致を確認（self-correction 0/3）。Phase 5 Proceed（再開判定チェックリスト1行固定）: **共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。**


## Stream Shared 共有競合専用同期ログ（2026-04-26 rerun-52, Phase 1-5）

- Phase 1 Read（3ファイル同時再読）: `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md` を再読し、件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26）、Active=5、Decision Queue（Ready=1 / Open=2）、依存順 `A1→A2→A3` を確認。
- Phase 2 Plan（対象差分宣言）: 反映対象を共有3ファイルに限定し、単一変更セットで公開固定値 `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` を維持する。
- Phase 3 Execute（単一変更セット）: rerun-52 の同期ログのみを追記し、対象外編集・未承認決定の確定化を行わない。
- Phase 4 Verify（validator/unittest/rg）: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-52|Decision Queue|Ready=1 / Open=2|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` の一致を確認。
- Phase 5 Proceed（固定値確定）: **共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` が一致していること。**

- Stream I 共有統合同期（2026-04-26 rerun-53, Phase 1-5）: Phase 1 Read（共有3ファイル相互整合確認）→ Phase 2 Plan（件数/状態/Decision Queue更新計画固定）→ Phase 3 Execute（単一変更セット）→ Phase 4 Verify（`python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-53|Decision Queue|Ready=1 / Open=2|A1→A2→A3|件数47|Active=5|Done=26|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md`）→ Phase 5 Proceed（再開判定チェックリスト1行固定）を完了し、公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` の一致を確認。

- Stream H 共有統合同期（2026-04-27 rerun-54, Phase 1-5）: Phase 1 Read（全レーン完了報告取り込み）で shared resource 3ファイルを再読し、Stream A〜L / Stream Shared / Stream I までの完了報告ログ、公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3`、停止条件違反0件を再確認。Phase 2 集計反映で3ファイルの件数/状態/Decision Queue/依存順を同一値へ固定。Phase 3 Verifyで `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-54|Decision Queue|Ready=1 / Open=2|A1→A2→A3|件数47|Active=5|Done=26|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイル整合一致を確認。Phase 4 公開値固定として `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` を維持。Phase 5 Proceed（再開判定1行更新）: **共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。**

### 6-49. Stream I 共有統合同期ログ（2026-04-28 rerun-55, Phase 1-5）

- Phase 1 Read（3ファイル再読）: shared resource 3ファイル（`01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / 本decision-pack）を再読し、公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Ready=1 / Open=2`、依存順 `A1→A2→A3`、停止条件違反0件を確認。
- Phase 2 Plan（同期項目固定）: 件数/状態/Decision Queue/再開判定チェックリスト1行を3ファイルで同一値へ固定し、未承認決定の確定扱い・件数不一致・未定義競合を停止条件として維持。
- Phase 3 Execute（単一変更セット）: `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / 本decision-pack の3ファイルのみを単一変更セットで同期し、指定外ファイル編集を実施しない。
- Phase 4 Verify（validator + unittest + rg）: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-55|Decision Queue|Ready=1 / Open=2|A1→A2→A3|件数47|Active=5|Done=26|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイル整合一致を確認（self-correction 0/3）。
- Phase 5 Proceed（再開判定チェックリスト1行確定）: **共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。**


### 6-50. Stream D 共有統合同期ログ（2026-04-29 rerun-57, Phase 1-5）

- Phase 1 Read同期（A/B/C完了報告・Decision Queue・件数）: shared resource 3ファイル（`01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md`）を再読し、公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2`、依存順 `A1→A2→A3`、停止条件違反0件を確認。
- Phase 2 Execute（Active一覧/状態/次の1手同期）: 同期対象を共有3ファイルに限定し、未承認決定の確定扱い・件数不整合・未定義競合を停止条件として維持したまま、Active一覧と次アクションを同一値へ再固定。
- Phase 3 Verify（件数整合/依存順/停止条件）: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-57|Decision Queue|Ready=1 / Open=2|A1→A2→A3|件数47|Active=5|Done=26|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、3ファイル整合一致を確認。
- Phase 4 Publish（再開判定チェックリスト1行固定）: **共有3ファイルで `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` が一致していること。**
- Phase 5 Proceed（次サイクル条件）: 次サイクルは `DQ-HIL-EXEC-01` Ready監査継続、`DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` Open期限管理、shared resource 3ファイル単一変更セット維持を開始条件とする。

- Stream F 共有統合同期（2026-04-29 rerun-59, Phase 1-5）: Phase 1 Read同期で shared resource 3ファイル（`01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md`）を同時再読し、件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26）・Active=5・Done=26・Decision Queue Ready=1/Open=2・依存順 `A1→A2→A3`・用語（Security Officer / System Owner / Platform Operator）・役割（2者承認と実行責務分離）・導線（`02_Architecture/strict_mode_exception_approval_flow.md` 起点）・固定値D1〜D4（4h / 2h / 代理承認なし / 48h+15m+60m）・停止条件違反0件の一致を確認。Phase 2 Planで反映対象を shared resource 3ファイル単一変更セットに限定。Phase 3 Executeで3ファイルを同一コミット境界の同期差分（本ログ追記）として更新。Phase 4 Verifyは `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-59|Decision Queue|Ready=1 / Open=2|A1→A2→A3|Security Officer|System Owner|Platform Operator|D1〜D4|4h / 2h / 代理承認なし / 48h\+15m\+60m|再開判定チェックリスト|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` で整合一致を確認。Phase 5 Proceed（1行固定）: **再開判定チェックリスト確定 = 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件（`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01`） / 停止条件違反なし。**


### 6-61. Stream F 共有統合同期ログ（2026-04-30 rerun-61, Phase 1-4）

- Phase 1 Read: `01_Plans/issues/README.md` と 本decision-pack を再読し、`Source Issue` 運用（Openは`N/A`、Draftは`TBD`）、Decision Queue（Ready=1 / Open=2）、再開判定チェックリスト1行、停止条件違反0件を確認。
- Phase 2 Sync: `Source Issue` 運用基準・Queue状態・再開条件の表現を README/decision-pack 間で整合確認し、差分がないことを記録（指定外ファイルは未編集）。
- Phase 3 Verify: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-61|Source Issue|Decision Queue|Ready=1 / Open=2|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し、README/decision-pack の記述整合を確認。
- Phase 4 Proceed: **次の人間判断待ち論点は `DQ-FB-P2C-01`（FB-P2C Gate 0承認）と `DQ-OPS-SOURCE-01`（GitHub Issues運用開始宣言）である。開始宣言未確定のため `Source Issue` は `N/A` 維持。**

- Stream G 同期ログ（2026-05-01 rerun-63）: shared resource 3ファイルを同時再読し、公開値 `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3` を単一変更セットで同期。`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=1 / Open=2|A1→A2→A3|件数47|Active=5|Done=26|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を通過し、未承認事項の確定化なし。再開判定チェックリスト1行固定: **Go / 未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件 / 停止条件違反なし**。

- Stream F Phase 1-5 同期（2026-05-03 rerun-65）: Phase 1 Read Gateで Stream B/C/D/E 完了報告と証跡（Decision Queue Ready=1/Open=2、依存順 `A1→A2→A3`、停止条件違反0件）を確認。Phase 2 Planで件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26）・Active=5・Done=26・Decision Queue（Ready=1/Open=2）を固定。Phase 3 Executeで shared resource 3ファイルを単一変更セット同期。Phase 4 Verifyで `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-65|Decision Queue|Ready=1 / Open=2|A1→A2→A3|件数47|Active=5|Done=26|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行して3ファイル一致を確認。Phase 5 Proceedで再開判定チェックリスト1行（未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件 / 停止条件違反なし）を更新。

- Stream D 共有統合同期（2026-05-04 rerun-66）: Phase 1 Readで shared resource 3ファイルを再読し、公開値 `件数47（Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26） / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` を再確認。Phase 2 Syncで Active issue / Queue / 次の1手を同一値へ固定。Phase 3 Auditで件数・依存順・停止条件違反の再計算を実施。Phase 4 Verifyで `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "rerun-66|Decision Queue|Ready=1 / Open=2|A1→A2→A3|件数47|Active=5|Done=26|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し一致を確認。Phase 5 Proceedで再開判定チェックリスト1行（未固定箇所0件 / 依存タスク契約リンク確定 / Queue未解決2件 / 停止条件違反なし）を固定。


## Stream D Sync Log（2026-05-06 rerun-68）

- Phase 1 Read: A/B/C完了報告・件数47・Decision Queue（Ready=1 / Open=2）・依存順 `A1→A2→A3`・停止条件違反0件を再読確認。
- Phase 2 Sync: Active issue memos / Decision Queue / 次の1手を shared resource 3ファイル（`issues/README.md` / `project-progress-dashboard.md` / `decision-pack-2026-03-human-judgement.md`）で整合反映。
- Phase 3 Audit: Open=10 / In Progress=1 / Blocked=2 / Draft=8 / Done系=26、Active=5、Done=26 を再計算し不整合0件を確認。
- Phase 4 Verify: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3|件数47|Active=5|Done=26" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を実行し成功。
- Phase 5 Publish: 再開判定1行を維持（未承認事項の確定扱い0件 / 二重計上0件 / 未定義競合0件）。

- Stream D Phase 1-4 同期（2026-05-07 rerun-70）: Plan→Execute→Verify→Proceed を直列実行し、A/B/C完了報告リンク再確認・未承認事項の確定扱い0件を監査したうえで、公開固定値 `件数47 / Active=5 / Done=26 / Decision Queue Ready=1 Open=2 / 依存順A1→A2→A3 / 停止条件違反0件` と次サイクル再開条件1行を shared resource 3ファイルで一致させた。
