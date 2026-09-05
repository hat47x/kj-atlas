# Issue Memo Index

このディレクトリは、現在の実行タスクを内部issue memoとして管理する。GitHub Issuesは未運用であり、`Source Issue: N/A` を使用する。

## 運用原則

- Actionはissue memo、長期的なDecisionはADR、実行履歴はGitとPRを正本とする。
- 現段階では `ADR-0039` を適用し、Maintainerが起票、実行、完了判断を担う。
- 同じ進捗をdashboard、decision-pack、READMEへ転記しない。
- rerun番号、Stream、固定5フェーズ、RACI通知、仮想役職、手動件数同期は使用しない。
- Done memoは通常のAIコンテキストへ入れず、履歴確認が必要な場合だけ検索する。
- Done memoの本体は `01_Plans/issues/done/` に置く(ADR/CHANGELOGへの昇華が追いつくまでの一時退避。`ADR-0000` rule 40-41)。保持例外(Retention Reason明記)のみ `01_Plans/issues/archive/` へ移動する。
- 同じissue memoのbasenameを `issues/` 直下、`done/`、`archive/` 等へ複製して共存させない。状態遷移に伴う配置変更はcopyではなくmoveとして扱う。`done/` 配下には `Status: Done` のmemoだけを置く。
- GitHub Issues運用を将来開始する場合は、その時点で必要な移行手順を新たに決める。未使用の移行runbookは維持しない。

## 起票方法

1. `TEMPLATE.md` を使い、課題、対応方針、受入条件、検証計画を短く記載する。
2. `Status` は `Draft -> Open -> In Progress -> Done` の順で更新する。
3. `Expected verification level` は変更リスクに応じて `docs-check / unit / integration / e2e` から選ぶ。
4. ADRは長期的、横断的、破壊的、または安全境界を変える判断に限る。
5. 完了時は検証結果と `Status: Done` をmemoへ一度記録し、同じ変更で原則 `done/` へ移す。索引の手動更新は不要。移動元の旧コピーを残さない。

### Done配置のlegacy境界

継続dogfood R18時点では、過去の運用差により `01_Plans/issues/` 直下に `Status: Done` のメモが58件残っていた。この58件はその後、正規の `01_Plans/issues/done/` へ段階的に移行され、2026-09-05に `LEGACY_DONE_AT_ROOT_BASELINE = 0` へ到達した。**現在、active rootに残るDone memoは0件であり、Done-at-rootを許容する移行期間は終了している。**

`validate_active_issue_memos.py` は、移行完了後も次の二つを独立に検査する。

1. **件数境界**: `LEGACY_DONE_AT_ROOT_BASELINE = 0` と実件数の一致を要求する。今後、`Status: Done` のmemoがactive rootへ1件でも現れた場合はfailする。baselineを再び増やして例外を作る運用はしない。
2. **path identity guard**: R18 commit `88aebae242d5d1a24278b3247d3544aeaa1ad386` から一度だけ機械生成した `legacy_done_at_root_r18.json` は、不変の歴史証拠として保持する。現在のDone-at-root集合は空集合なので、このmanifestは移行許可リストではなく「R18に何が存在していたか」を示す監査境界である。

さらに `01_Plans/tests/test_legacy_done_root_references.py` は、R18 legacy Done 58件について、旧 `01_Plans/issues/<name>` が存在しないこと、現在の `01_Plans/issues/done/<name>` が存在すること、tracked filesに旧rootパス参照が再出現しないことを固定する。

新たにDoneへ遷移するメモは、参照先を必要に応じて同時更新したうえで、同じ変更で `done/` へ移す。`legacy_done_at_root_r18.json` へ新規pathを追記したり、`LEGACY_DONE_AT_ROOT_BASELINE` を0より大きく戻したりして検査を回避する運用は禁止する。

このlegacy境界は現在のDone配置に対する例外ではない。R18の58件という数とmanifestは移行履歴・監査証拠として残し、現行契約は **Done-at-root 0件** と **旧root参照0件** を維持することである。

## 必須メタデータ

- `Type`
- `Status`
- `Source Issue`
- `Priority`
- `Scope`
- `Related ADR/Spec`
- `Expected verification level`

### `Owner` フィールドの意味（DOC-OPS-07 案(c)・2026-08-12 仮承認）

`Owner:` は**役職・担当者の割当てではなく、「どの観点からのレビューが望ましいか」を示すメモ**として扱う（`Security Officer + System Owner + Platform Operator` 等の記載は「複数観点のレビューを要する」の合図）。`ADR-0039`（個人OSS・Maintainer 単独運用）に合わせ、実行責務は全issueとも Maintainer が担う。`Owner` は必須メタデータに含まれない（`validate_active_issue_memos.py` も読み取らない）。

## Active issue memos

Active一覧は各memoの `Status` から生成する。READMEへ表を転記しない。

```powershell
python 01_Plans/triage_actionable_plans.py
```

`Draft / Open / In Progress` がActive、`Done` が完了である。特定領域だけを見る場合は、出力をBacklog ID、Priority、Scopeで絞り込む。

## 軽量ツール

- issue / docs変更の統一検証入口: `python 01_Plans/docs_check.py`（有効化済みruleだけをblocking実行し、未有効化ruleも表示）
- Active memo検証: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`（README表ではなくmemoを直接走査し、配置・basename一意性・Done-at-root件数/identity境界も検査）
- 検証ツールのテスト: `python -m unittest discover -s 01_Plans/issues/tests -p "test_*.py"`
- タスク候補の絞り込み: `python 01_Plans/triage_actionable_plans.py`

過去の同期ログ、件数、Decision Queue、RACI記録はGit履歴に残っている。現在の作業判断には使用しない。
