# Issue: DX-E2E-08 E2E現行runbookから形成履歴と旧契約テストを分離する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、E2Eの再現に必要な現行手順だけを正本へ残す。

- Type: Bug / Documentation / Test
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / QA contributor / Developer Experience contributor
- Scope: `03_Implement/frontend/docs/e2e_testing.md`, `03_Implement/backend/tests/test_qa_e2e_doc_contract.py`, `01_Plans/docs_contract_checks.py`, `01_Plans/tests/test_docs_contract_checks.py`, `01_Plans/issues/issue-DOC-OPS-06-current-view-history-and-contributor-route.md`, `01_Plans/issues/issue-DX-DOC-02-docs-contract-ci-and-index-completeness.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `01_Plans/issues/issue-DOC-OPS-06-current-view-history-and-contributor-route.md`, `03_Implement/frontend/docs/e2e_testing.md`
- Expected verification level: integration

## Requirement meta I/F（共通キー）

- RequirementID: DX-E2E-08
- RequirementStatement: E2E実務手順の単一正本を、現行コマンド、適用境界、失敗時証跡、安全確認だけで再現できるrunbookへ戻し、過去Stream計画・旧issue昇格テンプレート・廃止済みCLIを正本として固定するテストを除去する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=fresh cloneの開発者がE2Eを実行する / 操作=正本を上から読み、対象レーンを選んで記載コマンドを実行する / 期待結果=現行CLIだけで準備・実行・失敗記録まで到達し、過去のStreamやDraft昇格手順を現行必須条件と誤認しない / 除外=過去issue memoの履歴削除、E2Eシナリオ自体の機能追加。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 課題

`DOC-OPS-06`はE2E実務手順を`03_Implement/frontend/docs/e2e_testing.md`へ単一化し、過去の反復ログに遮られないcurrent-only導線をDone条件とした。しかしlatest mainの正本は、現行runbookの後ろに過去の計画・運用テンプレートを連結したままである。

- §「関連文書」で一度runbookが終わった後、§「UI Operability（計画）」、§「Draft群 Open化向け QA Gate」、§「Stream E/F/G」が続く。読者はどこまでが現在必須か判定できない。
- `Stream E/F/G`、固定直列実装順、Draft昇格、自己修復回数は2026-05の形成・進行情報であり、現在のE2Eコマンドや製品契約ではない。
- 295行目と363行目の`validate_active_issue_memos.py --files ...`は実行不能である。現validatorが受け付ける選択肢は`--root`だけで、正本の検証例がfresh cloneで失敗する。
- QA issue lifecycle、Open化条件、release gateの詳細は各issue memoと課題運用文書が正本であり、E2E runbookへの複製は状態ドリフトを起こす。
- `03_Implement/backend/tests/test_qa_e2e_doc_contract.py`が、E2E手順の実行可能性ではなく`Plan → Execute → Verify → Proceed`、`自己修復は最大3回`、`4回目相当は Stop`という旧運用tokenを必須化している。このテストが履歴混在を回帰防止してしまっている。
- `DC-CUR-001`はcurrent-only文書を検査するが、E2Eの単一正本を対象に含めないため、`Stream`見出しやexecution planningの再混入を検出できない。

結果として、E2E失敗の切り分けより先に廃止済みガバナンスを追わせ、記載どおりに実行してもCLI errorになる。これは可読性だけでなく、検証証跡の再現性とリリース判断を損なう。

## 対応方針

実施すること:

1. 現行E2E正本の各節を「現行runbook」「別正本への導線」「Git履歴で十分な形成履歴」に分類する。
2. 準備、smoke、Playwright、回帰レーン、Compose/代替経路、認証Level 2、fixture境界、失敗時証跡、安全確認を現行runbookとして連続配置する。
3. UI Operabilityのうち現在も有効な操作観点は「確認観点」へ統合する。実装前DOM契約、固定直列順、Draft昇格テンプレート、Stream E/F/G記録はcurrentから除く。
4. QA issueの状態・release gateは、現行の`issues/README.md`、対象issue、`release.md`またはADR-0019へリンクし、値や進行テンプレートをE2E文書へ複製しない。
5. `--files`を使う2つの無効な例を削除する。対象memoだけを確認する正式CLIが必要ならvalidator側へ別途設計・実装し、存在しないオプションを先に文書化しない。
6. `test_qa_e2e_doc_contract.py`を、現行runbookの不変条件へ変更する。少なくとも正準npm script、Compose優先、代替経路のrisk記録、SafeMode/share-export、失敗時証跡、現行リンクを検証し、過去Stream/自己修復tokenを要求しない。
7. `DC-CUR-001`のcurrent-only対象へE2E正本を加え、コードブロック内の説明例を除外しつつ、履歴・実行計画見出しの再混入を負例fixtureで検出する。
8. Doneの`DOC-OPS-06`へ本follow-upを記録し、「SSOTが1件」と「SSOT本文がcurrent-only」を別の完了条件として今後判定する。

実施しないこと:

- Playwright spec、製品UI、API、SafeMode、share/exportポリシーの変更。
- 過去issue memoやGit履歴から当時のStream記録を削除すること。
- E2E文書を一般利用者向け`04_Documentation`へ戻すこと。
- 旧tokenを別表現へ置換しただけで、履歴内容をcurrentに残すこと。

## 実行順序と担当境界

1. Documentation contributorが節inventoryを作り、残す現行情報と参照先を確定する。
2. QA contributorがpackage script、validator CLI、Compose/認証/fixtureの実在を確認し、runbookを縮約する。
3. Backend/Test contributorが文書契約テストを現行不変条件へ差し替える。
4. Documentation quality contributorが`DC-CUR-001`対象と負例fixtureを追加する。
5. Maintainerがfresh-clone dry-runとSafeMode/share-export非回帰を確認する。

文書縮約と契約テスト更新は同じPRで行う。どちらか一方だけでは、テスト失敗または旧tokenの再導入が起こる。

## 受入条件

- [x] E2E正本は対象読者・目的・範囲外から、準備、実行、判定、失敗記録、関連文書まで中断なく読める。
- [x] current見出しに`Stream E/F/G`、過去日付付きupdate、固定実装順、Draft昇格テンプレートが残らない。
- [x] 正本内の全コマンドが現行package scriptまたはCLIのhelpと一致し、`--files`参照が0件になる。
- [x] Compose、SQLite/mock差分、認証Level 2、fixture-backed suiteの非保証範囲が失われない。
- [x] SafeMode、share/export、provider=`none`、秘密情報を証跡へ含めない境界が維持される。
- [x] `test_qa_e2e_doc_contract.py`は現行runbook不変条件を検査し、過去運用tokenを要求しない。
- [x] `DC-CUR-001`がE2E正本への履歴見出し再混入を検出し、現行repositoryではfinding 0となる。
- [x] `DOC-OPS-06`から本follow-upへ到達できる。
- [x] fresh clone想定で、文書記載の正準コマンドをコピーして対象レーンを起動できる。

### 実装証跡（2026-07-16）

- `e2e_testing.md`: 「関連文書」以降に連結されていた `UI Operability（計画）`（Mock-first I/F契約、直列実装順、フェイルセーフ）、`Draft群 Open化向け QA Gate テンプレート（Stream E）`、`Stream E/F/G` の3節すべてを削除した。有効な操作観点5件（開始/選択/表示/閉じる/復帰）は「確認観点」表へ統合し、`Draft QA issue の Open化条件`（旧・重複していた2箇所）は`issues/README.md`/`ADR-0019`への導線1段落に置換した。`fixture-backed visibility suiteの境界`は末尾に孤立していた英語版の詳細（シナリオ表・コマンド）を統合し、`関連文書`の直前へ配置し直した。`関連文書`の後には`Release Gate 連携`のみが続く形にし、以降current見出しに履歴・実行計画混入がないことを確認した。`--files`参照は0件（現行validatorは`--root`のみ受理、`--help`で確認済み）。
- `test_qa_e2e_doc_contract.py`: `test_e2e_doc_has_plan_execute_verify_proceed_flow_and_self_repair_limit`を`test_e2e_doc_has_current_runbook_invariants`へ置換した。正準npm script（`e2e`/`e2e:mock`/`test:regression-guards`）、Compose優先文言、Risk ID表、SafeMode、失敗時証跡見出し、`ADR-0019`リンクの存在を検査し、`Plan → Execute → Verify → Proceed`/`自己修復は最大3回`/`4回目相当は Stop`/`Stream E/F/G`/`--files`/`直列実装順`/`Draft群 Open化`が再混入しないことを検査する。他の2 test関数（`issue-QA-E2E-USE-01`・`issue-PRODUCT-QA-01`対象）は本issueの対象外であり変更していない。
- `01_Plans/docs_contract_checks.py`: `CURRENT_ONLY_PATHS`へ`03_Implement/frontend/docs/e2e_testing.md`を追加した。`01_Plans/tests/test_docs_contract_checks.py`に、defaultパスにE2E正本が含まれることの確認1件と、E2E正本へ再混入した`Stream`見出しを`check_current_history_headings`が既定パスだけで検出することを確認する負例1件を追加した。
- `01_Plans/issues/issue-DOC-OPS-06-current-view-history-and-contributor-route.md`: Follow-upセクションを追記し、2026-07-15の完了記録が対象にしていなかった`e2e_testing.md`本体の残存を本issueへ切り出したことを明記した（DoneのDOC-OPS-06自体は変更していない）。

検証結果:
- `python 01_Plans/tests/test_docs_contract_checks.py`相当（`01_Plans.tests.test_docs_contract_checks`、unittest経由。pytestは本環境で利用不可）: 16/16 pass（新規2件含む）。
- `test_qa_e2e_doc_contract.py`の3 test関数を直接呼び出して検証（同じくpytest不可のため代替。`unittest`のdiscoveryはplain function testを検出しないため個別importで実行）: 3/3 pass。
- `check_current_history_headings(Path('.'))` / `check_relative_links` を現行repositoryへ直接実行: 0 findings。
- `rg -n "^#{2,3} .*Stream [EFG]|^#{2,3} .*update|直列実装順|Draft群 Open化|--files" e2e_testing.md`: 0件。
- `python3 01_Plans/issues/validate_active_issue_memos.py --help`: `--root`のみ受理することを確認し、文書側から`--files`参照をすべて除去した。
- `npm run e2e:mock -- --list`相当（`npx playwright test <spec> --list`）: ブラウザを起動せずにテスト一覧を解決できることを確認した（`libnspr4`欠落環境でも`--list`は動作する）。
- frontend `npm run typecheck`・`npx vitest run`は本PRでは非対象ファイル（`e2e_testing.md`はドキュメント、テストコードは変更なし）のため未実行。

**未完了・人手待ち**: 「実行順序と担当境界」段階5「Maintainerがfresh-clone dry-runとSafeMode/share-export非回帰を確認する」は人手のMaintainer確認であり、本セッションでは完了させていない。全AC達成の確認までは行ったが、Statusは`Open`のまま維持する。

### fresh-clone dry-run 実施記録（2026-07-17）

段階5の機械的な部分（実際にfresh cloneしてrunbook記載コマンドを再現できるか）を代行した。Docker Desktopは本実行環境で未使用のため、CONTRIBUTING.mdが認めるSQLite代替経路相当（frontend/backendのローカルテスト実行）で検証した。

- `git clone https://github.com/hat47x/kj-atlas`（`75d8fb76`時点）を新規ディレクトリへ実施。
- `cd 03_Implement/frontend && npm ci`: 74 packages、クリーンインストール成功（`npm audit`は6件の非関連devVulnerability検出のみ、本issueのscope外）。
- `npm run typecheck`: 0 errors。
- `npm run test`: 192 test files / 1,066 tests、全pass。
- `npm run test:regression-guards`: 10 test files / 135 tests、全pass（`review_pack_workflow.integration.test.ts`・`bundle_export.test.ts`等、share/export関連テストを含みSafeMode/share-export非回帰を確認）。
- `npx playwright test --list`: ブラウザを起動せず176 tests / 57 filesを解決（`libnspr4`欠落環境でも一覧解決は可能）。
- `cd 03_Implement/backend`: `pytest`は本環境で未導入のため、`test_qa_e2e_doc_contract.py`の3 test関数を直接importして実行（既存の代替検証手法と同一）: 3/3 pass。
- `python 01_Plans/docs_check.py`: pass（`active_memos=23, tracked_markdown=381`）。
- `rg`相当（`grep -c`）で`Stream [EFG]|直列実装順|Draft群 Open化|--files`の再混入を確認: 0件。

