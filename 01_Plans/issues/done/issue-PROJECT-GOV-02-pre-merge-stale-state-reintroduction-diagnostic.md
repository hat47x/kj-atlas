# Issue: PROJECT-GOV-02 merge前にstale state再流入候補を診断する

- Type: Process / DX / Contract Integrity
- Status: Done
- Source Issue: `PROJECT-GOV-01`
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/`, Git branch / PR integration workflow
- Related ADR/Spec: `ADR-0034`, `PROJECT-GOV-01`
- Expected verification level: `unit`

## Requirement meta I/F（共通キー）

- RequirementID: PROJECT-GOV-02
- RequirementStatement: 古いbranchであること自体を禁止せず、merge-base以降にcurrent mainとbranchの双方が触れたpathと、削除済み状態を逆向きに戻す強い候補をmerge前に機械診断できるようにする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=mainと作業branchが共通のmerge-baseから分岐している / 操作=診断scriptへbase/head refを与える / 期待結果=双方変更path、main削除後のbranch側再出現、main現存pathのbranch側削除を区別して報告し、commit距離だけでは失敗しない / 除外=semantic duplicateの完全検出、stale branch全面禁止、branch protection変更。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A

## 1. 課題 / Problem statement

2026-09-04までのcurrent-main継続dogfoodで、古いbranch状態が後から正本へ再流入する事象が、異なる面で複数回観測された。

- `DX-CI-STALE-MERGE-ONESHOT-01`: 成功時に削除済みだったmergeMethod系one-shot workflow/scriptが後続mainへ再出現した。
- `DOC-ISSUE-LIFECYCLE-REINTRODUCED-COPY-01`: `done/`へ整理済みのIssue旧コピーがactive直下へ再出現した。
- `DX-FRONTEND-MERGE-METHOD-DRIFT-01`: 旧branch由来の再mergeで、既に導入済みの`mergeMethod` import/field/parser blockが二重化し、古いfixtureとの不整合でtypecheckが失敗した。

局所guardは機能している。特にPR #2897では、退役したone-shot資産の正確な10pathについて再出現を回帰テストで拒否するようになった。またIssue lifecycle validatorやfrontend typecheckも、発生後の不整合を検出した。

不足しているのは、**未知のpathを含め、merge直前に「branchの世界像がcurrent mainで既に変更・削除された状態を戻そうとしていないか」を横断的に確認する診断**である。

## 2. 判断境界

### やること

- `git merge-base` を基準に、base側とhead側の変更pathを別々に取得する。
- 双方が触れたpathをreview signalとして列挙する。
- 次のpath-level状態を強い再流入候補として区別する。
  1. base側で削除済みだがhead側には存在し、headもmerge-base以降にそのpathを変更している。
  2. base側では現存・変更済みだがhead側がそのpathを削除している。
- JSON出力と人間可読出力を持つ。
- 明示指定時だけ強い候補でnon-zero exitできる。

### やらないこと

- branchがmainよりN commits古いという理由だけで失敗させない。
- 双方が同じpathを変更しただけで自動的にmergeを拒否しない。
- source file内部の意味的二重挿入を完全検出できるとは主張しない。
- #2897の既知path guardやtypecheck、unit/E2E testを置き換えない。
- このIssueだけでbranch protection、merge queue、required checkを変更しない。

R21で確認したとおり、commit距離と意味ドリフトは同じではない。診断は「stale度スコア」ではなく、現在mainとの差分関係を可視化する。

## 3. 受入条件 / Acceptance criteria

- [x] AC-1 `merge-base..base` と `merge-base..head` の変更pathを別々に取得できる。
- [x] AC-2 双方変更pathをoverlapとして報告するが、それだけではstrong findingにしない。
- [x] AC-3 base側で削除済み・head側で存在するpathを`main_deleted_branch_present`としてstrong分類できる。
- [x] AC-4 base側で現存・変更済み・head側で削除されたpathを`branch_deletes_main_present`としてstrong分類できる。
- [x] AC-5 commit距離が大きくてもpath overlapがなければstrong findingにならない。
- [x] AC-6 `--json`でmerge-base、両側commit数、overlap、strong findingを機械可読出力できる。
- [x] AC-7 `--fail-on-strong`指定時だけstrong findingでnon-zero exitし、通常診断は観察用途として成功終了する。
- [x] AC-8 synthetic Git repository testで非重複、resurrection、benign overlap、destructive deletion、commit距離のみの5ケースを検証する。
- [x] AC-9 planning/docs/triage検証に既存エラーを増やさない。
- [x] AC-10 current branchをcurrent mainに統合する直前に本診断を実使用し、結果と限界をR22へ記録する。

## 4. 実装タスク / Task breakdown

- [x] T1 `01_Plans/check_stale_merge_reintroduction.py` を追加する。
- [x] T2 `01_Plans/test_check_stale_merge_reintroduction.py` にsynthetic Git testを追加する。
- [x] T3 継続dogfood R22のA型/B型記録へ、局所guardと横断診断の役割分担を残す。
- [x] T4 branch-only検証でunit / planning / docs / triage / diff-checkを実行する。
- [x] T5 merge直前のcurrent mainに対して診断を実使用し、strong findingが出た場合は自動mergeせず内容を確認する。

## 5. 検証計画 / Validation plan

予定コマンド:

```bash
cd 01_Plans
python -m unittest test_check_stale_merge_reintroduction.py
python check_stale_merge_reintroduction.py --base-ref origin/main --head-ref HEAD --json
python check_stale_merge_reintroduction.py --base-ref origin/main --head-ref HEAD --fail-on-strong
cd ..
python 01_Plans/dogfood/validate_dogfood_docs.py
python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues
python 01_Plans/docs_check.py
python 01_Plans/triage_actionable_plans.py --format json
```

期待結果:

- synthetic 5ケースが成功する。
- current branch診断では重複pathを観察でき、strong findingがあればmerge前に止められる。
- `triage_actionable_plans.py` の`errors`が空である。

## 6. 代替案 / Alternatives considered

- **古いbranchを全面禁止する**: 却下。長期branchでも意味的に独立・妥当な変更はあり、commit距離だけでは意味ドリフトを判定できない。
- **全overlap pathでfailする**: 却下。並行開発で正常な同一path変更まで過剰に止める。
- **既知の危険pathだけdenylist化する**: #2897として有効だが、未知の再流入や既存source file内部のstale変更には一般化しないため補完策とする。
- **semantic merge checkerを先に作る**: 現時点では過大。まずpath-levelの強い候補を低コストに可視化し、実使用所見から必要性を判断する。

## 7. リスク / Rollback

- 誤検知: intentional resurrection/deletionもstrong候補になる。したがって初期段階は診断であり、意味判断は人間へ残す。
- 見逃し: 同一file内部の二重field/importのようなsemantic duplicateはpath-level診断だけでは判定できない。既存typecheck/testを維持する。
- rollback: script/test/Issueを削除すればproduct/runtime契約には影響しない。

## 8. 完了境界

このIssueは、診断script・synthetic test・current branchでの実使用までを完了境界とする。恒久required check化やbranch protection変更は、実使用で有益性と誤検知特性が確認されるまで別判断とし、本IssueのDone条件に含めない。

## 9. 完了記録 / Completion evidence

- synthetic Git repository 5ケース: success。
- 初回実使用 Run `33874427426`: current mainに対して `overlap=0 / strong=0`。
- merge直前再診断: base=`935f9fb2281aef9d7b90203b59fe22fb9eeb3885`, head=`4403e6a1dd796ccf21ac3a04e06ddad622612b84`, overlap=0, strong=0。
- dogfood/docs/Issue lifecycle/triageはone-shot検証で再確認する。
- 恒久required check / branch protection化は本IssueのDone条件外のまま保留する。
