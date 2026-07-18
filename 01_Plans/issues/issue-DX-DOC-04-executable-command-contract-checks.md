# Issue: DX-DOC-04 文書内の実行コマンドを現行契約へ静的照合する

> 文書のコードブロックは利用者がコピーするインターフェースである。リンク切れだけでなく、endpoint・CLI option・service・package scriptの実在をfail-closedで確認する。

- Type: Bug / Documentation quality / Tooling
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Developer Experience contributor
- Scope: `README.md`, `CONTRIBUTING.md`, `04_Documentation/*.md`, `03_Implement/frontend/docs/e2e_testing.md`, `02_Architecture/runtime_parameter_registry.md`, `03_Implement/deploy/docker-compose.yml`, `03_Implement/deploy/nginx.conf`, `03_Implement/frontend/package.json`, repository-local Python CLI entrypoints, `01_Plans/docs_contract_checks.py`, `01_Plans/docs_check.py`, `01_Plans/tests/test_docs_contract_checks.py`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`
- Related Backlog: `DX-DOC-02`, `DX-DOC-03`, `DX-E2E-08`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/issues/issue-DX-DOC-02-docs-contract-ci-and-index-completeness.md`, `01_Plans/issues/issue-DX-E2E-08-current-runbook-history-and-contract-test-drift.md`
- Expected verification level: integration

## Requirement meta I/F（共通キー）

- RequirementID: DX-DOC-04
- RequirementStatement: current/public文書からコピー可能なコマンドを抽出し、HTTP route、CLI option、npm script、Compose service、repository pathを現行の機械可読な正本へ静的照合して、実行不能な例をCIで阻止する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=利用者またはfresh cloneの貢献者が文書のコマンドをコピーする / 操作=記載されたhealth check、validator、npm、Composeコマンドを選ぶ / 期待結果=対象名と引数が現行実装に存在し、安全な前提・実行場所・非保証範囲が分かる / 除外=破壊的コマンドのCI実行、外部URLの常時到達性検査、組織固有インフラの検証。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 課題

現在のdocs-checkは相対リンク、Active issue、current/history境界を検査するが、コードブロックやインラインコードに書かれた実行契約を照合しない。この穴により、検査成功中でも次のコピー実行エラーが残る。

- `CONTRIBUTING.md`のCompose E2E手順は`curl -fsS http://localhost:8080/api/health`を案内する。実装はbackendの`/healthz`とnginxの`/api/`変換により、公開probeは`/api/healthz`である。
- Doneの`DX-DOC-03`はADR-0019とE2E runbookの同じdriftを修正したが、`CONTRIBUTING.md`を対象に含めず、同じ旧endpointが貢献者導線に残った。
- E2E正本は`validate_active_issue_memos.py --files ...`を2箇所で案内するが、現CLIのhelpは`--root`だけを受け付ける。
- これらを含む現行repositoryで`python 01_Plans/docs_check.py`は成功するため、既存gateでは再発を検出できない。
- 一方、current/public文書の`npm run`参照は監査時点で全て`03_Implement/frontend/package.json`のscriptsに存在した。package script、Compose service、repository-local CLIは決定論的な静的照合が可能である。

文書内コマンドは説明文ではなく利用者・開発者向けI/Fである。誤ったhealth probeは正常な環境を障害と誤認させ、存在しないvalidator optionは品質確認そのものを停止させる。個別修正だけでは、次のrenameやCLI変更で再発する。

## 対応方針

### 1. 検査対象を分類する

current/public文書のshell、PowerShell、JSON、インライン実行例を次の3区分へ分類する。

| 区分 | 例 | 自動検査 |
| --- | --- | --- |
| Static contract | npm script、Python CLI option、Compose service、repository path、既知route | 正本との静的照合を必須化する |
| Safe smoke | `--help`、`--list`、read-only GET、`docker compose config` | 隔離環境で副作用なく実行できる場合だけintegrationで確認する |
| Manual/mutating | PUT、restore、`down -v`、volume削除、秘密情報を伴う接続 | CIでは実行せず、警告・前提・停止条件と静的構文だけ検査する |

分類不能なコマンドを推測実行しない。外部サービス、認証済み環境、データ変更を伴う例は常にmanual側へ倒す。