**残る人手判断**: 上記はすべて機械的な再現性確認であり、Maintainer自身による最終確認（dry-run結果の妥当性判断とDone昇格の可否）は含まない。Statusは引き続き`Open`のまま維持し、Maintainerの確認後にDoneへ移行する。

## 検証計画

- `rg -n "^#{2,3} .*Stream [EFG]|^#{2,3} .*update|直列実装順|Draft群 Open化|--files" 03_Implement/frontend/docs/e2e_testing.md`
  - 期待結果: 0件。
- `python 01_Plans/issues/validate_active_issue_memos.py --help`
  - 期待結果: 文書で使用するvalidator引数と一致する。
- `npm run typecheck`、`npm run test:regression-guards`、`npm run e2e:mock -- --list`
  - 期待結果: 文書に記載した正準レーンが解決される。実ブラウザ実行を省略する場合は理由と再開条件を残す。
- `python -m pytest 03_Implement/backend/tests/test_qa_e2e_doc_contract.py`
  - 期待結果: 現行runbook不変条件でpassする。
- `python 01_Plans/docs_check.py`
  - 期待結果: E2E正本を含む`DC-CUR-001`と全既存ruleがpassする。
- fresh-clone dry-run:
  - README → CONTRIBUTING → E2E正本 → 対象コマンド → 失敗時証跡templateを辿り、旧issue lifecycleを読まずに実行判断できる。

## 補足

- 新規ADRは不要。ADR-0019/0039とDoneのDOC-OPS-06を実際の正本へ反映するfollow-upである。
- Git履歴だけでは失われる一次証拠が見つかった場合のみ、対象期間・保持理由・現行正本への逆リンク付きInformative archiveを検討する。通常のStream進捗はGit履歴へ委譲する。
- `test_qa_e2e_doc_contract.py`を単に削除せず、現在の失敗モードを防ぐ小さな契約テストへ置き換える。
