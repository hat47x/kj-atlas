# issue-DOC-ISSUE-LIFECYCLE-REINTRODUCED-COPY-01 — `done/`へ整理済みのIssue旧コピーをactive直下へ残さない

- Type: Process / Documentation quality
- Status: Done
- Source Issue: `DOC-ISSUE-LIFECYCLE-01`
- Priority: P1
- Scope: `01_Plans/issues/`, `01_Plans/issues/done/`
- Related ADR/Spec: `01_Plans/issues/README.md`
- Expected verification level: `docs-check`

## 背景

issue lifecycleの検証を実行したところ、すでに `01_Plans/issues/done/` へ整理済みの2件について、同じbasenameの旧コピーがactive直下にも存在していました。

- `AI-MERGE-PARTIAL-01-define-partial-merge-selection-contract`
- `DOC-ISSUE-LIFECYCLE-01-done-memos-remain-at-active-root`

前者のroot側は `Status: Done` のまま残っており、新たなDone-at-rootとしてR18 baseline 58件を59件へ増やしていました。後者のroot側は古い `In Progress` 版で、`done/`側にはその後のR19実装・レーンC補正と、自身を `done/` へ移して完了する判断まで記録されています。

この状態では、同じIssue identityにActiveとDoneの二つの正本候補が現れます。また、件数ratchetとidentity guardが意図どおり不整合を検出しているのに、repository全体のplanning検証が常時赤になるため、新しい変更による退行と既存の再流入を区別しにくくなっていました。

## 対応

`done/`側を現在の正本として維持し、active直下へ再流入していた旧コピー2件だけを削除しました。

`done/`側の本文は変更していません。特に `AI-MERGE-PARTIAL-01` の完了境界と、`DOC-ISSUE-LIFECYCLE-01` の58件baseline・identity guard・synthetic fixture境界の記録はそのまま保持します。

## 判断根拠

- `AI-MERGE-PARTIAL-01` はroot・`done/`ともDoneであり、`done/`側が実装履歴を圧縮した完了memoとして整理済みだった。
- `DOC-ISSUE-LIFECYCLE-01` の `done/`側にはroot版より後の実装・検証記録が含まれ、「本Issue自身も `done/` へ移して完了」と明示されていた。
- lifecycle validatorは同一basenameの重複、新規Done-at-root、baseline超過をすべて検出しており、guardを弱める理由はない。

## 完了条件

- 同一basenameのroot / `done/` 重複が解消されること。
- Done-at-root件数がR18 baselineの58件へ戻ること。
- active Issue memo validatorが成功すること。
- `docs_check.py` が成功すること。
- triageがエラーなく完走すること。

今回の対応ではbaselineやvalidatorを緩めず、不正状態そのものを正本配置へ戻す。