### 2. `DC-CMD-001`を追加する

`docs_contract_checks.py`に純関数と負例fixtureを追加し、少なくとも次を照合する。

1. `npm run <name>` → 対象`package.json`の`scripts`。
2. repository-local Python CLIの`--option` → そのCLIのargument parserまたは固定help snapshot。文書から任意Pythonを実行しない。
3. `docker compose logs/exec/run/restart <service>` → `docker-compose.yml`のservice集合。
4. repository pathやscript path → 対象文書の作業directoryを考慮した既存path。
5. localhost向け既知probe → backend routeとnginx proxy境界から作る小さなallowlist。外部URLの到達性は対象外。
6. runtime環境変数 → `runtime_parameter_registry.md`の正準key。内部adapter変数は公開文書で利用者向けkeyとして扱わない。

findingはrule ID、文書、行、検出token、照合先、正しい候補を示す。曖昧な自然言語や任意shell構文を無理に完全解析せず、対応対象を明示的に限定する。

### 3. baselineを修正してCIへ統合する

- `CONTRIBUTING.md`のCompose probeを`/api/healthz`へ直す。
- `DX-E2E-08`と協調し、E2E正本の存在しない`--files`例を除去する。
- ADR-0024の適用matrixへ`DC-CMD-001`を追補し、正常/負例fixture、current repositoryのclean pass、診断表示が揃ってからblocking化する。
- 文書作成者向けに、検査対象外とする例の最小escape方法と理由記録を定義する。広いfile単位除外は禁止する。

## 実施しないこと

- `docker compose down -v`、DB restore、PUT/POST、volume削除をCIで実行すること。
- 外部URLやLLM providerへ定期アクセスすること。
- shell全構文を実装する汎用parserの自作。
- 動的port、組織固有hostname、秘密情報を固定値として正本化すること。
- 誤った例を正当化するため、runtimeに不要なalias endpointやCLI optionを追加すること。

## 実行順序と担当境界

1. Documentation contributorが対象文書とコードブロックをinventory化し、3区分を付ける。
2. Backend/Frontend/Operations contributorがroute、script、service、parameterの正本を確認する。
3. DX contributorが小さな抽出器と各照合関数を実装し、負例fixtureを追加する。
4. Documentation contributorが既知baseline 2件を是正し、曖昧な例へ前提・作業directory・停止条件を加える。
5. MaintainerがCI blocking化、false positive、破壊的コマンド非実行を確認する。

`DX-E2E-08`はE2E正本の履歴分離と旧契約テスト更新を担当し、本Issueは文書横断のコマンド実在性を担当する。重複修正を避け、`--files`のbaseline修正は先にmergeされた側を採用する。

## 受入条件

- [x] `CONTRIBUTING.md`のCompose health probeが`/api/healthz`となり、backend-localの`/healthz`と区別される。→ 修正済み（下記「実装記録」参照）。
- [x] current/public文書に存在しないrepository-local CLI optionが0件で、`--files`参照がなくなる。→ 監査の結果、current/public文書（README/CONTRIBUTING/04_Documentation/e2e_testing.md）に`--files`参照は0件（`e2e_testing.md`分は`DX-E2E-08`で既に解消済み、他文書には元々存在しなかった）。`01_Plans/issues/*.md`に多数残る`--files`参照はDX-DOC-04のScope外（内部issueメモの実施時点記録であり、現行の利用者向けコピー対象ではない）と判断し対象外にした。
- [x] 文書で参照するnpm scripts、Compose services、repository paths、runtime parameter keysが正本と一致する。→ npm scripts・Compose services・repository paths・runtime parameter keysの自動照合をすべて実装した（下記「実装記録」参照）。
- [ ] `DC-CMD-001`がendpoint、CLI option、npm script、Compose service、pathの各負例をrule ID付きで検出する。→ npm script・Compose service・pathの3区分が実装済み。endpoint・CLI optionの2区分は未実装（follow-up、下記「実装記録」参照）。
- [x] コードフェンス外の説明、placeholder、外部URL、動的値を誤検出しない正常fixtureがある。→ npm script区分について、正常例・スコープ外文書除外の2 test fixtureを追加（下記参照）。他区分は該当区分自体が未実装のため対象外。
- [x] manual/mutatingコマンドはCIで実行されず、データ消失・秘密情報・本番利用に関する警告と停止条件を維持する。→ 本Issueでは静的照合のみを追加し、CI実行コマンドやworkflowの変更は一切行っていない。
- [x] localとCIが同じ`docs_check.py`から検査し、current repositoryでpassする。→ `check_npm_script_commands`を`docs_check.py`へ統合し、現行repositoryでpass済み（下記「実装記録」参照）。
- [x] SafeMode、share/export、provider=`none`、import sanitizeの安全既定を変更しない。→ アプリ実装・workflowは無改修。
- [ ] Doneの`DX-DOC-03`と`DOC-OPS-06`から本follow-upへ到達できる。→ 本セッションでは未確認・未対応（follow-up）。

