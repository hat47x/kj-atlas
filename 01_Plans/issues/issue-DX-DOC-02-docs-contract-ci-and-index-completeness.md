# Issue: DX-DOC-02 docs-contract CIとActive issue完全性のfail-closed化

- Type: Process / Documentation quality
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Developer Experience contributor
- Scope: `01_Plans/issues/validate_active_issue_memos.py`, `01_Plans/issues/tests/`, `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/`, `01_Plans/docs_contract_checks.py`, `01_Plans/docs_check.py`（新規候補）, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `.github/workflows/ci.yml`, `.github/pull_request_template.md`, current-only文書と公開対象文書の検査規則
- Related Backlog: `DOC-ARCH-02`, `DOC-OPS-06`, `DOC-UI-CATALOG-01`, `DATA-CONTRACT-DOC-01`, `DX-E2E-08`
- Related ADR/Spec: `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`, `01_Plans/issues/issue-DOC-ARCH-02-current-contract-history-physical-separation.md`, `01_Plans/issues/issue-DOC-OPS-06-current-view-history-and-contributor-route.md`, `01_Plans/issues/issue-DOC-UI-CATALOG-01-public-boundary-and-provenance.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DX-DOC-02
- RequirementStatement: ADR-0024がmerge blockingとしたdocs-checkを単一コマンドとCI jobとして実装し、Active issue集合、現行契約SSOT、current/history境界、公開境界、相対リンクの欠落をfail-closedで検出する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=文書またはissue memoを変更するPR / 操作=ローカルとCIで同じdocs-checkを実行する / 期待結果=active file未掲載、stale index、異義契約、currentへの履歴再混入、公開不可情報、リンク切れが非0終了でmergeを止める / 除外=文章の主観的採点、全Markdownのstyle lint。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

文書品質ゲートは方針上存在するが、リポジトリ状態を完全に検証する実装がない。

- ADR-0024は `01_Plans` のDecision文書・issue meta・dashboardと公開04文書のdocs-checkをmerge/release blockingとする。
- `.github/workflows/ci.yml` はfrontend/backend jobだけで、docs jobがない。
- 統一docs-check entrypointと相対リンクcheckは存在しない。
- 2026-07-15より前の `validate_active_issue_memos.py` はREADMEのActive表に掲載された行だけを検証していたため、filesystem上のDraft/Open/In Progress memoを見落としていた。
- この見落としは、READMEの固定表を廃止し、memoメタデータからActive集合を直接発見する方式へ変更して解消した。現在のActive viewは `triage_actionable_plans.py` の出力とし、手動同期する第二の台帳を持たない。
- `02_Architecture` は最上位の契約正本なのにADR-0024のblocking対象外で、異義契約やcurrent/history混在を機械的に止められない。
- 完了済み公開境界も `ui_catalog.md` で回帰しており、手動検索だけでは再発を防げていない。

CIが緑でも、課題キュー、安全関連契約、公開境界を丸ごと見落とせるため、これは文体品質ではなくプロジェクト制御の完全性問題である。

## 2) 背景 / Context

- `ADR-0039` は validator/triage を軽量で有効なKEEP対象としている。
- `ADR-0047` は新しい設計ADRより確定済み判断の実行を優先する。
- `QA-MONKEY-08` と既存validatorは、表に載った行のmetadata整合だけを扱い、filesystem→indexの逆向き完全性を検証しない。
- `DOC-ARCH-02`, `DOC-OPS-06`, `DOC-UI-CATALOG-01` がclean baselineを作り、本Issueが再発防止を担当する。

## 2.1 依存関係 / Dependencies

- `issue-DOC-ARCH-02-current-contract-history-physical-separation.md`: current contract/historyの検査境界を確定する。
- `issue-DOC-OPS-06-current-view-history-and-contributor-route.md`: current-only文書とActive viewを整理する。
- `issue-DOC-UI-CATALOG-01-public-boundary-and-provenance.md`: 公開UI catalogの許可内容と鮮度メタを確定する。

Open化条件:

1. 上記3件の検査対象・許可例外・正本anchorが確定している。
2. ADR-0024の02層blocking追補を既存ADRのamendmentで扱えるか確認済みである。
3. clean baseline上で新checkの期待成功状態が再現できる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 課題と契約の漏れを検出できなければ、価値を守るActionへ到達できない。
- 安全（THREAT_MODEL / SafeMode）: SafeMode・share/export・proposal-onlyの正本参照欠落をblocking検出する。
- 企業・行政要件（enterprise_architecture）: CI結果とローカルコマンドを同値化し、変更証跡を再現可能にする。
- 後方互換（schemas）: validator追加でruntime契約は変えない。historyはcurrent比較から除外する。

## 4) 提案する解決策 / Proposed solution

### 4.1 Active issue完全性

- filesystem上の `issue-*.md` からStatusを読み、Draft/Open/In Progress集合を自動発見する。
- Active判定はtriageと同じ共有parserを使う。`Draft (...)` 等の非正規Statusがcleanup後も残る場合は曖昧に正規化せず、対象ファイルを示してfailする。
- READMEには固定のActive表を置かず、`triage_actionable_plans.py` の出力を唯一のcurrent viewとする。
- validatorはREADMEを介さずActive memoを発見し、必須メタデータ、Status正規値、参照先、依存関係を検証する。
- triageとvalidatorのStatus parser共有、および重複Backlog ID等の追加検査は、既存責務を壊さない小さな変更として別スライスで実施する。

### 4.2 単一docs-check entrypoint

`python 01_Plans/docs_check.py`（名称は実装時に固定）から次を決定論的に実行する。

1. Active issue完全性validatorとunit tests。
2. triage parserとunit tests。
3. Markdown相対リンクと参照先存在確認。
4. current-only文書へのrerun/Stream実行ログ再混入検査。
5. current architecture領域のContract ID/型異義定義、API/schema key差異、support level欠落検査。
6. history領域のInformativeメタとcurrentへの逆リンク検査。
7. 公開対象文書の内部管理語・未確定情報・provenance必須項目検査。
8. `git diff --check` 相当の体裁検査、またはCIで隣接stepとして固定。

### 4.3 CIとPR導線

- `.github/workflows/ci.yml` に軽量な `docs-contract` jobを追加する。
- ADR-0024既存Boundary-1をblockingにし、`02_Architecture` current契約を追加する場合は同ADRへ根拠・適用matrix・段階移行を追補する。
- ローカルとCIは同じentrypointを呼ぶ。
- PR templateに `command / result / not_executed_reason / resume_condition` を記録する欄を置く。

非目標:

- 主観的な文章品質、読みやすさ、語調の自動採点。
- 全履歴memoの内容を現在契約と照合すること。
- アプリruntime、SafeMode、schema値の変更。
- 全Markdownへの一括prose/style lint。
- docs-only PRへアプリE2Eを無条件に要求すること。

## 5) 受入条件 / Acceptance criteria

- [x] indexへの手動掲載がなくても、filesystem上のActive memoをvalidatorが自動発見する。
- [x] READMEの固定Active表を廃止し、空index・stale row・手動件数同期という失敗原因を除去する。
- [x] 必須メタデータ、非正規Status、参照先不在、依存関係不正、重複Backlog IDの異常系testがある。
- [x] current repositoryでtriageとvalidatorが同じActive件数を返す（2026-07-15 Open化時点: 29件）。
- [x] triageとvalidatorが同じStatus parser・正規値を使い、同じActive件数を返す。
- [x] 1コマンドでローカル/CI同値のdocs-checkを実行できる。
- [x] docs-check非0終了がPRをblockする。
- [x] 01/02/04/root docsの適用check matrixと除外理由が文書化され、02層が無検査にならない。
- [x] current領域の同一Contract ID/型の異義定義、API/schema key差異、DocumentV1支援表欠落を検出する（`DC-ARC-001`、`issue-DATA-CONTRACT-DOC-01`のclean baseline確立後に実装）。
- [x] history領域はcurrent契約比較から除外され、Informativeメタと逆リンクだけを検証する。
- [x] broken relative linkとSSOT参照先不在を検出する。
- [x] 公開版UI catalog等への内部管理語再混入とprovenance欠落を検出する。
- [x] SafeMode、共有/書き出し、proposal-only、human review、provider=`none`の不変条件参照欠落を検出する。
- [x] docs-only PRへ不要なfrontend/backend E2Eを強制しない。
- [x] CI jobとvalidatorの失敗理由が、対象ファイル・rule ID・修正先を示す（`DocsCheckFinding.render()`が全checkerで`{rule_id} {path}:{line}: {message} Fix: {fix_hint}`形式を共有する）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 check matrixとrule IDを固定し、ADR-0024へ適用境界と段階有効化条件を追補する。
- [x] T2 Active issue validatorをfilesystem直接検査へ変更し、共有parserとActive重複Backlog ID検査を追加する。
- [x] T3 相対リンク・current/history・architecture contract・public boundary・安全導線の各checkerを小さな純関数/fixtureで実装する（`DC-LNK-001`, `DC-CUR-001`, `DC-HIS-001`, `DC-ARC-001`, `DC-PUB-001`, `DC-SAF-001`）。
- [x] T4 単一docs-check entrypointを追加し、ローカル実行手順を記載する。
- [x] T5 既存Backend CI jobへblocking docs-check stepを追加し、既存PRで動作確認する。
- [x] T6 PR templateへ証跡欄を追加する（`.github/pull_request_template.md`の`command/result/not_executed_reason/resume_condition`欄で充足済み。commit `439867a9`）。
- [x] T7 負例fixtureでfail、現行repositoryでpass、変更対象外のアプリtest非干渉を検証する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py 01_Plans/tests/test_triage_actionable_plans.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `python 01_Plans/docs_check.py`（実装後の固定入口）
  - `git diff --check`
  - workflow YAML parseまたはGitHub Actionsの `docs-contract` job
- 必須負例:
  - active未掲載、空index、stale row、重複Backlog、status mismatch。
  - 重複Contract ID異義定義、API/schema key差異、support level欠落。
  - currentへのrerun見出し再混入、history逆リンク欠落。
  - 公開文書への内部issue/ADR進捗混入、provenance欠落、relative link切れ。
- 期待結果:
  - 正常fixtureと現行repositoryは0、各負例はrule ID付き非0、CIとローカル結果が一致する。
- 未実施時の理由・代替検証:
  - GitHub Actionsを実行できない場合はYAML parseと同一entrypointのローカル結果を記録し、CI実行結果が得られるまでDoneにしない。

## 8) 代替案 / Alternatives considered

- 手動レビューだけを継続する: 完了済み境界が既に回帰し、Active集合も見落としているため不採用。
- 既存validatorへ全機能を詰め込む: issue metadataとarchitecture/public checksの責務が混ざるため、単一entrypoint配下の小checkerへ分ける。
- 外部Markdown actionだけを導入する: プロジェクト固有のActive集合・SSOT・SafeMode境界を検証できないため補助に留める。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: false positiveで軽微な文書変更を止める、historyをcurrent扱いする、OS差でリンク検査が揺れる。
- 影響範囲: 全PRのCI、issue運用、architecture変更、公開文書更新。
- ロールバック手順: rule単位でwarn-onlyへ戻せる構造にし、job全体を外さず問題ruleだけ無効化する。SafeMode等の不変条件checkは安易に緩和しない。
- 段階導入: clean baseline作成→ローカル負例tests→CI観測→blockingの順。blocking昇格条件をADR-0024追補に残す。

## 10) Additional context

- 本件はADR-0024の実装欠落を埋めるActionである。新規ADRは原則不要。
- ADR化が必要になる条件: 02層をblocking対象へ加える判断が既存ADR追補で扱えない、または新しい非機能境界を導入する場合（ADR-0047 R-3）。

## DOC-ARCH-02 handoff（2026-07-15）

`DOC-ARCH-02`が作成したclean baselineを、T1/T3のarchitecture checkerへ次の境界で引き継ぐ。

- current対象: `architecture.md`、`api.md`、`schemas.md`、`data_model_operations_overview.md`。`history/`はInformativeとして別ルールで検査し、currentの重複定義件数へ混ぜない。
- current/history分離: current対象の見出しへ`Stream`、`freeze`、`rerun`、`execution log`、`checkpoint`、`reaffirmation`が再混入したらfailする。正当な現行用語を誤検出しないよう、見出し単位・allowlist最小で実装する。
- 責務別SSOT: CE1/CE2/CE4の型定義は`schemas.md`、endpoint/status/error/副作用は`api.md`、責務・信頼境界は`architecture.md`だけが定義する。参照リンクとContract ID索引は重複定義として数えない。
- history metadata: `Status: Informative history`、Source document/anchors、Covered period、Snapshot/source revision、Retention reason、Current normative anchorsの欠落または逆リンク切れをfailする。
- 既知Conflict: `queryId` / `schemaVersion`差異は`CE1-CONTRACT-01`へ委譲済みであり、同IssueがOpenの間は「解消済み」と推測して一方の値をcheckerへ固定しない。
- 受入fixture: currentへの履歴見出し再挿入、architectureへのrequired key再掲、history metadata欠落、現行anchor切れを各1件以上の負例にする。

引き渡し時baselineは、current 4文書の履歴見出し0、CE4型を含むCE主要型の定義先が`schemas.md`のみ、H-A〜H-D履歴ファイルの必須メタ充足、変更文書の相対リンク切れ0である。checker/CI実装とrule ID確定は本Issueのスコープに残す。

## DOC-OPS-06 handoff（2026-07-15）

fresh-cloneの貢献者導線とcurrent-only文書のclean baselineを、T3/T7のroute/public checkerへ次の境界で引き継ぐ。

- route: `README.md` → `CONTRIBUTING.md` → `triage_actionable_plans.py`の`Ready issues` → 対象memo / `issues/README.md` → `TEMPLATE.md` → branch規律 → validator / 対象test。このいずれかの相対linkまたはcommand参照が欠けたらfailする。
- Active view: 固定Active表を再導入せず、memo metadataから生成する。`CONTRIBUTING.md`等に「Active表を確認」のような手動台帳依存が再混入したらfailする。
- E2E SSOT: 実務手順は`03_Implement/frontend/docs/e2e_testing.md`だけが保持し、`04_Documentation/e2e_testing.md`は移転stubのままにする。旧04側へ独立command/profile/fixture規範が追加されたらfailする。
- current-only: `project-progress-dashboard.md`、`issues/README.md`、`documentation_quality.md`へStream/rerun/過去件数/解消済みQueueが現行指示として再混入したらfailする。
- safety route: `AGENTS.md`または参照先からSafeMode既定ON、share/export漏洩防止、proposal-only、`human_reviewed`人手限定、provider=`none`へ到達できることを検査する。値の複製一致ではなく、正本への有効な導線を確認する。

引き渡し時baselineは、上記routeをfresh-clone想定で追跡可能、current log drift 0、内部issue memo/GitHub Issues方針の矛盾0、E2E旧pathの独立規範0、route対象の相対link切れ0である。checker/CI実装は本Issueのスコープに残す。

## 進捗記録 2026-07-15: Active viewの単一化

- READMEの手書きActive表を廃止し、`triage_actionable_plans.py` の生成結果をcurrent viewとした。
- validatorは `issue-*.md` を直接走査し、StatusがDraft/Open/In Progressの34件を検証する。
- triageもActive 34件を返し、validator/triage unit test 12件が成功した。
- parser共有、重複Backlog ID検査、統一docs-checkとCI blockingは未完了のため、本IssueはDraftを維持する。

## baseline補正 2026-07-15: リポジトリ内コード参照

- 追跡対象Markdown 374件の相対リンク存在確認で、ADR-0050の3件と完了済みUX-NAV-01 memoの12件が、文書ディレクトリから解決できないリポジトリルート基準または`:line`付きの参照先になっていることを確認した。
- 参照対象コードや履歴説明は変更せず、文書位置から解決できる`../../03_Implement/...`形式へ補正した。行番号は当時の調査位置としてリンクラベルに残し、現在行への誤った固定anchorには変換していない。
- `llm_input_ir_spec.md`の正規表現例`/[?&](token|key|secret|password)=/i`はMarkdownリンクではない。T3のcheckerはコードスパン・コードブロックを除外し、この記法を誤検出しないfixtureを持つ。
- コード記法を除外した全374 Markdown・相対リンク352件の存在確認は欠落0件となり、T3のbroken-link checkerを導入できるclean baselineを回復した。

## Open化記録 2026-07-15

- 依存する`DOC-ARCH-02`、`DOC-OPS-06`、`DOC-UI-CATALOG-01`はすべてDoneで、検査対象、許可例外、正本導線のhandoffが揃った。
- `ADR-0024`は品質ゲート境界そのものを扱うAccepted ADRである。`02_Architecture`を適用matrixへ加える判断は新規ADRへ分岐せず、T1で同ADRへ根拠、段階導入、除外を追補する。
- current/history、公開境界、貢献者route、全Markdown相対リンクのclean baselineが再現できた。Open化条件3点を満たしたため、T1から着手可能なOpenへ移す。
- 最初の実装単位はT1のrule ID/check matrix固定とする。CI変更やblocking昇格を先行させず、ローカル負例fixtureで規則を確定してからT3〜T5へ進む。

## T1完了記録 2026-07-15

- `ADR-0024`へroot/01/02-current/02-history/04-publicの適用matrixと`DC-ACT-001`〜`DC-FMT-001`の9 ruleを追補した。
- 内部相対参照先の存在確認だけをBoundary-1へ昇格し、外部URL到達性、文体lint、ヒューリスティックな意味判定はBoundary-2に維持した。
- rule単位の決定論的実装、正常/負例fixture、clean pass、ローカル/CI同一entrypoint、診断表示が揃うまでblockingを有効化しない段階条件を固定した。
- 次の実装単位はT2のStatus parser共有と重複Backlog検査、または独立に進められるT3の`DC-LNK-001`純関数/fixtureである。

## T3進捗 2026-07-15: `DC-LNK-001`

- `docs_contract_checks.py`へ、コードフェンス/コードスパン、外部URL、ページ内anchorを除外し、相対参照先の欠落とrepository外への逸脱を検出する純関数を追加した。
- findingはrule ID、対象ファイル、行、参照先、修正先を保持し、CI診断へそのまま渡せる形式とした。
- 正常、欠落、コード記法除外、外部参照除外、percent-encoded path、repository逸脱の4 unit testsが成功した。
- 同じ実装を追跡Markdown 374件へ適用し、`DC-LNK-001` finding 0件を確認した。T3全体はcurrent/history、architecture、public checkerが未実装のため未完了を維持する。

## T4/T5完了記録 2026-07-15: 単一entrypointとblocking CI

- `docs_check.py` をローカル/CI共通の1コマンド入口とし、01_Plansのunit tests、Active issue validator、相対リンク検査をfail-fastで実行する。
- `docs_contract_checks.py` に追跡対象Markdownだけを列挙するCLIを追加した。生成物や依存物を対象外にし、検査関数だけを実行せず成功していた偽陽性を解消した。
- CIは既存Backend jobのPython setup直後に `python 01_Plans/docs_check.py` を実行する。文書専用jobの追加は避け、同じblocking効果を小さいworkflow差分で実現した。
- ローカル実行で01_Plans 9 tests、issue validator 11 tests、Active memo 23件、追跡Markdown 374件がすべて成功した。CIの最終確認は本変更のPRで行う。

## T2完了記録 2026-07-15: issue metadata parser共有

- `issue_memo_metadata.py` に正規Status、メタデータ、見出し上の論理Backlog IDの解釈を集約し、triageとvalidatorで共有した。
- 非正規StatusはActive一覧から黙って消さず、Doneを含む全memoを対象に停止理由を示す。論理Backlog IDの重複は現在の実行判断を曖昧にするActive memoだけをfail-closedにし、完了済み履歴の過去衝突は改名しない。
- 単一docs-checkで01_Plans 9 tests、issue validator 12 tests、Active memo 23件、追跡Markdown 374件の成功を確認した。

## T3進捗 2026-07-15: `DC-CUR-001`

- Document V1再基準化を含む別ブランチ統合後、`data_model_operations_overview.md` に履歴へ移管済みのStream D旧§1.2/1.3・§8〜13が再混入していた。ER、CRUD、支援レベル、運用境界を残し、形成履歴104行だけを除去した。
- current-only 7文書のMarkdown見出しを検査し、Stream、rerun、checkpoint、reaffirmation、execution log/recordなどの実行履歴見出しを `DC-CUR-001` で拒否する純関数を追加した。本文、コード記法、`downstream` のような部分一致は対象外とする。
- 単一docs-checkで01_Plans 11 tests、issue validator 12 tests、Active memo 23件、追跡Markdown 374件が成功した。T3全体はarchitecture、history、public checkerが残るため継続する。

## T3進捗 2026-07-15: `DC-HIS-001`

- `02_Architecture/history/` の形成履歴4件について、Informative status、元文書、元anchor、対象期間、source revision、保持理由、現行正本anchorの7項目を検査する。
- Current normative anchorsに現行文書へのリンクがあり、Source documentに指定された元文書から履歴ファイルへ逆リンクできることをfail-closedで確認する。履歴本文の意味や当時の判断はcurrent契約比較の対象にしない。
- 逆リンクが欠けていた `data_model_operations_overview.md` に形成履歴への導線を追加した。T3全体はarchitectureとpublic checkerが残るため継続する。
- 単一docs-checkで01_Plans 13 tests、issue validator 12 tests、Active memo 23件、追跡Markdown 374件が成功した。

## `DC-ARC-001` baseline blocker 2026-07-15

- ADR-0058とDoneの`DATA-CONTRACT-RESET-01`は単一の完全な`DocumentV1`へ同期済みとするが、current `schemas.md`には旧最小V1定義と完全な`DocumentV2` / version 2定義、Legacy V1→V2正規化、mock dv2等が29行残る。`api.md`と`data_model_operations_overview.md`のV1契約、および実装のversion 1 gateと矛盾する。
- `contract_reading_guide.md`/inventoryの旧V2案内と、成功系`card_quality_assistance.spec.ts`/`zip_import.test.ts`のversion 2 fixtureも同時に見つかった。型・optional field・安全注記を欠落なく再整合するP1 follow-up `DATA-CONTRACT-DOC-01`をOpenで起票した。
- `DC-ARC-001`は同issueのclean baseline後に、単一型定義、version/key一致、旧Legacy規範なし、DocumentV1支援表を決定論的fixtureで固定する。既知のbaseline failureを先にblocking化して無関係な文書変更を止めない。

## E2E current-only follow-up 2026-07-15

- 単一正本`03_Implement/frontend/docs/e2e_testing.md`の後半に、過去のStream E/F/G、固定実装順、Draft昇格テンプレートと、現CLIに存在しない`validate_active_issue_memos.py --files`が残る。backendの文書契約テストも旧運用tokenを必須化している。
- `DX-E2E-08`でrunbook縮約、無効コマンド是正、契約テストの現行不変条件化を一体実施する。clean baseline後、`DC-CUR-001`の対象へE2E正本を追加し、SSOT本文自体のcurrent/history混在を再発防止する。

## T3進捗 2026-07-16: `DC-ARC-001` clean baseline確立、`DC-CUR-001` E2E正本追加、T6/AC棚卸し

- `issue-DATA-CONTRACT-DOC-01`のclean baselineが確立された（`schemas.md`の単一`DocumentV1`/`version: 1`統合、`contract_reading_guide.md`/inventoryの旧V2案内是正、fixture修正）。これを受けて`DC-ARC-001`（`check_document_contract_baseline`）を実装し、単一Document型定義・`DocumentV1`/`version: 1`・`DocumentV2`/`Legacy`語の非再混入・`api.md`/`data_model_operations_overview.md`の`DocumentV1`参照を決定論的fixtureで固定した。正常系1件・負例4件を追加した。
- `issue-DX-E2E-08`のrunbook縮約完了を受けて、`DC-CUR-001`の`CURRENT_ONLY_PATHS`へ`03_Implement/frontend/docs/e2e_testing.md`を追加し、既定パスだけで再混入を検出することを確認する負例fixtureを追加した。
- T6（PR templateの証跡欄）は`.github/pull_request_template.md`に`command/result/not_executed_reason/resume_condition`が既に存在すること（commit `439867a9`）を確認し、チェック済みへ更新した。棚卸しの結果、対応する受入条件2件（architecture領域の異義定義検出、CI失敗理由の対象ファイル/rule ID/修正先表示）も充足済みへ更新した。
- T3は architecture / current-history / relative-link の3 checkerが完了し、public boundary checkerとSafeMode/share-export/proposal-only/human review不変条件参照checkerが未実装のため、T3自体は継続する。この2件は本follow-upのスコープ外とし、別途スコープ設計を要する。

## T3進捗 2026-07-16: `DC-PUB-001`

- 公開入口 `public_index.md` に残っていた文書管理上の分類説明を除去し、利用者が現在の画面構成と操作を確認できる `ui_catalog.md` への目的別導線を追加した。
- `DC-PUB-001` は、公開入口への内部管理語の再混入、公開UIカタログへの内部設計識別子の再混入、UIカタログの確認revision・確認日・表示条件・検証結果・公開状態、画像台帳の撮影provenance欠落を検出する。公開文書からGitHub上の設計正本を参照する用途は妨げない。
- 正常fixtureと、内部管理語・導線・provenanceを欠落させた負例fixtureを追加した。単一entrypointへ配線し、同時に呼び出しが欠けていた既存 `DC-ARC-001` も配線した。
- `python -m unittest 01_Plans.tests.test_docs_contract_checks 01_Plans.tests.test_docs_check`: 21件成功。`python 01_Plans/docs_check.py`: Active memo 24件、追跡Markdown 377件で成功した。
- T3は `DC-SAF-001` が残るため継続する。公開境界の定義自体はADR-0024から変更していないため、新規ADRは不要と判断した。

## T3完了記録 2026-07-16: `DC-SAF-001`

- 生成AI向け入口 `AGENTS.md` で、SafeMode既定ON、proposal-only、`human_reviewed`の人手限定、provider=`none`での主要価値、共有/書き出し時の未レビュー情報・秘密情報保護、import無害化の6不変条件を検査する。
- `AGENTS.md` から `THREAT_MODEL.md`、現行architecture、一般利用者向け入口へのrepository相対パスが存在することを検査する。全文一致や複数文書間の値複製は要求しない。
- 一般利用者向け入口から、データ取り扱い、セキュリティ、AI提案、設定ガイドへのMarkdown導線と対象ファイルの存在を検査し、リンク先に担当する安全境界が残っていることを確認する。
- 正常fixtureと、不変条件・正本パス・公開導線・リンク先境界を欠落させた負例fixtureを追加した。`python -m unittest 01_Plans.tests.test_docs_contract_checks 01_Plans.tests.test_docs_check`: 23件成功。`python 01_Plans/docs_check.py`: Active memo 24件、追跡Markdown 377件で成功した。
- ADR-0024の既定ruleを実装したもので、安全境界や正本責務を変更していないため新規ADRは不要と判断した。T3は完了し、残件はdocs-only PRのアプリE2E非強制化とT7統合確認である。

## docs-only CI範囲制御 2026-07-16: 実装済み・CI実証待ち

- `01_Plans/ci_change_scope.py` に変更パス分類を分離した。`03_Implement/frontend/` と `03_Implement/backend/` は独立判定し、CI workflow・分類器・分類器テストの変更時は両方を実行する。文書と内部issueだけの変更は両方をfalseとする。
- 既存のfrontend 6 jobとbackend jobは名称を維持し、`change-scope`出力によるjob-level条件を追加した。`docs-contract`は変更範囲によらず常時実行する。
- docs-only、frontendのみ、backendのみ、CI/分類器変更、Windows区切りの正常/負例4件を追加した。workflow自体を変更する本PRでは全アプリjobを実行し、次のdocs-only検証PRでskip結果とrequired checkへの非干渉を確認してから受入条件とT7を完了する。
- 既存のCI責務分離を変更せず実行範囲だけを狭めるため、新規ADRは不要と判断した。

## docs-only CI実証・完了記録 2026-07-16

- 実装PR #2612では、workflow変更を`frontend=true / backend=true`と判定し、既存の全アプリjobとdocs-contractが成功した。
- docs-only PR #2613の初回実行（GitHub Actions run `29497878661`）で、`Detect application change scope`と`Docs contract`が成功し、frontend 6 jobとbackend jobがすべて`skipped`となり、PR全体が成功した。
- 正常/負例fixture、現行repositoryのdocs-check、workflow変更時の全job実行、docs-only変更時の重いjob省略を確認したため、T7と全受入条件を完了した。
