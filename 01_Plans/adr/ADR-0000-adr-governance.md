# ADR-0000: 01_Plans を ADR で管理する方針

- Status: Accepted
- Date: 2026-02-24
- Deciders: Project Maintainers
- Scope: `01_Plans/`

## Context

従来の `01_Plans` は `roadmap.md` / `phase*.md` / `phaseX*.md` / `value_to_requirements.md` に分散し、
意思決定（なぜそうするか）と実行計画（いつ・何をするか）が混在していた。
この状態では、判断根拠の追跡と差分レビューが困難になる。

## Decision

`01_Plans` 配下の計画文書を **ADR（Architecture Decision Record）形式へ全面移行**する。
今後の要件・計画・運用方針は `01_Plans/adr/ADR-xxxx-*.md` で管理する。

### ADR 管理方式

1. 採番: `ADR-0000` からの連番（4桁ゼロ埋め）。
2. 1 ADR = 1 意思決定境界（必要なら旧文書1つを1 ADRとして移管）。
3. 必須ヘッダ: `Status` / `Date` / `Deciders` / `Scope`。
4. 必須章: `Context` / `Decision` / `Consequences` / `Traceability`。
5. 変更時は「追記優先」。破壊的改変ではなく、
   `Supersedes` / `Superseded by` を使って履歴を残す。
6. ADR には意思決定・背景・影響を記録し、実装タスクの進捗管理は Issue で行う。
7. 旧 `phase*.md` などのタスク管理文書は廃止し、公開課題は GitHub Issues、AIエージェント向け補助情報は `01_Plans` の文脈メモへ整理する。

### ADR粒度ポリシー（2026-02-24 追記）

8. 1 ADR の目安は **50〜180行**。200行を継続的に超える場合は分割候補とする。
9. 分割軸は「意思決定境界」（例: 価値原則 / 要求マッピング / 受入基準 / 運用手順）。
10. 親ADRは要約と索引に縮約し、詳細は子ADRへ委譲して可読性を維持する。
11. 情報欠落を避けるため、分割時は `Traceability` に `Derived-from` を必須記載する。

### Issue と ADR の分離ポリシー（2026-02-26 追記）

12. **Issue は Action、ADR は Decision & Context を記録**する。
    - Issue: 「何をするか / どう直すか」を追跡し、完了後にCloseする。
    - ADR: 「なぜその選択をしたか / 何を選ばなかったか」を永続記録する。
13. ADR起票トリガーは次の3条件のいずれかを満たす場合とする。
    - 複数の選択肢とトレードオフ比較がある。
    - 性能・安全性・保守性など非機能要件に影響する。
    - 半年後の新規参加者に背景説明が必要になる。
14. **IssueとADRの連携**を明示する。
    - Issueで議論が設計判断へ発展した場合は、IssueからADRを起票して判断を固定する。
    - ADRがAcceptedになった後は、実装・移行・検証をIssueへ分解して実行する。
15. ADR本文には「実装タスクの進捗管理」を書き込まず、進捗はIssue側で管理する。
16. 対外的な課題管理は GitHub Issues を正本とする。
17. `01_Plans` 配下の issue 記述は AIエージェントのコンテキスト保持（再開性向上）の補助用途に限定する。


### 01_Plans issue補助メモのライフサイクル（2026-02-27 追記）

18. `01_Plans` 配下の issue 補助メモは、**完了時に削除（garbage collection）** を標準とし、archive の常時蓄積は行わない。
19. 完了時は次の順で処理する。
    1) GitHub Issue を Close（Actionの完了）
    2) 永続的に残す判断は ADR へ昇格（Decision/Context）
    3) 完了事実は `CHANGELOG.md` 等へ要約（What）
    4) 補助メモは `git rm` で削除
20. 例外的に archive 保存を許可するのは、以下の一次データ保持が必要な場合のみ。
    - 再発障害調査用の生ログ（例: stack trace, 時系列観測）
    - 将来比較に必要な検証生データ（例: 性能測定）
    - 監査/コンプライアンス上の記録保持
21. archive 保存時はファイル冒頭に `Retention Reason` / `Review Due` / `Source Issue` を必須記載し、四半期棚卸しで不要化した記録を削除する。
22. AIエージェントは補助メモを短命ドキュメントとして扱い、仕様判断が含まれる内容は補助メモへ滞留させず ADR 化を提案する。




### 01_Plans issue補助メモの配置・管理規約（2026-02-27 追記）

