# Issue: DOC-ISSUE-LIFECYCLE-01 完了済みIssueメモがactive直下へ残り続ける

- Type: Process / Documentation
- Status: Done
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

2026-09-04の初回対応では、既存58件をlegacy上限として固定する。これは維持目標ではなく、57件以下への減少を常に許容する上限である。新たな完了メモは同じ変更で `done/` へ移す運用を正本へ明記し、上限を超えた場合はdocs contractでblockingする。

## 受入条件

- [x] `Status: Done` とactive直下配置の関係について、legacy許容範囲と新規変更時の規則を明文化する。
- [x] 新たにDoneへ遷移するIssueが、意図せずactive直下へ残ることをdocs contractで検出できる。ただし既存legacy 58件を即時エラーにはしない。
- [x] legacy baselineを固定する場合、件数または対象一覧が理由なく増えないことを検査する。
- [x] 既存Done-at-rootを移動する場合は参照先を同時更新し、`docs_check.py` と関連dogfood検査を通す運用を明文化する。
- [x] 大量一括移動を、このIssueの完了条件にはしない。

## 実装・検証結果

- `validate_active_issue_memos.py` にactive直下のDone件数を検査する規則を追加し、58件をlegacy上限とした。
- `done/` 配下の完了メモは上限へ数えず、既存legacyを移して件数が減る場合も基準値の更新を要求しない。
- 回帰テストとして、58件の許容、59件目の拒否、57件への減少、`done/` 配下の非計上を追加した。焦点テスト4件はローカルで成功した。
- `01_Plans/issues/README.md` に、新規完了時は `Status: Done` の記録と `done/` への移動を同じ変更で行うこと、legacy Doneの移動時は参照先も同じ変更で更新し、docs-checkと関連dogfood検査を通すことを追記した。
- 一時workflow `Temporary issue lifecycle docs check`（run `33818932813`）で `python 01_Plans/docs_check.py`、dogfood文書検査、planning triage、`git diff --check` がすべて成功した。
- 一時workflowは成功後に自身を削除し、恒久的なCIファイルをmainへ残さない運用とした。
- 本Issue自身も新規完了ルールに従い、`Status: Done` とした本体を `01_Plans/issues/done/` へ移した。

## 優先度

P2とする。現在のactive判定はstatusベースで機能しており、今回発見したremote merge契約不整合のような実利用経路のP1欠陥を先に直すべきである。ただし、正本へ戻る導線を長期的に保つため、状態と配置の二重表現を放置して増やし続けない。

## 文書品質の仕上げ

「58件あるから直ちに全件移動する」とせず、現行triageが壊れていない事実と、導線としての不整合を分けて記述した。既存差分を増やすこと自体を目的にせず、今後の増加を止めてから段階的に整理する方針が自然に読めるよう整えた。