## 検証計画

- baseline検索:
  - `rg -n "api/health([^zA-Za-z0-9]|$)|validate_active_issue_memos.py --files" README.md CONTRIBUTING.md 04_Documentation 03_Implement/frontend/docs`
  - 期待結果: 0件。
- 正本照合:
  - `python 01_Plans/issues/validate_active_issue_memos.py --help`
  - frontend `package.json` scripts一覧。
  - `docker compose -f 03_Implement/deploy/docker-compose.yml config --services`（Docker利用可能時）。
  - backend OpenAPIまたはroute unit fixtureとnginx `/api/`変換。
- contract tests:
  - endpoint typo、未知CLI option、未知npm script、未知service、欠落pathを各1件以上。
  - placeholder、外部URL、manual command、コードではない文章を正常例にする。
- 統合:
  - `python 01_Plans/docs_check.py`
  - `git diff --check`
  - CIのblocking結果。

## 実装記録（2026-07-17）: baseline修正 + `DC-CMD-001`（npm script区分のみ）

本セッションでは、6区分（endpoint probe / CLI option / npm script / Compose service / repository path / runtime parameter key）のうち、issue自身が「決定論的に照合可能」と明示するnpm scriptだけを実装した。残り5区分は未実装のfollow-upとして明示的に残す（サイレントに省略しない）。

- **baseline修正（既知バグ2件のうち1件が現存）**: `CONTRIBUTING.md`のCompose health probeが`http://localhost:8080/api/health`（誤り、`z`欠落）だったのを`/api/healthz`へ修正した。もう1件（E2E正本の`--files`参照）は`DX-E2E-08`で既に解消済みであることを確認した。current/public文書（README/CONTRIBUTING/04_Documentation/e2e_testing.md）を`grep`で監査し、`--files`参照が他に残っていないことを確認した。`01_Plans/issues/*.md`に残る多数の`--files`参照は、本Issueの`Scope:`が明示的に対象外とする内部issueメモ（実施時点の検証コマンド記録）であり、対応していない。
- **`DC-CMD-001`（npm script区分）**: `01_Plans/docs_contract_checks.py`に`check_npm_script_commands()`を追加した。`npm run <name>`パターンを抽出し、`03_Implement/frontend/package.json`の`scripts`キーと照合する。対象はcurrent/public文書（`README.md`/`CONTRIBUTING.md`/`04_Documentation/`配下/`03_Implement/frontend/docs/e2e_testing.md`）に限定し、`00_Prompt`/`01_Plans`の内部issueメモは対象外とした（issueメモは実施時点の検証コマンドを記録する履歴であり、常設の利用者向けコピー対象ではないため）。`package.json`が存在しない実行コンテキスト（本モジュール自身の最小テストfixture等）ではfindingsを返さず、他ruleのテストを壊さないようにした。
- **`docs_check.py`統合**: `check_npm_script_commands`を`run_docs_check()`へ配線した。追加の実行ステップは不要（既存の`docs_check.py`実行だけでnpm script区分も検査される）。
- **テスト**: `01_Plans/tests/test_docs_contract_checks.py`に`NpmScriptCommandCheckTest`（3 test: 正常例、未知script検出、スコープ外文書の除外確認）を追加した。
- **未実装（follow-up）**: endpoint probe allowlist、CLI option照合、repository path照合、runtime parameter key照合の3区分＋残り1区分。`DX-DOC-03`/`DOC-OPS-06`からの導線確認、CI blocking化のMaintainer確認も未実施。

