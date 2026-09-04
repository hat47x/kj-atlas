# Issue: DOC-TRIAGE-ADR-STATUS-01 注釈付きAccepted ADRが依存Issueを誤ってBlockedにする

- Type: Bug / Process
- Status: Done
- Source Issue: レーンC active-plan再triage（2026-09-04）
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/test_triage_actionable_plans.py`
- Related ADR/Spec: `ADR-0069`, `01_Plans/issues/README.md`
- Expected verification level: `unit`

## 課題

レーンCで最新mainを `triage_actionable_plans.py --format json` へ通したところ、`AI-IR-PROJECTION-01` は `Status: In Progress / Priority: P1` でありながら、blockerとして次を持ち `Blocked` に分類された。

- `ADR-0069:Accepted（2026-08-29、...）`

ADR-0069はすでにAcceptedであり、依存条件を満たしている。triageの `parse_adr()` がADR statusへIssue用の `normalize_status()` を適用している一方、この関数は `Accepted / Proposed / Superseded / Deprecated / Rejected` を正規化しないため、注釈込み文字列をcanonical `Accepted` と認識できていなかった。

一回限り監査 run `33829297928` で81 ADRのraw `Status` を確認したところ、66件はexact `Accepted`、5件はexact `Proposed`、**10件は注釈付きAccepted** だった。対象はADR-0027/0035/0052/0053/0054/0057/0064/0069/0076/0078であり、半角括弧・全角括弧の双方が存在した。

したがってADR-0069だけのmetadata修正ではなく、triage parser側でADR statusと注釈を分離して解釈する。

## 対応方針

- Issue statusは引き続き `parse_issue_status()` によるstrict canonical contractを維持する。`Draft (waiting)` のような装飾付きIssue statusを許容しない。
- ADR専用 `normalize_adr_status()` を追加し、known canonical ADR statusの直後に空白・半角括弧・全角括弧で注釈が続く場合だけcanonical statusへ正規化する。
- canonical ADR statusは `Accepted / Proposed / Superseded / Deprecated / Rejected` とする。
- `AcceptedButPending` のように区切りなしで別語へ続く値は正規化せず、fail-closedのまま扱う。
- 注釈本文はADR文書側に残し、10 ADRを一括書換えしない。

## 受入条件

- [x] `Accepted (note)` と `Accepted（注釈）` の両方が `Accepted` として解釈される。
- [x] 注釈付きAccepted ADRへ依存するOpen/In Progress IssueがReadyになる。
- [x] `Proposed (note)` は `Proposed` として依然blockerになる。
- [x] `AcceptedButPending` のような非canonical語をAcceptedへ誤正規化しない。
- [x] Issue側の `Draft (waiting)` strict rejectionは維持される。
- [x] 実repo triageで `AI-IR-PROJECTION-01` からADR-0069の偽blockerが消える。
- [x] `test_triage_actionable_plans.py`、`docs_check.py`、triage JSON生成、`git diff --check` が成功する。

## 実装結果

`triage_actionable_plans.py` にADR専用 `normalize_adr_status()` を追加した。既知のcanonical ADR statusの直後が、完全一致、空白、半角 `(`、全角 `（` のいずれかである場合だけcanonical statusへ戻す。これにより注釈本文をADR側へ保持したまま依存判定では `Accepted` として扱える。

Issue statusの解釈経路は変更していない。Issueは従来どおり `parse_issue_status()` のstrict canonical contractを通り、`Draft (waiting)` 等を許容しない。

`test_triage_actionable_plans.py` へ次の回帰を追加した。

- `Accepted (note)` / `Accepted（注釈）` → `Accepted`
- `Proposed (note)` → `Proposed`
- `AcceptedButPending` → 非canonicalのまま
- 注釈付きAccepted依存 → Ready
- 注釈付きProposed依存 → Blocked

## 検証結果（2026-09-04）

一回限りworkflow run `33829411789` で次を確認した。

- `python -m unittest 01_Plans/tests/test_triage_actionable_plans.py` → 8 tests, OK
- 実repo triageで `AI-IR-PROJECTION-01` → `ready=True`, `blockers=[]`
- 全active Issueの `:Accepted...` blocker → 0件
- 修正Issue自身をactiveに含む時点のsummary → active=52 / ready=15 / blocked=37
- `python 01_Plans/docs_check.py` → `docs-check passed: active_memos=52, tracked_markdown=757`
- `git diff --check` → success

本Issue自身は新規完了memoなので、issue lifecycle契約に従ってactive直下へDoneとして残さず `done/` へmoveする。移動後はactive数が1件減るため、最終期待値は active=51 / ready=14 である。

## 非目標

- 10件のADR本文から注釈を削除すること。
- ADR metadata schema全体の再設計。
- `AI-IR-PROJECTION-01` 自体の実装を進めること。
- Accepted ADRを未採択へ戻すこと。