23. `01_Plans` 配下の issue 補助メモは **`01_Plans/issues/` に配置**し、ルート直下へは置かない。
24. 命名規則は `issue-<BacklogID>-<short-title>.md` を推奨し、Backlog/ADR/Issue の相互参照を先頭メタ情報へ明記する。
25. `01_Plans/issues/README.md` を **index正本** とし、Active（Draft/Open/In Progress）のみを一覧化する。
26. GitHub Issue が Done/Closed になった補助メモは、`README.md` の Active 一覧から外し、原則 `git rm` で削除する。
27. 例外保存（Retention Reason あり）の場合のみ `01_Plans/issues/archive/` へ移動し、`Review Due` を設定する。
28. `01_Plans/README.md` には個別 issue の固定一覧を持たず、`01_Plans/issues/README.md` への導線のみを置く（一覧の二重管理を避ける）。

29. issue補助メモの本文構成は `01_Plans/issues/TEMPLATE.md` を標準とし、必須項目（Meta/Traceability/Acceptance criteria/Validation plan）を省略しない。
30. `Source Issue`（GitHub URL）は Open化時に必須入力とし、Draft段階のみ `TBD` を許可する。
31. 受入条件には、少なくとも「安全影響」「後方互換」「検証手順（コマンド）」の3要素を含める。
32. 人間と生成AIの双方が再利用できるよう、issue補助メモは見出し固定（1)課題〜10)追加文脈）で記述する。

33. 新規ADRは `01_Plans/adr/TEMPLATE.md` を雛形として作成し、必須ヘッダ/必須章の欠落を禁止する。
34. ADRの初期Statusは原則 `Proposed` とし、合意時に `Accepted` へ更新する。
35. ADR本文へ実装進捗（チェックボックス等）は記載せず、進捗管理はIssueへ分離する。

### 個人OSS・プレリリース段階の適正化（2026-05-31 追記 / `ADR-0039`）

36. 本リポジトリは現在 solo・プレリリース（`README.md` NOTICE）であり、上記 1–35 のうち重量級の運用は段階に合わせて緩和する。詳細と不変条件は `ADR-0039` を正本とする。
37. 緩和: 「1 ADR 50–180行」「Authoring Checklist 必須」「`Draft→Open` での `Source Issue` 必須」「`Open/In Progress/Done` の多役割承認」は solo 段階では推奨へ降格し、Status 遷移は Maintainer 単独で確定してよい。
38. 維持（緩和禁止）: SafeMode 既定ON・漏えい防止・proposal-only・`human_reviewed` 人手昇格・`KJ_ATLAS_LLM_PROVIDER=none` 既定の各不変条件。これらはガバナンスではなくプロダクト本体として維持する。
39. 再導入: 外部協力者の継続参加、または公開リリースで実ユーザーが付いた時点で、役割分離・Decision Queue・観測スコアカードを段階的に戻す。

## Three-Element Verification（ADR-0067 遡及適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | 従来の計画文書はroadmap/phase/value_to_requirementsに分散し、意思決定（なぜ）と実行計画（いつ・何を）が混在して判断根拠の追跡と差分レビューが困難。01_Plans配下の計画文書をADR形式へ全面移行する | 機能: 1 ADR=1意思決定境界、必須ヘッダ（Status/Date/Deciders/Scope）と必須章（Context/Decision/Consequences/Traceability）を固定。データ: 変更時は追記優先でSupersedes/Superseded byで履歴を残す |
| **データ設計** | ADRには意思決定・背景・影響を記録し、実装タスクの進捗管理はIssueで行う。1 ADRの目安は50〜180行で200行超は分割候補。分割軸は意思決定境界（価値原則/要求マッピング/受入基準/運用手順） | 業務: どの判断がどの要件・設計・実装に影響するかを追跡しやすくする。機能: 親ADRは要約と索引に縮約し詳細は子ADRへ委譲して可読性を維持 |
| **機能設計** | IssueはAction（何をするか/どう直すか）、ADRはDecision&Context（なぜその選択か/何を選ばなかったか）を記録。ADR起票トリガーはトレードオフ比較・非機能要件影響・半年後の新規参加者への背景説明の3条件 | 業務: 維持（緩和禁止）はSafeMode既定ON・漏えい防止・proposal-only・human_reviewed人手昇格・provider=none既定。データ: 再導入は外部協力者の継続参加または公開リリースで実ユーザーが付いた時点 |

## Consequences

- どの判断が、どの要件・設計・実装に影響するかを追跡しやすくなる。
- 既存参照（AGENTS.md 等）は ADR パスへ更新が必要。
- 既存文書の情報は ADR 側へ欠落なく移管し、旧文書は削除する。

## Traceability

- Replaces: `01_Plans/roadmap.md`, `01_Plans/value_to_requirements.md`,
  `01_Plans/phase0_bootstrap.md`, `01_Plans/phase1_canvas_mvp.md`,
  `01_Plans/phase2_qualitative_integration.md`, `01_Plans/phase3_review_governance.md`,
  `01_Plans/phaseX_future_backlog.md`, `01_Plans/phaseX_cli_tool.md`,
  `01_Plans/phaseX_local_llm_integration.md`
