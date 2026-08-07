# Issue Draft: DOC-PUBLIC-BOUNDARY-02 内部文書2件の移管実行

- Type: Process
- Status: Draft
- Source Issue: `01_Plans/issues/issue-DOC-PUBLIC-BOUNDARY-01-developer-doc-relocation.md`
- Priority: P3
- Owner: Maintainer
- Scope: `04_Documentation/codex_skill_operations.md`, `04_Documentation/e2e_verification_log_2026-03-03.md`, `04_Documentation/README.md`
- Related ADR/Spec: `01_Plans/issues/issue-DOC-PUBLIC-BOUNDARY-01-developer-doc-relocation.md`, `01_Plans/adr/ADR-0022-doc-ops-04-documentation-information-interface.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## 課題

`DOC-PUBLIC-BOUNDARY-01`（Done 2026-06-20）で `e2e_testing.md` の移管は完了したが、次の2件は「後続タスク」としてdeferredのまま残っている。

- `04_Documentation/codex_skill_operations.md` — AIエージェント運用手順（一般利用者向けではない）
- `04_Documentation/e2e_verification_log_2026-03-03.md` — 検証記録テンプレート（一般利用者向けではない）

`04_Documentation/README.md` は両者を「開発者/AIエージェント向け」に分類しており、一般公開Gistには含めない方針が既に決まっている。物理配置だけが `04_Documentation/`（利用者向けディレクトリ）に残っている。

**参照元**: 両文書への参照は主に `01_Plans/issues/` 配下のissueメモ（履歴参照として許容）と `04_Documentation/README.md`。`DOC-PUBLIC-BOUNDARY-01` は「参照元が多いため、一括移動よりも対象文書ごとの移管先、リンク、公開対象一覧を確認してから行う」と明記している。

## 対応方針（案）

- `codex_skill_operations.md`（AIエージェント運用手順）: `00_Prompt/` または `01_Plans/` へ移設（DOC-PUBLIC-BOUNDARY-01 §5「AIエージェント向けは 00_Prompt/ または 01_Plans/ へ」）。
- `e2e_verification_log_2026-03-03.md`（検証記録）: `03_Implement/` の該当領域または `01_Plans/` へ移設（検証証跡のため）。
- 移設先を決定したら、`04_Documentation/README.md` の除外一覧とリンクを更新し、旧パスに `Superseded` リダイレクトstub（e2e_testing.md と同じ方式）を置くか、参照元issueを直接更新する。
- 移設先の決定は人間の確認を要する（どのディレクトリが正本として適切かの判断）。本issueで移設先案を示し、承認後に実行する。

## 受入条件

- [ ] 2文書の移設先が決定される（00_Prompt/01_Plans/03_Implement のいずれか）。
- [ ] `04_Documentation/README.md` の除外一覧・リンクが新パスへ更新される。
- [ ] 旧パスへの参照が壊れない（リダイレクトstubまたは参照元更新）。
- [ ] `python 01_Plans/docs_check.py` が通る。

## 検証計画

- `grep -rln "codex_skill_operations\|e2e_verification_log_2026-03-03" 01_Plans/ 02_Architecture/ 03_Implement/ 04_Documentation/`
- `python 01_Plans/docs_check.py`
- `git diff --check`
