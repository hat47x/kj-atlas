from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKS = ROOT / "01_Plans" / "docs_contract_checks.py"
CHECK_TESTS = ROOT / "01_Plans" / "tests" / "test_docs_contract_checks.py"
DOGFOOD = ROOT / "01_Plans" / "dogfood" / "cognitive-dogfood-continuous-2026-09-03-r10.md"
RELEASE_DOC = ROOT / "04_Documentation" / "release.md"
RELEASE_TEST = ROOT / "01_Plans" / "tests" / "test_release_artifact_contract.py"
ISSUE = ROOT / "01_Plans" / "issues" / "done" / "issue-DOC-CI-DRIFT-01-docs-check-optional-workflow-paths.md"

checks = CHECKS.read_text(encoding="utf-8")
old_check = '''def check_ci_job_timeouts(
    root: Path,
    workflow_paths: tuple[Path, ...] = CI_WORKFLOW_PATHS,
) -> list[DocsCheckFinding]:
    """Require every job in the maintained GitHub Actions workflows to have a bounded timeout."""
    findings: list[DocsCheckFinding] = []
    for relative_path in workflow_paths:
        source = root / relative_path
        lines = source.read_text(encoding="utf-8").splitlines()
'''
new_check = '''def check_ci_job_timeouts(
    root: Path,
    workflow_paths: tuple[Path, ...] = CI_WORKFLOW_PATHS,
) -> list[DocsCheckFinding]:
    """Require bounded timeouts in each maintained workflow that exists.

    A configured path identifies a workflow to inspect when present. It does
    not require GitHub Actions itself to be enabled, so an absent workflow has
    no jobs for this rule to inspect.
    """
    findings: list[DocsCheckFinding] = []
    for relative_path in workflow_paths:
        source = root / relative_path
        if not source.is_file():
            continue
        lines = source.read_text(encoding="utf-8").splitlines()
'''
if old_check not in checks:
    raise SystemExit("check_ci_job_timeouts anchor not found")
CHECKS.write_text(checks.replace(old_check, new_check, 1), encoding="utf-8")

check_tests = CHECK_TESTS.read_text(encoding="utf-8")
old_test = '''    def test_accepts_bounded_timeout_for_every_job(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflow = root / "workflow.yml"
            workflow.write_text(
                "jobs:\\n"
                "  first-job:\\n"
                "    timeout-minutes: 5\\n"
                "  second_job:\\n"
                "    timeout-minutes: 360\\n",
                encoding="utf-8",
            )

            findings = MODULE.check_ci_job_timeouts(root, (Path("workflow.yml"),))

        self.assertEqual(findings, [])


class HistoryMetadataTest(unittest.TestCase):
'''
new_test = '''    def test_accepts_bounded_timeout_for_every_job(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflow = root / "workflow.yml"
            workflow.write_text(
                "jobs:\\n"
                "  first-job:\\n"
                "    timeout-minutes: 5\\n"
                "  second_job:\\n"
                "    timeout-minutes: 360\\n",
                encoding="utf-8",
            )

            findings = MODULE.check_ci_job_timeouts(root, (Path("workflow.yml"),))

        self.assertEqual(findings, [])

    def test_ignores_configured_workflow_paths_that_do_not_exist(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            findings = MODULE.check_ci_job_timeouts(
                root,
                (Path(".github/workflows/ci.yml"), Path(".github/workflows/release.yml")),
            )

        self.assertEqual(findings, [])


class HistoryMetadataTest(unittest.TestCase):
'''
if old_test not in check_tests:
    raise SystemExit("CiJobTimeoutCheckTest anchor not found")
CHECK_TESTS.write_text(check_tests.replace(old_test, new_test, 1), encoding="utf-8")

dogfood = DOGFOOD.read_text(encoding="utf-8")
old_issue_path = "01_Plans/issues/issue-AI-IR-PROMPT-EVIDENCE-01-render-ir-evidence-in-provider-prompts.md"
new_issue_path = "01_Plans/issues/done/issue-AI-IR-PROMPT-EVIDENCE-01-render-ir-evidence-in-provider-prompts.md"
if old_issue_path not in dogfood:
    raise SystemExit("stale dogfood issue path not found")
DOGFOOD.write_text(dogfood.replace(old_issue_path, new_issue_path, 1), encoding="utf-8")

