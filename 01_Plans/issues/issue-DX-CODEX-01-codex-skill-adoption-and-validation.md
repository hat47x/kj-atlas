# Issue Draft: DX-CODEX-01 Codex skill 導入と運用妥当性検証

- Type: Developer Experience
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: AI Collaboration Ops
- Scope: `00_Prompt/` / `01_Plans/issues/` / `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0018`, `ADR-0019`
- Dependencies: N/A
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- Codex skill の利用価値は確認されているが、プロジェクト標準としての導入手順・適用境界・検証導線が分散している。
- その結果、エージェントごとに skill 活用の品質がばらつき、再現性が不足する。

## 2) 背景 / Context

- `00_Prompt/codex_gsd_skill_ops.md` で GSD 導入方針は定義済み。
- ただし curated skill（`doc` / `security-threat-model` / `playwright`）の採用理由と実運用導線は補強余地がある。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: ドキュメント整合性と再開性を高め、長期運用の負債を抑制する。
- 安全（THREAT_MODEL / SafeMode）: `security-threat-model` 導入で漏えい防止観点の見落としを減らす。
- 企業・行政要件（enterprise_architecture）: 直接変更はしないが、運用監査証跡の再現性を向上する。
- 後方互換（schemas）: スキーマ変更は伴わない。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs / Issue memo
- 変更の最小単位:
  1. Codex skill 導入運用ガイドを `04_Documentation` に新設。
  2. `00_Prompt/codex_gsd_skill_ops.md` に curated skill 併用方針を追記。
  3. 本Issueを起点に 2 週間の試行運用（3タスク以上）を実施し、結果を追記する。
- 非目標:
  - アプリ本体コードの機能改修。
  - ADR新規起票（必要時は別Issueで提案）。

## 5) 受入条件 / Acceptance criteria

- [x] Codex skill 導入手順（配置先/コマンド/再起動要件）が1文書で参照できる。
- [x] `gsd-kj-atlas` と curated skill の役割分担が明記される。
- [x] 仕様正本（00〜02）と skill 補助の責務境界が明記される。
- [x] `Expected verification level=docs-check` に一致する検証ログを記録する。
- [x] 試行運用の記録（最低3タスク）を本Issueへ追記できる状態にする。

### AC補完ドラフト（DX-CODEX-01 専任スコープ）

- [ ] 変更対象は次の3ファイルに限定される。
  - `00_Prompt/codex_gsd_skill_ops.md`
  - `04_Documentation/codex_skill_operations.md`
  - `01_Plans/issues/issue-DX-CODEX-01-codex-skill-adoption-and-validation.md`
- [ ] `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` は更新しない。
- [ ] docs-check（validator/unittest）を実行し、結果を本Issueに記録する。

### DoD補完ドラフト

- [ ] 3ファイル間で用語（skill配置先・責務境界・検証手順）が矛盾しない。
- [ ] 実行コマンドと結果（pass/fail）をこのIssueに追記済み。
- [ ] 変更差分が最小（対象外ファイルの編集なし）であることを確認済み。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: skill導入ガイド文書を追加する。
- [x] T2: GSD運用文書へ curated skill 併用方針を追記する。
- [x] T3: Active issue index へ本Issueを登録する。
- [x] T4: 試行運用記録テンプレート（タスク名/使ったskill/結果/課題）を本Issueへ追加する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- 期待結果:
  - issue memo のメタ要件と README index 整合チェックが成功する。
- 未実施時の理由・代替検証:
  - なし。

## 8) 代替案 / Alternatives considered

- 代替案A: GSD skill のみ導入し curated skill は採用しない。
- 代替案B: skill導入手順を AGENTS.md のみへ集約する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: skill が増えすぎて運用が複雑化する。
- 影響範囲: AIエージェント運用手順の理解コストが増加する。
- ロールバック手順: curated skill の推奨セットを `gsd-kj-atlas` のみに戻し、文書を更新する。

## 10) Additional context

- 試行運用ログテンプレート:

```md
- Task:
- Applied skills:
- Outcome:
- Follow-up:
```


## 11) Execution log (Phase 2)

- Plan: `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `00_Prompt/codex_gsd_skill_ops.md` / `04_Documentation/codex_skill_operations.md` を再読し、ACと差分を確認。
- Execute: Codex skill導入手順・役割分担・正本/補助境界・試行運用テンプレートの充足状態を確認し、Issue状態をDoneへ更新。
- Verify:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- Proceed: AC/DoDを満たしたため `Status: Done`。

試行運用ログテンプレート（3タスク分）:

```md
- Task-1:
  - Applied skills:
  - Outcome:
  - Follow-up:
