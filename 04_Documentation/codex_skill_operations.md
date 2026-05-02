# Codex Skill Operations

> Audience: 外部コントリビュータ（参照のみ）/ 内部運用担当者（正本利用）
> Purpose: 本文書を公開stubとして維持し、内部正本への導線を固定する。
> Outcome: 分類結果を **Move internal（運用正本は00_Prompt）** に固定し、公開境界の誤読を防ぐ。
> Public boundary: 公開文書は方針サマリと参照導線のみを保持し、内部手順・秘密情報・組織依存設定は保持しない。
> This document decides: 公開stubとして残す最小要素（分類結果、正本リンク、Go/No-Go、停止条件）。
> This document does not decide: skill詳細運用、内部監査詳細、環境固有の実行秘密、仕様の新規決定。
> Related: `00_Prompt/codex_gsd_skill_ops.md`, `00_Prompt/agent_handover.md`, `01_Plans/documentation_quality.md`

## 1. 分類結果（DOC-OPS-05-02）

- Classification: **Move internal**
- 公開配置方針: `04_Documentation/codex_skill_operations.md` は **stub（参照窓口）** としてのみ維持する。
- 内部正本: `00_Prompt/codex_gsd_skill_ops.md`
- 次アクション: 内部運用変更は `00_Prompt/codex_gsd_skill_ops.md` を更新し、本書はリンク整合のみ追随する。

## 2. 位置づけ（責務境界）

- skill は「実行補助」であり、仕様の正本ではありません。
- 仕様の正本は `00_Prompt` / `01_Plans` / `02_Architecture` です。
- 本書は「どう参照し、どう安全に運用するか」を定義します。

## 3. Go/No-Go gate（公開判定）

次を満たす場合のみ公開運用を Go とします。

1. Audience / decides / does not decide が明示されている。
2. 内部手順（秘密情報・組織依存設定）を本文に混在させていない。
3. SafeMode既定ON・share/export境界を後退させる記述がない。

未充足時は No-Go として内部文書側で修正してから再判定します。

## 4. 内部正本への導線

- 運用方針（詳細）: `00_Prompt/codex_gsd_skill_ops.md`
- タスク実行テンプレ / DoD: `00_Prompt/agent_handover.md`
- 公開品質ゲート: `01_Plans/documentation_quality.md`

## 5. 最小運用ルール

1. 作業開始前に `AGENTS.md` の Read Order を確認する。
2. docs-only タスクではコード変更を行わない。
3. 上流文書（00〜02）と矛盾が見つかった場合、実装を止めて論点化する。
4. Verify の自己修復は最大3回。3回超過は `StoppedForClarification`。

## 6. 環境依存手順の前提

skill導入/実行コマンドを使う場合は、前提条件を必ず明記します。

- Codex実行環境が利用可能であること。
- `$CODEX_HOME/skills` が参照可能であること。
- 組織ポリシー上、外部取得が許可されていること（必要時）。

> 環境が満たせない場合は、コマンド実行を省略し「未実施理由」を記録してください。

## 7. Verify

```bash
rg -n "Audience|This document decides|This document does not decide|Go/No-Go|SafeMode|StoppedForClarification" 04_Documentation/codex_skill_operations.md
git diff --check
```


## DOC-OPS user-requested serial execution（2026-04-22 / Issue 05-02）

### Phase 1 Read
- Phase開始時再Read: `04_Documentation/codex_skill_operations.md` と対応Issueを再読。

### Phase 2 Plan
- Phase開始時再Read: Audience/Purpose/Public boundary/decides節を再読。
- AC/DoD不足判定: 不足なし。公開stub運用を維持。

### Phase 3 Execute
- Phase開始時再Read: Go/No-Go節を再読。
- 実施: 本直列実行ログを追記（Classification=Move internal を維持）。

### Phase 4 Verify
- Phase開始時再Read: Verify節を再読。
- 実行: `rg -n "DOC-OPS user-requested serial execution|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 04_Documentation/codex_skill_operations.md`。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- 判定: **Ready**（内部正本導線を維持）。

## Stream H serial execution（2026-04-26 / DOC-OPS-05-02）

### Phase 1 Read
- 対象Issue（`issue-doc-ops-05-02-04doc-codex-skill-operations.md`）と本書を再読。

### Phase 2 ADR/CDC
- Context: 公開境界の誤読を防ぐため、04文書は内部正本への導線に限定する。
- Decision: 分類は **Move internal** を維持し、公開stub方針を継続。
- Consequences: 運用詳細は `00_Prompt/codex_gsd_skill_ops.md` 側で更新する。

### Phase 3 Plan
- docs-only / 最小差分で直列フェーズ記録のみ追加。

### Phase 4 Execute
- 本セクションを追加し、Issueとの整合ログを明示。

### Phase 5 Verify
- `rg -n "Stream H serial execution|Move internal|公開stub|Phase 5 Verify" 04_Documentation/codex_skill_operations.md`
- `git diff --check`
- 自己修復回数: 0/3。

### Phase 6 Proceed
- 状態: **Ready**（次Issueへ進行可）。

## Stream H Open化準備 run（2026-04-28）

### Phase 1 Read（issue + 対応docペア確認）
- 対応Issueと対象文書のペアを再読し、公開境界・分類・停止条件の整合を確認。

