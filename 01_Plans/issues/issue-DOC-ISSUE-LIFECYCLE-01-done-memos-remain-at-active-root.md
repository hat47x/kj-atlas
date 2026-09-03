# Issue: DOC-ISSUE-LIFECYCLE-01 完了済みIssueメモがactive直下へ残り続ける

- Type: Process / Documentation
- Status: In Progress
- Source Issue: 継続dogfood R18
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/issues/`, `01_Plans/issues/done/`, `01_Plans/triage_actionable_plans.py`, docs contract
- Related ADR/Spec: `01_Plans/issues/README.md`
- Expected verification level: docs-check

## 課題

継続dogfood R18で `01_Plans/issues/issue-*.md` を機械走査したところ、ルート直下110件のうち58件が `Status: Done` だった。`01_Plans/issues/README.md` は完了済みメモを `01_Plans/issues/done/` へ置く運用を示しているが、過去の実装では状態更新だけが先行し、配置が追随していない例が蓄積している。

現時点で `triage_actionable_plans.py` はstatusを正本としてDoneをactive対象から除外している。そのため58件の存在だけで実装優先順位が直ちに誤るわけではない。一方、ディレクトリ名から状態を推測する人間や補助ツールにとっては、active直下と完了済みという二つの表現が食い違う。今回も `AI-MERGE-APPLY-01` が `Status: Done` のままactive直下に残っていることから、このずれを再確認した。

## 方針

既存58件を一度に移動しない。大量の参照先変更を伴い、意味のない差分で現在の開発を埋めるためである。

まず、今後新たにDoneへ遷移するメモについて、状態と配置のずれを増やさない仕組みを整える。その後、既存のDone-at-rootは参照影響を確認しながら小さな単位で移行するか、legacyとして許容する範囲を明記する。

R19では58件を一時的な件数ラチェットとして固定する。既存legacyを即時エラーにせず、58件以下への減少は許容し、59件以上への増加だけをdocs contractで拒否する。個別ファイルを恒久的なallowlistとして正当化せず、段階整理が進めば上限を引き下げられる形にする。

## 受入条件

- [x] `Status: Done` とactive直下配置の関係について、legacy許容範囲と新規変更時の規則を明文化する。
- [x] 新たにDoneへ遷移するIssueが、意図せずactive直下へ残ることをdocs contractで検出できる。ただし既存legacy 58件を即時エラーにはしない。
- [x] legacy baselineを固定する場合、件数または対象一覧が理由なく増えないことを検査する。
- [ ] 既存Done-at-rootの移動は参照先を同時更新し、`docs_check.py` と関連dogfood検査を通す。
- [x] 大量一括移動を、このIssueの完了条件にはしない。

## R19実装結果（2026-09-04）

`validate_active_issue_memos.py` に、ルート直下の `Status: Done` だけを数える配置検査を追加した。R18で観測した58件を一時上限とし、件数が増えた場合だけblocking errorにする。`done/` 配下の完了メモはこのlegacy予算へ数えない。

専用unit testでは、基準件数そのものは許容すること、基準超過を拒否すること、件数減少を許容すること、`done/` 配下がルートlegacy件数へ混ざらないことを固定した。`README.md` にも、新たな完了メモは同じ変更で `done/` へ移すことと、58件が正規配置ではなく一時ラチェットであることを明記した。

実リポジトリ全体での `docs_check.py` と関連検査はPR上のCIで確認する。成功後、このIssue自身を `done/` へ移して完了とする。

## 優先度

P2とする。現在のactive判定はstatusベースで機能しており、今回発見したremote merge契約不整合のような実利用経路のP1欠陥を先に直すべきである。ただし、正本へ戻る導線を長期的に保つため、状態と配置の二重表現を放置して増やし続けない。

## 文書品質の仕上げ

「58件あるから直ちに全件移動する」とせず、現行triageが壊れていない事実と、導線としての不整合を分けて記述した。既存差分を増やすこと自体を目的にせず、今後の増加を止めてから段階的に整理する方針が自然に読めるよう整えた。
