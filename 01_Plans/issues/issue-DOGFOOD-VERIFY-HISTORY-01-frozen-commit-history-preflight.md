# Issue: DOGFOOD-VERIFY-HISTORY-01 frozen source検証がshallow checkoutを資料欠落として誤診断する

- Type: Test / Developer Experience
- Status: In Progress
- Source Issue: レーンC `DOC-TRIAGE-ADR-STATUS-01` 最終検証 run `33829493679`
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/dogfood/validate_dogfood_docs.py`, `01_Plans/dogfood/test_validate_dogfood_docs.py`, `01_Plans/dogfood/README.md`
- Related Backlog: `DOGFOOD-VERIFY-HISTORY-01`
- Related ADR/Spec: `01_Plans/dogfood/cognitive-dogfood-case-portfolio-freeze.md`
- Expected verification level: `unit`

## 課題

`validate_dogfood_docs.py` は Case 001–003 の frozen product source manifestについて、固定commit `2232b3bb26647e5c4a083f55bdbf83c161698649` の各pathを `git rev-parse <commit>:<path>` で照合する。ところが実行環境にそのcommitがない場合も各pathの欠落として扱うため、GitHub Actionsの既定shallow checkoutでは同一原因が56件の `source cannot resolve at frozen commit` に展開される。

run `33829493679` ではtriage unit、issue validator、docs-checkは成功した一方、この履歴不足だけでdogfood validatorが56件失敗した。`fetch-depth: 0` に変更した run `33829574611` では同じ内容が成功しており、資料欠落ではなく検証環境の前提不足だった。

## 対応方針

- frozen blob照合前に、固定product commitがローカルGit object databaseで利用可能か一度だけ検査する。
- 固定commitがない場合は、各source pathへ展開せず「固定commitを取得してから再実行する」1件の明確な環境エラーとしてfail-closedする。
- manifestのJSON/schema/path安全性等、Git履歴を必要としない検査はshallow環境でも継続する。
- 固定commitが利用可能な場合は既存のpath/blob照合をすべて維持する。
- validator自身はnetwork fetchを行わない。CI/利用者が `fetch-depth: 0` または固定commitの明示fetchを選べるようREADMEへ前提を書く。

## 受入条件

- [ ] 固定commitがないshallow checkoutで、履歴不足が1件のactionableな診断として報告される。
- [ ] 同じ条件で56件のpath欠落診断へ展開されない。
- [ ] 履歴不足でもmanifestの構造検査は継続される。
- [ ] 固定commit取得後は従来どおり全sourceのpath/blob照合が行われる。
- [ ] validatorは履歴不足を成功扱いせずexit 1を返す。
- [ ] validatorがnetwork fetchを副作用として実行しない。
- [ ] `test_validate_dogfood_docs.py`、dogfood validator、`docs_check.py`、active issue validator、`git diff --check` が成功する。

## 非目標

- frozen product commitやmanifest内容の変更。
- cultural-substrate-weaving側commitをkj-atlasのローカルGit履歴から照合すること。
- 永続GitHub Actions workflowの追加。
