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
