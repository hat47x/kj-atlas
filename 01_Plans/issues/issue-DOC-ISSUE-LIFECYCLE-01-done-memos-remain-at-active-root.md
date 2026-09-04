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

まず、今後新たにDoneへ遷移するメモについて、状態と配置のずれを増やさない仕組みを整える。その後、既存のDone-at-rootは参照影響を確認しながら小さな単位で移行する。

R19では58件を一時的なbaselineとしてコードへ固定し、実際のDone-at-root件数との**一致**を要求する。件数が59以上なら新しいlegacy debtとして拒否する。逆に57以下へ減った場合も、その変更でbaselineを同じ値へ下げなければ検査を通さない。これにより、一度減らしたlegacyが古い上限まで増え直すことを防ぐ。

個別ファイルを恒久的なallowlistとして正当化せず、baselineだけを段階的に58→57→…→0と単調減少させる。

## 受入条件

- [x] `Status: Done` とactive直下配置の関係について、legacy許容範囲と新規変更時の規則を明文化する。
- [x] 新たにDoneへ遷移するIssueが、意図せずactive直下へ残ることをdocs contractで検出できる。ただし既存legacy 58件を即時エラーにはしない。
- [x] legacy baselineを固定する場合、件数または対象一覧が理由なく増えないことを検査する。
- [x] 既存Done-at-rootを今後移動するときは、必要な参照先更新とbaseline引下げを同じ変更に含める規則を明文化する。
- [x] 大量一括移動を、このIssueの完了条件にはしない。

## R19実装結果（2026-09-04）

`validate_active_issue_memos.py` に、ルート直下の `Status: Done` だけを数える配置検査を追加した。R18で観測した58件を `LEGACY_DONE_AT_ROOT_BASELINE` として保持し、実件数がbaselineと異なる場合にblocking errorを返す。

- 59件以上: 新たなDone-at-rootが増えたため拒否する。
- 58件: 現在のlegacy状態として許容する。
- 57件以下: 整理自体は望ましいが、同じ変更でbaselineも下げるよう要求する。
- `done/` 配下: root legacy件数へ数えない。

最初は「58を上限にして、それ以下を許容する」実装を作った。しかし差分再点検で、57へ減った後に別変更で58へ戻れてしまうことを検出したため、exact baseline方式へ補正した。これはR19自身のdogfoodで得られた二次的な改善である。

専用unit契約について、基準値一致、増加拒否、減少時のbaseline更新要求、`done/` 除外の4ケースを確認した。新規テストファイルのmodule読込も、既存validator testと同じ `sys.path` / `sys.modules` 登録方式へ揃えた。

現在のmainには `.github/workflows/` が存在せず、PR #2854にも自動workflow runは作られていない。このIssueのためにworkflowを再導入してpushをblockすることはしない。リポジトリ全体の `docs_check.py` を自動CI成功と誤記せず、今回確認できた専用契約と差分レビューを実装根拠として分けて記録する。

## 優先度

P2とする。現在のactive判定はstatusベースで機能しており、今回発見したremote merge契約不整合のような実利用経路のP1欠陥を先に直すべきである。ただし、正本へ戻る導線を長期的に保つため、状態と配置の二重表現を放置して増やし続けない。

## 文書品質の仕上げ

「58件あるから直ちに全件移動する」とせず、現行triageが壊れていない事実と、導線としての不整合を分けて記述した。58という数も正規状態として固定せず、段階整理の現在地を単調に減らす一時baselineとして扱う。