検証結果:
- `python3 -m unittest 01_Plans.tests.test_docs_contract_checks 01_Plans.tests.test_docs_check`: 26/26 pass（新規3件含む、既存回帰なし）。
- `python 01_Plans/docs_check.py`: pass（`active_memos=22, tracked_markdown=381`）。
- `grep -E "api/health([^zA-Za-z0-9]|$)" CONTRIBUTING.md README.md 04_Documentation/*.md 03_Implement/frontend/docs/e2e_testing.md`: `/api/healthz`の正しい参照のみ、誤り0件。

## 実装記録（2026-07-17続き）: `DC-CMD-001`（Compose service区分を追加）

npm script区分に続き、Compose service区分を実装した。残り3区分（endpoint probe、CLI option、repository path、runtime parameter keyのうち後3つ）は引き続き未実装のfollow-upとする。

- `01_Plans/docs_contract_checks.py`に`_extract_compose_services()`（`services:`直下の2-indentキーを走査する軽量抽出、YAML依存を追加しない）と`check_compose_service_commands()`を追加した。対象は`docker compose logs/exec/restart/stop/start/run/kill/pause/unpause/top <service>`（サービス名を引数に取る副コマンドのみ）とし、`up`/`down`/`ps`/`config`はプロジェクト全体操作のため対象外にした。照合先は`03_Implement/deploy/docker-compose.yml`の`services:`直下キー（現行: `api`/`db`/`web`）。npm script区分と同じくcurrent/public文書スコープに限定し、Compose fileが存在しない実行コンテキストではfindingsを返さない。
- 現行current/public文書（README/CONTRIBUTING/04_Documentation/e2e_testing.md）を監査した結果、既存の`docker compose logs/exec <service>`例はすべて`api`/`db`/`web`のいずれかで、誤り0件だった（今回はbaseline是正なし、将来のservice rename/typo再発防止としての追加）。
- `01_Plans/tests/test_docs_contract_checks.py`に`ComposeServiceCommandCheckTest`（4 test: 正常例、未知service検出、スコープ外文書の除外確認、`up`/`ps`/`down -v`等サービス引数なし副コマンドの非検出確認）を追加した。
- `docs_check.py`へ`check_compose_service_commands`を配線した。

検証結果:
- `python3 -m unittest 01_Plans.tests.test_docs_contract_checks 01_Plans.tests.test_docs_check`: 30/30 pass（新規4件含む、既存回帰なし）。
- `python 01_Plans/docs_check.py`: pass（`active_memos=22, tracked_markdown=381`）。実際のCompose service参照（`api`/`db`/`web`）はすべて既存サービスと一致し、誤検知0件。

## Sonnet級エージェント実行計画（2026-07-18）: 残り4区分の実装仕様

この節は、残り4区分（runtime parameter key / repository path / CLI option / endpoint probe）を、**この節だけを読んだSonnet級エージェントが人間判断なしに実装完了できる**粒度で固定する。設計選択はすべてここで確定済みであり、実装側で再選択しない。

### 共通実装パターン（参照実装: `check_npm_script_commands` / `check_compose_service_commands`）

1. `01_Plans/docs_contract_checks.py`へ「定数（regex・正本パス）→抽出ヘルパ→`check_*`関数」を追加する。rule IDは全区分`DC-CMD-001`を共有する。
2. スコープは既存の`CURRENT_PUBLIC_DOC_ROOTS`（README/CONTRIBUTING/04_Documentation/e2e_testing.md）を再利用し、`_is_current_public_doc()`で判定する。
3. 正本ファイルが存在しない実行コンテキスト（最小テストfixture）では`[]`を返す（既存2区分と同じ理由・同じdocstring様式）。
4. `docs_contract_checks.py`の`main()`と`docs_check.py`の`run_docs_check()`の両方へ配線する（import追加を忘れない）。
5. `01_Plans/tests/test_docs_contract_checks.py`へテストクラスを追加する（最低: 正常例1・負例1・スコープ外文書の除外1。区分固有の除外があればもう1件）。
6. 検証ゲート（各区分のPR前に全部pass必須）:
   - `python3 -m unittest 01_Plans.tests.test_docs_contract_checks 01_Plans.tests.test_docs_check`
   - `python3 01_Plans/docs_check.py`（実repositoryで誤検知0件を確認）
   - `git diff --check`