RELEASE_DOC.write_text('''# Release

対象読者: kj-atlas のリリース、検証版の共有、公開前確認を担当する人。

目的: 利用者が触れる状態へ変更を出す前に、品質、安全性、文書、受け入れ確認を人間が確かめ、タグと検証記録を対応付けるための最小手順をまとめます。

範囲外: 組織固有の承認システム、配布先ごとの秘密設定、マーケティング告知、container/package registry、自動deploy、署名基盤の新設。

公開区分: リリース/04文書保守者向け管理文書。一般利用者向け Gist の本文には原則含めず、公開前確認と安全境界レビューのチェックリストとして使います。

## 現在の前提: GitHub Actionsによる自動リリースは無効

現在、このリポジトリには常設のGitHub Actions release workflowを置いていません。タグをpushしても自動build、GitHub Actions artifact、GitHub Release、container/package registryへの公開は行われず、**自動生成される成果物はありません**。

したがって、この文書の現行手順は「対象commitを手動で検証する」「必要ならローカルでbuildする」「確認済みcommitにタグを付ける」「結果を記録する」までを扱います。継続的な公開配布を始める場合は、公開channel、artifact構成、保持期間、checksum/provenance/SBOM/署名、backend imageのregistry、撤回方法を別IssueまたはADRで決め、automationとこの文書を同じ変更で更新します。

## リリース前チェック

```bash
git status -sb
git diff --check
```

この文書でいうリリースは、正式版だけでなく、検証版や限定共有を含め、利用者が触れる状態へ変更を出すことです。

## 前提知識

リリース担当者は、すべての実装詳細を理解している必要はありません。ただし、次の違いは確認できるようにしておきます。

| 用語 | 意味 |
| --- | --- |
| build | 利用者が実行できる形にfrontendなどを組み立てること |
| test | 期待した動作を機械的に確認すること |
| smoke test | 主要操作だけを短時間で手動確認すること |
| rollback | 問題が出たときに前の状態へ戻すこと |

## リリース判断の流れ

常設CIは現在無効なので、次の確認はタグを打つ**前**に、タグ対象にする予定のcommit SHAへ自分で実行し、結果をリリース記録に残します。

1. 差分の範囲を確認する。
2. 影響するテストを実行する。
3. 手動smoke testで利用者の主要操作を確認する。
4. security、SafeMode、外部サービスとの共有の安全境界が後退していないことを確認する。
5. data handlingの観点でexport、share、ログ、外部サービスとの共有の扱いを確認する。
6. `01_Plans/issues/done/issue-PRODUCT-QA-01-release-readiness-quality-gates.md` のG0〜G7と価値ゲートに未解消のBlockerがないことを確認する。
7. rollback方針を確認する。

frontend:

```bash
cd 03_Implement/frontend
npm ci
npm run typecheck
npm run test
npm run build
```

backend:

```bash
cd 03_Implement/backend
python -m pytest
```

Docker Compose:

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
```

文書契約:

```bash
python 01_Plans/docs_check.py
python 01_Plans/dogfood/validate_dogfood_docs.py
```

## タグ作成手順

1. 上記「リリース判断の流れ」を対象commit SHAに対して実行し、必要な確認が成功することを確かめる。説明できない失敗がある場合はタグを作らない。
2. `CHANGELOG.md` の `[Unreleased]` を、タグと同じバージョン番号・当日日付の見出しへ切り出す。
3. タグ名はSemVer形式 `vX.Y.Z` とし、対象は手順1で確認済みのcommit SHAに限る。
4. 一度作成したタグは強制更新（force push / re-tag）しない。誤りがあった場合は新しいバージョン番号で再実行し、誤ったタグはwithdrawnとして記録する。
5. タグをpushする。現在はGitHub Actionsによる後続処理がないため、push成功だけでbuildや配布が完了したとは扱わない。
6. 下記「リリース記録に残す項目」を記録する。

## 成果物の扱い

現在は、タグpushを起点に自動生成・自動保存される成果物はありません。frontendのbuild結果やDocker imageを検証に使う場合も、その実行結果は検証を行った環境にだけ存在します。

第三者へ継続配布するartifactを定義するときは、少なくとも次を決めてから自動化します。

- 何を正式な配布物とするか。
- どこから取得できるか。
- 対象tagとcommit SHAをどう対応付けるか。
- 保持期間と撤回方法。
- checksum、provenance、SBOM、署名をどう扱うか。
- backend imageをregistryへ送るか。

## CHANGELOGとの対応

`CHANGELOG.md` は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) 形式・SemVer準拠です。`[Unreleased]` から版を切る条件は次のとおりです。

- タグを作成する直前に、`[Unreleased]` の内容を `## [X.Y.Z] - YYYY-MM-DD`（タグと同じバージョン番号、当日日付）へ書き換える。
- 新しい空の `[Unreleased]` セクションを見出しだけ残す。
- `[Unreleased]` のままtagをpushしない。版とタグは1:1で対応させる。

## リリース記録に残す項目

- tag（`vX.Y.Z`）
- 対象commit SHA
- 実行したtest / docs check / buildとその結果
- gate decision（`PRODUCT-QA-01` のGo/No-Go判断）
- 手動smoke testの結果
- 共有した成果物がある場合は、その生成方法と取得場所
- 既知の制限
- rollback / withdrawal方針

GitHub Actions workflowを将来再導入した場合は、workflow run、artifact名、取得場所、保持境界も記録対象へ戻します。

## 手動確認

- [ ] アプリが開く。
- [ ] 新規ドキュメントを作成できる。
- [ ] カードを追加・移動できる。
- [ ] 保存して再読み込みしても内容が残る。
- [ ] share/exportに秘密情報や内部作業ログが含まれない。
- [ ] SafeModeの既定動作が緩んでいない。
- [ ] LLM providerが意図した値になっている。
- [ ] 監査ログのHTTP連携や外部アクセス制御を有効にした場合、連携先と失敗時の動作が説明できる。

## 文書確認

- [ ] [installation.md](installation.md) の起動手順が現行実装と合っている。
- [ ] [configuration.md](configuration.md) の環境変数がsettings.pyと矛盾していない。
- [ ] [data_handling.md](data_handling.md) の保存・外部サービスとの共有・共有前確認が現行実装と矛盾していない。
- [ ] [security.md](security.md) の外部サービスとの共有の境界が維持されている。
- [ ] [acceptance_check.md](acceptance_check.md) の確認手順が再現できる。
- [ ] READMEや04文書に内部issue記録や秘密情報が混ざっていない。

## 失敗時の扱い

次のいずれかに当てはまる場合、リリースを止めます。

- build、test、typecheck、docs checkの失敗理由が説明できない。
- SafeMode、share/export、LLM providerの安全境界が後退している。
- 秘密情報、内部URL、生の顧客情報が文書やexportに混ざっている。
- 受け入れ確認の主要操作が再現できない。

止めること自体を異常扱いしません。利用者に影響する不確実性を見つけた状態なので、原因、回避策、再開条件を記録してから次の確認に進みます。誤って作成したタグは強制更新せず、withdrawnとして記録し、新しいバージョン番号で再実行します。

## 関連文書

- [acceptance_check.md](acceptance_check.md)
- [data_handling.md](data_handling.md)
- [operations.md](operations.md)
- [security.md](security.md)
- [installation.md](installation.md)

2026-03-03時点のE2E検証ログは形成履歴としてGit履歴から参照します。現在のリリース判断には、対象commit SHAに対して都度実行した確認結果を使います。
''', encoding="utf-8")

