# Issue: DX-DOC-04 文書内の実行コマンドを現行契約へ静的照合する

> 文書のコードブロックは利用者がコピーするインターフェースである。リンク切れだけでなく、endpoint・CLI option・service・package scriptの実在をfail-closedで確認する。

- Type: Bug / Documentation quality / Tooling
- Status: Open
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

- [ ] `CONTRIBUTING.md`のCompose health probeが`/api/healthz`となり、backend-localの`/healthz`と区別される。
- [ ] current/public文書に存在しないrepository-local CLI optionが0件で、`--files`参照がなくなる。
- [ ] 文書で参照するnpm scripts、Compose services、repository paths、runtime parameter keysが正本と一致する。
- [ ] `DC-CMD-001`がendpoint、CLI option、npm script、Compose service、pathの各負例をrule ID付きで検出する。
- [ ] コードフェンス外の説明、placeholder、外部URL、動的値を誤検出しない正常fixtureがある。
- [ ] manual/mutatingコマンドはCIで実行されず、データ消失・秘密情報・本番利用に関する警告と停止条件を維持する。
- [ ] localとCIが同じ`docs_check.py`から検査し、current repositoryでpassする。
- [ ] SafeMode、share/export、provider=`none`、import sanitizeの安全既定を変更しない。
- [ ] Doneの`DX-DOC-03`と`DOC-OPS-06`から本follow-upへ到達できる。

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

## 補足

- 新規ADRは原則不要。ADR-0024の品質ゲート境界へ、既に顕在化した実行可能性検査を追補する実装Issueである。
- runtime routeやCLI設計を変える必要が判明した場合だけ、文書修正と分離して該当設計issueへ戻す。
- 将来、コードブロックannotationを導入する場合も、既存Markdown rendererで読める標準的な記法を優先し、文書編集の負担を増やし過ぎない。