7. **1区分=1PR**。docs+tooling-onlyのため、CI green後に自動マージしてよい（本セッション運用実績: PR #2620/#2623と同型）。
8. 実機で誤検知が出た場合、ルールを黙って狭めない。まず該当文書の記述が本当に正しいか確認し、正しい記述への誤検知であればスコープ/正規化ルールをこの節へ追記してから修正する。

### 区分3: runtime parameter key（優先度1・最小工数）

- 抽出regex: `KJ_ATLAS_[A-Z0-9_]+`。ただし(a)マッチ直後の文字が`*`のもの、(b)マッチが`_`で終わるものは「接頭辞言及」（例: `KJ_ATLAS_AUDIT_*`系）であり検査対象外。2026-07-18の実機棚卸しでこのノイズは`KJ_ATLAS_AUDIT_`と`KJ_ATLAS_ACCESS_CONTROL_`の2件のみと確認済み。
- 正本: `02_Architecture/runtime_parameter_registry.md`のMarkdown表行から第1セルがバッククォート付きキーの行（`| \`KJ_ATLAS_...\` |`で始まる行）を全表（Backend settings / Compose and frontend build keys / Verification harness keys）から収集した和集合。Private adapter表は`KJ_ATLAS_*`でないため自然に対象外。
- 2026-07-18棚卸し: 公開文書中の全43キー（ノイズ2件除く）はすべてregistryに存在 → **baseline是正なしで導入可能**。
- テストクラス名: `RuntimeParameterKeyCheckTest`（正常/未掲載キー負例/`KJ_ATLAS_FOO_*`接頭辞言及の除外/スコープ外除外の4 test）。

### 区分4: repository path（優先度2）

