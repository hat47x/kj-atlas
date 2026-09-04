# Issue: DOC-TRIAGE-ADR-STATUS-01 注釈付きAccepted ADRが依存Issueを誤ってBlockedにする

- Type: Bug / Process
- Status: In Progress
- Source Issue: レーンC active-plan再triage（2026-09-04）
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/test_triage_actionable_plans.py`
- Related ADR/Spec: `ADR-0069`, `01_Plans/issues/README.md`
- Expected verification level: `unit`

## 課題

レーンCで最新mainを `triage_actionable_plans.py --format json` へ通したところ、`AI-IR-PROJECTION-01` は `Status: In Progress / Priority: P1` でありながら、blockerとして次を持ち `Blocked` に分類された。

- `ADR-0069:Accepted（2026-08-29、...）`

ADR-0069はすでにAcceptedであり、依存条件を満たしている。triageの `parse_adr()` がADR statusへIssue用の `normalize_status()` を適用している一方、この関数は `Accepted / Proposed / Superseded / Deprecated / Rejected` を正規化しないため、注釈込み文字列をcanonical `Accepted` と認識できていない。

一回限り監査 run `33829297928` で81 ADRのraw `Status` を確認したところ、66件はexact `Accepted`、5件はexact `Proposed`、**10件は注釈付きAccepted** だった。対象はADR-0027/0035/0052/0053/0054/0057/0064/0069/0076/0078であり、半角括弧・全角括弧の双方が存在する。

したがってADR-0069だけのmetadata修正ではなく、triage parser側でADR statusと注釈を分離して解釈する。

## 対応方針

- Issue statusは引き続き `parse_issue_status()` によるstrict canonical contractを維持する。`Draft (waiting)` のような装飾付きIssue statusを許容しない。
- ADR専用 `normalize_adr_status()` を追加し、known canonical ADR statusの直後に空白・半角括弧・全角括弧で注釈が続く場合だけcanonical statusへ正規化する。
- canonical ADR statusは少なくとも `Accepted / Proposed / Superseded / Deprecated / Rejected` とする。
- `AcceptedButPending` のように区切りなしで別語へ続く値は正規化せず、fail-closedのまま扱う。
- 注釈本文はADR文書側に残し、10 ADRを一括書換えしない。

## 受入条件

- [ ] `Accepted (note)` と `Accepted（注釈）` の両方が `Accepted` として解釈される。
- [ ] 注釈付きAccepted ADRへ依存するOpen/In Progress IssueがReadyになる。
- [ ] `Proposed (note)` は `Proposed` として依然blockerになる。
- [ ] `AcceptedButPending` のような非canonical語をAcceptedへ誤正規化しない。
- [ ] Issue側の `Draft (waiting)` strict rejectionは維持される。
- [ ] 実repo triageで `AI-IR-PROJECTION-01` からADR-0069の偽blockerが消える。
- [ ] `test_triage_actionable_plans.py`、`docs_check.py`、triage JSON生成、`git diff --check` が成功する。

## 非目標

- 10件のADR本文から注釈を削除すること。
- ADR metadata schema全体の再設計。
- `AI-IR-PROJECTION-01` 自体の実装を進めること。
- Accepted ADRを未採択へ戻すこと。