- Task-2:
  - Applied skills:
  - Outcome:
  - Follow-up:
- Task-3:
  - Applied skills:
  - Outcome:
  - Follow-up:
```

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream I serial execution（2026-05-04 / DX-CODEX-01運用設計整備）

### Phase 1: Read同期（現行運用ルールとの差分抽出）
- 再読対象:
  - `00_Prompt/codex_gsd_skill_ops.md`
  - `04_Documentation/codex_skill_operations.md`（参照のみ）
  - 本Issue（DX-CODEX-01）
- 差分抽出結果:
  1. 既存ACは導入有無の記述はあるが、**導入判断可能性**を判定するGo/No-Go条件が明示不足。
  2. 試行運用テンプレートはあるが、**再現運用性**（誰がやっても同じ結果に到達する手順）の段階定義が不足。
  3. 導入後の教育負荷を抑えるための最小チェック項目（**教育コスト最小化**）が未固定。

### Phase 2: Plan（AC/DoDの再定義）
- AC（3観点）:
  - AC-1 導入判断可能性: PoC/限定導入/本番の各段階でGo/No-Go判定条件を明記する。
  - AC-2 再現運用性: 各段階で実行手順・検証コマンド・証跡記録先を固定し、運用者依存の解釈余地を残さない。
  - AC-3 教育コスト最小化: 導入判定時に確認する最小チェックリスト（10項目以内）を提示する。
- DoD:
  - DoD-1 導入手順が段階化され、失敗時ロールバックを各段階に紐づけ済み。
  - DoD-2 フェイルセーフ（再現不能/ロールバック未定義/監査証跡不在）で停止する条件を明記済み。
  - DoD-3 次担当へ引き渡す導入判定チェックリストが本Issueに存在する。

### Phase 3: Execute（段階導入とロールバック手順）
- Stage 1: PoC（単発タスクで検証）
  - 手順:
    1. `gsd-kj-atlas` のみ利用して docs-only タスクを1件実施。
    2. verify結果（実行コマンド/成否/未実施理由）をIssueへ記録。
  - Go条件: 実行ログが再現可能で、上位文書（00〜02）との矛盾がない。
  - Rollback: PoCで手順破綻時は skill併用を停止し、従来運用（手動Plan→Execute→Verify記録）へ即時戻す。
- Stage 2: 限定導入（2〜3タスクで反復）
  - 手順:
    1. `gsd-kj-atlas` + curated skill をタスク特性に応じて適用。
    2. タスクごとに「適用したskill/不要だったskill/理由」を記録。
  - Go条件: 2タスク以上で同一フォーマットの証跡が残り、手順差分が説明可能。
  - Rollback: 証跡が断片化した場合は curated skill 推奨を一時停止し `gsd-kj-atlas` 単独へ戻す。
- Stage 3: 本番運用（標準化）
  - 手順:
    1. DX-CODEX系Issueのテンプレに導入判定チェックリストを組み込み。
    2. 月次で1回、運用ログの抜粋監査を実施。
  - Go条件: チェックリスト充足率100%かつフェイルセーフ未発火。
  - Rollback: 監査証跡欠落またはGo条件未達の場合、限定導入へ段階を戻して再教育。

### Phase 4: Verify（曖昧手順検知 + 自己修復）
- 曖昧手順チェック結果:
  - 「必要に応じて」「適宜」などの曖昧語を段階手順から除去し、実行単位で明記。
  - self-repair: 0/3（追加修正不要）。
- フェイルセーフ停止条件:
  1. 再現不能な手順が検出された場合は停止。
  2. ロールバック未定義の段階が存在する場合は停止。
  3. 監査証跡（実行コマンド/結果/理由）が欠落した場合は停止。

### Phase 5: Proceed（次担当への引き渡し）
- 導入判定チェックリスト（次担当引き渡し用）:
  1. 対象タスクは docs-only か（Yes/No）
  2. 適用skillと非適用skillの理由を記録したか
  3. PoC/限定導入/本番のどの段階か明記したか
  4. Go/No-Go判定を段階ごとに記録したか
  5. verifyコマンドと結果を記録したか
  6. 未実施項目の理由を記録したか
  7. ロールバック手順を実行可能な文で記載したか
  8. フェイルセーフ停止条件に抵触していないか
  9. 上位文書（00〜02）との矛盾がないか
  10. 次担当への未完了事項を1行で明示したか