RELEASE_TEST.write_text('''import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release.yml"
RELEASE_DOC_PATH = REPO_ROOT / "04_Documentation" / "release.md"


class ReleaseArtifactContractTest(unittest.TestCase):
    """RELEASE-DOC-01: release.md must match the repository's automation state."""

    @classmethod
    def setUpClass(cls):
        cls.doc_text = RELEASE_DOC_PATH.read_text(encoding="utf-8")

    def test_tag_format_stays_documented(self):
        self.assertIn("vX.Y.Z", self.doc_text)

    def test_disabled_actions_state_is_explicit_when_workflow_is_absent(self):
        if WORKFLOW_PATH.is_file():
            self.skipTest("release workflow exists; enabled-workflow contract applies")

        self.assertIn("GitHub Actionsによる自動リリースは無効", self.doc_text)
        self.assertIn("自動生成される成果物はありません", self.doc_text)
        self.assertNotIn("frontend-dist-<tag>", self.doc_text)

    def test_workflow_artifact_contract_when_workflow_exists(self):
        if not WORKFLOW_PATH.is_file():
            self.skipTest("release workflow is intentionally absent")

        workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "v*.*.*",
            workflow_text,
            "release.yml's tag trigger pattern changed; update release.md's vX.Y.Z description to match.",
        )
        self.assertIn(
            "frontend-dist-${{ github.ref_name }}",
            workflow_text,
            "frontend artifact name changed; update release.md in the same change.",
        )
        self.assertIn("frontend-dist-<tag>", self.doc_text)
        self.assertIn("push: false", workflow_text)
        self.assertIn("kj-atlas-api:${{ github.ref_name }}", workflow_text)
        self.assertIn("kj-atlas-api:<tag>", self.doc_text)

        for marker in ("npm run test", "pytest", "playwright test"):
            self.assertNotIn(
                marker,
                workflow_text,
                f"release.yml now runs {marker!r}; update release.md's pre-tag verification contract.",
            )


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

ISSUE.write_text('''# Issue: DOC-CI-DRIFT-01 Actions無効化後のdocs/release契約を現行構成へ同期する

- Type: Test / Process / Documentation
- Status: Done
- Source Issue: COGNITIVE-DOGFOOD-01
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/docs_contract_checks.py`, `01_Plans/tests/test_docs_contract_checks.py`, `01_Plans/tests/test_release_artifact_contract.py`, `04_Documentation/release.md`, `01_Plans/dogfood/cognitive-dogfood-continuous-2026-09-03-r10.md`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `AGENTS.md`
- Expected verification level: docs-check

## 課題

AI入力IRの変更を検証するため現行リポジトリで `python 01_Plans/docs_check.py` を実行したところ、GitHub Actionsを無効化した後も文書契約が削除済みworkflowを必須としており、検査自体が完走できないことを確認した。

再現したずれは次の3系統だった。

1. `DC-CI-001` が、存在するworkflowのjob timeoutを検査するだけでなく、固定されたworkflowパスの存在まで暗黙に要求していた。
2. リリース文書とリリース契約テストが、削除済みrelease workflowによるartifact生成を現在も行うものとして扱っていた。
3. 継続dogfood R16が、Doneへ移動したIssueの旧パスを参照していた。

Git履歴では、workflow削除は `ci: disable GitHub Actions workflows` として意図的に行われている。したがってworkflowを復活させて検査へ合わせるのではなく、文書と検査を現行構成へ合わせる。

## 対応

- `check_ci_job_timeouts()` は、設定されたworkflowが実在する場合だけjobを検査する。存在するworkflowに対するtimeoutのfail-closed検査は維持する。
- release文書は、現在はGitHub Actionsによる自動リリースと自動artifact生成を行わないことを明記し、手動の事前検証・タグ・記録を現行手順として整理する。
- release契約テストは、workflow不在時には「自動化が無効であることを文書が明示する」契約を検査する。将来workflowが再導入された場合は、従来のtag/artifact境界を再び検査する。
- R16のIssue参照を現在のDoneパスへ修正する。

## 受入条件

- [x] 常設workflowが存在しない構成でも `DC-CI-001` が例外を送出しない。
- [x] 実在するworkflowのjobには従来どおり1〜360分の `timeout-minutes` を要求する。
- [x] release文書が存在しないworkflowや自動artifactを現在の機能として案内しない。
- [x] workflow不在時と将来の再導入時の双方をrelease契約テストで区別できる。
- [x] R16のIssue参照が現在のファイルへ解決する。
- [x] `python 01_Plans/docs_check.py` が最後まで成功する。
- [x] dogfood文書検査と計画メモ整合性検査が成功する。

## 検証

- `python -m unittest discover -s 01_Plans/tests -p test_docs_contract_checks.py`
- `python -m unittest discover -s 01_Plans/tests -p test_release_artifact_contract.py`
- `python 01_Plans/docs_check.py`
- `python 01_Plans/dogfood/validate_dogfood_docs.py`
- `python 01_Plans/triage_actionable_plans.py --check`
- `git diff --check`

## 非目標

- GitHub Actionsの常設workflowを再導入すること。
- 公開配布channelや署名基盤を、この修正だけで新設すること。
- 過去のリリースworkflowを現在も動作するものとして保存すること。

## 文書品質の仕上げ

原因と現行運用を分けて整理した後、意味を変えずに全文を読み直した。削除済みautomationを現在形で説明せず、現在の手動手順と将来automationを戻す場合の契約が自然に読み分けられる日本語へ整えた。
''', encoding="utf-8")
