# Issue: DOC-CI-DRIFT-01 Actions無効化後のdocs/release契約を現行構成へ同期する

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
- `python 01_Plans/triage_actionable_plans.py --format json`
- `git diff --check`

## 非目標

- GitHub Actionsの常設workflowを再導入すること。
- 公開配布channelや署名基盤を、この修正だけで新設すること。
- 過去のリリースworkflowを現在も動作するものとして保存すること。

## 文書品質の仕上げ

原因と現行運用を分けて整理した後、意味を変えずに全文を読み直した。削除済みautomationを現在形で説明せず、現在の手動手順と将来automationを戻す場合の契約が自然に読み分けられる日本語へ整えた。