### Phase 2 Plan（Draft→Openゲート明文化）
- Open化ゲートを次の4点で固定。
  1. 必須メタ（Audience/Goal/Non-goal/Public boundary/Outcome または Requirement meta I/F）が追跡可能。
  2. AC/DoD/Validationが docs-check 前提で再現可能。
  3. 未承認事項の確定化を行わない（DecisionStatus=Fixed の範囲外は承認待ち）。
  4. self-repair は最大3回、4回目相当で停止。

### Phase 3 Execute（不足メタ/AC/Validation/Stop条件補完）
- 本セクションを追記し、Open化判定に必要な最小メタ（ゲート、検証、停止条件、Proceed判定）を明示。

### Phase 4 Verify（ゲート到達判定 + docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "Stream H Open化準備 run（2026-04-28）|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed|Open化可否" 04_Documentation/codex_skill_operations.md`
- `git diff --check`
- self-repair: 0/3（4回目相当は停止）。

### Phase 5 Proceed（Open化可否）
- Open化可否: **Yes**。
- 判定理由: Draft→Openの最小ゲート（メタ、AC/DoD、検証、停止条件）を満たし、docs-only境界を維持。

## Stream E共通: Draft課題のOpen化条件（DOC-OPS-05）

- 本文書で扱う Draft 課題は、次の **5条件をすべて満たした場合のみ Open 化** する。
  1. **Read**: 対象本文書と上位根拠（00〜02、必要なADR）を再読し、参照差分を列挙済み。
  2. **Plan**: Scope / Non-Goals / Acceptance / Validation / Stop Conditions を明文化済み。
  3. **Execute**: docs-only 境界（実装コード非変更）を維持し、allowlist 外の差分が 0。
  4. **Verify**: 再現可能な docs-check コマンドと結果（成功/未実施理由）を記録済み。
  5. **Proceed**: Go/No-Go/Conditional を明示し、未確定事項を「決定」扱いせず次アクションに分離済み。
- 未確定事項は `TBD` / `Assumption` / `Decision Needed` で明示し、**承認前に仕様確定文へ昇格しない**。
- 自己修復（同一原因への再試行）は最大3回まで。4回目相当は Stop とし、Open 化を保留する。



## Stream F serial execution（2026-05-01 / DOC-OPS-05-02）

### Phase 1: Read同期
- 対応Issue（`issue-doc-ops-05-02-04doc-codex-skill-operations.md`）と本書を再読し、公開stub運用と `Move internal` 判定を再確認。

### Phase 2: ADR/CDC判定
- 新規ADR/CDCは不要。既存決定（公開stub + 内部正本導線）を維持。

### Phase 3: Plan
- docs-only / 単一doc更新を固定。
- docs-check観点: 分類語彙・公開境界・Go/No-Go導線の追跡性を維持。

### Phase 4: Execute
- 本セクションを追記し、Issueと同日の直列ログを同期。

### Phase 5: Verify
- `rg -n "Stream F serial execution（2026-05-01 / DOC-OPS-05-02）|Move internal|公開stub|Go/No-Go" 04_Documentation/codex_skill_operations.md`
- `git diff --check`
- Self-correction: 0/3（上限3回）。

### Phase 6: Proceed
- 状態: **Go**（Stop条件非該当）。

## Stream J serial execution（2026-05-02 / DX-CODEX 運用導線改善）

### Phase 1: Read
- 再読対象: `00_Prompt/codex_gsd_skill_ops.md` / `00_Prompt/skills/gsd-kj-atlas/SKILL.md` / `00_Prompt/skills/markdown-mermaid-docops/SKILL.md` / `01_Plans/issues/issue-DX-CODEX-01-codex-skill-adoption-and-validation.md` / `01_Plans/issues/issue-DX-CODEX-02-markdown-mermaid-mcp-doc-ops-adoption.md` / 本書。
- 目的: DX-CODEX の責務境界（公開stubと内部正本）を維持しつつ、再現可能な検証導線を明確化する。

### Phase 2: ADR/仕様明文化
- Context: DX-CODEX 系文書は「Done」状態が多く、更新時にどこへ実行証跡を追記すべきかが曖昧になりやすい。
- Decision: 本書（公開stub）に Stream J の実行ログを追加し、`docs-check + リンク整合 + 再現性` を最小検証セットとして固定する。
- Consequences:
  - 正の影響: 次回以降のDX文書更新で Verify 観点が即時再利用できる。
  - 留意点: 運用詳細は引き続き `00_Prompt/codex_gsd_skill_ops.md` を正本とし、本書は境界説明と証跡窓口に限定する。
- AC/DoD 提案:
  - AC-1: docs-only かつ DX-CODEX 直結文書のみ変更。
  - AC-2: Verifyコマンドを3系統（validator / unittest / diff-check）で記録。
  - DoD-1: `Move internal` の分類を維持。
  - DoD-2: 自己修復回数を 0〜3 の範囲で明記。

### Phase 3: Plan
- 変更文書: `04_Documentation/codex_skill_operations.md` のみ。
- 期待効果: Stream単位の運用履歴をこの公開stubに集約し、内部正本への導線を崩さずに監査可能性を向上する。
- 検証方法:
  1. issue memo validator
  2. validator unittest
  3. `git diff --check`

### Phase 4: Execute
- 本セクションを追記（最小差分）。

### Phase 5: Verify
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- self-repair: 0/3（失敗なし）。

### Phase 6: Proceed
- 判定: **Go**。
- 停止条件（修復超過/前提崩壊/競合検知）: 非該当。
