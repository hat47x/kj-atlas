# Codex Skill Operations（公開境界スタブ）

> DOC-OPS-05 Classification: **Move internal**
> Audience: 外部コントリビュータ（参照のみ）
> Goal: Skill運用文書の公開境界を固定し、内部正本への導線を示す。
> Non-goal: 内部運用手順・実行環境依存コマンド・監査詳細の公開。
> Public boundary: 本書は境界説明のみを保持し、運用詳細は `00_Prompt` / `01_Plans` に集約する。
> Outcome: 読者が公開文書と内部運用文書を混同しない。
> Related: `00_Prompt/codex_gsd_skill_ops.md`, `01_Plans/documentation_quality.md`, `01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`

この文書は公開向けの最小スタブです。Codex skill の実運用手順は内部正本を参照してください。

## 公開する最小説明

- 本プロジェクトでは skill を「実行補助」として扱います。
- 仕様正本は `00_Prompt` / `01_Plans` / `02_Architecture` です。
- SafeMode 既定ON・share/export 境界を緩和する運用は採用しません。

## Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されている。
2. 仕様正本の所在が明記され、skill文書が正本を上書きしない。
3. 内部専用手順（秘密情報・環境依存パス）が本文に混在していない。

未充足の場合は「No-Go」とし、内部文書へ移設してから再公開判定します。

## 内部正本参照先

- `00_Prompt/codex_gsd_skill_ops.md`
- `01_Plans/documentation_quality.md`
- `01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`


## 共通ワークフローとフェイルセーフ（DOC-OPS-05 共通）

本書の更新は次の固定順序で実施する。

1. Phase 1 Read
2. Phase 2 ADR明文化（Context / Decision / Consequences）
3. Phase 3 Plan
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed

フェイルセーフ:

- Verify 失敗時は **自己修復を最大3回まで** 実施する。
- 4回目相当は作業を停止し、`01_Plans/issues/` にブロッカーを記録してエスカレーションする。


## Stream G docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **CDC**: Context / Decision / Consequences を明文化し、分類結果（Move internal / Improve external）を固定する。
3. **Plan**: AC/DoD を先に定義し、docs-only スコープ（`03_Implement/**` 非変更）を明示する。
4. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
5. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
6. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## DOC-OPS-05 追加実行記録（2026-04-16 / Target 05-01..05）

### Phase 1 Read（再Read）
- 本書と関連Issueを再Readし、公開境界とdocs-onlyスコープを確認。

### Phase 2 Plan（再Read）
- 5Phase（Read→Plan→Execute→Verify→Proceed）で進行し、対象外文書へは非接触とする。

### Phase 3 Execute（再Read）
- 本書の既存分類・公開境界メタを維持しつつ、05-01..05セットの実行記録を追記。

### Phase 4 Verify（再Read）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/codex_skill_operations.md 01_Plans/documentation_quality.md`
- `git diff --check`
- 修復は最大3回まで。3回超過は停止（Hold）。

### Phase 5 Proceed（再Read）
- 判定: **Ready**
- 次アクション: 同一セット内Issue本文とScope本文の整合を維持して進行。

## DOC-OPS-05 Stream G 前半フェーズ実行記録（2026-04-16）

- Classification確認: **Move internal**（再判定なし）
- フェイルセーフ固定: 用語ドリフト検知・固定値不一致検知・自己修復3回超過で停止（Hold）

### Phase 1: Read（対象ファイル再読）
- 本ファイルを再読し、Scope / Audience / Goal / Public boundary / Related の整合を確認。

### Phase 2: Plan（対象ファイル再読）
- 本ファイルを再読したうえで、docs-only の変更範囲と受入条件を固定。

### Phase 3: Execute（対象ファイル再読）
- 本ファイルを再読したうえで、分類方針（Move internal / Improve external）を維持して更新。

### Phase 4: Verify（docs-check、対象ファイル再読）
- 本ファイルを再読したうえで docs-check を実施。
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/codex_skill_operations.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。

## Stream H docs群1 serial cycle (2026-04-18)

### Phase 1 Read
- 対象ファイルを再読し、`Audience / Goal / Non-goal / Public boundary / Outcome / Related` の整合を確認した。
- Scopeを docs-only に固定し、編集禁止対象（`security.md` / `security_operational_guidelines.md` / shared files）へ非接触であることを確認した。

### Phase 2 Plan
- 1Phase1責務で進行し、変更は「実行記録の同期」と「公開境界の維持」に限定する。
- AC/DoD不足があれば先に補完提案し、未合意の新規仕様決定は持ち込まない。

### Phase 3 Execute（1ファイル直列）
- Classification: **Move internal**
- 04_Documentation/codex_skill_operations.md は参照stub方針を維持し、正本は 00_Prompt 側へ委譲する。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/codex_skill_operations.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。

## DOC-OPS-05 Stream J2 execution record (2026-04-18)

### Phase 1: Read
- Target issue scope and this document were re-read to confirm Audience / Goal / Public boundary.
- Classification remains **Move internal** and no Stream H-owned file edits are required.

### Phase 2: ADR CDC
- CDC update is **not required** because the existing placement policy is within current DOC-OPS-05 decisions.

### Phase 3: Plan
- AC/DoD補足: 分類根拠（Audience/Goal/公開境界）・次アクション・検証一致（docs-check）を1セットで記録する。
- 次アクション固定: 00_Prompt側正本導線を維持し、公開stubを継続する。

### Phase 4: Execute
- docs-onlyで本ファイルのみを更新し、実装仕様変更は行わない。

### Phase 5: Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|DOC-OPS-05 Stream J2" 04_Documentation/codex_skill_operations.md`
- `git diff --check`
- Self-correction policy: max 3 attempts, then stop and reassign if unresolved.

### Phase 6: Proceed
- 判定: **Ready**
- 根拠: 分類根拠・次アクション・検証一致を同一文書内で追跡可能。


## Stream H serial cycle（2026-04-19 / DOC-OPS-05-02）

### Phase 1 Read
- `issue-doc-ops-05-02` と本書を再Readし、Classification=**Move internal** と DecisionStatus=Fixed を確認。

### Phase 2 ADR CDC
- 追加ADR不要。既存CDCで継続。

### Phase 3 Plan
- AC/DoD不足なし。公開境界スタブ運用を維持。

### Phase 4 Execute
- 公開文書は最小説明に限定し、内部運用は正本参照へ誘導。

### Phase 5 Verify
- docs-check（必須メタ・参照整合・`git diff --check`）を実施。
- 自己修復上限3回。

### Phase 6 Proceed
- 状態: **Ready**