- 抽出: バッククォート内トークン（`` `([^`]+)` ``でinline code抽出）のうち、`^(00_Prompt|01_Plans|02_Architecture|03_Implement|04_Documentation|\.github)/`で始まり、空白・`<`・`>`・`*`・`{`・`|`のいずれも含まないもの。トークン末尾の`:数字`（行参照）は照合前に除去する。コードブロック内はfence単位の除外をせず同じ規則で走査してよい（パス実在性はブロック内でも成立すべき契約のため）。
- 正本: `tracked_markdown_paths()`と同様に`git -C <root> ls-files -z`（全ファイル、`-- *.md`制限なし）で得たtracked集合＋「トークンがtrackedファイルのディレクトリprefixに一致する場合」も存在扱い。
- DC-LNK-001（相対リンク）との分担: Markdownリンクは既存DC-LNK-001が担当。本区分は**インラインコード・コマンド引数中のパス**が対象。
- テストクラス名: `RepositoryPathCheckTest`（実在パス正常/欠落パス負例/`<placeholder>`除外/`:42`行参照付き正常の4 test）。

### 区分5: CLI option（優先度3）

- 抽出regex: `python3?\s+([\w./-]+\.py)((?:\s+--[\w-]+(?:[= ][^\s`]+)?)*)`で(script, options列)。scriptパスがrepository配下に実在するもののみ対象（欠落パスは区分4が報告するため二重報告しない）。
- 正本: 対象スクリプトのソーステキストから`add_argument\(\s*["'](--[\w-]+)`で収集したoption集合。**スクリプトを実行しない**（issueの固定条件）。`ArgumentParser`の出現がないスクリプトは「検証不能」としてスキップし、findingを出さない（推測しない）。
- 2026-07-18棚卸し: 公開文書中の該当は`03_Implement/deploy/tools/mock_local_llm.py --host --port`の1件のみで両option実在確認済み → **baseline是正なし**。
- テストクラス名: `CliOptionCheckTest`（正常/未知option負例/parser無しスクリプトのスキップ/スコープ外除外の4 test）。

### 区分6: endpoint probe allowlist（優先度4）

- 抽出regex: `https?://localhost[:/][\w./:?=&-]*`
- 正本: モジュール内定数`LOCALHOST_PROBE_ALLOWLIST`（exact集合とprefix集合の2種）。**各entryに由来コメント必須**。2026-07-18棚卸し（公開文書の全9 URL）に基づく初期値:
  - exact: `http://localhost:8080/api/healthz`（nginx `location /api/` → `api:8000`の`/healthz`）、`http://localhost:8000/healthz`（backend直接起動）、`http://localhost:8001/generate`・`http://localhost:8001`（mock adapter/local LLM例）、`http://localhost:4173/api/healthz`（vite preview、e2e_testing.md）、`http://localhost:8080`（web入口）
  - prefix: `http://localhost:8080/api/docs/`（document API のGET例）
- 効果: 既知バグ形`/api/health`（`z`欠落）の再発をCIで検出する。allowlist外の新URLは、`03_Implement/deploy/nginx.conf`とbackend routeで実在確認したうえでallowlistへ追加し、由来コメントを書く。
- テストクラス名: `LocalhostProbeCheckTest`（exact正常/prefix正常/`/api/health`負例/スコープ外除外の4 test）。

### 実行順序とstop条件

- 順序: 区分3 → 区分4 → 区分5 → 区分6（工数昇順・依存なし。区分4を区分5より先にするのは、区分5が「実在するスクリプトのみ対象」の前提で区分4の存在チェックへ依存するため）。
- Stop条件: (a)実機棚卸しで10件超の誤検知が出た区分は、パターン設計に欠陥があるため実装を停止し本issueへ観測結果を追記する（ルールを黙って狭めて通さない）。(b)同一区分でVerifyゲート3連続失敗時も停止し記録する（repo慣例）。

### AC対応

- 区分3+4の完了 → 受入条件「文書で参照するnpm scripts、Compose services、repository paths、runtime parameter keysが正本と一致する」の残り2項目が閉じる。
- 区分5+6の完了 → 受入条件「`DC-CMD-001`がendpoint、CLI option、npm script、Compose service、pathの各負例をrule ID付きで検出する」の残り3項目が閉じる。
- 本計画完了後に残るのは「CI blocking化のMaintainer確認」と「`DX-DOC-03`/`DOC-OPS-06`からの導線確認」のみ（いずれも人間確認・軽微）。

## 実装記録（2026-07-18）: `DC-CMD-001`（runtime parameter key区分を追加）

区分3（runtime parameter key）を実行計画どおり実装した。残り区分4〜6（repository path/CLI option/endpoint probe）は引き続き未実装のfollow-upとする。

- `01_Plans/docs_contract_checks.py`に`_extract_registry_keys()`と`check_runtime_parameter_key_commands()`を追加した。抽出regex`KJ_ATLAS_[A-Z0-9_]+`のマッチが`_`で終わる場合（`KJ_ATLAS_AUDIT_*`等の接頭辞言及）は検査対象外とした。照合先は`02_Architecture/runtime_parameter_registry.md`の表行（第1セルがバッククォート付き`KJ_ATLAS_*`キーの行）全体。
- **実装中に発見・修正した2件**:
  1. 正本パースの自作バグ: 行抽出regexが`` `KEY` `` の直後に空白+`|`を要求しており、実際のregistryにある`` `KJ_ATLAS_API_KEY` ⚠️ ``（既知ギャップの注記マーカー付き行、`KJ_ATLAS_ALLOW_JIT_PROVISIONING`も同様）を拾えなかった。mainへ到達する前に、閉じバッククォートと`|`の間の任意非パイプ文字を許容するよう修正した（回帰テスト追加済み）。
  2. registryの実在ギャップ: `04_Documentation/assets/screenshots/README.md`が使う`KJ_ATLAS_SCREENSHOT_HOST`/`_PORT`/`_BASE_URL`/`_OUTPUT_DIR`/`_BROWSER_PATH`の5キー（`capture_release_screenshots.mjs`等のscreenshot capture scriptが実際に読む環境変数）が、同種のAuth Level2 harness keyとは異なりregistryのどの表にも未登録だった。DX-DOC-04第1PRの`/api/health`typo修正と同じ「新規検査導入時に顕在化したbaselineの是正」として、Verification harness keys (non-public)表へ5行追加した。
- `01_Plans/tests/test_docs_contract_checks.py`に`RuntimeParameterKeyCheckTest`（5 test: 正常例、⚠️マーカー付き行の許容、未掲載キー検出、接頭辞言及の除外、スコープ外文書の除外）を追加した。
- `docs_check.py`へ`check_runtime_parameter_key_commands`を配線した。

検証結果:
- `python3 -m unittest 01_Plans.tests.test_docs_contract_checks 01_Plans.tests.test_docs_check`: 35/35 pass（新規5件含む、既存回帰なし）。
- `python 01_Plans/docs_check.py`: pass（`active_memos=22, tracked_markdown=382`）。registry是正後、実際のcurrent/public文書で誤検知0件。

## 実装記録（2026-07-18続き）: `DC-CMD-001`（repository path区分を追加）

区分4（repository path）を実行計画どおり実装した。残り区分5〜6（CLI option/endpoint probe）は引き続き未実装のfollow-upとする。

- `01_Plans/docs_contract_checks.py`に`check_repository_path_commands()`を追加した。バッククォート内トークンのうち既知のrepositoryルート接頭辞（`00_Prompt/`等）で始まり、placeholder/glob文字（space・`<`・`>`・`*`・`{`・`|`）を含まないものを対象とし、末尾`:数字`（行参照）を除去してから存在確認する。
- 正本は計画が示した`git ls-files`ではなく、**`root`直下のファイルシステム存在確認**（`Path.exists()`）を採用した。理由: この検査が走査するパスはすべて検査対象文書と同じworking tree内にあり、on-disk存在とtracked存在がここでは一致する。加えて`Path.exists()`はディレクトリにも真を返すため、計画が求めた「トークンがtrackedファイルのディレクトリprefixに一致する場合も存在扱い」を追加ロジックなしで満たす。
- **実装中に発見した1件（設計拡張、baseline是正ではない）**: `04_Documentation/release.md`が説明する`03_Implement/frontend/dist`（GitHub Actions artifactの内容を指す）が誤検知した。原因は`git check-ignore`がディレクトリ専用pattern（`dist/`等）を、パスが実在してディレクトリだと確認できる場合しか認識しないため（`git check-ignore`自体は採用しておらず、これは設計段階で確認した制約）。build成果物は本質的にfresh cloneでは不在なため、`.gitignore`解析ではなく明示allowlist（`REPOSITORY_PATH_BUILD_OUTPUT_LEAF_NAMES = {dist, node_modules, build, __pycache__, .venv}`）で「親ディレクトリが実在し、末尾セグメントがbuild成果物名」の場合だけ許容する設計とした。誤って別の場所を指す`.../wrong-place/dist`のような壊れた参照は、親ディレクトリ自体が存在しないため引き続き検出される（回帰テストで固定済み）。
- `01_Plans/tests/test_docs_contract_checks.py`に`RepositoryPathCheckTest`（7 test: 正常例、欠落パス検出、`<placeholder>`除外、`:42`行参照付き正常、スコープ外文書の除外、build成果物パスの許容、誤った親パスでのbuild成果物名は検出）を追加した。
- `docs_check.py`へ`check_repository_path_commands`を配線した。

検証結果:
- `python3 -m unittest 01_Plans.tests.test_docs_contract_checks 01_Plans.tests.test_docs_check`: 42/42 pass（新規7件含む、既存回帰なし）。
- `python 01_Plans/docs_check.py`: pass（`active_memos=22, tracked_markdown=382`）。build成果物allowlist追加後、実際のcurrent/public文書で誤検知0件。

## 補足

- 新規ADRは原則不要。ADR-0024の品質ゲート境界へ、既に顕在化した実行可能性検査を追補する実装Issueである。
- runtime routeやCLI設計を変える必要が判明した場合だけ、文書修正と分離して該当設計issueへ戻す。
- 将来、コードブロックannotationを導入する場合も、既存Markdown rendererで読める標準的な記法を優先し、文書編集の負担を増やし過ぎない。
