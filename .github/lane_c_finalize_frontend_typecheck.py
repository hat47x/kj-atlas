from pathlib import Path

src = Path("01_Plans/issues/issue-DX-FRONTEND-MERGE-METHOD-DRIFT-01-restore-typecheck-after-stale-merge.md")
done = Path("01_Plans/issues/done") / src.name
text = src.read_text(encoding="utf-8")
text = text.replace("- Status: In Progress", "- Status: Done", 1)
text = text.replace("- [ ] ", "- [x] ")
text += """

## 検証結果

current main `528d05956dd96fc9880cd800dce3c714acef9909` から切ったbranchで、正本契約を変えずに状態ドリフトを修復した。

- `npm run typecheck`: success
- mergeMethod / Stream B / external-agent / decision / UIの対象Vitest: 59件成功
- planning unit tests: 130件成功、1件skip
- Active issue memo validator: success
- docs-check: success
- triage: `errors: []`
- `git -c core.whitespace=cr-at-eol diff --check`: success
- 実装差分は対象frontend 7ファイルだけ、追加15行・削除14行相当の局所差分として検証した

## 原因整理

PR #2869で `mergeMethod` のproposal→decision追跡契約はtypecheckを含めて検証済みだった。その後、旧作業branch由来の変更がmainへ再マージされ、同じimport・field・property・parser blockが一部経路へ二重に入った。一方、別系統の古いfixtureは新規入力で必須となった `mergeMethod` やpartial時の明示 `selectedCardIds` を持たないまま残った。

このため、同じ正本内に「新契約の二重挿入」と「旧fixtureの未同期」が同時に存在し、TypeScript型検査とStream B回帰が破綻していた。

## 完了境界

- `mergeMethod` の二値語彙とremote/commonのfail-closed契約は変更していない。
- 旧保存済みdecisionで `mergeMethod` 欠落を許容し、推測補完しない後方互換境界も変更していない。
- partialの明示選択契約は緩めず、Stream B handoff側が `selectedCardIds` を運べるように同期した。
- unrelatedなfrontend refactor、依存パッケージ更新、npm audit警告の解消は本Issueへ含めていない。
"""
done.write_text(text, encoding="utf-8")
src.unlink()
