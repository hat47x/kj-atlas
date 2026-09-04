# Issue: DOC-ISSUE-LEGACY-PATH-01 Done-at-rootの同数入替でlegacy境界をすり抜けられる

- Type: Bug / Process
- Status: In Progress
- Source Issue: PR #2858 再評価 / レーンC横断監査（2026-09-04）
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/issues/`, `01_Plans/issues/validate_active_issue_memos.py`
- Related ADR/Spec: `DOC-ISSUE-LIFECYCLE-01`, `DOC-ISSUE-IDENTITY-01`, `01_Plans/issues/README.md`
- Expected verification level: `unit`

## 課題

`DOC-ISSUE-LIFECYCLE-01` では、R18時点でactive直下に残っていた `Status: Done` 58件を一時baselineとし、実件数との一致を要求するexact count ratchetを導入した。58件から57件へ減らした場合は同じ変更でbaselineも57へ下げるため、一度減ったlegacy件数が古い上限まで戻ることは防げる。

しかし件数だけでは、次の変更を区別できない。

1. R18 legacyの `issue-b.md` を正しく `done/` へ移す。
2. 同じ変更で、新たに完了した `issue-c.md` をactive直下へ `Status: Done` のまま置く。
3. Done-at-root件数は58のままなので、count ratchetだけなら一致してしまう。

`DOC-ISSUE-IDENTITY-01` で導入したbasename一意性ガードも、このケースでは旧pathが消えて新pathだけが残るため検出できない。

PR #2858 はR18 commitから毎回Git履歴を再構成する案を提示していた。方向は妥当だが、最新mainではrepo固有baselineをsynthetic fixtureへ漏らさない境界が追加されており、さらにshallow cloneや履歴を持たない配布ソースでも検証を安定させたい。そのため、R18 commitから一度だけ機械生成した不変manifestを履歴境界として保存する方式へ置き換える。

## 事前監査

一回限りworkflow run `33828753648` で、R18 commit `88aebae242d5d1a24278b3247d3544aeaa1ad386` と現在mainのDone-at-root basename集合を比較した。

- R18 baseline: 58件
- current: 58件
- currentのうちR18集合外: 0件
- R18集合のうち既に移動済み: 0件

したがって現時点では同数入替はまだ発生しておらず、新しいlegacy例外を設けずにfail-closed化できる。

## 対応方針

- R18 commitから機械生成した `legacy_done_at_root_r18.json` を不変のidentity baselineとして保持する。
- 現在active直下にある `Status: Done` のbasename集合は、常にR18 identity集合の部分集合でなければならない。
- legacyを `done/` へ移して現在集合が縮むことは許容する。identity manifestは更新しない。
- 件数ratchetは従来どおり別に維持し、移行時は `LEGACY_DONE_AT_ROOT_BASELINE` を58→57→…→0へ下げる。
- identity manifestへ新規pathを追記して検査を通す運用は禁止する。固定R18 commitからの歴史証拠として扱う。
- synthetic fixtureにはrepo固有identity baselineを暗黙適用せず、unit testではbaseline集合を明示注入できるようにする。

## 受入条件

- [ ] R18 identity manifestが固定commitから機械生成され、58件・重複なし・basenameのみであることをvalidatorが検証する。
- [ ] legacy 1件を減らし新規Done-at-root 1件を増やして件数を維持するfixtureで、count ratchetは通るがidentity guardが新規pathを拒否する。
- [ ] R18集合の部分集合へ減る正常なlegacy移行はidentity guardを通る。
- [ ] synthetic rootではrepo identityを暗黙適用せず、明示baselineで統一 `validate()` の配線をテストできる。
- [ ] 実repoでR18集合外のDone-at-rootが0件である。
- [ ] `docs_check.py`、issue validator、lifecycle/identity関連unit、triage、`git diff --check` が成功する。

## 非目標

- legacy 58件の一括移動。
- R18 identity manifestを現在状態へ同期し続けること。
- 完了済み `DOC-ISSUE-LIFECYCLE-01` を再オープンすること。
- GitHub Actionsの恒久再導入。
